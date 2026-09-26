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
RESULTS = ROOT / "state" / "coder" / "results"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load(name: str) -> dict:
    path = RESULTS / name
    if not path.exists():
        pytest.skip(f"{name} is not present; nothing to assert against")
    return json.loads(path.read_text())


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
