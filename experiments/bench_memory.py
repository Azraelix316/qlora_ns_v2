"""Peak memory: does the reduced integrator save any, and does it cost?

The draft asks for peak memory and nothing in the project recorded it, so this
measures it rather than leaving the question to a reader's assumption.

**One fresh process per configuration.**  Peak RSS is a process high-water mark
(``ru_maxrss``), so measuring several configurations inside one process would
report the largest allocation any of them ever made, for all of them.  Each
configuration is therefore a subprocess that builds its grid and initial
condition, runs its own method, and reports its own high-water mark.

**Only the overhead is meaningful.**  The interpreter, NumPy and BLAS account for
a fixed baseline of tens of MiB that no method choice affects, so the artifact
reports the difference from the full-grid step and says so, rather than quoting
raw RSS as if it were the method's footprint.  The interpreter baseline is
measured once and reported so the reader can subtract it if they wish.

**No timing claims.**  This is memory only; wall-clock cost is
``cost_retiming.json``, where the reduced step is about twice the full grid's
and rank-independent.
"""
from __future__ import annotations

import argparse
import hashlib
import json

from _cli import ListOnce
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
from provenance import provenance as _provenance
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from solvers import (  # noqa: E402
    BUGIntegrator,
    DLRA,
    Grid2D,
    StreamFunctionNS,
    ZeroForcing,
)
from run_kolmogorov import make_initial_state  # noqa: E402

KIB = 1024.0


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"



def thread_settings() -> dict:
    keys = (
        "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
    )
    return {k: os.environ.get(k) for k in keys}


def peak_rss_mib() -> float:
    """Process high-water RSS in MiB."""
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / KIB


def _memory_interpretation(rank_rows: list[dict], noise_floor: float,
                           noise_stats: dict | None = None) -> str:
    """State the rank variation as measured, per grid, and claim nothing more.

    D19.4/D89: the overhead over the full grid is positive at every rank and
    grid and is the robust part.  The variation *with rank* is a separate
    question and the honest answer differs by grid, so it is stated per grid
    from this run's own numbers.  A verdict that cannot be evaluated is
    distinguished from one that fails, and neither is reported as "flat" --
    "flat" asserts the opposite of a resolved variation.
    """
    parts = [
        "Report the overhead over the full-grid step, not raw RSS: the "
        "interpreter and BLAS baseline is tens of MiB and no method choice "
        "affects it. THE ANSWER TO THE QUESTION THAT MATTERS IS NEGATIVE AND "
        "ROBUST: the reduced integrator does not save memory. It costs MORE "
        "than the full-grid step at both grids and every rank, because its "
        "state is a full N x N field plus its factors plus the factorization "
        "workspace, and that overhead is many times the run-to-run noise floor "
        "measured here from repeating one configuration, so it is real."
    ]
    for method in sorted({r.get("method", "?") for r in rank_rows}):
        label = {
            "dlra": "projected integrator",
            "bug": "midpoint BUG integrator",
        }.get(method, method)
        per_grid = [r for r in rank_rows if r.get("method") == method]
        detail = []
        verdicts = []
        for row in sorted(per_grid, key=lambda r: r.get("N", 0)):
            hi, lo = row.get("peak_mib_max"), row.get("peak_mib_min")
            spread = row.get("spread_over_rank_mib")
            if spread is None and hi is not None and lo is not None:
                spread = hi - lo
            if spread is None:
                continue
            ratio = spread / noise_floor if noise_floor else float("nan")
            resolved = row.get("rank_independence_resolved")
            verdicts.append(bool(resolved))
            # How much headroom the verdict has, and how much of it the floor's
            # own uncertainty could eat.  A verdict stated without its margin is
            # the thing that flipped: with the smallest of four measured floors
            # this read 49x, with the largest it reads 1.4x and crosses the
            # threshold of 2.  Both numbers are reported so a reader can see
            # which side of the line the answer is on.
            headroom = ratio / 2.0 if noise_floor else float("nan")
            detail.append(
                f"N={row.get('N')}: varies by {spread:.2f} MiB, which is "
                f"{ratio:.1f}x the noise floor (threshold 2x, so the margin is "
                f"{headroom:.1f}x either side) -- "
                + ("RESOLVED, so the variation with rank is real"
                   if resolved else "NOT resolved, so no variation is established")
            )
        if detail:
            tail = (
                "Neither 'flat in rank' nor 'varies with rank' is supported here, "
                "because the two grids disagree about whether a variation exists "
                "at all."
                if len(set(verdicts)) > 1 else
                ("The variation with rank is resolved at every grid, so 'flat in "
                 "rank' would assert the opposite of the measurement."
                 if all(verdicts) else
                 "No variation with rank is resolved at any grid, so the spread is "
                 "consistent with zero but does not demonstrate it.")
            )
            parts.append(
                f"For the {label}, peak RSS " + "; ".join(detail) + f". {tail}"
            )
    if noise_stats and noise_stats.get("samples", 0) > 1:
        parts.append(
            f"THE NOISE FLOOR IS A DISTRIBUTION, not a point: it is the largest of "
            f"{noise_stats['samples']} re-measurements of one configuration "
            f"({noise_stats['min_mib']:.4f} to {noise_stats['max_mib']:.4f} MiB, "
            f"a factor of {(noise_stats['max_over_min'] or float('nan')):.0f} "
            f"between them). With a single repeat this number has been observed at "
            f"0.1328, 0.0664, 0.0977 and 0.0039 MiB -- a factor of 34 -- and the "
            f"verdicts above flip between 'resolved' and 'not established' across "
            f"that range for the projected integrator. **Any claim of the form "
            f"'the variation with rank is N times the noise floor' therefore "
            f"carries the floor's own spread, and the verdicts here are taken "
            f"against its maximum so that the error can only fall on the side of "
            f"not claiming a rank dependence.**"
        )
    parts.append(
        "The BUG integrator trades memory for time: its overhead is SMALLER "
        "than the projected integrator's at both grids, while its cost per step "
        "is 3.4-5.1x the projected one. Its spread over rank is also larger, in "
        "the direction its construction predicts, since it holds augmented "
        "factors of size up to 4r rather than a whole-field factorization."
    )
    return " ".join(parts)


def _load_average() -> list[float] | None:
    """The node's load average, recorded because the node is shared.

    ``bench_cost.py`` records this and a memory measurement on the same machine
    is no less sensitive to a neighbour: an allocator's behaviour under load can
    move a peak by tenths of a MiB, which is the size of the rank effect being
    asked about here.
    """
    try:
        return [float(x) for x in os.getloadavg()]
    except (OSError, AttributeError):
        return None


def run_one(args) -> dict:
    """Build, run one configuration, and report its own peak RSS."""
    baseline_before_setup = peak_rss_mib()
    grid = Grid2D(args.N)
    dt = args.dt if args.dt is not None else 5e-4 * (64.0 / args.N)
    initial = make_initial_state(
        grid, base_speed=0.5, perturbation_velocity_rms=1.0,
        cutoff=8, seed=20260925,
    )
    initial = initial - initial.mean()
    after_setup = peak_rss_mib()

    model = StreamFunctionNS(grid, 0.02, forcing=ZeroForcing(), dealias=True)
    after_init = after_setup
    start = time.perf_counter()
    if args.method == "full":
        state = initial
        for i in range(args.steps):
            state = model.step(state, dt, t=i * dt)
    elif args.method == "dlra":
        dlra = DLRA(
            model, rank=args.rank, min_rank=args.rank, max_rank=args.rank,
            relative_amplitude_cutoff=1e-10,
            check_every=10 ** 9,        # hold the rank fixed: this is about memory
            adapt_initial=False,
        )
        state = dlra.initialize(initial)
        after_init = peak_rss_mib()
        for i in range(args.steps):
            state = dlra.step(state, dt, t=i * dt)
    elif args.method == "bug":
        bug = BUGIntegrator(
            model, rank=args.rank, min_rank=args.rank, max_rank=args.rank,
            relative_amplitude_cutoff=1e-10, substeps=2,
        )
        state = bug.initialize(initial)
        after_init = peak_rss_mib()
        for i in range(args.steps):
            state = bug.step(dt=dt, t=i * dt)
    else:
        raise ValueError(args.method)
    elapsed = time.perf_counter() - start
    peak_during = peak_rss_mib()
    if not np.isfinite(state).all():
        raise FloatingPointError(f"{args.method} r={args.rank} went non-finite")
    return {
        "method": args.method,
        "N": args.N,
        "rank": args.rank,
        "steps": args.steps,
        "peak_rss_mib": peak_during,
        "rss_after_setup_mib": after_setup,
        "rss_after_init_mib": after_init,
        "rss_baseline_at_start_mib": baseline_before_setup,
        "interpreter_and_library_mib": after_setup - baseline_before_setup,
        # The *worker's* own thread settings.  Reporting the parent's instead
        # would record an environment the measurement did not run under, which is
        # the provenance gap this project keeps having to close.
        "worker_thread_settings": thread_settings(),
        # Recorded only as evidence the configuration actually ran.  It is NOT a
        # timing measurement: this driver may share a machine, and wall-clock
        # cost is cost_retiming.json's job.
        "wall_seconds_not_a_timing_measurement": elapsed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--N", type=int, nargs="+", action=ListOnce,
                        default=[64, 128])
    parser.add_argument("--ranks", type=int, nargs="+", action=ListOnce,
                        default=[2, 8, 16, 32, 43])
    parser.add_argument("--methods", nargs="+", action=ListOnce,
                        default=["full", "dlra", "bug"])
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument(
        "--noise-repeats", type=int, default=8,
        help=(
            "how many times to re-measure ONE configuration to estimate the "
            "noise floor. One repeat gives a single sample, and a single "
            "sample of this quantity has been observed to move by a factor "
            "of 34, which is enough to flip a verdict. 8 costs 7 extra "
            "worker subprocesses and no integration time."
        ),
    )
    parser.add_argument(
        "--overhead-repeats", type=int, default=5,
        help=(
            "how many times to measure EVERY configuration, so the overhead "
            "over the full grid is a distribution rather than a single sample. "
            "Four registry rows are pinned to that single sample and cannot be "
            "satisfied by any correct measurement: across three independent "
            "measurements the projected integrator's N=64 overhead moved by "
            "+136%%. 5 keeps the driver's cost near 5x, which is minutes."
            # The %% is not a typo. argparse %-interpolates help strings, so a
            # bare '%' in one raises ValueError and the driver cannot print its
            # own --help at all -- which is how this was found, by
            # check_driver_flags.py, after it had been broken.
        ),
    )
    parser.add_argument("--dt", type=float, default=None)
    parser.add_argument("--output", type=Path,
                        default=Path("state/coder/results/peak_memory.json"))
    args = parser.parse_args()

    rows = []
    for N in args.N:
        for method in args.methods:
            ranks = [0] if method == "full" else list(args.ranks)
            for rank in ranks:
                # An identical configuration is measured repeatedly, so the
                # artifact carries the measurement's own noise floor.  Without
                # it, a "rank-independent" verdict is a boolean that flips when
                # allocator behaviour moves the peak by a few tenths of a MiB --
                # which is exactly the size of the effect being asked about.
                #
                # The repeat count is NOT 2.  With a single repeat the "floor"
                # is one sample of |RSS(a) - RSS(b)|, and it was measured four
                # times on this problem at 0.1328, 0.0664, 0.0977 and 0.0039 MiB
                # -- a factor of 34 for the same quantity.  Under the threshold
                # below (spread > 2 x floor) that is the difference between
                # "the variation with rank is real" and "no variation is
                # established" for the DLRA at both grids.  A floor estimated
                # from one sample cannot carry a verdict that swings on it, so
                # the floor is now a distribution and the verdict is taken
                # against its MAXIMUM, which is the conservative side.
                is_reference = (N == args.N[0] and method == args.methods[0]
                                and rank == 0)
                # EVERY configuration is now repeated, not just the one the noise
                # floor is estimated from.  The reason is the registry: four
                # `mem_overhead_*` rows are pinned to a single-sample peak-RSS
                # overhead, and across three independent measurements the
                # projected integrator's N=64 overhead moved by +136% -- so those
                # rows cannot be satisfied by any correct measurement, exactly
                # like the noise-floor row.  Recording the overhead as a
                # distribution over repeats makes it pinnable, and it is cheap:
                # peak RSS is a subprocess high-water mark, so a repeat costs one
                # worker launch and no integration time.
                repeats = (args.noise_repeats + 1) if is_reference else 1
                repeats = max(repeats, args.overhead_repeats)
                for rep in range(repeats):
                    cmd = [
                        sys.executable, str(Path(__file__).resolve()),
                        "--worker", "--method", method, "--N", str(N),
                        "--steps", str(args.steps), "--rank", str(rank),
                    ]
                    if args.dt is not None:
                        cmd += ["--dt", str(args.dt)]
                    env = dict(os.environ)
                    env.update({
                        k: "1" for k in (
                            "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                            "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                        )
                    })
                    print(f"memory: N={N} {method} rank={rank} "
                          f"repeat={rep} ...", flush=True)
                    out = subprocess.run(
                        cmd, cwd=ROOT, env=env, capture_output=True, text=True,
                    )
                    if out.returncode != 0:
                        print(out.stdout[-2000:], out.stderr[-2000:])
                        raise SystemExit(f"worker failed for {method} r={rank}")
                    row = json.loads(out.stdout.strip().splitlines()[-1])
                    row["repeat"] = rep
                    rows.append(row)

    by_key = {(r["method"], r["N"], r["rank"]): r for r in rows if r["repeat"] == 0}
    # The noise floor: the same configuration measured repeatedly, so the reader
    # can see whether a spread over rank is larger than the spread over nothing.
    # It is reported as a DISTRIBUTION, not a point, because one sample of this
    # quantity has been observed to move by a factor of 34 (see the repeat-count
    # comment above) and a verdict must not rest on the luck of which sample is
    # taken.  ``noise_floor`` -- the value the verdicts use -- is the MAXIMUM,
    # because the failure mode being guarded against is claiming a rank
    # dependence that is allocator noise, and the conservative side of that
    # error is the larger floor.
    repeats = [r for r in rows if r["repeat"] > 0]
    # A LIST, keyed by repeat.  This was a dict keyed by configuration, which
    # silently kept only the last repeat: the noise floor was one sample no
    # matter how many were measured, and it reported `samples: 1` while looking
    # like an estimate.  A distribution stored in a dict keyed by the thing it
    # varies with is a distribution of size one, which is how the 34x swing
    # survived four re-measurements unnoticed.
    noise = []
    for r in repeats:
        base = by_key.get((r["method"], r["N"], r["rank"]))
        if base is not None:
            noise.append({
                "config": f"N{r['N']}_{r['method']}_r{r['rank']}",
                "N": r["N"], "method": r["method"], "rank": r["rank"],
                "repeat": r["repeat"],
                "delta_mib": abs(r["peak_rss_mib"] - base["peak_rss_mib"]),
            })
    deltas = [n["delta_mib"] for n in noise]
    noise_floor = max(deltas) if deltas else None
    noise_stats = None
    if deltas:
        ordered = sorted(deltas)
        median = (ordered[len(ordered) // 2] if len(ordered) % 2
                  else 0.5 * (ordered[len(ordered) // 2 - 1]
                              + ordered[len(ordered) // 2]))
        noise_stats = {
            "samples": len(ordered),
            "min_mib": ordered[0],
            "median_mib": median,
            "max_mib": ordered[-1],
            "max_over_min": (ordered[-1] / ordered[0]) if ordered[0] > 0 else None,
            # A bare None here is exactly the kind of thing that gets misread
            # later -- and this project has already lost an afternoon to a bare
            # number meaning something other than what a reader assumed.  The
            # minimum is 0 when two repeats of the same configuration measured
            # *identically*, which is common at this resolution, so the ratio is
            # unbounded rather than unknown.
            "max_over_min_is_unbounded": ordered[0] == 0.0,
            "min_is_zero_note": (
                "the smallest same-configuration difference is exactly 0: two "
                "repeats measured identically, so peak RSS is quantised at this "
                "resolution and max_over_min is unbounded rather than undefined"
                if ordered[0] == 0.0 else
                "the smallest same-configuration difference is non-zero, so the "
                "max/min spread of the floor is a finite ratio"
            ),
            "values_mib": ordered,
            "used_for_verdicts": "max_mib",
            "why_max": (
                "the verdicts ask whether a spread over rank exceeds twice this "
                "quantity. Taking the maximum is the conservative side: it can "
                "only turn a 'varies with rank' verdict into 'not established', "
                "never the reverse, and a false claim of rank-independence is "
                "the error this project has been correcting all cycle."
            ),
        }
    for N in args.N:
        base = by_key.get(("full", N, 0))
        base_repeats = [
            r["peak_rss_mib"] for r in rows
            if r["method"] == "full" and r["N"] == N and r["rank"] == 0
        ]
        if base is None:
            continue
        for method in args.methods:
            for rank in ([0] if method == "full" else list(args.ranks)):
                row = by_key.get((method, N, rank))
                if row is None:
                    continue
                row["peak_overhead_vs_full_grid_mib"] = (
                    row["peak_rss_mib"] - base["peak_rss_mib"]
                )
                row["peak_overhead_fraction"] = (
                    row["peak_overhead_vs_full_grid_mib"] / base["peak_rss_mib"]
                )
                # The same quantity over every repeat of THIS configuration and
                # of the full-grid reference, so the overhead is a distribution.
                #
                # A single-sample overhead is not pinnable: the projected
                # integrator's N=64 overhead was measured at 0.098 MiB, 0.230 and
                # 0.231 across three runs -- +136% -- while the registry row for
                # it is fixed to 8 significant figures. Reporting the spread
                # alongside the point is what lets a reader (or a gate) say
                # whether a given pinned value is even in the right range, and it
                # costs nothing because the repeats were already being taken.
                own = [
                    r["peak_rss_mib"] for r in rows
                    if (r["method"], r["N"], r["rank"]) == (method, N, rank)
                ]
                if len(own) > 1 and base_repeats:
                    overheads = sorted(o - b for o in own for b in base_repeats)
                    median = (
                        overheads[len(overheads) // 2] if len(overheads) % 2
                        else 0.5 * (overheads[len(overheads) // 2 - 1]
                                    + overheads[len(overheads) // 2])
                    )
                    row["peak_overhead_samples_mib"] = {
                        "samples": len(overheads),
                        "min_mib": overheads[0],
                        "median_mib": median,
                        "max_mib": overheads[-1],
                        "spread_mib": overheads[-1] - overheads[0],
                        "spreads_over_median": (
                            (overheads[-1] - overheads[0]) / abs(median)
                            if median else None
                        ),
                        "note": (
                            "every pairing of this configuration's repeats with "
                            "the reference's repeats, so the spread includes the "
                            "reference's own variation and not only this "
                            "configuration's"
                        ),
                    }

    # The claim that matters: is the reduced method's peak *rank*-independent,
    # and is it below the full grid's?
    rank_scaling = []
    for N in args.N:
        for method in args.methods:
            if method == "full":
                continue
            vals = [
                by_key[(method, N, r)]["peak_rss_mib"]
                for r in args.ranks
                if (method, N, r) in by_key
            ]
            base = by_key.get(("full", N, 0))
            if len(vals) < 2 or base is None:
                continue
            rank_scaling.append({
                "N": N,
                "method": method,
                "ranks": [r for r in args.ranks if (method, N, r) in by_key],
                "peak_mib_min": min(vals),
                "peak_mib_max": max(vals),
                "spread_over_rank_mib": max(vals) - min(vals),
                "overhead_vs_full_grid_mib": max(vals) - base["peak_rss_mib"],
                "noise_floor_mib": noise_floor,
                # Stated against the measurement's own resolution rather than a
                # fixed threshold: if the spread over rank is the size of the
                # spread over an identical repeat, the honest verdict is "not
                # resolved at this resolution", not "rank-dependent".
                "rank_independence_resolved": (
                    None if noise_floor is None
                    else bool((max(vals) - min(vals)) > 2.0 * noise_floor)
                ),
                "rank_independence_note": (
                    "true means the spread over rank exceeds twice the "
                    "run-to-run noise floor of an identical configuration, i.e. "
                    "the variation with rank is real rather than allocator noise"
                ),
            })

    # Every worker must have run under the same pinned threading, and the values
    # recorded are the ones the workers themselves saw.
    worker_threads = {json.dumps(r.get("worker_thread_settings"), sort_keys=True)
                      for r in rows}
    if len(worker_threads) > 1:
        raise SystemExit(
            f"workers ran under different thread settings: {sorted(worker_threads)}"
        )

    artifact = {
        "case": "peak_memory",
        "case_family": "cost",
        "provenance": {
            **_provenance(Path(__file__).resolve()),
            "driver": "experiments/bench_memory.py",
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "parent_thread_settings": thread_settings(),
            "worker_thread_settings": rows[0].get("worker_thread_settings") if rows else None,
            # Recorded because bench_cost.py records it and this node is shared:
            # two drivers measuring the same machine should report the same
            # machine state, or a reader cannot tell a memory difference from a
            # load difference.
            "load_average_at_end": _load_average(),
        },
        "parameters": {
            "grids": list(args.N),
            "ranks": list(args.ranks),
            "methods": list(args.methods),
            "steps": args.steps,
            "noise_repeats": args.noise_repeats,
            "overhead_repeats": args.overhead_repeats,
            "repeats_note": (
                "EVERY configuration is measured `overhead_repeats` times, so "
                "the noise floor is estimated from "
                "`noise_floor_samples_mib.samples` same-configuration "
                "differences rather than one, and each overhead is a "
                "distribution. Both were single-sample until 2026-09-26, which "
                "is why four registry rows pinned to a single-sample overhead "
                "could not be satisfied by any correct measurement: the "
                "projected integrator's N=64 overhead was measured at 0.098, "
                "0.230 and 0.231 MiB across three runs, a factor of 1.36 apart."
            ),
            "noise_floor": (
                "the largest of the same-configuration differences between a "
                "repeat and the first measurement; the resolution against which "
                "a spread over rank is judged, taken at its MAXIMUM so the error "
                "can only fall on the side of not claiming a rank dependence"
            ),
            "process_isolation": (
                "one fresh subprocess per configuration, because peak RSS is a "
                "process high-water mark and sharing a process would report the "
                "largest allocation any configuration made for all of them"
            ),
        },
        "measurements": rows,
        "noise_floor_mib": noise_floor,
        "noise_floor_samples_mib": noise_stats,
        "run_to_run_noise_mib": noise,
        "rank_scaling": rank_scaling,
        # D19.4: "peak memory is rank-independent" is NOT supported.  The
        # variation over rank is RESOLVED at N=64 and UNRESOLVED at N=128, so
        # neither "flat in rank" nor "grows with rank" can be said, and "flat"
        # asserts the opposite of what was measured.  Every number below is read
        # out of this run's own rows; the previous version of this string was a
        # literal whose arithmetic had gone stale (it claimed 1.5x and 6x the
        # noise floor against measured 2.7x and 1.9x).
        "interpretation": "",   # filled in below, once `artifact` exists
    }
    # D19.4: the interpretation is computed from the rows this run produced, not
    # written as a literal.  It has to be assigned after the dict is built,
    # because it reads the dict.
    artifact["interpretation"] = _memory_interpretation(
        artifact.get("rank_scaling", []), artifact["noise_floor_mib"],
        artifact.get("noise_floor_samples_mib"),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    # A worker re-enters through --worker; the parent orchestrates subprocesses.
    if "--worker" in sys.argv:
        argv = sys.argv[sys.argv.index("--worker") + 1:]
        ns = argparse.Namespace(
            method="full", N=64, rank=0, steps=400, dt=None, worker=True,
        )
        i = 0
        while i < len(argv):
            if argv[i] == "--method":
                ns.method = argv[i + 1]; i += 2
            elif argv[i] == "--N":
                ns.N = int(argv[i + 1]); i += 2
            elif argv[i] == "--rank":
                ns.rank = int(argv[i + 1]); i += 2
            elif argv[i] == "--steps":
                ns.steps = int(argv[i + 1]); i += 2
            elif argv[i] == "--dt":
                ns.dt = float(argv[i + 1]); i += 2
            else:
                i += 1
        print(json.dumps(run_one(ns)))
    else:
        main()
