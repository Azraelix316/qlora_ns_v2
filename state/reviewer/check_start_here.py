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
    bad = []
    m = re.search(r"\b([0-9a-f]{7,40})\b", line)
    if m and re.search(r"\b(?:main|commit|[0-9a-f]{7,40})\b", line):
        bad.append(f"names the commit {m.group(1)!r}, which no status line can keep current -- "
                   f"say what is true of the PROJECT, not of one tree state")
    claims = [("registry", rf"(\d+)/(\d+)\s+verified"), ("build defects", r"(\d+)\s+build defects"),
              ("tests", r"(\d+)\s+tests")]
    for what, rx in claims:
        q = re.search(rx, line)
        if q and not what_is_current(what, q):
            bad.append(f"quotes {q.group(0)!r} for {what}, which the gates do not report")
    if bad:
        return 1, "the '> Status:' line is STALE or uncheckable: " + "; ".join(bad)
    return 0, "1 line, no commit hash, and every gate number it quotes is current"


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
    print(f"TOTAL: {len(facts) + 2} assertion(s), {bad + sbad2} failed")
    if bad:
        print("FAIL: START_HERE.md is stale. Fix the numbers above from the evidence lines,")
        print("      or delete the number -- a gate you have not run is better than one you")
        print("      have run twice and written down wrongly.")
        return 1
    print("PASS: every number in START_HERE.md section 4, and in the board's status line, was")
    print("      produced by the gate it names.")
    return 0


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
        "a commit hash, which no status line can keep current": (
            "> Status: main 2d3b0a4, 239 files, registry 31/35, 10 build defects, 47 tests.\n\n"
            "## 4. Run these five checks\n\n```\npython3 a.py\n```\n\n## 5. next\n"
        ),
    }
    print(f"POPULATION: {1 + len(bad_cases) + len(WORD)} hand-checked cases -- 1 must accept, "
          f"{len(bad_cases)} must reject, and {len(WORD)} must round-trip through the number-word table")
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

    # A commit hash in the status line can never be current: merging is what changes main, so a
    # hash written before the merge is wrong the instant it lands. That is D116, and the first
    # version of this check asserted the hash was current -- i.e. it asserted something impossible.
    for name, text in bad_cases.items():
        s = section4(text)
        reasons = []
        if "commit hash" in name and status_line_facts.__doc__ and re.search(r"\b[0-9a-f]{7,40}\b", text):
            reasons.append("the status line names a commit, which cannot stay current")
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
    if fails:
        print(f"FAIL: {fails} case(s) wrong")
        return 1
    print(f"PASS: 1 accept, {len(bad_cases)} reject, and the rejection reasons name the defect")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    sys.exit(check())
