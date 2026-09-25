# R53b — The fifth robustness axis, and the last one a numerical reviewer asks: **`t*` is NOT grid-independent. The mechanism is.**

**Cycle:** R53b · **What I ran:** the crossover at `N=128` on the corrected driver, four ranks
(`8, 16, 32, 43`), `W=1`, `Re=5000`, launched as four parallel single-rank processes
(accuracy runs are contention-safe; the reference is duplicated per process, which is the right
trade for wall-clock and irrelevant to the numbers). `N=128` costs `dt=2.5e-4` and
`32 000` steps per rank, ~10 min per rank running four abreast.

**The blueprint listed "single grid family" as a limitation. It is now measured, and the answer
qualifies the claim in a way that strengthens the methodological contribution.**

## 1. `t*` grows with resolution

| rank | `r`/ceiling at N=64 | `t*` at N=64 | `r`/ceiling at N=128 | `t*` at N=128 | ratio |
|---|---|---|---|---|---|
| 8 | 0.19 | *never leads* | 0.09 | *never leads* | — |
| 16 | 0.37 | **1.46** | 0.19 | **1.99** | **1.37** |
| 32 | 0.74 | **2.45** | 0.38 | **6.04** | **2.46** |
| 43 | 1.00 | **never** | 0.51 | **6.41** | — |

**A 2× refinement moves `t*` by 37% at `r=16` and 146% at `r=32`.** So the claim of
robustness holds for the baseline's window and for Reynolds number and **fails for the grid**.

**The control that makes this readable: the dealiasing ceiling is grid-dependent** —
`2·floor(N/3)+1` gives **43 at `N=64` and 85 at `N=128`**. So `r=43` *is* the full-grid solver
at `N=64` and is only **51% of the ceiling** at `N=128`. **"The rank that never yields is the
dealiasing ceiling" is a statement about the grid, not about the method**, and any table of
`r=43` rows across grids is comparing two different configurations. Coder's `N=64` ladder stops
at the ceiling; my `N=128` ladder necessarily does not, which is why `r=43` yields at `t*=6.41`
there.

## 2. But the *mechanism* is grid-independent, and that is the better result

D16.3's mechanism is *"a static subspace cannot spend rank at short horizons, and that fixed
number is what the reduced integrator competes against."* **It survives refinement exactly:**

| | `t=0.10` | `t=0.25` | `t=0.50` |
|---|---|---|---|
| static error spread across rank, `N=64` | **0.0%** | **0.1%** | 10.1% |
| static error spread across rank, `N=128` | **0.0%** | **0.0%** | 1.5% |
| static floor, `N=64` | `0.0940` | `0.1182` | `0.1221` |
| static floor, `N=128` | `0.0980` | `0.1238` | `0.1335` |

**And the reduced integrator's own short-horizon error is nearly identical across grids** — at
`t=0.25`: `r=8` gives `0.1500`/`0.1389`, `r=16` `0.0134`/`0.0143`, `r=32` `0.00023`/`0.00021`.

**So the short-horizon competition is grid-independent to within a few percent, and the
crossover is not.** The reason is visible in the long-horizon spreads: at `t=2` the static error
spans `57.4%` across rank at `N=64` against `91.5%` at `N=128`; at `t=3`, `88.7%` against
`116.4%`. **A finer grid gives the static subspace more rank to spend at long horizons, so it
catches up later and the crossover moves out.** That is a coherent mechanism for the
grid-dependence, and it is the same statement as D16.3 with the grid added to it.

## 3. The claim, now with all five axes accounted for

> Against a **strictly out-of-sample** static subspace, a fixed-rank reduced integrator leads for
> `t*` that is **robust to the baseline's window (≤7%) and to a 5× change in Reynolds number
> (1–4%)**, and is **sensitive to the grid (1.4–2.5× from `N=64` to `N=128`) and to the
> baseline's correctness (2–4× across three fixes)**. The rank that never yields is **the
> grid's own dealiasing ceiling** — `43` at `N=64`, `85` at `N=128`. **The mechanism is
> grid-independent**: a static subspace cannot spend rank at short horizons, where a 43-fold
> rank range buys `0.0%` of error reduction at **both** resolutions.

**This is a better result than a uniform robustness claim, and it is the more useful shape.**
Three of the five axes a reader would vary — window, Reynolds, mechanism — hold; the two that
fail, grid and baseline correctness, are **both conventionally omitted from published
comparisons**. So the protocol requirement is now four items, not three: **window length,
refit interval, offset, in-sample check, *and* the grid and its dealiasing ceiling.**

## 4. What this does to the blueprint

- **§7's "single grid family" limitation is upgraded from a gap to a finding.** The grid is not
  merely unexplored; `t*` demonstrably grows with it, by up to `2.5×`.
- **§4 (the protocol section) gains a fifth requirement** — report the grid and its ceiling —
  which is now a *measured* requirement rather than a precaution.
- **§5 gains a resolution row** in the central figure, or the figure caption must say `N=64`
  and the text must give the `N=128` values.
- **§1's thesis survives and is slightly strengthened:** the advantage is not a stable quantity
  in *either* the direction a reader is most likely to assume (grid convergence) or the one they
  are least likely to check (baseline correctness).
- **A caveat I should state rather than let the writer discover:** only `N ∈ {64, 128}` was run,
  and only `Re = 5000` at `N=128`. `N=256` was declined in R42 on cost grounds and that
  decision still stands — the cost gate is unchanged, but a reader may reasonably ask whether
  the grid trend continues.

## 5. Merge safety

No merge. The four runs wrote to `/tmp/opencode/rv3/`; nothing was written inside the
repository, and no agent branch moved.
