# R52 — `t*` is Reynolds-robust; **D15.4's "rank-independent floor" was an endpoint artefact and is qualified**; peak memory measured; and the mechanism behind `t*` identified

**Cycle:** R52 · **What I ran, rather than wait on idle agents:** the `Re = 1000` column on the
**corrected** (out-of-sample, offset) driver with the full window sweep, and **peak memory**,
which no artifact in the project records while the draft explicitly asks for it.

## 1. `t*` is robust to Reynolds number as well as to the window. D15 confirmed.

The corrected driver, windows `0.25 / 0.5 / 1.0`, `Re ∈ {1000, 5000}`:

| rank | Re=5000 | Re=1000 | ratio |
|---|---|---|---|
| 2, 4, 8 | *never leads* (all `W`, both `Re`) | *never leads* | — |
| 16 | `1.26 / 1.26 / 1.46` | `1.24 / 1.24 / 1.33` | **0.99** |
| 32 | `2.44 / 2.42 / 2.45` | `2.53 / 2.52 / 2.53` | **1.04** |
| 43 | **never** | **never** | — |

**A 5× change in Reynolds number moves `t*` by 1–4%, and a 4× change in the baseline's window
by ≤7% (r=16) and ≤1% (r=32).** So D15's claim now has **both** robustness checks, on the
corrected baseline, at two Reynolds numbers. That is as well-supported as this project has
ever had anything.

## 2. D15.4 is qualified: the static floor is rank-independent only at *short* horizons, and my "2%" was an endpoint artefact

I made load-bearing in D15.4: *"the static error is flat in rank — at `t=8, W=0.25`, `r=2` gives
`0.101` and `r=43` gives `0.099`, a 43-fold rank range buying 2%."* **That is one endpoint pair
at one horizon, and it is not representative.** The full row, `W=0.25`:

| `t` | spread across rank, Re=5000 | spread across rank, Re=1000 |
|---|---|---|
| 0.10 | **0.0%** | **0.0%** |
| 0.25 | **0.1%** | **0.1%** |
| 0.50 | 8.7% | 8.7% |
| 1.00 | 24.5% | 24.4% |
| 2.00 | 40.0% | 39.3% |
| 3.00 | 40.7% | **45.4%** |
| 4.00 | 35.7% | **45.8%** |
| 6.00 | 31.2% | **44.9%** |
| 8.00 | 16.4% | **42.7%** |

**Three corrections, and the third is the important one:**
1. **The static error is rank-independent at short horizons** — `0.0%` at `t=0.1`, `0.1%` at
   `t=0.25` — and **only becomes rank-sensitive from `t ≈ 1`**, reaching ~40% by `t = 2–3`.
2. **It is not monotone in rank.** The interior rank `r = 8` is consistently the **worst**
   (at `t=8, Re=5000`: `0.1009, 0.0996, 0.1160, 0.0994, 0.0994, 0.0994` for
   `r = 2,4,8,16,32,43`). **Comparing only the endpoints `r=2` and `r=43` — which is what both
   coder and I did — understates the spread by 8×**, because it skips the worst rank.
3. **The long-horizon sensitivity is Reynolds-dependent**: at `t ≥ 3` a 21× rank range buys
   `43–46%` at `Re=1000` against `16–41%` at `Re=5000`. **So "a static subspace has a
   rank-independent floor that no rank removes" is true at short horizons at both Reynolds
   numbers, and false at long ones at low Reynolds.**

**D15.4 must be restated, and the corrected version is better because it is testable:** the
static error is *exactly* rank-independent at `t ≤ 0.25` and becomes rank-sensitive as the
trajectory has time to move.

## 3. The mechanism behind `t*`, which the corrected data now supports

This is the payoff of §2, and it is the first explanation of the crossover that is not a
restatement of it:

> **A static subspace cannot spend rank at short horizons, and that is what the reduced
> integrator is competing against.** At `t = 0.1` and `t = 0.25` the static error is
> `0.0940` and `0.1183` at **every** rank — the trajectory has not moved far enough for a
> richer subspace to help, so extra rank buys exactly nothing. Meanwhile the reduced
> integrator's error falls steeply with rank (`0.0002` at `r=32, t=0.25`, against the
> baseline's `0.1183` — a factor of `941`). **So the short-horizon competition is against a
> fixed number that rank cannot move, which is precisely why high rank wins decisively there.
> From `t ≈ 1` the static subspace can start to use rank, and the crossover is the moment it
> does.**

This predicts what the data shows: `t*` is where the static error's rank-sensitivity turns on,
it grows with the reduced integrator's rank because only rank buys the early advantage, and it
is nearly Reynolds-independent because the *short-horizon* floor is identical at both. **It also
explains why the ceiling never yields: at `r = 43` the method is the full-grid solver, so its
error is zero by construction rather than by competition.**

## 4. Peak memory: measured, and there is **no** memory advantage

D11.1 bars any per-step *time* speedup, and time has been measured exhaustively. **Memory is a
different axis and nothing in the project recorded it** — while the draft asks for *"per-step and
total wall-clock time **and peak memory**"*. One fresh process per configuration, because peak
RSS is a process high-water mark that cannot be reset; threads pinned; 400 steps; `Re=5000`,
`A=0.2`, `dt=5e-4`.

| `N` | method | peak RSS (MiB) | Δ over setup |
|---|---|---|---|
| 64 | full grid | **35.4** | 0.6 |
| 64 | DLRA `r=2…43` | **38.2** (identical at all six ranks) | 2.8 |
| 128 | full grid | **39.0** | 1.8 |
| 128 | DLRA `r=2…43` | **42.1–42.6** | 4.8–5.5 |

**Two findings, both honest negatives:**
- **Peak RSS is rank-independent** — a **21× rank range changes it by `< 0.5 MiB`** — which is
  the same conclusion as for time and for the same structural reason: the per-step footprint
  is dominated by full-grid work.
- **The reduced method uses ~2.8–3.5 MiB _more_ than the full-grid reference, not less.** It
  holds the full field *plus* the factors *plus* the factorization workspace, so it cannot be a
  memory saving in this implementation. **A reviewer will ask "does it at least save memory?"
  and the answer is no.**

**Caveat I must state, because the absolute numbers are misleading:** the interpreter baseline
is ~34 MiB, so the method's own footprint is 1–8 MiB and the *absolute* figures are not
meaningful. **Only the differences and the rank-independence are.** Any paper text should give
the *overhead over the full grid*, not the raw RSS.

## 5. Two small findings while I was in there

1. **The artifact does not record the refit offset, though its own docstring says it does.**
   `run_crossover.py` states *"The window length, refit interval **and offset** are recorded in
   the artifact"*, and the artifact's `parameters` carry only `moving_window_lengths` and
   `moving_window_refit_interval`. **D15.3 tells every author to report the offset, and the
   project's own artifact does not — so the rule is currently unactionable.** This is the
   second time the offset/in-sample distinction has turned out to be load-bearing.
2. **`crossover_surface.json`'s `crossovers` block is wrong for the third cycle** and its reason
   string is false at `r = 16` and `r = 32`. Unchanged from R51.

## 6. Merge safety

No merge this cycle. The two runs wrote to `/tmp/opencode/rv2/` and used one-process-per-config
probes; nothing was written inside the repository. No agent branch moved.
