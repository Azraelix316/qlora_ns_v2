# R41 — The cost axis of R39's trade, measured: **rank is nearly free. `r=2 → r=32` costs 4.4% more per step and buys 22× the horizon.**

**Cycle:** R41 · **Origin:** R39 produced the accuracy side of the trade and flagged that the
cost figure is missing because `bench_cost.py` has not run (R40). **So I measured the cost
side myself**, under the R5q protocol: threads pinned **and recorded** (asserted, not
assumed), 200-step warm-up discarded, 7 repeats, 2000-step region, median with `[min,max]`
spread, both accountings from the same runs. `Re=5000`, `A=0.2`.

## 1. The measurement

| N | method | ms/step (median) | [min, max] | SVD ms/step | ratio to full grid |
|---|---|---|---|---|---|
| 64 | full grid | 4.937 | [4.932, 4.951] | — | 1.00 |
| 64 | DLRA r=2 | 8.977 | [8.953, 9.313] | 3.872 | **1.82** |
| 64 | DLRA r=8 | 9.167 | [8.981, 9.346] | 3.873 | **1.86** |
| 64 | DLRA r=32 | 9.369 | [9.333, 9.453] | 4.167 | **1.90** |
| 64 | DLRA r=43 | 9.579 | [9.530, 9.680] | 4.405 | **1.94** |
| 128 | full grid | 12.481 | [12.481, 12.528] | — | 1.00 |
| 128 | DLRA r=2 | 27.533 | [27.461, 27.616] | 13.235 | **2.21** |
| 128 | DLRA r=8 | 28.715 | [28.166, 28.786] | 14.036 | **2.30** |
| 128 | DLRA r=32 | 28.327 | [27.851, 28.523] | 14.302 | **2.27** |
| 128 | DLRA r=43 | 29.175 | [28.681, 29.180] | 14.616 | **2.34** |

**Rank-independence confirmed**: a **21× rank range costs 6.7%** at `N=64` and **5.96%** at
`N=128`. R5q's criterion was "within a factor of 1.25" — this passes at 1.067 and 1.060, with
spreads of under 4%. **D11.1's rank-independence claim is verified under the protocol, by
measurement, with threads pinned.**

The SVD is **43%** of the DLRA step at `N=64` and **48%** at `N=128`.

## 2. The trade, which is the paper's cost section

Combining with R39's `t*`:

| rank | cost vs full grid | advantage horizon `t*` |
|---|---|---|
| 2 | **1.82×** | 0.11 |
| 8 | **1.86×** | 0.49 |
| 32 | **1.90×** | 2.42 |
| 43 | **1.94×** | exact at every horizon |

**Going from `r=2` to `r=32` costs 4.4% more per step and buys 22× the horizon. `r=43` costs
6.6% more than `r=2` and is exact forever.**

**That is an unusually favourable trade, and the reason is structural rather than lucky: the
per-step cost is dominated by a rank-independent factorization, so rank is nearly free and
only the dynamics limits you.** This is the honest answer to "what does the method cost", and
it is a better cost section than a speedup table because it says what the money buys.

## 3. A correction to the cost model, and to the extrapolation built on it

**D11.1 and R5q describe the projector as factorizing "the whole `N×N` field" at Θ(N³). The
matrix actually passed to `np.linalg.svd` is `(N, N)` — the field as a 2-D array, not `(N², N²)`.
** Measured: a genuine `4096×4096` full SVD takes **70.05 s**; the projector's per-stage SVD
at `N=64` takes **0.97 ms** — a factor of **72,212**.

This matters for the *asymptotic* argument, not the measured one. The DLRA step grew **3.07×**
per doubling of `N` and the full grid **2.53×**, so the ratio grew **1.21×** per doubling —
whereas the asymptotic prediction from Θ(N³)/Θ(N² log N) is `N/log N`, or **1.72×** per
doubling. The measured range is far from asymptotic (at `N=256` the `(N,N)` SVD sustains
13.4 GFLOP/s, which is memory-bound rather than flop-bound).

**So the claim that "the near-parity-by-`N=512` expectation does not exist" is not
established.** It rests on extrapolating an asymptotic that the measurements contradict in
direction and magnitude. What the data supports is narrower and should be said instead: **the
measured ratio grows by ≈1.2× per doubling, so at `N=512` it is of order 4–5×, and
extrapolation across three doublings from a memory-bound regime is not reliable.** Neither
parity nor divergence is established. Coder's calibration (`2.06 / 2.65 / 2.90`) and mine
(`1.82–1.94 / 2.21–2.34`) agree closely and both should be reported with that caveat.

## 4. And the argument this gives the V6 port

**Rank is nearly free only because the current cost model is rank-*independent*.** The
per-step cost is set almost entirely by an `N`-dependent factorization that does not care
what rank is retained. So the method's cost is `Θ(N³)`-ish regardless of how much
compression it achieves, and the only way to make rank matter to the cost — the only way for
a low-rank method to be *cheap* — is to make the per-step cost **depend** on rank.

**That is a measured argument for the V6 per-stage rank update**, and it is the first one in
this project that does not rest on an asymptotic. D10-V6 has wanted that port on theoretical
grounds since R1; R41 says that under the current implementation the port is what converts
an accuracy advantage into a cost advantage, and that without it the accuracy advantage is
bought for 4%.

## 5. Required

1. **The cost figure is now available** — these are its numbers. Restore `fig_cost.*` and put
   the `t*`-versus-cost table beside the crossover surface. Together they are the paper's
   central figure and its honest cost accounting.
2. **Coder should re-run `bench_cost.py`** to confirm mine independently; the SVD accounting
   and the rank-independence sweep are what I would most want a second opinion on, since
   they are the load-bearing rows.
3. **Drop the "near-parity does not exist" claim** in both directions. Report the measured
   1.2×-per-doubling growth with the memory-bound caveat.
4. **The V6 argument above** belongs in the discussion, attributed to measurement rather than
   to asymptotics.
