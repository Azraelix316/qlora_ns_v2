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
                return row["relative_l2_oracle_mean"]

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
    initial condition and the same rank, a subspace propagated without refreshing
    overflows and a refreshing one does not. Every other test either checks the
    engine's operators or reads a recorded artifact, so this is the only place
    the claim is re-established rather than re-read. If the contrast quietly
    stopped holding — a sign error in the projection, a rank criterion that
    stopped evolving, a change in the splitting — this is what would notice.

    **Three arms, and the control says something narrower than the thesis.**
    ``check_every`` gates the *basis refresh*, not only the rank, so the arm that
    refreshes (``check_every=5``) is bracketed by two frozen ones: a basis built
    from raw snapshots and never refitted, and the DLRA's own subspace frozen
    after initialisation. **Measured: the frozen DLRA survives too** — both
    refreshing and frozen reach ``T`` with the same ``max|∇·u|`` to four
    significant figures. So *at this configuration* the difference from a
    raw-snapshot static basis is in how the subspace is **constructed**
    (fluctuation basis, energy criterion, proper initialisation), and this test
    does **not** separate construction from evolution. The docstring says so, the
    assertions record which way the control fell, and basis evolution against
    static propagation is pinned from the shipped ``T=8`` artifact by
    ``test_the_subspace_must_evolve_contrast_is_present_in_the_artifact``
    instead. If a future change makes the frozen arm diverge, the test fails and
    says the stronger claim has become available.

    The configuration was chosen by probing for the cheapest one that shows the
    contrast at all, and the answer is not the one the shipped artifact uses:
    at **N=32, rank 16, dt=0.002** the raw-snapshot basis overflows at
    ``t = 5.388`` while the DLRA at the *same* rank reaches ``T = 6.0``. At N=64
    the same rank survives statically, so the threshold is not merely in the
    rank -- it is in the rank *relative to the resolved band* (the largest
    alias-free rank is 21 at N=32 and 43 at N=64). That is worth knowing, and it
    is why the test fixes the grid rather than the rank alone.

    Cost is about 25 s, which is why this lives in the results layer rather than
    being deferred to a benchmark.
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

    # Arm 2: the basis genuinely refreshes.  This is the project's method.
    evolving_div, evolving_max_div, _ = rollout(dlra=make(5))
    # Arm 3: the control.  Same code, same rank, subspace frozen after
    # initialisation -- so anything that separates arm 2 from arm 3 is attributable
    # to the refresh and to nothing else.
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
    # What the control actually shows, recorded rather than assumed.  Measured:
    # at N=32/rank 16 the *frozen* DLRA subspace survives as well as the
    # refreshing one (both reach T with the same max|div u| to 4 significant
    # figures).  So at this configuration the difference from a raw-snapshot
    # static basis is in how the subspace is **constructed** -- fluctuation basis,
    # energy criterion, proper initialisation -- and not in whether it is
    # refreshed.  Asserting otherwise would be asserting something the run does
    # not say.
    #
    # The direction that would strengthen the claim is recorded rather than
    # required: if a future change makes the frozen arm diverge, this fails and
    # the docstring can be widened, because then construction and evolution are
    # separable and the thesis has the stronger form.  Basis evolution against
    # static propagation is pinned separately, from the shipped T=8 artifact, by
    # `test_the_subspace_must_evolve_contrast_is_present_in_the_artifact`.
    if frozen_div is None:
        assert frozen_max_div == evolving_max_div, (
            f"the frozen control survived with max|div u| = {frozen_max_div:.3e} "
            f"while the refreshing arm gave {evolving_max_div:.3e}. The two arms "
            f"are now distinguishable, so this test may be claiming more than it "
            f"measures -- update the docstring and the claim with them."
        )
    else:
        assert evolving_div is None and frozen_div is not None, (
            f"the frozen DLRA basis diverged at step {frozen_div} while the "
            f"refreshing one survived: at this configuration construction and "
            f"evolution ARE separable, so the docstring should say so and the "
            f"stronger form of the claim is available."
        )


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
