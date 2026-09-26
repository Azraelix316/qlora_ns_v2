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
# A 4th element, `window`, makes a pattern match across `window` consecutive lines instead of
# one. It exists for D60, whose defect SPANS TWO LINES: the paper writes
#   "$\max|\grad\cdot u| = O(\varepsilon_{\mathrm{mach}}) \approx 10^{-14}$ at"
#   "every step, for every rank and every Reynolds number"
# so the number and the universal quantifier that makes it a defect are not on the same line.
# D111: a negator in the 34 characters before a match means the phrase DESCRIBES something else
# (a baseline that has "no online rank adaptation") rather than CLAIMING it. Separate from
# PROHIBITION, which suppresses matches inside text already marked withdrawn. A regex cannot do
# this: Python needs a fixed-width lookbehind and the negator list is variable-width.
NEGATOR = re.compile(r"\b(?:no|not|never|without|neither|nor|non)\b", re.I)

def claim_present(row, probe):
    """Does `probe` assert `row`'s withdrawn claim?  ONE definition, used by every scanner.

    D111: this logic was duplicated across the scanning loops, and a fix landed in one copy
    and not the others, so the draft and the order documents disagreed about the same
    sentence. A check whose logic is duplicated cannot be fixed in one place. Three
    conditions, in the order the D60 comment demands:

      1. the claim's pattern matches;
      2. the probe is not already marked withdrawn (PROHIBITION);
      3. if the row carries a negation guard, no negator sits in the 34 characters
         before the match -- "(no online rank adaptation)" DESCRIBES a baseline and is
         true, while the bare phrase CLAIMS a contribution.

    A regex cannot do (3): Python's lookbehind is fixed-width and the negator list is
    not. So it is a windowed test, here, once.
    """
    pattern = row[1]
    window = row[3] if len(row) > 3 else 1
    neg_guard = row[4] if len(row) > 4 else False
    rx = re.compile(pattern, re.I | (re.S if window > 1 else 0))
    m = rx.search(probe)
    if not m or PROHIBITION.search(probe):
        return False
    if neg_guard and NEGATOR.search(probe[max(0, m.start() - 34):m.start()]):
        return False
    return True


WITHDRAWN = [
    ("D29",   r"\b1\.26\b|\b2\.44\b|\b1\.46\b|\b2\.45\b|\b1\.24\b|\b2\.53\b|\b1\.33\b",
     "the pre-D29 t* values"),
    # D111: this was `1\.78|2\.18` -- keyed to two SUPERSEDED NUMBERS, which is the inverse of
    # what it must do. Measured over the draft's 1,284 rendered lines it returned ZERO hits, so
    # for cycles "0 candidates" in this population read as "no defect" when it meant "this gate
    # cannot see the draft's cost claims at all". The draft states the band as $2.1$--$2.7\times$
    # and `2.1` is in no pattern. A pattern keyed to VALUES cannot catch a claim stated with
    # DIFFERENT values -- which is exactly what happened when D52.5 re-derived the minimum from
    # 2.08 to 2.2377 and the draft kept saying 2.1.
    # The claim-keyed form -- a ratio band attributed to the full-grid step -- returns exactly the
    # two real sites (00_abstract.tex, 01_introduction.tex) and nothing else.
    ("D52.5", r"\$\d\.\d\$?\\?--\\?\$?\d\.\d\\times\$?\s*(?:the\s+)?full[-\s]grid",
     "a per-step cost band attributed to the full-grid step (D52.5: 2.2-2.7, floor 1.4)"),

    # D132. THE DRAFT'S ABSTRACT AND CONCLUSION CARRIED THREE MORE CLAIMS THAT D104, D117 AND D122 HAD
    # WITHDRAWN, AND THE SUPPLIED BLOCKS WERE CLEAN ON ALL THREE. The cost band was ALREADY caught --
    # D52.5's entry above fires on the abstract -- so "nobody caught it" was too strong for that one;
    # these two had NO pattern at all, which is the only reason they survived. Keyed to the CLAIM'S
    # TEXT rather than to its numbers, per D95 and D132.5.
    ("D104",  r"static baseline[^.]{0,60}grows by (?:three|3) orders of magnitude",
     "the static baseline growing under refinement (D104: it IMPROVES, 9.93e-09 -> 1.89e-09; none of 36 shared error quantities grows >10x)"),
    # NARROWED AFTER MEASURING THE POPULATION. The first pattern also matched the bare phrase
    # "a quasi-stationary rank", which returned 13 sites of which 3 are CORRECT PROSE:
    # 04_methods.tex:252 and :275 ("with a quasi-stationary rank afterwards") and
    # 08_limitations.tex:76 ("whether the quasi-stationary rank and the statistical quantities...").
    # Neither asserts Re-dependence. **The claim is not the PHRASE; it is the FUNCTION FORM** --
    # r*(Re), or an explicit statement that the rank increases with Re. Keying to the phrase would
    # have shipped a gate firing on 3 correct sites, which is the failure mode D95 exists to prevent.
    ("D122",  r"r\^\*\(\\mathrm\{Re\}\)|r\^\*\{\\mathrm\{Re\}\}|r\^\*\(\\mathrm\{Re\}\)|quasi-stationary rank[^.]{0,80}increases with|r\*\(Re\)",
     "the withdrawn r*(Re) (D122: the rank history is byte-identical across all three Re, sha1 a317f44b850b)"),
    ("D56",   r"1\.46\s*(?:→|->)\s*1\.99|2\.45\s*(?:→|->)\s*6\.04", "the STRUCK N=128 multipliers"),
    # D60.1: the DEFECT is a UNIVERSAL QUANTIFIER over a roundoff number, not the number.
    # "at the level of the 10^-14 roundoff floor" is CORRECT and says so; "~1e-14 at every
    # step, for every rank and every Reynolds number" is the claim D60 withdrew, because the
    # measured spread over finite methods is 462x. So require BOTH the number AND a
    # universal quantifier, within a 2-line window (D95). The old bare-number pattern had
    # produced 11 false positives and was matching the wrong quantity.
    # `any` is DELIBERATELY NOT in the quantifier list (D95): "the largest residual of ANY
    # surviving method is 1.1e-13" is D66's CORRECT population statement, and including `any`
    # flagged it. D60's actual defect used "every" and "all".
    ("D60",   r"(?=.*(?:1e-14|10\^\{-14\}))(?=.*\b(?:every|all|always|universal|global)\b)",
     "a universal bound on |div u| stated as the 1e-14 roundoff level", 2),
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
    # D111: the pattern matched four FIXED WORDINGS, so it both missed the claim and flagged a
    # correct statement. `05_experimental_setup.tex` says a baseline has "(no online rank
    # adaptation)" -- that is TRUE, it describes the baseline, and the old pattern flagged it. A
    # false positive trains a reader to skip the row (D95). The claim form is broader, and the 5th
    # tuple element is a NEGATION GUARD: drop a match whose preceding 34 characters contain a
    # negator. A regex cannot do this -- Python needs a fixed-width lookbehind and the negator
    # list is variable-width -- so the guard is applied in code. Measured on the draft: 2 hits
    # with 1 false positive -> 1 hit, 0 false positives, and the survivor is the real one.
    # `01_introduction.tex:116` ("with adaptive rank") is deliberately NOT matched: the runs did
    # use an adaptive rank criterion, so that describes the method rather than claiming the
    # adaptation is a validated contribution -- the same 3-keep / 7-fix split as D110.
    ("D32.2", r"(?:online|adaptive|in-situ|on-the-fly)\s+rank\s+adap\w*|adapted\s+online|"
              r"rank\s+is\s+adapted",
     "the barred online-adaptive-rank claim (the rank sits at the cap for 92.5-99.2% of a run)",
     1, True),
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
    for row in WITHDRAWN:
        decision, what = row[0], row[2]
        window = row[3] if len(row) > 3 else 1
        for i, line in enumerate(lines):
            if i >= cut and i not in in_latex:
                continue                      # order region, or paste-ready text
            probe = "\n".join(lines[i:i + window])
            if not claim_present(row, probe):
                continue
            kind = "PASTE-READY TEXT" if i in in_latex else "order"
            found.append((decision, what, i + 1, kind, line.strip()[:100]))
    return len(lines), cut, len(latex), found


def draft_lines(root):
    """The DRAFT, read from git (D88). WHY FROM GIT: a filesystem glob silently scans nothing
    when the path is absent, which is exactly how claims_registry.py came to report clean
    results over an empty population (D87).

    D111 CORRECTS A COMMENT THAT HAD BECOME FALSE. This used to assert *"`paper/` does not exist
    on `main` -- the draft lives only on origin/agent/writer"*, which was true when written and
    became false in R139, when the whole draft was merged to `main`. The default ref is now
    `origin/main`, so the gate reads the INTEGRATED state; `DRAFT_REF` points it at a branch on
    purpose. A comment asserting a fact about the repository is a claim, and nothing checks
    comments for truth (D103.6).
    Returns (rendered, commented, source)."""
    import subprocess
    ref = os.environ.get("DRAFT_REF", "origin/main")
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


def self_test():
    """D111 ADDED THIS, AND THE REASON IS THE FINDING.

    `--self-test` was DOCUMENTED in the usage line and SILENTLY IGNORED, so this gate had no
    positive control at all: it could report candidates, but nothing verified that any pattern
    fires on the thing it claims to detect. That is how D52.5's `1\\.78|2\\.18` survived
    cycles while returning ZERO hits on the draft -- a pattern that cannot fail and cannot fire
    looks identical to a pattern that is working.

    Each case below is a hand-built string with a stated expectation. The three that matter most
    are the D111 changes: the negation guard, and the two patterns re-keyed from values to
    claims. `claims_registry.py` ALSO has no self-test, for the same reason and with the same
    risk; it is C10-1.
    """
    by_id = {r[0]: r for r in WITHDRAWN}
    cases = [
        # (row id, probe, must_fire, what the case is)
        ("D52.5", r"a per-step cost $2.1$--$2.7\times$ the full grid with no memory saving", True,
         "the real defect: a cost band attributed to the full grid (the OLD pattern missed this)"),
        ("D52.5", r"the band was $1.78$ or $2.18$ in an earlier measurement", False,
         "the OLD pattern's own values, which are no longer the claim"),
        ("D52.5", r"the cost is 2.24x the reference step", False,
         "a single ratio is not a band"),
        ("D52.5", r"a per-step cost $2.2$--$2.7\times$ the full-grid step", True,
         "the CORRECTED band still fires, so the fix did not blind the pattern"),
        ("D32.2", "the contribution is online rank adaptation, validated in a regime", True,
         "the real defect: the claim, unqualified"),
        ("D32.2", "a static basis (no online rank adaptation), same nonlinear step", False,
         "the FALSE POSITIVE the guard removes: describing a baseline"),
        ("D32.2", "we do not claim online rank adaptation here", False,
         "a negated claim is not a claim"),
        ("D32.2", "with adaptive rank", False,
         "DESCRIPTIVE and correct: the runs did use an adaptive criterion (D111.7)"),
        ("D85", r"above rank $\approx 8$ additional rank buys it nothing measurable", True,
         "an untouched pattern still fires"),
    ]
    print(f"POPULATION: {len(cases)} hand-built strings, {sum(1 for c in cases if c[2])} must-fire "
          f"and {sum(1 for c in cases if not c[2])} must-pass, drawn from "
          f"{len({c[0] for c in cases})} pattern(s).")
    print("  A pattern that can neither fire nor fail is indistinguishable from a working one, so")
    print("  every case states which of the two it is.")
    print()
    fails = 0
    for rid, probe, want, why in cases:
        row = by_id.get(rid)
        if row is None:
            print(f"  MISSING PATTERN {rid}")
            fails += 1
            continue
        got = claim_present(row, probe)
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  [{rid:<6}] fires={str(got):<5} expected={str(want):<5} {why}")
        if not ok:
            fails += 1
    print()
    if fails:
        print(f"FAIL: {fails} case(s) wrong -- the gate cannot be trusted until they pass")
        return 1
    print("PASS: every case behaves as stated, including the negation guard and both re-keyed patterns")
    return 0


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
    # The probe must satisfy D60's CONJUNCTION (a roundoff number AND a universal quantifier),
    # because that conjunction is the defect. A probe carrying only the number would make the
    # self-test fail for the right reason at the wrong time.
    probe = ("the dealiasing ceiling and 1e-14 for every rank and every Reynolds number "
             "and 1.26 and 3-5x slower and 1.46->1.99")
    # the wrapped form must fire too, or the gate is blind to hard-wrapped prose (D78)
    wrapped = "bracketed\n   between 32 and 43"
    if not re.search(dict((r[0], r[1]) for r in WITHDRAWN)["D74"], wrapped, re.I):
        print("SELF-TEST FAILED: the D74 pattern does not fire on the line-wrapped form")
        return 2
    fired = sum(1 for r in WITHDRAWN if re.search(r[1], probe, re.I))
    if fired < 5:
        print(f"SELF-TEST FAILED: only {fired} of {len(WITHDRAWN)} patterns fire on a known-bad string")
        return 2
    print(f"SELF-TEST PASS: {fired}/{len(WITHDRAWN)} patterns fire on a known-bad string")

    # CHECKLIST 1.15.4: every pattern must fire on a known instance of the thing it withdraws.
    # A pattern that has never been observed to fire is a pattern that has not been shown to work.
    for row in WITHDRAWN:
        decision, pat = row[0], row[1]
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

    # POPULATION FIRST, in the same form as the other two gates (D87 / CHECKLIST 1.15). A verdict
    # with no population above it is not a result.
    docs_meta = [scan(d) for d in docs]
    print(f"  POPULATION: {len(docs)} order document(s), "
          f"{sum(m[0] for m in docs_meta)} lines, "
          f"{sum(m[2] for m in docs_meta)} paste-ready latex block(s)")

    total = 0
    for d, (n, cut, nlatex, found) in zip(docs, docs_meta):
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
    for row in WITHDRAWN:
        decision, pat, what = row[0], row[1], row[2]
        window = row[3] if len(row) > 3 else 1
        pp = re.compile(pat, re.I | (re.S if window > 1 else 0))
        fidx = {loc: k for k, (loc, _) in enumerate(fig)}
        for loc, line in fig:
            if pp.search("\n".join(l for _, l in fig[fidx[loc]:fidx[loc] + window])):
                fighits += 1
                print(f"  CANDIDATE [{decision}] {what}  {loc} (FIGURE TITLE/CODE): "
                      f"{line.strip()[:100]}")
    if not fighits:
        print("  no candidates in figure titles")
    total += fighits

    hits = 0
    idx = {loc: k for k, (loc, _) in enumerate(rendered)}   # so a window can look ahead
    for row in WITHDRAWN:
        decision, what = row[0], row[2]
        window = row[3] if len(row) > 3 else 1
        for loc, line in rendered:
            probe = "\n".join(l for _, l in rendered[idx[loc]:idx[loc] + window])
            if claim_present(row, probe):
                hits += 1
                print(f"  CANDIDATE [{decision}] {what}  {loc} (RENDERED TEXT): "
                      f"{line.strip()[:100]}")
    ncom = sum(1 for r in WITHDRAWN for loc, l in commented if re.search(r[1], l, re.I))
    print(f"  {hits} candidate(s) in RENDERED draft text; {ncom} further match(es) in LaTeX "
          f"COMMENTS (not rendered, listed for the record only)")
    if not hits:
        print("  no candidates in rendered draft text")
    total += hits

    print(f"\n{total} CANDIDATE(S). Exit 1 means candidates exist, NOT that a defect does.")
    print("Read each one: it is a prohibition, a quoted defect, or a finding - or it is real.")
    return 1 if total else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    # A CRASH MUST NOT LOOK LIKE A PASS. An unhandled exception propagated out of main() and the
    # interpreter still exited 0, so a gate that had stopped running entirely reported success
    # (D95). Anything unexpected is now a non-zero exit with the reason.
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:                      # noqa: BLE001 - deliberate catch-all
        print(f"  !! THE GATE CRASHED: {type(exc).__name__}: {exc}")
        print("     THIS IS NOT A CLEAN RESULT. A gate that did not run reports nothing.")
        import traceback
        traceback.print_exc()
        sys.exit(3)
