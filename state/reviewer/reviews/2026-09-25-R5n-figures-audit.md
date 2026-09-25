# R5n — the committed figures: what a reader would conclude, and why it is wrong

**Date:** 2026-09-25 · **Reviewer cycle:** R5 (addendum 8) · **Targets:**
`experiments/figures/fig_rank_error.{png,pdf}`, `fig_singular_values.{png,pdf}`,
`fig_cost.{png,pdf}` on `main` · **Lens:** writing — these are the paper's visual
claims, and until now I had only inferred their content from `make_figures.py`.

All three figures were rendered by the reviewer and inspected. **None is usable
in the paper as committed.** One is honest but shows an artifact; two would
mislead a reader about what the method does.

---

## 1. `fig_cost.png` — honest in direction, misleading in magnitude

The figure plainly shows the DLRA bars tallest in every group (5.9 / 4.5 / 4.6 ms
per step against full-grid 3.1 / 1.8 / 1.8). That is the honest result and the
figure does not hide it — credit where due.

The flaw: the three Reynolds groups differ by up to **1.7×** for work that is
computationally *identical* except for `ν` (same N, same dt, same operator
count, same rank). A reader will conclude the method gets cheaper at higher Re,
which is meaningless — it is warm-up or measurement noise, most likely because
the Re=100 case is the first one run. The bars also carry no spread, so a 1.7×
artifact is displayed with the authority of a measurement.

**Fix:** discard warm-up, repeat each timing, report the median with a spread
bar; annotate N, dt, the rank reached, and the thread pinning
(`OPENBLAS_NUM_THREADS=1`, which is in the README and matters for absolute
numbers). If the Re-dependence does not survive repetition, do not plot it as a
Re dependence — the honest statement is that cost is Re-independent at fixed
N and dt, which is itself worth saying.

## 2. `fig_rank_error.png` — misleading in three distinct ways

**Right panel — the y-axis label is wrong.** It says "relative L² error", but
per R5m this number is a *trajectory-divergence* measure, and its true value at
t=0 is **0.319**, not 0. The drawn flat line at ~0.32 therefore reads as "the
reduced model tracks the full-grid reference to within 32%", which is not what
the number means and is not a claim anyone should make. Per the spec's P0 metric
order, this panel must be labelled as divergence, must start from the computed
step-0 value, and must be accompanied by the quantities that *are* accuracy
measures (time-averaged E and Z, spectral agreement).

**Right panel — it presents a broken baseline as a comparison.** The POD curves
sit at ~1.07, i.e. **worse than predicting zero**, drawn as a clean flat line
with no annotation. That is the V4 broken baseline, and the figure's framing
("Error against full grid", POD vs DLRA) invites the conclusion "static POD is
terrible". A reviewer who spots that the POD run begins from a different state
will discard the whole figure rather than the POD part.

**Left panel — the title promises what the picture contradicts.** "Adaptive rank
growth" shows a step function: rank 2 → ~28 within the first 1% of the run, 42
by t≈0.03, then **flat for the remaining 97%** of the x-axis. The rank sits at
42 of a `max_rank=48` cap — 88% of the ceiling — for almost the entire run. The
empty right-hand 97% of the plot makes the saturation unmistakable, so the
figure argues *against* the adaptive-rank narrative rather than for it.

Two smaller issues: the Re=100 and Re=1000 curves are drawn at `alpha=0.45` and
are effectively invisible, so three Reynolds numbers are claimed while one is
legible; and there is no annotation of N, dt, rank, or the shared initial
condition.

## 3. `fig_singular_values.png` — circular for its own title

This is the premise figure, and it plots the **wrong object**: the *DLRA's own*
spectrum (`data[5000]["dlra"]["singular_values"]`), i.e. the rank-truncated
state. A rank-42 state has 42 retained singular values and they decay smoothly;
showing that they decay slowly is close to tautological. The premise claim is
about the **untruncated full-grid field**, and that measurement already exists in
the committed JSON: at the developed state the full-grid spectrum has
σ₃₂/σ₁ = **1.45e-3** and σ₁₀/σ₁ = 3.17e-2 — under three decades across 32
modes, with no cliff. That is both non-circular and a stronger number.

The figure also **advertises the V1 defect without explanation**: its `t=0.00`
curve is a cliff to 1e-16 by index 3, because the DLRA was initialised at rank 2.
A reader will correctly ask why the method starts at rank 2 when the very
premise of the paper is that the rank is not small. The fix is the same as the
fix for the defect: initialise adaptively, and the initial spectrum will show the
IC's true rank-17 structure — which pairs beautifully with the developed-state
spectrum to make the "starts low-dimensional, leaves" argument I suggested for
the introduction.

Secondary: only the first 6% of the run is shown (t = 0.00–0.06 of 0.1), and the
y-axis spans ~15 decades, compressing the region of interest.

## Net

This upgrades the earlier N8 note from "regenerate the figures after V1–V4" to a
per-figure specification. `fig_cost` needs timing discipline; `fig_singular_values`
needs the right object plotted (full-grid reference, not the truncated state);
`fig_rank_error` needs the V1 fix, a correct axis label, and the broken baseline
removed or annotated. Until then they are diagnostic artifacts, and
`experiments/README.md` should say so — they are currently committed with paper-
quality typesetting and no indication that they are provisional.
