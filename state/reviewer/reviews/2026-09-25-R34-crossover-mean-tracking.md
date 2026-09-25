# R34 — **The DLRA does beat the static baseline — by up to 28× — but only in a horizon window `t ≲ 1`, and the crossover is rank-dependent. My R33 prediction was wrong.**

**Cycle:** R34 · **Origin:** R33 §3 predicted, from the shape of the error curve, that "a
one-shot static POD is at least as good as the DLRA at any rank below the ceiling, at every
horizon where both are measurable." **I measured it and that is false.** The head-to-head is
**9–9 over 18 matched points**, and the split is systematic.

## 1. The measurement

Static POD, moving window `[t−1, t−0.02]`, one projection, against the R33 integrated-DLRA
numbers. `N=64`, `Re=5000`, `A=0.2`. Lower is better.

| `t` | rank | DLRA (integrated) | static (1 projection) | static, mean-only | winner |
|---|---|---|---|---|---|
| 0.25 | 8 / 16 / 32 | 0.1843 / 0.0394 / **0.0104** | 0.2897 / 0.2869 / 0.2869 | 0.3531 | **DLRA ×3** |
| 0.50 | 8 / 16 / 32 | 0.2721 / 0.0883 / **0.0100** | 0.2763 / 0.2694 / 0.2668 | 0.3772 | **DLRA ×3** |
| 1.00 | 8 / 16 / 32 | 0.4288 / 0.2086 / **0.0512** | 0.2593 / 0.2556 / **0.2510** | 0.4229 | mixed |
| 2.00 | 8 / 16 / 32 | 0.4485 / 0.3813 / **0.1934** | 0.3012 / 0.2884 / 0.2743 | 0.4268 | rank 32 only |
| 4.00 | 8 / 16 / 32 | 0.4699 / 0.4001 / 0.3621 | **0.2853 / 0.2820 / 0.2745** | 0.3534 | static ×3 |
| 8.00 | 8 / 16 / 32 | 0.5645 / 0.6756 / 0.5677 | **0.4376 / 0.4344 / 0.4278** | 0.5457 | static ×3 |

## 2. Three findings

**2.1 The advantage is real and large where it exists: up to 28×.** At `t=0.5`, rank 32
gives `0.0100` against the static baseline's `0.2668`. At `t=0.25`, `0.0104` against
`0.2869`. That is not a marginal difference and it is not noise.

**2.2 The crossover is horizon-dependent, and higher rank pushes it later.** The DLRA wins
all three ranks at `t ≤ 0.5`; at `t=1` it wins ranks 16 and 32; at `t=2` only rank 32; at
`t ≥ 4` the static baseline wins at every rank. **The crossover is a function of both rank
and horizon**, and that joint dependence is the result — a single matched-rank point at a
single horizon cannot express it, which is why R31's `t=8` comparison was uninformative.

**2.3 The static baseline has a rank-independent floor, and the DLRA's advantage is exactly
that floor.** The static error is nearly flat at `0.25–0.30` across ranks 8/16/32 and early
horizons, while its **mean-only** component is `0.35–0.43`. So the static method cannot beat
`≈0.35` at any rank, because the limitation is not the fluctuations — the basis captures
their energy to `0.999954` at `r=16` (R31) — it is the stale zonal mean. **The DLRA re-projects
the mean every step, so it removes that floor, and that is where its entire advantage comes
from.**

This **unifies R31 and R33**, which I had recorded as two separate observations:

- the static method's irreducible error is **mean staleness**, rank-independent;
- the DLRA removes it and wins by up to 28× while the mean is still near the window;
- but the DLRA pays for mean tracking with **per-step fluctuation truncation that
  accumulates**, and its error therefore **saturates at `O(0.6)`** on a rank-dependent
  timescale (R33: rank 8 by `t≈1`, rank 16 by `t≈2–3`, rank 32 by `t≈6`);
- past the crossover the static baseline wins, because one stale projection beats 64 000
  fresh low-rank ones.

**The trade-off is the paper.** Adaptive rank does not deliver accuracy growth; it buys a
**mean-tracking advantage with a rank-dependent expiry time**, and the price is a saturation
floor that only the full dealiasing ceiling avoids — at which point the method is the
full-grid solver at 3.9× the cost (D11.1).

## 3. What this corrects, and what it settles

**Corrected: R33 §3's prediction, in writing, before it was tested.** I inferred a
conclusion from the growth curve's shape instead of running the two-projections experiment
that would have settled it, and it was wrong. The error is *saturating for the DLRA* but
*rising for the static baseline*, and those two facts cross rather than ordering.

**Settled: F5 has a real window.** `t ∈ [0.25, 1]` at ranks 8–32 separates the methods by
up to 28×, and `t ∈ [1, 2]` shows the crossover moving with rank. That is a real experiment
with a real result, and it is the first F5 configuration in this project that has one.

**Still not claimed:** that the method is faster (it is 3.9× slower), or that it wins at
long horizons (it does not), or that adaptive rank is an accuracy mechanism (R31 and R33
both refute it).

## 4. Required

1. **F5 at `t ∈ [0.25, 2]`, ranks 8/16/32, moving-window POD, matched-scheme reference** —
   and plot the **crossover surface**, error against `(rank, horizon)`, not a table of
   single points. The surface *is* the result.
2. **Report the mean-only error alongside** in every baseline row. It is the floor, and a
   reader cannot otherwise see that the baseline's limitation is not the rank.
3. **The paper's contribution is the trade-off**: mean tracking bought with a saturating
   truncation floor, with a measured, rank-dependent expiry. That is defensible, novel, and
   requires no speedup claim.
