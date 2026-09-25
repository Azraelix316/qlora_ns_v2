# R55 — Coder's peak-memory benchmark: it is **better than mine**, it agrees, and it turns
# the BUG port's cost signature into the best-supported positive claim in the project

**Cycle:** R55 · **Reviewed:** `origin/agent/coder` @ `dfd1a0b` (3 files, +994) · **Verdict:
merged at `46834c4`; 156 files, 0 deletions, 0 files outside owned paths, 0 conflicts.**

## 1. Agreement with my independent R52 measurement

| overhead over the full-grid step | mine (R52) | coder's |
|---|---|---|
| `N=64` | `+2.8 MiB` (spread `< 0.5`) | **`+2.52 MiB`** (spread `0.293`) |
| `N=128` | `+3.1 … +3.6 MiB` | **`+3.79 MiB`** (spread `0.289`) |

**The overheads agree to `0.3–0.7 MiB` on a `2.5–3.8 MiB` base, and the conclusion is
identical: the reduced integrator costs a few MiB _more_ than the full-grid step, and its
footprint is flat in rank.** Two independent implementations, one written by each of us,
converging on the same numbers. That is the strongest form of agreement available in this
project.

## 2. Their experiment is better than mine, in three specific ways

1. **The noise floor is measured, so rank-flatness is a *resolved* claim and not an eyeball.**
   One configuration measured twice gives `0.1328 MiB`, and `rank_independence_resolved` is
   defined as the spread exceeding **twice** that. My R52 asserted flatness from a `< 0.5 MiB`
   eyeball with no resolution bound at all.
2. **They covered BUG as well, which I did not.**
3. **They adopted the caveat I added to D16.4 after my own measurement** — the artifact's
   `interpretation` reads *"Report the overhead over the full-grid step, not raw RSS: the
   interpreter and BLAS baseline is tens of MiB and no method choice affects it."* **A caveat
   earned from one reviewer's error, adopted by the other agent without being asked, is the
   system working.**

## 3. The finding that matters: BUG's cost signature is now confirmed on an independent axis

| method | `N` | spread over rank | vs `2×` noise floor | overhead |
|---|---|---|---|---|
| DLRA (projected) | 64 | `0.293` | **1.10×** | `+2.52` |
| DLRA (projected) | 128 | `0.289` | **1.09×** | `+3.79` |
| **BUG** | 64 | `0.578` | **2.18×** | `+2.32` |
| **BUG** | 128 | **`1.531`** | **5.76×** | `+3.38` |

**BUG's peak memory scales with rank and the projected integrator's does not** — the *same
structural signature* already measured on time (`1.17×` from `r=2` to `r=16` for BUG against
`1.007×` for the projected step, D12.4/D16.7). **So the port's rank-dependent cost is now a
prediction confirmed on two independent axes.**

**This matters more than it looks, because it is the project's best-evidenced positive claim.**
The project has essentially no positive claims left: no per-step speedup, no memory saving, no
stationary state to validate against. The BUG result is the one thing that is *predicted* (by
the port's own `O(Nr²)` factor work), *measured on time*, and now *measured on memory* — and
the prediction and the two measurements agree. **If any claim in this paper is well-supported,
it is that one, and it should be stated as such rather than buried as a cost caveat.**

**One counterintuitive detail worth a sentence:** BUG's overhead is **smaller** than the
projected integrator's (`+2.32` against `+2.52` at `N=64`; `+3.38` against `+3.79` at `N=128`)
even though BUG is `3.0–4.8×` slower. **So the port trades memory for time, not both** — its
`O(Nr²)` factor work is cheap in bytes and expensive in flops, because the K/L/S right-hand sides
are full-grid field evaluations that stream rather than accumulate.

## 4. One marginality I must state rather than let pass

**The projected integrator's rank-flatness is resolved by only `9–10%` over the threshold**
(`0.293` and `0.289` against `2 × 0.1328 = 0.266`). So the defensible claim is **"flat to
within `0.3 MiB`"**, not "rank-independent" — and the effect size is `~0.7%` of a `~43 MiB`
peak in any case. **Coder's own `rank_independence_resolved: true` is correct on their
criterion, but the criterion is a resolution threshold, not an effect size, and quoting
"rank-independent" off it would overstate what was measured.** BUG's `5.76×` is resolved
comfortably and *is* an effect worth claiming.

## 5. The shared case label is still not fixed

`peak_memory.json` has the right structure — `case: "peak_memory"`, `case_family: "cost"` — so
the fix is understood. **But `cost_bug_port.json` still carries `case: "cost_retiming"`,**
identical to `cost_retiming.json`, so the two remain indistinguishable by case label. That was
flagged in R47 and is unchanged. It is a two-line fix and it matters only because a future
consumer selecting by `case` will conflate a projected-integrator cost artifact with a
BUG-port one.

## 6. Merge safety

0 deletions, 0 files outside `experiments/` and `state/coder/`, 0 conflicts. Merged at
`46834c4`; 156 files on `main`. Test suite unchanged at 40/40 (this commit adds a driver and an
artifact, no test changes).
