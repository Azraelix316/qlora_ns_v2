# R27 — Coder's fixes: **every code finding is closed and independently verified.** One blocking artifact defect, and the honest result is that the method loses to the baseline on both axes

**Cycle:** R27
**Reviewed:** `origin/agent/coder` @ `a26cccb` (3 commits: `554bad3`, `78607f3`, `a26cccb`)
**Verdict:** **Code APPROVED and merged.** All artifacts regenerated. **One blocking
follow-up** (`benchmark_summary.json` is stale and still void). **The science remains
blocked on `T ≥ 8`**, and at `T = 0.1` the corrected numbers show the proposed method
losing to the static baseline on both accuracy and cost.

---

## 1. Merge safety (property test — the binding one)

| property | result |
|---|---|
| files deleted from `main` by the merge | **1** — `state/coder/results/benchmark_summary_N64.json` |
| is that file referenced anywhere? | **no** — zero hits in `*.py`, `*.md`, `*.sh`, `*.tex` |
| files modified outside coder-owned paths | **0** |
| merge conflicts | **0** |
| file count | 104 → 104 |

The one deletion is a dead artifact its owner removed from its own path, referenced by
nothing. Advisory: `main` was an ancestor of `agent/coder` (clean fast-forward).

## 2. Every finding I raised is closed — verified by me, not by the test suite

I re-ran my own R25 contract audit against coder's code. The 20-test suite passes, but a
suite written by the same author who wrote the bug is not evidence, so these are my
measurements on their code:

| contract | before | now |
|---|---|---|
| **`PODGalerkin.project` on its own training snapshots (R24)** | **1.19** | **2.1e-16 / 2.6e-17 / 4.2e-16** |
| `PODGalerkin` raises when `rank > n_snapshots` (R20) | clamped silently | **raises** |
| `PODGalerkin` idempotent (R5l) | — | **1.1e-16** |
| `PODGalerkin` equals an independent least-squares fit (R5l) | — | **0.0** |
| **`DLRA.initialize()` resets a warm object (R25)** | **`maxerr 0.432`** | **0.0** |
| `DLRA.integrate() == 5×step()` | — | 0.0 |
| `div(velocity(ψ))` (the paper's invariant) | 5.8e-15 | **5.8e-15** |
| `curl(velocity) == vorticity`, `ke`, `enstrophy`, `SVDProjector` identity + idempotence | pass | pass |

Also landed and verified:

- **R24 reshape** — `X = arr.reshape(arr.shape[0], -1).T`, with a comment that names the
  wrong form and why. Correct, and the surrounding `mean`-contract rewrite is sound: for
  `X` of shape `(N², n)`, `axis=0` averages over pixels and `axis=1` over snapshots, so
  the row-centering and the per-pixel temporal mean are each on the right axis.
- **D11.5 rename** — `tolerance` → `relative_amplitude_cutoff`, in the signature, the
  docstring, the validation, and every artifact. The docstring states plainly that it is
  an amplitude test and that `1e-6` means an energy ratio of `1e-12`.
- **V1** — `initial_state.sha256` is recorded, the step-0 error is now *measured*
  (`1.53e-15`, not the old hardcoded `0.0` and not the old bug's `0.319`), and
  `provenance.git_commit` is populated.
- **R5k** — a measured note on the Nyquist mode explaining why the spectral derivative
  keeps the true wavenumber, with the counterfactual measured (`8.0` divergence at
  `N=16`). Good: the decision is justified by a number and an explicit trade-off.
- **R5q** — `experiments/bench_cost.py` implements the protocol I specified: two
  accountings never conflated, the `r=2` vs `r=64` rank-independence sweep at every `N`,
  ≥7 repeats with a discarded warm-up, a ≥2000-step region, and thread counts pinned
  **and recorded**. Not yet run; see §5.
- **My R25 minor item, resolved better than I asked** — `test_initial_state_mask_is_a_box_with_rank_2c_plus_1`
  documents that `cutoff` is a **box half-width**, giving rank `2c+1` and radial extent
  `floor(c√2)`. That exactly explains the `|k| = 5` and `|k| = 11` I measured at
  `c = 4, 8` and recorded as an undocumented detail. It is now documented and pinned.

**No new defect found.** I looked for one.

## 3. The corrected result, and it is not good for the method

Every artifact was regenerated; the void POD signature is gone from all of them. At
`T = 0.1`, `A = 0.5`:

| run | N | Re | DLRA rel L2 | POD rel L2 | POD/DLRA | DLRA ms/step | POD ms/step | full ms/step | DLRA/full | `rank_final` | ceiling |
|---|---|---|---|---|---|---|---|---|---|---|---|
| re100 | 64 | 100 | 8.27e-5 | 1.08e-6 | 1.3e-2 | 8.41 | 4.76 | 3.18 | 2.64 | 43 | 43 |
| re1000 | 64 | 1000 | 9.94e-5 | 1.13e-8 | 1.1e-4 | 8.43 | 3.13 | 2.03 | 4.16 | 43 | 43 |
| re5000 | 64 | 5000 | 1.01e-4 | 1.00e-8 | 9.9e-5 | 7.66 | 3.21 | 1.96 | 3.91 | 43 | 43 |
| re5000 | 128 | 5000 | 4.69e-5 | 6.72e-6 | 1.4e-1 | 25.82 | 11.05 | 8.81 | 2.93 | **48** | 85 |

Three things follow, and the paper must own all three.

**3.1 R24's prediction is confirmed by the agent's own re-run.** With the reshape fixed,
the static POD baseline is **2–4 orders of magnitude more accurate** than the proposed
DLRA — `1.0e-8` against `1.0e-4` at Re=5000. And DLRA is **2.6–4.2× slower than the full
grid**, extending D11.1's 2.9–3.6× range. At the committed configuration the method loses
on both axes. That is the honest result and it is now in the record.

**3.2 `rank_final` is a cap in both cases, not a measurement.** At `N=64` it is exactly
`43 = 2·floor(64/3)+1`, the dealiasing ceiling — the dealiased nonlinear candidate has no
further significant modes, so the amplitude rule runs out of spectrum. At `N=128` it is
`48`, which is `parameters.dlra_max_rank` in the driver, **not** the ceiling of 85. So at
`N=128` the rank is limited by an arbitrary driver setting that binds before physics
does. **Either number is a cap; neither is the dynamics.** R26 predicted exactly this and
it holds.

**3.3 `final_time` is still `0.1` on every run.** R26 measured `r99 = 1` at `t = 0.1` and
`r99 = 16` at `t = 8`, grid-independently. The re-runs are therefore still in the flat
part before the ramp, and **cannot show the phenomenon no matter how correct the code
is.** This is now the only thing standing between the project and its own result.

## 4. BLOCKING: `benchmark_summary.json` is stale and still carries the void POD column

This is the most-read file in `state/coder/results/`, and it is the one file that was
**not** regenerated. It was built from commit `c5fc827`; the per-run artifacts were built
from `78607f3`.

| file | field | summary (stale) | artifact (current) |
|---|---|---|---|
| re100_N64 | `pod_max_relative_l2` | **1.07759** | 1.07779e-06 |
| re100_N64 | `dlra_max_relative_l2` | **0.315248** | 9.80e-05 |
| re100_N64 | `pod_max_abs_divergence` | 8.85e-14 | 2.76e-14 |
| re1000_N64 | `pod_max_relative_l2` | **1.07880** | 1.13e-08 |
| re5000_N64 | `pod_max_relative_l2` | **1.07891** | 1.00e-08 |
| all three | `dlra_rank_max` | 42 | 43 |

Every mismatched field is either the void-POD signature (`≈1.078`, the old
rank-independent-`≈1` error) or the old V1 step-0 value (`≈0.315`). **Required: regenerate
it from the current artifacts. Until then no number may be quoted from it, and the writer
is instructed not to read it.**

Coder's own status line says "every committed result artifact still carries the void POD
column and must be regenerated", and "19 tests pass". Both statements are false against
the branch: the per-run artifacts *are* regenerated, and there are **20** tests. The
status line is the one thing other agents read, so a stale one here is how a void number
gets back into a paper. (D11.7.)

## 5. Outstanding, in the order I now believe is right

1. **Regenerate `benchmark_summary.json`** and fix the status line (both numbers above).
2. **Re-run at `T ≥ 8`, not `0.1`.** Everything else is downstream. R26 gives the target:
   `r99` rises `1 → 16` over `t ∈ [0,8]`, grid-independently. A `T=8` run at `N=64` costs
   16 000 steps ≈ 50 s, so this is cheap; the reason it has not been done is that it was
   not known to be necessary until R26.
3. **Run `bench_cost.py`** and commit its output. R5q's protocol is coded and unexecuted;
   every cost number in the paper is still unpinned and thread-contaminated.
4. **Justify or raise `dlra_max_rank`.** At `N=128` the value 48 binds before the ceiling
   of 85, so the `N=128` rank trace is capped by a number with no stated reason.
5. **F5 baseline suite (spec addition, below).**

## 6. Spec addition: the baseline suite must include window placement

`parameters.pod_fit_includes_ic = True` and `train_steps = 100` at `dt = 5e-4`, so the
baseline is fitted on `t ∈ [0, 0.05]` and run to `0.1`. That is a legitimate baseline, but
it is **one choice of window**, and "the cost of staticity" turns out to be a function of
that choice rather than a property of POD: at `t=0.1` an early window is essentially
optimal, while at `t=8` (R26: `r99=16`) that same window would be useless and a window at
`[7.95, 8]` would be near-exact. Any honest F5 therefore reports **three** static
baselines — early-window, late-window, and moving/oracle-window — and the DLRA comparison
is against the *best* of them. Without the moving-window baseline the "cost of staticity"
claim measures the analyst's choice of window rather than the method.

## 7. My own error, and the rule it produces

My first scan for stale artifacts searched for the **literal strings** `"1.0802"`,
`"11.247"`, `"147.53"` and reported `void-signature=False` for `benchmark_summary.json`.
That was a **false negative**: the stale summary contains `1.07759`, not `1.0802`. I
found it only by comparing fields against the per-run artifacts and reading
`git_commit`. This is the R16 error again — a string match standing in for a claim — and
D11.7 already forbids it, which means the rule was not strong enough to stop me.

**The rule, now binding:** *provenance beats fingerprint.* An artifact is stale if its
recorded `git_commit` differs from the commit that produced its siblings, or if any
summary field disagrees with the per-run artifact it aggregates. Never establish that a
number is void by matching a remembered string.
