"""R5q cost re-timing: two accountings, thread-pinned, with spread.

The gate has three parts and this script is the evidence for all of them.

1. **Two accountings, never conflated.** ``linear_algebra`` is the measured
   time inside the whole-field SVDs; ``full_step`` is the wall time of a
   complete reduced step, which also pays the full-grid nonlinear evaluation
   that the reference pays too.  A win in the first is not a per-step win
   (D11.1), and this script reports the ratio against the full grid for both.
2. **Rank independence.** ``SVDProjector`` factorizes the whole N x N field,
   so per-step cost must not depend on the retained rank.  The rank sweep
   checks r=2 against r=64 within a factor 1.25 at every N.
3. **Affordability.** Median over >=7 repeats after a discarded warm-up, with
   the spread reported, over a >=2000-step measurement region, so the numbers
   are not a cache-warm artifact.  Thread counts are pinned *and recorded*,
   because the committed timings were taken with a default multi-threaded
   LAPACK and are not reproducible.

Run from the repository root::

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
      ~/.venvs/ns/bin/python experiments/bench_cost.py
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from solvers import BUGIntegrator, DLRA, Grid2D, StreamFunctionNS, ZeroForcing


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def thread_settings() -> dict:
    keys = (
        "OPENBLAS_NUM_THREADS",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    )
    return {key: os.environ.get(key) for key in keys}


def make_state(grid: Grid2D, seed: int = 20260925, amplitude: float = 1.0) -> np.ndarray:
    """A bounded, smooth multi-mode state for the cost measurement.

    The cost question is "how long does a reduced step take", and the answer is
    set by the whole-field SVD (Theta(N^3)) plus the full-grid nonlinear
    evaluation -- neither depends on the state's content.  The canonical forced
    IC is deliberately *not* used here: holding a fixed low rank for thousands
    of steps on a forced field drives the state to extreme magnitudes, and
    LAPACK then fails to converge, which is a statement about that
    configuration rather than about cost.  ``measure`` verifies the
    content-independence claim instead of asserting it, by repeating the
    measurement at a second amplitude.
    """
    X, Y = np.meshgrid(grid.x, grid.y, indexing="ij")
    field = (
        np.sin(X) * np.sin(Y)
        + 0.5 * np.cos(2 * X) * np.sin(Y)
        + 0.25 * np.sin(3 * X) * np.cos(2 * Y)
    )
    field = field - field.mean()
    return float(amplitude) * field


def full_step_seconds(model: StreamFunctionNS, state, dt: float, steps: int) -> float:
    start = time.perf_counter()
    for i in range(steps):
        state = model.step(state, dt, t=i * dt)
    elapsed = time.perf_counter() - start
    if not np.isfinite(state).all():
        raise FloatingPointError("reference step went non-finite")
    return elapsed


def reduced_step_seconds(
    N: int, rank: int, dt: float, steps: int, amplitude: float = 1.0
) -> tuple[float, float, int]:
    """Return (full_step_seconds, linear_algebra_seconds, svd_calls)."""
    grid = Grid2D(N)
    # Unforced: the cost of a step is independent of the forcing, and an
    # unforced decay keeps the benchmark state bounded for a long run.
    model = StreamFunctionNS(grid, nu=0.02, forcing=ZeroForcing(), dealias=True)
    dlra = DLRA(
        model,
        rank=rank,
        min_rank=1,
        max_rank=grid.N,
        relative_amplitude_cutoff=1e-10,
        check_every=10**9,   # hold the rank fixed: this measures cost, not adaptation
        adapt_initial=False,
    )
    state = dlra.initialize(make_state(grid, amplitude=amplitude))
    start = time.perf_counter()
    for i in range(steps):
        state = dlra.step(state, dt, t=i * dt)
    elapsed = time.perf_counter() - start
    if not np.isfinite(state).all():
        raise FloatingPointError("reduced step went non-finite")
    return elapsed, dlra.projector.svd_seconds, dlra.projector.svd_calls


def bug_step_seconds(
    N: int, rank: int, dt: float, steps: int, amplitude: float = 1.0
) -> tuple[float, float, int, int]:
    """Return (full_step_seconds, svd_seconds, svd_calls, svd_max_dimension).

    Same protocol as :func:`reduced_step_seconds` -- same unforced state, same
    held rank, warm-up discarded by the caller -- so the BUG timing and the
    projected timing are directly comparable.  The rank is held fixed by
    ``min_rank == max_rank``; this measures cost, not adaptation.
    """
    grid = Grid2D(N)
    model = StreamFunctionNS(grid, nu=0.02, forcing=ZeroForcing(), dealias=True)
    bug = BUGIntegrator(
        model,
        rank=rank,
        min_rank=rank,
        max_rank=rank,
        relative_amplitude_cutoff=1e-10,
        substeps=2,
    )
    state = bug.initialize(make_state(grid, amplitude=amplitude))
    start = time.perf_counter()
    for i in range(steps):
        state = bug.step(dt=dt, t=i * dt)
    elapsed = time.perf_counter() - start
    if not np.isfinite(state).all():
        raise FloatingPointError("BUG step went non-finite")
    return elapsed, bug.svd_seconds, bug.svd_calls, bug.svd_max_dimension


def measure(
    N: int,
    ranks: list[int],
    steps: int,
    repeats: int,
    warmup: int,
    dt: float,
    amplitude_check: bool = True,
    bug_ranks: list[int] | None = None,
) -> dict:
    grid = Grid2D(N)
    model = StreamFunctionNS(grid, nu=0.02, forcing=ZeroForcing(), dealias=True)
    state0 = make_state(grid)

    # Discarded warm-up: first touch of every buffer, and the LAPACK handle.
    full_step_seconds(model, state0, dt, warmup)
    full_runs = [full_step_seconds(model, state0, dt, steps) for _ in range(repeats)]

    rows = []
    for rank in ranks:
        # Warm-up, discarded: it also reports the per-step SVD call count.
        _, _, calls = reduced_step_seconds(N, rank, dt, warmup)
        runs = [reduced_step_seconds(N, rank, dt, steps) for _ in range(repeats)]
        # Both accountings come from the same runs, so they are directly
        # comparable rather than independently noisy.
        red_med = statistics.median([r[0] for r in runs])
        la_med = statistics.median([r[1] for r in runs])
        run_secs = [r[0] for r in runs]
        full_med = statistics.median(full_runs)
        # Content-independence, measured rather than assumed: the same step at
        # a 1e-3 amplitude must cost the same.
        amp_med = statistics.median(
            [reduced_step_seconds(N, rank, dt, steps, amplitude=1e-3)[0]
             for _ in range(max(2, repeats // 3))]
        ) if amplitude_check else red_med
        rows.append(
            {
                "rank": rank,
                "full_step_seconds_median": red_med,
                "full_step_seconds_min": min(run_secs),
                "full_step_seconds_max": max(run_secs),
                "full_step_seconds_per_step": red_med / steps,
                "full_step_relative_spread": (max(run_secs) - min(run_secs)) / red_med,
                "linear_algebra_seconds_median": la_med,
                "linear_algebra_seconds_per_step": la_med / steps,
                "svd_calls_per_step": calls / warmup,
                "full_step_ratio_vs_reference": red_med / full_med,
                "linear_algebra_ratio_vs_reference": la_med / full_med,
                "amplitude_1e_3_seconds_median": amp_med,
                "amplitude_cost_ratio": red_med / amp_med,
            }
        )
        # The BUG port, on the same protocol and the same state, so the two
        # timings differ only in the integrator.
        if bug_ranks is not None and rank in bug_ranks:
            bug_step_seconds(N, rank, dt, warmup)          # discarded warm-up
            bug_runs = [bug_step_seconds(N, rank, dt, steps) for _ in range(repeats)]
            bug_secs = [b[0] for b in bug_runs]
            bug_med = statistics.median(bug_secs)
            rows[-1]["bug"] = {
                "full_step_seconds_median": bug_med,
                "full_step_seconds_min": min(bug_secs),
                "full_step_seconds_max": max(bug_secs),
                "full_step_seconds_per_step": bug_med / steps,
                "full_step_relative_spread": (max(bug_secs) - min(bug_secs)) / bug_med,
                "svd_seconds_median": statistics.median([b[1] for b in bug_runs]),
                "svd_calls_per_step": bug_runs[0][2] / steps,
                "svd_max_dimension": bug_runs[0][3],
                "full_step_ratio_vs_reference": bug_med / full_med,
                "speedup_over_projected_same_rank": red_med / bug_med,
                "note": (
                    "same state, same held rank, same warm-up and repeat count; "
                    "the only factorization inside a BUG step is of the "
                    "augmented S-matrix, so svd_max_dimension is at most 4r"
                ),
            }
    return {
        "N": N,
        "steps_per_repeat": steps,
        "repeats": repeats,
        "warmup_steps_discarded": warmup,
        "dt": dt,
        "benchmark_state": (
            "unforced multi-mode decay (nu=0.02, ZeroForcing) at amplitude 1, "
            "with an amplitude-1e-3 repeat to measure content-independence"
        ),
        "reference_full_step_seconds_median": statistics.median(full_runs),
        "reference_full_step_seconds_per_step": statistics.median(full_runs) / steps,
        "reference_relative_spread": (
            max(full_runs) - min(full_runs)
        ) / statistics.median(full_runs),
        "dealias_rank_ceiling": 2 * (N // 3) + 1,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grids", type=int, nargs="+", default=[64, 128, 256])
    parser.add_argument("--ranks", type=int, nargs="+", default=[2, 64])
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--warmup", type=int, default=200)
    parser.add_argument(
        "--bug-ranks", type=int, nargs="*", default=None,
        help="ranks at which to also time the BUG port, on the same protocol; "
             "omit to time the projected integrator only",
    )
    parser.add_argument("--dt", type=float, default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("state/coder/results/cost_retiming.json"),
    )
    args = parser.parse_args()

    grids = []
    for N in args.grids:
        # dt scales with dx so the CFL number is held fixed across grids (P0
        # item 3/4): the canonical N=64 run uses dt=5e-4 at CFL 0.0147.
        dt = args.dt if args.dt is not None else 5e-4 * (64.0 / N)
        print(f"timing N={N} ranks={args.ranks} ...", flush=True)
        grids.append(
            measure(
                N, args.ranks, args.steps, args.repeats, args.warmup, dt,
                bug_ranks=args.bug_ranks,
            )
        )

    rank_independence = []
    for entry in grids:
        by_rank = {row["rank"]: row for row in entry["rows"]}
        if set(by_rank) >= {2, 64}:
            lo = by_rank[2]["full_step_seconds_median"]
            hi = by_rank[64]["full_step_seconds_median"]
            lo_la = by_rank[2]["linear_algebra_seconds_median"]
            hi_la = by_rank[64]["linear_algebra_seconds_median"]
            row = {
                "N": entry["N"],
                "full_step_ratio_r64_over_r2": hi / lo,
                "linear_algebra_ratio_r64_over_r2": hi_la / lo_la,
                "within_1p25": bool(hi / lo <= 1.25 and hi_la / lo_la <= 1.25),
            }
            # The port's claim is the opposite one: its cost should *scale* with
            # the rank, because that is what the O(N r^2) factor work means.
            if "bug" in by_rank[2] and "bug" in by_rank[64]:
                b_lo = by_rank[2]["bug"]["full_step_seconds_median"]
                b_hi = by_rank[64]["bug"]["full_step_seconds_median"]
                row["bug_full_step_ratio_r64_over_r2"] = b_hi / b_lo
                row["bug_rank_dependent"] = bool(b_hi / b_lo > 1.25)
                row["bug_speedup_r2"] = by_rank[2]["bug"]["speedup_over_projected_same_rank"]
                row["bug_speedup_r64"] = by_rank[64]["bug"]["speedup_over_projected_same_rank"]
            rank_independence.append(row)

    output = {
        "case": "cost_retiming",
        "provenance": {
            "git_commit": _git_commit(),
            "driver": "experiments/bench_cost.py",
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "processor": platform.processor() or "unknown",
            "thread_settings": thread_settings(),
        },
        "method": {
            "accountings": {
                "full_step": "wall time of a complete reduced step, including the "
                             "full-grid nonlinear evaluation and all projections",
                "linear_algebra": "measured time inside the whole-field SVD calls",
            },
            "rank_held_fixed": "check_every is set beyond the run, so cost is "
                               "measured at a fixed rank rather than under adaptation",
            "benchmark_state": "unforced multi-mode decay; the forced IC is not "
                               "used because a fixed low rank on a forced field "
                               "grows unboundedly and makes LAPACK fail, which is "
                               "a property of that configuration and not of cost. "
                               "An amplitude-1e-3 repeat measures the "
                               "content-independence claim rather than assuming it.",
            "why": "the factorization is of the whole N x N field, so it is "
                   "rank-independent and Theta(N^3); a linear-algebra win is "
                   "not a per-step win",
        },
        "grids": grids,
        "rank_independence": rank_independence,
        "interpretation": (
            "Per-step cost is reported as a ratio against the pinned-thread "
            "full-grid reference under both accountings. No per-step speedup is "
            "claimed anywhere: the reduced method pays the same full-grid "
            "nonlinear evaluation as the reference plus its own factorization."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
