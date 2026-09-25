"""Long-time full-grid/DLRA forced-turbulence validation.

This driver intentionally omits the static POD projection: the short Re suite
in ``run_kolmogorov.py`` supplies the three-way baseline comparison, while this
run checks that the full reference and adaptive DLRA remain finite and
structurally divergence-free beyond the short comparison horizon.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.run_kolmogorov import (
    _energy_residual,
    _stability_assessment,
    _git_commit,
    initial_state_fingerprint,
    make_initial_state,
    normalized_spectrum,
    relative_l2,
)
from solvers import DLRA, Grid2D, KolmogorovForcing, StreamFunctionNS


def run_case(
    re: int = 5000,
    N: int = 64,
    dt: float = 0.0005,
    final_time: float = 1.0,
    sample_stride: int = 100,
    history_stride: int = 10,
    rank: int = 2,
    min_rank: int = 2,
    max_rank: int = 48,
    relative_amplitude_cutoff: float = 1e-10,
    adapt_initial: bool = True,
) -> dict:
    nsteps = int(round(final_time / dt))
    if nsteps < 1 or abs(nsteps * dt - final_time) > 1e-12:
        raise ValueError("final_time must be an integer multiple of dt")
    if history_stride < 1:
        raise ValueError("history_stride must be positive")
    grid = Grid2D(N)
    initial = make_initial_state(
        grid,
        base_speed=0.5,
        perturbation_velocity_rms=1.0,
        cutoff=8,
        seed=20260925,
    )
    forcing = KolmogorovForcing(amplitude=0.5, wavenumber=1.0)
    full_model = StreamFunctionNS(grid, 1.0 / re, forcing=forcing, dealias=True)
    dlra_model = StreamFunctionNS(grid, 1.0 / re, forcing=forcing, dealias=True)
    dlra_model.track_step_diagnostics = True
    dlra = DLRA(
        dlra_model,
        rank=rank,
        min_rank=min_rank,
        max_rank=max_rank,
        relative_amplitude_cutoff=relative_amplitude_cutoff,
        check_every=5,
        adapt_initial=adapt_initial,
    )
    full = initial.copy()
    reduced = dlra.initialize(initial)
    full_energy = [grid.ke(full)]
    dlra_energy = [grid.ke(reduced)]
    full_enstrophy = [grid.enstrophy(full)]
    dlra_enstrophy = [grid.enstrophy(reduced)]
    full_projection_energy = []
    dlra_projection_energy = []
    full_div = grid.max_div_velocity(full)
    dlra_div = grid.max_div_velocity(reduced)
    u0, v0 = grid.velocity(full)
    full_max_cfl = float(np.max(np.hypot(u0, v0)) * dt / grid.dx)
    u0, v0 = grid.velocity(reduced)
    dlra_max_cfl = float(np.max(np.hypot(u0, v0)) * dt / grid.dx)
    full_residual = 0.0
    dlra_residual = 0.0
    dlra_full_pde_residual = 0.0
    full_max_energy = full_energy[0]
    dlra_max_energy = dlra_energy[0]
    full_max_enstrophy = full_enstrophy[0]
    dlra_max_enstrophy = dlra_enstrophy[0]
    samples = [
        {"step": 0, "time": 0.0, "relative_l2": relative_l2(reduced, full)}
    ]
    full_spectrum = {0: normalized_spectrum(full)}
    dlra_spectrum = {0: normalized_spectrum(reduced)}
    unstable = {"full": None, "dlra": None}
    start = time.perf_counter()
    for step in range(1, nsteps + 1):
        t = (step - 1) * dt
        old_full = full
        old_reduced = reduced
        full = full_model.step(old_full, dt, t=t)
        reduced = dlra.step(old_reduced, dt, t=t)
        dlra_projection_increment = float(
            dlra.last_step_info.get("projection_energy_increment", 0.0)
        )
        if not np.isfinite(full).all():
            unstable["full"] = step
            break
        if not np.isfinite(reduced).all():
            unstable["dlra"] = step
            break
        full_energy_now = grid.ke(full)
        dlra_energy_now = grid.ke(reduced)
        full_enstrophy_now = grid.enstrophy(full)
        dlra_enstrophy_now = grid.enstrophy(reduced)
        full_max_energy = max(full_max_energy, full_energy_now)
        dlra_max_energy = max(dlra_max_energy, dlra_energy_now)
        full_max_enstrophy = max(full_max_enstrophy, full_enstrophy_now)
        dlra_max_enstrophy = max(dlra_max_enstrophy, dlra_enstrophy_now)
        if step % history_stride == 0 or step == nsteps:
            full_energy.append(full_energy_now)
            dlra_energy.append(dlra_energy_now)
            full_enstrophy.append(full_enstrophy_now)
            dlra_enstrophy.append(dlra_enstrophy_now)
            full_projection_energy.append(0.0)
            dlra_projection_energy.append(dlra_projection_increment)
        u_now, v_now = grid.velocity(full)
        full_max_cfl = max(
            full_max_cfl, float(np.max(np.hypot(u_now, v_now)) * dt / grid.dx)
        )
        u_now, v_now = grid.velocity(reduced)
        dlra_max_cfl = max(
            dlra_max_cfl, float(np.max(np.hypot(u_now, v_now)) * dt / grid.dx)
        )
        full_div = max(full_div, grid.max_div_velocity(full))
        dlra_div = max(dlra_div, grid.max_div_velocity(reduced))
        full_residual = max(
            full_residual, _energy_residual(full_model, old_full, full, dt, t, grid)
        )
        dlra_full_pde_residual = max(
            dlra_full_pde_residual,
            _energy_residual(dlra_model, old_reduced, reduced, dt, t, grid, 0.0),
        )
        dlra_residual = max(
            dlra_residual,
            _energy_residual(
                dlra_model,
                old_reduced,
                reduced,
                dt,
                t,
                grid,
                dlra_projection_increment,
            ),
        )
        if step % sample_stride == 0 or step == nsteps:
            samples.append(
                {
                    "step": step,
                    "time": step * dt,
                    "relative_l2": relative_l2(reduced, full),
                }
            )
            full_spectrum[step] = normalized_spectrum(full)
            dlra_spectrum[step] = normalized_spectrum(reduced)
    seconds = time.perf_counter() - start
    full_stability = _stability_assessment(
        [full_energy[0], full_max_energy],
        [full_enstrophy[0], full_max_enstrophy],
        full_div,
        full_max_cfl,
        unstable["full"],
    )
    dlra_stability = _stability_assessment(
        [dlra_energy[0], dlra_max_energy],
        [dlra_enstrophy[0], dlra_max_enstrophy],
        dlra_div,
        dlra_max_cfl,
        unstable["dlra"],
    )
    sample_values = [
        item["relative_l2"] for item in samples if item["relative_l2"] is not None
    ]
    return {
        "case": "kolmogorov_long_time",
        "provenance": {
            "git_commit": _git_commit(),
            "driver": "experiments/run_long_time.py",
        },
        "grid": {"N": N, "L": grid.L},
        "reynolds": re,
        "parameters": {
            "dt": dt,
            "nsteps": nsteps,
            "final_time": final_time,
            "sample_stride": sample_stride,
            "history_stride": history_stride,
            "initial_rank": rank,
            "min_rank": min_rank,
            "max_rank": max_rank,
            "relative_amplitude_cutoff": relative_amplitude_cutoff,
            "adapt_initial": adapt_initial,
            "force_amplitude": 0.5,
            "base_speed": 0.5,
            "perturbation_velocity_rms": 1.0,
            "cutoff": 8,
            "seed": 20260925,
        },
        "initial_state": initial_state_fingerprint(grid, initial),
        "initial_energy": grid.ke(initial),
        "samples": samples,
        "full": {
            "energy_history": full_energy,
            "enstrophy_history": full_enstrophy,
            "projection_energy_history": full_projection_energy,
            "stable": full_stability["stable"],
            "unstable_step": full_stability["unstable_step"],
            "unstable_reason": full_stability["unstable_reason"],
            "max_relative_energy": full_stability["max_relative_energy"],
            "max_relative_enstrophy": full_stability["max_relative_enstrophy"],
            "max_cfl": full_stability["max_cfl"],
            "stability_limits": full_stability["limits"],
            "final_energy": full_energy[-1],
            "final_enstrophy": full_enstrophy[-1],
            "forcing_aware_invariant": {
                "status": "full_grid_pde_balance",
                "formula": "dE/dt + nu*||omega||^2 - <psi,zeta> + <psi,adv>",
                "max_scaled_residual": full_residual,
            },
            "max_abs_divergence": full_div,
            "max_scaled_full_pde_energy_residual": full_residual,
            "max_scaled_energy_balance_residual": full_residual,
            "singular_value_steps": sorted(full_spectrum),
            "singular_values": [full_spectrum[s] for s in sorted(full_spectrum)],
        },
        "dlra": {
            "energy_history": dlra_energy,
            "enstrophy_history": dlra_enstrophy,
            "projection_energy_history": dlra_projection_energy,
            "stable": dlra_stability["stable"],
            "unstable_step": dlra_stability["unstable_step"],
            "unstable_reason": dlra_stability["unstable_reason"],
            "max_relative_energy": dlra_stability["max_relative_energy"],
            "max_relative_enstrophy": dlra_stability["max_relative_enstrophy"],
            "max_cfl": dlra_stability["max_cfl"],
            "stability_limits": dlra_stability["limits"],
            "final_energy": dlra_energy[-1],
            "final_enstrophy": dlra_enstrophy[-1],
            "forcing_aware_invariant": {
                "status": "projected_discrete_balance_with_projection_work",
                "formula": "dE/dt + nu*||omega||^2 - <psi,zeta> + <psi,adv> - projection_energy_increment/dt",
                "max_scaled_residual": dlra_residual,
            },
            "max_abs_divergence": dlra_div,
            "max_scaled_full_pde_energy_residual": dlra_full_pde_residual,
            "max_scaled_energy_balance_residual": dlra_residual,
            "rank_history": [int(x) for x in dlra.rank_history],
            "rank_min": int(min(dlra.rank_history)),
            "rank_max": int(max(dlra.rank_history)),
            "rank_final": int(dlra.rank),
            "singular_value_steps": sorted(dlra_spectrum),
            "singular_values": [dlra_spectrum[s] for s in sorted(dlra_spectrum)],
        },
        "max_relative_l2_dlra_vs_full": max(sample_values) if sample_values else None,
        "wall_seconds": seconds,
        # Two cost accountings (R5q): measured factorization time inside the
        # whole-field SVDs, and the wall time of the whole online run.  The
        # factorization is of the full N x N field, so the first is
        # rank-independent; a linear-algebra win is not a per-step win (D11.1).
        "linear_algebra_seconds": dlra.projector.svd_seconds,
        "linear_algebra_calls": int(dlra.projector.svd_calls),
        "method_note": "Long-time run compares full-grid and DLRA only; see the short Re suite for static POD.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--re", type=int, default=5000)
    parser.add_argument("--N", type=int, default=64)
    parser.add_argument("--dt", type=float, default=0.0005)
    parser.add_argument("--final-time", type=float, default=1.0)
    parser.add_argument("--sample-stride", type=int, default=100)
    parser.add_argument("--history-stride", type=int, default=10)
    parser.add_argument("--rank", type=int, default=2)
    parser.add_argument("--min-rank", type=int, default=2)
    parser.add_argument("--max-rank", type=int, default=48)
    parser.add_argument("--relative-amplitude-cutoff", type=float, default=1e-10)
    parser.add_argument(
        "--adapt-initial",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("state/coder/results/kolmogorov_re5000_N64_long.json"),
    )
    args = parser.parse_args()
    result = run_case(
        args.re,
        args.N,
        args.dt,
        args.final_time,
        args.sample_stride,
        args.history_stride,
        args.rank,
        args.min_rank,
        args.max_rank,
        args.relative_amplitude_cutoff,
        args.adapt_initial,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
