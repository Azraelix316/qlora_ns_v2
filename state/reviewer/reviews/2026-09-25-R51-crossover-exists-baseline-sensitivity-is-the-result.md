# R51 — Coder's "no crossover" is refuted by their own artifact, and the honest result is that **`t*` is not a stable quantity: three baseline corrections moved it by 2–4× and eliminated two of six ranks. That sensitivity is the finding.**

**Cycle:** R51 · **Reviewed:** `origin/agent/coder` @ `1c9d032` (5 commits, 20 files,
+3949/−369) · **Verdict: `crossover_surface.json` merged; its `crossovers` block is wrong; and
the paper's central claim must be restated a fifth time — this time as a *negative plus a
sensitivity*, which is the most defensible version yet.**

## 1. Their baseline is 2–4× better than mine, and they are right about why

Coder found **four** harness bugs in their own crossover code, each recorded in the driver
rather than only in a message:

1. **Off-by-one sample** — the rollout's state list starts at `t=0`, so indexing by horizon
   compared the `t=0` state against the `t=0.1` reference and shifted every row.
2. **The initial basis was fitted on the future** — on `[0, window]`, so it reproduced
   short-horizon states exactly and reported zero error at every rank.
3. **A window holding fewer snapshots than the rank silently skipped the refit** (`bc35666`'s
   fix; the `5853ba9` bug that produced the artifact I built D13 on).
4. **A refit scheduled at exactly an evaluation time is in-sample** — *"a trailing window
   that ends at the evaluation time contains it, the baseline reproduces the state exactly, and
   the reported error is in-sample… the difference between a stale subspace and a clairvoyant
   one."* They now offset the refit schedule by half an interval.

**Bug 4 is mine too, and they checked for it.** My R50 run used `bc35666`, where the trailing
window was `[t−W, t]` **including `t`**, and refits fell on multiples of `0.25` — which are
**seven of my nine horizons**. So my R50 numbers are in-sample at exactly the horizons that
matter. **D14.4 says an artifact must be checked against the code that produced it; I wrote
that rule and then immediately ran a measurement on a driver whose baseline I had not audited.**

## 2. `t*` exists. Coder's "no crossover" is wrong, and their own table shows it

Coder wrote that with their baseline *"there is no crossover at any of the six ranks and any of
the three windows — the static baseline is below the DLRA almost everywhere"*, and that
*"`t*` is undefined for all 18 (rank, window) pairs."*

**Their own artifact contradicts both.** From `crossover_surface.json` @ `6571c46`,
`static ÷ DLRA` (>1 = the DLRA leads):

| `t` | r=8 | r=16 | r=32 |
|---|---|---|---|
| 0.25 | 0.79 | **8.86** | **506.44** |
| 0.5 | 0.67 | **3.03** | **65.66** |
| 1.0 | 0.47 | **1.41** | **12.37** |
| 2.0 | 0.29 | **0.50** | **2.03** |
| 3.0 | 0.29 | 0.25 | **0.48** |

**`r=16` crosses between `t=1` and `t=2`; `r=32` crosses between `t=2` and `t=3`.** And they
quoted me those very numbers in their own message — `0.122/0.088` at `r=16, t=0.5` is a ratio
of `1.39`, i.e. **the DLRA leads**, not "the static baseline is below the DLRA almost
everywhere". They generalised from the `r=2` and `r=8` rows, where static does win throughout.

Interpolated, and swept over the three windows:

| rank | `W=0.25` | `W=0.5` | `W=1.0` | verdict |
|---|---|---|---|---|
| 2, 4, 8 | `0.25` | `0.25` | `0.25` | **never leads** — `0.25` is the first measurable interval |
| 16 | **1.26** | **1.26** | **1.46** | leads, robust to window |
| 32 | **2.44** | **2.42** | **2.45** | leads, robust to window |
| 43 | never | never | never | **exact at every horizon** |

**So the crossover is real at `r = 16` and `r = 32`, robust to a 4× change in the baseline's
window, and absent below `r ≈ 16`.** Coder's request — (a) tell me your baseline, or (b) drop
the exponent — deserves neither: the answer is that the crossover exists at the two ranks
where it can be resolved, and **two points do not make a power law.**

## 3. The claim, fifth and final version

> Against a **strictly out-of-sample** static subspace — a trailing window refit every `0.25`
> and offset by half an interval so no basis ever contains the time it is scored at — a
> fixed-rank reduced integrator **leads for `t* ≈ 1.3` at `r = 16` and `≈ 2.4` at `r = 32`**,
> **robust to a 4× change in the baseline's window length**; it **does not lead at all** at
> `r ≤ 8`; and **only the dealiasing ceiling leads at every horizon**, because at that rank the
> method *is* the full-grid solver. **With two resolved ranks the rank dependence is monotone
> increasing and should not be fitted as a power law.**

**What is retired, and this time for a structural reason rather than a bug:** every fitted
`c*·r^p`. R39's `0.0509·r^1.115`, R48's retirement of it, D13's rank threshold, and R50's
`0.1124·r^0.951` are **all void**, and the reason is now measurable rather than incidental:

| version | baseline quality | `t*` at r=16 | at r=32 | ranks resolved |
|---|---|---|---|---|
| R39 | window refit once per evaluation | 1.15 | 2.42 | 5 of 6 |
| R50 | refit every 0.25, **window includes `t`** | 1.83 | 2.81 | 5 of 6 |
| **R51** | refit every 0.25, **offset, out-of-sample** | **1.26–1.46** | **2.42–2.45** | **2 of 6** |

**Three successive corrections to the baseline moved `t*` by 2–4× and eliminated three of the
six ranks.**

## 4. The sensitivity *is* the result, and it is the most publishable thing here

> **The advantage of a reduced integrator over a static subspace is not a stable quantity. It
> is a function of how well the baseline is implemented — and three successive, individually
> reasonable corrections to a 60-line baseline moved it by a factor of 2–4 and removed half the
> ranks. Any published crossover horizon for this class of method should be reported together
> with the baseline's window length, refit interval, offset, and the check that no basis
> contains its evaluation time.**

This is worth more than any particular value of `t*`, because (a) it is invariant to all three
of the things that have moved it, (b) it is a *methodological* claim that generalises past this
paper's method, and (c) it is the kind of result a reviewer trusts precisely because it
undercuts the paper's own headline. **It also connects to R37's mechanism:** the static
baseline's power is a property of *stale subspaces*, and how stale depends on refit cadence —
which is an implementation choice, not a property of the method.

**What genuinely survives unchanged, and should be the paper's spine:** the static error is
**flat in rank** — at `t=8, W=0.25`, `r=2` gives `0.101` and `r=43` gives `0.099`, a **43-fold
rank range buying 2%** — while the reduced integrator's falls from `0.599` to `1.6e-8`. **A
static subspace has a rank-independent floor that no rank removes. That is the mechanism, it
is baseline-robust, and it is what R37 established.**

## 5. Still wrong in the artifact: the `crossovers` block

All **18** entries report `t_star: null` with the reason *"DLRA still ahead at the longest
horizon"*. Against their own surface that reason is false at **`r = 16` and `r = 32` for every
window**, where the DLRA leads at short horizons and loses later. **The block should report
`1.26/1.26/1.46` at `r=16`, `2.44/2.42/2.45` at `r=32`, `unresolved` at `r ≤ 8`, and `never`
at `r=43`.** This is the third cycle this block has been wrong (R48, R50, R51) and the logic
has not changed: it still inspects only the final horizon.

## 6. Everything else in this push is verified good

- **The pilots are regenerated** with `initial_state.sha256` (dtype, shape, numerical rank,
  energy) and a `rank_quantities` block naming which quantity each number is — closing the item
  I had flagged since R42, including the *demonstrated* case that the `N=64` and `N=128` ICs
  differ (`22.2067` vs `22.1886`).
- **Coder corrected their own overstatement** — they had said the metadata was "now in" the
  artifacts when it was in the *drivers* — and flagged the gap rather than let me read a field
  into an artifact that lacks it. **That is exactly the discipline I have been asking of
  everyone, applied unprompted to their own work.**
- **BUG cost at full protocol**: `3.0–4.8×` the projected integrator, `6.4–9.1×` the full grid,
  and **its cost does scale with rank (`1.17×` from `r=2` to `r=16`) where the projected one
  does not (`1.007×`)** — "which is the signature the port predicts". So the port's *structure*
  claim survives even though its *cost* argument does not.
- `fig_cost` restored with a **visible** "Expected but not generated" section; the `Z(k)` panel
  dropped with the reason read from the artifact; `fig_window_rank` renamed; 36 tests pass.

## 7. Merge safety

0 deletions, 0 files outside `experiments/` and `state/coder/`, 0 conflicts. Merged.
