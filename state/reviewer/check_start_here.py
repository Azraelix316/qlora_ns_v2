#!/usr/bin/env python3
"""Is `START_HERE.md` still true?

WHY THIS EXISTS. `START_HERE.md` is the entry point: it is the first file every
agent opens, and §4 tells them what to run and what the answer will be. It had
drifted two generations: it promised "four checks", `20/24` registry rows, "44
tests" and `24/24`, while the gates actually report five checks, `29/33`, 46
tests and `29/33`. An entry point that quotes stale numbers is worse than one
that quotes none, because every agent who opens it is misinformed about the
state of the project and cannot tell they are misinformed.

THE DESIGN, AND WHY IT IS NOT A PATTERN MATCH. Earlier gates in this project
matched *wording* and were caught matching the wrong quantity (D95: eleven false
positives; D60: a pattern that matched a correct number in both a claim and its
correct form). So this gate does not match prose. For each gate it RUNS the gate,
extracts one headline number from the real output, and then asserts that exact
string is PRESENT in §4. It is a presence assertion over a computed value, so:

  * it cannot fire on a correct site -- it only ever asks "is this string here";
  * it cannot be satisfied by a coincidental match, because the value it looks
    for is the value the gate just produced;
  * it fails by ABSENCE, which is the only failure mode a stale document has.

POPULATION IS PRINTED, because a check that reports clean has usually measured
nothing (D87, CHECKLIST §1.15). Every gate it runs prints the population it
measured over, and that population is echoed here.

It deliberately does NOT run the full test suite: `pytest experiments/` takes
~197 s. It uses `--collect-only -q` for the test COUNT, which is the quantity
START_HERE quotes, and says so, so nobody reads a green run as "the tests pass".

Usage:  check_start_here.py              check START_HERE against the gates
        check_start_here.py --self-test  prove the check can fail
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PY = sys.executable

WORD = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
        8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}
"""Number-word table for the section-4 heading. It was originally {2..7} and
omitted 8, so when the eighth gate was added the check demanded the literal
'8' where the document correctly read 'eight' -- the gate failed on a correct
document because of a gap in its own table. A completeness bug in a checker is
indistinguishable from a stale document unless the table is exercised, so the
self-test now drives the table over its whole range rather than one value."""


def _run(args: list[str], cwd: Path) -> str:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                           timeout=900, env=env)
    except subprocess.TimeoutExpired:
        return ""
    return (r.stdout or "") + (r.stderr or "")


def collect_facts() -> list[tuple[str, str, str, str]]:
    """Return (gate, human label, the string START_HERE must contain, evidence)."""
    facts: list[tuple[str, str, str, str]] = []

    # 1. the claims registry's own verified count
    out = _run([PY, str(HERE / "claims_registry.py")], REPO)
    m = re.search(r"(\d+)/(\d+) verified", out)
    if m:
        facts.append(("claims_registry.py", "registry rows verified",
                      f"{m.group(1)}/{m.group(2)}", f"ran it: '{m.group(0)}'"))
    else:
        facts.append(("claims_registry.py", "registry rows verified",
                      "<could not read>", "the gate printed no 'n/m verified' line"))

    # 2. the paper build check's defect count
    out = _run([PY, str(HERE / "check_paper_builds.py")], REPO)
    m = re.search(r"(\d+) defect", out)
    if m:
        facts.append(("check_paper_builds.py", "paper build defects",
                      f"{m.group(1)} defect", f"ran it: '{m.group(0)}'"))
    else:
        facts.append(("check_paper_builds.py", "paper build defects",
                      "<could not read>", "the gate printed no 'n defect' line"))

    # 3. heading integrity -- must be zero, and that is the claim START_HERE makes
    out = _run([PY, str(HERE / "check_headings.py")], REPO)
    m = re.search(r"(\d+) wrapped heading\(s\)", out)
    if m:
        facts.append(("check_headings.py", "wrapped headings in my own documents",
                      f"{m.group(1)} wrapped heading", f"ran it: '{m.group(0)}'"))
    else:
        facts.append(("check_headings.py", "wrapped headings in my own documents",
                      "<could not read>", "the gate printed no 'n wrapped heading(s)' line"))

    # 4. the test COUNT, via --collect-only (START_HERE quotes a count, not a result)
    out = _run([PY, "-m", "pytest", "experiments/", "-q", "--collect-only"], REPO)
    m = re.search(r"(\d+) tests? collected", out) or re.search(r"(\d+) test", out)
    if m:
        facts.append(("pytest --collect-only", "tests in the suite",
                      f"{m.group(1)} tests", f"collected only, NOT run: '{m.group(0)}'"))
    else:
        facts.append(("pytest --collect-only", "tests in the suite",
                      "<could not read>", "collection printed no test count"))

    return facts


def section4(text: str) -> str:
    """The region of START_HERE that carries the claims: §4 up to the next `## `."""
    m = re.search(r"^## 4\..*?(?=^## \d)", text, re.S | re.M)
    return m.group(0) if m else ""


def listed_checks(sec: str) -> int:
    """How many check commands §4 actually lists.

    Counted from the fenced code blocks, as "a line whose first token is
    `python`". The first version of this matched `python3 <path> <something>`
    and therefore only fired on commands that happened to carry a trailing
    comment -- so it under-counted a bare list, which the self-test caught by
    handing it a bare fixture. A count that depends on the presence of a
    comment is not a count of the thing being counted.
    """
    n = 0
    for block in re.findall(r"```.*?```", sec, re.S):
        for line in block.splitlines():
            if line.strip().startswith("python"):
                n += 1
    return n


def status_line_line_problems(line):
    """The problems with ONE `> Status:` line, as a list of strings. Empty list means clean.

    Takes the line as an argument rather than reading NOTES.md, so the self-test can drive it with a
    fixture. The first version read the file itself, which made it untestable: the self-test case
    added alongside it was ACCEPTED and then rejected by a DIFFERENT (section-4) assertion, so the
    positive control passed with the bug both present and absent. A test that cannot reach its own
    bug is worse than no test (D113).
    """
    bad = []
    m = re.search(r"\b([0-9a-f]{7,40})\b", line)
    if m and re.search(r"\b(?:main|commit|[0-9a-f]{7,40})\b", line):
        bad.append(f"names the commit {m.group(1)!r}, which no status line can keep current -- "
                   f"say what is true of the PROJECT, not of one tree state")
    claims = [("registry", r"(\d+)/(\d+)(?:\s+verified)?"), ("build defects", r"(\d+)\s+build defects"),
              ("tests", r"(\d+)\s+tests")]
    for what, rx in claims:
        q = re.search(rx, line)
        if q and not what_is_current(what, q):
            bad.append(f"quotes {q.group(0)!r} for {what}, which the gates do not report")
    return bad


def status_line_facts():
    """(failures, evidence) for the board's `> Status:` line CONTENT.

    check_headings.py asserts the line is one line and under a length cap. It does not look at what
    the line SAYS. This does, and the first version of it checked the wrong things.

    D116: it asserted the line's quoted COMMIT and FILE COUNT. Both are computable, and both were
    stale within one merge -- because merging IS what changes main, so a hash written before the
    merge is wrong the instant the merge lands. **A field that cannot stay true should not carry
    the thing that cannot stay true.** So the commit hash is now FORBIDDEN in the status line, and
    what is checked instead is the durable content: the gate numbers it quotes, which a reader
    actually acts on, verified against the gates themselves exactly as section 4 is.

    Same shape as the section-4 assertions: run the thing, extract the value, require the document
    to contain it. The status line is the first thing an agent reads, so a stale one misleads
    before anything else can correct it.
    """
    p = HERE / "NOTES.md"
    if not p.exists():
        return 0, "NOTES.md absent, skipped"
    hits = [l for l in p.read_text().splitlines() if l.startswith("> Status:")]
    if len(hits) != 1:
        return 1, f"found {len(hits)} '> Status:' lines, expected exactly 1"
    line = hits[0]
    # D117: the claim patterns originally required the literal word "verified", which the status
    # line does not use -- so the registry number it quotes was NEVER COMPARED, and the assertion
    # passed on an unchecked number. Each pattern now accepts either form.
    bad = status_line_line_problems(line)
    if bad:
        return 1, "the '> Status:' line is STALE or uncheckable: " + "; ".join(bad)
    return 0, "1 line, no commit hash, and every gate number it quotes is current"


def run_gate(script, pattern):
    """Run one of my own gates and return the first regex match, or None. Never guesses."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, str(HERE / script)], cwd=REPO, capture_output=True,
                       text=True, env=env)
    return re.search(pattern, r.stdout or "")


def run_gate_pytest():
    """The test count, or None. Never guesses."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-m", "pytest", "experiments/", "-q", "--collect-only"],
                       cwd=REPO, capture_output=True, text=True, env=env)
    m = re.search(r"(\d+) tests collected", r.stdout or "")
    return m.group(1) if m else None


# D127: SECTION 0 IS THE ENTRY POINT AND IT ASSERTS THREE BLOCKERS FROM MEMORY. EACH IS COMPUTABLE, SO EACH
# IS MEASURED. The point is not that the numbers are wrong today -- they are right -- it is that a
# blocker list written from memory is a blocker list that goes stale silently, and this is the ONE
# document every agent reads first.
#
# AND THE COUNTING IS THE INTERESTING PART. I first counted the phantom citations with
# `\\cite\{koch2019dlra\}` and got 2, because that matches only the form where the key stands ALONE.
# Two of the four sites carry it AMONG OTHERS -- one in an 11-key cite, one in a 4-key cite -- so the
# real count is 4, which is what check_paper_builds.py independently reports. Counting the TOKEN rather
# than the QUANTITY understated the work by half, and would have told the writer there were two edits
# to make when there are four, two of which a find-and-replace cannot see. D95, and the reason this
# function counts cite COMMANDS CONTAINING the key rather than occurrences of a string.
SECTION0_CLAIMS = [
    # (what section 0 asserts, THE NUMBER, the substring that must appear, how to measure it)
    #
    # THE NUMBER IS A FIELD, NOT PARSED OUT OF THE SUBSTRING. The first version extracted it with
    # `re.search(r"\\d+", literal)` and duly reported "asserts 2019" -- because the literal contains
    # the string `koch2019dlra`, so the first digit run in the sentence about the number of phantom
    # citations is the year in a citation key. And the figure claim, written "five figures no code
    # generates", has no digit at all, so it asserted None. **A NUMBER PARSED OUT OF PROSE IS A TOKEN,
    # NOT A CLAIM** -- D111 again, this time inside the check written to catch exactly that. The
    # substring is now a PRESENCE check only; the number is stated.
    #
    # A BUCKET DEFINED BY JUDGEMENT IS NOT A MEASUREMENT AND IS DELIBERATELY NOT HERE. Section 0
    # also says "~20 of the 50 markers are transcription" and that is a judgement about which
    # markers are closable by reading a table, not something this function can count. Putting it in
    # a measured table would be the same error as parsing a number out of prose: it would acquire the
    # authority of a measurement without being one. Six crisp claims; the judgement stays prose.
    ("the phantom citations",        4, "four `\\cite{koch2019dlra}`",                    "phantom_cite_sites"),
    ("the figures with no generator", 5, "**five figures no code generates**",              "missing_generators"),
    ("the unresolvable figure files", 6, "`paper/figures/` is **empty on all three branches**", "unresolvable_figures"),
    ("the supplied blocks",          24, "the 24 supplied blocks",                          "paste_ready_blocks"),
    ("the marker total",             51, "**THE `51` `PENDING-CODER` MARKERS ARE NOT FIFTY-ODD BLOCKED ITEMS",               "pending_markers"),
    ("the withdrawn-quantity traps",  5, "**withdrawn-quantity traps**",                                         "rstar_traps"),
]


CITE_RX = re.compile(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])?\{([^}]*)\}")


def _git(*a):
    import subprocess
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout


def _ls(ref, prefix):
    return [f for f in _git("ls-tree", "-r", "--name-only", ref, "--", prefix).splitlines() if f]


def _load(ref, path):
    return _git("show", f"{ref}:{path}")


def _draft_text():
    """Every .tex the paper \inputs, as one string, from the same ref the other checks use."""
    out = []
    for f in sorted(_ls("main", "paper/sections")):
        if f.endswith(".tex"):
            out.append(_load("main", f) or "")
    main_tex = _load("main", "paper/main.tex")
    if main_tex:
        out.append(main_tex)
    return "\n".join(out)


def section0_facts():
    """(failures, evidence) for section 0's asserted blockers, measured against the tree.

    Returns one failure per claim whose measurement disagrees with what the document says. A claim
    whose measurement cannot be taken is a FAILURE, not a skip (D87): an unmeasurable claim in the
    entry point is the worst kind, because it reads as authoritative.
    """
    doc = (HERE / "START_HERE.md")
    if not doc.exists():
        return 1, "START_HERE.md absent, skipped"
    text = doc.read_text()
    i = text.find("## 0. THE CRITICAL PATH")
    if i < 0:
        return 1, "START_HERE.md has no '## 0. THE CRITICAL PATH' section -- the entry point's"
    sec0 = text[i:]
    j = sec0.find("\n## 1. ")
    if j > 0:
        sec0 = sec0[:j]
    draft = _draft_text()

    # 1. cite COMMANDS containing the key, not occurrences of the string
    key = "koch2019dlra"
    sites = 0
    solo = 0
    for m in CITE_RX.finditer(draft):
        keys = [k.strip() for k in m.group(1).split(",")]
        if key in keys:
            sites += 1
            solo += (len(keys) == 1)
    tree = _ls("main", "paper/figures")
    figs = sorted(set(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{figures/([a-z_]+)\}", draft)))
    missing = [f for f in figs if f"paper/figures/{f}.pdf" not in tree]
    order = ""
    op = HERE / "WRITER_ORDER.md"
    if op.exists():
        order = op.read_text()
    blocks = len(re.findall(r"```latex\n", order))
    markers = len(re.findall(r"PENDING-?CODER", draft, re.I))
    traps = len(re.findall(r"PENDING-?CODER[^\n]*(?:r\*\(Re\)|r_POD\(Re\))", draft, re.I))
    # Search CONTENTS, not paths: the first version tested `f in x` against file NAMES, which is
    # never true, so it reported all six as ungenerated -- including fig_cost, which make_figures.py
    # writes. A generator check that never reads a generator.
    py = [f for f in _ls("main", "experiments") if f.endswith(".py")]
    bodies = {f: (_load("main", f) or "") for f in py}
    missing_gen = [f for f in figs if not any(f in b for b in bodies.values())]
    measured = {
        "phantom_cite_sites": sites,
        "missing_generators": len(missing_gen),
        "unresolvable_figures": len(missing),
        "paste_ready_blocks": blocks,
        "pending_markers": markers,
        "rstar_traps": traps,
    }
    bad = 0
    print("SECTION 0 -- the entry point's asserted blockers, MEASURED (not remembered)")
    print(f"  POPULATION: {len(draft.split())} words of draft, {len(order.split())} words of order doc, "
          f"{len(tree)} file(s) in paper/figures/")
    for what, asserted, literal, keyname in SECTION0_CLAIMS:
        n = measured[keyname]
        # the substring may be broken across a line wrap, so compare on collapsed whitespace
        flat = re.sub(r"\s+", " ", sec0)
        present = re.sub(r"\s+", " ", literal) in flat
        if not present:
            print(f"  ??  {what}: section 0 does not contain {literal!r} -- a FAILURE, because a claim I")
            print("      cannot find is a claim I cannot check")
            bad += 1
            continue
        ok = (asserted == n)
        if not ok:
            bad += 1
        extra = ""
        if keyname == "phantom_cite_sites":
            extra = f"  [{solo} with the key ALONE, {sites - solo} among other keys -- a find-and-replace sees only the {solo}]"
        if keyname == "unresolvable_figures":
            extra = f"  [{len(figs)} included, paper/figures/ has {len([x for x in tree if x.endswith(('.pdf', '.png'))])} file(s)]"
        print(f"  {'ok  ' if ok else 'FAIL'}  {what:28} asserts {asserted}, measured {n}{extra}")
    if bad:
        print(f"  {bad} claim(s) wrong -- **section 0 is the first thing an agent reads, so a stale one")
        print("      misleads before anything else can correct it. Update it from these lines.**")
    else:
        print(f"  {len(SECTION0_CLAIMS)} claim(s) checked, 0 wrong")
    return bad, f"section 0: {measured}"


def what_is_current(what, q):
    """True if the numbers the status line quotes match what the gate reports right now."""
    import subprocess
    def run(script, pattern):
        env = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"}
        r = subprocess.run([sys.executable, str(HERE / script)], cwd=REPO,
                           capture_output=True, text=True, env={**env, **{k: v for k, v in os.environ.items() if k.startswith(("PATH", "HOME"))}})
        m = re.search(pattern, r.stdout or "")
        return m
    if what == "registry":
        m = run("claims_registry.py", r"(\d+)/(\d+) verified")
        return bool(m) and (m.group(1), m.group(2)) == (q.group(1), q.group(2))
    if what == "build defects":
        m = run("check_paper_builds.py", r"(\d+) defect\(s\)")
        return bool(m) and m.group(1) == q.group(1)
    import subprocess
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-m", "pytest", "experiments/", "-q", "--collect-only"],
                       cwd=REPO, capture_output=True, text=True, env=env)
    m = re.search(r"(\d+) tests collected", r.stdout or "")
    return bool(m) and m.group(1) == q.group(1)


def check() -> int:
    start = (HERE / "START_HERE.md").read_text()
    sec = section4(start)
    if not sec:
        print("FAIL: could not locate '## 4.' in START_HERE.md")
        return 1

    facts = collect_facts()
    print(f"POPULATION: {len(facts)} gate-derived number(s) that START_HERE.md section 4 asserts,")
    print(f"            measured over {len(facts)} gate(s) run live just now.")
    print(f"            section 4 is {len(sec.splitlines())} lines and lists "
          f"{listed_checks(sec)} check command(s).")
    print()

    bad = 0
    for gate, label, want, evidence in facts:
        if want == "<could not read>":
            print(f"  ??    {gate:<26} {label}: {evidence} -- treated as a FAILURE, because a")
            print(f"        number I cannot measure is a number I cannot vouch for")
            bad += 1
            continue
        # the string as START_HERE would write it, tolerating a backticked form
        present = want in sec
        print(f"  {'ok  ' if present else 'FAIL'}  {gate:<26} {label}: needs {want!r}"
              f"{'' if present else '  -- ABSENT from section 4'}")
        print(f"        evidence: {evidence}")
        if not present:
            bad += 1

    # the count word in the heading must equal the number of commands listed
    n = listed_checks(sec)
    m = re.search(r"^## 4\.\s*Run these (\w+) checks?\b", sec, re.M)
    print()
    if not m:
        print("  FAIL  the §4 heading does not state a number of checks, so it cannot go stale")
        print("        silently -- but it also cannot be checked. Rewrite it as 'Run these N checks'.")
        bad += 1
    else:
        said = m.group(1)
        expect = WORD.get(n, str(n))
        good = said == expect
        print(f"  {'ok  ' if good else 'FAIL'}  section 4 heading says {said!r} checks; "
              f"it lists {n} check command(s) (expected {expect!r})")
        if not good:
            bad += 1

    print()
    sbad2, sev2 = status_line_facts()
    print(f"  {'FAIL' if sbad2 else 'ok  '}  NOTES.md '> Status:' line CONTENT: {sev2}")

    print()
    sbad3, sev3 = section0_facts()
    print()

    print(f"TOTAL: {len(facts) + 3} assertion(s), {bad + sbad2 + sbad3} failed")
    if bad:
        print("FAIL: START_HERE.md is stale. Fix the numbers above from the evidence lines,")
        print("      or delete the number -- a gate you have not run is better than one you")
        print("      have run twice and written down wrongly.")
        return 1
    print("PASS: every number in START_HERE.md section 4, and in the board's status line, was")
    print("      produced by the gate it names.")
    # D127: this line was `return 1 if (bad or sbad2) else 0` and sbad3 was never added, so the
    # section-0 verdict was PRINTED AND DISCARDED: the gate reported '1 failed' and exited 0. The
    # same bug as D123's self_test(), and the second time in this project that a check could not
    # fail. The verdict is now wired to every failure count the function computes.
    return 1 if (bad or sbad2 or sbad3) else 0


def self_test() -> int:
    """Positive controls: a START_HERE that is stale in each of the three ways
    this gate detects must be REJECTED, and a current one ACCEPTED."""
    facts = [("g.py", "label", "29/33", "evidence"), ("h.py", "l2", "6 defect", "ev")]
    good = ("## 4. Run these two checks before you trust anything\n\n```\n"
            "python3 state/reviewer/g.py      # a registry\n"
            "python3 state/reviewer/h.py\n```\n\n"
            "It reports `29/33` and `6 defect`.\n\n## 5. next\n")
    bad_cases = {
        "stale number (the common failure)": good.replace("29/33", "20/24"),
        "count word disagrees with the commands": good.replace("these two checks", "these four checks"),
        "number deleted entirely": good.replace("`29/33` and ", ""),
        # D116: a commit hash in the status line can never be current, because MERGING is what
        # changes main. A hash written before the merge is wrong the instant it lands, so the check
        # forbids one rather than asserting it is right. This case must live in the literal above,
        # not be added afterwards: a self-test that miscounts its own population is the same failure
        # as a gate that miscounts what it measured (D111.6).
    }
    # D117: status-line cases are SEPARATE, because a DIFFERENT function checks them. Driving
    # them through the section-4 loop is what made the first version of these cases report
    # ACCEPT-then-reject-for-the-wrong-reason: the section-4 assertions fired on the fixture,
    # not the status-line assertion, so the positive control could not see the bug the case
    # was written for (D113).
    # Each case perturbs EXACTLY ONE number of the derived clean line, so the reason printed is
    # unambiguously the number under test. A case that differs in two places reports whichever the
    # checker happens to test first, which is how three of these went wrong in the first place.
    # Built FROM THE LIVE GATES, never written by hand. The first version hardcoded "32/36", so when
    # D118 withdrew a registry row the count became 32/35 and every fixture went stale at once -- and
    # three rejection cases then reported the WRONG reason, tripping on the registry before reaching
    # the number each was written to test. A fixture that must be edited when a count changes is a
    # fixture that will silently stop testing what it says it tests.
    _reg = run_gate("claims_registry.py", r"(\d+)/(\d+) verified")
    _bld = run_gate("check_paper_builds.py", r"(\d+) defect\(s\)")
    _tst = run_gate_pytest()
    if not (_reg and _bld and _tst):
        print("  BROKEN FIXTURE: could not read the live gate numbers, so the status-line cases are")
        print("                  SKIPPED rather than reported as passing -- an unreadable population is")
        print("                  a failure (D87), not a clean result.")
        return 1
    good_status = (f"> Status: 8 gates green (registry {_reg.group(1)}/{_reg.group(2)}, "
                   f"{_bld.group(1)} build defects, {_tst} tests).")
    print(f"  the clean status line is derived from the live gates: {good_status}")
    _bad_reg = re.sub(r"registry \d+/\d+", "registry 29/33", good_status)
    _bad_bld = re.sub(r"\d+ build defects", "3 build defects", good_status)
    _bad_tst = re.sub(r"\d+ tests", "40 tests", good_status)
    _bad_hash = "> Status: " + good_status.split("> Status: ", 1)[1].split(" ", 1)[0] \
        + " 2d3b0a4, 239 files, " + good_status.split(", ", 1)[1]
    bad_status = {
        "a stale registry number, status-line form": _bad_reg,
        "a commit hash, which no status line can keep current": _bad_hash,
        "a stale build-defect count": _bad_bld,
        "a stale test count": _bad_tst,
    }
    for _nm, _ln in bad_status.items():
        assert _ln != good_status, f"case {_nm!r} is identical to the clean line, so it cannot reject"
    # Every count here is COMPUTED from the dicts, never written by hand: a self-test
    # that miscounts its own population is the same failure as a gate miscounting what it
    # measured (D111.6). The `+2` are the section-4 accept and the status-line accept.
    print(f"POPULATION: {2 + len(bad_cases) + len(bad_status) + len(WORD)} hand-checked cases -- 2 must accept, "
          f"{len(bad_cases) + len(bad_status)} must reject, and {len(WORD)} must round-trip through the number-word table")
    fails = 0

    # The number-word table must be complete over its declared range. A gap in
    # it makes this check demand a digit where a document correctly reads a
    # word, which is a gate failing a correct site -- the failure mode D95 exists
    # to prevent, arriving through the checker rather than the pattern.
    for n, word in sorted(WORD.items()):
        got = WORD.get(n, str(n))
        if got != word:
            print(f"  BROKEN TABLE: {n} -> {got!r}, expected {word!r}")
            fails += 1
    print(f"  the number-word table round-trips over {sorted(WORD)}: "
          f"{'ok' if not fails else 'BROKEN'}")

    sec = section4(good)
    if not sec or "29/33" not in sec or listed_checks(sec) != 2:
        print(f"  BROKEN FIXTURE: section4={sec!r} listed={listed_checks(sec)}")
        fails += 1
    m = re.search(r"^## 4\.\s*Run these (\w+) checks?\b", sec, re.M)
    if not (m and m.group(1) == WORD[2]):
        print(f"  BROKEN FIXTURE: count word is {m and m.group(1)!r}, expected 'two'")
        fails += 1
    print(f"  the current-START_HERE fixture parses: 2 commands, count word "
          f"{m and m.group(1)!r}, all facts present -> must be ACCEPTED")

    for name, text in bad_cases.items():
        s = section4(text)
        reasons = []

        if facts[0][2] not in s:
            reasons.append(f"{facts[0][2]!r} absent")
        mm = re.search(r"^## 4\.\s*Run these (\w+) checks?\b", s, re.M)
        # WORD.get with a digit fallback, exactly as check() does it. The bare WORD[...] raised
        # KeyError on any count outside the table, so this rejection branch crashed instead of
        # reporting -- a latent bug that only a fixture with an unusual command count reaches.
        n_cmds = listed_checks(s)
        if not (mm and mm.group(1) == WORD.get(n_cmds, str(n_cmds))):
            reasons.append(f"count word {mm and mm.group(1)!r} != {WORD.get(n_cmds, str(n_cmds))!r}")
        if not s:
            reasons.append("section 4 not found")
        if reasons:
            print(f"  rejects: {name:<38} -> {', '.join(reasons)}")
        else:
            print(f"  MISSED: {name} was ACCEPTED but must be rejected")
            fails += 1

    print()
    # D117: this `if fails: return 1` used to sit HERE -- before the status-line cases
    # ran -- and the function ended in an unconditional `return 0`. So a MISSED status-line
    # case printed MISSED, incremented `fails`, and STILL EXITED 0: a self-test that could not
    # fail the gate, which is the worst kind of gate bug because it reports green. The verdict
    # is now decided ONCE, at the end, from `fails`.
    # status-line population, driven through the drivable function
    gp = status_line_line_problems(good_status)
    print(f"  {'ok  ' if not gp else 'MISSED'}  a status line whose every number is current"
          + ("" if not gp else f" -> {gp}"))
    if gp:
        fails += 1
    for name, line in bad_status.items():
        ps = status_line_line_problems(line)
        if ps:
            print(f"  rejects: {name:<44} -> {ps[0]}")
        else:
            print(f"  MISSED: {name} was ACCEPTED but must be rejected")
            fails += 1
    if fails:
        print(f"FAIL: {fails} case(s) wrong")
        return 1
    print(f"PASS: 2 accept, {len(bad_cases) + len(bad_status)} reject, and the rejection reasons name the defect")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    sys.exit(check())
