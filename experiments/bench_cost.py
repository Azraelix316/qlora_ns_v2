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
import hashlib
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


def provenance() -> dict:
    """Commit, plus whether the tree that ran is the commit that is named.

    A run started with uncommitted changes produces numbers from code that its
    recorded commit does not contain, which is the staleness D14.4 is about --
    just one commit further out, and therefore easy to miss.  The diff's hash is
    recorded so the exact code can be recovered.
    """
    commit = _git_commit()
    try:
        diff = subprocess.check_output(
            ["git", "diff", "HEAD"], cwd=ROOT, text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return {"git_commit": commit, "working_tree_dirty": None}
    return {
        "git_commit": commit,
        "working_tree_dirty": bool(diff.strip()),
        "working_tree_diff_sha256": hashlib.sha256(diff.encode()).hexdigest()
        if diff.strip() else None,
        "note": (
            "git_commit is HEAD at launch. If working_tree_dirty is true the run "
            "used uncommitted code that this commit does not contain; the diff "
            "hash recovers it."
        ),
    }


def thread_settings() -> dict:
    keys = (
        "OPENBLAS_NUM_THREADS",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    )
    return {key: os.environ.get(key) for key in keys}


def load_average() -> list[float] | None:
    """The node's load average, recorded because the node is shared.

    This machine also serves a language model, so its load moves with someone
    else's work.  Recording it is what lets a reader decide whether a large
    spread is the method or the neighbours, and it is the reason the protocol
    interleaves configurations: on a node this noisy the per-configuration median
    is unreliable while the ratio between two interleaved configurations is not.
    """
    try:
        return [float(x) for x in os.getloadavg()]
    except (OSError, AttributeError):
        return None


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
    # **Interleaved, not sequential.** Repeats are the outer loop and
    # configurations the inner one, so every configuration is measured once per
    # "round" and a slow patch of machine time -- the node is shared -- inflates
    # all of them together instead of penalising whichever one happened to run
    # during it. Timing all repeats of one configuration and then all repeats of
    # the next makes every cross-configuration ratio depend on when each block
    # ran, and on a shared node that produced spreads of 50% on one block and
    # 4% on the next, which is enough to invent or hide a rank-scaling effect.
    full_runs: list[float] = []
    runs: dict[int, list] = {r: [] for r in ranks}
    bug_runs: dict[int, list] = {r: [] for r in ranks if bug_ranks and r in bug_ranks}
    calls: dict[int, int] = {}

    full_step_seconds(model, state0, dt, warmup)          # discarded warm-up
    for rank in ranks:                                     # discarded warm-ups
        _, _, calls[rank] = reduced_step_seconds(N, rank, dt, warmup)
        if rank in bug_runs:
            bug_step_seconds(N, rank, dt, warmup)

    for _ in range(repeats):
        full_runs.append(full_step_seconds(model, state0, dt, steps))
        for rank in ranks:
            runs[rank].append(reduced_step_seconds(N, rank, dt, steps))
            if rank in bug_runs:
                bug_runs[rank].append(bug_step_seconds(N, rank, dt, steps))

    full_med = statistics.median(full_runs)
    rows = []
    for rank in ranks:
        # Both accountings come from the same runs, so they are directly
        # comparable rather than independently noisy.
        red_med = statistics.median([r[0] for r in runs[rank]])
        la_med = statistics.median([r[1] for r in runs[rank]])
        run_secs = [r[0] for r in runs[rank]]
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
                "svd_calls_per_step": calls[rank] / warmup,
                "full_step_ratio_vs_reference": red_med / full_med,
                "linear_algebra_ratio_vs_reference": la_med / full_med,
                "amplitude_1e_3_seconds_median": amp_med,
                "amplitude_cost_ratio": red_med / amp_med,
            }
        )
        # The BUG port, on the same protocol and the same state, and interleaved
        # with the projected runs above, so the two timings differ only in the
        # integrator.
        if rank in bug_runs:
            bug_secs = [b[0] for b in bug_runs[rank]]
            bug_med = statistics.median(bug_secs)
            rows[-1]["bug"] = {
                "full_step_seconds_median": bug_med,
                "full_step_seconds_min": min(bug_secs),
                "full_step_seconds_max": max(bug_secs),
                "full_step_seconds_per_step": bug_med / steps,
                "full_step_relative_spread": (max(bug_secs) - min(bug_secs)) / bug_med,
                "svd_seconds_median": statistics.median([b[1] for b in bug_runs[rank]]),
                "svd_calls_per_step": bug_runs[rank][0][2] / steps,
                "svd_max_dimension": bug_runs[rank][0][3],
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
        "protocol": (
            "interleaved: one round times the reference and every configuration "
            "once, so a slow patch of machine time inflates all of them together "
            "rather than whichever block happened to run during it"
        ),
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
    bug_ranks = args.bug_ranks

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
        # Compare the two ranks actually requested.  Hard-coding {2, 64} made
        # this section come out empty for any other ladder, which is a silently
        # missing result rather than a reported one.
        present = sorted(by_rank)
        if len(present) < 2:
            continue
        lo_rank, hi_rank = present[0], present[-1]
        lo = by_rank[lo_rank]["full_step_seconds_median"]
        hi = by_rank[hi_rank]["full_step_seconds_median"]
        lo_la = by_rank[lo_rank]["linear_algebra_seconds_median"]
        hi_la = by_rank[hi_rank]["linear_algebra_seconds_median"]
        row = {
            "N": entry["N"],
            "ranks_compared": [lo_rank, hi_rank],
            "full_step_ratio_hi_over_lo": hi / lo,
            "linear_algebra_ratio_hi_over_lo": hi_la / lo_la,
            "within_1p25": bool(hi / lo <= 1.25 and hi_la / lo_la <= 1.25),
        }
        # The port's claim is the opposite one: its cost should *scale* with the
        # rank, because that is what the O(N r^2) factor work means, while the
        # projected integrator's does not.
        if "bug" in by_rank[lo_rank] and "bug" in by_rank[hi_rank]:
            b_lo = by_rank[lo_rank]["bug"]["full_step_seconds_median"]
            b_hi = by_rank[hi_rank]["bug"]["full_step_seconds_median"]
            row["bug_full_step_ratio_hi_over_lo"] = b_hi / b_lo
            row["bug_rank_dependent"] = bool(b_hi / b_lo > 1.25)
            row["bug_speedup_lo"] = by_rank[lo_rank]["bug"]["speedup_over_projected_same_rank"]
            row["bug_speedup_hi"] = by_rank[hi_rank]["bug"]["speedup_over_projected_same_rank"]
        rank_independence.append(row)

    output = {
        # One shared family label so the cost artifacts are recognisably the same
        # kind of measurement, plus a variant so a reader can tell which
        # integrators a given file actually timed.  Two files both labelled
        # "cost_retiming" with nothing else is how a reader ends up comparing
        # them without knowing they timed different code.
        "case": "cost_retiming",
        "case_family": "cost",
        "case_variant": "projected+bug" if bug_ranks else "projected_only",
        "integrators_timed": (
            ["full_grid_reference", "projected_dlra", "midpoint_bug"]
            if bug_ranks else ["full_grid_reference", "projected_dlra"]
        ),
        "provenance": {
            **provenance(),
            "driver": "experiments/bench_cost.py",
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "processor": platform.processor() or "unknown",
            "thread_settings": thread_settings(),
            "load_average_at_end": load_average(),
            "shared_node_note": (
                "this node also serves a language model, so its load moves with "
                "someone else's work; the protocol interleaves configurations "
                "because on a node this noisy the per-configuration median is "
                "unreliable while the ratio between interleaved configurations "
                "is not"
            ),
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
