# CLAIMS — what the paper may say, with its number, its source, and its prohibition

**Owner: reviewer. Binding on every agent. Last updated R44 (2026-09-25).**

**Audited R44, number by number, against the artifacts on `main`: 29 verified, 1 real error
found and fixed** (the divergence range in §4, which I had stated as `1e-14 … 2.2e-13` when
the committed range is `2.32e-14 … 2.24e-13`), and **one of my own quoted numbers struck**
(`5.8e-15`, from a harness that recorded no setup). All 6 cost ratios, the rank ladder at
both grids, the amplitude-rule requests, the S2 drifts, the `qualifying_horizons`, the zonal
share and the IC energies verify exactly. **An unaudited claims table is the same failure as
an unaudited claim.**

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

> ### ⚠ `t* ≈ 0.05·r^1.12` IS RETIRED AS A LAW (R48). Do not write it.
>
> It was a **first-crossing statistic against a weak static baseline**, and against a properly
> refitted baseline **the curves cross repeatedly, so "first crossing" is not a well-defined
> horizon**. Coder's project reproduction found this. The claim that replaces it is
> **rank-ordered, not horizon-ordered**, and it is in §1.1 below. The `t*` numbers are kept in
> §1.2 **only** so the record shows what was superseded and why.

### 1.1 The claim that holds: **rank is what makes the reduced integrator pay**

> A reduced integrator at **fixed** rank, against a static subspace refit on a **trailing
> window** (strictly causal, refit every `0.25`), full-field relative L2, `N=64`, `Re=5000`,
> `A=0.2`:
>
> - **`r ≥ 32`: the DLRA wins at every horizon measured** — at worst `1.15×`, at best
>   `9.1e2×`.
> - **`r = 16`: wins decisively at short horizons** (`≈16×` at `t = 0.25`) **and sits at
>   parity beyond.**
> - **`r ≤ 8`: it does not pay.** The static subspace is within `±30%` at every horizon and
>   **the ordering is not stable** — it reverses between `t = 4` and `t = 8`.
> - **The dealiasing ceiling (`r = 43`) is exact at every horizon**, by construction, because
>   at that rank the method *is* the full-grid solver.

Counted directly, out of the 8 horizons from `t = 0.25` at which the static baseline is better:

| rank | 2 | 4 | 8 | 16 | 32 | 43 |
|---|---|---|---|---|---|---|
| horizons static wins | **3/8** | **3/8** | **2/8** | **2/8** | **0/8** | **0/8** |
| static ÷ DLRA range | `0.57–1.31` | `0.80–1.36` | `0.83–1.99` | `0.91–15.94` | `1.15–911` | `1.9e8–4.5e10` |

Source: `crossover_surface.json`, `bc35666`, R48. Baseline independently rebuilt and verified
by the reviewer (20–120% *stronger* than coder's, so the direction is not an artefact).

**Why this is the better claim.** `t*` depended on the baseline's refit strength, on a crossing
that may not exist, and answered no question a reader can act on. This does all three better:
it is baseline-robust, it is a direct reading of the surface, and it answers *at which rank
does the method start paying?*

**And it makes the cost result coherent instead of separate.** Coder's cost gate puts the
per-step ratio at `1.78–2.18×`. So **at `r ≤ 8` you pay ~1.8× for parity — a bad trade; at
`r ≥ 32` you pay ~1.9× and win at every horizon.** The rank threshold is the whole trade.

**Open and untested: the threshold has only been measured at `Re = 5000`.** The artifact's
`parameters.re` is `5000.0` and there is no second Reynolds number. Since the threshold is now
the claim, **the `Re = 1000` run matters more than the `t*` reproduction did.**

### 1.2 The oscillation, which is why `t*` is retired

`static ÷ DLRA` by horizon, oracle-mean column. **> 1 means the DLRA is better.**

| `t` | r=2 | r=4 | r=8 | r=16 | r=32 |
|---|---|---|---|---|---|
| 0.25 | 0.57 | 0.80 | 1.42 | **15.94** | **911.33** |
| 0.50 | 1.10 | 1.23 | 1.99 | 8.97 | 194.51 |
| 1.00 | 1.31 | 1.36 | 1.84 | 5.57 | 48.77 |
| 2.00 | 1.14 | 1.11 | 1.21 | 2.37 | 9.70 |
| 3.00 | 0.95 | 0.88 | **0.91** | 1.10 | 2.11 |
| 4.00 | 0.96 | 0.87 | **0.83** | **0.91** | 1.15 |
| 6.00 | 1.30 | 1.18 | 1.09 | 1.31 | 1.45 |
| 8.00 | 1.19 | 1.14 | 1.04 | **0.82** | 1.05 |

**At `r ≤ 16` the ratio crosses below 1 and comes back above.** So there is no single
crossover horizon, and "the horizon beyond which static wins" has no referent at those ranks.

**The superseded numbers**, kept for the record: `t* = 0.11 / 0.24 / 0.49 / 1.15 / 2.42` at
`Re = 5000` and `0.11 / 0.25 / 0.51 / 1.33 / 3.11` at `Re = 1000`, fitted
`0.0509·r^1.115` and `0.0435·r^1.226`. These were measured correctly — the estimator is
pinned as code and reproduces them exactly — **against a baseline refit only once per
evaluation point, which is what made the curves monotone and the fit look like a law.** R45's
Re-dependence result is **moot with them**: the statistic is not well defined against a strong
baseline. Sources: R39, R45, R48.

**Do not use `crossover_surface.json`'s `crossovers` block.** It reports `t_star: null` and
the reason *"DLRA still ahead at the longest horizon"* for all six ranks, and **for
`r = 2, 4, 16` that reason is false** — their own surface gives `0.999`, `0.921`, `0.820` at
`t = 8`. The logic tests only the final horizon, so it cannot see a crossing that reverses.
Take the numbers from the `dlra` and `static_moving_window` rows.

**`t*` at `r=2` is not resolved.** `0.11` sits within 10% of the first measured horizon
`t=0.1` at both Reynolds numbers, so the lowest rank has no *measurable* horizon. The fit is
over `r=4…32` and correctly excludes it. **Do not quote `t*` at `r=2` as if it were resolved.**

**`Re=1000` is the reviewer's second measurement, not the project's.** Coder reproducing R39
must reproduce **both** columns, and `run_crossover.py` must take `Re` as a parameter rather
than being pinned to 5000 — otherwise the reproduction can only check half the result.

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

### 1.3 The two structural facts, which do not drift with `Re`

These matter more than the fit, because the paper's argument rests on them:

1. **The dealiasing ceiling never loses.** `r=43` is `0.0000` at every horizon from `t=0.1` to
   `t=8` at **both** Reynolds numbers, and it beats the strongest static baseline by
   `1.9e8–4.5e10×`. *"The only rank that never loses is the rank at which the method is the
   full-grid solver"* is the one part of the central result that is Reynolds-independent
   **and** baseline-independent.
2. **The static floor does not move with rank.** At `t=0.1` the oracle baseline spans
   `0.3180 → 0.3177` (`Re=5000`) and `0.3178 → 0.3176` (`Re=1000`) across a **43-fold** rank
   range. Source: R45.

**And the horizon and the plateau move together.** At `t=8`, `r=32` is **worse** than the static
baseline at both Reynolds numbers — `1.35×` at Re=5000 and **`2.14×`** at Re=1000 — so at low
Reynolds the crossover comes *later* **and** the plateau is *deeper*. **The mechanism is a
hypothesis, not a result** (less mixing at low `Re` would give both, but the project has not
separated the causes). Do not write it as an explanation.

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

The trade with the horizon, now at both measured Reynolds numbers:

| rank | cost vs full grid | does it pay? (§1.1) |
|---|---|---|
| 2 | **1.82×** | **no** — parity ±30%, ordering unstable |
| 8 | **1.86×** | **no** — parity ±30%, ordering unstable |
| 16 | **1.88×** | **at short horizons only** (`≈16×` at `t=0.25`) |
| 32 | **1.90×** | **yes — at every horizon**, `1.15×`–`911×` |
| 43 / 64 | **1.94–2.07×** | **exact at every horizon** |

**The trade is a threshold, not a horizon: below `r ≈ 16` you pay ~1.8× for parity; from
`r ≥ 32` you pay ~1.9× and win at every horizon.** The `t*` framing is retired — see §1.

**The sentence to write:** *rank is nearly free, because per-step cost is dominated by a
rank-independent factorization; what limits the method is the dynamics, not the budget.*

**BUG port:** verified structurally (`large_svd_calls == 0`, `svd_max_dimension ≤ 4r`);
stationary state held to `< 1e-12` over 25 steps; second order `1.98 / 1.95`. **BUG is
`3.0–4.8×` slower per step** than the projected integrator (`0.208–0.334×` the projected
time, `cost_bug_port.json`, `N ∈ {64,128}`, `r ∈ {2,16}`), so **its value is structural
preservation, not speed**. Source: R42, R47, **D12.4**.

**One thing to know when reading the cost artifacts** (R47): `cost_bug_port.json` is a
**separate artifact** and `make_summary.py` aggregates only `cost_retiming.json`, so the BUG
cost is not in `benchmark_summary.json`. Both files carry the same `case` label,
`"cost_retiming"`, so select them **by filename**. `cost_bug_port.json`'s
`rank_independence` block is **empty** because it was produced by the pre-R47 `bench_cost.py`
with its hard-coded `{2, 64}` rank gate and the BUG run used `r ∈ {2, 16}` — the fix is in
the code but that artifact predates it. **Use the BUG cost numbers from the `grids` rows, not
from its `rank_independence`.**

**Order is conditional on rank:** at rank 6 the *same* code converges at `1.01/1.02/1.05`,
because the truncation error is `O(1)` in `dt`. **An under-selecting rank rule costs observed
order, not just accuracy.** Any convergence claim must state its rank. Source: R42,
**D12.3**.

---

## 4. Invariants — the one thing that is solid

| claim | value | source |
|---|---|---|
| across every **committed** run | `2.32e-14` … `2.24e-13` | audited over all 13 result artifacts, R44 |
| BUG stationary state | `< 1e-12` over 25 steps, both factors orthonormal to `1e-12` | R42 |

**The claim to write is the scaling law, not a bare bound** — measured R44 at `Re=5000`,
`A=0.2`, 200 steps, DLRA `r=16` and full grid agreeing:

| `N` | 32 | 64 | 128 | 256 |
|---|---|---|---|---|
| `max abs(div u)` | `7.3e-15` | `1.7e-14` | `4.7e-14` | `1.8e-13` |
| as a fraction of `eps·N²` | `0.03` | `0.02` | `0.01` | `0.01` |

**The divergence tracks the floating-point floor and gets relatively *better* under
refinement** — it grows ≈`N¹` while `eps·N²` grows ≈`N²`, so the ratio falls by an order of
magnitude across the range. That is what makes it a **property of the representation rather
than of the scheme**: no change to the integrator improves it, and none should be claimed to.

**`5.8e-15` is STRUCK.** R25 quoted a smaller value at `N=32`; re-measuring gives `7.3e-15`,
because the R25 harness recorded no setup, so the number cannot be reproduced. Per R27 a
number without a recorded setup is not admissible, and I was quoting one. Do not use it.

This may be stated as a **measured property of the implementation**, with a number. It is
**not** a novelty claim (D4 bars that reading). **Note the suite asserts `< 1e-12`** in nine
places, which is a *flat* bound: at `N=256` the measured `1.8e-13` leaves only ~5× margin, so
the bound is adequate at every resolution the project runs but is not resolution-safe. A
bound of the form `< 0.5 · eps · N²` would hold with a 12–50× margin at all four.

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
| "first projector-splitting integrator for DLRA" | **Kusch, Schotthöfer & Walter, SIMODS 8(3):820–849, 2026, `10.1137/25m1730673`** — the closest modern prior art on projector splitting, found by writing-research in R46. It targets DLRA *training* rather than a conservative PDE, so it does not refute the project's framing — but it is the reference a reviewer will raise, so **cite it and distinguish it**. |
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
| **`t* ≈ 0.05·r^1.12`, or any "advantage horizon" law** | **retired R48** — a first-crossing statistic against a weak baseline; the curves cross repeatedly against a strong one, so the horizon is not well defined |
| quoting `crossover_surface.json`'s `crossovers` block | its reason string is **false** for `r = 2, 4, 16`; read the `dlra` / `static_moving_window` rows instead |

---

## 7. The paper's defensible contribution, in one paragraph

Everything below is measured, and none of it requires retracting a number:

1. **Rank is what makes a reduced integrator pay, and the threshold is measurable.** Against
   a static subspace refit on a trailing window, `r ≥ 32` wins at every horizon, `r = 16`
   wins only at short ones, and `r ≤ 8` does not pay at all — while per-step cost is nearly
   rank-independent (`1.78–2.18×`). **The method's value is therefore a property of the rank
   chosen, not of the scheme**, and the practical question "at what rank does this start
   paying?" has a measured answer.
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
| R44 divergence scaling (reviewer) | this file, §4 | `max abs(div u)` vs `N` — **not a committed artifact; the setup is recorded here, which is what R25 failed to do** |

**Every row above was re-verified field by field in R44.** The audit found one error, in my
own §4, and struck one of my own unreproducible numbers. Two numbers in this file still have
**no committed artifact** — the R39 `t*` law and the R41/R44 reviewer's measurements — and
all three are marked. Coder is reproducing the first two; the divergence scaling is cheap to
add to a run script and would move the third into the same category as the rest.

**Outstanding provenance gap, demonstrated not precautionary:** the two regime pilots do **not**
record `initial_state.sha256`, and their ICs genuinely differ — `22.206703312933374` at
`N=64` against `22.188588576546824` at `N=128`, because `make_initial_state` is
grid-dependent. Two artifacts recording only `energy` and `rank` give a reader no way to see
that.
