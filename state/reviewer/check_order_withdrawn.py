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
    ("D74",   r"bracketed (?:between )?32\s*(?:and|[-–])\s*43",
     "the withdrawn never-yields bracket"),
    ("D4",    r"no DLRA NS solver|first exactly divergence-free|"
              r"first structure-preserving low-rank|to our knowledge",
     "the barred novelty claims"),
    ("D71",   r"3-5x slower", "the wrong BUG slowdown in a figure title"),
    ("D30",   r"dealiasing ceiling", "a wavenumber count used as a rank claim"),
]

# A hit is only a CANDIDATE if the line is not itself telling the reader not to write it.
PROHIBITION = re.compile(
    r"never write|do not write|withdrawn|struck|barred|prohibit|"
    r"not\b[^.]{0,40}\b(?:claim|write)|hardcodes|says\b[^.]{0,60}\bwrong|"
    r"^\s*\|?\s*(?:[0-9]+\.|-)\s|still says|described as wrong",
    re.I,
)

ORDER_END = re.compile(r"^## (?:REFERENCE|DETAIL)")


def scan(path):
    lines = Path(path).read_text().splitlines()
    cut = len(lines)
    for i, line in enumerate(lines):
        if ORDER_END.match(line):
            cut = i
            break
    found = []
    for decision, pattern, what in WITHDRAWN:
        rx = re.compile(pattern, re.I)
        for i, line in enumerate(lines[:cut]):
            if rx.search(line) and not PROHIBITION.search(line):
                found.append((decision, what, i + 1, line.strip()[:100]))
    return len(lines), cut, found


def main():
    root = Path(__file__).resolve().parent
    docs = [root / "WRITER_ORDER.md", root / "CODER_ORDER.md"]

    for d in docs:
        if not d.exists():
            print(f"MISSING {d} - refusing to report")
            return 2

    # Self-test: the pattern set must be able to fire on a string known to be bad.
    probe = "the dealiasing ceiling and 1e-14 and 1.26 and 3-5x slower and 1.46->1.99"
    fired = sum(1 for _, pat, _ in WITHDRAWN if re.search(pat, probe, re.I))
    if fired < 5:
        print(f"SELF-TEST FAILED: only {fired} of {len(WITHDRAWN)} patterns fire on a known-bad string")
        return 2
    print(f"SELF-TEST PASS: {fired}/{len(WITHDRAWN)} patterns fire on a known-bad string")

    total = 0
    for d in docs:
        n, cut, found = scan(d)
        print(f"\n{d.name}: {n} lines, order region = lines 1-{cut}")
        for decision, what, line, text in found:
            total += 1
            print(f"  CANDIDATE [{decision}] {what}  line {line}: {text}")
        if not found:
            print("  no candidates")
    print(f"\n{total} CANDIDATE(S). Exit 1 means candidates exist, NOT that a defect does.")
    print("Read each one: it is a prohibition, a quoted defect, or a finding - or it is real.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
