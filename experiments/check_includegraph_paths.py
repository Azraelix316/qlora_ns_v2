"""Which directory does ``\\includegraphics`` resolve against? Both models, run.

`state/reviewer/check_paper_builds.py` resolves an ``\\includegraphics`` target
against **the file that contains it**, so ``{figures/fig_cost}`` inside
``paper/sections/06_results.tex`` is looked for at
``paper/sections/figures/fig_cost.pdf``.  LaTeX does not do that.  It resolves
graphics against the directory of the **main document** plus any
``\\graphicspath`` entries; ``\\input`` does not change that directory.  Since
``paper/main.tex`` does ``\\input{sections/06_results}``, the correct location is
``paper/figures/fig_cost.pdf`` -- which is where the figures are generated.

This was left as an argument, and an argument is what this project keeps losing
to a measurement.  So here both models are *run* over the real draft and the
actual generated files, and the disagreement is printed as a count.  Nothing is
asserted about which model is right -- that is the reviewer's decision -- only
about which one finds the files that exist.

    python experiments/check_includegraph_paths.py [--draft-ref origin/agent/writer]

The draft is read from a git ref, not from the working tree, for the reason the
other gates give: the reviewer's copy of the paper is what everyone sees, and a
check that described a draft nobody else has would be a result with no
provenance in the shared state.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPHIC = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}")
EXTS = (".pdf", ".png", ".jpg", ".jpeg", ".eps")


def _sh(*args: str) -> str:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True).stdout


def draft_texts(ref: str) -> dict[str, str]:
    names = [
        n for n in _sh("git", "ls-tree", "-r", "--name-only", ref, "--", "paper").splitlines()
        if n.endswith(".tex")
    ]
    if not names:
        raise SystemExit(f"no .tex under paper/ at {ref}")
    return {n: _sh("git", "show", f"{ref}:{n}") for n in names}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft-ref", default="origin/agent/writer")
    args = parser.parse_args()

    texts = draft_texts(args.draft_ref)
    main_tex = next((p for p in texts if p.endswith("paper/main.tex")), None)
    if main_tex is None:
        raise SystemExit("no paper/main.tex in the draft; cannot locate the main document")
    doc_dir = os.path.dirname(main_tex)

    # Does the draft set \graphicspath?  If it did, the search list would be
    # wider and the comparison below would need to include it.
    graphicspath = [ln.strip() for t in texts.values() for ln in t.splitlines()
                    if "\\graphicspath" in ln]
    standalone = [p for p, t in texts.items() if "\\documentclass" in t and p != main_tex]

    inc = []
    for path, text in sorted(texts.items()):
        for m in GRAPHIC.finditer(text):
            inc.append((path, m.group(1)))

    by_including, by_document = 0, 0
    unresolved_doc, unresolved_inc = [], []
    for path, target in inc:
        stem = os.path.splitext(target)[0]
        if any(os.path.exists(os.path.join(os.path.dirname(path), stem + e))
               for e in EXTS):
            by_including += 1
        else:
            unresolved_inc.append(f"{path}: {target}")
        if any(os.path.exists(os.path.join(doc_dir, stem + e)) for e in EXTS):
            by_document += 1
        else:
            unresolved_doc.append(f"{path}: {target}")

    print("INCLUDEGRAPH RESOLUTION — both models, run over the real draft\n")
    print(f"  draft ref        : {args.draft_ref}")
    print(f"  main document    : {main_tex}  (graphics resolve against its directory)")
    print(f"  \\includegraphics : {len(inc)} across {len(texts)} .tex file(s)")
    print(f"  \\graphicspath    : {graphicspath or 'NOT SET — the search list is the document directory alone'}")
    print(f"  standalone docs  : {standalone or 'none — every section is \\input into the main document'}")
    print()
    print(f"  resolved against the INCLUDING file   (paper/sections/...): "
          f"{by_including}/{len(inc)}")
    print(f"  resolved against the MAIN DOCUMENT    (paper/...):           "
          f"{by_document}/{len(inc)}")
    print()
    if by_including == by_document == len(inc):
        print("  the two models agree here; nothing to decide")
        return 0
    print("  The models DISAGREE, so one of them is wrong about this tree:")
    if by_document == len(inc) and by_including < len(inc):
        print("    the main-document model finds every target, the including-file")
        print("    model does not. Under LaTeX, \\input does not move the graphics")
        print("    search path -- only \\graphicspath does, and it is not set -- so")
        print("    the including-file model is the incorrect one for a document")
        print("    assembled with \\input. Unresolvable under it:")
        for line in unresolved_inc:
            print(f"      {line}")
    else:
        print("    NEITHER model resolves everything. Under the main-document model:")
        for line in unresolved_doc:
            print(f"      {line}")
        print("    under the including-file model:")
        for line in unresolved_inc:
            print(f"      {line}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
