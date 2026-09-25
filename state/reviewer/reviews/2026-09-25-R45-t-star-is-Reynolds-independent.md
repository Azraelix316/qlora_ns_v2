# R45 — Is `t* ≈ 0.05 · r^1.12` a law or a one-point fit? **Substantially a law: a 5× change in Reynolds number moves the prefactor 17% and the exponent 10%, and both structural facts hold at both.**

**Cycle:** R45 · **Origin:** R39's law was measured at **one** Reynolds number. A reviewer asks
"is this a law or a fit?" and the project had no answer. The `Re=1000` trajectory was already
cached, so this cost 12 minutes of compute. **Verdict: the law survives, with a weak and
characterisable Reynolds dependence that the paper should state rather than hide.**

## 0. First, a provenance failure inside my own central result

Before running anything I checked that the R39 pipeline still reproduced R39's published
numbers — **and it did not**, because `r39_surface.py` dumps the two surfaces and *nothing
else*. The step from surfaces to `t*` — the log-log interpolation — **existed only in the
report's prose.** The headline numbers of the paper's central result were not derivable from
the code that produced the data.

**That is the R27 failure committed inside the artifact I built R44's rule about.** I have
pinned the estimator as code:

> `t*` is the first crossing of `log(dlra / static_oracle)` through zero, log-log
> interpolated between the bracketing horizons.

Applied to the cached Re=5000 surfaces it reproduces R39's published values **exactly** —
`0.11 / 0.24 / 0.49 / 1.15 / 2.42` at every rank — and the fit to **`0.0509 · r^1.115`**
against the published `0.050 · r^1.12`. The estimator is now re-derivable, and the control
passed before the new measurement was trusted.

## 1. The measurement

Identical pipeline, `A=0.2`, `N=64`, ranks `{2,4,8,16,32,43}`, horizons
`{0.1, 0.25, 0.5, 1, 2, 3, 4, 6, 8}`, oracle-mean moving-window static baseline (`W=1.0`),
full-field relative L2 against the full-grid reference. The decomposition helper validated
against an independent construction on the `Re=1000` cache, as it does on every run.

| rank | `t*` at Re=5000 | `t*` at Re=1000 | ratio |
|---|---|---|---|
| 2 | 0.11 | 0.11 | 1.03 |
| 4 | 0.24 | 0.25 | 1.03 |
| 8 | 0.49 | 0.51 | 1.03 |
| 16 | 1.15 | 1.33 | 1.16 |
| 32 | 2.42 | **3.11** | **1.28** |
| 43 | **never** | **never** | — |
| **fit, `r=4…32`** | **`0.0509 · r^1.115`** | **`0.0435 · r^1.226`** | |

## 2. The exponent difference is real, not fit noise

Four points spanning a factor of 8 in `r` is a thin basis for an exponent, so I checked it
properly with **leave-one-out**:

| | exponent | LOO spread |
|---|---|---|
| Re=5000 | `1.115` | `[1.106, 1.146]` |
| Re=1000 | `1.226` | `[1.201, 1.302]` |

**The two spreads do not overlap.** So `p ≈ 1.12` at Re=5000 and `p ≈ 1.23` at Re=1000 is a
genuine difference, not an artifact of four points — and I would not have known that without
the check, because the headline conclusion is unaffected either way.

## 3. What the paper should now say

> The advantage horizon is a power law in rank, `t* ≈ c · r^p`, with `c ≈ 0.044–0.051` and
> `p ≈ 1.1–1.2` over `Re ∈ {1000, 5000}`. A 5× change in Reynolds number moves the prefactor
> by 17% and the exponent by 10%. The horizon **lengthens as Reynolds number falls** — by 3% at
> `r ≤ 8` and 28% at `r = 32`.

**`t* ≈ 0.05 · r^1.12` remains a fair single-number summary, and it is the Re=5000 value.**
It understates the Re=1000 horizon by up to 28% at `r=32`, so it should carry its Reynolds
number. This is a *better* result than a one-point fit: it is a law with a bounded, measured,
one-sign dependence on a second parameter, and the cost to the paper is one extra column.

**The horizon and the plateau move together, in opposite directions to what "more accuracy"
would suggest.** At `t=8`, `r=32` is **worse** than the static baseline at both Reynolds
numbers — `1.35×` at Re=5000 and **`2.14×`** at Re=1000. So at low Reynolds the crossover
comes *later* **and** the plateau is *deeper*.

*Candidate mechanism, offered as a hypothesis and not as a result, because I have not isolated
it:* at lower Reynolds the flow mixes less, so a stale subspace remains a good predictor for
longer (horizon up) while the reduced integrator's accumulated per-step truncation is less
masked by genuine dynamics (plateau down). **A reviewer will ask whether this is one cause or
two, and the honest answer is that the project has not separated them.**

## 4. The two structural facts do not drift with Reynolds number

These matter more than the fit, because they are the claims the paper's argument rests on:

1. **The dealiasing ceiling never loses.** `r=43` gives `0.0000` at every horizon from `t=0.1`
   to `t=8` at **both** Reynolds numbers, so `t* = ∞` at both. *"The only rank that never
   loses is the rank at which the method is the full-grid solver"* is Reynolds-independent.
2. **The static baseline's floor does not move with rank.** At Re=1000 the oracle baseline
   spans `0.3176` at `r=2` to `0.3176` at `r=43` at `t=0.1` — a 43-fold rank range buying
   nothing at the first horizon, exactly as at Re=5000 (`0.3180` → `0.3177`).

## 5. One caveat that was already true and is now load-bearing

**`r=2`'s `t* = 0.11` is within 10% of the first measured horizon `t=0.1`**, at both Reynolds
numbers. So the lowest rank has **no measurable advantage horizon** — `0.11` is the
interpolation's edge, not a resolved quantity. R39 fitted over `r=4…32` and so already excluded
it correctly; the paper should not quote `t*` at `r=2` as though it were resolved.

## 6. What is still missing

**This is the reviewer's second Reynolds number, not the project's.** Coder reproducing R39
should reproduce **both** columns, and `run_crossover.py` should take `Re` as a parameter
rather than being pinned to 5000 — otherwise the reproduction can only check half of the
result. The surfaces are at
`/tmp/opencode/r39_surface.json` (Re=5000) and `/tmp/opencode/r45_surface_Re1000.json`
(Re=1000); the estimator is appended to `/tmp/opencode/r45_re1000.py` and reproduces R39's
published values exactly, so coder can adopt it rather than re-deriving it.
