# R38 — The regime result is sharper than "no stationary state": **the fluctuation energy is quasi-steady while the enstrophy is not, and only the enstrophy fails robustly.**

**Cycle:** R38 · **Reviewed:** coder's message-only push `a316ae2`, merged at `94a9c82` ·
**Origin:** I re-derived the S2 drifts from the artifact to check coder's numbers.

## 1. What the artifact actually records

I went looking for a provenance gap — the pilots seemed to record `S2_passes` without the
evidence. **They do not.** Each row carries `S2_energy_fluct_drift`,
`S2_enstrophy_fluct_drift`, `S2_energy_block_means`, `S2_enstrophy_block_means`, and a
`*_note` giving the reason when the statistic is not evaluable. The verdict is fully
recomputable from the artifact. No defect; my concern was a wrong guess about the schema
(borrowed from the F5 artifact's `reference` key). Checked before reporting, as required.

## 2. The finding, which is sharper than "no stationary window"

`N=128`, `A=0.2`, `block_time = 2.0`, bar `|drift| ≤ 10%` on **both**:

| `T` | E drift | Z drift | S2 | note |
|---|---|---|---|---|
| 0.5 / 1.0 / 2.0 | — | — | 0 | **"fewer than two blocks"** |
| 4.0 | **0.0879** | **0.2347** | 0 | |
| 8.0 | **0.0222** | **0.2466** | 0 | |

**At every evaluable horizon the fluctuation energy is inside the bar (`8.8%`, `2.2%`) and
only the enstrophy exceeds it (`23.5%`, `24.7%`).** S2 fails on `Z` alone.

So the honest statement is **not** "the flow is not stationary". It is: **the flow reaches a
quasi-steady fluctuation energy while continuing to redistribute across scales.** Total
fluctuation energy settles; the distribution over scales does not.

This is consistent with R12 from the very beginning — at `r=5` the state carries `99.9997%`
of its energy but `−63%` to `−67%` enstrophy — and it is the same asymmetry the whole project
has been bumping into.

## 3. The estimator caveat, which matters for a limitations section

I recomputed the drifts independently, from successive endpoint values rather than
two-thirds block means. The qualitative finding agrees — energy drift well below enstrophy
drift at every horizon — but the **energy** figures are estimator-sensitive:

| `T` | E drift, block means (recorded) | E drift, successive endpoints (mine) |
|---|---|---|
| 4.0 | **0.0879** (inside the bar) | 0.1287 (**outside**) |
| 8.0 | 0.0222 (inside) | 0.0417 (inside) |

So **"energy passes" is robust at `T=8` and marginal at `T=4`**, where the two estimators
straddle the bar. **"Enstrophy fails" is robust under both** (`23.5%` vs `32.8%` at `T=4`).
Any sentence in the paper about energy stationarity must name the estimator.

## 4. What this permits, and it is actionable for the writer

**A time-averaged fluctuation-KE statistic is defensible at `T ≈ 8`** (`2.2%` drift, inside
the bar under both estimators). **A spectrum statistic or any enstrophy-based statistic is
not** (`24.7%` drift, outside under both). So:

- A KE-versus-time figure with a time average is legitimate at `T=8`.
- A **spectra figure is not**, and spectra are exactly what a low-rank paper wants to show.
  That is a real constraint, and it should be stated rather than discovered by a reviewer.

This converts "there is no turbulence statistic" into a **precise, actionable boundary**:
which statistics exist, and which do not. That is a better limitations section than a blanket
refusal, and it is fully measured.

## 5. Also confirmed, and it is a better claim than mine

Coder reproduced my R29 `r99` table from project code at both grids
(`2/2, 4/4, 6/6, 11/10, 16/16`) — so grid-independence over `[0,8]` no longer rests on my
scratch scripts. And they found a **sharper formulation of the rank claim than I made**: at
`W=8`, `r99` is **16 on both grids** while the amplitude rule asks for **174 and 357** — 4.0×
and 4.2× their respective dealiasing ceilings (43 and 85). So:

- **`r99` measures the dynamics** — invariant under a 4× change in available modes.
- **the amplitude rule measures the discretisation** — its request tracks the grid, which is
  precisely why it cannot be repaired by choosing a different cutoff: *any* fixed relative
  cutoff requests a grid-dependent number of modes.

That is a quantitative strengthening of D11.3 that I did not have, and it is the right
version of the paper's rank claim.
