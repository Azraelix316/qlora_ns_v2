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
import os
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
    # Added R124, with the draft itself now scanned (D88).
    ("D67",   r"99\.9\s*\\?%", "the baseline energy threshold: draft says 99.9%, runs used 99%"),
    ("D32.2", r"rank is adapted online|adapted online by|online rank adaptation|"
              r"rank is adapted online as",
     "the barred online-adaptive-rank claim (only evidence is nsteps: 200)"),
    ("D85",   r"above rank[^.]{0,24}(?:\\approx\s*)?8\b",
     "the withdrawn saturation threshold (it is r=16, not above r~8)"),
]

# Lines beginning with % are LaTeX COMMENTS: they do not render, so a barred claim in one is not
# a submission defect. The draft carries the barred-claims list itself in comments, which is good
# practice — so comment hits are counted and printed separately, never mixed with rendered text.
COMMENT = re.compile(r"^\s*%")

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


def draft_lines(root):
    """The DRAFT, read from git (D88). `paper/` does not exist on `main` — the draft lives only
    on origin/agent/writer — so a filesystem glob here would silently scan nothing, which is
    exactly how claims_registry.py came to report clean results over an empty population (D87).
    Returns (rendered, commented, source)."""
    import subprocess
    ref = os.environ.get("DRAFT_REF", "origin/agent/writer")
    # `git ls-tree` restricts to the CURRENT SUBDIRECTORY, and --full-name does not lift that
    # restriction (verified: 0 hits from state/reviewer, 10 from the repo root). So run git from
    # the toplevel, not from this file's directory.
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=str(root),
                         capture_output=True, text=True).stdout.strip() or str(root)
    def sh(*a):
        return subprocess.run(a, cwd=top, capture_output=True, text=True).stdout
    names = [l for l in sh("git", "ls-tree", "-r", "--name-only", ref).splitlines()
             if l.startswith("paper/sections/") and l.endswith(".tex")]
    rendered, commented = [], []
    for n in names:
        for i, l in enumerate(sh("git", "show", f"{ref}:{n}").splitlines(), 1):
            (commented if COMMENT.match(l) else rendered).append((f"{n}:{i}", l))
    return rendered, commented, f"git {ref}:paper/sections", len(names)


def figure_titles(root):
    """Matplotlib title/label strings in the figure code, read from git (D91.10).

    Returns (lines, source, nfiles). Scans title/label/annotate/suptitle calls, because a
    withdrawn claim in a figure title reaches every reader of the paper while a withdrawn
    claim in a code comment reaches nobody.
    """
    import subprocess
    ref = os.environ.get("CODE_REF", "origin/main")
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=str(root),
                         capture_output=True, text=True).stdout.strip() or str(root)

    def sh(*a):
        return subprocess.run(a, cwd=top, capture_output=True, text=True).stdout
    names = [l for l in sh("git", "ls-tree", "-r", "--name-only", ref).splitlines()
             if l.startswith("experiments/") and l.endswith(".py")]
    out = []
    for n in names:
        for i, line in enumerate(sh("git", "show", f"{ref}:{n}").splitlines(), 1):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            out.append((f"{n}:{i}", line))
    return out, f"git {ref}:experiments/*.py", len(names)


def main():
    root = Path(__file__).resolve().parent
    # START_HERE.md is FIRST in this list deliberately: it is the file an agent opens first,
    # so a withdrawn claim there is the most likely one to be believed (D84).
    docs = [root / "START_HERE.md", root / "WRITER_ORDER.md", root / "CODER_ORDER.md"]

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

    # CHECKLIST 1.15.4: every pattern must fire on a known instance of the thing it withdraws.
    # A pattern that has never been observed to fire is a pattern that has not been shown to work.
    for decision, pat, what in WITHDRAWN:
        inst = {
            "D67":   r"$r_{\mathrm{POD}}$ resolving 99.9\% of the energy",
            "D32.2": "The rank is adapted online by incremental singular value decomposition.",
            "D85":   "above rank $\\approx 8$ additional rank buys it nothing measurable",
        }.get(decision)
        if inst is None:
            continue
        if not re.search(pat, inst, re.I):
            print(f"SELF-TEST FAILED: [{decision}] does not fire on a known instance "
                  f"({what}): {inst!r}")
            return 2
    print(f"SELF-TEST PASS: every draft-targeted pattern fires on a known instance of its claim")

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

    # The DRAFT — the artifact actually submitted (D88). Scanned last because it is the one a
    # reviewer of the paper will read, and the one no earlier decision could reach from `main`.
    rendered, commented, src, nfiles = draft_lines(root)
    print(f"\nDRAFT: {nfiles} file(s), {len(rendered)} rendered line(s) + {len(commented)} "
          f"comment line(s), from {src}")
    if not nfiles:
        print("  !! EMPTY POPULATION — the draft was not found, so NOTHING BELOW IS EVIDENCE.")
        print("     A clean result here would be vacuous (D87). Check DRAFT_REF.")
        return 1
    # The FIGURE CODE (D91.10). Both barred titles live here and nowhere else: D71's "3-5x
    # slower" and D77.2's "the dealiasing ceiling". A barred phrase in a figure title is a
    # submission defect, and this gate could not see the file that produces the most visible
    # text in the paper. Third population after the three orders (D84) and the draft (D88).
    fig, figsrc, nfig = figure_titles(root)
    print(f"\nFIGURE CODE: {nfig} file(s), {len(fig)} non-comment line(s), from {figsrc}")
    if not nfig:
        print("  !! EMPTY POPULATION - the figure code was not found (D87).")
        total += 1
    fighits = 0
    for decision, pat, what in WITHDRAWN:
        pp = re.compile(pat, re.I)
        for loc, line in fig:
            if pp.search(line):
                fighits += 1
                print(f"  CANDIDATE [{decision}] {what}  {loc} (FIGURE TITLE/CODE): "
                      f"{line.strip()[:100]}")
    if not fighits:
        print("  no candidates in figure titles")
    total += fighits

    hits = 0
    for decision, pat, what in WITHDRAWN:
        p = re.compile(pat, re.I)
        for loc, line in rendered:
            if p.search(line) and not PROHIBITION.search(line):
                hits += 1
                print(f"  CANDIDATE [{decision}] {what}  {loc} (RENDERED TEXT): "
                      f"{line.strip()[:100]}")
    ncom = sum(1 for d, pat, _ in WITHDRAWN for loc, l in commented if re.search(pat, l, re.I))
    print(f"  {hits} candidate(s) in RENDERED draft text; {ncom} further match(es) in LaTeX "
          f"COMMENTS (not rendered, listed for the record only)")
    if not hits:
        print("  no candidates in rendered draft text")
    total += hits

    print(f"\n{total} CANDIDATE(S). Exit 1 means candidates exist, NOT that a defect does.")
    print("Read each one: it is a prohibition, a quoted defect, or a finding - or it is real.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
