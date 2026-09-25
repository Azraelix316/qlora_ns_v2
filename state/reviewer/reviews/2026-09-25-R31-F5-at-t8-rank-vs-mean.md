# R31 — The decisive F5 measurement: **at `t=8` any rank below the dealiasing ceiling fails, and a one-shot stale static POD beats all of them**

**Cycle:** R31 · **Origin:** R26 said the rank grows `1 → 16` by `t=8`; R24 said a static POD
is exact at `t ≤ 0.1`; nobody had measured a static POD at the horizon where the rank means
something. Coder flagged the fairness trap correctly — the baseline window must not be a
prefix of the evaluation period. I measured it, at `N=64`, `Re=5000`, `A=0.2`, `Δt=5e-4`.

**This is the most consequential experimental result of the review. It changes what the paper
can claim, and it is not close.**

## 1. Headline

| method at `t=8` | rel. L2 vs full-grid reference |
|---|---|
| **DLRA at rank 43 = the dealiasing ceiling** | **0.0000** (exact) |
| DLRA at rank 32 | 0.5677 |
| DLRA at rank 16 | 0.6756 |
| DLRA at rank 8 | 0.5645 |
| DLRA at rank 4 | 0.6413 |
| DLRA at rank 2 | 0.5991 |
| **static POD, `r=43`, projected ONCE** | **0.4268** |
| static POD, `r=1`, projected once | 0.4584 |

**Rank 43 is exact and every rank below it is O(0.6).** Including rank 32, which is 74% of
the ceiling. And **a single stale static projection beats every sub-ceiling DLRA.** So:

- The method is accurate **only at the rank where it is the full-grid solver**, 3.9× slower
  (D11.1).
- **Any genuine rank reduction loses to a one-shot static baseline.**
- The error is **not monotone in rank** (16 is the worst of the six), so "adaptive rank
  growth" cannot be presented as an accuracy mechanism at this horizon.

## 2. Why the static baseline's 0.43 is *not* a rank story

I chased this through four wrong explanations before measuring it, so the controls matter:

| quantity | value | meaning |
|---|---|---|
| fluctuation energy captured at `r=16` | **0.999954** | the basis is essentially perfect |
| at `r=43` | **1.0000000000** | total |
| projection error, `r=1` → `r=43` | 0.4584 → 0.4268 | **rank buys 7%** |
| in-sample vs out-of-sample | 0.4265 vs 0.4268 | **no in-sample advantage** |
| `‖truth − stored mean‖/‖truth‖` | **0.5457** | **the whole error** |

The static POD's error is **entirely its stale zonal mean.** A static basis stores the
*window-average* mean; the mean grows secularly (R8a, ≈0.11–0.13 per time unit), so the
projection cannot represent its current value. The fluctuations are captured essentially
perfectly. So **"the cost of staticity" is mean tracking, not rank** — which is a real and
publishable observation, and the opposite of the draft's framing.

## 3. Why the DLRA fails below the ceiling — and it is not truncation *at a step*

The per-step projection error at `t=8` is negligible at every rank (`1.7e-10` at `r=2`,
`3.5e-15` at `r=43`). The divergence **accumulates over 16 000 steps × 4 stage projections**.
Two controls:

- **Not a scheme difference.** `StreamFunctionNS.step` with an identity projector versus no
  projector at all: `1.5e-11` after 2 000 steps, growing linearly from `4.7e-15` at step 1.
- **Then rank 43 is exactly `0.0000` over the full 16 000 steps.** So the integrator is sound
  and the entire `O(0.6)` is the consequence of truncating.

**The honest statement, and it is the paper's real subject:** the *state* is energetically
low-rank (`r99 ≈ 16`, grid-independent per R29), but *integrating* with that rank for eight
time units produces `O(1)` error. **Representational low-rankness and trajectory
low-rankness are different properties, and the gap between them is the phenomenon.** That is
a genuine, falsifiable, publishable finding — and it is the opposite of what the draft argues.

## 4. What this retires, and what it leaves

**Retires.** The "cost of staticity" argument *as a rank argument* — `r_POD` dominating
"transient peaks of `r(t)`". At `t=8` a rank-16 static POD and a rank-16 DLRA are both
`O(0.6)`, so there is no rank gap to exploit. It also retires adaptive rank as an
*accuracy* mechanism here, since the error is non-monotone in rank.

**Leaves standing, and it is substantial.** R26/R29's `1 → 16` growth (a real, grid-
independent property of the state). Exact divergence-freeness at `7.1e-15`. The mean-growth
mechanism. D11.1's honest cost accounting. And a new, well-supported claim: **the mean, not
the rank, is what a static method cannot track**, with a measured `0.5457`.

## 5. Required

1. **F5 must be run at `t=8` with a matched-*scheme* full-grid reference** — same integrator,
   projector disabled — or the comparison attributes integrator error to rank strategy. The
   identity-projector control is `1.5e-11` per 2 000 steps and is the right control.
2. **The three-baseline suite stands**, and the moving-window baseline is the one to beat:
   it removes the `0.5457` mean staleness. A POD refitted every `0.02` is the honest strong
   baseline, not a frozen one.
3. **Report the rank-sensitivity curve, not a rank.** `0.60 / 0.64 / 0.56 / 0.68 / 0.57 /
   0.00` for `r = 2…43` is the result. A single matched-rank point hides it.
4. **The paper should be about the representational/trajectory gap**, not about adaptive rank
   growth. That is a better paper, it is supported by everything measured so far, and it
   requires retracting the current framing rather than any number.

## 6. What I got wrong on the way, briefly

Four wrong explanations before the measurement: (i) that `r=43` error was decorrelation — no,
it is rank-independent at `Δ=0.02` where decorrelation is `0.014`; (ii) that the degenerate
`W=0.05` moving window was a bug in the basis — it held 2 snapshots, so every rank gave the
same answer, and widening to `W=1.0` fixed it; (iii) an in-place rank truncation
`U = U[:, :min(r, U.shape[1])]` that capped every rank at the first one, making all seven
columns identical — the symptom that looked like "rank doesn't matter" and was actually my
own bug; (iv) that the DLRA's 105% divergence was a scheme difference. Each was caught by a
control, not by reasoning. The rank-truncation bug is the one worth remembering: it
manufactured a plausible-looking finding, and only the non-monotonicity of the fixed-rank
table exposed it.
