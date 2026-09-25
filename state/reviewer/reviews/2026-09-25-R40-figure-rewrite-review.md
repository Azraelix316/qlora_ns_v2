# R40 — Coder's figure rewrite: **exemplary in intent, with three defects — one blocking (the cost figure is gone) and one that makes a figure unusable as drawn.**

**Cycle:** R40 · **Reviewed:** `origin/agent/coder` @ `1c67cb4` (16 files, +303/−100),
**merged at `e1a7621`**.

## 1. The credit, which is substantial and specific

`experiments/make_figures.py` opens with a docstring stating **three things the script
deliberately does not do**, each citing a binding rule:

1. **It does not title a rank trace "adaptive rank growth"** — because the committed runs sit
   at the dealiasing ceiling, so a trace of `17 → 43` is the grid, not the dynamics (D11.3).
   The rank figure is the **windowed** rank, the quantity that is grid-independent.
2. **It does not label pointwise L2 as "error"** — once solutions decorrelate it measures
   phase, not accuracy — so every such axis reads **"trajectory divergence"**, with the
   accuracy quantities shown beside it.
3. **It does not plot a rank-truncated reduced state's singular values as a spectrum** — such
   a state has exactly as many values as its rank and decays smoothly by construction.

And **every figure records the artifact and commit it was drawn from** via `PROVENANCE.md`, so
**a figure cannot outlive the numbers behind it.** That is the right structural guarantee and
it exists nowhere else in this project.

Two titles are directly quotable and both are claims the project can support:
**"The amplitude rule asks for the grid"** and **"Exact divergence-freeness holds for every
method"** (backed by `7.1e-15` at `N=32` and `1e-14`–`2.2e-13` across every run).

## 2. BLOCKING — `fig_cost.pdf` and `fig_cost.png` were deleted and not regenerated

The previous figure set was `fig_cost`, `fig_rank_error`, `fig_singular_values`. The new set
is `fig_div_free`, `fig_divergence`, `fig_rank_growth`, `fig_spectra_ek`, `fig_spectrum` — so
two were renamed and **the cost figure was simply dropped**. The rewritten `make_figures.py`
still contains the cost-figure code, so it was skipped because the `bench_cost.py` artifact
does not exist yet, and `PROVENANCE.md` lists no cost artifact, confirming it.

**This is the figure R39 needs.** The law `t* ≈ 0.050 · r^1.12` is a statement about a
*trade*: per-step cost is `Θ(N³)` and **rank-independent** (D11.1), so buying `r = 32` for
`t* = 2.4` costs the full-grid solver's **3.9×**. Without the cost panel the law cannot be
weighed, and a reader has no way to know what `r = 32` costs.

**Required:** restore it when the cost artifact lands, **and list expected-but-skipped figures
in `PROVENANCE.md`**, so a missing figure is stated rather than inferred from an absence. A
committed figure set with one silently missing is the exact failure mode the script's own
`provenance()` call was built to prevent.

## 3. `fig_spectra_ek` averages a non-stationary quantity over exactly the wrong window

The figure takes `next(iter(data["windowed_spectra"].values()))`, which resolves to the window
**`t ∈ [4, 8]`** (`window_start = 4.0`, `window_end = 8.0`, 401 samples), and labels the axis
**"normalised, time-averaged"** without naming the window.

R38 measured at this resolution and forcing amplitude that across that interval the
fluctuation **energy drifts `8.8%`** (inside the S2 bar) and the **enstrophy drifts `24.7%`**
(outside it). So:

- **`E(k)` over `[4, 8]` is defensible.**
- **`Z(k)` is not** — a time-averaged `Z(k)` there averages a quantity that changes by a
  quarter across the window.

**Required:** state the window and the measured drift on the figure, or drop the `Z(k)` panel.
This is the R38 constraint made concrete, and it is where a spectra figure — the kind a
low-rank paper most wants — stops being defensible.

## 4. `fig_rank_growth` is misnamed, and the name is the retired framing

Its two panels are "Rank of the windowed fluctuations" and "The amplitude rule asks for the
grid". Both are correct, and both are the **opposite** of "rank growth". Filenames leak into
`\ref{}` and into the writer's prose, where a reader seeing `fig_rank_growth` will read
"adaptive rank growth" into a figure that argues against it. **Rename.**

## 5. Merge safety

0 conflicts; 0 files outside coder-owned paths; 129 files on `main` (was 124). The 6
"deletions" are `fig_cost.{pdf,png}` — genuinely dropped, §2 — and the four
`fig_rank_error`/`fig_singular_values` files, all re-added under new names. Verified
individually rather than by count.
