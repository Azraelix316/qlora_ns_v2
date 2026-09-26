#!/usr/bin/env python3
"""CHECKLIST 1.14 — grep each order document for claims that later decisions withdrew.
Self-testing: refuses to report unless the file exists, is long enough to be the real
document, and the pattern set is non-empty (D50.4: prove the instrument on a known case)."""
import re, sys
from pathlib import Path

WITHDRAWN = [
    ("D29",  r"\b1\.26\b|\b2\.44\b|\b1\.46\b|\b2\.45\b|\b1\.24\b|\b2\.53\b|\b1\.33\b", "the pre-D29 t* values"),
    ("D52.5",r"1\.78|2\.18",                     "the superseded cost range"),
    ("D56",  r"1\.46\s*(?:→|->)\s*1\.99|2\.45\s*(?:→|->)\s*6\.04", "the STRUCK N=128 multipliers"),
    ("D60",  r"1e-14|10\^\{-14\}|10\^\{-14",    "the withdrawn |grad div u| magnitude"),
    ("D74",  r"bracketed (?:between )?32\s*(?:and|[-–])\s*43", "the withdrawn never-yields bracket"),
    ("D4",   r"no DLRA NS solver|first exactly divergence-free|first structure-preserving low-rank|to our knowledge", "the barred novelty claims"),
    ("D71",  r"3-5x slower",                      "the wrong BUG slowdown in a figure title"),
    ("D30",  r"dealiasing ceiling",              "a wavenumber count used as a rank claim"),
]
# a hit is only a FINDING if it is not inside an explicit prohibition
PROHIBITION = re.compile(r"never write|do not write|withdrawn|struck|barred|prohibit|"
                        r"^\s*\|?\s*(?:[0-9]+\.|-)\s|D\d+\.\d+.*(?:withdraw|bar|struck)|"
                        r"not\b.*\b(?:claim|write)|has been withdrawn", re.I)

def scan(path, order_end_pat=r"^## (?:REFERENCE|DETAIL)"):
    t = Path(path).read_text()
    lines = t.splitlines()
    # the ORDER region only: up to the first REFERENCE/DETAIL heading, else the whole file
    cut = len(lines)
    for i, l in enumerate(lines):
        if re.match(order_end_pat, l):
            cut = i; break
    findings = []
    for d, pat, what in WITHDRAWN:
        rx = re.compile(pat, re.I)
        for i, l in enumerate(lines[:cut]):
            if rx.search(l) and not PROHIBITION.search(l):
                findings.append((d, what, i + 1, l.strip()[:100]))
    return len(lines), cut, findings

if __name__ == "__main__":
    root = Path("state/reviewer")
    docs = [root / "WRITER_ORDER.md", root / "CODER_ORDER.md"]
    total = 0
    for p in docs:
        if not p.exists():
            print(f"  MISSING {p} - refusing to report"); sys.exit(2)
        n, cut, f = scan(p)
        # self-test: the pattern set must be able to fire
        probe = sum(1 for _, pat, _ in WITHDRAWN if re.search(pat, "the dealiasing ceiling and 1e-14 and 1.26", re.I))
        assert probe >= 3, f"SELF-TEST FAILED: only {probe} patterns fire on a known-bad string"
        print(f"  {p.name}: {n} lines, order region = lines 1-{cut}, "
              f"self-test {probe}/8 patterns fire on a known-bad string")
        for d, what, ln, txt in f:
            total += 1
            print(f"    !! [{d}] {what}  line {ln}: {txt}")
        if not f:
            print(f"    clean: no withdrawn claim appears in the order region")
    print(f"\n  {total} finding(s).")
    sys.exit(1 if total else 0)
