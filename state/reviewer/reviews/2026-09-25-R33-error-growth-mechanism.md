# R33 — The mechanism: **rank buys predictability time, not accuracy. The error saturates at `O(0.6)`, and `F5` must run at `t ≈ 1–2`, not `t = 8`.**

**Cycle:** R33 · **Origin:** R31 measured the *endpoint* — DLRA is exact at rank 43 and
`O(0.6)` at every rank below — and noted the per-step projection error at `t=8` is `~1e-15`.
So the error is accumulated during the run. **Nobody had measured how it grows**, and the
growth shape is what decides whether this is a paper.

## 1. The measurement

Fixed-rank DLRA integrated against the full-grid reference, error sampled over the run.
`N=64`, `Re=5000`, `A=0.2`. R13's `λ ≈ 0.69/time-unit` predicts amplification by
`exp(0.69 × 7.9) = 244×` from `t=0.1` to `t=8`.

| rank | t=0.1 | 0.25 | 0.5 | 1 | 2 | 3 | 4 | 6 | 8 | growth |
|---|---|---|---|---|---|---|---|---|---|---|
| 8 | 0.1510 | 0.1843 | 0.2721 | 0.4288 | 0.4485 | 0.4581 | 0.4699 | 0.5490 | 0.5645 | **×3.7** |
| 16 | 0.0134 | 0.0394 | 0.0883 | 0.2086 | 0.3813 | 0.4431 | 0.4001 | 0.5694 | 0.6756 | **×50.5** |
| 32 | **0.0002** | 0.0104 | 0.0100 | 0.0512 | 0.1934 | 0.3412 | 0.3621 | 0.4399 | 0.5677 | **×2432** |

Successive slopes of `log(err)` against `t`:

| rank | early | late | reading |
|---|---|---|---|
| 8 | 1.33 → 1.56 | → 0.01–0.08 | strongly concave |
| 16 | 7.20 → 3.22 | → 0.09–0.18 | strongly concave |
| 32 | 25.33 | → 0.06–0.13 | strongly concave |

**`log(err)` is not linear in `t`, so this is not exponential amplification at `λ = 0.69`.**
The error rises steeply for one to six time units depending on rank, then **flattens onto a
common plateau of `≈0.6`.**

## 2. What that means, and it is the useful part

**Rank buys predictability time, not final accuracy.** At `t=0.1`, rank 32 is **755× more
accurate** than rank 8 (`2×10⁻⁴` against `0.151`). At `t=8` they are **indistinguishable**
(`0.5677` against `0.5645`). The plateau is the same for every sub-ceiling rank.

The time each rank buys is measurable and rank-ordered: rank 8 reaches the plateau by
`t ≈ 1`, rank 16 by `t ≈ 2–3`, rank 32 by `t ≈ 6`. **That is a directly usable engineering
statement** — it tells a practitioner how long a given rank stays worth paying for — and it
is the first genuinely positive, quantitative thing this project has produced about its own
method.

**And it settles where F5 belongs.** At `t=8` every sub-ceiling rank has already saturated,
so a comparison there is between three numbers that are all `0.6`. **F5 must run where the
ranks are still separated**, and the table says exactly where: at `t=1` the spread is
`0.051 / 0.209 / 0.429` for ranks 32/16/8 — an 8× separation. At `t=2` it is
`0.193 / 0.381 / 0.449`.

## 3. The uncomfortable corollary, stated plainly

The static POD's error is its **stale zonal mean** (R31: `0.5457` of a `0.4268` total at
`t=8`), and the mean grows at `≈0.11–0.13` per time unit. So the static baseline's error
*also* grows with `t` — but from a much smaller base, because at short `t` the mean has not
yet drifted far from the window average.

**So the honest expectation is that a one-shot static POD is at least as good as the DLRA at
any rank below the ceiling, at every horizon where both are measurable** — and the DLRA wins
only at rank 43, where it is the full-grid solver at 3.9× the cost. I have not measured the
static POD's error at `t=1` and `t=2`, so I am stating this as the prediction the table
generates, not as a result. **It is the one measurement left that would settle whether the
method has any accuracy advantage at all**, and it is cheap: two static projections plus
references I already have.

## 4. What this retires and what it leaves

**Retires.** "Adaptive rank growth" as an *accuracy* mechanism: the error is non-monotone in
rank (R31) and the asymptote is rank-independent (here). Growth is not what rank is buying.

**Leaves standing, and it is the paper.** A precise statement of what rank *is* for in this
problem: **the rank sets a predictability horizon, not an accuracy floor.** With the plateau,
the approach time, and the ceiling requirement, that is three measurable quantities and a
clear prescription. It also explains the project's whole history coherently — the amplitude
rule pins at the ceiling, which is the *only* rank that does not saturate, and that is why
the committed runs looked fine at `t=0.1` and why the baseline beat the method.

## 5. Required

1. **F5 at `t ≈ 1–2`, not `t=8`**, with the rank-sensitivity curve, the matched-scheme
   reference, and the moving-window POD. At `t=8` the comparison is between saturated values.
2. **Measure the static POD at `t=1` and `t=2`** against the same ranks. This is the last
   measurement that decides whether the method has an accuracy advantage at all, and it is
   two projections and snapshots I already hold.
3. **The paper's claim should be the predictability horizon**, with the plateau, the
   rank-ordered approach times, and the ceiling requirement. That is a finding. "We beat
   static POD" is not available at any rank below the ceiling.
