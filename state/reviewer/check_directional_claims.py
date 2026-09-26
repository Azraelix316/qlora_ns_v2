#!/usr/bin/env python3
"""Directional comparative claims in paper-facing text must be sourced.

WHY THIS EXISTS. The abstract said, and I put it there:

    "under grid refinement the reduced error falls by a factor $2.2$ while the
     static baseline's grows by three orders of magnitude"

The `2.2` is sound -- it re-derives to `2.181`-`2.183` across five time keys, a
spread of 0.09% (D104). **The other half is not merely unverified, it is
contradicted**: of the 36 error-like quantities the two grid artifacts share,
**none grows by more than 10x** between `N=64` and `N=128` (largest growth
`1.64x`), and the static baseline's own `max_relative_l2_vs_full` **improves**,
`9.93e-09 -> 1.89e-09`. D56 had already recorded that quantity as unstable,
ranging `2.5x` to `1464x`, "unstably". So the abstract stated the least
defensible end of a range my own decision log had flagged as unstable.

**WHY NO EXISTING GATE CAUGHT IT.** `claims_registry.py` PART 4 traces numeric
*literals*, and it did trace `2.2` -- correctly, because `2.2` is true. The
false half is the phrase **"three orders of magnitude"**, which contains no
digit at all. A magnitude claim written in words is invisible to a literal
tracer. This is the sixth instrument failure of the same family (D60, D66, D77,
D83, D84, D95, D97): the tool measured something real and the thing that broke
was outside what it measures.

SCOPE, AND WHY IT IS NARROW (D95/D97). A gate over every "N orders of
magnitude" phrase would fire on **81** sites across the paper and my documents,
almost all of them correct. That is the noise band D97 measured at 85 false
positives and deliberately did not ship. So this gate matches only a
**COMPARATIVE** -- a contrast word (`while`, `whereas`, `but`) within 120
characters of a magnitude phrase -- which is the shape that makes a two-sided
claim a referee will check both sides of. Measured population: **1 site in the
paper.** Over the whole paper plus my decision log it is 19, and 18 of those are
either my own record *quoting the claim in order to withdraw it* or a correct
scaling argument, so the gate's scope is paper-facing text: the draft, and the
paste-ready LaTeX blocks in my order documents -- which is where I author paper
prose. A decision log must be able to quote a withdrawn claim; that is what a
log is for.

Usage:  check_directional_claims.py [--self-test]
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

NUM = r"(?:a|an|one|two|three|four|five|six|seven|eight|nine|ten|\d+(?:\.\d+)?)"
ANY = re.compile(rf"{NUM}\s+orders?\s+of\s+magnitude", re.I)
# A contrast word within 120 chars of a magnitude phrase, EITHER ORDER.
# Whitespace is collapsed first: in LaTeX the contrast word and the magnitude
# phrase routinely land on different lines, and the first version of this check
# scanned line-by-line and therefore reported 0 on a document that contains the
# defect -- a clean result that had measured nothing.
CONTRAST_A = re.compile(rf"{NUM}\s+orders?\s+of\s+magnitude.{{0,120}}?\b(?:while|whereas|but)\b", re.I | re.S)
CONTRAST_B = re.compile(rf"\b(?:while|whereas|but)\b.{{0,120}}?{NUM}\s+orders?\s+of\s+magnitude", re.I | re.S)


def _sh(*a: str) -> str:
    return subprocess.run(a, cwd=REPO, capture_output=True, text=True).stdout


def _strip_comments(t: str) -> str:
    """Drop LaTeX comments: a commented-out sentence is not a claim."""
    out = []
    for line in t.splitlines():
        cut, esc = len(line), False
        for j, ch in enumerate(line):
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == "%":
                cut = j
                break
        out.append(line[:cut])
    return "\n".join(out)


def _order_blocks(name: str) -> list[tuple[str, str]]:
    """(label, text) for each paste-ready ```latex block in one of my order docs."""
    p = HERE / name
    if not p.exists():
        return []
    src = p.read_text()
    return [(f"{name} block {i}", b)
            for i, b in enumerate(re.findall(r"```latex\n(.*?)\n```", src, re.S), 1)]


def sources() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    files = [f for f in _sh("git", "ls-tree", "-r", "--name-only", "HEAD", "--", "paper").splitlines()
             if f.endswith(".tex")]
    for f in files:
        out.append((f, _sh("git", "show", f"HEAD:{f}")))
    for doc in ("WRITER_ORDER.md", "CODER_ORDER.md"):
        for label, b in _order_blocks(doc):
            out.append((label, b))
    return out


def scan() -> tuple[int, int, list[tuple[str, str]]]:
    n_phrase = 0
    hits: list[tuple[str, str]] = []
    for label, text in sources():
        flat = re.sub(r"\s+", " ", _strip_comments(text))
        n_phrase += len(ANY.findall(flat))
        spans: list[tuple[int, int]] = []
        for rx in (CONTRAST_A, CONTRAST_B):
            for m in rx.finditer(flat):
                spans.append(m.span())
        # Merge overlapping spans. CONTRAST_A and CONTRAST_B both fire on one
        # sentence when the contrast word sits between the two magnitudes, so
        # without this the same claim is reported twice -- which is how a
        # candidate list trains a reader to skip it (D95).
        merged: list[tuple[int, int]] = []
        for s, e in sorted(spans):
            if merged and s <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))
            else:
                merged.append((s, e))
        for s, e in merged:
            hits.append((label, flat[max(0, s - 60):e + 40].strip()))
    return n_phrase, len(hits), hits


def check() -> int:
    n_phrase, n_hits, hits = scan()
    n_src = len(sources())
    print(f"POPULATION: {n_src} paper-facing source(s) -- every .tex file of HEAD:paper, plus the")
    print(f"            paste-ready ```latex blocks of WRITER_ORDER.md and CODER_ORDER.md.")
    print(f"            Comments are stripped; whitespace is collapsed before matching.")
    print(f"  'N orders of magnitude' phrases: {n_phrase}")
    print(f"  COMPARATIVES (contrast word within 120 chars of a magnitude phrase): {n_hits}")
    print()
    if not hits:
        print("PASS: no directional comparative magnitude claim in paper-facing text.")
        print("      Each such claim is a two-sided assertion a referee will check on both")
        print("      sides, and neither side is a literal a registry row can pin.")
        return 0
    for label, s in hits:
        print(f"  CANDIDATE  {label}")
        print(f"            ...{s}...")
    print()
    print("FAIL: a directional comparative magnitude claim is unsourced or contradicted.")
    print("      For each candidate: name the artifact, the quantity, and the indexing, and")
    print("      check BOTH sides. A range my own log records as unstable cannot be stated")
    print("      as a point value -- say it is not stably measurable, or drop the clause.")
    return 1


def self_test() -> int:
    good = [
        "the residual is seven orders of magnitude below the trajectory error",
        "the ratio falls by an order of magnitude as N grows",
        "while the static baseline holds, the reduced error does not",          # no magnitude
        "% while the static baseline's grows by three orders of magnitude",     # commented out
        "the horizon grows by factors of $1.45$ and $1.64$ from a $64^2$ grid",  # corrected form
    ]
    bad = [
        ("error falls by a factor $2.2$ while the static baseline's\ngrows by three orders of magnitude",
         "the real defect, split across a LaTeX line break"),
        ("the static baseline grows by three orders of magnitude, whereas ours does not fall",
         "contrast word AFTER the magnitude phrase"),
    ]
    print(f"POPULATION: {len(good)} must-pass and {len(bad)} must-fire cases")
    print("  the must-fire cases are the two orderings of the same shape; the first is the")
    print("  defect verbatim, including the line break that defeated the first version.")
    fails = 0
    for t in good:
        flat = re.sub(r"\s+", " ", _strip_comments(t))
        n = len({m.span() for rx in (CONTRAST_A, CONTRAST_B) for m in rx.finditer(flat)})
        if n:
            print(f"  FALSE POSITIVE on {t[:56]!r}: {n} hit(s)")
            fails += 1
    for t, why in bad:
        flat = re.sub(r"\s+", " ", _strip_comments(t))
        n = len({m.span() for rx in (CONTRAST_A, CONTRAST_B) for m in rx.finditer(flat)})
        if not n:
            print(f"  MISSED: {why}")
            fails += 1
        else:
            print(f"  fires as required: {why}")
    print()
    if fails:
        print(f"FAIL: {fails} case(s) wrong")
        return 1
    print(f"PASS: {len(good)} must-pass clean, {len(bad)} must-fire fire")
    return 0


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else check())
