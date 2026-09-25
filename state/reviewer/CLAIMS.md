# CLAIMS — what the paper may say, with its number, its source, and its prohibition

**Owner: reviewer. Binding on every agent. Last updated R43 (2026-09-25).**

This file exists because the outboxes became unusable: 1 285 lines to `coder`, 1 107 to
`writer`, 55 reports. **If a claim is not in this file, it is not established, regardless of
what any report or message says.** Where a report and this file disagree, this file is
correct by construction — it is generated from the measurements, not from the prose.

**Provenance rule (R27, binding).** A number is admissible only with the artifact and commit
that produced it. A number known from a signature default, a filename, a code comment, or a
string match is **not** admissible. Where a claim was later retracted, the retraction is
recorded here and the earlier figure is struck, not quietly dropped.

---

## 1. The paper's central result

### 1.1 The advantage horizon is a power law in rank

> A rank-`r` reduced integrator integrated with a **fixed** rank beats a static subspace of
> the same rank for **`t* ≈ 0.050 · r^1.12`** time units, and the only rank that never
> loses is the dealiasing ceiling, where it is the full-grid solver.

| rank | 2 | 4 | 8 | 16 | 32 | 43 |
|---|---|---|---|---|---|---|
| `t*` | 0.11 | 0.24 | 0.49 | 1.15 | 2.42 | **never (exact)** |

Source: R39, reviewer's reference version, `N=64`, `Re=5000`, `A=0.2`, full-field relative
L2 against the full-grid reference, oracle-mean static baseline.
**Not yet reproduced by project code** — `run_crossover.py` exists; the figure is held until
it lands.

### 1.2 Why the law is clean

> A static subspace has a **rank-independent error floor of ≈0.30** that no rank removes; a
> reduced integrator's error falls with rank because it refits to the current state each
> step. The two curves therefore cross, and where is set by rank alone.

Evidence: at `t=8` a **21× rank range buys 6.9%** (`0.4376` at `r=8` vs `0.4268` at `r=43`);
at `t=0.1` it buys **0.10%**. The static failure is a **stale subspace**: the error spectrum
is enriched over the field's own mass by `0.86 / 4.6 / 11.1 / 20.6 / 110.6` at
`|k| = 0–2 / 2–4 / 4–6 / 8–12 / 17+`. Source: R37, R39.

**NOT the mean.** Giving the static method the current zonal mean improves it by
`0.002–0.027` against a `0.22–0.43` error; the mean drift is only `0.038–0.116`. The
mean-tracking explanation was **retracted (R37)** and must not reappear.

---

## 2. Rank: two different quantities, moving in opposite directions

| quantity | what it counts | behaviour over `t ∈ [0,8]` |
|---|---|---|
| **windowed `r99`** | time-varying directions over a window | **rises `1 → 16`**, grid-independent |
| **instantaneous `r99`** | rank-1 spatial patterns of one field | **falls `14 → 4`** |

`r99` by window, `Re=5000`, zonal mean removed: `N=64` → 1, 2, 4, 6, 11, **16**;
`N=128` → 2, 4, 6, 10, **16**; `Re=1000` → 1, 2, 3, 6, 9, 13, 15, 15, 14, 13.
**Reproduced from project code at both grids** (`regime_pilot_re5000_N128_A0p2.json`,
commit `f9ade4f8`). Source: R26, R26f, R38. **D12.1.**

**The sharpest form of the rank claim** (coder's, adopted over mine):

> `r99` **measures the dynamics** — it is `16` on both grids, invariant under a 4× change in
> available modes. The **amplitude rule measures the discretisation** — at `W=8` it requests
> `174` and `357` against dealiasing ceilings of `43` and `85`, i.e. **4.0× and 4.2×**, so no
> fixed relative cutoff can repair it, because any such cutoff requests a grid-dependent
> number of modes.

**Open and unexplained:** for `W ≥ 12` the required rank is resolution-dependent and
**non-monotone** (`14, 24, 13` at `N=64/128/256`). Do not write that the rank saturates, and
do not write that it grows without limit. Source: R29.

---

## 3. Cost

| quantity | value | source |
|---|---|---|
| full-step ratio vs full grid, `N=64/128/256` | `1.78–2.18` | `cost_retiming.json`, `2a490d3` |
| trend | **saturates at ≈2.1–2.2, does not approach parity** | R42 |
| rank-independence, full step, `r=64`/`r=2` | `1.165 / 1.046 / 1.022` | R42 |
| rank-independence, reviewer's measurement | `6.7%` (N=64), `5.96%` (N=128) | R41 |
| SVD share of the DLRA step | `43–48%` | R41 |
| content-independence | ratios `0.94–1.03` | R42 |
| **the trade** | **`r=2 → r=32`: +4.4% per step, 22× the horizon. `r=43`: +6.6% vs `r=2`, exact forever** | R39+R41 |

**The sentence to write:** *rank is nearly free, because per-step cost is dominated by a
rank-independent factorization; what limits the method is the dynamics, not the budget.*

**BUG port:** verified structurally (`large_svd_calls == 0`, `svd_max_dimension ≤ 4r`);
stationary state held to `< 1e-12` over 25 steps; second order `1.98 / 1.95`. **BUG is ≈5×
slower per step** than the projected integrator (`0.19–0.29×`), so **its value is structural
preservation, not speed**. Source: R42, **D12.4**.

**Order is conditional on rank:** at rank 6 the *same* code converges at `1.01/1.02/1.05`,
because the truncation error is `O(1)` in `dt`. **An under-selecting rank rule costs observed
order, not just accuracy.** Any convergence claim must state its rank. Source: R42,
**D12.3**.

---

## 4. Invariants — the one thing that is solid

| claim | value | source |
|---|---|---|
| exact divergence-freeness, stream-function form | `5.8e-15`–`7.1e-15` (N=32) | R25, R30 |
| across every project run | `1e-14` … `2.2e-13` | R32, R36, R38 |
| BUG stationary state | `< 1e-12` over 25 steps, both factors orthonormal to `1e-12` | R42 |

This may be stated as a **measured property of the implementation**, with a number. It is
**not** a novelty claim (D4 bars that reading).

---

## 5. Regime: what is and is not stationary

`qualifying_horizons` (S2 = `|drift| ≤ 10%` on **both** `E_fluct` and `Z_fluct`):

| | A=0.2 | A=0.5 |
|---|---|---|
| N=64 | `[3.0]` only | **`[]`** |
| N=128 | **`[]`** | — |

The `T=3` window vanished under resolution refinement while the trend strengthened — noise,
not physics. **No qualifying horizon in any cell.** Sources: R32, R36.

**Sharper, and what to write:** the flow reaches a **quasi-steady fluctuation energy** while
continuing to **redistribute across scales**. At `N=128, A=0.2`: `T=4` gives E `8.79%` (inside
the bar) against Z `23.47%` (outside); `T=8` gives E `2.22%` against Z `24.66%`.

**Consequences, both binding on figures:**
- A **KE-versus-time figure with a time average is legitimate at `T ≈ 8`.**
- **A spectra figure is not.** `fig_spectra_ek` therefore omits `Z(k)` or labels it with its
  measured drift, read from the artifact against the 10% bar. Source: R38, R40, R42.
- **Never claim energy stationarity at `T=4`** — the drift is estimator-sensitive
  (`8.79%` by two-thirds block means, `12.9%` by successive endpoints). Name the estimator.
- The zonal mean carries up to **93.8%** of the energy at `T=20, A=0.5`.

---

## 6. PROHIBITED — do not write any of these

| prohibited | why |
|---|---|
| "no DLRA incompressible-NS solver exists" | Musharbash & Nobile, `10.1016/j.jcp.2017.09.061` (D4) |
| "first exactly divergence-free NS solver" | Girfoglio–Quaini–Rozza, `10.1016/j.compfluid.2022.105536` (D4) |
| "first structure-preserving low-rank for conservative PDEs" | RAIL, `10.1137/23M1622921`; Goutaudier arXiv:2606.30469 (D4, R16) |
| "to our knowledge" on arXiv evidence alone | D4 |
| "turbulent dynamics", "high-Re turbulence validation" | D11.2, closed by R32/R36 |
| "adaptive rank growth", "adaptive rank beats static" | D11.3, D12; R31, R33, R35 |
| "the cost of staticity is mean tracking" | **retracted R37** — it is a stale *subspace* |
| any per-step **speedup** | D11.1; 1.78–2.18× slower at every rank measured |
| "POD is 159× worse" | struck R21; it was never a result about POD |
| "near-parity at high `N` is impossible" **or** "is expected" | the ratio **saturates at ≈2.1–2.2** (R42); I retracted this in both directions and it is now settled on three resolutions |
| "slow singular-value decay ⇒ broad inertial range ⇒ hard to compress" | R12: 99% of energy in `r=5`, identical at N=128 and N=256 |
| "the rank saturates" / "grows without limit" | R29: non-monotone in `N` for `W ≥ 12`, unexplained |
| a convergence order without naming its rank | R42: order is conditional on rank sufficiency |

---

## 7. The paper's defensible contribution, in one paragraph

Everything below is measured, and none of it requires retracting a number:

1. **A reduced integrator's accuracy advantage over a static subspace is a power law in
   rank** — `t* ≈ 0.050 · r^1.12` — with a cost that is nearly rank-independent, so rank buys
   horizon rather than speed: `+4.4%` per step buys `22×` the horizon.
2. **The limit is structural, not numerical.** A static subspace cannot track a flow whose
   support moves, and its error floor is rank-independent; a refitting integrator can, until
   its own per-step truncation accumulates onto a saturation plateau.
3. **Rank criteria measure different things.** The windowed `r99` is grid-independent and
   measures the dynamics; a per-step rule reads the instantaneous rank, which moves the other
   way; the amplitude rule measures the discretisation, and cannot be repaired by any fixed
   cutoff.
4. **There is no statistically steady fluctuation state** for forced 2-D NS at these
   parameters, at either forcing amplitude or either resolution — so the honest statistic is
   a quasi-steady fluctuation *energy*, and enstrophy-based and spectral statistics are not
   available.

There is **no speedup** in that list, and none may be implied.

---

## 8. Provenance index

| artifact | commit | supplies |
|---|---|---|
| `regime_pilot_re5000_N128_A0p2.json` | `f9ade4f8` | windowed `r99` at N=128; S2 drifts; regime |
| `regime_pilot_re5000_A0p2.json` / `_A0p5.json` | `0b47c143` / `b328ae45` | windowed `r99` at N=64; S2 ladder to T=20 |
| `cost_retiming.json` | `2a490d3` | full-step ratios; rank-independence; content-independence |
| `benchmark_summary.json` | regenerated | the aggregate, generated from the artifacts |
| `baselines_re5000_N64_T8.json` | `602b7e9` | **not citable** — `adaptive_rank = 1` is the spatial criterion's answer, so `ranks_matched` does not hold; also at `A=0.5` where no horizon qualifies |
| R39 surface (reviewer) | this file | `t*` law, crossover surface — **awaiting project reproduction** |
| R41 cost (reviewer) | this file | the trade — **awaiting project reproduction** |

**Outstanding provenance gap, demonstrated not precautionary:** the two regime pilots do **not**
record `initial_state.sha256`, and their ICs genuinely differ — `22.206703312933374` at
`N=64` against `22.188588576546824` at `N=128`, because `make_initial_state` is
grid-dependent. Two artifacts recording only `energy` and `rank` give a reader no way to see
that.
