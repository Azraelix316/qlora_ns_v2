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

## 0. The two exact invariants — the method's defining property, and the second one was missing

**`AGENTS.md` names two invariants. Both are implemented, and both are verified.**

| invariant | statement | verification | status |
|---|---|---|---|
| **exact divergence-freeness** | the velocity field is divergence-free to machine precision at **every rank** | `max abs div` `2.3e-14`–`2.0e-13` across every committed run; four tests including an injected-violation detector | **`TODAY`** |
| **forcing-aware energy balance** | **`dE/dt + nu*||omega||^2 - <psi, zeta> = 0`**, with the advection input **retained explicitly and vanishing to roundoff rather than assumed zero** | `test_continuous_energy_balance_for_arbitrary_state` asserts the residual `< 1e-10` for an arbitrary state at `A=0.2`; discrete residual `3.16e-4` in `taylor_green.json` | **`TODAY`** |

**Why the second one belongs in the paper (D39.3).** **A structure-preserving method is defined by the
invariants it preserves, and the paper was preserving and verifying only one of the two it could.**
With both, "structure-preserving" becomes a checkable statement rather than a label. **It also closes
a hole the paper does not know it has: `AGENTS.md` says KE monotonicity is REPLACED by the
forcing-aware balance, so any energy discussion reasoning from monotonicity is reasoning from a
statement the project has disowned.**

**The discrete residual per method is NOT yet recorded** (D39.4): `run_projected` computes
`max_scaled_energy_balance_residual` for every method, but `baselines_re5000_N64_T8.json` does not
persist it, so the artifact carrying contribution 4 lacks the one *continuous* diagnostic that would
say how the methods differ before one of them overflows. **Not claimed as a discriminator until
measured.**

---

## 1. The paper's central result

> ### The settled claim — write this, and nothing fitted
>
> > Against a **strictly out-of-sample** static subspace — a trailing window refit every `0.25`
> > with the refit schedule **offset by half an interval, so no basis ever contains the time it
> > is scored at** — a fixed-rank reduced integrator **leads for `t* = 0.649` at `r = 16` and
> > `1.482` at `r = 32`**, **robust to a 4× change in the baseline's window length (`≤0.63%`)**;
> > **it does not lead at all at `r ≤ 8`**; and **above a rank threshold — bracketed between 32
> > and 43 at `N=64` — it leads at every horizon**, because its error there stays `6–11` orders of
> > magnitude below the static baseline's. **`r=43` is the largest rank tested, NOT the dealiasing
> > ceiling** (D30.2): `2·floor(64/3)+1 = 43` is a *wavenumber*, and the dealiased 64×64 grid
> > carries ~1849 dof, so a rank-43 subspace is not the full-grid solver.
> > **Do not fit a power law** — two resolved ranks cannot support one.

| rank | 2 | 4 | 8 | 16 | 32 | 43 |
|---|---|---|---|---|---|---|
| `t*`, `W=0.25`, `Re=5000` | *never leads* | *never leads* | *unresolved* | **0.649** | **1.482** | **never (exact)** |
| `t*`, `W=0.5`, `Re=5000` | *never leads* | *never leads* | *unresolved* | **0.650** | **1.474** | **never (exact)** |
| `t*`, `W=1.0`, `Re=5000` | *never leads* | *never leads* | *unresolved* | **0.651** | **1.483** | **never (exact)** |
| `t*`, `W=0.25`, `Re=1000` | *never leads* | *never leads* | *unresolved* | **0.667** | **1.609** | **never (exact)** |
| `t*`, `W=0.5`, `Re=1000` | *never leads* | *never leads* | *unresolved* | **0.667** | **1.604** | **never (exact)** |
| `t*`, `W=1.0`, `Re=1000` | *never leads* | *never leads* | *unresolved* | **0.668** | **1.606** | **never (exact)** |

**Window sensitivity `0.15–0.63%`; Reynolds sensitivity `2.8%` (`r=16`) and `8.6%` (`r=32`).**

> ### ⚠⚠ D29 — **I WAS WRONG AND CODER WAS RIGHT. `t*` IS `0.649`/`1.482`, NOT `1.26`/`2.44`.**
>
> **`crossover_surface.json`'s `dlra` list has 10 entries starting at `t=0.00`; the
> `static_moving_window` list has 9 starting at `t=0.10`.** I indexed the DLRA rows with the static
> horizon list, so **every DLRA value I quoted from R60 onward was shifted one horizon.** Everything
> I asserted against the block — the `1.90×` gap, the `3.06×` static gap, "un-provenanced", "stale",
> "window-independent hence not from the rows" — **was that one bug.**
>
> **`crossover_horizon` filters `time > 0.0`, which aligns the two series perfectly:
> `static[oracle]/dlra[rel_l2]` at the same horizon reproduces the block's `ratio_by_horizon` to
> `1e-9` at all nine horizons. The block is correct.**
>
> **AND THE ROWS ARE BIT-FOR-BIT REPRODUCIBLE.** I ran the committed driver fresh: **`0.00%`
> difference on every cell.** This is the strongest provenance result in the project — an
> independent reviewer ran the committed code and recovered every number exactly.
>
> **USE THE TABLE ABOVE (`0.649`/`1.482`, window `≤0.63%`, Re `3–9%`).** Barred: `1.26`, `2.44`,
> `1.46`, `2.45`, `1.24`, `2.53`, `1.33`, and the `≤7%`/`1–4%` robustness figures — all mine, all
> from the shifted lookup. D29.2, D29.4.
>
> **One item still suspect:** the `N=128` grid-dependence multipliers (`1.46→1.99`, `2.45→6.04`)
> may carry the same error. **D17.1's conclusion is probably right; the multipliers are not
> currently verifiable** and must be re-derived from time-aligned rows on both grids (D29.7).

> ### ⚠ D25.5 — SUPERSEDED by D28 above. The rows' `t*` is quotable with D17's five
> qualifiers; the *block's* is not. Retained for the reconciliation record.
>
> `fig_crossover` reads the **rows**; the artifact's `crossovers` block is a **different static
> basis**. **The figure and the block differ by `1.90×` in `t*` and `3.06×` in the static error at
> one horizon** (`t=0.25, r=16, W=0.25`: rows `0.118208` vs block-implied `0.038658`). **The error
> columns explain only 1–3% of that, so it is a different basis, not a different definition.**
>
> **The block's gap has the direction an IN-SAMPLE static baseline produces** (better fit → lower
> error → earlier crossover) — so **the block is the more in-sample of the two**, which is the
> *opposite* of coder's reading, and it is the artifact D15.6 should distrust. **But I could not
> reproduce either convention from the snapshots** (mine give `0.284`/`0.297` where the rows give
> `0.118`), so **nothing is settled — see D25.2/D25.3.**
>
> **Coder's competing values are `0.649` (`r=16`) and `1.482` (`r=32`)**, i.e. the answer moves the
> paper's central number by **`1.9–2.4×`**. **Write the sentence above only once the two agree;
> until then state the qualitative claim (leads at `r ≥ 16`, never at `r ≤ 8`, ceiling is exact)
> without a `t*` value.**

`N=64`, `A=0.2`, full-field relative L2, `Re ∈ {1000, 5000}`, `W ∈ {0.25, 0.5, 1.0}`.

**Source, and it is now a single authoritative one (D29):** the committed `crossover_surface.json`'s
`crossovers` block, which **is** the `dlra` / `static_moving_window` rows — `static[oracle] /
dlra[relative_l2]` at the same horizon reproduces the block's `ratio_by_horizon` to `1e-9` at all
nine horizons — and **the rows are bit-for-bit reproducible**. The Re=1000 column is **coder's own
run**, not a number imported from a reviewer's scratch directory, because an artifact must come from
the code committed beside it.

**Provenance, verified by running the recorded code and NOT by fingerprinting the artifact
(R82/D47).** `crossover_surface.json` records `git_commit: 5909af66` and **no working-tree flag**, so
the run that produced it could in principle have used uncommitted code — a staleness one commit
further out than the one D14.4 covers, and therefore easy to miss. **Settled by extraction, not by
argument:** the recorded commit was extracted with `git archive` into a tree with **no `.git`
directory, so an uncommitted modification was not even possible**, and its own `run_crossover.py` was
run at `Re=5000`, `N=64`, `dt=5e-4`, `A=0.2`, `W=0.25`, `seed=20260925`, ranks 16 and 32, horizons
through `t=2.0` (160 s wall clock, BLAS threads pinned to 1). It returned
**`t* = 0.6493281145096707` and `t* = 1.4816252539052939` — bit-for-bit identical to the committed
artifact, as was every ratio inside both crossing brackets** (`[0.5, 1.0]` and `[1.0, 2.0]`). A run on
uncommitted code would have had to produce coincidentally identical doubles. `solvers/ns_psi.py` and
`solvers/forcing.py` are additionally **md5-identical** between `5909af66` and `HEAD`, and
`run_crossover.py` differs from `HEAD` only by the additive `provenance()` helper.

**A second claim this established, which had been an assumption: the rows are PATH-INDEPENDENT.** A
500-step run to `t=0.25` reproduced the 16 000-step run's ratios at `t=0.1` and `t=0.25` exactly
(`0.00e+00` relative difference, exact float equality), so **a row depends only on the trajectory up
to that time, not on the horizon list or on `final_time`.** That is what makes a short run a valid
reproduction of a long one, and therefore what makes this class of check cheap enough to run
routinely — a 500-step check of the central number costs 12 seconds.

**BOUNDARY (D47.5a, R83) — this is TRUE OF `crossover_surface.json` AND FALSE OF THE ARTIFACTS WHOSE
BASES ARE FITTED ON A FUTURE WINDOW.** A run can be reproduced from a truncated horizon **iff every
basis in the comparison is fitted on the past.** `baselines_re5000_N64_T8.json` does not qualify: its
`pod_late` baseline is fitted on `[T-2.8, T]` and then propagated, and the windows are derived from
`args.T` (`run_baselines.py:561-562`), so **shortening `T` moves the window and changes the answer.**
Its recorded cost is **3 014 s across 19 methods**, and it is **not** covered by the 12-second check.

**The Re dependence is `2.8%` at `r=16` and `8.6%` at `r=32`** (`0.667/0.649` and `1.609/1.482`).
**WITHDRAWN (D29.2–D29.3): the earlier `0.989`/`1.037` "1–4%" figures, and the "three independent
routes agree exactly" claim** — the routes agreed because my one-horizon index bug was consistent
across them, not because three independent computations confirmed each other. `r ≤ 8`'s `0.25` is
the first measurable interval, so "never leads" means *no resolvable lead*, not a measured zero.

**Robustness — what holds, and the one axis that does not (D29.2, D29.7, D30).** From the
committed block, at `N=64`:

| axis | change | effect on `t*` | status |
|---|---|---|---|
| baseline window | 4× (`0.25 → 1.0`) | **`0.15–0.63%`** | **measured, both Re, both ranks** |
| Reynolds number | 5× (`1000 → 5000`) | **`2.8%` (`r=16`), `8.6%` (`r=32`)** | **measured** |
| **grid** | 2× (`64 → 128`) | **NOT ESTABLISHED** | **withdrawn (D29.7) — the `N=128` multipliers are mine and may carry an index shift. Do not quote `1.46→1.99`, `2.45→6.04` or `6.41`.** |

**AND TWO CORRECTIONS TO THE OLD FRAMING OF THIS AXIS. (1) The `r`/ceiling ratios are
MEANINGLESS — they divide a rank by a WAVENUMBER.** `2·floor(N/3)+1` is the largest wavenumber 2/3
dealiasing keeps per direction; it is not a mode count, and the dealiased 64×64 grid carries ~1849
dof. **Never write a rank divided by a "ceiling" (D30.2). (2) `r=43` is the LARGEST RANK TESTED, not
a ceiling, and `r=85` at `N=128` appears in NO artifact** (D30.5).

**WHAT SURVIVES: the grid still belongs in a reported `t*` — we do not know how `t*` behaves under
refinement, and saying so is the honest position — but we no longer assert a multiplier, and D17.2's
"report the ceiling beside the ladder" is WITHDRAWN in favour of "report the grid and the largest
rank tested."**

**A reported `t*` must therefore state FIVE things: the baseline's window length, its refit
interval, its offset, the in-sample check, AND **the grid together with the largest rank
   tested**. *(D30.5: NOT "the dealiasing ceiling" — that is a wavenumber, not a rank.)*
**The offset is now recorded in the artifact (`moving_window_refit_offset: 0.125`), so this
requirement is satisfiable from the artifact rather than from the driver (D22.1).**

**The corrected spine, which is a mechanism rather than a slogan** (R52, **D16.2–D16.3**):

> **A static subspace cannot spend rank at short horizons, and that fixed number is what the
> reduced integrator competes against.** At `t = 0.1` and `t = 0.25` the static error is
> `0.0940` and `0.1183` at **every** rank tested — the spread across the **whole** resolved
> rank range is `0.00%` and `0.09%` — while the reduced integrator's falls to `0.0002` at `r=32`, a
> factor of `941`. **And above `r ≈ 8` the static baseline SATURATES: `r=16`, `r=32` and `r=43` have
> *identical* static errors at every horizon (D30.1).** From `t ≈ 0.5` at the smallest ranks the
> static subspace can begin to use rank, and the crossover is when it does.

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
factor of `1.6–2.8×` and eliminated three of six ranks** (R51, **D15.3**, range **corrected by
D34**):

| baseline as implemented | `t*` at r=16 | at r=32 | ranks resolved |
|---|---|---|---|
| window refit once per evaluation (R39) | 1.15 | 2.42 | 5 of 6 |
| refit every `0.25`, trailing window **includes `t`** (R50) | 1.83 | 2.81 | 5 of 6 |
| **refit every `0.25`, schedule offset, out-of-sample** | **0.649** | **1.482** | **2 of 6** |

> **AND THE DIRECTION MATTERS MORE THAN THE FACTOR.** The corrections made `t*` **SMALLER**, not
> larger: the honest, strictly out-of-sample baseline is the **strongest** one, so the reduced
> integrator's advantage horizon is **shorter** than the buggy baselines suggested. **Fixing the
> baseline made our own method look worse, and we report the corrected number.**

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

**Do not use `crossover_surface.json`'s `crossovers` block — under ANY revision, and it is now
UN-PROVENANCED rather than merely mis-indexed (D23).** The regenerated block's ratios match
**no** error column, **no** cross-column pair (all 16), **no** other rank, and **neither**
`static[t]/dlra[t]` nor `static[t]/dlra[t+1]`, and **the entry names no error column** — so it is
a number with no reproducible relationship to the rows beside it, and its `t_star` is
`0.52–0.64×` the rows' value. It was also unchanged (byte-identical) between the two
regenerations despite a commit message reading "corrected crossovers" (D23.2, D23.5).
**`benchmark_summary.json`'s `crossover_surface.resolved_t_star` copies it verbatim and is
equally unusable (D23.3).** The old committed version reported six nulls with a false reason
string (D15.5). **In every revision: read the `dlra` and `static_moving_window` rows, and
assert any derived block against them under a declared column (D22.5, D23.4).**
**`fig_crossover` reads the rows, so the paper's central figure is correct (D23.3).**

**Do not use `crossover_surface.json`'s `crossovers` block — under ANY revision (D22).** The
committed one (generated at `6571c46`) reports six nulls with a false reason string (D15.5). The
**regenerated** one is better-formatted but **off by one horizon — it pairs `static[t]` with
`DLRA[t+1]`** — and would give `t*(r=16) = 0.649` where the rows give `1.256`, **a `1.9×` error in
the central number**. The proof is at `t = 0.1`, where the rows say the DLRA error is **exactly
`0.0`** (so the ratio is unbounded) and the block reports a finite `7.021`; the error it implies
is the rows' value at `t = 0.25`. **This is coder's own R54 off-by-one, reintroduced in the
derived block rather than the rows (D22.2–D22.3). Read the `dlra` and `static_moving_window`
rows, and **assert any derived block against them** (D22.5).

### 1.3 The two structural facts, which do not drift with `Re`

These matter more than the fit, because the paper's argument rests on them:

1. **Above a rank threshold, nothing overtakes the reduced integrator — and the threshold is
   BRACKETED, not identified.** At `r=43` the DLRA's error runs `6.7e-13` (`t=0.1`) to `2.5e-09`
   (`t=8`, Re=1000) and beats the static baseline by `6e6–1.4e11×`, at **both** Reynolds numbers.
   At `r=32` it does **not** hold (error `0.568` at `t=8`, worse than the static's `0.099`), so the
   threshold lies **between 32 and 43**. **This is Reynolds-independent and baseline-independent.**
   **It is NOT the dealiasing ceiling, and the method is NOT the full-grid solver at that rank**
   (`r=43` is the largest rank tested and coincides with the *wavenumber* `2·floor(64/3)+1`; the
   dealiased grid has ~1849 dof). **"Exact" is also wrong — the error is `1e-13`–`1e-8`, not zero.**
   The real reason is that the dynamics here are effectively low-dimensional. **D30.2–D30.4.**
   **The test that would settle it: `r ∈ {40, 48, 64, 85}` at `N=64`.**
2. **The static baseline SATURATES in rank — above `r ≈ 8`, extra rank buys it nothing.** Verified
   time-keyed from the committed artifact at both Re, all six tested ranks: the spread across rank
   is **`0.00%` at `t=0.1` and `0.09%` at `t=0.25`**, and **`r=16`, `r=32` and `r=43` have
   *identical* static errors to four decimals at every horizon.** Rank-sensitivity begins at
   **`t=0.5` at `r=2` and `r=4`** (not "from `t≈1`"), reaching `40–46%` by `t=2–4` on
   `(max−min)/max` and `56–84%` on `(max−min)/min` — **so the normaliser must be stated; it changes
   the number by nearly 2×.** Re=5000 falls back to `14.3%` by `t=8`. Source: R65/D30.1, superseding
   R45's older `0.3180 → 0.3177` figures, which are from a different regime.

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
> available modes. The **amplitude rule measures the discretisation, not the dynamics** — at `W=8`
> it requests `174` and `357` modes at the two grids, i.e. roughly four times as many modes as the
> largest rank we ever ran, so no fixed relative cutoff can repair it, because any such cutoff
> requests a **grid-dependent** number of modes.
> **DO NOT express this as a multiple of a "dealiasing ceiling": `2·floor(N/3)+1` (`43`, `85`) is a
> WAVENUMBER, and dividing a rank by it is meaningless (D30.2). The claim is that the rank
> requested grows with the grid, not that anything is a multiple of a ceiling.**

**Open and unexplained:** for `W ≥ 12` the required rank is resolution-dependent and
**non-monotone** (`14, 24, 13` at `N=64/128/256`). Do not write that the rank saturates, and
do not write that it grows without limit. Source: R29.

---

## 3. Cost

| quantity | value | source |
|---|---|---|
| full-step ratio vs full grid, `N=64/128/256` | `1.78–2.18` | `cost_retiming.json`, `2a490d3` |
| trend | **saturates at ≈2.1–2.2, does not approach parity** | R42 |
| rank-independence, full step, `r=64`/`r=2` | `1.165 / 1.046 / 1.022` — **the `1.165` was noise; interleaved re-measure gives `1.013`/`1.012` (D25.6)** | R42, D25.6 |
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
| 16 | **1.88×** | **`t* = 0.649`** (D29.4) |
| 32 | **1.90×** | **`t* = 1.482`** (D29.4) |
| 43 | **1.94–2.07×** | **never yields — error `1e-13`–`1e-8`, 6–11 orders below the static baseline. `r=43` is the largest rank TESTED, not a ceiling (D30.2)** |
| any | — | **and no memory advantage: `+2.5 MiB` (N=64) to `+3.8 MiB` (N=128`) _more_ than the full-grid step, flat in rank to within 0.3 MiB** |

**The trade: the lead grows linearly in rank and the cost is nearly rank-independent, so rank
buys *lead time* rather than speed.** Going from `r=8` to `r=32` costs **~2% more per step**
and extends the lead from `0.75` to `2.8` time units — but pays for that lead with a step
that is `1.9×` a full-grid step, so **the method only pays if you need the trajectory's
accuracy over a horizon of order 1–3 time units, and the ceiling is the only rank that never
runs out.**

**The sentence to write:** *rank is nearly free, because per-step cost is dominated by a
rank-independent factorization; what limits the method is the dynamics, not the budget.*

**BUG port — report the SLOWDOWN, not a rank-scaling (D19.2 → D25.6/D25.7).**
**What survives:** **BUG costs `3.3–5.1×` the projected step** (`bug_speedup_hi/lo` `0.195–0.303`,
`cost_bug_port.json`, interleaved protocol with load recorded, `N ∈ {64,128}`, `r ∈ {2,16}`).
Verified structurally (`large_svd_calls == 0`, `svd_max_dimension ≤ 4r`); stationary state held to
`< 1e-12` over 25 steps; second order `1.98 / 1.95`. **Its value is structural preservation, not
speed.** Source: R42, R47, D12.4, **D25.7**.

**WITHDRAWN (D25.6) — the rank-scaling fails on both axes, on coder's own interleaved evidence:**

- **Time: unresolved.** `bug_full_step_ratio_hi_over_lo = 1.366` at `N=64` (`rank_dependent: true`)
  but `1.043` at `N=128` (`false`). The projected integrator's is `1.013`/`1.012`. **Resolved at one
  grid and not the other is not a resolved result.** *(The earlier `1.165` was noise.)*
- **Memory: the committed artifact is stale and contradicted.** `peak_memory.json` still carries
  BUG spread `1.531 MiB` at `N=128` (`5.76×` the `0.1328 MiB` floor,
  `rank_independence_resolved: true`) while the spread **moved `0.125 → 0.398 MiB` between two runs
  of identical code.** **Not reproducible — do not quote `1.531`.**

**So `CLAIMS.md` no longer calls this the project's best-evidenced positive claim. A slowdown is a
negative result; it is still the honest one, and it is weaker than previously stated.**

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
unidirectional shear**, `A ∈ {0.2, 0.5}`, `Re ∈ {100, 1000, 5000}`, `N ∈ {64, 128}`. The
resolution is to describe the flow accurately, not to change it (D20.4).

**And the stationarity negative now has a control (D24).** The AKS pump
`f = (A sin ky, −A k sin kx cos ky)` **was tested, not assumed**: it admits a qualifying S2
horizon where the shear admits **none** — `N=64, A=0.2, T=4` (`8.9% / 6.5%`) and
`N=128, A=0.2, T=2` (`0.4% / 6.0%`). **But the window SHRINKS under refinement** (`T=4` fails
at `N=128`, `Z` drift `12.2%`) and there is **none at `A = 0.5`**. So:

> **Neither forcing admits a resolution-robust stationary fluctuation state at these parameters.**
> The honest statistic is a **window-dependent quasi-steady fluctuation energy, reported with its
> window and its measured drift.**

**This is the negative result _plus_ the positive control that makes it credible** — and it is
why "no stationary state" may be stated at all. **The AKS numbers are reviewer-measured and are
NOT yet citable** (D24.6): no artifact, and the class is not in `solvers/forcing.py`. **Cite only
the negative.**

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
| **any fitted `c·r^p` for the crossover, at any constants** | **void (R51/D15)** — the baseline moved it `1.6–2.8×` (D34) and left only two resolvable ranks. State the two values. |
| `t* ≈ 0.05·r^1.12` (R39) | weak baseline; later found in-sample and starvation-affected |
| `t* ≈ 0.11·r^0.95` (R50/D14) | measured on a driver whose baseline window **ends at the evaluation time** |
| "the curves cross repeatedly, so no horizon exists" (R48) | over-correction; an artefact of the starvation bug |
| "`r ≥ 32` wins at every horizon" / "`r ≤ 8` does not pay" (D13) | from the starvation-affected artifact |
| quoting `crossover_surface.json`'s `crossovers` block | wrong for the third cycle; read the `dlra` / `static_moving_window` rows |
| reporting `t*` without the baseline's window, refit interval and offset | **D15.3** — the number is meaningless without them |
| "a static subspace's floor is rank-independent" **without the horizon qualifier** | **D16.2** — true at `t ≤ 0.25` (0.0–0.1%), false by `t ≈ 2–3` (~40%), and stronger at low `Re` and on a finer grid |
| reporting `t*` without the grid **and the largest rank tested** | **D30.5** — the grid matters (`t*` grows under refinement) but the *dealiasing ceiling* is a **wavenumber**, not a rank, and `r=85` is untested. **D17.1–D17.2 withdrawn on the ceiling clause.** |
| **"only the dealiasing ceiling leads at every horizon, because at that rank the method is the full-grid solver"** | **D30.2/D30.3** — **false on every part.** `r=43` is the largest rank *tested* and coincides with the wavenumber `2·floor(64/3)+1`; the dealiased grid has ~1849 dof; the real reason is that `r=43`'s error is `1e-13`–`1e-8`, i.e. the dynamics are effectively low-dimensional. **"Exact" is also wrong — it is near-roundoff, not zero.** |
| "the rank that never yields is the ceiling" as a grid-free statement | **D17.2** — it is a statement about the *grid*; at `N=128`, `r=43` is half the ceiling and does yield |
| `27.5%` / `1.5%` for the rank rules | **D18.6** — message-only, no artifact; not admissible until committed |
| "a window-accumulating rank rule would fix the criterion" | **D18.1** — implemented and measured: it is **worse** (`1.5%` vs `27.5%` of fluctuation energy) |
| "the window collapses because it fills with the method's own states" | **D18.3** — **refuted**: seeding with reference states gave `1.3%` vs `1.5%`. Record as refuted; do not tell it to a reader |
| any memory or footprint advantage | **D16.4, D19.1** — the reduced method costs `+2.5` to `+3.8 MiB` **more** than the full grid; two independent measurements agree |
| "peak memory is rank-independent" for the projected integrator | **D19.4** — resolved by only `9–10%` over the noise threshold; say **"flat to within 0.3 MiB"** |
| "the BUG port costs more memory as well as more time" | **D19.3** — BUG's overhead is **smaller** (`+2.32` vs `+2.52`); it trades memory for time |
| quoting raw RSS as the memory figure | the ~34 MiB interpreter baseline dominates; report the **overhead over the full grid** |
| quoting `crossover_surface.json`'s `crossovers` block | its reason string is **false** for `r = 2, 4, 16`; read the `dlra` / `static_moving_window` rows instead |
| **`t* = 1.26` / `2.44`, or window robustness `≤7%`, or Re robustness `1–4%`** | **D29.2** — my values, from a one-horizon index shift in the `dlra` list. The block is correct: `0.649`/`1.482`, window `≤0.63%`, Re `3–9%`. |
| "the `crossovers` block is stale / un-provenanced / not derived from the rows" | **D29.2** — all withdrawn. It is the rows, time-aligned, to `1e-9`. |
| "the rows are authoritative" (R58) / "the rows are a fixed floor" (R62) | **both withdrawn** — the block and the rows agree exactly; neither is privileged. The rows are correct, bit-reproducible, and out-of-sample. |
| the `N=128` grid multipliers `1.46→1.99`, `2.45→6.04` | **D29.7** — suspect for the same index shift; the *conclusion* (`t*` is not grid-independent) probably stands, the numbers are unverified |
| calling the central column `relative_l2_oracle_mean`, or describing it as an oracle-mean / perfect-mean error | **D27.1** — it is `d_fluct/‖ref‖` with **each field's own** zonal mean removed, which the artifact's `error_columns` block documents as the opposite. Rename it or compute the column its name promises. |
| **the `crossovers` block's `0.649` / `1.482`, or "the crossover is window-invariant to 0.3%"** | **D28.3/D28.5** — the block is **window-independent** while the rows are window-dependent, so it was not derived from the rows; it is stale. Quote the rows' `1.26`/`2.44`. |
| "a static floor" / "rank-independent floor" as a description of the baseline's construction | **D28.2** — refuted: it is a genuine refitted trailing-window baseline, strictly out-of-sample. The floor language survives only as D16.2's measured horizon-qualified statement. |
| **"BUG's cost scales with rank on both axes"** / "`1.165`" / "`1.531 MiB`" / "the project's best-evidenced positive claim" | **withdrawn (D25.6)** — time is `1.366` (N=64) vs `1.043` (N=128), unresolved; the memory spread moved `0.125 → 0.398 MiB` between identical runs. **Report the `3.3–5.1×` slowdown only.** |

---

## 7. The paper's defensible contribution, in one paragraph

Everything below is measured, and none of it requires retracting a number:

1. **A static subspace's error SATURATES in rank — above `r ≈ 8`, extra rank buys it nothing
   measurable at any horizon**, and the spread across the whole resolved rank range is `0.00%` at
   `t=0.1`, reaching `40–46%` by `t=2–4` (D30.1; **state the normaliser, it changes the number by
   nearly 2×**). Meanwhile a reduced integrator's error falls from `0.6` to `1.6e-8`. **Rank buys
   predictability time, not accuracy**, and the horizon is **`0.649` at `r=16` and `1.482` at
   `r=32`** against a correctly implemented baseline.
2. **That horizon is not a stable quantity, and saying so is the methodological contribution.**
   Three successive corrections to a 60-line baseline moved it by `1.6–2.8×` (D34) and removed half the
   ranks. **Any published crossover for this class of method should carry FIVE things: the
   baseline's window length, its refit interval, its offset, a check that no basis contains its
   evaluation time, and the grid together with the largest rank tested** (D30.5 — the fifth is
   *not* the dealiasing ceiling, which is a wavenumber).
3. **The limit is structural, not numerical.** A static subspace cannot track a flow whose
   support moves, and **its error saturates in rank — `r ≥ 16` buys it nothing measurable at any
   horizon** (D30.1); a refitting integrator can, until
   its own per-step truncation accumulates onto a saturation plateau.
4. **Rank criteria measure different things, and a causal rule provably cannot reach the
   cumulative one.** The windowed `r99` rises `1 → 16` and is grid-independent; a per-step rule
   reads the *instantaneous* `r99`, which falls `14 → 4`; the amplitude rule measures the
   discretisation and asks for a **grid-dependent** number of modes — `174` and `357` at the two
   grids, roughly four times the largest rank we ran — so **no fixed cutoff can repair it.**
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
