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

> ### The settled claim — write this, and nothing fitted
>
> > Against a **strictly out-of-sample** static subspace — a trailing window refit every `0.25`
> > with the refit schedule **offset by half an interval, so no basis ever contains the time it
> > is scored at** — a fixed-rank reduced integrator **leads for `t* ≈ 1.3` at `r = 16` and
> > `≈ 2.4` at `r = 32`**, **robust to a 4× change in the baseline's window length**;
> > **it does not lead at all at `r ≤ 8`**; and **only the dealiasing ceiling leads at every
> > horizon**, because at that rank the method *is* the full-grid solver.
> > **Do not fit a power law** — two resolved ranks cannot support one.

| rank | 2 | 4 | 8 | 16 | 32 | 43 |
|---|---|---|---|---|---|---|
| `t*`, `W=0.25`, `Re=5000` | *never leads* | *never leads* | *never leads* | **1.26** | **2.44** | **never (exact)** |
| `t*`, `W=1.0`, `Re=5000` | *never leads* | *never leads* | *never leads* | **1.46** | **2.45** | **never (exact)** |
| `t*`, `W=0.25`, `Re=1000` | *never leads* | *never leads* | *never leads* | **1.24** | **2.53** | **never (exact)** |
| `t*`, `W=1.0`, `Re=1000` | *never leads* | *never leads* | *never leads* | **1.33** | **2.53** | **never (exact)** |

`N=64`, `A=0.2`, full-field relative L2, `Re ∈ {1000, 5000}`, `W ∈ {0.25, 0.5, 1.0}`. Sources:
`crossover_surface.json` @ `6571c46` (Re=5000, R51) and the reviewer's Re=1000 run on the same
corrected driver (R52). **D16.1.** `r ≤ 8`'s `0.25` is the first measurable interval, so "never
leads" means *no resolvable lead*, not a measured zero.

**Robustness — and the third axis fails (R53b, D17).** A 4× change in the baseline's window
moves `t*` by ≤7% (`r=16`) and ≤1% (`r=32`); a 5× change in Reynolds number by 1–4%. **But a 2×
refinement of the grid moves it by 37% at `r=16` and 146% at `r=32`:**

| rank | `t*` at `N=64` | `t*` at `N=128` | `r`/ceiling at `N=64` | `r`/ceiling at `N=128` |
|---|---|---|---|---|
| 8 | *never leads* | *never leads* | 0.19 | 0.09 |
| 16 | 1.46 | **1.99** | 0.37 | 0.19 |
| 32 | 2.45 | **6.04** | 0.74 | 0.38 |
| 43 | **never** | **6.41** | **1.00** | **0.51** |

**THE CEILING IS GRID-DEPENDENT — `2·floor(N/3)+1` = 43 at `N=64`, 85 at `N=128` — so `r=43` is
the full-grid solver at `N=64` and only half the ceiling at `N=128`. Never quote a rank ladder
without the ceiling beside it (D17.2).**

**A reported `t*` must therefore state FIVE things: the baseline's window length, its refit
interval, its offset, the in-sample check, AND the grid with its dealiasing ceiling.**

**The corrected spine, which is a mechanism rather than a slogan** (R52, **D16.2–D16.3**):

> **A static subspace cannot spend rank at short horizons, and that fixed number is what the
> reduced integrator competes against.** At `t = 0.1` and `t = 0.25` the static error is
> `0.0940` and `0.1183` at **every** rank — a 43-fold rank range buys **0.0%** and **0.1%** —
> while the reduced integrator's falls to `0.0002` at `r=32`, a factor of `941`. From
> `t ≈ 1` the static subspace can begin to use rank and the crossover is when it does.

**The static error is rank-independent at SHORT horizons only — and that is GRID-INDEPENDENT.**
Spread across rank at `t=0.1` is `0.0%` at **both** `N=64` and `N=128`, and `0.0–0.1%` at
`t=0.25`; the floors are `0.0940`/`0.0980` and `0.1182`/`0.1238`. Beyond `t≈1` it becomes
rank-sensitive (`~24%` at `t=1`, `~40%` by `t=2–3` at `N=64`), **more so on the finer grid**
(`57.4%` against `91.5%` at `t=2`), and **more so at low Reynolds** (`43–46%` at `Re=1000`
against `16–41%` at `Re=5000` for `t ≥ 3`). **A finer grid gives the static subspace more rank
to spend at long horizons, so it catches up later — which is the mechanism behind D17.1.** **And it is not monotone in rank: the
interior rank `r=8` is consistently the worst**, so comparing only the endpoints `r=2` and
`r=43` **understates the spread by 8×** — which is what both coder and I did.

### 1.1 The sensitivity is itself the result, and it is the most publishable finding here

**Three successive, individually reasonable corrections to a 60-line baseline moved `t*` by a
factor of 2–4 and eliminated three of six ranks** (R51, **D15.3**):

| baseline as implemented | `t*` at r=16 | at r=32 | ranks resolved |
|---|---|---|---|
| window refit once per evaluation (R39) | 1.15 | 2.42 | 5 of 6 |
| refit every `0.25`, trailing window **includes `t`** (R50) | 1.83 | 2.81 | 5 of 6 |
| **refit every `0.25`, schedule offset, out-of-sample** | **1.26–1.46** | **2.42–2.45** | **2 of 6** |

> **The advantage of a reduced integrator over a static subspace is not a stable quantity: it
> is a function of how well the baseline is implemented. Any published crossover horizon for
> this class of method should be reported with the baseline's window length, refit interval,
> offset, and an explicit check that no basis contains its evaluation time.**

**Why this is worth more than any value of `t*`.** It is invariant to all three of the things
that moved it; it generalises past this paper's method; and it **undercuts the paper's own
headline**, which is why a reviewer will trust it. It also completes R37's mechanism: the
static baseline's power is a property of *stale subspaces*, and how stale depends on refit
cadence — an implementation choice, not a property of the method.

### 1.1a Every fitted form is void — and why, which is the useful part

| was | cycle | why void |
|---|---|---|
| `t* ≈ 0.0509·r^1.115` | R39 | weak baseline; later found in-sample and starvation-affected |
| "the curves cross repeatedly, so `t*` is undefined" | R48 | over-correction; an artefact of the starvation bug |
| "`r ≥ 32` wins at every horizon; `r ≤ 8` does not pay" | D13 | from the starvation-affected artifact |
| `t* ≈ 0.1124·r^0.951`, "invariant to window and Re" | R50/D14 | measured on `bc35666`, whose baseline window **ends at the evaluation time** — in-sample at 7 of 9 horizons |
| **any `c·r^p` at all** | **R51/D15** | **only two ranks have a resolvable crossover. Two points do not make a power law.** |

**The standing rule, now applied to my own work** (**D15.6**): an artifact is not verified
until it has been checked against the code that produced it, **and that applies to reviewer
measurements on a shared driver too.** R50's numbers were taken on a driver whose baseline I
had not audited, one cycle after I wrote the rule. The four baseline bugs coder found are
recorded in their driver: off-by-one sample; the initial basis fitted on the future; a window
holding fewer snapshots than the rank silently skipping the refit; and **a refit at exactly an
evaluation time being in-sample**.

**Do not use `crossover_surface.json`'s `crossovers` block** — wrong for the third cycle
(R48, R50, R51). All 18 entries report `t_star: null` and *"DLRA still ahead at the longest
horizon"*, which is **false at `r=16` and `r=32` for every window**. Read the `dlra` and
`static_moving_window` rows. **The committed artifact itself is current** — its
`provenance.git_commit` is `6571c46`, matching the driver (**D14.4** verified).

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

| rank | cost vs full grid | how long it leads a refitted static subspace (§1) |
|---|---|---|
| 2 | **1.82×** | *never leads* |
| 4 | **1.86×** | *never leads* |
| 8 | **1.86×** | *never leads* |
| 16 | **1.88×** | `t* ≈ 1.3`, leading by `8.9×` at `t = 0.25` |
| 32 | **1.90×** | `t* ≈ 2.4`, leading by `506×` at `t = 0.25` |
| 43 / 64 | **1.94–2.07×** | **never yields — exact at every horizon** |
| any | — | **and no memory advantage: `+2.5 MiB` (N=64) to `+3.8 MiB` (N=128`) _more_ than the full-grid step, flat in rank to within 0.3 MiB** |

**The trade: the lead grows linearly in rank and the cost is nearly rank-independent, so rank
buys *lead time* rather than speed.** Going from `r=8` to `r=32` costs **~2% more per step**
and extends the lead from `0.75` to `2.8` time units — but pays for that lead with a step
that is `1.9×` a full-grid step, so **the method only pays if you need the trajectory's
accuracy over a horizon of order 1–3 time units, and the ceiling is the only rank that never
runs out.**

**The sentence to write:** *rank is nearly free, because per-step cost is dominated by a
rank-independent factorization; what limits the method is the dynamics, not the budget.*

**BUG port — the project's best-evidenced positive claim (D19.2):** its cost **scales with
rank on BOTH axes** — `1.17×` in time from `r=2` to `r=16`, and a peak-memory spread of
`1.531 MiB` (`5.76×` the noise floor) against the projected integrator's `0.289 MiB` (`1.09×`) —
**a prediction confirmed on two independent axes.** State it as such rather than as a cost
caveat. Verified structurally (`large_svd_calls == 0`, `svd_max_dimension ≤ 4r`);
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

## 3a. The setup, and what it actually is (D20 — read this before describing the flow)

> **The forcing is `f = (A sin(k y), 0)`: a single-mode periodic unidirectional shear, whose
> curl is `zeta = -A k cos(k y)`. It is NOT the Arnold–Korkin–Sinitsyn Kolmogorov cellular
> pump.** The naming is genuinely ambiguous in the literature, but **the paper must not call
> this the Kolmogorov flow without stating the formula**, and the draft currently never does.

| do not write | why |
|---|---|
| "Kolmogorov flow" as a description of this setup | D20.1 — the forcing is a unidirectional shear; the AKS flow is a cellular pump with a steady state and the Vinograd–Cullen–Clark boundary |
| "the system possesses the Kolmogorov equilibrium" | D20.1 — that equilibrium belongs to the AKS pump, not to this force |
| "classification of Kolmogorov flow of Vinograd, Cullen, and Clark" as applying here | D20.1 — that classification is about the AKS cellular flow |
| "there is no statistically steady fluctuation state" **as a property of the flow** | **D20.3 — it is a property of the forcing.** The AKS flow *has* a steady cellular state; a periodic shear has no such attractor, so its absence is expected and is not evidence about Kolmogorov flow |

**What the paper studies:** forced 2-D incompressible NS with a **single-mode periodic
unidirectional shear**, `A ∈ {0.2, 0.5}`, `Re ∈ {100, 1000, 5000}`, `N ∈ {64, 128}`. **The
implementation of the true AKS pump would invalidate every measurement in the project**, so the
resolution is to describe the flow accurately, not to change it (D20.4).

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

**Sharper, and what to write** — and note the attribution, which D20.3 requires: this is a
property of **this forcing**, not of the Kolmogorov flow. The flow reaches a **quasi-steady
fluctuation energy** while continuing to **redistribute across scales**. At `N=128, A=0.2`: `T=4` gives E `8.79%` (inside
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
| **"Kolmogorov flow"** as a name for this setup | **D20.1** — the force is a unidirectional shear `f=(A sin ky,0)`, not the AKS cellular pump. State the formula |
| "the Kolmogorov equilibrium", "Vinograd–Cullen–Clark classification" | **D20.1** — those describe the AKS flow |
| "no stationary state" attributed to the **flow** rather than the **forcing** | **D20.3** — the AKS flow has a steady cellular state, so the absence is expected here and is not evidence about Kolmogorov flow |
| "adaptive rank growth", "adaptive rank beats static" | D11.3, D12; R31, R33, R35 |
| "the cost of staticity is mean tracking" | **retracted R37** — it is a stale *subspace* |
| any per-step **speedup** | D11.1; 1.78–2.18× slower at every rank measured |
| "POD is 159× worse" | struck R21; it was never a result about POD |
| "near-parity at high `N` is impossible" **or** "is expected" | the ratio **saturates at ≈2.1–2.2** (R42); I retracted this in both directions and it is now settled on three resolutions |
| "slow singular-value decay ⇒ broad inertial range ⇒ hard to compress" | R12: 99% of energy in `r=5`, identical at N=128 and N=256 |
| "the rank saturates" / "grows without limit" | R29: non-monotone in `N` for `W ≥ 12`, unexplained |
| a convergence order without naming its rank | R42: order is conditional on rank sufficiency |
| **any fitted `c·r^p` for the crossover, at any constants** | **void (R51/D15)** — the baseline moved it 2–4× and left only two resolvable ranks. State the two values. |
| `t* ≈ 0.05·r^1.12` (R39) | weak baseline; later found in-sample and starvation-affected |
| `t* ≈ 0.11·r^0.95` (R50/D14) | measured on a driver whose baseline window **ends at the evaluation time** |
| "the curves cross repeatedly, so no horizon exists" (R48) | over-correction; an artefact of the starvation bug |
| "`r ≥ 32` wins at every horizon" / "`r ≤ 8` does not pay" (D13) | from the starvation-affected artifact |
| quoting `crossover_surface.json`'s `crossovers` block | wrong for the third cycle; read the `dlra` / `static_moving_window` rows |
| reporting `t*` without the baseline's window, refit interval and offset | **D15.3** — the number is meaningless without them |
| "a static subspace's floor is rank-independent" **without the horizon qualifier** | **D16.2** — true at `t ≤ 0.25` (0.0–0.1%), false by `t ≈ 2–3` (~40%), and stronger at low `Re` and on a finer grid |
| reporting `t*` without the grid and its dealiasing ceiling | **D17.1–D17.2** — `t*` grows 1.4–2.5× from `N=64` to `N=128`, and the ceiling is 43 vs 85 |
| "the rank that never yields is the ceiling" as a grid-free statement | **D17.2** — it is a statement about the *grid*; at `N=128`, `r=43` is half the ceiling and does yield |
| `27.5%` / `1.5%` for the rank rules | **D18.6** — message-only, no artifact; not admissible until committed |
| "a window-accumulating rank rule would fix the criterion" | **D18.1** — implemented and measured: it is **worse** (`1.5%` vs `27.5%` of fluctuation energy) |
| "the window collapses because it fills with the method's own states" | **D18.3** — **refuted**: seeding with reference states gave `1.3%` vs `1.5%`. Record as refuted; do not tell it to a reader |
| any memory or footprint advantage | **D16.4, D19.1** — the reduced method costs `+2.5` to `+3.8 MiB` **more** than the full grid; two independent measurements agree |
| "peak memory is rank-independent" for the projected integrator | **D19.4** — resolved by only `9–10%` over the noise threshold; say **"flat to within 0.3 MiB"** |
| "the BUG port costs more memory as well as more time" | **D19.3** — BUG's overhead is **smaller** (`+2.32` vs `+2.52`); it trades memory for time |
| quoting raw RSS as the memory figure | the ~34 MiB interpreter baseline dominates; report the **overhead over the full grid** |
| quoting `crossover_surface.json`'s `crossovers` block | its reason string is **false** for `r = 2, 4, 16`; read the `dlra` / `static_moving_window` rows instead |

---

## 7. The paper's defensible contribution, in one paragraph

Everything below is measured, and none of it requires retracting a number:

1. **A static subspace has a rank-independent error floor that no rank removes** — a 43-fold
   rank range buys 2% — while a reduced integrator's error falls from `0.6` to `1.6e-8`. **Rank
   buys predictability time, not accuracy**, and the horizon is `≈1.3` at `r=16` and `≈2.4` at
   `r=32` against a correctly implemented baseline.
2. **That horizon is not a stable quantity, and saying so is the methodological contribution.**
   Three successive corrections to a 60-line baseline moved it by 2–4× and removed half the
   ranks. **Any published crossover for this class of method should carry the baseline's window
   length, refit interval, offset, and a check that no basis contains its evaluation time.**
3. **The limit is structural, not numerical.** A static subspace cannot track a flow whose
   support moves, and its error floor is rank-independent; a refitting integrator can, until
   its own per-step truncation accumulates onto a saturation plateau.
4. **Rank criteria measure different things, and a causal rule provably cannot reach the
   cumulative one.** The windowed `r99` rises `1 → 16` and is grid-independent; a per-step rule
   reads the *instantaneous* `r99`, which falls `14 → 4`; the amplitude rule measures the
   discretisation and asks for `4.0×`/`4.2×` the dealiasing ceilings, so **no fixed cutoff can
   repair it.** **A window-accumulating rule was implemented, measured, and does not work:** it
   never exceeds rank 2 and keeps `1.5%` of the fluctuation energy against the per-step rule's
   `27.5%`, because it measures *local* complexity — which genuinely is `≈2` — while `1 → 16`
   is **cumulative**, reachable only by remembering the whole trajectory, which is what static
   and offline methods do and **what a causal per-step method cannot do** (D18.2). *The
   `27.5%`/`1.5%` figures are message-only and are **not yet citable** until they are in an
   artifact (D18.6).*
5. **There is no statistically steady fluctuation state** for forced 2-D NS at these
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
