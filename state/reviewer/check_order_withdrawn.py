#!/usr/bin/env python3
"""
check_order_withdrawn.py — CHECKLIST 1.14 (D76, D77). Reviewer instrument.

WHAT IT DOES. Grep each agent order document for claims that later decisions withdrew, in the
ORDER region only (above the first REFERENCE/DETAIL heading), skipping lines that are
themselves prohibitions.

THIS IS A LIST OF CANDIDATES FOR THE REVIEWER TO READ, NOT AN AUTOMATED PASS/FAIL. On its first
run over both documents it gave 11 raw hits and 0 real defects, in three false-positive classes:
  - a PROHIBITION      ("`1.1e-13` (not `1e-14`)" is the correct form, and the grep flags it)
  - a QUOTED DEFECT    (the "3-5x slower" title, described as the thing that is wrong)
  - a FINDING STATED CORRECTLY (D74's own result)
A pure grep cannot distinguish "write this claim" from "this claim is wrong, do not write it" from
"this claim turned out to be true", and these documents are mostly made of descriptions of
defects. This is the same failure as D104 (matching a NAME where a ROLE was needed) and as D111
(a figure title is where false suspicions are generated; the artifact is where they die).

The automation's value is that it FINDS THE CANDIDATES. Its limitation is that it cannot RANK
them. Print the population; the verdict is the reviewer's (D55c.6, D98).

It has twice found a real defect in the reviewer's own prose, and both were wording rather than
code: the pre-send instruction that had silently no-op'd (D76.3), and D74's own "is the dealiasing
ceiling" phrasing, which invited exactly the conflation D30 bars (D77.2).

SELF-TESTS (D50.4). Refuses to report unless every document exists and the pattern set fires on a
known-bad string.

EXIT. 1 means CANDIDATES EXIST. It does not mean a defect does. This is the only check in this
project that exits 1 for candidates rather than for defects.

Run:  python3 check_order_withdrawn.py
"""
import re
import sys
from pathlib import Path

# (decision that withdrew it, pattern, what it is)
WITHDRAWN = [
    ("D29",   r"\b1\.26\b|\b2\.44\b|\b1\.46\b|\b2\.45\b|\b1\.24\b|\b2\.53\b|\b1\.33\b",
     "the pre-D29 t* values"),
    ("D52.5", r"1\.78|2\.18", "the superseded cost range"),
    ("D56",   r"1\.46\s*(?:→|->)\s*1\.99|2\.45\s*(?:→|->)\s*6\.04", "the STRUCK N=128 multipliers"),
    ("D60",   r"1e-14|10\^\{-14\}",
     "the withdrawn |div u| magnitude"),
    # \s+ not " ": these documents hard-wrap, and "bracketed\n   between 32 and 43"
    # is the very instance this gate exists to catch (D78).
    ("D74",   r"bracketed\s+(?:between\s+)?32\s*(?:and|[-–])\s*43",
     "the withdrawn never-yields bracket"),
    ("D4",    r"no DLRA NS solver|first exactly divergence-free|"
              r"first structure-preserving low-rank|to our knowledge",
     "the barred novelty claims"),
    ("D71",   r"3-5x slower", "the wrong BUG slowdown in a figure title"),
    ("D30",   r"dealiasing ceiling", "a wavenumber count used as a rank claim"),
]

# A hit is only a CANDIDATE if the line is not itself telling the reader not to write it.
# NEGATIVE-CONTROLLED (D78). An earlier version of this filter also suppressed any line beginning
# with a number, to silence the old numbered Tier items. A positive control then caught only 1 of 4
# injected bad claims -- because "1. The never-yields rank is bracketed..." and "2. The cost is
# 1.78 to 2.18..." are the SAME SHAPE as the items it was suppressing. The rule was eating the
# findings. Suppression by shape cannot work when the target format and the noise have one format,
# so this filter is now LINGUISTIC ONLY: it suppresses a line that SAYS it is prohibiting something,
# and nothing else. Everything else is reported and the reviewer ranks it (D77.3).
PROHIBITION = re.compile(
    r"never write|do not write|withdrawn|struck|barred|prohibit|"
    r"hardcodes|hard-codes|still says|described as wrong|"
    r"\bnot\b[^.]{0,40}\b(?:claim|write|print)|"
    r"\bis wrong\b|\bare wrong\b|\bfalse\b[^.]{0,20}\btitle\b",
    re.I,
)

ORDER_END = re.compile(r"^## (?:REFERENCE|DETAIL)")


def fenced_latex_regions(lines):
    """Line ranges of every ```latex ... ``` block, ANYWHERE in the file.

    A withdrawn phrase inside paste-ready text is MORE dangerous than one in the index,
    because the writer pastes it verbatim and it stops being a warning and becomes the
    paper. The order-region scan alone cannot see it: D18b sat at line ~670, well below
    the fold, carrying the exact "dealiasing ceiling" phrasing D77.2 had barred (D83).
    """
    regions, i = [], 0
    while i < len(lines):
        if lines[i].strip().startswith("```latex"):
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("```"):
                j += 1
            regions.append((i, min(j + 1, len(lines))))
            i = j + 1
        else:
            i += 1
    return regions


def scan(path):
    lines = Path(path).read_text().splitlines()
    cut = len(lines)
    for i, line in enumerate(lines):
        if ORDER_END.match(line):
            cut = i
            break
    latex = fenced_latex_regions(lines)
    in_latex = set()
    for a, b in latex:
        in_latex.update(range(a, b))
    found = []
    for decision, pattern, what in WITHDRAWN:
        rx = re.compile(pattern, re.I)
        for i, line in enumerate(lines):
            if i >= cut and i not in in_latex:
                continue                      # order region, or paste-ready text
            if rx.search(line) and not PROHIBITION.search(line):
                kind = "PASTE-READY TEXT" if i in in_latex else "order"
                found.append((decision, what, i + 1, kind, line.strip()[:100]))
    return len(lines), cut, len(latex), found


def main():
    root = Path(__file__).resolve().parent
    docs = [root / "WRITER_ORDER.md", root / "CODER_ORDER.md"]

    for d in docs:
        if not d.exists():
            print(f"MISSING {d} - refusing to report")
            return 2

    # Self-test: the pattern set must be able to fire on a string known to be bad.
    probe = "the dealiasing ceiling and 1e-14 and 1.26 and 3-5x slower and 1.46->1.99"
    # the wrapped form must fire too, or the gate is blind to hard-wrapped prose (D78)
    wrapped = "bracketed\n   between 32 and 43"
    if not re.search(dict((d, p) for d, p, _ in WITHDRAWN)["D74"], wrapped, re.I):
        print("SELF-TEST FAILED: the D74 pattern does not fire on the line-wrapped form")
        return 2
    fired = sum(1 for _, pat, _ in WITHDRAWN if re.search(pat, probe, re.I))
    if fired < 5:
        print(f"SELF-TEST FAILED: only {fired} of {len(WITHDRAWN)} patterns fire on a known-bad string")
        return 2
    print(f"SELF-TEST PASS: {fired}/{len(WITHDRAWN)} patterns fire on a known-bad string")

    total = 0
    for d in docs:
        n, cut, nlatex, found = scan(d)
        print(f"\n{d.name}: {n} lines, order region = lines 1-{cut}, "
              f"paste-ready latex blocks = {nlatex}")
        for decision, what, line, kind, text in found:
            total += 1
            flag = "  <-- PASTE-READY, HIGHEST PRIORITY" if kind == "PASTE-READY TEXT" else ""
            print(f"  CANDIDATE [{decision}] {what}  line {line} ({kind}): {text}{flag}")
        if not found:
            print("  no candidates")
    print(f"\n{total} CANDIDATE(S). Exit 1 means candidates exist, NOT that a defect does.")
    print("Read each one: it is a prohibition, a quoted defect, or a finding - or it is real.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
