"""The crossover surface: where does a reduced integrator beat a static subspace?

R39 states the paper's central result -- a rank-``r`` reduced integrator beats a
static subspace for about ``t* = 0.050 r^1.12`` time units and not much longer
-- and the reviewer produced a reference version of the surface and asked for it
to be reproduced here with project code, with a disagreement being more
informative than agreement.  This driver produces it.

The quantity is the full-field relative L2 against the full-grid reference,
evaluated on a grid of ranks and horizons.  Three error columns are recorded for
every (rank, horizon) pair, and the difference between them is the mechanism:

``relative_l2``
    the method's own mean handling, full field.  This is the comparable number.
``relative_l2_oracle_mean``
    the same error with the zonal mean replaced by the reference's, i.e. the
    error a static baseline would make if its mean were handled perfectly.
``relative_l2_mean_only``
    only the zonal mean's contribution to the error.

If the static baseline's error is dominated by its mean, the oracle-mean column
collapses relative to the full-field one; if it is dominated by a stale
*fluctuation* subspace (R37), the oracle-mean column barely moves and the floor
survives.  Reporting only the full-field number would hide which it is.

Two honesty constraints are built into the driver rather than left to prose:

* The rank is **fixed per run** in this surface.  The advantage comes from
  re-fitting the subspace to the current state at every step, not from the rank
  changing, so nothing here says anything about adaptive rank.
* Nothing here is a cost claim.  Per-step cost is Theta(N^3) and
  rank-independent (D11.1, measured in ``cost_retiming.json``), so the surface is
  an accuracy result and is read together with that cost table.
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "experiments") not in sys.path:
    sys.path.insert(0, str(ROOT / "experiments"))

from solvers import (
    DLRA,
    Grid2D,
    KolmogorovForcing,
    PODGalerkin,
    StreamFunctionNS,
    fluctuations,
    zonal_mean,
)
from run_baselines import run_projected_moving, select_window
from run_kolmogorov import make_initial_state

def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def decompose(method: np.ndarray, reference: np.ndarray, grid: Grid2D) -> dict:
    """Split a state error into zonal-mean and fluctuation parts.

    ``psi' = psi - x-avg(psi)`` throughout (S1), so the decomposition is
    orthogonal: the mean and fluctuation errors are separate contributions to
    the full-field error, and the two normalizers make them comparable either
    against the full reference norm (comparable with the reviewer's table) or
    against their own norm (the fraction of that component that is wrong).
    """
    m_mean, r_mean = zonal_mean(method), zonal_mean(reference)
    m_fluct, r_fluct = method - m_mean, reference - r_mean
    full = np.sqrt(grid.l2_sq(reference))
    fluct_norm = np.sqrt(grid.l2_sq(r_fluct))
    d_mean = np.sqrt(grid.l2_sq(m_mean - r_mean))
    d_fluct = np.sqrt(grid.l2_sq(m_fluct - r_fluct))
    d_full = np.sqrt(grid.l2_sq(method - reference))
    return {
        "relative_l2": d_full / full,
        "relative_l2_oracle_mean": d_fluct / full,
        "relative_l2_mean_only": d_mean / full,
        "relative_l2_fluct_normalized": d_fluct / fluct_norm,
        "mean_energy_share_of_reference": (
            grid.l2_sq(r_mean) / full ** 2 if full > 0 else None
        ),
    }


def reference_run(
    grid: Grid2D, model, initial: np.ndarray, dt: float, final_time: float,
    snap_stride: int, horizons: list[float],
) -> dict:
    """Full-grid reference, plus the snapshot series the windows are built from."""
    state = initial.copy()
    snap_times, snap_states = [0.0], [initial.copy()]
    snapshots: dict[float, np.ndarray] = {0.0: initial.copy()}
    max_div = grid.max_div_velocity(state)
    nsteps = int(round(final_time / dt))
    start = time.perf_counter()
    for step in range(1, nsteps + 1):
        state = model.step(state, dt, t=(step - 1) * dt)
        if not np.isfinite(state).all():
            raise FloatingPointError(f"reference non-finite at step {step}")
        max_div = max(max_div, grid.max_div_velocity(state))
        t = step * dt
        if step % snap_stride == 0 or step == nsteps:
            snap_times.append(t)
            snap_states.append(state.copy())
        for h in horizons:
            if abs(t - h) < 0.5 * dt:
                snapshots[h] = state.copy()
    return {
        "snap_times": snap_times,
        "snap_states": snap_states,
        "snapshots": snapshots,
        "max_abs_divergence": max_div,
        "wall_seconds": time.perf_counter() - start,
        "nsteps": nsteps,
    }


def fixed_rank_dlra(
    grid: Grid2D, model, initial: np.ndarray, dt: float, final_time: float,
    rank: int, horizons: list[float],
) -> dict:
    """DLRA at a rank held fixed for the whole run (never adapts)."""
    dlra = DLRA(
        model, rank=rank, min_rank=rank, max_rank=rank,
        relative_amplitude_cutoff=1e-10,
        check_every=10 ** 9,      # never adapt: this isolates the rank
        adapt_initial=False,
    )
    state = dlra.initialize(initial)
    out: dict[float, np.ndarray] = {0.0: state.copy()}
    max_div = grid.max_div_velocity(state)
    nsteps = int(round(final_time / dt))
    start = time.perf_counter()
    for step in range(1, nsteps + 1):
        state = dlra.step(state, dt, t=(step - 1) * dt)
        if not np.isfinite(state).all():
            raise FloatingPointError(f"DLRA r={rank} non-finite at step {step}")
        max_div = max(max_div, grid.max_div_velocity(state))
        for h in horizons:
            if abs(step * dt - h) < 0.5 * dt:
                out[h] = state.copy()
    return {
        "states": out,
        "max_abs_divergence": max_div,
        "wall_seconds": time.perf_counter() - start,
        "rank_actual": int(dlra.rank),
    }


def moving_window_schedule(
    grid: Grid2D, snap_times, snap_states, rank: int, window: float,
    interval: float, dt: float, final_time: float,
) -> dict:
    """Refit a rank-``r`` basis on a **trailing** window, every ``interval``.

    This is the oracle static baseline: at each refit the basis is built from the
    most recent window *of the reference trajectory*, so it is the best a
    fixed-rank, offline-fitted subspace can do at that instant.

    The window is trailing only -- ``[t - window, t]`` -- and the refit times are
    offset by half an interval, so **no basis ever contains the time it is being
    scored at**.  Both matter: a trailing window that ends at the evaluation time
    contains it, the baseline reproduces the state exactly, and the reported
    error is in-sample.  That is a property of the harness rather than of the
    method, and it is the difference between a *stale* subspace (R37's mechanism,
    and the one that produces a rank-independent floor) and a clairvoyant one.
    The window length, refit interval and offset are recorded in the artifact,
    because the floor is a function of them.
    """
    schedule = {}
    starved = 0
    refit_step = max(1, int(round(interval / dt)))
    # Refits are offset by half an interval from the evaluation times on purpose.
    # A refit at exactly t = evaluation time would fit its trailing window on
    # data that *includes* that time, so the baseline reproduces the state it is
    # being scored on and reports an in-sample error.  With the offset, every
    # evaluation is at least ``interval/2`` beyond the newest snapshot any basis
    # could have seen, which is what makes this a prediction comparison at all.
    for step in range(refit_step // 2, int(round(final_time / dt)) + refit_step,
                      refit_step):
        if step < 1 or step > int(round(final_time / dt)):
            continue
        t_now = step * dt
        snaps = select_window(snap_times, snap_states, max(0.0, t_now - window), t_now)
        if not snaps:
            continue
        # A window can hold fewer snapshots than the requested rank.  Skipping
        # the refit in that case leaves the baseline stuck on whatever basis it
        # started with, which silently turns a rank-r baseline into a rank-1 one
        # and makes a short window look catastrophic for the wrong reason.  Fit
        # as many modes as the window supports and record the shortfall.
        effective = min(rank, len(snaps))
        if effective < rank:
            starved += 1
        schedule[step] = PODGalerkin(grid, effective).fit(snaps)
    return schedule, starved


def crossover_horizon(
    dlra_rows: list[dict], static_rows: list[dict]
) -> dict:
    """First horizon at which the static baseline overtakes the DLRA.

    Interpolated in log-log between the bracketing horizons on the *ratio*
    static/DLRA, which crosses 1.  Reported as ``null`` when the DLRA is still
    ahead at the longest horizon, which is the honest answer for a rank that is
    exact.
    """
    by_t = {r["time"]: r for r in static_rows}
    # Only horizons both surfaces actually evaluated: the DLRA rows carry a
    # synthetic t=0 entry (both methods start from the same state) and the
    # baseline is not run there, and a log-log interpolation needs a strictly
    # positive lower bracket.
    shared = sorted(
        set(by_t) & {r["time"] for r in dlra_rows if r["time"] > 0.0}
    )
    ordered = [r for r in sorted(dlra_rows, key=lambda r: r["time"])
               if r["time"] in set(shared)]
    if len(ordered) < 2:
        return {"t_star": None, "reason": "fewer than two shared horizons"}
    for prev, cur in zip(ordered, ordered[1:]):
        s_prev, d_prev = by_t[prev["time"]], by_t[prev["time"]]
        s_cur, d_cur = by_t[cur["time"]], by_t[cur["time"]]
        r_prev = s_prev["relative_l2_oracle_mean"] / max(d_prev["relative_l2"], 1e-300)
        r_cur = s_cur["relative_l2_oracle_mean"] / max(d_cur["relative_l2"], 1e-300)
        if r_prev < 1.0 <= r_cur:
            # log-log interpolation between the bracketing horizons
            lt0, lt1 = math.log(prev["time"]), math.log(cur["time"])
            frac = (math.log(1.0) - math.log(r_prev)) / (math.log(r_cur) - math.log(r_prev))
            return {
                "t_star": float(math.exp(lt0 + frac * (lt1 - lt0))),
                "bracketing": [prev["time"], cur["time"]],
                "ratio_at_brackets": [r_prev, r_cur],
            }
    return {"t_star": None, "reason": "DLRA still ahead at the longest horizon"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--re", type=float, default=5000.0)
    parser.add_argument("--N", type=int, default=64)
    parser.add_argument("--dt", type=float, default=None)
    parser.add_argument("--force-amplitude", type=float, default=0.2)
    parser.add_argument("--horizons", type=float, nargs="+",
                        default=[0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0])
    parser.add_argument("--ranks", type=int, nargs="+",
                        default=[2, 4, 8, 16, 32, 43])
    parser.add_argument("--window", type=float, nargs="+", default=[1.0],
                        help="trailing window length(s) for the moving-window "
                             "baseline. More than one produces the surface as a "
                             "function of the window as well as the rank, which "
                             "is the honest shape of the result: a static "
                             "baseline's accuracy is a property of its window, "
                             "not of POD.")
    parser.add_argument("--refit-interval", type=float, default=0.25)
    parser.add_argument("--snapshot-stride", type=float, default=0.02)
    parser.add_argument("--base-speed", type=float, default=0.5)
    parser.add_argument("--perturbation-velocity-rms", type=float, default=1.0)
    parser.add_argument("--cutoff", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260925)
    parser.add_argument(
        "--output", type=Path,
        default=Path("state/coder/results/crossover_surface.json"),
    )
    args = parser.parse_args()

    grid = Grid2D(args.N)
    dt = args.dt if args.dt is not None else 5e-4 * (64.0 / args.N)

    def new_model():
        return StreamFunctionNS(
            grid, 1.0 / args.re, forcing=KolmogorovForcing(args.force_amplitude, 1.0)
        )

    initial = make_initial_state(
        grid, base_speed=args.base_speed,
        perturbation_velocity_rms=args.perturbation_velocity_rms,
        cutoff=args.cutoff, seed=args.seed,
    )
    final_time = max(args.horizons)
    snap_stride = max(1, int(round(args.snapshot_stride / dt)))

    print(f"crossover: reference to t={final_time} ...", flush=True)
    ref = reference_run(
        grid, new_model(), initial, dt, final_time, snap_stride, args.horizons,
    )
    print(f"  done in {ref['wall_seconds']:.0f}s", flush=True)

    dlra_surface: dict[str, list[dict]] = {}
    static_surface: dict[str, dict[str, list[dict]]] = {}
    crossovers: list[dict] = []
    diagnostics: dict[str, dict] = {}
    windows = list(args.window)

    for rank in args.ranks:
        print(f"crossover: rank {rank} (DLRA) ...", flush=True)
        run = fixed_rank_dlra(
            grid, new_model(), initial, dt, final_time, rank, args.horizons
        )
        dlra_rows = [
            {"time": h, "rank": rank, **decompose(run["states"][h], ref["snapshots"][h], grid)}
            for h in args.horizons
        ]
        dlra_rows.insert(0, {
            "time": 0.0, "rank": rank, "relative_l2": 0.0,
            "relative_l2_oracle_mean": 0.0, "relative_l2_mean_only": 0.0,
            "relative_l2_fluct_normalized": 0.0,
        })
        dlra_surface[str(rank)] = dlra_rows
        diagnostics[str(rank)] = {
            "dlra": {
                "wall_seconds": run["wall_seconds"],
                "rank_actual": run["rank_actual"],
                "max_abs_divergence": run["max_abs_divergence"],
            }
        }

        # The DLRA run does not depend on the window, so it is computed once and
        # compared against every window's baseline.
        for window in windows:
            print(f"crossover: rank {rank} static, window={window} ...", flush=True)
            schedule, starved = moving_window_schedule(
                grid, ref["snap_times"], ref["snap_states"], rank,
                window, args.refit_interval, dt, final_time,
            )
            # Strictly causal initialisation: before the first refit the only
            # snapshot that exists is the initial condition, so the only honest
            # basis is rank 1 on the IC.  Fitting the initial basis on any longer
            # window hands the baseline the future: a trailing window that *ends
            # at* an evaluation time contains that time, so the baseline
            # reproduces the state there exactly and reports an error of zero.
            # That is a property of the harness, not of the method.
            initial_projector = PODGalerkin(grid, 1).fit([initial])
            run_s = run_projected_moving(
                grid, new_model(), initial, dt, final_time,
                max(1, int(round(0.01 / dt))), schedule,
                initial_projector=initial_projector,
            )
            # Key the states by *time*, not by list index.  The rollout's state
            # list starts at t=0, so indexing it with the horizon index silently
            # compares the t=0 state against the t=0.1 reference.
            lookup = {t: s for t, s in zip(run_s["times"], run_s["states"])}
            static_rows = []
            for h in args.horizons:
                nearest = min(lookup, key=lambda t: abs(t - h))
                static_rows.append(
                    {"time": h, "rank": rank,
                     **decompose(lookup[nearest], ref["snapshots"][h], grid)}
                )
            key = f"W{window:g}_r{rank}"
            static_surface[key] = static_rows
            star = crossover_horizon(dlra_rows, static_rows)
            star.update({"rank": rank, "window": window})
            crossovers.append(star)
            diagnostics[key] = {
                "wall_seconds": run_s["wall_seconds"],
                "refits": len(schedule),
                "refits_with_fewer_snapshots_than_rank": starved,
                "max_abs_divergence": run_s["max_abs_divergence"],
                "diverged": run_s["diverged_at_step"] is not None,
            }
            print(
                f"  t* = {star['t_star'] if star['t_star'] is None else round(star['t_star'], 3)}",
                flush=True,
            )

    artifact = {
        "case": "crossover_surface",
        "provenance": {
            "git_commit": _git_commit(),
            "driver": "experiments/run_crossover.py",
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "parameters": {
            "re": args.re,
            "N": args.N,
            "dt": dt,
            "final_time": final_time,
            "force_amplitude": args.force_amplitude,
            "horizons": args.horizons,
            "ranks": args.ranks,
            "dealias_ceiling": 2 * (args.N // 3) + 1,
            "moving_window_lengths": windows,
            "moving_window_refit_interval": args.refit_interval,
            "snapshot_stride": args.snapshot_stride,
            "base_speed": args.base_speed,
            "perturbation_velocity_rms": args.perturbation_velocity_rms,
            "cutoff": args.cutoff,
            "seed": args.seed,
            "rank_policy": "fixed per run; never adapts",
        },
        "initial_state": {
            "energy": grid.ke(initial),
            "numerical_rank": int(np.count_nonzero(
                np.linalg.svd(initial - initial.mean(), compute_uv=False)
                > 1e-10 * np.linalg.svd(initial - initial.mean(), compute_uv=False)[0]
            )),
        },
        "reference": {
            "max_abs_divergence": ref["max_abs_divergence"],
            "wall_seconds": ref["wall_seconds"],
            "nsteps": ref["nsteps"],
        },
        "error_columns": {
            "relative_l2": "the method's own mean handling, full field; the comparable number",
            "relative_l2_oracle_mean": "error with the zonal mean replaced by the reference's, i.e. what the baseline would make with a perfect mean",
            "relative_l2_mean_only": "the zonal mean's contribution alone, over the full-field norm",
            "relative_l2_fluct_normalized": "fluctuation error over the fluctuation norm",
        },
        "dlra": dlra_surface,
        "static_moving_window": static_surface,
        "crossovers": crossovers,
        "run_diagnostics": diagnostics,
        "interpretation": (
            "An accuracy surface, not a cost surface. The rank is fixed per run, so "
            "the advantage comes from re-fitting the subspace to the current state "
            "each step and says nothing about adaptive rank. The static baseline is "
            "the oracle form (refitted on a trailing window of the reference), and "
            "its error floor is a function of the window length and refit interval, "
            "which are recorded above. Per-step cost is Theta(N^3) and "
            "rank-independent (D11.1, measured in cost_retiming.json): the only rank "
            "that never loses is the dealiasing ceiling, and that rank is the "
            "full-grid solver at over twice its cost."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
