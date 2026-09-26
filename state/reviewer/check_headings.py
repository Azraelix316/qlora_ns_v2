#!/usr/bin/env python3
"""Heading integrity for the reviewer's own binding documents.

WHY THIS EXISTS. `DECISIONS.md` is the binding document: every other agent
cites it by decision number, and a reader locates a decision by grepping for
`## D<n>`. Five of its headings were wrapped across two lines with `## ` on
*both* lines, so the second line rendered as a heading of its own. One of the
five began `## D12's preference into evidence`, which means `grep -n '## D12'`
returns a line that is not D12 (D12 is at line 691). That is D86.3's failure
mode -- Markdown written by hand and wrapped -- and it was found by reading,
not by any check.

THE RULE, AND WHY IT IS THIS RULE. A `## ` line immediately following another
`## ` line is a wrapped heading. Genuine consecutive headings are legal in
these documents only when the second is a *sub-decision* (`## D19.4a`),
which never immediately follows its parent `## D19` -- sub-decisions are always
separated by the parent's body. So the rule has no false positives here, and
the population is printed so that can be re-checked rather than believed.

SCOPE IS THE IDENTIFIER, NOT THE STRING (D95). The check looks at heading
*structure* -- `## ` at the start of a line, and adjacency -- never at the
wording of a heading. It therefore cannot fire on a correct site because a
number in it happens to resemble a decision number, which is what D95's first
pattern did.

Usage:  check_headings.py            check the documents
        check_headings.py --self-test  prove the check can fail
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The reviewer's own documents. Only state/reviewer/ is ours, so this is the
# whole population -- there is no other file we are allowed to hold to this.
DOCS = [
    "DECISIONS.md",
    "CLAIMS.md",
    "reviews/CHECKLIST.md",
    "WRITER_ORDER.md",
    "CODER_ORDER.md",
    "START_HERE.md",
    "NOTES.md",
    "PROVENANCE_ATTESTATION_N128.md",
]


def wrapped_headings(lines: list[str]) -> list[tuple[int, str, str]]:
    """Return (1-based line no, heading start, continuation) for each wrap."""
    hits: list[tuple[int, str, str]] = []
    for i in range(len(lines) - 1):
        a, b = lines[i], lines[i + 1]
        if a.startswith("## ") and b.startswith("## "):
            hits.append((i + 1, a, b))
    return hits


def phantom_decision_numbers(lines: list[str]) -> list[tuple[int, str]]:
    """Continuation lines whose text begins `D<n>`, i.e. that impersonate a
    decision number in a grep for it. This is the harmful subset: a wrapped
    heading that does NOT look like a decision is merely untidy, one that DOES
    sends a reader to the wrong place."""
    out = []
    for i in range(len(lines) - 1):
        b = lines[i + 1]
        if lines[i].startswith("## ") and b.startswith("## D"):
            out.append((i + 2, b))
    return out


STATUS_CAP = 400
"""A `> Status:` line longer than this is a log that has forgotten it is a
status line. See D107: mine reached 33,003 characters -- 5,513 words on ONE
line -- all of it history that was already in the 165 dated `## Log` entries
directly below it. AGENTS.md calls this field "the one-line current state"."""

_ONE_LINE_STATUS = (
    "> Status: main 6a2b676, 217 files, 0 pycache, 5 gates green, 46 tests. "
    "Next: writer D13/D14, coder C2-1."
)


def status_failures(lines: list[str]) -> tuple[int, str]:
    """(failures, evidence) for the board's one-line status field.

    Two properties, both structural rather than textual: there is exactly one
    `> Status:` line, and it fits in STATUS_CAP characters. Neither depends on
    the wording, so this cannot fire because a status says something the check
    disagrees with -- only because it has stopped being a status.
    """
    hits = [l for l in lines if l.startswith("> Status:")]
    if len(hits) != 1:
        return 1, f"found {len(hits)} '> Status:' lines, expected exactly 1"
    if len(hits[0]) > STATUS_CAP:
        return 1, (f"the '> Status:' line is {len(hits[0])} characters "
                   f"({len(hits[0].split())} words) on ONE line; the cap is "
                   f"{STATUS_CAP}. History belongs in the dated '## Log' "
                   f"entries below it.")
    return 0, f"1 line, {len(hits[0])} characters, cap {STATUS_CAP}"


def check_status_line() -> tuple[int, str]:
    p = HERE / "NOTES.md"
    if not p.exists():
        return 0, "NOTES.md absent, skipped"
    return status_failures(p.read_text().splitlines())


def check() -> int:
    present = [d for d in DOCS if (HERE / d).exists()]
    missing = [d for d in DOCS if not (HERE / d).exists()]
    total_lines = 0
    total_heads = 0
    bad = 0
    phantoms = 0

    print(f"POPULATION: {len(present)} document(s) in {HERE}")
    if missing:
        print(f"  (not present, skipped: {', '.join(missing)})")
    print("  rule: a line starting '## ' must not immediately follow another '## ' line")
    print()

    for name in present:
        lines = (HERE / name).read_text().splitlines()
        total_lines += len(lines)
        heads = sum(1 for l in lines if l.startswith("## "))
        total_heads += heads
        wraps = wrapped_headings(lines)
        ph = phantom_decision_numbers(lines)
        bad += len(wraps)
        phantoms += len(ph)
        flag = "FAIL" if wraps else "ok  "
        print(f"  {flag}  {name:<34} {len(lines):>6} lines, {heads:>3} '## ' lines, "
              f"{len(wraps)} wrapped heading(s)")
        for ln, a, b in wraps:
            print(f"          line {ln}: continuation renders as its own heading")
            print(f"            {a.strip()[:96]}")
            print(f"            {b.strip()[:96]}")
        for ln, b in ph:
            print(f"          line {ln}: IMPERSONATES A DECISION NUMBER -> grep for it returns the wrong line")
            print(f"            {b.strip()[:96]}")

    print()
    sbad, sev = check_status_line()
    print(f"  {'FAIL' if sbad else 'ok  '}  NOTES.md '> Status:' line: {sev}")

    print()
    print(f"TOTAL: {total_lines} lines, {total_heads} '## ' lines, "
          f"{bad} wrapped heading(s), {phantoms} impersonating a decision number, "
          f"{sbad} status-line failure(s)")
    if bad or sbad:
        print()
        if bad:
            print("FAIL: join each continuation onto its heading line, or demote it to plain text.")
            print("      Do NOT delete the words -- the title text is load-bearing.")
        if sbad:
            print("FAIL: the board's '> Status:' line must be ONE line. Cut it back to the")
            print("      current state and the top blockers; the history is already in '## Log'.")
        return 1
    print("PASS")
    return 0


def self_test() -> int:
    """A check that reports clean has usually measured nothing. Each case below
    is hand-verified, and the POSITIVE controls are the three that must fire."""
    good = [
        "## D19 - Peak memory\n\nbody\n",
        "## D19.4a - sub-decision\n\nbody\n",
        "## D19 - Peak memory\n\n## a genuine second heading\n",  # legal, non-adjacent
        "### D1 - deeper level heading\n\nbody\n",
        "# D1 - h1\n\nbody\n",
        "plain text with ## inside it, not at line start\n",
        "## D20 - no trailing newline",
    ]
    bad_wrap = [
        ("## D18 - The windowed rank rule was built\n## D12's preference into evidence\n",
         1, "D18 - The windowed rank rule was built", "D12's preference into evidence"),
        ("## D19 - Peak memory: no advantage\n## on an independent axis\n",
         1, "D19 - Peak memory: no advantage", "on an independent axis"),
    ]
    print("POPULATION: 7 must-pass cases and 2 must-fire cases (the positive controls)")
    print("  the two must-fire cases are hand-checked: one whose continuation reads as a")
    print("  DECISION NUMBER and one whose continuation does not. The check must fire on")
    print("  both, and must call only the first a phantom decision number.")
    fails = 0
    for t in good:
        lines = t.rstrip("\n").split("\n")
        w = wrapped_headings(lines)
        if w:
            print(f"  FALSE POSITIVE on {t.splitlines()[0][:56]!r}: {w}")
            fails += 1
    phantom_counts = []
    for t, n, a, b in bad_wrap:
        lines = t.rstrip("\n").split("\n")
        w = wrapped_headings(lines)
        ph = phantom_decision_numbers(lines)
        got_a = w[0][1].removeprefix("## ") if w else None
        got_b = w[0][2].removeprefix("## ") if w else None
        want_ph = 1 if b.startswith("D") else 0
        phantom_counts.append(len(ph))
        if not w:
            print(f"  MISSED the wrap in {a[:40]!r}")
            fails += 1
            continue
        if w[0][0] != n or got_a != a or got_b != b:
            print(f"  WRONG match: {(w[0][0], got_a, got_b)} != {(n, a, b)}")
            fails += 1
        if len(ph) != want_ph:
            print(f"  WRONG phantom count: {len(ph)} != {want_ph} for {b[:40]!r}")
            fails += 1
        print(f"  fires as required: {a[:44]!r} + {b[:44]!r} "
              f"(phantom decision number: {len(ph)}, expected {want_ph})")
    print()
    if fails:
        print(f"FAIL: {fails} case(s) wrong")
        return 1
    print(f"PASS: 7 must-pass clean, 2 must-fire fire, and the phantom subset discriminates "
          f"({phantom_counts[0]} vs {phantom_counts[1]})")

    # --- the status-line property, with its own positive controls
    print()
    print("  the board's '> Status:' line: 2 must-pass, 2 must-fire")
    ok_cases = {
        "a genuine one-liner": ["> Status: main abc1234, 7 gates green. Next: C2-1."],
        "one liner among other content": ["# NOTES", "", _ONE_LINE_STATUS, "", "## Log", "- 2026-01-01 x"],
    }
    for name, lines in ok_cases.items():
        n, ev = status_failures(lines)
        if n:
            print(f"    FALSE POSITIVE on {name}: {ev}")
            fails += 1
        else:
            print(f"    clean: {name} ({ev})")
    bad_cases = {
        "the real defect: one line, ~34,000 chars": ["> Status: main abc1234. " + "x " * 17000],
        "two status lines": [_ONE_LINE_STATUS, _ONE_LINE_STATUS],
    }
    for name, lines in bad_cases.items():
        n, ev = status_failures(lines)
        if not n:
            print(f"    MISSED: {name} was ACCEPTED but must be rejected")
            fails += 1
        else:
            print(f"    fires as required: {name} -> {ev[:86]}")
    print()
    if fails:
        print(f"FAIL: {fails} case(s) wrong")
        return 1
    print("PASS: heading cases and status-line cases both discriminate")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    sys.exit(check())
