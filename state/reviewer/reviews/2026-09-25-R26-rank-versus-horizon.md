# R26 — **Rank versus horizon: the adaptive-rank-growth premise is real, and the project has been measuring it in the first 0.6% of the time it happens**

**Cycle:** R26
**Origin:** R24 established that at `t ≤ 0.1` a rank-1 static POD already solves the
problem, and concluded the experiment was too easy. R25 confirmed the rest of the engine
is sound. That left exactly one question standing, and it is the project's founding
premise: **does the effective rank grow with the horizon?** `AGENTS.md` asserts
"rank ≫ 3, slow singular-value decay, adaptive rank growth — that turbulence validation
is the contribution." Nobody had measured it.

**Answer: yes, and the growth is large — but it happens over `t ∈ [1, 16]`, and the
committed runs stop at `t = 0.1`.** The energetically relevant rank grows from **1 to
16** over the first eight time units, and that part is **grid-independent**. Beyond
`t ≈ 8` the rank keeps climbing as the grid is refined, so the apparent turnover at
`N = 64` is **resolution-limited, not a property of the dynamics**. At `t = 0.1` the
rank is **1**. Every committed artifact is a snapshot of the flat part before the ramp.

This is the first measurement in the review that **supports** the project's premise
rather than retiring part of it, and it is also the measurement that makes the current
experiments fixable: the phenomenon is real, it is simply somewhere the project has not
looked.

---

## 1. Method

Full-grid spectral reference, `N = 64`, `A = 0.2`, `dt = 5e-4`, run to `T = 40`, snapshots
every `0.02` (2000 snapshots, 236 s per Reynolds number). The **zonal (x-) mean is
removed**, because R11 established it is exactly rank 1 and R8a showed it grows
secularly, so leaving it in measures the wrong object. For each **nested** window
`[0, W]` the corrected POD of R24 is computed on the fluctuations and three ranks are
reported:

- `r99` / `r999` — modes for 99% / 99.9% of the fluctuation **energy**. This is the
  rank that matters for accuracy.
- `r(amp 1e-6)` — the rank the **implemented** rule selects, `#\{σ_i > 10⁻⁶σ₁\}`
  (D11.3, D11.5). This is what the code actually does.

Nested windows from a common start are the cleanest form of the question: if forced
dynamics forced rank growth, `r99` would climb with `W`.

## 2. Results

`Re = 5000`:

| window `W` | 0.1 | 0.5 | 1 | 2 | 4 | 8 | 16 | 24 | 32 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|
| `r99` | **1** | 2 | 4 | 6 | 11 | **16** | 14 | 11 | 9 | 6 |
| `r999` | 2 | 3 | 6 | 11 | 22 | 38 | 44 | **49** | 44 | 35 |
| `r(amp 1e-6)` | 4 | 12 | 21 | 41 | 84 | 174 | 368 | 590 | 826 | **1073** |

`Re = 1000`:

| window `W` | 0.1 | 0.5 | 1 | 2 | 4 | 8 | 16 | 24 | 32 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|
| `r99` | **1** | 2 | 3 | 6 | 9 | 13 | **15** | **15** | 14 | 13 |
| `r999` | 2 | 3 | 5 | 10 | 17 | 27 | 36 | **39** | 37 | 35 |
| `r(amp 1e-6)` | 4 | 12 | 21 | 39 | 78 | 154 | 324 | 515 | 665 | **766** |

The two Reynolds numbers agree closely and independently. The dealiasing ceiling is
`2·floor(N/3)+1` — **43** at `N=64`, **85** at `N=128`.

### 2.1 The resolution check, and it is the most important table here

`N = 128`, `Re = 5000`, `A = 0.2`, same protocol, `T = 16` (254 s):

| window `W` | 0.5 | 1 | 2 | 4 | 8 | 12 | 16 |
|---|---|---|---|---|---|---|---|
| `r99` at **N=64** | 2 | 4 | 6 | 11 | **16** | 14 | 14 |
| `r99` at **N=128** | 2 | 4 | 6 | 10 | **16** | **22** | **24** |
| `r999` at **N=64** | 3 | 6 | 11 | 22 | 38 | 44 | 44 |
| `r999` at **N=128** | 3 | 6 | 10 | 18 | 31 | 43 | **50** |

Ground truth for the decomposition at `N=128`: `‖ψ − zonal(ψ)‖ = 41.3094` at `t=4` from
the per-snapshot path, reproduced exactly by an independent broadcast construction
(`match=True`).

**Two regimes, and they behave differently.**

- **`t ≤ 8`: grid-independent.** `r99` agrees to within one mode at every window
  (2, 4, 6, 11/10, 16/16). This growth is a property of the dynamics, and it is the
  growth `AGENTS.md` asserts. It is real.
- **`t ≥ 12`: grid-dependent.** `r99` is 14 at `N=64` and 22–24 at `N=128`. The rank is
  still climbing at `N=128` at `t=16`, where `N=64` has already turned over.

**Therefore the turnover in the `N=64` curve is a resolution artefact, not saturation of
the dynamics.** The flow is still populating scales `N=64` cannot represent, which is
exactly consistent with R8a's independent finding that at `Re=5000` the fluctuation
energy was still *accelerating* (+295%) at `t=40`: it was still being fed structure the
grid could not hold.

## 3. Four findings

**3.1 The energetically relevant rank grows by a factor of sixteen over the first eight
time units, and that growth is grid-independent.** `r99` climbs `1 → 16` at both `N=64`
and `N=128`, agreeing to within one mode at every window. **This part is a property of
the dynamics.** Beyond `t ≈ 8` the two grids part company (§2.1): `N=64` turns over and
falls to 6 by `t=40`, while `N=128` is still climbing to 24 at `t=16`. Both the
mean-growth effect (R8a: `ū_bar` growing, fluctuation share shrinking) and the
resolution limit are visible, and **this measurement cannot separate them** — that needs
a resolution sweep at fixed `Re`, which is now required. What can be said firmly is
that the turnover at `N=64` is *not* saturation, because a finer grid does not saturate.

**3.2 `r(amp 1e-6)` reaches the representable rank between `W = 2` and `W = 4`, and
exceeds it thereafter, at every Re.** The implemented rule asks for 41 modes at `W=2`
(just under the ceiling of 43), then 84, 174, 368, 590, 826, 1073 at `W = 4 … 40`. So by
`t = 4` the rank is not a property of the dynamics at all — it is the ceiling, and the
project's runs have been reporting the ceiling while describing it as adaptation. **D11.3
is confirmed and sharpened: the pinning is not incidental, it is total from `t≈4`
onward, and it is the reason the committed rank traces look flat.** (R27 re-confirmed this
through the code's own rule: `rank_final = 43` at `N=64`, exactly the ceiling.)

**3.3 At 99.9% accuracy the requirement is at or above the ceiling.** `r999` peaks at
**49** (`Re=5000`) and **39** (`Re=1000`) against a ceiling of 43. A 99.9%-energy
representation is therefore *not representable* at `N=64` at the worst horizon. This is
a sharper statement than D11.3's, and it is a real, reportable limitation.

**3.4 The zonal mean dominates the norm and its share shrinks.** `‖residual‖/‖ψ‖` rises
`0.356 → 0.713` from `t=0.02` to `t=40` (`Re=5000`), so the zonal share of the L² norm
falls from 64% to 29% while the *energy* share stays near half. Both are recorded
because they are different quantities and the draft must not conflate them.

## 4. What this changes

**D11.3 is partly reversed, and the reversal is specific.** D11.3 retired "adaptive rank
growth" as a *narrative* claim because rank was the dealiasing ceiling. That remains
true of the **implemented** rule and of every committed artifact. But the
**energetically relevant** rank genuinely grows `1 → 15–16`, and an energy-based rule —
which D11.5 already recommends — would track it. So:

- **Retired:** any claim that the *implemented* rank adapts. It does not; it pins at the
  ceiling from `t=2`.
- **Restored, in a precise form:** there is a real, measurable, horizon-dependent growth
  in the rank the dynamics requires, and the project's chosen rank criterion is what
  hides it. **That is a better contribution than the one currently claimed** — it is a
  finding with a concrete methodological recommendation attached, and it is falsifiable.

**F5 moves.** The matched-rank DLRA-vs-POD comparison is meaningless at `t=0.1`, where
`r99 = 1` and a rank-1 POD is exact (R24). It is meaningful at `t ≈ 8–24`, where
`r99 = 9–16` and a static window has real work to do. **F5 should be run in the
`[8, 24]` window, not at `t=0.1`.**

**The paper's "cost of staticity" sentence is half right.** "In accuracy, intervals
where the basis is insufficient appear as error spikes" — testable at `t≈16`, and now
so. "In rank, `r_POD` must dominate the transient peaks of `r(t)`" — the *peaks* are
real (`r99` peaks at 16), so this sentence is defensible at `t≈16` and indefensible at
`t=0.1`.

**The abstract's "tracking rank growth" becomes true** if and only if the runs are long
enough to contain the ramp, and the rank criterion is energy-based. Neither holds today.

## 5. What this does not change

- **No stationary state** (R8/R8a). Unchanged; this is a transient-growth measurement
  and makes no stationarity claim.
- **The mean-dominated regime characterisation** (D11.2). Unchanged and reinforced:
  the recession in `r99` at late times *is* the mean dominating.
- **Exact divergence-freeness.** Unchanged; R25 measured it at `5.8e-15`.
- **"POD is 159× worse"** remains struck.
- **The POD reshape bug** (R24) and the `DLRA` warm-object defect (R25) are untouched and
  still block F5.

## 6. Required next, in order

1. **A resolution sweep at fixed `Re`, to `N=256`, separating mean growth from
   resolution.** R12 found `r=5` at `N=128` and `N=256`, but at **early times only**.
   §2.1 now shows the late-time behaviour is grid-dependent (14 at `N=64` vs 24 at
   `N=128` at `t=16`). Until that sweep exists, **the turnover in the `N=64` curve
   cannot be attributed** — to the secular mean, to the grid, or to both. This is the
   single most important open question in the project.
2. **`Re = 100`.** D11.2 says quasi-laminar; confirm `r99` is lower, which would make the
   three Reynolds numbers three regimes rather than one phenomenon sampled three times.
3. **The DLRA's own rank trace at `t ≈ 16`.** Prediction: flat at 43 from `t=2`. If so,
   the trace is a measurement of the ceiling, and plotting it as "adaptive rank" is the
   error D11.3 names.
4. **F5 at `t ∈ [8,24]`**, after the reshape and reset fixes.

## 7. The lesson, and it is about batching

This measurement took five attempts and **four of them were wrong in the same way**. My
`zonal` helper averaged `axis=0` and repeated `f.shape[0]` times. That is correct for an
unbatched `(N,N)` field. For a **batched** `(n,N,N)` field, axis 0 is the *snapshot*
axis, x is axis 1, and `f.shape[0]` is `n`, not `N` — so the helper silently returned a
field of the wrong shape and the residuals came out empty (every predicted error printed
`0.000`).

Three separate false beliefs prolonged it:

- **"`E_fluc ≤ E`"** — I treated this as a defining property of the decomposition. It is
  not: the zonal mean is not orthogonal to the residual in the `k²`-weighted inner
  product `ke` uses, so removing it can *increase* the energy (measured: **−10.2%** on
  average). That invalid check is precisely what let the wrong axis pass for a full
  cycle.
- **"The zonal field is constant along `x`"** — checked as `v[i] - v[0:1]`, which is
  satisfied *trivially by a field that is nearly zero*. The wrong axis produced a nearly
  zero field, so the check passed for the wrong reason.
- **A spectral cross-check I added to catch all this** had its own axis confusion: the
  measured ratio `0.518 ≈ 0.5` is the signature of having transformed the **y**-profile.
  I deleted it as redundant rather than fix it, which was the right call but for the
  wrong reason — I should have recognised it as a *third* independent axis error.

What finally settled it was not reasoning but **one function, checked against a measured
constant**: `‖ψ − zonal(ψ)‖ = 19.788` at `t=4` from the unbatched path, reproduced to
the last digit by the batched construction, with a bit-for-bit equality assert.

This is the R25 rule again, one level deeper still. R24: *is the thing real?* R25: *is
the check real?* R26: **is the check real, and does it mean the same thing in every
shape I call it with?** A helper that is correct on `(N,N)` and wrong on `(n,N,N)` is
worse than one that is always wrong, because it passes the tests written for it. The
concrete rule: **a helper must be validated in the exact shape it will be used, against
a constant measured by an independent construction** — not against a property you
believe should hold.
