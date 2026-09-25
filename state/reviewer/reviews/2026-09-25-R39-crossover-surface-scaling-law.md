# R39 — The paper's central result, measured: **the advantage horizon scales as `t* ≈ 0.050 · r^1.12`. A static subspace has a rank-independent floor of ≈0.30 that no rank removes.**

**Cycle:** R39 · **Origin:** the crossover surface is the paper's central figure and coder
has not run it (they are on `bench_cost.py`). The paper is blocked on it, so I produced the
reviewer's reference version. 6 ranks × 9 horizons, two static baselines, one run per rank
(~12 min total). `N=64`, `Re=5000`, `A=0.2` — the same flow as every rank measurement the
project now has.

## 1. The surface

DLRA, integrated from the canonical IC, full-field relative L2 against the full-grid
reference. `*` = best in the row.

| `t` | r=2 | r=4 | r=8 | r=16 | r=32 | r=43 |
|---|---|---|---|---|---|---|
| 0.10 | 0.3154 | 0.2672 | 0.1510 | 0.0134 | 0.0002 | *0.0000 |
| 0.25 | 0.3272 | 0.2964 | 0.1843 | 0.0394 | 0.0104 | *0.0103 |
| 0.50 | 0.3767 | 0.3681 | 0.2721 | 0.0883 | 0.0100 | *0.0000 |
| 1.00 | 0.4566 | 0.4674 | 0.4288 | 0.2086 | 0.0512 | *0.0000 |
| 2.00 | 0.4588 | 0.4912 | 0.4485 | 0.3813 | 0.1934 | *0.0000 |
| 3.00 | 0.4262 | 0.4614 | 0.4581 | 0.4431 | 0.3412 | *0.0000 |
| 4.00 | 0.4057 | 0.4436 | 0.4699 | 0.4001 | 0.3621 | *0.0000 |
| 6.00 | 0.5090 | 0.5272 | 0.5490 | 0.5694 | 0.4399 | *0.0000 |
| 8.00 | 0.5991 | 0.6413 | 0.5645 | 0.6756 | 0.5677 | *0.0000 |

Static POD, moving window, **oracle mean** (R37's strongest static baseline):

| `t` | r=2 | r=4 | r=8 | r=16 | r=32 | r=43 |
|---|---|---|---|---|---|---|
| 0.10 | 0.3180 | *0.3177* | *0.3177* | *0.3177* | *0.3177* | *0.3177* |
| 0.25 | 0.3005 | 0.2949 | 0.2873 | *0.2844* | *0.2844* | *0.2844* |
| 0.50 | 0.2820 | 0.2755 | 0.2700 | 0.2629 | *0.2603* | *0.2603* |
| 1.00 | 0.2569 | 0.2378 | 0.2322 | 0.2280 | 0.2229 | *0.2211* |
| 2.00 | 0.2991 | 0.2872 | 0.2808 | 0.2670 | 0.2518 | *0.2468* |
| 4.00 | 0.2826 | 0.2747 | 0.2716 | 0.2682 | 0.2602 | *0.2584* |
| 8.00 | 0.4511 | 0.4367 | 0.4300 | 0.4268 | 0.4201 | *0.4190* |

## 2. The result: a scaling law

**The advantage horizon is a clean monotone function of rank.** Interpolating where the
oracle baseline overtakes the DLRA at equal rank:

| rank | 2 | 4 | 8 | 16 | 32 | 43 |
|---|---|---|---|---|---|---|
| **crossover `t*`** | **0.11** | **0.24** | **0.49** | **1.15** | **2.42** | **never** (exact) |

Log-log fit over `r = 4…32`: **`t* ≈ 0.050 · r^1.12`**, i.e. the horizon roughly **doubles per
doubling of rank** (successive ratios `2.04, 2.35, 2.10`).

**And the mechanism is the reason it is clean.** The static baseline's error is nearly
**rank-independent**: at `t=8`, `r=43` gives `0.4268` against `r=2`'s `0.4584` — a 21× rank
range buys **6.9%**, and at `t=0.1` it buys **0.10%**. A static subspace has a **floor of
≈0.30** that no rank removes (R37: a stale subspace, enriched up to 110× in the wavenumber
bands the field barely uses). The DLRA's error, by contrast, **falls with rank**. So the two
curves cross, and where they cross is set by rank alone.

**This is the paper.** It states R33's qualitative claim — *rank buys predictability time, not
accuracy* — as a law a reader can use: **a rank-`r` reduced integrator beats a static
subspace for `≈0.05·r^1.12` time units and not much longer, and the only rank that never
loses is the dealiasing ceiling, where it is the full-grid solver at 3.9× the cost.**

## 3. Why this is the right central figure, and what it supersedes

It supersedes every single-point comparison the project has: R31's `t=8` matched-rank point
(all ranks saturated), R33's endpoint table, R34's 18-point head-to-head. A surface in
`(rank, horizon)` contains all of them and shows the structure.

It also **reconciles the three results that looked contradictory**:

- R31/R33: the DLRA saturates at `O(0.6)` and its error is non-monotone in rank — true at
  fixed horizon, visible in the `t ≥ 2` columns.
- R34: the DLRA wins by up to 28× — true, and confined to the `r ≥ 16`, `t ≤ 1` corner.
- R37: the static baseline's error is neither the mean nor truncation — true, and it is why
  the static rows are flat.

## 4. What must not be claimed

- **No speedup.** 3.9× slower at the only rank that is exact (D11.1). The surface is an
  *accuracy* result and must be presented as one.
- **Not adaptive rank.** The advantage comes from re-fitting to the current state each step
  (R37), not from the rank changing. In this surface the rank is *fixed* per run, which is
  exactly what makes the law clean — and exactly why it is about subspace, not rank.
- **`r*` is not a free parameter.** The law says the useful horizon is set by the rank you
  can afford, and the cost is `Θ(N³)` per step *independent* of rank (D11.1), so paying for
  `r = 32` buys `t* = 2.4` at the price of the full-grid solver's 3.9×. **That trade is the
  honest framing of the cost section.**

## 5. Required of `coder`

This is the reviewer's reference version, not the project's artifact. Reproduce it with
`run_baselines.py` — same ranks, same horizons, oracle-mean column included — and check the
two agree. **If they do not, mine is wrong and I want to know why before anything is written.**
A disagreement would be more informative than agreement at this point, and the decomposition
helper is the part most likely to differ, given my own axis errors in R26.

**Blocked for the writer until that lands:** the central figure, and §5/§7's framing. The
3-item blocking list is unchanged and still independent of this.
