#!/usr/bin/env python3
"""Assemble paper/main.tex + its ten \\input sections into ONE self-contained .tex file.

Why this exists: the draft is a multi-file document, so `main.tex` looks empty and the
paper cannot be read or compiled as one piece. This inlines every section VERBATIM --
no flattening, no rewriting of the prose -- so the output is the real LaTeX and a
reviewer can compile it directly.

The one rewrite is \\includegraphics paths: `\\includegraphics{figures/x}` resolves
against the main document's directory, so once the body is inlined into a file that
lives outside `paper/`, those paths break. They are rewritten to `paper/figures/x`,
which makes the output compile from the repository ROOT:

    pdflatex -output-directory=/tmp state/reviewer/PAPER.tex

GENERATED FILE -- DO NOT EDIT. It is a view of paper/, and it goes stale the moment a
section changes. Regenerate:  python state/reviewer/assemble_tex.py
The paper itself lives in paper/ and is owned by the writer.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "PAPER.tex"

SECTIONS = [
    "00_abstract", "01_introduction", "02_contributions", "03_related_work",
    "04_methods", "05_experimental_setup", "06_results", "07_discussion",
    "08_limitations", "09_conclusion",
]


def sh(*args):
    r = subprocess.run(["git", "show", *args], capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        sys.exit(f"git show {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    main_tex = sh(f"{ref}:paper/main.tex")

    # Split the preamble from the body at \begin{document}, then drop the \input lines.
    m = re.search(r"^\\begin\{document\}", main_tex, re.M)
    if not m:
        sys.exit("no \\begin{document} in main.tex")
    preamble, body = main_tex[: m.start()], main_tex[m.start():]

    inputs = re.findall(r"^\\input\{([^}]*)\}", body, re.M)
    if inputs != [f"sections/{s}" for s in SECTIONS]:
        sys.exit(f"unexpected \\input list: {inputs}")

    banner = [
        "% " + "=" * 74,
        "% GENERATED FILE -- DO NOT EDIT.  A verbatim view of paper/ on " + ref + ".",
        "% Regenerate:  python state/reviewer/assemble_tex.py",
        "% Compile from the repository root:",
        "%     pdflatex -output-directory=/tmp state/reviewer/PAPER.tex",
        "%     (bibtex needs \\bibliography{references} reachable; see check_tex() below)",
        "% The paper lives in paper/ and is owned by the writer. Edit there, not here.",
        "% " + "=" * 74,
        "",
    ]

    chunks = list(banner)
    chunks.append(preamble)
    chunks.append("\\begin{document}\n")
    chunks.append("\\maketitle\n")
    for s in SECTIONS:
        body_s = sh(f"{ref}:paper/sections/{s}.tex")
        if re.search(r"^\\input\{", body_s, re.M):
            sys.exit(f"{s}.tex has a nested \\input; the inliner only handles one level")
        # Resolve graphics against the repo root, not against paper/.
        body_s = re.sub(r"(\\includegraphics(?:\[[^\]]*\])?\{)figures/",
                        r"\1paper/figures/", body_s)
        chunks.append(f"\n% ===== paper/sections/{s}.tex =====\n")
        chunks.append(body_s.rstrip() + "\n")

    tail = re.search(r"^\\bibliographystyle.*?^\\end\{document\}", body, re.M | re.S)
    if not tail:
        sys.exit("no \\bibliographystyle/\\end{document} tail in main.tex")
    tail_s = tail.group(0)
    # Same reason as the graphics: bibtex resolves \bibliography against the main document's
    # directory, and this file does not live in paper/.
    tail_s = re.sub(r"^\\bibliography\{([^}]*)\}", r"\\bibliography{paper/\1}", tail_s, flags=re.M)
    chunks.append("\n" + tail_s + "\n")

    text = "".join(chunks)
    OUT.write_text(text)
    check_tex(text, ref)
    return text


def check_tex(text, ref):
    """Structural checks. This is NOT a LaTeX run -- it cannot prove the file compiles.

    What it can prove: balanced braces and environments, every \\includegraphics target
    present on disk, every \\cite key present in references.bib, every \\ref/\\eqref
    target defined by a \\label, and no \\input left behind.
    """
    ok, bad = [], []

    stripped = re.sub(r"(?<!\\)%[^\n]*", "", text)  # drop comments, as LaTeX does

    for env in ("document", "abstract", "itemize", "enumerate", "figure", "table",
                "equation", "align", "tabular", "equation*", "align*"):
        o = len(re.findall(rf"\\begin\{{{re.escape(env)}\}}", stripped))
        c = len(re.findall(rf"\\end\{{{re.escape(env)}\}}", stripped))
        (ok if o == c else bad).append(f"environment {env}: {o} begin / {c} end")

    depth = 0
    worst = 0
    for ch in re.sub(r"\\[{}]", "", stripped):
        depth += (ch == "{") - (ch == "}")
        worst = min(worst, depth)
    depth += worst
    (ok if depth == 0 else bad).append(f"braces balanced (net depth {depth})")

    leftover = re.findall(r"^\\input\{", stripped, re.M)
    (ok if not leftover else bad).append(f"no \\input left ({len(leftover)} found)")

    # graphics resolve on disk
    figs = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", stripped)
    for f in sorted(set(figs)):
        cands = [ROOT / f, ROOT / (f + ".pdf"), ROOT / (f + ".png")]
        (ok if any(c.exists() for c in cands) else bad).append(f"graphic {f}")
    print(f"  graphics: {len(set(figs))} distinct, {len(figs)} uses")

    # every \ref target defined
    labels = set(re.findall(r"\\label\{([^}]*)\}", stripped))
    refs = set(re.findall(r"\\(?:eq)?ref\{([^}]*)\}", stripped))
    missing = sorted(refs - labels)
    (ok if not missing else bad).append(
        f"cross-references: {len(refs)} targets, {len(labels)} labels, "
        + (f"MISSING {missing}" if missing else "all defined"))

    # every \cite key in the bib
    bib = sh(f"{ref}:paper/references.bib")
    keys = set(re.findall(r"@\w+\{([^,]+),", bib))
    cites = set()
    for grp in re.findall(r"\\cite[tp]?\*?(?:\[[^\]]*\])*\{([^}]*)\}", stripped):
        cites |= {k.strip() for k in grp.split(",") if k.strip()}
    missc = sorted(cites - keys)
    (ok if not missc else bad).append(
        f"citations: {len(cites)} keys cited, {len(keys)} in bib, "
        + (f"MISSING {missc}" if missc else "all defined"))

    markers = len(re.findall(r"PENDING-?CODER", re.sub(r"(?<!\\)%[^\n]*", "", text), re.I))
    allm = len(re.findall(r"PENDING-?CODER", text, re.I))

    for line in bad:
        print(f"  FAIL  {line}")
    for line in ok:
        print(f"  ok    {line}")
    bib_path = re.search(r"^\\bibliography\{([^}]*)\}", text, re.M)
    print(f"  bibliography: \\bibliography{{{bib_path.group(1)}}} -> "
          f"{'found' if (ROOT / bib_path.group(1)).with_suffix('.bib').exists() else 'MISSING'}")
    print(f"  PENDING-CODER in compiled text: {markers}  (of {allm} total, rest are comments)")
    print(f"  wrote {OUT}  ({len(text.split())} words, {text.count(chr(10)) + 1} lines)")
    if bad:
        sys.exit(f"{len(bad)} structural problem(s); the file is NOT clean")


if __name__ == "__main__":
    main()
