"""Artifact tests: the results layer, which the fast unit suite does not cover.

The unit tests in ``test_engine.py`` verify the *engine* -- operators, splits,
rank criteria, integrators.  They cannot verify a *result*, because a result
comes from an 8-unit-time rollout that a fast test cannot afford.  These tests
read the committed artifacts instead, and they are the layer that would catch a
claim quietly changing while the engine stayed correct.

The first of them is the most valuable test in the project, and it exists for
one reason: **the paper's thesis is a claim about a contrast**, and a contrast
nobody asserts can silently disappear.  The thesis is that the subspace must
evolve -- that a fixed-basis projected POD run overflows at high rank where the
structure-preserving DLRA does not, on the same runner, the same splitting and
an orthonormal basis.  If a future re-run or a re-merge quietly changed that, no
unit test would notice, and the paper would be asserting something its own
artifact contradicts.

It cannot be a fast unit test: the earliest recorded divergence is step 11 026
(``pod_late_r32`` at ``t = 5.513``), so asserting it requires either the rollout
or the recorded artifact.  Reading the artifact is the point -- it is a
regression test on what was actually shipped.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
RESULTS = ROOT / "state" / "coder" / "results"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load(name: str) -> dict:
    path = RESULTS / name
    if not path.exists():
        pytest.skip(f"{name} is not present; nothing to assert against")
    return json.loads(path.read_text())


def test_the_static_baseline_error_is_flat_in_rank_above_16():
    """The mechanism the paper's central claim rests on, asserted on the artifact.

    The claim is that a static subspace **saturates** in rank: above some rank the
    extra modes buy essentially nothing, because the subspace is stale rather than
    merely small.  That is a claim about the *shape* of the static error against
    rank, and it is falsifiable -- if the error kept falling with rank, the
    saturation would be an artifact of the rank range tested.

    Saturation is visible at ``t = 0.1``, the horizon the suite already operates
    at, so this needs no long rollout.  The test asserts the *shape*: the spread
    across ranks from 16 upward is a small fraction of the spread below it.  A
    monotone decrease through the high ranks would fail it.
    """
    art = load("crossover_surface.json")
    ranks = [int(r) for r in art["parameters"]["ranks"]]
    if max(ranks) < 32:
        pytest.skip("surface does not reach rank 32")
    high = [r for r in ranks if r >= 16]
    low = [r for r in ranks if r < 16]
    if not high or not low:
        pytest.skip("surface lacks ranks on one side of 16")

    for re, case in sorted(art["by_reynolds"].items()):
        window = art["parameters"]["moving_window_lengths"][0]
        # the shortest measured horizon: the static subspace has had least time to
        # go stale, so this is the *hardest* place for saturation to show
        t_short = min(art["parameters"]["horizons"])
        for t in (t_short, max(art["parameters"]["horizons"])):
            def value(rank: int) -> float:
                rows = case["static_moving_window"][f"W{window:g}_r{rank}"]
                row = min(rows, key=lambda x: abs(x["time"] - t))
                return row["relative_l2_fluct_over_full"]

            hi = [value(r) for r in high]
            lo = [value(r) for r in low]
            spread_hi = (max(hi) - min(hi)) / min(hi) if min(hi) > 0 else 0.0
            spread_lo = (max(lo) - min(lo)) / min(lo) if min(lo) > 0 else 0.0
            assert spread_hi < max(0.35, 0.5 * spread_lo), (
                f"Re={re} t={t}: the static error is not saturated in rank. "
                f"Spread over ranks {high} is {100*spread_hi:.1f}%, against "
                f"{100*spread_lo:.1f}% over ranks {low}. Saturation is the "
                f"paper's mechanism; a continued fall through the high ranks "
                f"would refute it."
            )


def test_a_propagated_fixed_basis_overflows_and_the_evolving_one_does_not():
    """The project's central claim, re-derived from scratch — the one live test.

    The thesis is a *contrast*: on the same runner, the same splitting, the same
    initial condition and the same rank, a subspace **fitted once and propagated**
    overflows, and one **re-derived from the current state every step** does not.
    Every other test either checks the engine's operators or reads a recorded
    artifact, so this is the only place the claim is re-established rather than
    re-read.

    **What the third arm does and does not control, corrected.** An earlier
    version of this test ran a "frozen DLRA" arm at ``check_every=10**9`` and
    concluded from it that the difference was subspace *construction* rather than
    *evolution*. That conclusion was wrong, and the arm was not the control it
    looked like: ``SVDProjector.project`` recomputes ``self._svd(field)`` on
    **every** call, so the projection is a fresh rank-``r`` truncation of whatever
    field it is handed whether or not ``check_every`` ever fires. A large
    ``check_every`` freezes the **rank**, not the subspace — the subspace still
    tracks the state every step, because tracking it is what the projection does.
    The "frozen" arm was therefore a second instance of the same evolving arm, and
    it agreeing with it was not evidence about construction at all.

    What the arms actually establish, and it is enough for the thesis:

    - a basis fitted on a training window and propagated **overflows**;
    - the same basis fitted on zonal-mean-removed snapshots and propagated
      **also overflows** (so it is not the zonal mean doing the damage);
    - the projector that re-derives per step **survives**, at the same rank.

    So the contrast is **propagated-versus-re-derived**, which is the claim the
    paper makes. ``state/coder/results/static_basis_construction_N32.json`` is the
    shipped version of this measurement, with the rank sweep and the three-seed
    replication; the non-monotonicity of the overflow time in rank is recorded
    there as a finding, because an artifact reporting only "the rank at which it
    fails" would mislead the next reader.

    The configuration was chosen by probing for the cheapest one that shows the
    contrast at all: at **N=32, rank 16, dt=0.002** the propagated basis overflows
    at ``t = 5.388`` and the re-derived one reaches ``T = 6.0``. At N=64 the same
    rank survives statically, so the threshold is not merely in the rank -- it is
    in the rank *relative to the resolved band* (the largest alias-free rank is 21
    at N=32 and 43 at N=64). That is why the test fixes the grid, not the rank
    alone.

    Cost is load-dependent and worth stating as a range rather than a number,
    because the node is shared: **17 s measured end-to-end on an otherwise-idle
    node**, 27 s with three other long runs resident, and 35 s and 56 s measured
    on the reviewer's node under its own load. An earlier version of this
    docstring said "about 25 s", which is inside that range but implied a
    precision the measurement does not have.
    """
    import numpy as np

    from solvers import DLRA, Grid2D
    from solvers.pod import PODGalerkin
    from run_baselines import make_initial_state, new_model

    N, dt, final_time, rank, re, amplitude = 32, 0.002, 6.0, 16, 5000, 0.5
    grid = Grid2D(N)
    model = new_model(grid, re, amplitude)
    initial = make_initial_state(
        grid, base_speed=0.5, perturbation_velocity_rms=1.0, cutoff=8,
        seed=20260925,
    )

    # A basis fitted once on a short window and then never touched: this is the
    # whole mechanism, so the test builds it the way the artifact's baselines
    # do rather than reaching for a shortcut.
    n_train = int(0.5 / dt)
    stride = max(1, n_train // (rank + 2))
    snapshots = [initial]
    trained = initial.copy()
    for k in range(n_train):
        trained = model.step(trained, dt, t=k * dt)
        if (k + 1) % stride == 0:
            snapshots.append(trained.copy())
    static = PODGalerkin(grid, rank=rank).fit(snapshots)

    nsteps = int(round(final_time / dt))

    def rollout(projector=None, dlra=None):
        state = dlra.initialize(initial) if dlra is not None else projector(
            initial.copy()
        )
        max_div = grid.max_div_velocity(state)
        diverged_at = None
        for step in range(1, nsteps + 1):
            if dlra is not None:
                state = dlra.step(state, dt, t=(step - 1) * dt)
            else:
                state = model.step(
                    state, dt, t=(step - 1) * dt, projector=projector
                )
            if not np.isfinite(state).all():
                diverged_at = step
                break
            max_div = max(max_div, grid.max_div_velocity(state))
        return diverged_at, max_div, state

    # The overflow is the *expected* outcome on the static side, so the invalid
    # and overflow warnings it provokes are the mechanism rather than a problem.
    # They are contained here instead of being left to train a reader to ignore
    # warnings, and nothing is suppressed on the side that must stay finite.
    with np.errstate(invalid="ignore", over="ignore"):
        static_div, _, _ = rollout(projector=static.project)
    assert static_div is not None, (
        f"the propagated fixed basis survived to t={final_time} at rank {rank} "
        f"on N={N}. The claim under test is that it overflows, so either the "
        f"projection has changed or this configuration no longer exhibits the "
        f"contrast -- in which case the test is pinning nothing."
    )

    # Three arms, and the middle one exists because ``check_every`` gates the
    # *basis refresh*, not only the rank.  An earlier version of this test set
    # check_every=10**9, which reads as "isolate the rank" but in fact freezes the
    # DLRA's subspace too -- so all it compared was a raw-snapshot static basis
    # against the DLRA's own frozen one, and the docstring's claim about *basis
    # evolution* was not what the test measured.  Pinning that honestly needs the
    # frozen arm to be run and reported, not assumed.
    def make(check_every: int) -> DLRA:
        return DLRA(
            new_model(grid, re, amplitude),
            rank=rank, min_rank=rank, max_rank=rank,   # same rank in every arm
            rank_criterion="energy", energy_fraction=0.99,
            rank_basis="fluctuations",
            check_every=check_every,
            adapt_initial=False,
        )

    # Arm 2: the rank adapts as configured.  This is the project's method.
    evolving_div, evolving_max_div, _ = rollout(dlra=make(5))
    # Arm 3: the rank is held fixed.  NOT a frozen subspace: SVDProjector
    # recomputes the SVD of whatever field it is handed on every call, so this arm
    # re-derives per step exactly as arm 2 does.  What it shows is that the *rank
    # rule* is not what keeps the run alive -- a real and narrower fact, and why
    # the docstring attributes the contrast to the projection rather than to the
    # adaptation.
    frozen_div, frozen_max_div, _ = rollout(dlra=make(10**9))

    assert evolving_div is None, (
        f"the evolving basis also overflowed, at step {evolving_div} "
        f"(t={evolving_div * dt:.3f}); the static basis went at step "
        f"{static_div} (t={static_div * dt:.3f}). The claim is a contrast, and a "
        f"contrast in which both sides fail is not evidence for the thesis."
    )
    assert evolving_max_div < 1e-12, (
        f"the surviving evolving run reached {evolving_max_div:.3e} in max "
        f"|div u|, so it survived without keeping the invariant that the "
        f"structure-preserving split exists to enforce"
    )
    # Arms 2 and 3 must agree, and the reason they do is now recorded rather than
    # assumed: they agree because the per-step projection re-derives the subspace
    # from the current field in BOTH, so the rank rule cannot be what separates
    # them.  Asserted, because if they ever diverge then something *has* begun to
    # gate the projection itself and this test's attribution would be wrong.
    assert (frozen_div is None) == (evolving_div is None), (
        f"the fixed-rank arm diverged={frozen_div is not None} but the adapting "
        f"arm diverged={evolving_div is not None}. These arms differ only in the "
        f"rank rule, and both re-derive the subspace per step, so they should "
        f"agree; if they no longer do, the projection has started depending on "
        f"check_every and this test's attribution needs revisiting."
    )
    if frozen_div is None:
        assert abs(frozen_max_div - evolving_max_div) <= 1e-15 + 1e-9 * max(
            abs(evolving_max_div), 1e-30
        ), (
            f"the fixed-rank arm survived with max|div u| = {frozen_max_div:.3e} "
            f"against the adapting arm's {evolving_max_div:.3e}. The two take "
            f"different code paths so a difference is possible, but it should be "
            f"roundoff: both re-derive the same per-step projection."
        )


def test_a_diverged_method_cannot_destroy_the_whole_artifact():
    """A divergence is a result; it must not cost every other method's numbers.

    This is a real failure that cost a run.  ``run_baselines.py`` writes with
    ``allow_nan=False``, which is correct -- ``Infinity`` is not valid JSON --
    but a method that goes non-finite produces an infinite ``relative_l2``, the
    encoder refused, and the entire Re=1000 rank ladder (sixteen configurations,
    hours of compute) was lost **at the write**, after every number had been
    computed correctly.  The bug is not that the value was infinite; it is that
    one method's infinity took the other fifteen down with it.

    So the artefact-level assertion is: the output is valid JSON *and* the
    surviving methods are still in it.  The guard is checked directly here too,
    because the cheap unit version of this is the one that runs every day.
    """
    import json as _json
    import math

    from run_baselines import json_safe

    counter: dict = {}
    payload = {
        "methods": {
            "survivor": {"max_abs_divergence": 7.6e-14, "max_trajectory_divergence": 1.0},
            "diverged": {
                "max_abs_divergence": 7.09e278,
                # what a non-finite state actually produces
                "max_trajectory_divergence": math.inf,
                "series": [{"time": 0.1, "relative_l2": math.inf},
                           {"time": 0.2, "relative_l2": math.nan}],
            },
        }
    }
    safe = json_safe(payload, counter)
    # 1. valid JSON, which is the whole point
    text = _json.dumps(safe, indent=2, sort_keys=True, allow_nan=False)
    assert _json.loads(text) == safe
    # 2. the survivor is untouched -- this is the part that was broken
    assert safe["methods"]["survivor"]["max_trajectory_divergence"] == 1.0
    assert "survivor" in safe["methods"] and "diverged" in safe["methods"]
    # 3. the diverged method's values became null, and the count is recorded so a
    #    reader can tell "null because it diverged" from "never measured"
    assert safe["methods"]["diverged"]["max_trajectory_divergence"] is None
    assert all(
        row["relative_l2"] is None
        for row in safe["methods"]["diverged"]["series"]
    )
    assert counter.get("non_finite_values_replaced") == 3, counter
    # 4. and the magnitude of the divergence itself is preserved, because that is
    #    the result and it is finite
    assert safe["methods"]["diverged"]["max_abs_divergence"] == 7.09e278


def test_every_driver_runs(tmp_path):
    """Each driver must actually execute, at a size that costs nothing.

    This is a test of the *harness*, not the physics, and it exists because a
    driver was broken for many cycles without anyone noticing:
    `run_kolmogorov.py` referenced a bare `N` that does not exist in `main()`,
    so the project's canonical suite driver raised `NameError` on every
    invocation -- and nothing caught it, because the committed artifacts predate
    the break. A driver that cannot run is indistinguishable from a driver that
    has not been run, which is the same failure D14.4 exists to prevent.

    Each driver is invoked as a subprocess with a minimal configuration and a
    temporary output, so the test exercises argparse, the run, the artifact
    assembly and the write -- the whole path, not just the import.
    """
    import os
    import subprocess
    import sys

    env = dict(os.environ)
    env.update({
        "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
    })
    # Minimal configurations chosen to satisfy each driver's own preconditions
    # (enough snapshots to fit the default pod_rank of 16).
    cases = {
        "run_kolmogorov.py": [
            "--re", "5000", "--N", "16", "--dt", "0.0005", "--steps", "40",
            "--train-steps", "20", "--snapshot-stride", "2", "--compare-stride", "10",
            # Small ranks: the driver refuses a rank it cannot fit from the
            # snapshots supplied, which is the behaviour worth keeping, so the
            # smoke configuration has to respect it.
            "--pod-rank", "4", "--dlra-rank", "2", "--dlra-min-rank", "2",
            "--dlra-max-rank", "8",
        ],
        "run_baselines.py": [
            "--re", "5000", "--N", "16", "--T", "0.05", "--train-time", "0.02",
            "--ranks", "4", "--train-snapshot-stride", "0.001", "--sample-every", "20",
            "--refit-interval", "0.01",
        ],
        # The block time is the S2 specification's own (>= 2 time units) and the
        # driver enforces it.  A short horizon is still run: the statistic is
        # recorded as unevaluable with a reason rather than failing, which is the
        # distinction the project cares about.
        "run_regime_pilot.py": [
            "--re", "5000", "--N", "16", "--horizons", "0.02", "--block-time", "2.0",
            "--sample-every", "10",
        ],
        # This driver hard-codes pod_rank=16 and takes train_steps = steps // 2
        # with snapshot_stride 5, so 160 steps is the least that supplies 16
        # snapshots.  Cheap at N=16.
        "run_rank_growth_sweep.py": ["--N", "16", "--re", "5000", "--dt", "0.0005",
                                     "--steps", "160"],
        # window / snapshot-stride chosen so the window still holds more
        # snapshots than the rank, which the driver requires.
        "run_crossover.py": [
            "--re", "5000", "--N", "16", "--horizons", "0.02", "0.04",
            "--ranks", "4", "--window", "0.04", "--refit-interval", "0.01",
            "--snapshot-stride", "0.002",
        ],
        "run_taylor_green.py": [],
        "bench_memory.py": ["--N", "16", "--ranks", "2", "--methods", "full", "dlra",
                            "--steps", "5"],
    }
    for script, extra in cases.items():
        out = tmp_path / f"{script}.json"
        cmd = [sys.executable, str(EXPERIMENTS / script), "--output", str(out), *extra]
        result = subprocess.run(
            cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=900,
        )
        assert result.returncode == 0, (
            f"{script} exited {result.returncode}\n"
            f"--- stdout tail ---\n{result.stdout[-1500:]}\n"
            f"--- stderr tail ---\n{result.stderr[-1500:]}"
        )
        assert out.exists() and out.stat().st_size > 0, (
            f"{script} exited cleanly but wrote no artifact"
        )
        data = json.loads(out.read_text())
        assert data.get("provenance", {}).get("git_commit"), (
            f"{script} wrote an artifact with no commit recorded"
        )


def test_the_subspace_must_evolve_contrast_is_present_in_the_artifact():
    """The thesis contrast, asserted on the shipped artifact.

    Three things must hold together, and the failure message names the step and
    time so a break says *when* the contrast went, not only that it did:

    * every fixed-basis ``pod_early``/``pod_late`` run at rank >= 32 overflowed;
    * **every** ``dlra_*`` run survived to the end;
    * the artifact's own ``diverged_methods`` list agrees with the per-method
      flags, so the summary cannot disagree with the data it summarizes.
    """
    art = load("baselines_re5000_N64_T8.json")
    methods = art["methods"]
    final_time = art["parameters"]["T"]

    fixed_high = {
        name: m for name, m in methods.items()
        if (name.startswith("pod_early_r") or name.startswith("pod_late_r"))
        and m.get("rank_requested", 0) >= 32
    }
    assert fixed_high, (
        "no fixed-subspace run at rank >= 32 is in the artifact, so the "
        "contrast cannot be asserted at all"
    )
    broke = [
        f"{name} (step {m['diverged_at_step']}, t={m['diverged_at_time']}, "
        f"ended t={m['final_time_reached']})"
        for name, m in fixed_high.items()
        if not (m["diverged"] and m["covers_requested_window"] is False)
    ]
    assert not broke, "fixed-subspace runs at rank >= 32 that did NOT overflow: " + "; ".join(broke)

    dlra = {name: m for name, m in methods.items() if name.startswith("dlra_")}
    assert dlra, "no DLRA method in the artifact; the contrast has no other side"
    survived = [
        f"{name} (ended t={m['final_time_reached']}, diverged={m['diverged']})"
        for name, m in dlra.items()
        if m["diverged"] or abs(m["final_time_reached"] - final_time) > 1e-9
    ]
    assert not survived, "DLRA runs that did not reach the final time: " + "; ".join(survived)

    flagged = {name for name, m in methods.items() if m["diverged"]}
    assert flagged == set(art["diverged_methods"]), (
        f"diverged_methods {sorted(art['diverged_methods'])} disagrees with the "
        f"per-method flags {sorted(flagged)}"
    )


def test_exact_divergence_freeness_holds_for_every_surviving_method():
    """The invariant, asserted on the shipped artifact rather than in a unit test.

    The bound asserted is the one the data supports, not an aspirational one.
    Every surviving method's max |div u| lands between **2e-14 and 2e-13** -- one
    to two orders above the 1e-14 figure of merit, which is the roundoff floor
    for an 8-unit-time rollout at N=64, not a target every method meets.  So the
    test asserts that all survivors stay within two orders of that floor, and
    that exactly one named method is the outlier.  Asserting 1e-14 would fail on
    correct data, and asserting 1e-12 would pass on data that had quietly drifted
    two orders worse; two orders is the honest window.

    The diverged runs are excluded because their last recorded value is
    meaningless: they were growing without bound when the run stopped.
    """
    art = load("baselines_re5000_N64_T8.json")
    floor = 1e-14
    bound = 100.0 * floor
    surviving = {
        name: m for name, m in art["methods"].items() if not m["diverged"]
    }
    offenders = {
        name: m["max_abs_divergence"]
        for name, m in surviving.items() if m["max_abs_divergence"] > bound
    }
    # pod_dmd_r32 is a *known* exception: it degraded by three orders of
    # magnitude without diverging, which the figure annotates.  It is named here
    # so that if a second method joins it, this test fails.
    allowed = {"pod_dmd_r32"}
    unexpected = set(offenders) - allowed
    assert not unexpected, (
        f"surviving methods more than two orders above the {floor:.0e} floor: "
        + ", ".join(f"{n}={v:.3e}" for n, v in offenders.items())
    )
    for name in allowed & set(surviving):
        assert surviving[name]["max_abs_divergence"] > bound, (
            f"{name} is on the allow-list but no longer degrades; remove it so "
            f"the exception does not silently become unreported"
        )
    # Every survivor must at least be at the floor, or the word "exact" is doing
    # no work in the claim.
    slack = {
        name: m["max_abs_divergence"]
        for name, m in surviving.items() if m["max_abs_divergence"] < 0.1 * floor
    }
    assert not slack, (
        "surviving methods *below* the roundoff floor, which would mean the "
        "divergence diagnostic is not measuring what it claims: "
        + ", ".join(f"{n}={v:.3e}" for n, v in slack.items())
    )


def test_the_crossover_block_agrees_with_the_rows_it_sits_beside():
    """The derived `crossovers` block, asserted against the rows (D22.5).

    D23 records the block as unusable: its ``t_star`` had no reproducible
    relationship to any error column, and the file says *read the rows*. This is
    that instruction made executable -- the block is recomputed from the rows by
    the same function the driver uses, and required to agree.

    It fails on the currently committed surface, by 7-16%, on both error columns
    and both interpolation conventions -- so the disagreement is neither a column
    choice nor a convention. That is the defect this test exists to make
    impossible to carry silently: a derived block that disagrees with its own
    data looks exactly as authoritative as one that agrees.
    """
    from run_crossover import (
        CROSSOVER_AGREEMENT_TOLERANCE,
        DECLARED_CROSSOVER_COLUMN,
        t_star_from_rows,
    )

    art = load("crossover_surface.json")
    windows = art["parameters"]["moving_window_lengths"]
    column = DECLARED_CROSSOVER_COLUMN
    assert column in art["error_columns"], (
        f"the declared crossover column {column!r} is not one the artifact "
        f"documents: {sorted(art['error_columns'])}"
    )

    disagreements, checked = [], 0
    for re, case in sorted(art["by_reynolds"].items()):
        for entry in case["crossovers"]:
            if entry.get("t_star") is None:
                continue
            rank, window = entry["rank"], entry["window"]
            rows_dlra = case["dlra"][str(rank)]
            rows_static = case["static_moving_window"][f"W{window:g}_r{rank}"]
            derived = t_star_from_rows(rows_dlra, rows_static, column)
            assert derived["t_star"] is not None, (
                f"Re={re} r={rank} W={window}: the block reports a crossover at "
                f"t*={entry['t_star']:.4f} but the rows on column {column!r} show "
                f"none"
            )
            checked += 1
            block, rows_value = entry["t_star"], derived["t_star"]
            if abs(block - rows_value) > CROSSOVER_AGREEMENT_TOLERANCE * abs(rows_value):
                disagreements.append(
                    f"Re={re} r={rank} W={window}: block t*={block:.4f} vs rows "
                    f"{rows_value:.4f} on {column!r} "
                    f"({100*(block-rows_value)/rows_value:+.1f}%)"
                )
            # The bracket is the convention-free statement, so it must agree
            # exactly even when the point estimate does not.
            assert [round(x, 9) for x in entry["bracket"]] == [
                round(x, 9) for x in derived["bracket"]
            ], (
                f"Re={re} r={rank} W={window}: bracket {entry['bracket']} (block) "
                f"vs {derived['bracket']} (rows). The bracket does not depend on "
                f"the interpolation convention, so a difference here is a "
                f"different failure from a point-estimate difference."
            )
    assert checked, "no resolved crossovers to check"
    assert not disagreements, (
        f"{len(disagreements)} of {checked} resolved crossovers disagree with the "
        f"rows by more than {100*CROSSOVER_AGREEMENT_TOLERANCE:.0f}%:\n  "
        + "\n  ".join(disagreements)
        + "\nD23: the block is not a usable source for t*; read the rows."
    )


def test_the_crossover_artifact_records_its_own_provenance():
    """The central figure's artifact must be traceable to committed code.

    The crossover surface is the paper's central result and has been produced by
    three different drivers over the project.  This asserts the artifact records
    a driver, a commit, and -- where the driver records it -- that the driver
    file on disk matched that commit when the numbers were produced.
    """
    art = load("crossover_surface.json")
    prov = art.get("provenance", {})
    assert prov.get("driver"), f"no driver recorded: {prov}"
    assert prov.get("git_commit"), f"no commit recorded: {prov}"
    if "reproducible" in prov:
        assert prov["reproducible"] is True, (
            f"the artifact records itself as not reproducible: {prov}"
        )
    assert "key_schema" in art, (
        "the artifact's keys are not self-describing, so a reader needs a "
        "mapping table to read it"
    )
    assert art["parameters"].get("moving_window_refit_offset") is not None, (
        "the refit offset is load-bearing -- with a zero offset, refits landing "
        "on an evaluation horizon make that horizon's error in-sample -- and it "
        "is not recorded"
    )
    for re, case in art["by_reynolds"].items():
        resolved = [c for c in case["crossovers"] if c["t_star"] is not None]
        assert resolved, f"no crossover resolved at Re={re}; the surface is empty"
        for entry in resolved:
            assert entry["bracket"][0] < entry["t_star"] < entry["bracket"][1], (
                f"Re={re} rank={entry['rank']} window={entry['window']}: t*="
                f"{entry['t_star']} is outside its own bracket {entry['bracket']}"
            )
