# R50 — The central claim, settled: **`t* ≈ 0.11·r^0.95`, invariant to the baseline's window length and to a 5× change in Reynolds number. D13 was wrong. R48 was an over-correction. R39's prefactor was 2.2× too small.**

**Cycle:** R50 · **What I ran, rather than wait:** the `Re = 1000` column I called the
project's highest-value outstanding measurement, **plus the control that turned out to matter
more**, plus a window sweep. Three `run_crossover.py` invocations, ~45 min, threads pinned.
**Verdict: the law is real, its constants were wrong, and it is robust.**

## 1. The control I skipped in R48, and it was the load-bearing one

Coder's committed `crossover_surface.json` records `provenance.git_commit = 5853ba9`. The
driver changed in the *next* commit, `bc35666`, and the change was substantive:

> *"A window can hold fewer snapshots than the requested rank. **Skipping the refit in that
> case leaves the baseline stuck on whatever basis it started with, which silently turns a
> rank-`r` baseline into a rank-1 one** and makes a short window look catastrophic for the
> wrong reason."*

**So the committed artifact was produced by a driver with a bug that degrades the static
baseline, and `bc35666` fixes it.** **I printed that provenance field in R48 and did not act
on it.** I reviewed the artifact and the driver as separate objects and never asked whether
the committed driver was the one that produced the committed artifact. That is the gap, and it
is the same shape as the R48 gap (varying parameters, never varying the baseline's *strength*)
except that this time the tool handed me the answer and I read past it.

**How much it bites, measured rather than assumed.** At `W = 1.0` with stride `0.02`, the
window holds **12 snapshots at the `t=0.25` refit and 24 at `t=0.50`**, so ranks 16/32/43 were
**starved at exactly the short horizons where the DLRA's advantage is largest.** From `t ≥ 1`
the window holds ~50 and nothing is starved. The bug therefore inflated precisely the
short-horizon numbers the headline claim rests on.

## 2. The measurement, and it is invariant

`t*` = the first horizon at which a static subspace refit on a trailing window (strictly
causal, refit every `0.25`) becomes at least as accurate as the reduced integrator,
log-log interpolated. `N=64`, `A=0.2`, full-field relative L2.

| rank | R39 (my published, weak baseline) | **Re=5000, fixed driver** | **Re=1000, fixed driver** |
|---|---|---|---|
| 2 | 0.11 | `0.25` *unresolved* | `0.25` *unresolved* |
| 4 | 0.24 | `0.25` *unresolved* | `0.25` *unresolved* |
| 8 | 0.49 | **0.75** | **0.72** |
| 16 | 1.15 | **1.83** | **1.86** |
| 32 | 2.42 | **2.81** | **3.03** |
| 43 | never | **never** | **never** |

Fit over `r = 8…32`, where `t*` is resolved:

| | prefactor | exponent |
|---|---|---|
| R39 (weak baseline) | `0.0509` | `1.115` |
| **Re=5000, fixed** | **`0.1124`** | **`0.951`** |
| **Re=1000, fixed** | **`0.0915`** | **`1.031`** |

**Window invariance — the baseline's window length does not matter at all:**

| `W` | `t*` at r=8 | r=16 | r=32 |
|---|---|---|---|
| 0.5 | 0.75 | 1.83 | 2.81 |
| 1.0 | 0.75 | 1.83 | 2.81 |
| 2.0 | 0.75 | 1.84 | 2.81 |

**A 4× change in the baseline's window moves `t*` by ≤1%.** That is the robustness statement
the claim actually needed, and R39 never had it.

**Reynolds invariance — a 5× change in Re moves `t*` by 3–8%**, and the exponent moves by 8%
(`0.951 → 1.031`), consistent with the R45 leave-one-out spreads.

## 3. The claim, finally

> A rank-`r` reduced integrator integrated at **fixed** rank leads a static subspace refit on
> a trailing window for **`t* ≈ 0.11·r^0.95`** time units — **essentially linear in rank** —
> and the only rank that never yields is the **dealiasing ceiling**, where the method *is* the
> full-grid solver. The result is **invariant to the baseline's window length** (≤1% over
> `W ∈ {0.5, 1, 2}`) and **to a 5× change in Reynolds number** (3–8% over `Re ∈ {1000, 5000}`).

**The mechanism is the reason it is clean, and it is unchanged:** the static baseline's error
is nearly rank-independent — at `t = 0.1` it spans `0.3176–0.3178` across a **43-fold** rank
range — while the reduced integrator's falls with rank. The two therefore cross, and where is
set by rank alone.

**`r = 2` and `r = 4` are unresolved**, as at R39: `t* = 0.25` is the first measurable interval,
so the lowest ranks have **no measurable lead**. The fit correctly excludes them.

## 4. Three of my own statements were wrong, and only one survives

| cycle | what I said | status |
|---|---|---|
| **R39** | `t* ≈ 0.0509·r^1.115` | **prefactor 2.2× too small, exponent too steep.** Direction and the ceiling result were right. |
| **R48** | "the curves cross repeatedly, so `t*` is not well defined" | **over-correction.** True of the *buggy* committed artifact (where `r=8` reads `1.42, 1.99, 1.84, 1.21, 0.91, 0.83, 1.09, 1.04`); on the fixed driver the excursion is a single ≤17% blip at `t=6` and the crossing is essentially unique. |
| **D13** | "at `r ≥ 32` the reduced integrator wins at **every** horizon; at `r ≤ 8` it does not pay" | **flatly wrong, and it came from the buggy artifact.** On the fixed driver `r=32` yields at `t = 3, 4, 6, 8`. **Superseded by D14.** |
| **R45** | the horizon lengthens as `Re` falls | **direction confirmed** (2.81 → 3.03 at `r=32`), magnitude smaller than the weak-baseline version suggested. |

**So the law was never wrong in kind — only in its constants — and my R48 retirement of it was
based on a buggy artifact.** Two consecutive over-corrections, and both came from the same
place: **I accepted an artifact without checking which code produced it.**

## 5. Two schema findings, so this cannot recur silently

1. **The driver's output key scheme changed between the two commits** — plain rank keys at
   `5853ba9`, `W{window}_r{rank}` at `bc35666`. **The committed artifact is not reproducible by
   the committed driver without a key mapping**, which is what made this reviewable only by
   hand.
2. **`crossover_surface.json`'s `crossovers` block remains wrong** (R48): `t_star: null` and
   "DLRA still ahead at the longest horizon" for all six ranks. On the fixed driver `t*` is
   `0.75 / 1.83 / 2.81` at `r = 8/16/32` and unresolved at `r = 2/4`, so the block should
   report **three values, not six nulls**. The same "inspect only the final horizon" logic
   produces a `null` for the ranks where the crossing is real.

## 6. What the paper should now say, and what it must not

**Say:** the lead is linear in rank, `≈0.11·r^0.95`, for about `0.7` time units at `r = 8` and
`2.8` at `r = 32`; it is invariant to the baseline's window length and nearly so to Reynolds
number; the static floor is rank-independent; the ceiling is exact. **This is a better paper
than R48's version was, because it now has the robustness check that the claim needed and did
not have.**

**Do not say:** `0.05·r^1.12` (R39's constants); that the curves cross repeatedly (R48, an
artefact of a bug); that `r ≥ 32` wins at every horizon (D13, same artefact); that `r ≤ 8` does
not pay (D13 — on the fixed driver `r = 8` leads until `t ≈ 0.75`); or that `t*` at `r = 2, 4`
is resolved.

**Still no per-step speedup** (D11.1, `1.78–2.18×`), and the ceiling result is unchanged: at
`r = 43` the DLRA error runs `0.0` to `2.8e-09` across the horizons, i.e. it is the full-grid
solver.

## 7. Merge safety

No merge this cycle; the three runs wrote to `/tmp/opencode/rv/`, not to the repository. No
agent branch moved.
