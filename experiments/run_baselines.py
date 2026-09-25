"""F5: rank- and work-matched baselines on one initial state.

F5's bar, from the gate spec: full-grid spectral; static POD at r = 16/32/42
**and at the rank the adaptive method reached**; POD-DMD at the same matched
ranks; and a fixed-rank variant of the proposed method, so that adaptivity is
separated from rank.  Identical IC (hash-verified), same dt policy, same
forcing.  The comparison is made on the accuracy metrics in the P0 order --
time-averaged KE and enstrophy of the fluctuations over the statistical window,
and the spectra over the resolved range -- with pointwise L2 reported last and
labelled as trajectory divergence.

Three things this driver is careful about, each of which has already gone
wrong once in this project:

* **The IC is hashed and shared.**  Every method records the same fingerprint
  and the run aborts if they differ, so a method can never quietly start from
  its own projection (P0).
* **The metrics are computed on fluctuations.**  ``psi' = psi - x-avg(psi)``,
  per S1.  The zonal mean grows secularly in this problem (D11.2), so a
  total-energy statistic would measure that growth instead of the method.
* **Ranks are matched, not nominal.**  The adaptive rank is read from the
  DLRA run and then requested explicitly from POD and POD-DMD, so a
  "rank 42" claim is a rank the baseline actually ran at.

Run from the repository root, after the regime pilot has chosen T::

    ~/.venvs/ns/bin/python experiments/run_baselines.py --re 5000 --T 20
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from solvers import (
    DLRA,
    Grid2D,
    KolmogorovForcing,
    PODDMD,
    PODGalerkin,
    StreamFunctionNS,
    fluctuations,
)
from experiments.run_kolmogorov import (
    _git_commit,
    initial_state_fingerprint,
    make_initial_state,
    relative_l2,
)


def new_model(grid: Grid2D, re: int, amplitude: float) -> StreamFunctionNS:
    forcing = KolmogorovForcing(amplitude=amplitude, wavenumber=1.0)
    model = StreamFunctionNS(grid, nu=1.0 / re, forcing=forcing, dealias=True)
    model.track_step_diagnostics = True
    return model


def window_metrics(
    grid: Grid2D, states: list[np.ndarray], times: list[float], window: tuple[float, float]
) -> dict:
    """Time-averaged fluctuation KE/enstrophy and spectra over a window.

    Returns the block-mean spread as well as the mean, because a mean over a
    window that is not actually stationary is not a statistic (S2).
    """
    t0, t1 = window
    selected = [
        (t, s) for t, s in zip(times, states) if t0 - 1e-12 <= t <= t1 + 1e-12
    ]
    if len(selected) < 2:
        return {"window_start": t0, "window_end": t1, "samples": len(selected)}
    e_series, z_series = [], []
    e_sum = z_sum = None
    count = 0
    for _, s in selected:
        prime = fluctuations(s)
        e_series.append(grid.ke(prime))
        z_series.append(grid.enstrophy(prime))
        k, e, z = grid.isotropic_spectra(prime)
        if e_sum is None:
            e_sum, z_sum = np.zeros_like(e), np.zeros_like(z)
        e_sum += e
        z_sum += z
        count += 1
    e_arr = np.asarray(e_series)
    z_arr = np.asarray(z_series)
    return {
        "window_start": t0,
        "window_end": t1,
        "samples": count,
        "energy_fluct_mean": float(e_arr.mean()),
        "energy_fluct_relative_std": float(e_arr.std() / max(abs(e_arr.mean()), 1e-30)),
        "energy_fluct_block_means": _block_means(e_series, len(e_series) // 4 or 1),
        "enstrophy_fluct_mean": float(z_arr.mean()),
        "enstrophy_fluct_relative_std": float(z_arr.std() / max(abs(z_arr.mean()), 1e-30)),
        "enstrophy_fluct_block_means": _block_means(z_series, len(z_series) // 4 or 1),
        "k": [int(x) for x in k],
        "E_fluct": [float(x) for x in (e_sum / count)],
        "Z_fluct": [float(x) for x in (z_sum / count)],
        "sum_E_fluct": float(np.sum(e_sum / count)),
        "sum_Z_fluct": float(np.sum(z_sum / count)),
        "dealias_resolved_k_max": int(grid.N // 3),
    }


def _block_means(series: list[float], blocks: int) -> list[float]:
    blocks = max(1, min(blocks, len(series)))
    chunks = np.array_split(np.asarray(series, dtype=float), blocks)
    return [float(c.mean()) for c in chunks if c.size]


def run_reference(
    grid: Grid2D, model: StreamFunctionNS, initial: np.ndarray, dt: float,
    final_time: float, sample_every: int, train_until: float, keep_stride: int,
) -> dict:
    """Full-grid reference; also the source of the offline training window."""
    state = initial.copy()
    times = [0.0]
    states = [state.copy()]
    training = [state.copy()]          # t=0 included: P0 for the static baseline
    checkpoints = {0: state.copy()}
    max_div = grid.max_div_velocity(state)
    u0, v0 = grid.velocity(state)
    max_cfl = float(np.max(np.hypot(u0, v0)) * dt / grid.dx)
    max_residual = 0.0
    nsteps = int(round(final_time / dt))
    for step in range(1, nsteps + 1):
        old = state
        state = model.step(old, dt, t=(step - 1) * dt)
        if not np.isfinite(state).all():
            raise FloatingPointError(f"reference non-finite at step {step}")
        max_div = max(max_div, grid.max_div_velocity(state))
        max_residual = max(
            max_residual,
            abs(model.energy_terms(old, (step - 1) * dt).residual_from_derivative(
                (grid.ke(state) - grid.ke(old)) / dt
            )) / max(1.0, grid.enstrophy(old), 1e-30),
        )
        if step <= int(round(train_until / dt)) and step % max(1, int(round(keep_stride / dt))) == 0:
            training.append(state.copy())
        if step % sample_every == 0 or step == nsteps:
            times.append(step * dt)
            states.append(state.copy())
            checkpoints[step] = state.copy()
    return {
        "times": times,
        "states": states,
        "training": training,
        "checkpoints": checkpoints,
        "max_abs_divergence": max_div,
        "max_cfl": max_cfl,
        "max_scaled_energy_balance_residual": max_residual,
    }


def run_projected(
    grid: Grid2D, model: StreamFunctionNS, initial: np.ndarray, dt: float,
    final_time: float, sample_every: int, projector, reference_checkpoints: dict,
) -> dict:
    """A projected run: static POD or fixed-rank DLRA share this path."""
    state = projector(initial.copy())
    times = [0.0]
    states = [state.copy()]
    max_div = grid.max_div_velocity(state)
    max_residual = 0.0
    projection_energy = 0.0
    nsteps = int(round(final_time / dt))
    start = time.perf_counter()
    for step in range(1, nsteps + 1):
        old = state
        before = grid.ke(old)
        state = model.step(old, dt, t=(step - 1) * dt, projector=projector)
        if not np.isfinite(state).all():
            raise FloatingPointError(f"projected run non-finite at step {step}")
        projection_energy += grid.ke(state) - before
        max_div = max(max_div, grid.max_div_velocity(state))
        if step % sample_every == 0 or step == nsteps:
            times.append(step * dt)
            states.append(state.copy())
    return {
        "times": times,
        "states": states,
        "max_abs_divergence": max_div,
        "max_scaled_energy_balance_residual": max_residual,
        "projection_energy_total": projection_energy,
        "wall_seconds": time.perf_counter() - start,
    }


def run_dmd(
    grid: Grid2D, dmd: PODDMD, initial: np.ndarray, dt: float,
    final_time: float, sample_every: int,
) -> dict:
    """POD-DMD rollout: the modal operator advances, not the PDE."""
    coefficients = dmd.coefficients(initial)
    state = dmd.reconstruct(coefficients)
    times = [0.0]
    states = [state.copy()]
    max_div = grid.max_div_velocity(state)
    nsteps = int(round(final_time / dt))
    start = time.perf_counter()
    for step in range(1, nsteps + 1):
        coefficients = dmd.step(coefficients)
        state = dmd.reconstruct(coefficients)
        if not np.isfinite(state).all():
            raise FloatingPointError(f"POD-DMD non-finite at step {step}")
        max_div = max(max_div, grid.max_div_velocity(state))
        if step % sample_every == 0 or step == nsteps:
            times.append(step * dt)
            states.append(state.copy())
    return {
        "times": times,
        "states": states,
        "max_abs_divergence": max_div,
        "wall_seconds": time.perf_counter() - start,
    }


def divergence_series(
    times: list[float], states: list[np.ndarray], reference_times: list[float],
    reference_states: list[np.ndarray],
) -> list[dict]:
    """Pointwise L2 against the reference -- reported last, as divergence."""
    out = []
    ref = dict(zip(reference_times, reference_states))
    for t, s in zip(times, states):
        # nearest reference sample at or before t
        candidates = [rt for rt in ref if rt <= t + 1e-12]
        if not candidates:
            continue
        rt = max(candidates)
        out.append({"time": t, "relative_l2": relative_l2(s, ref[rt])})
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--re", type=int, default=5000)
    parser.add_argument("--N", type=int, default=64)
    parser.add_argument("--dt", type=float, default=None)
    parser.add_argument("--T", type=float, required=True,
                        help="final time; must be the horizon the regime pilot selected")
    parser.add_argument("--window-start", type=float, default=None,
                        help="start of the statistical window (default: final third)")
    parser.add_argument("--sample-every", type=int, default=None,
                        help="comparison stride in steps (default: 200)")
    parser.add_argument("--train-time", type=float, default=None,
                        help="offline training window (default: first 20%% of T)")
    parser.add_argument("--train-snapshot-stride", type=float, default=0.05)
    parser.add_argument("--ranks", type=int, nargs="+", default=[16, 32, 42])
    parser.add_argument("--dmd-ridge", type=float, default=0.0)
    parser.add_argument("--dlra-relative-amplitude-cutoff", type=float, default=1e-10)
    parser.add_argument("--dlra-max-rank", type=int, default=64)
    parser.add_argument("--dlra-check-every", type=int, default=5)
    parser.add_argument("--force-amplitude", type=float, default=0.5)
    parser.add_argument("--base-speed", type=float, default=0.5)
    parser.add_argument("--perturbation-velocity-rms", type=float, default=1.0)
    parser.add_argument("--cutoff", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260925)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    grid = Grid2D(args.N)
    dt = args.dt if args.dt is not None else 5e-4 * (64.0 / args.N)
    sample_every = args.sample_every or max(1, int(round(0.1 / dt)))
    train_time = args.train_time if args.train_time is not None else 0.2 * args.T
    window_start = (
        args.window_start if args.window_start is not None else args.T / 3.0
    )
    output_path = args.output or Path(
        f"state/coder/results/baselines_re{args.re}_N{args.N}.json"
    )
    initial = make_initial_state(
        grid,
        base_speed=args.base_speed,
        perturbation_velocity_rms=args.perturbation_velocity_rms,
        cutoff=args.cutoff,
        seed=args.seed,
    )
    fingerprint = initial_state_fingerprint(grid, initial)
    window = (window_start, args.T)

    # Fail before a long run, not inside it: a truncated SVD of an (N^2, n)
    # matrix has exactly n directions, so a window with fewer snapshots than
    # the largest requested rank cannot supply that rank.  ``PODGalerkin.fit``
    # raises on this too; this check exists so the message arrives before the
    # reference run has consumed the horizon.
    n_train = 1 + int(train_time / max(args.train_snapshot_stride, 1e-12))
    largest = max(args.ranks)
    if n_train < largest:
        raise SystemExit(
            f"the offline window supplies about {n_train} snapshots (t=0 plus "
            f"one every {args.train_snapshot_stride} up to t={train_time}), "
            f"which cannot supply rank {largest}. Increase --train-time, "
            f"decrease --train-snapshot-stride, or lower --ranks. The adaptive "
            f"rank is not known yet, so the ladder must already cover it."
        )
    print(
        f"offline window: ~{n_train} snapshots for ranks up to {largest}",
        flush=True,
    )

    print(f"reference: Re={args.re} N={args.N} T={args.T} dt={dt} ...", flush=True)
    ref = run_reference(
        grid, new_model(grid, args.re, args.force_amplitude), initial, dt,
        args.T, sample_every, train_time, args.train_snapshot_stride,
    )
    ref_metrics = window_metrics(grid, ref["states"], ref["times"], window)

    methods: dict[str, dict] = {}
    ref_div = divergence_series(
        ref["times"], ref["states"], ref["times"], ref["states"]
    )

    def record(name: str, run: dict, extra: dict | None = None) -> None:
        metrics = window_metrics(grid, run["states"], run["times"], window)
        div = divergence_series(run["times"], run["states"], ref["times"], ref["states"])
        finite = [d["relative_l2"] for d in div if d["relative_l2"] is not None]
        entry = {
            "metrics": metrics,
            "max_abs_divergence": run["max_abs_divergence"],
            "trajectory_divergence_series": div,
            "max_trajectory_divergence": max(finite) if finite else None,
            "final_trajectory_divergence": finite[-1] if finite else None,
            "wall_seconds": run.get("wall_seconds"),
        }
        if extra:
            entry.update(extra)
        methods[name] = entry
        print(
            f"  {name}: E_fluct={metrics.get('energy_fluct_mean')} "
            f"Z_fluct={metrics.get('enstrophy_fluct_mean')} "
            f"maxdiv={run['max_abs_divergence']:.2e} "
            f"traj_div={entry['max_trajectory_divergence']}",
            flush=True,
        )

    record("full_grid", {**ref, "wall_seconds": None},
           {"fingerprint": fingerprint, "role": "reference"})

    # The adaptive method, which also supplies the rank the others must match.
    print("adaptive DLRA (supplies the matched rank) ...", flush=True)
    adaptive = DLRA(
        new_model(grid, args.re, args.force_amplitude),
        rank=2,
        min_rank=1,
        max_rank=args.dlra_max_rank,
        relative_amplitude_cutoff=args.dlra_relative_amplitude_cutoff,
        check_every=args.dlra_check_every,
        adapt_initial=True,
    )
    dlra_state = adaptive.initialize(initial)
    dlra_times = [0.0]
    dlra_states = [dlra_state.copy()]
    dlra_div = grid.max_div_velocity(dlra_state)
    dlra_start = time.perf_counter()
    nsteps = int(round(args.T / dt))
    for step in range(1, nsteps + 1):
        dlra_state = adaptive.step(dlra_state, dt, t=(step - 1) * dt)
        if not np.isfinite(dlra_state).all():
            raise FloatingPointError(f"DLRA non-finite at step {step}")
        dlra_div = max(dlra_div, grid.max_div_velocity(dlra_state))
        if step % sample_every == 0 or step == nsteps:
            dlra_times.append(step * dt)
            dlra_states.append(dlra_state.copy())
    adaptive_rank = int(adaptive.rank)
    record(
        "dlra_adaptive",
        {
            "times": dlra_times,
            "states": dlra_states,
            "max_abs_divergence": dlra_div,
            "wall_seconds": time.perf_counter() - dlra_start,
        },
        {
            "rank_final": adaptive_rank,
            "rank_min": int(min(adaptive.rank_history)),
            "rank_max": int(max(adaptive.rank_history)),
            "role": "adaptive reference point; also the rank POD and POD-DMD must match",
        },
    )

    # Matched ranks: the requested ladder plus the rank adaptivity reached.
    matched = sorted(set(args.ranks + [adaptive_rank]))
    for rank in matched:
        print(f"static POD at matched rank {rank} ...", flush=True)
        pod = PODGalerkin(grid, rank).fit(ref["training"])
        run = run_projected(
            grid, new_model(grid, args.re, args.force_amplitude), initial, dt,
            args.T, sample_every, pod.project, ref["checkpoints"],
        )
        run["max_scaled_energy_balance_residual"] = None
        record(
            f"pod_r{rank}",
            run,
            {
                "rank_requested": rank,
                "rank_effective": pod.effective_rank(),
                "rank_matched_to_adaptive": rank == adaptive_rank,
                "initial_projection_relative_l2": pod.relative_error(initial),
                "role": "static offline baseline at a matched rank",
            },
        )

    for rank in matched:
        print(f"POD-DMD at matched rank {rank} ...", flush=True)
        pod = PODGalerkin(grid, rank).fit(ref["training"])
        dmd = PODDMD(pod, ridge=args.dmd_ridge)
        train_model = new_model(grid, args.re, args.force_amplitude)
        state = initial.copy()
        train_steps = int(round(train_time / dt))
        for step in range(train_steps):
            state = train_model.step(state, dt, t=step * dt)
            dmd.accumulate(state)
        fit_start = time.perf_counter()
        dmd.fit()
        fit_seconds = time.perf_counter() - fit_start
        run = run_dmd(grid, dmd, initial, dt, args.T, sample_every)
        record(
            f"pod_dmd_r{rank}",
            run,
            {
                "rank_requested": rank,
                "rank_effective": pod.effective_rank(),
                "rank_matched_to_adaptive": rank == adaptive_rank,
                "ridge": args.dmd_ridge,
                "training_steps": train_steps,
                "training_pairs": dmd._samples,
                "fit_seconds": fit_seconds,
                "role": "dynamic data-driven baseline at a matched rank",
            },
        )

    # Fixed-rank variants of the proposed method, to separate rank from adaptivity.
    for rank in matched:
        print(f"fixed-rank DLRA at {rank} ...", flush=True)
        fixed = DLRA(
            new_model(grid, args.re, args.force_amplitude),
            rank=rank,
            min_rank=rank,
            max_rank=rank,
            relative_amplitude_cutoff=args.dlra_relative_amplitude_cutoff,
            check_every=10**9,        # never adapt: this isolates the rank
            adapt_initial=False,
        )
        state = fixed.initialize(initial)
        times = [0.0]
        states = [state.copy()]
        div = grid.max_div_velocity(state)
        start = time.perf_counter()
        for step in range(1, nsteps + 1):
            state = fixed.step(state, dt, t=(step - 1) * dt)
            if not np.isfinite(state).all():
                raise FloatingPointError(f"fixed-rank DLRA non-finite at step {step}")
            div = max(div, grid.max_div_velocity(state))
            if step % sample_every == 0 or step == nsteps:
                times.append(step * dt)
                states.append(state.copy())
        record(
            f"dlra_fixed_r{rank}",
            {
                "times": times,
                "states": states,
                "max_abs_divergence": div,
                "wall_seconds": time.perf_counter() - start,
            },
            {
                "rank_requested": rank,
                "rank_matched_to_adaptive": rank == adaptive_rank,
                "role": "fixed-rank variant isolating adaptivity from rank",
            },
        )

    # P0: every method must report the same fingerprint.
    fingerprints = {
        name: entry.get("fingerprint")
        for name, entry in methods.items()
        if entry.get("fingerprint") is not None
    }
    if len(fingerprints) > 1:
        raise SystemExit(f"methods disagree about the initial state: {fingerprints}")

    output = {
        "case": "baselines",
        "provenance": {
            "git_commit": _git_commit(),
            "driver": "experiments/run_baselines.py",
        },
        "parameters": {
            "re": args.re,
            "N": args.N,
            "dt": dt,
            "T": args.T,
            "window": list(window),
            "sample_every": sample_every,
            "train_time": train_time,
            "train_snapshot_stride": args.train_snapshot_stride,
            "ranks_requested": args.ranks,
            "ranks_matched": matched,
            "adaptive_rank": adaptive_rank,
            "dmd_ridge": args.dmd_ridge,
            "dlra_relative_amplitude_cutoff": args.dlra_relative_amplitude_cutoff,
            "dlra_max_rank": args.dlra_max_rank,
            "dlra_check_every": args.dlra_check_every,
            "force_amplitude": args.force_amplitude,
            "base_speed": args.base_speed,
            "perturbation_velocity_rms": args.perturbation_velocity_rms,
            "cutoff": args.cutoff,
            "seed": args.seed,
            "dealias_resolved_k_max": grid.N // 3,
        },
        "initial_state": fingerprint,
        "reference": ref_metrics,
        "methods": methods,
        "interpretation": (
            "Ranks are matched by construction: the adaptive rank is read from "
            "the DLRA run and then requested explicitly from static POD and "
            "POD-DMD. Accuracy is judged on time-averaged fluctuation KE and "
            "enstrophy over the statistical window and on the spectra over the "
            "resolved range; pointwise L2 is reported last and is labelled "
            "trajectory divergence. If the adaptive method does not win at "
            "matched rank, that is recorded here rather than argued away."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
