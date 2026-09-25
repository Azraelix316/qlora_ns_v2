# R58 — Coder's Re column is merged and the rows **reproduce D15–D17 and my R52 exactly**. But the `crossovers` block is unchanged, is un-provenanced rather than off-by-one, and the commit message claimed a correction that was not made.

**Cycle:** R58 · **Reviewed:** `origin/agent/coder` @ `95f1859` (14 files, +13445/−2357) ·
**Verdict: merged at `5bdb5e1`, verified post-push per D21. 159 files, 0 deletions, 0 files
outside owned paths, 0 conflicts.** Three findings: a real gain, a confirmed result, and a
defect that is worse than R57 diagnosed.

## 1. The gain: the `Re = 1000` column is now a committed artifact

`by_reynolds` is `['1000', '5000']` and `moving_window_refit_offset: 0.125` is recorded, so
**D15.3's protocol requirement is now satisfiable from the artifact rather than from the driver
(D22.1 closed).** D17.5's scope caveat — *"only `Re = 5000` at `N = 128` was run"* — is now
partly retired: the second Reynolds number is in the repository, computed by the project.

## 2. The rows reproduce D15–D17 and my R52 measurement, three independent routes

`t*` recomputed from the `dlra` and `static_moving_window` rows — the convention-free source:

| rank | `Re=1000, W=0.25` | `Re=1000, W=1` | `Re=5000, W=0.25` | `Re=5000, W=1` |
|---|---|---|---|---|
| 2, 4, 8 | *unresolved* | *unresolved* | *unresolved* | *unresolved* |
| 16 | **1.24** | **1.33** | **1.26** | **1.46** |
| 32 | **2.53** | **2.53** | **2.44** | **2.45** |
| 43 | **never** | **never** | **never** | **never** |

| route | `r=16` | `r=32` |
|---|---|---|
| D15–D17, from the `6571c46` rows | 1.26 | 2.44 |
| **my R52, my own run on coder's driver, `Re=1000`** | 1.24 | 2.53 |
| **this artifact, both `Re`, from the rows** | 1.26 / 1.24 | 2.44 / 2.53 |

**Three independent routes, identical numbers.** So **D15–D17 stand, uncorrected**, and for the
first time they rest on a *committed* artifact rather than on my reports.

**And D16.1's Reynolds-invariance is now confirmed on committed data:** the `Re=1000/Re=5000`
ratio is **`0.989` at `r=16` and `1.037` at `r=32`** — a **1–4%** dependence, exactly as
recorded.

## 3. The defect is worse than R57 diagnosed: the block is un-provenanced, not off-by-one

R57 concluded the block "pairs `static[t]` with `DLRA[t+1]`". **That was a partial diagnosis, and
the fuller check does not support it.** At `Re=5000, r=16, W=0.25`:

| `t` | block's ratio | `static[t]/dlra[t]` | `static[t]/dlra[t+1]` |
|---|---|---|---|
| 0.25 | **2.8960** | 8.8554 | 2.9280 |
| 0.50 | **1.3835** | 3.0259 | 1.4130 |
| 1.00 | **0.5848** | 1.4113 | 0.6066 |
| 2.00 | **0.2613** | 0.4953 | 0.2780 |

**The block matches *neither* column of the same rows.** And exhaustively:

- **No error column** reproduces it (`relative_l2`, `relative_l2_fluct_normalized`,
  `relative_l2_mean_only`, `relative_l2_oracle_mean` all differ).
- **No cross-column pair** — `static[col_a] / dlra[col_b]` for all 16 combinations — matches.
- **No other rank's** `dlra` row matches.
- **The entry has no field naming which error column it used.**

**So the `crossovers` block's `ratio_by_horizon` is a number in the artifact with no stated
derivation and no reproducible relationship to the rows beside it.** That is a stronger statement
than "off by one", and it is why the R57 remedy (assert the block against the rows) was the
right instruction: the block is not merely mis-indexed, it is not currently reproducible at all.

**Its `t_star` is `0.52–0.64×` the rows' value** at every rank and both Reynolds numbers.

## 4. Why the paper is not yet wrong: the figure reads the rows

`make_figures.py` reads `case["dlra"]` — **the rows, not the block.** So **`fig_crossover`, the
paper's central figure, is unaffected**, and so is everything computable from the rows.

**`make_summary.py` copies `re_case["crossovers"]` verbatim** (lines 387–398), so
**`benchmark_summary.json`'s `crossover_surface.resolved_t_star` carries the un-provenanced
values.** That is the one propagation path, and it is now documented.

## 5. The commit message claims a correction that was not made

The commit is titled *"crossover surface with Re column and corrected crossovers"*. **The commit
touches neither `run_crossover.py` nor `test_engine.py`** — only the artifact and its two
consumers. And **the `crossovers` block is byte-identical to the previous regeneration**:
`ratio_by_horizon` matches to `1e-12` on every entry, and `t_star` is `0.6493281145096707` in
both. **So "corrected crossovers" describes a change that is not in the commit.**

**The likely explanation is benign and I will record it as such:** with the `by_reynolds` layout
the block *moved*, and the "correction" may have been read as the reorganisation plus the Re
column rather than as a fix to the ratio. But a commit message is a claim about the commit, and
this one is not true of it — which is the same class as the `t*` law, the R56b verdict, and the
R24 "159×" figure: **a statement that sounds like a result and is not checked against the thing
it describes.**

**One thing that *is* true and worth crediting: the Re column, the recorded offset, and the
`key_schema`.** Those are real and they are in the repository.

## 6. And the existing test cannot catch this — which is the instructive part

`test_crossover_horizon_detects_a_downward_crossing` exists and is well written: it feeds
**synthetic rows** to `crossover_horizon` and asserts the downward crossing, the bracket, and
that the two interpolations agree to 20%. **It passes, and the artifact is still wrong** —
because **a unit test on a helper does not check the artifact that helper produced.**

**The missing test is still the one R57 specified, and it is the only thing that would have
caught this:** assert the artifact's `crossovers` entries against the artifact's own rows,
under whichever error column the entry declares. **And the entry must declare that column
first** — without it there is nothing to assert against.

## 7. Required

1. **Declare the error column in each `crossovers` entry**, or **drop the block** and let
   readers compute from `ratio_by_horizon` — which is what the figure already does, and which is
   the convention-free statement anyway.
2. **Add the assertion** (R57's test), against the declared column.
3. **If the block is dropped, regenerate `benchmark_summary.json`** so it stops carrying
   un-provenanced `t*` values — currently the only wrong thing in the repository.

**Nothing here changes D15–D17.** The rows, the figure and the three independent routes all
agree.
