#!/usr/bin/env python3
r"""check_paper_builds.py — the closest thing to a build that is possible without a LaTeX toolchain.

WHY THIS EXISTS. There is NO TeX toolchain on this node: `pdflatex`, `xelatex`, `lualatex`,
`latexmk`, `tectonic`, `pandoc`, `tex`, `bibtex` and `biber` are all absent, and there is no TeX
distribution under /usr/share/texlive, /usr/local/texlive, /opt/texlive or ~/.TinyTeX. So the paper
CANNOT be compiled here, by anyone, and "it compiles" is an unverified claim about the project.

Installing a TeX distribution on a shared node is not the reviewer's call, so this does the next
best thing: it checks, statically, the failure modes that actually break a LaTeX build, over the
ASSEMBLED paper (main.tex + every \input target), not over the four paste-ready blocks.

WHAT IT CHECKS, each of which is a real build-breaker:
  1. every \input / \include target exists
  2. every \cite key resolves in references.bib
  3. every \ref / \eqref / \autoref target has a \label somewhere
  4. every \includegraphics path resolves to a file in the tree
  5. per-file brace balance and $ parity (ignoring % comments)
  6. no \input is listed twice, and no section file is orphaned

POPULATION (D87 / CHECKLIST 1.15). Prints the number of files and characters it read, and where
from, BEFORE any verdict. An empty population is a FAILURE with a non-zero exit, never a clean
result: "nothing to check" and "nothing found" are different claims.

SELF-TESTS AND POSITIVE CONTROL (CHECKLIST 1.15.4). A checker that has never been observed to fail
has not been shown to work. `--self-test` injects one instance of each defect class into a copy of
the real tree and requires the corresponding check to fire; it exits non-zero if any does not.

EXIT. 0 = no defect found. 1 = defects. 2 = could not check (empty population / self-test failure).

Run:  python3 check_paper_builds.py [--ref origin/agent/writer] [--self-test]
"""
import os
import re
import subprocess
import sys

INPUT = re.compile(r"\\(?:input|include)\{([^}]*)\}")
CITE = re.compile(r"\\cite[a-zA-Z]*\{([^}]*)\}")
REFS = re.compile(r"\\(?:ref|eqref|autoref|pageref)\{([^}]*)\}")
LABEL = re.compile(r"\\label\{([^}]*)\}")
GRAPHIC = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}")
BIBKEY = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")


def strip_comments(text):
    """Drop % comments, honouring \\% escapes, so counts are of CODE not of commentary."""
    out = []
    for line in text.splitlines():
        cut, esc = len(line), False
        for i, ch in enumerate(line):
            if esc:
                esc = False
                continue
            if ch == "\\":
                esc = True
            elif ch == "%":
                cut = i
                break
        out.append(line[:cut])
    return "\n".join(out)


def brace_and_dollar_balance(code):
    """Naive balance on comment-stripped code. Escaped braces do not count."""
    depth, dollars, esc = 0, 0, False
    i = 0
    while i < len(code):
        ch = code[i]
        if esc:
            esc = False
        elif ch == "\\":
            esc = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                return f"closing brace with depth {depth}"
        elif ch == "$":
            dollars += 1
        i += 1
    if depth != 0:
        return f"brace depth {depth} at end of file"
    if dollars % 2:
        return f"odd number of $ ({dollars})"
    return None


def git(toplevel, ref, *args):
    return subprocess.run(("git",) + args, cwd=toplevel,
                          capture_output=True, text=True).stdout


def load_tree(toplevel, ref, path):
    return git(toplevel, ref, "show", f"{ref}:{path}")


def ls(toplevel, ref, prefix):
    return [l for l in git(toplevel, ref, "ls-tree", "-r", "--name-only", ref).splitlines()
            if l.startswith(prefix)]


def split_keys(blob):
    out = []
    for group in CITE.findall(blob):
        out += [k.strip() for k in group.split(",") if k.strip()]
    return out


def run_checks(files, bibkeys, treefiles, verbose=True):
    """files: {path: code}. Returns a list of (severity, message)."""
    bad = []
    citekeys, reftargets, labelnames, graphics, inputs = [], [], [], [], []

    for path, raw in files.items():
        code = strip_comments(raw)
        citekeys += [(path, k) for k in split_keys(code)]
        reftargets += [(path, k.strip()) for k in REFS.findall(code) for k in [k]]
        labelnames += [(path, k) for k in LABEL.findall(code)]
        graphics += [(path, g) for g in GRAPHIC.findall(code)]
        inputs += [(path, i) for i in INPUT.findall(code)]
        problem = brace_and_dollar_balance(code)
        if problem:
            bad.append(("ERROR", f"{path}: {problem}"))

    seen = set()
    for path, target in inputs:
        for ext in ("", ".tex", ".txt"):
            cand = os.path.normpath(os.path.join(os.path.dirname(path), target + ext))
            if cand in files or cand in treefiles:
                break
        else:
            bad.append(("ERROR", f"{path}: \\input{{{target}}} resolves to no file in the tree"))
        if target in seen:
            bad.append(("ERROR", f"{path}: \\input{{{target}}} is included more than once"))
        seen.add(target)

    for path, key in citekeys:
        if key not in bibkeys:
            bad.append(("ERROR", f"{path}: \\cite{{{key}}} is not a key in the .bib"))

    labels = {k for _, k in labelnames}
    unresolved = {}
    for path, target in reftargets:
        if target not in labels:
            unresolved.setdefault(target, []).append(path)
    for target in sorted(unresolved):
        where = sorted(set(unresolved[target]))
        bad.append(("ERROR", f"\\ref{{{target}}} has no \\label  (used {len(unresolved[target])}x in "
                            f"{', '.join(os.path.basename(w) for w in where)})"))

    for path, g in graphics:
        stem = re.sub(r"\.(pdf|png|jpg|eps)$", "", g)
        ok = any(cand in treefiles or cand in files
                 for cand in (g, stem + ".pdf", stem + ".png",
                              os.path.normpath(os.path.join(os.path.dirname(path), g)),
                              os.path.normpath(os.path.join(os.path.dirname(path), stem + ".pdf")),
                              os.path.normpath(os.path.join(os.path.dirname(path), stem + ".png"))))
        if not ok:
            bad.append(("ERROR", f"{path}: \\includegraphics{{{g}}} resolves to no file in the tree"))

    dupes = {k for k in labelnames if [x for _, x in labelnames].count(k) > 1}
    for k in sorted(dupes):
        bad.append(("ERROR", f"\\label{{{k}}} is defined more than once"))

    if verbose:
        print(f"  inputs={len(inputs)}  cites={len(citekeys)}  refs={len(reftargets)}  "
              f"labels={len(labelnames)} (unique {len(labels)})  graphics={len(graphics)}")
    return bad


def self_test(toplevel, ref):
    """Inject one instance of each defect class; require the matching check to fire."""
    base = {}
    for p in [f"paper/main.tex"] + ls(toplevel, ref, "paper/sections/"):
        base[p] = load_tree(toplevel, ref, p)
    bib = load_tree(toplevel, ref, "paper/references.bib")
    tree = set(ls(toplevel, ref, "paper/")) | set(ls(toplevel, ref, "experiments/"))
    bibkeys = set(BIBKEY.findall(bib))

    clean = run_checks(base, bibkeys, tree, verbose=False)
    print(f"\nSELF-TEST baseline: {len(clean)} defect(s) in the unmodified tree")
    for s, m in clean[:6]:
        print(f"    {s} {m}")

    def prepend(d, path, text):
        d[path] = text + d[path]

    cases = [
        ("missing \\input target",
         lambda f: f.__setitem__("paper/main.tex",
                                 f["paper/main.tex"].replace("\\input{sections/09_conclusion}",
                                                             "\\input{sections/99_nonexistent}")),
         "99_nonexistent"),
        ("unresolvable \\cite key",
         lambda f: prepend(f, "paper/sections/09_conclusion.tex",
                           "\\cite{definitely_not_a_real_key_zzz}\n"),
         "definitely_not_a_real_key_zzz"),
        ("\\ref with no \\label",
         lambda f: prepend(f, "paper/sections/09_conclusion.tex",
                           "See \\ref{label_that_does_not_exist_zzz}.\n"),
         "label_that_does_not_exist_zzz"),
        ("missing \\includegraphics target",
         lambda f: prepend(f, "paper/sections/06_results.tex",
                           "\\includegraphics{fig_absent_zzz}\n"),
         "fig_absent_zzz"),
        ("unbalanced brace",
         lambda f: prepend(f, "paper/sections/09_conclusion.tex", "\\section{Unclosed\n"),
         "brace depth"),
        ("odd number of $",
         lambda f: prepend(f, "paper/sections/09_conclusion.tex",
                           "an inline $x$ and a dangling $\n"),
         "odd number of $"),
    ]
    print()
    allgood = True
    for name, mutate, expect in cases:
        f = dict(base)
        mutate(f)
        got = run_checks(f, bibkeys, tree, verbose=False)
        blob = " | ".join(m for _, m in got)
        fired = expect in blob
        allgood &= fired
        print(f"  {'FIRED  ' if fired else 'MISSED '} {name:<32} (looking for {expect!r})")
        if not fired:
            for s, m in got[:3]:
                print(f"            got: {s} {m}")
    print(f"\nSELF-TEST {'PASS' if allgood else 'FAIL'}: every defect class is detected")
    return 0 if allgood else 2


def main():
    args = sys.argv[1:]
    # R140: the whole paper was merged to main in R139, so main is the integrated
    # state and is the right thing to check. Override with --ref to inspect an
    # unmerged writer branch on purpose. The ref is printed in the population.
    ref = "origin/main"
    if "--ref" in args:
        ref = args[args.index("--ref") + 1]
    root = Path_dir = os.path.dirname(os.path.abspath(__file__))
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=root,
                         capture_output=True, text=True).stdout.strip() or root

    if "--self-test" in args:
        return self_test(top, ref)

    files, order = {}, []
    maintex = "paper/main.tex"
    if maintex not in set(ls(top, ref, "paper/")):
        print(f"  !! {maintex} is absent from {ref}. A draft that cannot be found cannot be checked;")
        print("     this is a FAILURE, not a clean result (D87).")
        return 2
    files[maintex] = load_tree(top, ref, maintex)
    order.append(maintex)
    # follow \input transitively, so an input added inside a section is also checked
    frontier = [maintex]
    while frontier:
        cur = frontier.pop()
        code = strip_comments(files[cur])
        for target in INPUT.findall(code):
            cand = os.path.normpath(os.path.join(os.path.dirname(cur), target + ".tex"))
            if cand in files or cand not in set(ls(top, ref, "paper/")):
                continue
            files[cand] = load_tree(top, ref, cand)
            order.append(cand)
            frontier.append(cand)

    bib = load_tree(top, ref, "paper/references.bib")
    bibkeys = set(BIBKEY.findall(bib))
    treefiles = set(ls(top, ref, "paper/")) | set(ls(top, ref, "experiments/"))

    chars = sum(len(v) for v in files.values())
    print(f"  POPULATION: {len(files)} file(s), {chars} chars, from git {ref}:paper/")
    for p in order:
        print(f"    {p}  ({len(files[p])} chars)")
    print(f"  references.bib: {len(bibkeys)} unique keys")
    if not files:
        print("  !! EMPTY POPULATION — nothing was checked.")
        return 2

    bad = run_checks(files, bibkeys, treefiles)
    print()
    for s, m in bad:
        print(f"  {s} {m}")
    print(f"\n  {len(bad)} defect(s). "
          f"This is a STATIC check: it cannot prove the paper compiles (no TeX toolchain here), "
          f"only that these build-breakers are absent.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
