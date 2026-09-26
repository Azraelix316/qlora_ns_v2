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
from pathlib import Path
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
    # D94: the WINDOW SWEEP was unpinned, so the robustness figure derived from it could be
    # misquoted freely -- and it was, twice: once corrected in D29.4, then repeated in D93.4
    # four hours later as "0.3%" when the measured spread over the three windows is 0.63%.
    # With tstar_r32 pinned at W=0.25 and these two, the 0.63% spread is derivable from three
    # machine-verified numbers. Robustness claims are the ones most likely to be misquoted,
    # because they sound like rounding.
    ("tstar_r32_W0p5", "crossover_surface.json", "by_reynolds.5000.crossovers",
     {"rank": 32, "window": 0.5}, "t_star", 1.4739544217813643, 16),
    ("tstar_r32_W1p0", "crossover_surface.json", "by_reynolds.5000.crossovers",
     {"rank": 32, "window": 1.0}, "t_star", 1.4832176727372877, 16),

    # --- D104: the grid-refinement claim. The `2.2` in the abstract is SOUND and these two rows
    #     are what make it checkable: the reduced integrator's own max-over-run relative L2 error
    #     against the full grid, at the two resolutions. Time-keyed per-t ratios re-derive to
    #     2.181-2.183 across five shared time keys -- a spread of 0.09% -- so `2.2` is stable.
    #     sf=2, not 6: this is a chaotic quantity and a re-run moves it. D91.5's rule -- pin what
    #     the measurement can reproduce, and let the RATIO be the claim rather than the digits.
    ("grid64_dlra_max_l2", "kolmogorov_re5000_N64.json", "dlra", None,
     "max_relative_l2_vs_full", 0.00010108416677874297, 2),
    ("grid128_dlra_max_l2", "kolmogorov_re5000_N128.json", "dlra", None,
     "max_relative_l2_vs_full", 4.6067480921986504e-05, 2),

    # --- cost (D52.5: 2.08-2.71x SLOWER. 2.08 is the MINIMUM, so "comparable to" is false
    #     everywhere -- the euphemism the abstract had to be rewritten for.)
    # D91: this row asserted 16 SIGNIFICANT FIGURES on a quantity whose own recorded within-run
    # spread is 8.7-26.5% and whose REFERENCE varies 16-32% across repeats. A re-run moved it
    # +7.58% -- WITHIN its own recorded noise -- so a 16-s.f. gate reports a defect where the
    # measurement says there is none. The precision is now set FROM the measurement: sf=1.
    # A real regression (the method becoming cheaper than the grid) still fails at sf=1,
    # because 2.24 -> 1.1 crosses the leading digit.
    # D117: the band the PAPER quotes is `2.2-2.7x`, and until now only its LOWER end was pinned --
    # `cost_ratio_min_N64` is an N=64 row, so every `2.7` in the abstract, the contributions, the
    # introduction and the draft was UNPINNED. The band spans N=64..256, so both ends are now
    # aggregated over ALL grids with the @min/@max forms, which is what the paper states.
    # D117: the band the PAPER quotes is `2.2-2.7x`, and until now only its LOWER end was pinned --
    # `cost_ratio_min_N64` is an N=64 row, so every `2.7` in the abstract, the contributions, the
    # introduction and the DRAFT was UNPINNED. The envelope over all six rows of `cost_retiming.json`
    # is 2.2377 (N=64, r=2) .. 2.7405 (N=128, r=64), and the minimum row already pins the lower end
    # because the minimum happens to fall at N=64. So the upper end gets its own row.
    #
    # WHY A SELECTED GRID AND NOT AN ALL-GRIDS AGGREGATE: `@min:`/`@max:` flattens ONE level, so
    # `rows.full_step_ratio_vs_reference` applied to the `grids` list walks into a list of lists and
    # resolves to nothing. The first version of this row used `selector=None` and FAILED with "did not
    # resolve to a non-empty list" -- the aggregate cannot express a two-level path. The envelope is
    # therefore pinned one grid at a time, and the comment above records what the envelope is.
    # D126: the REPLACEMENT for the withdrawn r*(Re), pinned so it can never again be withheld for
    # want of a check. The quantity is (total - fluct)/total -- the zonal share OF THE TOTAL -- and the
    # definition lives in run_kolmogorov.py:_zonal_fraction and in the artifact's own
    # `zonal_fraction_definition` string. D106s four values reproduce to 0.0002 percentage points.
    #
    # THESE ARE RED ON PURPOSE. C7-4s code is merged; its artifacts are not regenerated (0 of 21 carry
    # the key). A row that pins a key fails until the run lands, and fails loudly if it never does. That
    # is the point: in D122.5 I refused to cite this quantity because I could not verify it, having
    # computed the wrong ratio. Pinning it is the durable answer.
    ("zonal_share_energy_Re100_N64", "kolmogorov_re100_N64.json", "dlra", None,
     "zonal_energy_fraction.at_final_step", 0.200891, 4),
    ("zonal_share_energy_Re1000_N64", "kolmogorov_re1000_N64.json", "dlra", None,
     "zonal_energy_fraction.at_final_step", 0.185328, 4),
    ("zonal_share_energy_Re5000_N64", "kolmogorov_re5000_N64.json", "dlra", None,
     "zonal_energy_fraction.at_final_step", 0.183979, 4),
    ("zonal_share_energy_Re5000_N128", "kolmogorov_re5000_N128.json", "dlra", None,
     "zonal_energy_fraction.at_final_step", 0.172832, 4),
    ("cost_ratio_max_N128", "cost_retiming.json", "grids", {"N": 128},
     "@max:rows.full_step_ratio_vs_reference", 2.7404672498718976, 1),
    ("cost_ratio_min_N64", "cost_retiming.json", "grids", {"N": 64},
     "@min:rows.full_step_ratio_vs_reference", 2.237746367620425, 1),
    # I ADDED TWO ROWS PINNING THE NOISE ITSELF AND THEN REMOVED THEM (D91.5). The noise estimate
    # is only reproducible to 11-173% between two runs of the SAME protocol, so a value row
    # for it fails on nearly every re-run: a tripwire, not a gate. The noise belongs in D91,
    # which is where the sf=1 justification lives; the registry keeps the quantities that are
    # stable enough to pin.

    # --- the rank ceiling is a WAVENUMBER count, not an accuracy result (D30). Recorded so
    #     that "the dealiasing ceiling" can never again be used as a rank claim.
    ("dealias_ceiling_N64", "cost_retiming.json", "grids", {"N": 64}, "dealias_rank_ceiling", 43, 2),
    ("dealias_ceiling_N128", "cost_retiming.json", "grids", {"N": 128}, "dealias_rank_ceiling", 85, 2),
    ("dealias_ceiling_N256", "cost_retiming.json", "grids", {"N": 256}, "dealias_rank_ceiling", 171, 2),

    # --- MEMORY (added R126/D89). These were load-bearing in FOUR documents and the registry
    #     asserted NONE of them, which is exactly how D19.4a's numbers went stale through two
    #     regenerations before I found them by reading the coder's message. Now a re-run that
    #     moves them fails here instead.
    #     D89: the SIGN is the claim (no memory saving); these rows pin the digits AND the
    #     resolution flag, because the flag is what changed qualitatively.
    ("mem_noise_floor_mib", "peak_memory.json", ".", None,
     "noise_floor_mib", 0.09765625, 8),
    ("mem_overhead_N64_dlra", "peak_memory.json", "rank_scaling", {"N": 64, "method": "dlra"},
     "overhead_vs_full_grid_mib", 2.37109375, 8),
    ("mem_overhead_N128_dlra", "peak_memory.json", "rank_scaling", {"N": 128, "method": "dlra"},
     "overhead_vs_full_grid_mib", 4.2109375, 8),
    ("mem_overhead_N64_bug", "peak_memory.json", "rank_scaling", {"N": 64, "method": "bug"},
     "overhead_vs_full_grid_mib", 2.17578125, 8),
    ("mem_overhead_N128_bug", "peak_memory.json", "rank_scaling", {"N": 128, "method": "bug"},
     "overhead_vs_full_grid_mib", 3.6328125, 8),
    # A non-numeric claim, asserted because D89's whole point is that it is FALSE: the N=128
    # projected rank-variation is NOT resolved, so neither "flat in rank" nor "grows with rank"
    # is supported there. If a future run resolves it, this row fails and the guidance changes.
    ("mem_rank_resolved_N128_dlra", "peak_memory.json", "rank_scaling", {"N": 128, "method": "dlra"},
     "rank_independence_resolved", None, None),

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
    # D118: `tstar_N128_r43` is WITHDRAWN, not failing. The N=128 re-scope (one window 0.25,
    # final_time 8.0 -> 3.0, ranks {16,32,85} instead of {16,32,43,85}) dropped r=43, so the artifact
    # has no r=43 element and the row could never verify. D74's claim that "at N=128 rank 43 DOES
    # yield, t* = 2.6828" therefore has NO artifact behind it in the new run, and the paper must not
    # make it. D17.2 predicted r=43 would yield at N=128; that prediction is now UNTESTED, not
    # refuted. A row whose subject is not measured is withdrawn with a reason, not left red.
    # D118: the shape is `by_reynolds.5000.crossovers` with a `{"rank": 32, "window": 0.25}`
    # selector, copied from the r=16 row above. My first version used path "by_reynolds" with
    # selector {"re": 5000}, and `by_reynolds` is a DICT, so the selector had nothing to select and
    # the row reported "by_reynolds is dict, not a list; cannot select" -- a FAILURE that named the
    # shape, not the number. `t_star` (6 dp) is pinned, not `t_star_loglog`, because the two differ
    # in precision and the registry should pin what the field actually says.
    ("tstar_N128_r32", "crossover_N128.json", "by_reynolds.5000.crossovers",
     {"rank": 32, "window": 0.25}, "t_star", 2.526112, 1),
        # never-yields status is itself the claim: the static baseline does not overtake at the
    # dealiasing ceiling of each grid. Verified by the `status` field, not by a null t_star.
    ("never_yields_rank_N64", "crossover_surface.json", "by_reynolds.5000.crossovers",
     {"rank": 43, "window": 0.25}, "status", None, None),
    ("never_yields_rank_N128", "crossover_N128.json", "by_reynolds.5000.crossovers",
     {"rank": 85, "window": 0.25}, "status", None, None),


    # --- the ENERGY invariant's TWO keys (D96). The same balance computed with and without the
    #     projection's energy increment. IDENTICAL for the full grid (no projection), 1.1-1.6x apart
    #     for SP-DLRA, and 16-663x apart FOR THE STATIC POD BASELINE -- whose projected-key value
    #     reaches 0.311, i.e. 31% of the energy scale. FOUR names are in circulation for the two
    #     quantities and NEITHER WAS PINNED, so a writer could quote the wrong one and be off by
    #     two orders. D18a quotes the `full_pde` key, which is the correct choice.
    # D99: the worst case is NO LONGER the static baseline. A coder fix removed a 3551x error in
    # the N=128 static POD, so the population ceiling fell 2.2e-3 -> 4.9e-4 and the maximum is
    # now SP-DLRA ITSELF. The old row named the N=128 pod, which is no longer the worst case.
    ("energy_pde_worst", "kolmogorov_re100_N64.json", "dlra", None,
     "max_scaled_pde_energy_residual", 4.932977786977058e-4, 4),
    ("energy_pde_best", "kolmogorov_re5000_N128.json", "full", None,
     "max_scaled_pde_energy_residual", 1.2867783923817304e-4, 4),
    ("energy_pde_dlra_N64", "kolmogorov_re5000_N64.json", "dlra", None,
     "max_scaled_pde_energy_residual", 4.6923135768045965e-4, 4),
    ("energy_full_keys_agree", "kolmogorov_re5000_N64.json", "full", None,
     "max_scaled_projected_energy_residual", 2.5885138556773246e-4, 4),
    ("energy_projected_pod", "kolmogorov_re5000_N64.json", "pod", None,
     "max_scaled_projected_energy_residual", 3.3448867445314806e-2, 4),

    # --- Re=1000 horizons (D97). D18c states them, and until now no row covered them, so PART 4
    #     reported them UNTRACED. They are the Re-invariance claim, so they need a source.
    ("tstar_r16_re1000", "crossover_surface.json", "by_reynolds.1000.crossovers",
     {"rank": 16, "window": 0.25}, "t_star", 0.6665645808117523, 16),
    ("tstar_r32_re1000", "crossover_surface.json", "by_reynolds.1000.crossovers",
     {"rank": 32, "window": 0.25}, "t_star", 1.6094633714766546, 16),
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

    UNTIL R139 the draft did not live on `main`: `git ls-tree -r origin/main --
    paper` was EMPTY and `paper/` existed only on `origin/agent/writer` (13
    files). So the default `paper/sections` glob silently matched nothing, `body`
    was the empty string, and PART 2 reported "the draft does not state this
    threshold; nothing to fix" and PART 3 reported "0 uncovered" — CLEAN RESULTS
    OVER AN EMPTY POPULATION. The 99.9% defect (D67) was only ever caught when
    the gate was run by hand with an explicit path.

    So: read the draft out of git by default, and never report a result without
    printing how many files it actually read.

    R140 CHANGED THE DEFAULT, AND THE REASON IS THE POINT. The whole paper was
    merged to `main` in R139 (13 files, 0 deletions, 0 conflicts, D21-verified),
    so `origin/main` is now the INTEGRATED state and is the right thing to
    check: it is what every other agent sees. Reading `origin/agent/writer`
    instead meant this gate described a paper that `main` did not contain —
    a result with no provenance in the shared state, which is the failure this
    project keeps making (D66, D77, D85, D94, D96). The ref is still printed in
    the population line, and `DRAFT_REF` still overrides it, so an unmerged
    writer branch can still be checked on purpose by naming it.
    """
    if paper_arg:                                   # explicit override: a directory
        return {os.path.basename(f): open(f, errors="replace").read()
                for f in sorted(glob.glob(os.path.join(paper_arg, "*.tex")))}, \
               f"directory {paper_arg}"
    import subprocess
    ref = os.environ.get("DRAFT_REF", "origin/main")
    def sh(*a):
        return subprocess.run(a, cwd=root, capture_output=True, text=True).stdout
    names = [l for l in sh("git", "ls-tree", "-r", "--name-only", ref, "--", "paper/sections").splitlines()
             if l.endswith(".tex")]
    return {n: sh("git", "show", f"{ref}:{n}") for n in names}, f"git {ref}:paper/sections"



# ---------------------------------------------------------------------------------------
# PART 4. Every numeric literal in the text that BECOMES THE PAPER, traced to a registry row.
#
# WHY (D97). Three findings in three cycles -- D85's saturation threshold, D94's window figure
# and D96's energy ceiling -- were all defects in MY OWN documents, and all three were found by
# READING, not by a gate. PART 3 checks the draft only, at 4+ significant figures, and PART 1
# checks artifact -> registry. NOTHING checked registry -> the sentences the writer pastes. So a
# number could be wrong in a paste-ready block and every gate would stay green.
#
# This part closes that direction. For each literal it classifies:
#   MATCH       - equals a registry value at the literal's own precision
#   NEAR-MISS   - within a factor of 2 of a registry value but not equal to it  -> INVESTIGATE
#   UNACCOUNTED - no registry value within 100x                              -> needs a claim
# The near-miss band is the point: it is what would have caught 0.3% (D94) and 4.9e-4 (D96).
# ---------------------------------------------------------------------------------------
NEAR_MISS_FACTOR = 2.0
UNACCOUNTED_FACTOR = 100.0


def _sig_ok(s, lo=2):
    try:
        return sig_figs(s) >= lo
    except Exception:
        return False


def trace_literals(text, values, lo=2, unaccounted_lo=4):
    """Classify every numeric literal in `text` against the registry `values`."""
    out = {"MATCH": [], "UNACCOUNTED": [], "small": []}
    if not values:
        return out
    vlist = [(k, float(v)) for k, v in values.items() if isinstance(v, (int, float))
             and not isinstance(v, bool) and float(v) != 0.0]
    for s in NUM.findall(text):
        try:
            x = float(s)
        except ValueError:
            continue
        if x == 0.0:
            continue
        # A YEAR IN A DATE IS NOT A CLAIM. `2026` was reported UNTRACED in CODER_ORDER and
        # START_HERE, and it is the only kind of 4-significant-figure literal in these documents
        # that can never be a measurement.
        if 1900 <= x <= 2100 and "." not in s and "e" not in s.lower():
            out["small"].append(s)
            continue
        if not _sig_ok(s, lo):
            out["small"].append(s)
            continue
        hit = None
        for k, v in vlist:
            if round_sig(v, sig_figs(s)) == Decimal(s):
                hit = k
                break
        if hit:
            out["MATCH"].append((s, hit))
            continue
        # UNTRACED means UNTRACED: no registry row accounts for this literal. An earlier version
        # added a magnitude guard ("unless it is within 100x of SOME registry value"), and that
        # guard is what stopped the assertion ever firing -- my positive control injected an
        # unaccounted 3.1416 and the gate reported 0 untraced. A literal is either sourced or it
        # is not; how big it is has no bearing on whether it is a claim.
        if sig_figs(s) >= unaccounted_lo:
            best = min(vlist, key=lambda kv: abs(abs(kv[1]) - abs(x)) / max(abs(x), 1e-300))
            out["UNACCOUNTED"].append((s, best[0], abs(x) / abs(best[1])))
        else:
            out["small"].append(s)
    return out


def mismatch_detail(actual, expect, sf, numeric=True):
    """D112.4: the text a value FAIL prints. Extracted so the self-test can drive the bands.

    A FAIL that cannot be diagnosed is a FAIL that gets ignored. `artifact X != registry Y` says
    nothing about whether X moved because the code regressed or because the run was repeated, and
    D112.3 measured that 30 of the 32 numeric rows reject a +10% displacement -- so most failures
    here ARE re-runs. The bands are heuristics anchored on D91.5's recorded 8.7-26.5% within-run and
    11-173% between-run spreads; the registry carries no per-quantity noise figure and inventing one
    would be the error this decision is about. The row's own `sf` is printed with it, so a reader
    can overrule the band.
    """
    if not (numeric
            and isinstance(actual, (int, float)) and not isinstance(actual, bool)
            and isinstance(expect, (int, float)) and not isinstance(expect, bool)):
        return f"artifact {actual!r} != registry {expect!r}"
    rel = abs(float(actual) - float(expect)) / abs(float(expect)) if expect else float("inf")
    pct = rel * 100
    if rel == 0.0:
        # The caller only reaches here on a FAILED comparison, so an identical pair means this
        # function was called on something that is not a failure. Say so rather than banding a
        # 0% difference as "plausibly a re-run", which would be the wrong words for an exact match.
        return (f"artifact {actual!r} == registry {expect!r}  [0% apart]  IDENTICAL -- this is NOT a "
                f"failure; if you are reading this, the comparison that called this is wrong")
    if rel < 0.10:
        band = ("within 10% -- PLAUSIBLY A RE-RUN. D91.5 recorded 8.7-26.5% within-run and "
                "11-173% between-run on a chaotic quantity, so check this row's recorded noise "
                "before calling it a regression")
    elif rel < 1.0:
        band = ("10-100% -- NOT NOISE on any quantity measured in this project; treat as a "
                "regression until shown otherwise")
    else:
        band = ("over 100% -- the value changed by more than its own magnitude; the artifact, the "
                "driver, or the registry row is wrong")
    return (f"artifact {actual!r} != registry {expect!r}  "
            f"[{pct:.4g}% apart, row pinned at sf={sf}]  {band}")


def self_test():
    """D112 ADDED THIS. THE REASON IS THE FINDING, AND IT IS THE SAME ONE AS D111.9.

    `claims_registry.py` had NO self-test, and it is the most load-bearing gate in the
    project: 35 rows covering every number the paper states. D111.9's lesson applies with
    more force here than anywhere else -- **a gate that cannot fail cannot be caught**, and
    this one had never been shown to fail on a wrong value.

    FOUR PROPERTIES, each measured over the real REGISTRY rather than a fixture:

      1. NO ROW IS VACUOUS. Perturbing every asserted value by +50% must make the
         comparison reject it. This also VERIFIES D91.5's own stated justification for
         pinning the cost ratio at sf=1 -- "a real regression still fails at sf=1, because
         2.24 -> 1.1 crosses the leading digit" -- a claim that had been asserted in a
         comment and never tested on any row.
      2. THE TRIPWIRE POPULATION, MEASURED. A registry row that fails on a value which
         merely MOVED is a tripwire, not a gate. So: perturb every value by +10% -- a
         plausible re-run displacement, against D91.5's recorded 8.7-26.5% within-run and
         11-173% between-run spreads -- and count the rows that reject it. **A row that
         cannot tell a regression from a re-run is not reporting a diagnosis, and the
         registry's FAIL message does not distinguish them.**
      3. THE RESOLVER'S THREE GUARDS. A missing path, a selector matching nothing, and a
         selector matching MORE THAN ONE must each raise. A resolver that silently picks
         the first of several matches would verify a row against the wrong element, and
         every such row would read OK.
      4. round_sig's BOUNDARIES, including the trailing-zero trap D91.5's `sig_figs`
         docstring calls out (`1000` is one significant figure, not four).

    Usage:  claims_registry.py --self-test
    """
    from decimal import Decimal

    def accepts(actual, expect, sf):
        """Does the registry ACCEPT `actual` for a row asserting `expect` at `sf`?

        The registry's own comparison, from main(): round_sig(actual, sf) ==
        round_sig(expect, sf). A non-numeric claim (expect is None) is accepted on status
        words instead, so it is excluded from the numeric properties by construction.

        D112 NOTE: this helper was first written as `rejects` and RETURNED TRUE WHEN THE TWO
        VALUES ARE EQUAL -- that is, it answered "does the row accept this?" under a name
        that said the opposite, and every population it printed was inverted. It was caught
        by reading the output against the arithmetic, not by the test. The name now matches
        the return value, and the two conditions below were checked against it."""
        return round_sig(actual, sf) == round_sig(expect, sf)

    rows = REGISTRY
    numeric = [r for r in rows if r[5] is not None and r[6]]
    nonnum = [r for r in rows if r[5] is None]
    print(f"POPULATION: {len(rows)} registry row(s) -- {len(numeric)} numeric, "
          f"{len(nonnum)} non-numeric claim(s).")
    print("  Read from the real REGISTRY, so this measures the rows the gate actually uses.")
    sf_hist = {}
    for r in numeric:
        sf_hist[r[6]] = sf_hist.get(r[6], 0) + 1
    print(f"  significant figures requested: {dict(sorted(sf_hist.items()))}")
    print()
    fails = 0

    # --- 1. no row is vacuous
    print("  PROPERTY 1 -- no row is vacuous: a +50% error must be rejected by every row")
    vacuous = []
    for cid, art, path, sel, field, expect, sf in numeric:
        bumped = float(expect) * 1.5
        if accepts(bumped, expect, sf):          # accepts a 50% error -> the row is vacuous
            vacuous.append((cid, sf, expect, bumped))
    if vacuous:
        for cid, sf, e, b in vacuous:
            print(f"    VACUOUS  {cid:<26} sf={sf}  {e} vs {b} -- the row ACCEPTS a 50% error")
        fails += len(vacuous)
    else:
        print(f"    ok  all {len(numeric)} numeric rows reject a +50% error")
        print("        (this is the property D91.5 asserted for sf=1 and never tested on any row)")
    print()

    # --- 2. the tripwire population, measured
    print("  PROPERTY 2 -- the TRIPWIRE POPULATION: rows that reject a +10% displacement,")
    print("  which is a plausible re-run movement (D91.5 recorded 8.7-26.5% within-run and")
    print("  11-173% between-run on the cost quantity). These rows cannot distinguish a")
    print("  regression from a re-run, and the FAIL message does not say which it is.")
    for pct in (0.10, 0.01):
        tripped, tolerant = [], []
        for r in numeric:
            (tolerant if accepts(float(r[5]) * (1 + pct), r[5], r[6]) else tripped).append(r[0])
        print(f"    +{int(pct*100):>2}% displacement: {len(tripped):>2}/{len(numeric)} rows REJECT it"
              f"  ({100*len(tripped)/len(numeric):.0f}%), {len(tolerant)} tolerate it")
        if pct == 0.10:
            sfs = {}
            for r in numeric:
                if r[0] in tripped:
                    sfs[r[6]] = sfs.get(r[6], 0) + 1
            print(f"        the {len(tripped)} that reject it, by requested sf: {dict(sorted(sfs.items()))}")
            print(f"        the {len(tolerant)} that TOLERATE it: {tolerant}")
    print()

    # --- 3. the resolver's guards
    print("  PROPERTY 3 -- resolve() must raise rather than silently pick one of several")
    guard_cases = [
        ("missing path", ({"a": 1}, "nope", None, "f")),
        ("selector matches nothing", ({"rows": [{"N": 64}, {"N": 128}]}, "rows", {"N": 999}, "f")),
        ("selector matches TWO", ({"rows": [{"N": 64}, {"N": 64}]}, "rows", {"N": 64}, "f")),
    ]
    for name, args in guard_cases:
        try:
            resolve(*args)
            print(f"    FAIL  {name:<28} returned a value -- a resolver that picks the first of")
            print("          several would verify rows against the WRONG element and read OK")
            fails += 1
        except Exception as exc:                      # noqa: BLE001 - the point is that it raises
            print(f"    ok    {name:<28} raises {type(exc).__name__}: {str(exc)[:52]}")
    print()

    # --- 4. round_sig boundaries, including the trailing-zero trap
    print("  PROPERTY 4 -- round_sig() boundaries, including the trailing-zero trap")
    sig_cases = [
        (2.237746367620425, 1, Decimal("2"), "D91.5's cost row at sf=1: one leading digit"),
        (0.6493281145096707, 16, Decimal("0.6493281145096707"), "a 16-s.f. row keeps everything"),
        (20.0891, 4, Decimal("20.09"), "4 s.f. of 20.0891"),
        (0.000101084, 2, Decimal("0.00010"), "2 s.f. of a small value: trailing zeros ARE significant here"),
    ]
    for val, sf, want, why in sig_cases:
        got = round_sig(val, sf)
        ok = got == want
        print(f"    {'ok  ' if ok else 'FAIL'}  round_sig({val!r}, {sf}) = {got!r}"
              f"{'' if ok else f'  expected {want!r}'}   {why}")
        if not ok:
            fails += 1
    bare = sig_figs("1000")
    ok = bare == 1
    print(f"    {'ok  ' if ok else 'FAIL'}  sig_figs('1000') = {bare}"
          f"{'' if ok else '  expected 1'}   a bare integer's trailing zeros are not significant")
    if not ok:
        fails += 1
    # --- 5. the FAIL diagnostic's bands (D112.4)
    print()
    print("  PROPERTY 5 -- the FAIL diagnostic must CLASSIFY, not merely report a difference")
    band_cases = [
        (0.6493281145096707, 0.6493281145096707 * 1.05, "within 10%", "a 5% move reads as a re-run"),
        (0.6493281145096707, 0.6493281145096707 * 1.5, "10-100%", "a 50% move reads as a regression"),
        # the denominator is the REGISTRY value, so a 3x artifact is 200% apart -- the first
        # version of this case had the arguments the wrong way round and read 66.7%, which is
        # the 10-100% band. The banding is right; the fixture was wrong.
        (0.6493281145096707 * 3.0, 0.6493281145096707, "over 100%", "a 3x artifact reads as a wrong artifact"),
        (0.6493281145096707, 0.6493281145096707, "IDENTICAL", "an exact match must not be banded as a re-run"),
        (0.6493281145096707, 0.6493281145096707 * 0.95, "within 10%", "the band is two-sided"),
    ]
    for actual, expect, want, why in band_cases:
        detail = mismatch_detail(actual, expect, 16)
        ok = want in detail
        print(f"    {'ok  ' if ok else 'FAIL'}  {actual:.6g} vs {expect:.6g} -> "
              f"{'banded' if want != '== registry' else 'unbanded':<8} {why}")
        if not ok:
            fails += 1
    # a non-numeric claim must not be banded: it has no magnitude to band
    d = mismatch_detail("never", "never", None, numeric=False)
    ok = "band" not in d and "!=" in d
    print(f"    {'ok  ' if ok else 'FAIL'}  a non-numeric claim prints no band"
          f"{'' if ok else ' -- it has no magnitude to band'}")
    if not ok:
        fails += 1
    print()
    if fails:
        print(f"FAIL: {fails} case(s) wrong -- the registry cannot be trusted until they pass")
        return 1
    print("PASS: 5 properties. (1) no row is vacuous; (2) the tripwire population is measured and")
    print("      reported; (3) resolve() raises on all three ambiguity cases; (4) round_sig's boundaries")
    print("      hold; (5) the FAIL diagnostic classifies rather than merely reporting a difference.")
    print("      NOTE: a large tripwire population is REPORTED, not failed -- whether that is")
    print("      acceptable is a judgement about what the registry is for, recorded in D112.3.")
    return 0


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
        if expect is None and isinstance(actual, bool):
            # A BOOLEAN CLAIM (D89). The claim asserted is that the flag is FALSE --
            # e.g. peak_memory rank_independence_resolved at N=128 for the projected
            # integrator. Accepted only when it really is False; a future run that
            # resolves it fails this row, and the guidance that depends on it changes.
            ok = (actual is False)
            note = (f"{field}={actual!r} (asserted False; a run that RESOLVES it must fail "
                    f"this row and the rank-independence guidance must be revisited)")
        elif expect is None:
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
            # D112.4: a FAIL that cannot be diagnosed is a FAIL that gets ignored. `artifact X !=
            # registry Y` does not say whether X moved because the code regressed or because the run
            # was repeated -- and D91.5 MEASURED that the cost quantity moves 8.7-26.5% within a run
            # and 11-173% between runs of the same protocol, while D112.3 measured that 30 of these
            # 32 numeric rows REJECT a +10% displacement. So the difference is printed, and banded
            # against that recorded spread, so a reader can classify it without leaving the output.
            #
            # THE BANDS ARE HEURISTICS ANCHORED ON D91.5's RECORDED SPREADS, NOT PER-QUANTITY NOISE.
            # The registry carries no per-quantity noise figure and inventing one would be the error
            # this decision is about. What it does carry is each row's `sf` -- the tolerance the row
            # itself declares -- so that is printed too, and the two together let a reader overrule
            # the band.
            detail = mismatch_detail(actual, expect, sf, numeric=not want_lit)
            bad.append((cid, detail))
            print(f"  FAIL {cid:<26} {detail}")
            if not want_lit:
                print(f"       {art}:{path}" + (f"[{sel}].{field}" if sel else f".{field}"))
    print(f"\n  {ok_n}/{len(REGISTRY)} verified, {len(bad)} failed")
    if bad:
        print("  A failure above is NOT by itself a regression: compare the percentage against that")
        print("  quantity's recorded noise (D91.5) before acting on it. Rows pinned at many")
        print("  significant figures are tripwires BY CONSTRUCTION -- 30 of the 32 numeric rows reject")
        print("  a +10% displacement (D112.3) -- so most failures here are re-runs, not defects.")

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

    # ---------------------------------------------------------------------------------
    # PART 4 (D97). The same traceability question asked of the text that BECOMES THE
    # PAPER: the draft AND the reviewer's own paste-ready LaTeX blocks. PART 3 asks only
    # "is this literal in the registry?"; PART 4 also asks "is it CLOSE to a registry value
    # without being it?", which is the band that hides a stale number.
    print("\nPART 4 — every numeric literal in the paper-facing text, traced to a registry row\n")
    root_dir = Path(__file__).resolve().parent
    pops = [("DRAFT", "\n".join(tex.values()))]
    for name in ("WRITER_ORDER.md", "CODER_ORDER.md", "START_HERE.md"):
        f = root_dir / name
        if not f.exists():
            continue
        body = f.read_text()
        blocks = re.findall(r"```latex\n(.*?)\n```", body, re.S)
        if blocks:
            # the paste-ready blocks: what the writer actually pastes
            pops.append((f"{name} paste-ready latex ({len(blocks)} blocks)",
                         "\n".join(blocks)))
        else:
            # No paste-ready block, but the prose still carries numbers an agent will copy --
            # START_HERE.md is the file every agent opens first. Scanning it is a strictly larger
            # population, and measured it contributes 11 and 54 traced literals with none untraced.
            pops.append((f"{name} prose (no paste-ready block)", body))
    tot = {"MATCH": 0, "UNACCOUNTED": 0}
    empty = []
    for label, body in pops:
        if not body.strip():
            empty.append(label)
    for label, body in pops:
        if not body.strip():
            continue
        r = trace_literals(body, values)
        tot["MATCH"] += len(r["MATCH"])
        tot["UNACCOUNTED"] += len(r["UNACCOUNTED"])
        print(f"  {label}")
        print(f"    traced to a registry row: {len(r['MATCH'])}   "
              f"UNTRACED at 4+ sig figs: {len(r['UNACCOUNTED'])}")
        for s, key, f_ in r["UNACCOUNTED"][:12]:
            print(f"      UNTRACED  {s:<16} nearest registry value {key} at {f_:.4g}x  -> needs a row")
    if empty:
        print(f"  !! EMPTY POPULATION for: {empty} -- those contributed nothing and the count above")
        print("     does not cover them. A clean total over a missing population is not a result (D87).")
        bad.append(("part4_population", f"empty population(s): {empty}"))
    if tot["MATCH"] == 0 and tot["UNACCOUNTED"] == 0:
        print("  !! NOTHING WAS TRACED AT ALL -- the registry is empty or the text is empty.")
        bad.append(("part4_population", "traced 0 and untraced 0"))
    print(f"\n  TOTAL  traced {tot['MATCH']}   UNTRACED {tot['UNACCOUNTED']}")
    print("  A number in the paper-facing text that no registry row accounts for is a claim with no")
    print("  source. The assertion is UNTRACED == 0, and it is the direction this gate closes: PART 1")
    print("  checks artifact -> registry, and this checks registry -> the sentences that get pasted.")
    print("\n  NOT CHECKED HERE, AND DELIBERATELY SO: a *near-miss* band. Measured, it fires 85 times on")
    print("  the current documents - 13 in the draft, 72 in the paste-ready blocks - and almost all of")
    print("  them are labels, not claims: `32` is a RANK, flagged as 0.744x the dealiasing ceiling 43,")
    print("  and `64` is a GRID. It cannot tell that from '0.3% should be 0.63%', which needs a")
    print("  semantics engine this does not have. **A gate that fires 85 times on correct text trains a")
    print("  reviewer to skip it, which is how D85's threshold and D94's window figure survived as long")
    print("  as they did. So the band is dropped and the measurement is recorded instead (D97).**")
    if tot["UNACCOUNTED"]:
        bad.append(("part4_untraced", f"{tot['UNACCOUNTED']} untraced literal(s) in paper-facing text"))
    return 1 if bad else 0


if __name__ == "__main__":
    # D112: this gate had no positive control at all, and it is the most load-bearing gate
    # in the project -- 35 rows covering every number the paper states. A gate that cannot
    # fail cannot be caught (D111.9).
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    sys.exit(main())
