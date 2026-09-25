"""Forced periodic 2-D turbulence benchmark.

The comparison is deliberately apples-to-apples: full-grid spectral, static
POD-Galerkin, and adaptive SVD-DLRA all use the same stream-function split,
time step, forcing, dealiasing mask, and initial state.  The DLRA path pays for
all three stage projections, so the reported timing is an honest end-to-end
comparison rather than a factored-kernel estimate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

import numpy as np

# Make direct ``python experiments/run_*.py`` execution work from any cwd.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from solvers import (
    DLRA,
    Grid2D,
    KolmogorovForcing,
    PODGalerkin,
    StreamFunctionNS,
)


def make_initial_state(
    grid: Grid2D,
    base_speed: float = 0.5,
    perturbation_velocity_rms: float = 0.25,
    cutoff: int = 8,
    seed: int = 20260925,
) -> np.ndarray:
    """Build a reproducible Kolmogorov shear plus broadband perturbation.

    The base stream function is ``-base_speed*cos(y)``, hence
    ``u=base_speed*sin(y), v=0``.  A real random field is spectrally filtered
    and normalized by its velocity RMS.  The construction is independent of the
    reduced rank and is therefore suitable for a fair reference comparison.

    Mask semantics -- ``cutoff`` is a *box half-width in wavenumber*, not a
    radial cutoff: the filter keeps every mode with ``|k_x| <= cutoff`` **and**
    ``|k_y| <= cutoff``.  Two consequences are worth stating because they are
    not guessable from the parameter name:

    * The highest **radial** wavenumber present is the box corner,
      ``floor(cutoff*sqrt(2))`` -- so cutoff 2, 4, 8 reach |k| = 2, 5, 11, not
      2, 4, 8.
    * The real field therefore factors through ``2*cutoff+1`` modes per axis,
      so its matrix rank is at most ``2*cutoff+1``: cutoff 8 gives exactly
      rank 17, which is the IC rank the gate records.

    The base shear sits at ``(0,+-1)``, inside the box for any cutoff >= 1, so
    it adds no rank.  Both facts are pinned by a test.
    """
    _, Y = np.meshgrid(grid.x, grid.y, indexing="ij")
    base = -float(base_speed) * np.cos(Y)
    rng = np.random.default_rng(seed)
    raw = rng.normal(size=(grid.N, grid.N))
    F = grid.fft(raw)
    mask = (np.abs(grid.kx)[:, None] <= cutoff) & (
        np.abs(grid.ky)[None, :] <= cutoff
    )
    perturbation = grid.ifft(F * mask)
    perturbation -= np.mean(perturbation)
    u, v = grid.velocity(perturbation)
    rms = float(np.sqrt(np.mean(u * u + v * v)))
    if rms > 0.0:
        perturbation *= float(perturbation_velocity_rms) / rms
    state = base + perturbation
    state -= np.mean(state)
    return state


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def relative_l2(a: np.ndarray, b: np.ndarray) -> float | None:
    if not (np.isfinite(a).all() and np.isfinite(b).all()):
        return None
    # The stream-function constant is a physical gauge; compare centered
    # states so a harmless rank-projection gauge offset is not called error.
    a = a - np.mean(a)
    b = b - np.mean(b)
    denom = max(float(np.linalg.norm(b)), np.finfo(float).eps)
    return float(np.linalg.norm(a - b) / denom)


def initial_state_fingerprint(grid: Grid2D, initial: np.ndarray, tolerance: float = 1e-10) -> dict:
    """Fingerprint the shared initial state (P0) for every result artifact.

    Records the SHA-256 of the float64 C-contiguous bytes, the dtype and
    shape, the numerical rank of the centered field at the working
    tolerance, and the initial kinetic energy, so any result can be tied
    back to the exact state all methods start from.

    ``tolerance`` here is a *relative singular-value (amplitude)* threshold on
    the centered state, used only to state the IC's numerical rank; it is
    unrelated to the DLRA's ``relative_amplitude_cutoff`` and is not an
    accuracy criterion for either.
    """
    arr = np.ascontiguousarray(initial, dtype=float)
    payload = {
        "sha256": hashlib.sha256(arr.tobytes()).hexdigest(),
        "dtype": arr.dtype.name,
        "shape": list(arr.shape),
        "initial_energy": float(grid.ke(initial)),
    }
    centered = arr - np.mean(arr)
    try:
        values = np.linalg.svd(centered, compute_uv=False)
        payload["numerical_rank"] = (
            int(np.sum(values > tolerance * values[0])) if values.size else 0
        )
    except np.linalg.LinAlgError:
        payload["numerical_rank"] = None
    return payload


def finite_or_none(value):
    value = float(value)
    return value if np.isfinite(value) else None


def normalized_spectrum(field: np.ndarray, count: int | None = None) -> list[float]:
    """Return a JSON-safe normalized singular-value spectrum.

    ``count=None`` (the default) records every singular value of the state
    matrix.  F2 requires the *untruncated* reference spectrum over all
    resolved modes -- a cap makes the truncation threshold unverifiable -- so
    the leading-``count`` form is available for compact diagnostics only.
    """
    if not np.isfinite(field).all():
        return []
    try:
        values = np.linalg.svd(field, compute_uv=False)
    except np.linalg.LinAlgError:
        return []
    limit = values.size if count is None else min(count, values.size)
    if values.size == 0 or not np.isfinite(values).all() or values[0] <= np.finfo(float).eps:
        return [0.0 for _ in range(limit)]
    return [float(x) for x in (values[:limit] / values[0])]


def _energy_residual(
    model: StreamFunctionNS,
    old: np.ndarray,
    new: np.ndarray,
    dt: float,
    t: float,
    grid: Grid2D,
    projection_energy_increment: float = 0.0,
) -> float:
    terms = model.energy_terms(old, t)
    derivative = (grid.ke(new) - grid.ke(old)) / dt
    residual = terms.residual_from_derivative(derivative)
    # A projection changes the numerical state by an explicit amount.  For a
    # reduced run, subtract that measured control work before judging the
    # discrete balance; the unmodified residual is retained separately as a
    # full-PDE diagnostic.
    residual -= projection_energy_increment / dt
    scale = max(1.0, abs(terms.dissipation), abs(terms.forcing_input))
    return abs(residual) / scale


def _stability_assessment(
    energy_history: list[float],
    enstrophy_history: list[float],
    max_divergence: float,
    max_cfl: float,
    unstable_step: int | None,
) -> dict:
    """Apply scale-aware sanity limits in addition to finite-value checks."""
    limits = {
        "max_relative_energy": 10.0,
        "max_relative_enstrophy": 100.0,
        "max_abs_divergence": 1.0e-10,
        "max_cfl": 0.5,
    }
    finite = all(np.isfinite(energy_history)) and all(np.isfinite(enstrophy_history))
    max_energy_ratio = (
        max(energy_history) / max(abs(energy_history[0]), np.finfo(float).eps)
        if energy_history
        else np.inf
    )
    max_enstrophy_ratio = (
        max(enstrophy_history) / max(abs(enstrophy_history[0]), np.finfo(float).eps)
        if enstrophy_history
        else np.inf
    )
    reasons = []
    if unstable_step is not None:
        reasons.append(f"nonfinite_state_at_step_{unstable_step}")
    if not finite:
        reasons.append("nonfinite_energy_or_enstrophy")
    if max_energy_ratio > limits["max_relative_energy"]:
        reasons.append("energy_sanity_limit")
    if max_enstrophy_ratio > limits["max_relative_enstrophy"]:
        reasons.append("enstrophy_sanity_limit")
    if max_divergence > limits["max_abs_divergence"]:
        reasons.append("divergence_limit")
    if max_cfl > limits["max_cfl"]:
        reasons.append("cfl_limit")
    return {
        "stable": not reasons,
        "unstable_step": unstable_step,
        "unstable_reason": reasons,
        "max_relative_energy": finite_or_none(max_energy_ratio),
        "max_relative_enstrophy": finite_or_none(max_enstrophy_ratio),
        "max_cfl": finite_or_none(max_cfl),
        "limits": limits,
    }


def _run_full(
    model: StreamFunctionNS,
    initial: np.ndarray,
    dt: float,
    nsteps: int,
    train_steps: int,
    snapshot_stride: int,
    compare_stride: int,
    spectrum_count: int | None = None,
) -> dict:
    grid = model.grid
    state = initial.copy()
    training = []
    checkpoints = {0: state.copy()}
    times = [0]
    spectra = {0: normalized_spectrum(state, spectrum_count)}
    energy_history = [grid.ke(state)]
    enstrophy_history = [grid.enstrophy(state)]
    max_div = grid.max_div_velocity(state)
    u0, v0 = grid.velocity(state)
    max_cfl = float(np.max(np.hypot(u0, v0)) * dt / grid.dx)
    max_residual = 0.0
    max_energy_increase = -np.inf
    unstable_step = None
    start = time.perf_counter()
    for step in range(1, nsteps + 1):
        old = state
        t = (step - 1) * dt
        old_energy = grid.ke(old)
        state = model.step(old, dt, t=t)
        if not np.isfinite(state).all():
            unstable_step = step
            break
        energy_history.append(grid.ke(state))
        enstrophy_history.append(grid.enstrophy(state))
        u_now, v_now = grid.velocity(state)
        max_cfl = max(max_cfl, float(np.max(np.hypot(u_now, v_now)) * dt / grid.dx))
        max_div = max(max_div, grid.max_div_velocity(state))
        max_residual = max(
            max_residual, _energy_residual(model, old, state, dt, t, grid)
        )
        max_energy_increase = max(max_energy_increase, grid.ke(state) - old_energy)
        if step <= train_steps and step % snapshot_stride == 0:
            training.append(state.copy())
        if step % compare_stride == 0 or step == nsteps:
            checkpoints[step] = state.copy()
            times.append(step)
            spectra[step] = normalized_spectrum(state, spectrum_count)
    seconds = time.perf_counter() - start
    stability = _stability_assessment(
        energy_history, enstrophy_history, max_div, max_cfl, unstable_step
    )
    if not training:
        training = [initial.copy(), state.copy()]
    return {
        "state": state,
        "training": training,
        "checkpoints": checkpoints,
        "checkpoint_steps": times,
        "singular_value_steps": times,
        "singular_values": [spectra[step] for step in times],
        "energy_history": energy_history,
        "enstrophy_history": enstrophy_history,
        "initial_energy": energy_history[0],
        "final_energy": energy_history[-1],
        "final_enstrophy": enstrophy_history[-1],
        "forcing_aware_invariant": {
            "status": "full_grid_pde_balance",
            "formula": "dE/dt + nu*||omega||^2 - <psi,zeta> + <psi,adv>",
            "max_scaled_residual": finite_or_none(max_residual),
        },
        "max_abs_divergence": finite_or_none(max_div),
        "max_scaled_full_pde_energy_residual": finite_or_none(max_residual),
        "max_scaled_energy_balance_residual": finite_or_none(max_residual),
        "max_energy_increase": finite_or_none(max_energy_increase),
        "stable": stability["stable"],
        "unstable_step": stability["unstable_step"],
        "unstable_reason": stability["unstable_reason"],
        "max_relative_energy": stability["max_relative_energy"],
        "max_relative_enstrophy": stability["max_relative_enstrophy"],
        "max_cfl": stability["max_cfl"],
        "stability_limits": stability["limits"],
        "wall_seconds": seconds,
        "wall_seconds_per_step": seconds / max(nsteps, 1),
    }


def _run_projected(
    model: StreamFunctionNS,
    initial: np.ndarray,
    dt: float,
    nsteps: int,
    compare_stride: int,
    projector: Callable[[np.ndarray], np.ndarray],
    reference_checkpoints: dict,
    rank_history=None,
    spectrum_count: int | None = None,
) -> dict:
    grid = model.grid
    state = projector(initial.copy())
    checkpoints = {0: state.copy()}
    spectra = {0: normalized_spectrum(state, spectrum_count)}
    energy_history = [grid.ke(state)]
    enstrophy_history = [grid.enstrophy(state)]
    projection_energy_history = []
    errors = []
    if 0 in reference_checkpoints:
        errors.append(
            {
                "step": 0,
                "time": 0.0,
                "relative_l2": relative_l2(state, reference_checkpoints[0]),
            }
        )
    max_div = grid.max_div_velocity(state)
    u0, v0 = grid.velocity(state)
    max_cfl = float(np.max(np.hypot(u0, v0)) * dt / grid.dx)
    max_residual = 0.0
    max_full_pde_residual = 0.0
    max_energy_increase = -np.inf
    unstable_step = None
    start = time.perf_counter()
    for step in range(1, nsteps + 1):
        old = state
        t = (step - 1) * dt
        old_energy = grid.ke(old)
        try:
            state = model.step(old, dt, projector=projector, t=t)
        except (FloatingPointError, np.linalg.LinAlgError):
            unstable_step = step
            break
        projection_increment = float(model.last_step_info.get("projection_energy_increment", 0.0))
        projection_energy_history.append(projection_increment)
        if not np.isfinite(state).all():
            unstable_step = step
            break
        energy_history.append(grid.ke(state))
        enstrophy_history.append(grid.enstrophy(state))
        u_now, v_now = grid.velocity(state)
        max_cfl = max(max_cfl, float(np.max(np.hypot(u_now, v_now)) * dt / grid.dx))
        max_div = max(max_div, grid.max_div_velocity(state))
        max_full_pde_residual = max(
            max_full_pde_residual,
            _energy_residual(model, old, state, dt, t, grid, 0.0),
        )
        max_residual = max(
            max_residual,
            _energy_residual(
                model, old, state, dt, t, grid, projection_increment
            ),
        )
        max_energy_increase = max(max_energy_increase, grid.ke(state) - old_energy)
        if step % compare_stride == 0 or step == nsteps:
            checkpoints[step] = state.copy()
            spectra[step] = normalized_spectrum(state, spectrum_count)
            if step in reference_checkpoints:
                errors.append(
                    {
                        "step": step,
                        "time": step * dt,
                        "relative_l2": relative_l2(
                            state, reference_checkpoints[step]
                        ),
                    }
                )
    seconds = time.perf_counter() - start
    stability = _stability_assessment(
        energy_history, enstrophy_history, max_div, max_cfl, unstable_step
    )
    finite_errors = [
        item["relative_l2"]
        for item in errors
        if item["relative_l2"] is not None
    ]
    if finite_errors:
        max_error = max(finite_errors)
        final_error = errors[-1]["relative_l2"]
    else:
        max_error = None if not stability["stable"] else 0.0
        final_error = None if not stability["stable"] else 0.0
    result = {
        "state": state,
        "checkpoints": checkpoints,
        "singular_value_steps": sorted(spectra),
        "singular_values": [spectra[step] for step in sorted(spectra)],
        "energy_history": energy_history,
        "enstrophy_history": enstrophy_history,
        "projection_energy_history": projection_energy_history,
        "initial_energy": energy_history[0],
        "final_energy": energy_history[-1],
        "final_enstrophy": enstrophy_history[-1],
        "forcing_aware_invariant": {
            "status": "projected_discrete_balance_with_projection_work",
            "formula": "dE/dt + nu*||omega||^2 - <psi,zeta> + <psi,adv> - projection_energy_increment/dt",
            "max_scaled_residual": finite_or_none(max_residual),
        },
        "comparison": errors,
        "max_relative_l2_vs_full": max_error,
        "final_relative_l2_vs_full": final_error,
        "max_abs_divergence": finite_or_none(max_div),
        "max_scaled_full_pde_energy_residual": finite_or_none(max_full_pde_residual),
        "max_scaled_energy_balance_residual": finite_or_none(max_residual),
        "max_energy_increase": finite_or_none(max_energy_increase),
        "stable": stability["stable"],
        "unstable_step": stability["unstable_step"],
        "unstable_reason": stability["unstable_reason"],
        "max_relative_energy": stability["max_relative_energy"],
        "max_relative_enstrophy": stability["max_relative_enstrophy"],
        "max_cfl": stability["max_cfl"],
        "stability_limits": stability["limits"],
        "wall_seconds": seconds,
        "wall_seconds_per_step": seconds / max(nsteps, 1),
    }
    if rank_history is not None:
        result["rank_history"] = [int(x) for x in rank_history]
        result["rank_min"] = int(min(rank_history))
        result["rank_max"] = int(max(rank_history))
        result["rank_final"] = int(rank_history[-1])
    return result


def run_case(
    re: int = 100,
    N: int = 64,
    dt: float = 0.002,
    nsteps: int = 200,
    force_amplitude: float = 0.2,
    base_speed: float = 0.5,
    perturbation_velocity_rms: float = 0.25,
    cutoff: int = 8,
    seed: int = 20260925,
    train_steps: int = 100,
    snapshot_stride: int = 5,
    compare_stride: int = 10,
    pod_rank: int = 12,
    dlra_rank: int = 4,
    dlra_min_rank: int = 2,
    dlra_max_rank: int = 48,
    dlra_relative_amplitude_cutoff: float = 1e-6,
    dlra_check_every: int = 5,
    dlra_adapt_initial: bool = True,
    spectrum_count: int | None = None,
) -> dict:
    if re <= 0:
        raise ValueError("Re must be positive")
    if nsteps < 1 or train_steps < 1:
        raise ValueError("nsteps and train_steps must be positive")
    grid = Grid2D(N)
    forcing = KolmogorovForcing(amplitude=force_amplitude, wavenumber=1.0)
    initial = make_initial_state(
        grid,
        base_speed=base_speed,
        perturbation_velocity_rms=perturbation_velocity_rms,
        cutoff=cutoff,
        seed=seed,
    )
    full_model = StreamFunctionNS(grid, nu=1.0 / re, forcing=forcing, dealias=True)
    full = _run_full(
        full_model,
        initial,
        dt,
        nsteps,
        train_steps,
        snapshot_stride,
        compare_stride,
        spectrum_count=spectrum_count,
    )

    def strip(result):
        return {
            key: value
            for key, value in result.items()
            if key not in {"state", "training", "checkpoints"}
        }

    if not full["stable"] or not np.isfinite(full["state"]).all():
        return {
            "case": "kolmogorov",
            "provenance": {
                "git_commit": _git_commit(),
                "driver": "experiments/run_kolmogorov.py",
            },
            "grid": {"N": N, "L": grid.L},
            "reynolds": re,
            "viscosity": 1.0 / re,
            "parameters": {
                "dt": dt,
                "nsteps": nsteps,
                "final_time": nsteps * dt,
                "force_amplitude": force_amplitude,
                "base_speed": base_speed,
                "perturbation_velocity_rms": perturbation_velocity_rms,
                "cutoff": cutoff,
                "seed": seed,
                "train_steps": train_steps,
                "snapshot_stride": snapshot_stride,
                "compare_stride": compare_stride,
                "pod_rank": pod_rank,
                "dlra_initial_rank": dlra_rank,
                "dlra_min_rank": dlra_min_rank,
                "dlra_max_rank": dlra_max_rank,
                "dlra_relative_amplitude_cutoff": dlra_relative_amplitude_cutoff,
                "dlra_check_every": dlra_check_every,
                "dlra_adapt_initial": dlra_adapt_initial,
            },
            "initial_state": initial_state_fingerprint(grid, initial),
            "initial_energy": grid.ke(initial),
            "full": strip(full),
            "pod": None,
            "dlra": None,
            "skipped_reason": "full-grid run failed finite/scale-aware stability checks",
        }

    fit_start = time.perf_counter()
    # P0: the static-POD baseline must start from the same bit-identical IC as
    # the full-grid and DLRA runs.  Its offline snapshot set therefore includes
    # t=0, so the IC lies in span(mean, basis) and its L2 projection is exact
    # (the online state is then the IC itself, not a projected surrogate of it).
    pod = PODGalerkin(grid, pod_rank).fit([initial] + list(full["training"]))
    fit_seconds = time.perf_counter() - fit_start
    pod_ic_projection_error = pod.relative_error(initial)
    pod_model = StreamFunctionNS(grid, nu=1.0 / re, forcing=forcing, dealias=True)
    pod_model.track_step_diagnostics = True
    pod_result = _run_projected(
        pod_model,
        initial,
        dt,
        nsteps,
        compare_stride,
        pod,
        full["checkpoints"],
        rank_history=[pod.effective_rank()] * (nsteps + 1),
        spectrum_count=spectrum_count,
    )
    pod_result["fit_seconds"] = fit_seconds
    pod_result["initial_projection_relative_l2"] = pod_ic_projection_error
    pod_result["offline_plus_online_seconds"] = (
        fit_seconds + pod_result["wall_seconds"]
    )
    pod_result["effective_rank"] = pod.effective_rank()

    dlra_model = StreamFunctionNS(grid, nu=1.0 / re, forcing=forcing, dealias=True)
    dlra_model.track_step_diagnostics = True
    dlra = DLRA(
        dlra_model,
        rank=dlra_rank,
        min_rank=dlra_min_rank,
        max_rank=dlra_max_rank,
        relative_amplitude_cutoff=dlra_relative_amplitude_cutoff,
        check_every=dlra_check_every,
        adapt_initial=dlra_adapt_initial,
    )
    # The stateful driver is used here rather than a static projector so that
    # rank adaptation is exercised and included in the timing.  Keep the
    # one-time projection visible separately from online evolution.
    dlra_init_start = time.perf_counter()
    dlra_state = dlra.initialize(initial)
    dlra_init_seconds = time.perf_counter() - dlra_init_start
    dlra_start = time.perf_counter()
    dlra_max_div = grid.max_div_velocity(dlra_state)
    u0, v0 = grid.velocity(dlra_state)
    dlra_max_cfl = float(np.max(np.hypot(u0, v0)) * dt / grid.dx)
    dlra_max_residual = 0.0
    dlra_max_full_pde_residual = 0.0
    dlra_max_energy_increase = -np.inf
    dlra_unstable_step = None
    dlra_errors = [
        {
            "step": 0,
            "time": 0.0,
            "relative_l2": relative_l2(dlra_state, full["checkpoints"][0]),
        }
    ]
    dlra_spectra = {0: normalized_spectrum(dlra_state, spectrum_count)}
    dlra_energy_history = [grid.ke(dlra_state)]
    dlra_enstrophy_history = [grid.enstrophy(dlra_state)]
    dlra_projection_energy_history = []
    for step in range(1, nsteps + 1):
        old = dlra_state
        t = (step - 1) * dt
        try:
            dlra_state = dlra.step(old, dt, t=t)
        except (FloatingPointError, np.linalg.LinAlgError):
            dlra_unstable_step = step
            break
        dlra_projection_increment = float(
            dlra.last_step_info.get("projection_energy_increment", 0.0)
        )
        dlra_projection_energy_history.append(dlra_projection_increment)
        if not np.isfinite(dlra_state).all():
            dlra_unstable_step = step
            break
        dlra_energy_history.append(grid.ke(dlra_state))
        dlra_enstrophy_history.append(grid.enstrophy(dlra_state))
        u_now, v_now = grid.velocity(dlra_state)
        dlra_max_cfl = max(
            dlra_max_cfl, float(np.max(np.hypot(u_now, v_now)) * dt / grid.dx)
        )
        dlra_max_div = max(dlra_max_div, grid.max_div_velocity(dlra_state))
        dlra_max_full_pde_residual = max(
            dlra_max_full_pde_residual,
            _energy_residual(dlra_model, old, dlra_state, dt, t, grid, 0.0),
        )
        dlra_max_residual = max(
            dlra_max_residual,
            _energy_residual(
                dlra_model,
                old,
                dlra_state,
                dt,
                t,
                grid,
                dlra_projection_increment,
            ),
        )
        dlra_max_energy_increase = max(
            dlra_max_energy_increase, grid.ke(dlra_state) - grid.ke(old)
        )
        if step % compare_stride == 0 or step == nsteps:
            dlra_spectra[step] = normalized_spectrum(dlra_state, spectrum_count)
            if step in full["checkpoints"]:
                dlra_errors.append(
                    {
                        "step": step,
                        "time": step * dt,
                        "relative_l2": relative_l2(
                            dlra_state, full["checkpoints"][step]
                        ),
                    }
                )
    dlra_seconds = time.perf_counter() - dlra_start
    dlra_stability = _stability_assessment(
        dlra_energy_history,
        dlra_enstrophy_history,
        dlra_max_div,
        dlra_max_cfl,
        dlra_unstable_step,
    )
    finite_dlra_errors = [
        item["relative_l2"]
        for item in dlra_errors
        if item["relative_l2"] is not None
    ]
    dlra_result = {
        "max_relative_l2_vs_full": max(finite_dlra_errors)
        if finite_dlra_errors
        else (None if not dlra_stability["stable"] else 0.0),
        "final_relative_l2_vs_full": dlra_errors[-1]["relative_l2"]
        if dlra_errors
        else (None if not dlra_stability["stable"] else 0.0),
        "comparison": dlra_errors,
        "singular_value_steps": sorted(dlra_spectra),
        "singular_values": [dlra_spectra[step] for step in sorted(dlra_spectra)],
        "energy_history": dlra_energy_history,
        "enstrophy_history": dlra_enstrophy_history,
        "projection_energy_history": dlra_projection_energy_history,
        "initial_energy": dlra_energy_history[0],
        "final_energy": dlra_energy_history[-1],
        "final_enstrophy": dlra_enstrophy_history[-1],
        "forcing_aware_invariant": {
            "status": "projected_discrete_balance_with_projection_work",
            "formula": "dE/dt + nu*||omega||^2 - <psi,zeta> + <psi,adv> - projection_energy_increment/dt",
            "max_scaled_residual": finite_or_none(dlra_max_residual),
        },
        "max_abs_divergence": finite_or_none(dlra_max_div),
        "max_scaled_full_pde_energy_residual": finite_or_none(dlra_max_full_pde_residual),
        "max_scaled_energy_balance_residual": finite_or_none(dlra_max_residual),
        "max_energy_increase": finite_or_none(dlra_max_energy_increase),
        "stable": dlra_stability["stable"],
        "unstable_step": dlra_stability["unstable_step"],
        "unstable_reason": dlra_stability["unstable_reason"],
        "max_relative_energy": dlra_stability["max_relative_energy"],
        "max_relative_enstrophy": dlra_stability["max_relative_enstrophy"],
        "max_cfl": dlra_stability["max_cfl"],
        "stability_limits": dlra_stability["limits"],
        "wall_seconds": dlra_seconds,
        "initialization_seconds": dlra_init_seconds,
        "offline_plus_online_seconds": dlra_init_seconds + dlra_seconds,
        "wall_seconds_per_step": dlra_seconds / max(nsteps, 1),
        "rank_history": [int(x) for x in dlra.rank_history],
        "rank_min": int(min(dlra.rank_history)),
        "rank_max": int(max(dlra.rank_history)),
        "rank_final": int(dlra.rank),
    }

    return {
        "case": "kolmogorov",
        "provenance": {
            "git_commit": _git_commit(),
            "driver": "experiments/run_kolmogorov.py",
        },
        "grid": {"N": N, "L": grid.L},
        "reynolds": re,
        "viscosity": 1.0 / re,
        "parameters": {
            "dt": dt,
            "nsteps": nsteps,
            "final_time": nsteps * dt,
            "force_amplitude": force_amplitude,
            "base_speed": base_speed,
            "perturbation_velocity_rms": perturbation_velocity_rms,
            "cutoff": cutoff,
            "seed": seed,
            "train_steps": train_steps,
            "snapshot_stride": snapshot_stride,
            "compare_stride": compare_stride,
            "pod_rank": pod.effective_rank(),
            "pod_fit_includes_ic": True,
            "spectrum_count": spectrum_count,
            "dlra_initial_rank": dlra_rank,
            "dlra_min_rank": dlra_min_rank,
            "dlra_max_rank": dlra_max_rank,
            "dlra_relative_amplitude_cutoff": dlra_relative_amplitude_cutoff,
            "dlra_check_every": dlra_check_every,
            "dlra_adapt_initial": dlra_adapt_initial,
        },
        "initial_state": initial_state_fingerprint(grid, initial),
        "initial_energy": grid.ke(initial),
        "full": strip(full),
        "pod": strip(pod_result),
        "dlra": dlra_result,
        "method_note": "DLRA timings include all SVD projections; its current implementation materializes the nonlinear residual on the full grid.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--re", type=int, default=100)
    parser.add_argument("--N", type=int, default=64)
    parser.add_argument("--dt", type=float, default=0.002)
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--force-amplitude", type=float, default=0.2)
    parser.add_argument("--base-speed", type=float, default=0.5)
    parser.add_argument("--perturbation-velocity-rms", type=float, default=0.25)
    parser.add_argument("--cutoff", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260925)
    parser.add_argument("--train-steps", type=int, default=100)
    parser.add_argument("--snapshot-stride", type=int, default=5)
    parser.add_argument("--compare-stride", type=int, default=10)
    parser.add_argument("--pod-rank", type=int, default=12)
    parser.add_argument("--dlra-rank", type=int, default=4)
    parser.add_argument("--dlra-min-rank", type=int, default=2)
    parser.add_argument("--dlra-max-rank", type=int, default=48)
    parser.add_argument(
        "--dlra-relative-amplitude-cutoff",
        type=float,
        default=1e-6,
        help="retain singular values above this fraction of s[0]; this is an\n"
             "amplitude test on singular values, not an accuracy tolerance",
    )
    parser.add_argument("--dlra-check-every", type=int, default=5)
    parser.add_argument(
        "--dlra-adapt-initial",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "--spectrum-count",
        type=int,
        default=0,
        help="leading singular values to record per state; 0 records the full spectrum",
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = run_case(
        re=args.re,
        N=args.N,
        dt=args.dt,
        nsteps=args.steps,
        force_amplitude=args.force_amplitude,
        base_speed=args.base_speed,
        perturbation_velocity_rms=args.perturbation_velocity_rms,
        cutoff=args.cutoff,
        seed=args.seed,
        train_steps=args.train_steps,
        snapshot_stride=args.snapshot_stride,
        compare_stride=args.compare_stride,
        pod_rank=args.pod_rank,
        dlra_rank=args.dlra_rank,
        dlra_min_rank=args.dlra_min_rank,
        dlra_max_rank=args.dlra_max_rank,
        dlra_relative_amplitude_cutoff=args.dlra_relative_amplitude_cutoff,
        dlra_check_every=args.dlra_check_every,
        dlra_adapt_initial=args.dlra_adapt_initial,
        spectrum_count=args.spectrum_count or None,
    )
    output = args.output or Path(f"state/coder/results/kolmogorov_re{args.re}_N{args.N}.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
