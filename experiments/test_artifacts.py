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
import re
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


def test_the_scheme_card_cites_code_that_says_what_the_card_claims():
    """Every `file:line` in the scheme card resolves, and the card is regenerated.

    `paper/sections/04_methods.tex` and `05_experimental_setup.tex` carry open
    `PENDING-CODER` markers for the de-aliasing policy, the rank rule and its
    tolerances, the step order and the projection subspace. None of that was
    written down anywhere a writer could read it — it was in the source, and in the
    artifacts as `parameters` *values* without *meanings*. A writer reading the
    source for it is a writer who can get it wrong, which is how `fig:tg`'s caption
    came to promise a rank decay a single Fourier mode cannot produce.

    So the facts are in `scheme_card.md`, and every one carries a citation that is
    **verified by reading the line**. The generator refuses to write the card if
    any citation fails, because a card that silently cites the wrong line is worse
    than no card: a writer cannot tell which parts to trust.

    This test re-runs the generator rather than reading the committed markdown, so
    the committed card cannot be stale relative to the code without this failing.
    """
    import subprocess
    import sys

    from _paths import EXPERIMENTS, REPO_ROOT

    result = subprocess.run(
        [sys.executable, str(EXPERIMENTS / "make_scheme_card.py")],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=600,
    )
    assert result.returncode == 0, (
        "a scheme-card citation no longer resolves, so the card was not "
        f"written:\n{result.stdout[-1500:]}\n{result.stderr[-600:]}\n"
        "Either the code moved (update the line number in "
        "experiments/make_scheme_card.py) or the behaviour changed (rewrite the "
        "claim -- do not just repoint it)."
    )
    assert "all verified" in result.stdout, result.stdout[-600:]

    card = load("scheme_card.json")
    assert card is not None, "scheme_card.json is missing"
    facts = [f for section in card["sections"] for f in section["facts"]]
    assert len(facts) >= 20, (
        f"only {len(facts)} scheme facts; the card is meant to cover the open "
        "method and setup markers, and this is too few to be doing that"
    )
    # Every fact must name a file that exists and carry the text it expects, so a
    # reader (or a gate) can re-verify without running anything.
    for fact in facts:
        rel, _, line = fact["citation"].rpartition(":")
        path = REPO_ROOT / rel
        assert path.exists(), f"{fact['citation']} does not exist"
        lines = path.read_text().splitlines()
        assert 1 <= int(line) <= len(lines), fact["citation"]
        assert fact["expect"] in lines[int(line) - 1], (
            f"{fact['citation']} does not contain {fact['expect']!r}: "
            f"{lines[int(line) - 1].strip()[:80]!r}"
        )
    # And the card must record its own provenance, like every other artifact here.
    assert card.get("provenance", {}).get("captured_at") == "launch", (
        "the scheme card carries no launch-time provenance"
    )


def test_the_rank_at_which_the_dlra_never_yields_is_the_grid_dealiasing_ceiling():
    """The never-yields rank equals the de-aliasing ceiling, at every grid measured.

    This is a mechanism rather than an observation. The ranks that never yield are
    **43 at N=64** and **85 at N=128** — and those are exactly the
    `dealias_rank_ceiling` at those grids, which `cost_retiming.json` records as 43,
    85 and 171 for N = 64, 128 and 256.

    The reason the surface gives is the same at both: *"the DLRA is exact at every
    horizon here (relative error at roundoff), so no static baseline can overtake
    it."* A rank that reproduces the whole resolved band has nothing left to
    adapt, so its subspace is the full band and its error is at roundoff. The
    crossover therefore cannot exist above the ceiling, and the "never yields"
    observation is a statement about the grid, not about the method.

    Two grids is thin, so the test asserts the identity holds where it is
    measured **and** that the reason is the exactness one — if a rank ever
    reported `never` for a different reason, the identity would no longer be a
    mechanism and the claim would need rewording rather than re-measuring.
    """
    cost = load("cost_retiming.json")
    assert cost is not None
    ceiling = {g["N"]: g["dealias_rank_ceiling"] for g in cost["grids"]
               if "dealias_rank_ceiling" in g}
    assert ceiling, "cost_retiming.json records no dealias_rank_ceiling"

    surfaces = {
        64: load("crossover_surface.json"),
        128: load("crossover_N128.json"),
    }
    checked = 0
    for N, data in surfaces.items():
        if data is None or N not in ceiling:
            continue
        block = data["by_reynolds"]["5000"]
        never = {c["rank"] for c in block["crossovers"] if c["status"] == "never"}
        assert never, f"N={N}: no rank is reported as never yielding"
        assert never == {ceiling[N]}, (
            f"N={N}: ranks reported as never yielding are {sorted(never)} but the "
            f"de-aliasing ceiling is {ceiling[N]}. If this no longer holds, the "
            "claim is an observation rather than a mechanism and the wording has "
            "to change."
        )
        for c in block["crossovers"]:
            if c["status"] == "never":
                assert "exact at every horizon" in (c.get("reason") or ""), (
                    f"N={N} r={c['rank']}: status 'never' with reason "
                    f"{c.get('reason')!r} -- the identity above only explains a "
                    "never-yields rank if the DLRA is exact there"
                )
        checked += 1

    assert checked >= 2, (
        f"the identity was checked at {checked} grid(s); it is a two-point claim "
        "and should be checked at both"
    )

    # The ceiling is a wavenumber-derived bound, not a mode count (D30.2), so the
    # identity is a statement about the resolved band and not about a mode count.
    assert ceiling[64] == 43 and ceiling[128] == 85, ceiling


def test_the_memory_overhead_is_a_distribution_and_not_one_sample():
    """The peak-RSS overhead over the full grid must carry its own spread.

    Four `mem_overhead_*` registry rows are pinned to a single-sample overhead at
    eight significant figures, and they cannot be satisfied by any correct
    measurement: the projected integrator's N=64 overhead was measured at 0.098,
    0.230 and 0.231 MiB across three independent runs — **+136%** — while the row
    is fixed. So the artifact now records, per configuration, the overhead over
    every pairing of its own repeats with the reference's repeats.

    A smoke run makes the point concretely: for one configuration the recorded
    point value was the *minimum* of its own distribution. A gate pinning that
    point would be pinning a lower bound it had no way of knowing was one.

    The assertion is deliberately about the distribution's presence and internal
    consistency rather than about any value, because the values are measurements
    of allocator behaviour and asserting them would be asserting noise.
    """
    data = load("peak_memory.json")
    assert data is not None
    measured = [
        m for m in data.get("measurements", [])
        if m.get("peak_overhead_samples_mib")
    ]
    assert measured, (
        "no configuration carries peak_overhead_samples_mib: the overhead is a "
        "single sample again, so the four mem_overhead_* rows cannot be pinned"
    )
    for m in measured:
        s = m["peak_overhead_samples_mib"]
        assert s["samples"] > 1, (m.get("method"), m["N"], s["samples"])
        assert s["min_mib"] <= s["median_mib"] <= s["max_mib"], s
        assert abs(s["spread_mib"] - (s["max_mib"] - s["min_mib"])) < 1e-12, s
        # The point value must be *inside* the distribution it summarises. If it
        # is not, the two are measuring different things.
        point = m["peak_overhead_vs_full_grid_mib"]
        assert s["min_mib"] - 1e-9 <= point <= s["max_mib"] + 1e-9, (
            f"{m.get('method')} N={m.get('N')}: the recorded point {point} is "
            f"outside its own distribution {s['min_mib']}..{s['max_mib']}"
        )

    # And the parameter that makes it so must exist, or the distribution is a
    # lucky accident of one configuration being repeated for the noise floor.
    parameters = data.get("parameters", {})
    assert "overhead_repeats" in parameters or any(
        "repeats" in str(k) for k in parameters
    ), (
        f"the artifact does not record how many repeats produced the "
        f"distribution: {sorted(parameters)}"
    )

    # The full grid's own overhead against itself is the degenerate case and must
    # still be reported -- it is what makes the reference's variation visible.
    full = [
        m for m in measured
        if m.get("method") == "full" and m.get("N") == data.get("grids", [None])[0]
    ] or [m for m in measured if m.get("method") == "full"]
    if full:
        assert any(
            m["peak_overhead_samples_mib"]["min_mib"] < 0 < m["peak_overhead_samples_mib"]["max_mib"]
            for m in full
        ), (
            "the full grid's overhead against itself has no spread, so the "
            "reference's own variation is not being carried into the "
            "distributions above"
        )


def test_provenance_is_captured_at_launch_and_can_actually_fail():
    """`driver_matches_HEAD` must be able to say False, and mean it.

    It could not, until 2026-09-26. `provenance()` read `HEAD` and hashed the
    driver *when the artifact was written*, so for any run that outlasted a commit
    the two were read together and the check compared the driver against itself.
    Demonstrated on a real run: a crossover surface started at 07:40, a commit
    landed at 07:45, the artifact was written at 08:24, and it recorded

        driver_sha256        98b3d61b2496d313   (the file at 08:24)
        the driver that ran  4b2ca8f8bb0bc599   (loaded at 07:40)
        driver_matches_HEAD  true
        reproducible          true

    Both verdicts were wrong, and the module's own note claimed "git_commit is
    HEAD at launch" -- so the intent was right and the code had drifted from it.

    The properties asserted here, in order of how much they would have caught:

    1. `git_commit` comes from a *time* query, not from `rev-parse HEAD` -- the
       old implementation used the latter, which is by definition current;
    2. `driver_sha256` is the driver's hash **at launch**, so if the file changed
       after the process started, the recorded hash is still the one that ran;
    3. `driver_matches_HEAD` goes **False** when the launch driver is not the one
       in the launch commit. That is the check the whole module exists for, and
       it is exercised here by perturbing the launch snapshot directly.
    """
    import importlib
    import sys

    from _paths import EXPERIMENTS
    sys.path.insert(0, str(EXPERIMENTS))
    import provenance as prov

    importlib.reload(prov)
    from pathlib import Path as _Path

    driver = _Path(EXPERIMENTS / "run_kolmogorov.py")
    rel = "experiments/run_kolmogorov.py"

    block = prov.provenance(driver)

    # (1) a time-anchored query, not HEAD.
    assert block.get("git_commit_how", "").startswith("git log -1 --before="), (
        f"git_commit is not time-anchored: {block.get('git_commit_how')!r}. "
        "rev-parse HEAD is by definition current, which is what made the "
        "original check vacuous."
    )
    assert block.get("captured_at") == "launch", block.get("captured_at")

    # (2) the recorded hash is the launch snapshot's, not a fresh read.
    assert block["driver_sha256"] == prov.LAUNCH_SOURCE_SHAS[rel], (
        "driver_sha256 was re-read at write time instead of taken from the "
        "launch snapshot"
    )
    assert block["sources_files_at_launch"] > 20, block["sources_files_at_launch"]
    assert len(block["sources_fingerprint_at_launch"]) == 64

    # (3) THE CONTROL: if the driver that ran is not the one in the launch
    # commit, the verdict must be False. Aiming the old implementation at an
    # older commit's driver is exactly the situation it reported as true.
    original = dict(prov.LAUNCH_SOURCE_SHAS)
    try:
        import hashlib
        import subprocess
        # Only the commits that touched THIS file, not an arbitrary window of
        # recent history.  A `--max-count=40` window was the first version and it
        # stopped finding anything once this branch passed forty commits without a
        # change to the driver -- so the control silently stopped running and the
        # test failed for the wrong reason.  `git log -- <path>` is both faster
        # and correct, and it cannot go stale as the history grows.
        older = subprocess.run(
            ["git", "log", "--format=%H", "--", rel],
            cwd=str(EXPERIMENTS.parent), capture_output=True, text=True,
        ).stdout.split()
        assert len(older) > 1, (
            f"{rel} has no history beyond its current state, so there is no "
            "earlier version to check the provenance verdict against"
        )
        stale = None
        for commit in older:
            blob = subprocess.run(
                ["git", "show", f"{commit}:{rel}"],
                cwd=str(EXPERIMENTS.parent), capture_output=True,
            )
            if blob.returncode == 0:
                digest = hashlib.sha256(blob.stdout).hexdigest()
                if digest != original[rel]:
                    stale = digest
                    break
        assert stale is not None, "no earlier version of the driver to test against"
        prov.LAUNCH_SOURCE_SHAS[rel] = stale
        perturbed = prov.provenance(driver)
        assert perturbed["driver_sha256"] == stale
        assert perturbed["driver_matches_HEAD"] is False, (
            "a driver that ran but is not the one in the recorded commit was "
            "reported as matching -- the exact failure this test exists for"
        )
        assert perturbed["reproducible"] is False
    finally:
        prov.LAUNCH_SOURCE_SHAS.clear()
        prov.LAUNCH_SOURCE_SHAS.update(original)

    # And it is not stuck at False either: restoring the truth restores the
    # verdict, so the check discriminates rather than defaulting.
    assert prov.provenance(driver)["driver_matches_HEAD"] is True


def test_the_driver_drift_classifier_separates_wiring_from_computation():
    """`check_driver_drift.py` must not confuse a parser edit with a maths edit.

    It was wrong once already. The first implementation compared *lines*, and
    adding `action=ListOnce` to an `add_argument` call that already spanned two
    lines pushes its `default=` onto a continuation line — so a pure wiring
    change produced `+ default=[64, 128])` and thirteen of twenty artifacts were
    labelled "substantive". The replacement compares parsed structure, with the
    wiring removed, so a continuation line is not a node and cannot be mistaken
    for a change.

    Both directions are tested on synthetic sources, because a classifier that
    only ever says "fine" is the failure mode this project keeps hitting.
    """
    import sys

    from _paths import EXPERIMENTS
    sys.path.insert(0, str(EXPERIMENTS))
    import check_driver_drift as drift

    base = (
        "import json\n"
        "from _cli import ListOnce\n"
        "def main():\n"
        "    p = argparse.ArgumentParser()\n"
        "    p.add_argument('--ranks', type=int, nargs='+',\n"
        "                  default=[2, 8, 16, 32, 43])\n"
        "    return p.parse_args()\n"
    )
    stripped = base.replace("from _cli import ListOnce\n", "").replace(
        "nargs='+',\n", "nargs='+', "
    ).replace(", action", ", action")

    # The old version, and the current one with the wiring added back. These must
    # be the same computation even though the text differs by several lines.
    old = (
        "import json\n"
        "def main():\n"
        "    p = argparse.ArgumentParser()\n"
        "    p.add_argument('--ranks', type=int, nargs='+',\n"
        "                  default=[2, 8, 16, 32, 43])\n"
        "    return p.parse_args()\n"
    )
    import ast
    assert ast.dump(drift._strip_wiring(ast.parse(base))) == ast.dump(ast.parse(old)), (
        "stripping the wiring did not recover the original program"
    )

    # A change to a default is NOT wiring, even though it sits in the same call.
    changed_default = base.replace("default=[2, 8, 16, 32, 43]", "default=[2, 4, 8]")
    assert ast.dump(drift._strip_wiring(ast.parse(changed_default))) != ast.dump(
        ast.parse(old)
    ), "a changed default was classified as wiring-only"

    # A change to the arithmetic is NOT wiring.
    changed_math = base.replace(
        "return p.parse_args()", "return p.parse_args() * 2"
    )
    assert ast.dump(drift._strip_wiring(ast.parse(changed_math))) != ast.dump(
        ast.parse(old)
    ), "a changed computation was classified as wiring-only"

    # And the report itself must run, and must be honest about which of the two
    # situations it is in rather than defaulting to "fine".
    import subprocess
    import sys as _sys
    from _paths import REPO_ROOT

    result = subprocess.run(
        [_sys.executable, str(EXPERIMENTS / "check_driver_drift.py")],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=600,
    )
    assert result.returncode == 0, result.stderr[-600:]
    # Assert the report's states are drawn from the known set -- NOT that all of
    # them appear. The first version asserted `wiring-only` was mentioned, which
    # made the test depend on the *current state of the tree*: after the
    # relaunch cleared all nine wiring-only artifacts the assertion fired, on a
    # report that was correct. The classifier's behaviour is established by the
    # synthetic sources above; this half only checks the report runs and
    # classifies rather than crashing.
    assert "artifacts with provenance:" in result.stdout, result.stdout[-600:]
    for line in result.stdout.splitlines():
        token = line.strip().split()[0] if line.strip() else ""
        if token in {"current", "wiring-only", "substantive", "unverifiable",
                     "driver-missing"}:
            continue
    known = {"current", "wiring-only", "substantive", "unverifiable",
             "driver-missing"}
    reported = {
        ln.strip().split()[0]
        for ln in result.stdout.splitlines()
        if ln.strip() and ln.strip().split()[0] in known
    }
    assert reported, f"the report classified nothing:\n{result.stdout[-900:]}"
    # Every artifact with provenance must be accounted for by exactly one state.
    total = int(re.search(r"artifacts with provenance:\s*(\d+)",
                          result.stdout).group(1))
    counted = sum(int(m.group(1)) for m in
                  re.finditer(r"^\s+(\d+)\s+(current|wiring-only|substantive|"
                              r"unverifiable|driver-missing)\s*$",
                              result.stdout, re.M))
    assert counted == total, (
        f"the report classifies {counted} of {total} artifact(s); a state is "
        "being dropped rather than counted"
    )


def test_no_list_valued_flag_silently_drops_a_repeated_occurrence():
    """Every ``nargs`` flag refuses a second occurrence instead of keeping the last.

    On 2026-09-26 `--re 5000 --re 1000` was passed to `run_crossover.py`. `--re`
    is declared `nargs="+"`, which takes a *list* after one flag; argparse kept
    the last occurrence, the run covered Re=1000 only, and a partial artifact
    overwrote a complete one — deleting the paper's central result from the
    file with nothing in the output to say so. The same shape had already cost
    an hour in a shell script that passed `--dt` twice.

    Seventeen flags across eight drivers had the property. The check here is on
    the *source*, not on a run, because the failure is a parser behaviour and a
    run cannot detect what it was never asked to do: `test_every_driver_runs`
    passes a well-formed command line, and it passed while the hazard was live.
    """
    import ast
    from pathlib import Path

    from _paths import EXPERIMENTS

    offenders: list[str] = []
    found = 0
    for path in sorted(EXPERIMENTS.glob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "add_argument"):
                continue
            kwargs = {kw.arg: kw.value for kw in node.keywords if kw.arg}
            if "nargs" not in kwargs:
                continue
            found += 1
            flag = None
            if node.args and isinstance(node.args[0], ast.Constant):
                flag = node.args[0].value
            if "action" not in kwargs:
                offenders.append(f"{path.name}: {flag}")
            elif not any(
                isinstance(v, ast.Name) and v.id == "ListOnce"
                for v in [kwargs["action"]]
            ):
                offenders.append(f"{path.name}: {flag} (action is not ListOnce)")

    assert found >= 15, (
        f"only found {found} nargs-valued flag(s); the scan is broken, so the "
        "green below would mean nothing"
    )
    assert not offenders, (
        "list-valued flags that silently drop a repeated occurrence "
        "(use action=ListOnce from experiments/_cli.py):\n  "
        + "\n  ".join(offenders)
    )

    # And the guard must actually fire, on the flag that cost the hour.  A scan
    # of the source proves the attribute is there; only a parse proves it works.
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, str(EXPERIMENTS / "run_crossover.py"),
         "--re", "5000", "--re", "1000", "--N", "64"],
        capture_output=True, text=True, timeout=600,
    )
    assert result.returncode != 0, "the repeated --re was accepted"
    assert "was given more than once" in result.stderr, result.stderr[-600:]
    # The message has to be actionable, not just a refusal: it must show the
    # form that would have worked.
    assert "--re A B" in result.stderr, result.stderr[-600:]


def test_every_included_figure_resolves_against_the_main_document():
    """The figures live where LaTeX will look for them.

    `check_paper_builds.py` resolves `\\includegraphics` against the file that
    contains it, so `{figures/fig_cost}` inside `paper/sections/06_results.tex`
    is looked for at `paper/sections/figures/`. LaTeX does not do that: it
    resolves graphics against the directory of the **main document** plus
    `\\graphicspath`, and `\\input` does not move that directory. The draft has
    no `\\graphicspath` and no standalone section documents, so the correct
    location is `paper/figures/` -- which is where they are generated.

    Rather than assert that, the test *runs* both models over the real draft and
    requires the main-document one to resolve every target. If the writer ever
    adds `\\graphicspath`, or a section becomes a standalone document, this test
    is what notices that the two models have stopped disagreeing -- because
    disagreeing is the only reason the question was ever in dispute.

    Read from `origin/agent/writer` deliberately: the reviewer's copy of the
    draft is the one that gets compiled, and a check that described a draft
    nobody else had would be a result with no provenance in the shared state.
    """
    import subprocess
    import sys

    from _paths import EXPERIMENTS, REPO_ROOT

    result = subprocess.run(
        [sys.executable, str(EXPERIMENTS / "check_includegraph_paths.py")],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=600,
    )
    out = result.stdout
    assert "resolved against the MAIN DOCUMENT" in out, out[-800:]
    line = [
        ln for ln in out.splitlines() if "resolved against the MAIN DOCUMENT" in ln
    ][0]
    # Parse both counts and compare them.  The first version of this assertion
    # was `"/6)" in resolved`, which also matches "5/6" -- so it passed with a
    # figure deliberately deleted.  Third time this session that a check was
    # written too loosely to fail; all three were found by trying to break them
    # rather than by reading them.
    got, total = re.search(r"(\d+)/(\d+)", line).groups()
    got, total = int(got), int(total)
    assert total > 0, out[-800:]
    assert got == total, (
        f"only {got} of {total} \\includegraphics targets resolve against the main "
        "document's directory, so a figure is not where the build will look for "
        f"it:\n{out[-1200:]}"
    )
    # And the premise of the whole question: the two models must still differ.
    # If they ever agree, the checker's model became right by accident and the
    # reason for the disagreement is gone -- which is worth knowing, not ignoring.
    assert "\\graphicspath    : NOT SET" in out, (
        "the draft now sets \\graphicspath, so the resolution question has to be "
        f"re-asked with it in the search list:\n{out[-1200:]}"
    )


def test_the_memory_noise_floor_is_a_distribution_and_not_one_sample():
    """The noise floor must have more than one sample behind it.

    Found on 2026-09-26: the "run-to-run noise floor" was `max()` over a dict
    keyed by *configuration*, so re-measuring one configuration N times kept only
    the last measurement. The artifact reported a floor of 0.0039 MiB and the
    verdicts rested on it -- and that one sample had been observed at 0.1328,
    0.0664, 0.0977 and 0.0039 MiB on four re-measurements, a factor of 34. The
    threshold is `spread > 2 x floor`, so the "the variation with rank is real"
    verdicts in the artifact's own interpretation **flipped** across that range:
    with 8 samples the floor is 0.324 MiB and three of the four verdicts become
    "not established".

    Two things are asserted. The first is the obvious one and would not have
    caught it: more than one sample exists. The second is the one that matters --
    the recorded `noise_floor_mib` is the **maximum** of the samples, so a single
    unlucky low reading cannot make a rank-dependence look resolved.
    """
    data = load("peak_memory.json")
    assert data is not None
    stats = data.get("noise_floor_samples_mib")
    assert stats is not None, (
        "peak_memory.json has no noise_floor_samples_mib: the floor is a single "
        "sample again, so the rank-variation verdicts rest on one reading"
    )
    assert stats["samples"] >= 4, (
        f"the noise floor rests on {stats['samples']} sample(s); a quantity "
        "observed to swing by a factor of 34 needs more than one"
    )
    values = stats["values_mib"]
    assert len(values) == stats["samples"], (len(values), stats["samples"])
    assert data["noise_floor_mib"] == max(values), (
        f"the floor used for verdicts is {data['noise_floor_mib']} but the "
        f"largest sample is {max(values)}; the verdicts must be taken against "
        "the maximum so a low sample cannot manufacture a rank dependence"
    )
    assert stats["used_for_verdicts"] == "max_mib"

    # And the verdicts must be consistent with the floor actually used, rather
    # than with whatever floor was current when they were computed.
    floor = data["noise_floor_mib"]
    for row in data.get("rank_scaling", []):
        spread = row.get("spread_over_rank_mib")
        if spread is None:
            continue
        assert row["rank_independence_resolved"] == (spread > 2.0 * floor), (
            f"N={row.get('N')} {row.get('method')}: spread {spread} vs floor "
            f"{floor} (2x = {2 * floor}) is recorded as "
            f"{row['rank_independence_resolved']}, which does not follow"
        )

    # A negative control on the control: with the floor this run measured, at
    # least one pair must be unresolved, or the floor is too small to be
    # informative and the distribution is not doing any work.
    margins = [
        r["spread_over_rank_mib"] / (2.0 * floor)
        for r in data.get("rank_scaling", [])
        if r.get("spread_over_rank_mib") is not None
    ]
    assert margins and min(margins) < 1.0, (
        f"every margin clears the threshold (min {min(margins):.2f}); with a "
        "floor estimated from several samples that would mean the floor is far "
        "too small, so check that the repeats actually re-measure something"
    )


def test_the_zonal_share_and_the_fluctuation_share_are_exact_complements():
    """The definition is machine-readable, and the two halves are complements.

    On 2026-09-26 the reviewer recomputed the pair of series D106 is derived from,
    formed ``fluctuation / total`` -- the *fluctuation* share, ~82% -- and read
    the recorded ~20% as a different quantity that was "a factor of 4 apart with
    the Re trend inverted". Both halves of that are consequences of the ratio not
    being stated: the recorded number is the *complement*, and because the energy
    is additive under the zonal split the two sum to 1 exactly, so the Re trend
    is the same trend seen from the other side rather than an opposite one.

    Three things are asserted, in increasing order of how much they would have
    caught:

    1. the artifact *states* the formula, the numerator, the denominator and the
       index, so it can be read without inferring a ratio from key names;
    2. the stored share equals the ratio recomputed from the stored component
       energies, so the definition and the number cannot disagree;
    3. the two shares sum to 1, which is what makes (2) non-coincidental.
    """
    import sys

    from _paths import EXPERIMENTS
    sys.path.insert(0, str(EXPERIMENTS))
    from run_kolmogorov import zonal_fraction_semantics

    semantics = zonal_fraction_semantics()
    # (1) the definition, not a description of it.
    assert "(energy_history - fluctuation_energy_history) / energy_history" in (
        semantics["formula_zonal"]
    ), semantics["formula_zonal"]
    assert "fluctuation_energy_history / energy_history" in (
        semantics["formula_fluctuation"]
    ), semantics["formula_fluctuation"]
    for key in ("energy_history", "fluctuation_energy_history", "index",
                "the_two_are_exact_complements", "how_to_miscompute_it"):
        assert key in semantics, f"the definition omits {key!r}"

    for name in ("kolmogorov_re100_N64.json", "kolmogorov_re1000_N64.json",
                 "kolmogorov_re5000_N64.json", "kolmogorov_re5000_N128.json"):
        data = load(name)
        assert data is not None, name
        for method in ("full", "dlra"):
            block = data[method]
            assert "zonal_fraction_semantics" in block, (
                f"{name}:{method} has no zonal_fraction_semantics, so the share's "
                "definition lives only in a decision record"
            )
            stored = block["zonal_fraction_semantics"]["formula_zonal"]
            assert stored == semantics["formula_zonal"], (name, method, stored)
            for index in ("at_t0", "at_final_step"):
                zonal = block["zonal_energy_fraction"][index]
                fluct = block["zonal_energy_fraction_fluctuation"][index]
                comp = block["zonal_energy_fraction_components"][index]
                # (2) the number equals the ratio of the recorded components.
                assert abs((comp["total_energy"] - comp["fluctuation_energy"])
                           / comp["total_energy"] - zonal) < 1e-15, (name, method, index)
                assert abs(comp["fluctuation_energy"] / comp["total_energy"]
                           - fluct) < 1e-15, (name, method, index)
                # (3) and the two are exact complements, which is the identity
                # that makes the reviewer's ~82% the same measurement.
                assert abs(zonal + fluct - 1.0) < 1e-15, (
                    f"{name}:{method}:{index}: zonal {zonal} + fluctuation {fluct} "
                    f"= {zonal + fluct}, not 1"
                )


def test_the_energy_is_additive_under_the_zonal_split():
    """The complement identity is structural, not a coincidence of one run.

    E(psi) = E(zonal) + E(psi') holds because the Parseval inner product of
    grad(psi_zonal) with grad(psi') vanishes -- the zonal mode occupies only kx=0
    and psi' occupies only kx!=0.  If this ever stopped holding, the complement
    claim in ``zonal_fraction_semantics`` would become false and the
    documentation would be lying, so it is measured rather than asserted in
    prose.  A random field is used because a single-Fourier-mode field would
    satisfy it trivially.
    """
    import sys

    import numpy as np

    from _paths import EXPERIMENTS, REPO_ROOT
    sys.path.insert(0, str(EXPERIMENTS))
    sys.path.insert(0, str(REPO_ROOT))
    from solvers.spectral import Grid2D, fluctuations, zonal_mean

    rng = np.random.default_rng(20260926)
    for N in (16, 32, 64):
        grid = Grid2D(N)
        k = np.fft.fftfreq(N)
        psi = np.fft.ifft2(
            rng.normal(size=(N, N))
            * np.exp(-(k[:, None] ** 2 + k[None, :] ** 2) / 4.0)
        ).real
        total = grid.ke(psi)
        zonal = grid.ke(zonal_mean(psi))
        fluct = grid.ke(fluctuations(psi))
        assert abs(zonal + fluct - total) <= 4e-16 * total, (N, zonal + fluct, total)


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


def test_a_committed_artifact_reproduces_bit_for_bit(tmp_path):
    """The reproducibility claim, enforced rather than asserted (C8-3).

    The project's strongest selling point is that a re-run reproduces every
    recorded series *byte-identically* -- not to a tolerance, not on the scalars
    that matter, on everything except the timings. That is the kind of statement
    reviewers ask for and rarely get, and it is currently only a sentence.

    So it is a test. One suite configuration is re-run into a temporary file and
    compared field by field against the committed artifact, with **bit-identity**
    required (``==`` on the floats, not ``isclose``): a tolerance would let a
    drift of any size pass as long as it stayed small, which is exactly the
    failure the claim is meant to exclude. Only timing fields and the provenance
    block are excluded, and the exclusion list is written out rather than
    pattern-matched, so a new timing field has to be added deliberately.

    Cost is about 30 s at T=0.1, which is the shortest horizon the project runs
    and the one every artifact in the suite shares.
    """
    import subprocess
    import sys

    from _paths import CANONICAL_ARGS, REPO_ROOT, EXPERIMENTS  # noqa: F401

    committed = load("kolmogorov_re5000_N64.json")
    assert committed is not None, "the canonical Re=5000 N=64 run is absent"

    out = tmp_path / "repro.json"
    result = subprocess.run(
        [sys.executable, str(EXPERIMENTS / "run_kolmogorov.py"),
         *CANONICAL_ARGS, "--output", str(out)],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=1800,
    )
    assert result.returncode == 0, (
        f"the re-run failed:\n{result.stdout[-800:]}\n{result.stderr[-800:]}"
    )
    fresh = json.loads(out.read_text())

    # Excluded deliberately, not by pattern: a new timing field must be added
    # here on purpose rather than swept up by a substring match.
    timing = {
        "wall_seconds", "wall_seconds_per_step", "seconds_per_step",
        "initialization_seconds", "fit_seconds", "offline_plus_online_seconds",
        "linear_algebra_seconds", "linear_algebra_seconds_per_step",
        "peak_rss_mib", "provenance", "generated",
    }

    differences, compared = [], 0

    def walk(a, b, path):
        nonlocal compared
        if path.split(".")[-1] in timing:
            return
        if isinstance(a, dict):
            for key in a:
                if key not in b:
                    differences.append(f"{path}.{key}: absent from the re-run")
                    continue
                walk(a[key], b[key], f"{path}.{key}")
        elif isinstance(a, list):
            if len(a) != len(b):
                differences.append(
                    f"{path}: length {len(a)} vs {len(b)}"
                )
                return
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, f"{path}[{i}]")
        else:
            compared += 1
            # Bit-identity, deliberately: `==` and not `isclose`.
            if a != b:
                differences.append(
                    f"{path}: committed {a!r} vs re-run {b!r}"
                )

    walk(committed, fresh, "")
    assert compared > 500, (
        f"only {compared} fields were compared, which is too few for the "
        f"comparison to mean anything"
    )
    assert not differences, (
        f"{len(differences)} of {compared} fields differ between the committed "
        f"artifact and a re-run of the same configuration on committed code. "
        f"Bit-identity is the claim; a difference breaks it:\n  "
        + "\n  ".join(differences[:12])
        + (f"\n  ... and {len(differences) - 12} more" if len(differences) > 12
           else "")
    )


def test_the_papers_figure_captions_have_not_drifted_from_the_artifacts():
    """The caption check reports drift, and there is none.

    Six of the paper's six figure captions were written before the figures
    existed, and four of them claim things the artifacts do not support. Those
    are recorded in ``state/coder/results/caption_verdicts.json`` and the
    measured values are in ``experiments/figures/CAPTIONS.md``.

    This asserts the *absence of drift*, not the absence of disagreement: a
    re-run that turns a supported claim into an unsupported one, or moves a
    measured value, is what would otherwise reach the paper unnoticed. The check
    is not a gate on the draft -- the captions are the writer's to correct, and a
    permanently-red gate is a gate that gets bypassed.
    """
    import subprocess
    import sys

    from _paths import EXPERIMENTS, REPO_ROOT

    result = subprocess.run(
        [sys.executable, str(EXPERIMENTS / "check_figure_captions.py")],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=600,
    )
    assert result.returncode == 0, (
        "a figure caption's support changed since the recorded baseline:\n"
        f"{result.stdout[-1200:]}\n{result.stderr[-600:]}\n"
        "Either a re-run moved a measured value, or a claim was resolved. If it "
        "was resolved, re-record the baseline deliberately; if a re-run moved a "
        "value, the draft's caption needs the new number."
    )
    # And the check must actually be looking at something.
    assert "unsupported claims:" in result.stdout, result.stdout[-400:]


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
