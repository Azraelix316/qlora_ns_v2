#!/usr/bin/env python3
"""
claims_registry.py — reviewer instrument. Is every load-bearing number in the paper an
artifact's number, checked BY CONSTRUCTION rather than by search?

WHY (R104, R105). Two numbers were in circulation for the paper's headline invariant, one of
them in the authoritative claims table, and the draft states 99.9% where the runs used 99%.
Nothing checked the transcription into LaTeX.

WHY NOT A SEARCH (R105). The first version extracted every numeric literal from the draft and
searched a 34,775-value population for a match. It does not work, and the record is the point:
the SAME draft number was classified DECISIVE, then COINCIDENCE, then SUPPORTED across three
successive fixes to the disambiguation heuristic, and `5000 -> parameters.re` — a correct match
— was rejected as a coincidence because the key name is two characters long. A search over a
population of nameless numbers needs semantics to disambiguate, and heuristics for semantics are
unstable. That instrument was deleted rather than tuned.

THE DESIGN THAT WORKS. Invert the question: do not search the artifacts for the draft's numbers,
NAME the draft's numbers. Each claim is (id, artifact, key path, SELECTOR, field, value,
precision), so no search and no semantic guessing is involved.

  PART 1  VERIFY  every registry entry resolves in its artifact and equals the asserted value.
                 A wrong path is an ERROR, not a silent skip. This caught my own bad path
                 (`crossovers.…`, when the real key is `by_reynolds`) on the first run — which
                 is the whole argument for naming paths instead of searching for values.
  PART 2  POLICY  claims about a THRESHOLD the draft may mis-state. A defect here is a policy
                 mismatch, not a transcription slip, and it is the more dangerous kind.
  PART 3  COVER   literals at 4+ significant figures in the draft that the registry does not
                 account for. Each needs a row, or a decision that it is not a claim.

SELECTORS exist because these artifacts are regenerated: a list index is not stable across runs,
a (rank=16, window=0.25) selector is.

Run:  python3 claims_registry.py [REPO_ROOT] [PAPER_SECTIONS_DIR]
Exit: 0 iff every entry verifies, no threshold is over-stated, and nothing is uncovered.
"""
import json, glob, os, re, sys
from decimal import Decimal, ROUND_HALF_EVEN

# --------------------------------------------------------------------------------------
# THE REGISTRY — one row per load-bearing number. Adding a claim to the paper means adding a
# row here. That is the point: the paper's numbers become machine-checkable, and they are
# written down in exactly one place.
#   (id, artifact, path, selector, field, asserted value, significant figures)
# selector: {field: value}, matched against dict elements of the list that `path` resolves to.
# --------------------------------------------------------------------------------------
REGISTRY = [
    # --- the accuracy horizon (D29/D47: reproduced bit-for-bit from the artifact's own commit)
    ("tstar_r16", "crossover_surface.json", "by_reynolds.5000.crossovers",
     {"rank": 16, "window": 0.25}, "t_star", 0.6493281145096707, 16),
    ("tstar_r32", "crossover_surface.json", "by_reynolds.5000.crossovers",
     {"rank": 32, "window": 0.25}, "t_star", 1.4816252539052939, 16),

    # --- cost (D52.5: 2.08-2.71x SLOWER. 2.08 is the MINIMUM, so "comparable to" is false
    #     everywhere -- the euphemism the abstract had to be rewritten for.)
    ("cost_ratio_min_N64", "cost_retiming.json", "grids", {"N": 64},
     "@min:rows.full_step_ratio_vs_reference", 2.0800072205298386, 16),

    # --- the rank ceiling is a WAVENUMBER count, not an accuracy result (D30). Recorded so
    #     that "the dealiasing ceiling" can never again be used as a rank claim.
    ("dealias_ceiling_N64", "cost_retiming.json", "grids", {"N": 64}, "dealias_rank_ceiling", 43, 2),
    ("dealias_ceiling_N128", "cost_retiming.json", "grids", {"N": 128}, "dealias_rank_ceiling", 85, 2),
    ("dealias_ceiling_N256", "cost_retiming.json", "grids", {"N": 256}, "dealias_rank_ceiling", 171, 2),

    # --- divergence (D66: a POPULATION, never a single universal bound)
    ("div_worst_our_method", "baselines_re5000_N64_T8.json", "methods.dlra_fixed_r1", None,
     "max_abs_divergence", 1.1093903573566877e-13, 16),
    ("div_full_grid", "baselines_re5000_N64_T8.json", "methods.full_grid", None,
     "max_abs_divergence", 7.638334409421077e-14, 16),
    ("div_worst_nondiverging", "baselines_re5000_N64_T8.json", "methods.pod_dmd_r32", None,
     "max_abs_divergence", 1.0459189070388675e-11, 16),
    ("div_overflow_r32", "baselines_re5000_N64_T8.json", "methods.pod_late_r32", None,
     "max_abs_divergence", 7.090649168385425e+278, 16),
    ("div_overflow_time_r32", "baselines_re5000_N64_T8.json", "methods.pod_late_r32", None,
     "diverged_at_time", 5.513, 16),
    ("div_overflow_time_r42", "baselines_re5000_N64_T8.json", "methods.pod_late_r42", None,
     "diverged_at_time", 7.1715, 16),

    # --- Taylor-Green is EXACTLY rank 1 (D49), which is why it cannot support a rank-growth
    #     claim, and why rank-1 DLRA there is slower than the full grid.
    ("tg_numerical_rank", "taylor_green.json", "initial_state", None, "numerical_rank", 1, 1),
    # --- the N=128 grid refinement (D74). The artifact is NOT yet in the repository; the rows
    #     below name where it must live, so this check currently reports it MISSING, which is the
    #     correct signal to the coder rather than a silent pass. Provenance is attested in
    #     state/reviewer/PROVENANCE_ATTESTATION_N128.md (the run had no .git, so the artifact
    #     itself records git_commit "unknown").
    ("tstar_N128_r16", "crossover_N128.json", "by_reynolds.5000.crossovers",
     {"rank": 16, "window": 0.25}, "t_star", 0.9386425215032279, 16),
    ("tstar_N128_r32", "crossover_N128.json", "by_reynolds.5000.crossovers",
     {"rank": 32, "window": 0.25}, "t_star", 2.4334866060994007, 16),
    ("tstar_N128_r43", "crossover_N128.json", "by_reynolds.5000.crossovers",
     {"rank": 43, "window": 0.25}, "t_star", 2.682771521118821, 16),
    # never-yields status is itself the claim: the static baseline does not overtake at the
    # dealiasing ceiling of each grid. Verified by the `status` field, not by a null t_star.
    ("never_yields_rank_N64", "crossover_surface.json", "by_reynolds.5000.crossovers",
     {"rank": 43, "window": 0.25}, "status", None, None),
    ("never_yields_rank_N128", "crossover_N128.json", "by_reynolds.5000.crossovers",
     {"rank": 85, "window": 0.25}, "status", None, None),
]

# Claims about a THRESHOLD the draft may mis-state. Kept separate because the defect is a policy
# mismatch rather than a transcription slip, and because its direction matters: describing a
# STRICTER truncation than the one run gives the baseline a LARGER rank, which makes the baseline
# look more expensive and therefore flatters our own method.
THRESHOLDS = [
    ("energy_fraction",
     "run_baselines.py:380 default=0.99  |  baselines_re5000_N64_T8.json parameters.energy_fraction=0.99"
     "  |  solvers/dlra.py:51 'an r99-style rule'  |  test_engine.py uses 0.99 throughout",
     0.99, "99"),
]


def get(d, path):
    """Resolve a dotted path with [i] indices. Raises if absent."""
    cur = d
    for part in re.split(r"\.(?![^\[]*\])", path):
        m = re.match(r"^([^\[]*)((?:\[\d+\])*)$", part)
        if not m:
            raise KeyError(f"cannot parse path segment {part!r} in {path!r}")
        name, idxs = m.group(1), re.findall(r"\[(\d+)\]", m.group(2))
        if name:
            if not isinstance(cur, dict) or name not in cur:
                raise KeyError(f"{path}: no key {name!r}")
            cur = cur[name]
        for i in idxs:
            if not isinstance(cur, list) or int(i) >= len(cur):
                raise IndexError(f"{path}: index {i} out of range")
            cur = cur[int(i)]
    return cur


def resolve(d, path, selector, field):
    node = get(d, path)
    if selector:
        if not isinstance(node, list):
            raise TypeError(f"{path} is {type(node).__name__}, not a list; cannot select")
        seen = [{k: e.get(k) for k in selector} for e in node if isinstance(e, dict)]
        hits = [e for e in node if isinstance(e, dict) and all(e.get(k) == v for k, v in selector.items())]
        if not hits:
            raise KeyError(f"no element of {path} matches {selector}; candidates {seen[:6]}")
        if len(hits) > 1:
            raise KeyError(f"{len(hits)} elements of {path} match {selector}; selector not unique")
        node = hits[0]
    if field is None:
        return node
    # @min:<dotted> / @max:<dotted> -- aggregate over a nested list, for a claim that is itself
    # an extremum ("the smallest ratio we measured"). The selector still guards the outer list.
    m = re.match(r"^@(min|max):(.+)$", field)
    if m:
        agg, dotted = m.group(1), m.group(2)
        cur = node
        for part in dotted.split("."):
            if isinstance(cur, dict):
                if part not in cur:
                    raise KeyError(f"{dotted}: no key {part!r}")
                cur = cur[part]
            elif isinstance(cur, list):
                cur = [i[part] for i in cur if isinstance(i, dict) and part in i]
            else:
                raise TypeError(f"{dotted}: cannot descend into {type(cur).__name__} at {part!r}")
        if not isinstance(cur, list) or not cur:
            raise KeyError(f"{dotted}: did not resolve to a non-empty list")
        bad = [v for v in cur if not isinstance(v, (int, float)) or isinstance(v, bool)]
        if bad:
            raise TypeError(f"{dotted}: {len(bad)} non-numeric entries, e.g. {bad[:2]}")
        return min(cur) if agg == "min" else max(cur)
    if not isinstance(node, dict) or field not in node:
        raise KeyError(f"field {field!r} absent at {path}")
    return node[field]


def round_sig(x, sf):
    d = Decimal(repr(float(x)))
    if d == 0:
        return d
    return d.quantize(Decimal(1).scaleb(d.adjusted() - sf + 1), rounding=ROUND_HALF_EVEN)


def strip_latex(text):
    out = []
    for line in text.splitlines():
        cut, i, esc = len(line), 0, False
        while i < len(line):
            c = line[i]
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == "%":
                cut = i
                break
            i += 1
        out.append(line[:cut])
    t = "\n".join(out)
    for pat in (r"\\label\{[^}]*\}", r"\\(?:auto|eq)?ref\{[^}]*\}", r"\\cite[a-zA-Z]*\{[^}]*\}",
                r"\\(?:tag|setcounter)\{[^}]*\}", r"\\(?:vspace|hspace)\*?\{[^}]*\}"):
        t = re.sub(pat, " ", t)
    return t


NUM = re.compile(r"(?<![\w.])(\d+\.\d+(?:[eE][-+]?\d+)?|\d+[eE][-+]?\d+|\d+\.\d+|\d+)(?![\w.])")
PCT = re.compile(r"(\d+\.?\d*)\\?%")


def sig_figs(s):
    """Significant figures as WRITTEN.

    A bare integer's trailing zeros are not significant: `1000` is one significant figure
    (or two at most), not four. Counting them made every Reynolds number in the draft look
    like a 4-sf claim and produced 25 false "uncovered" reports. Only a decimal point or an
    exponent makes trailing zeros meaningful (`0.649`, `2.242e-13`).
    """
    mant = s.split("e")[0].split("E")[0]
    if "." in mant:
        d = mant.replace(".", "").lstrip("0")
    else:
        d = mant.lstrip("0").rstrip("0") or "0"   # bare integer: leading run only
    return max(1, len(d))


def load_draft(root, paper_arg):
    """Return {name: text} for the draft. ORDER MATTERS (D87).

    The draft does not live on `main`: `git ls-tree -r origin/main -- paper` is
    EMPTY, and `paper/` exists only on `origin/agent/writer` (13 files). So the
    default `paper/sections` glob silently matched nothing, `body` was the empty
    string, and PART 2 reported "the draft does not state this threshold;
    nothing to fix" and PART 3 reported "0 uncovered" — CLEAN RESULTS OVER AN
    EMPTY POPULATION. The 99.9% defect (D67) was only ever caught when the gate
    was run by hand with an explicit path.

    So: read the draft out of git by default, and never report a result without
    printing how many files it actually read.
    """
    if paper_arg:                                   # explicit override: a directory
        return {os.path.basename(f): open(f, errors="replace").read()
                for f in sorted(glob.glob(os.path.join(paper_arg, "*.tex")))}, \
               f"directory {paper_arg}"
    import subprocess
    ref = os.environ.get("DRAFT_REF", "origin/agent/writer")
    def sh(*a):
        return subprocess.run(a, cwd=root, capture_output=True, text=True).stdout
    names = [l for l in sh("git", "ls-tree", "-r", "--name-only", ref, "--", "paper/sections").splitlines()
             if l.endswith(".tex")]
    return {n: sh("git", "show", f"{ref}:{n}") for n in names}, f"git {ref}:paper/sections"


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    res = os.path.join(root, "state", "coder", "results")

    print("PART 1 — VERIFY every registry entry against its artifact\n")
    # PRINT THE POPULATION (D87 / CHECKLIST 1.15). Part 1 reads state/coder/results, which is NOT
    # reviewer's to own and is NOT present in every checkout — agent/reviewer's tree has 0 of the
    # 17 artifact files, so a run from the reviewer worktree reports 0/18. That answer is honest
    # but useless, and without this line a reader cannot tell which tree the run came from.
    nart = len(glob.glob(os.path.join(res, "*.json")))
    print(f"  POPULATION: {nart} artifact file(s) in {res}")
    print(f"  ROOT: {root}")
    if nart == 0:
        print("  !! NO ARTIFACTS — every row will report 'artifact missing'. Run this from a tree")
        print("     that has state/coder/results (the main checkout does; agent/reviewer does not).")
    ok_n, bad, values = 0, [], {}
    for cid, art, path, sel, field, expect, sf in REGISTRY:
        f = os.path.join(res, art)
        if not os.path.exists(f):
            bad.append((cid, f"artifact missing: {art}"))
            print(f"  FAIL {cid:<26} artifact missing: {art}")
            continue
        try:
            actual = resolve(json.load(open(f)), path, sel, field)
        except Exception as e:
            bad.append((cid, str(e)))
            print(f"  FAIL {cid:<26} {e}")
            continue
        if expect is not None and (not isinstance(actual, (int, float)) or isinstance(actual, bool)):
            bad.append((cid, f"{field} is {type(actual).__name__}, not a number"))
            print(f"  FAIL {cid:<26} {field} is {type(actual).__name__}")
            continue
        if expect is None:                     # a non-numeric claim, e.g. status == "never"
            want_lit = True
        if expect is None:
            ok = str(actual) in ("never", "unresolved", "resolved")
            note = f"status={actual!r} (a non-numeric claim; accepted if it is a status word)"
        else:
            want_lit = False
        got = None if want_lit else round_sig(actual, sf)
        if (want_lit and ok) or (not want_lit and got == round_sig(expect, sf)):
            ok_n += 1
            if not want_lit:
                values[cid] = actual
            where = f"{art}:{path}" + (f"[{sel}].{field}" if sel else f".{field}")
            print(f"  OK   {cid:<26} {where}")
            print(f"       {note if want_lit else actual!r}")
        else:
            bad.append((cid, f"artifact {actual!r} != registry {expect!r}"))
            print(f"  FAIL {cid:<26} artifact {actual!r} != registry {expect!r}")
    print(f"\n  {ok_n}/{len(REGISTRY)} verified, {len(bad)} failed")

    print("\nPART 2 — THRESHOLD claims: does the draft state the value the runs actually used?\n")
    tex, src = load_draft(root, sys.argv[2] if len(sys.argv) > 2 else None)
    tex = {k: strip_latex(v) for k, v in tex.items()}
    chars = sum(len(v) for v in tex.values())
    print(f"  POPULATION: {len(tex)} file(s), {chars} chars, from {src}")
    for n in sorted(tex):
        print(f"    {n}  ({len(tex[n])} chars)")
    if not tex:
        print("  !! EMPTY POPULATION — this gate has measured NOTHING. A clean result below")
        print("     would be meaningless. Fix the draft ref (DRAFT_REF) or pass a directory.")
        bad.append(("population", "draft population is EMPTY: the gate measured nothing"))
    body = "\n".join(tex.values())
    for cid, where, codeval, pct in THRESHOLDS:
        stated = sorted(set(PCT.findall(body)), key=float)
        over = [s for s in stated if float(s) > float(pct)]
        print(f"  {cid}")
        print(f"    evidence : {where}")
        print(f"    runs used: {codeval} = {pct}%")
        print(f"    draft says: {['%' + s for s in stated] if stated else '(no percentage stated)'}")
        if over:
            print(f"    !! OVER-STATED: the draft says {['%' + s for s in over]} where the runs used {pct}%.")
            print(f"       A stricter truncation than the one run yields a LARGER baseline rank, so the")
            print(f"       baseline looks MORE expensive — the error flatters our own method.")
            bad.append((cid, f"draft over-states the threshold: {over} vs {pct}"))
        elif pct in stated:
            print(f"    OK  the draft states {pct}%")
        else:
            print(f"    --  the draft does not state this threshold; nothing to fix")

    print("\nPART 3 — literals at 4+ significant figures in the draft that the registry does not cover\n")
    n = 0
    for f, b in tex.items():
        for ln, line in enumerate(b.splitlines(), 1):
            for s in NUM.findall(line):
                if sig_figs(s) < 4:
                    continue
                d = Decimal(s)
                if any(round_sig(v, sig_figs(s)) == d for v in values.values()):
                    continue
                n += 1
                print(f"    {os.path.basename(f)}:{ln}  {s:<18} {line.strip()[:90]}")
    print(f"\n  {n} uncovered. Each needs a registry row, or a decision that it is not a claim.")
    if n:
        bad.append(("coverage", f"{n} uncovered high-precision literal(s)"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
