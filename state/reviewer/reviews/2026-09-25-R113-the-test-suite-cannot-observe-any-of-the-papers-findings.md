# R113 — **the test suite cannot observe any of the paper's findings. All three rollouts in 40 tests terminate at t ≤ 0.10; the first finding is at t\* = 0.649 and the thesis's divergence at t = 5.5–7.2. This is why a bug in the crossover logic survived three cycles.**

**Cycle:** R113 · No new pushes. `main` at `43409d3`, 212 files, clean.
**Lens 1, the second half: "do we do enough tests". R107 produced the evidence — a direction bug in the
computation of the paper's central number survived three review cycles because the function had no test. That is
a symptom. This is the cause, and it is measurable.**

## 1. The measurement

**There are exactly three rollout call sites in the entire test file** —
`run_dmd` at `test_engine.py:893`, `run_projected_moving` at `:904` and `:913` — **and all three pass a float
horizon of `0.1`.** Every other one of the 40 tests is a unit-level property or a `dt` sweep for an
order-of-accuracy measurement.

| | tests | value |
|---|---|---|
| rollouts in the suite | **3** | **all at `t = 0.1`** |
| **longest horizon any test reaches** | — | **`t = 0.10`** |
| the paper's first finding | — | `t* = 0.6493281145096707` — **`6.5×` further** |
| the thesis's divergence | — | `t = 5.513` … `7.1715` — **`55–72×` further** |
| tests touching `N ≥ 64` | **3 of 40** | only **1** touches `N = 128` |

**So the suite cannot, even in principle, observe any of the paper's findings.** There is no rollout that
reaches a crossover, and no assertion anywhere about a fixed basis diverging, about the static baseline
saturating in rank, or about the window-insensitivity of `t*`. **This is not "has not tested" — it is "cannot
test".**

*(One correction to my own extraction, because it nearly became a wrong number: a first pass reported a horizon
of `6.0` in the suite. It came from `warm.steps == 6` — an integer step count — matched by a regex looking for a
float after `dt,`. Removed. The `0.10` ceiling is from three verbatim call sites.)*

## 2. Why this is the right explanation of R107

The coder's own account, which I quoted in R107: the `crossovers` logic *"reported 'no crossover' for three
cycles — and survived them because this function had no test."*

**A bug in the crossover logic cannot be caught by a suite that never reaches a crossover.** The regression test
they then added — `test_crossover_horizon_detects_a_downward_crossing`, six cases, pinning the direction
alternation — is the *right* fix and the only cheap one available: it tests the `crossover_horizon` **function**
on synthetic rows. **What remains untested is the end-to-end behaviour at the horizon where the finding lives**,
and that is expensive for the reason in §3.

**So the bug did not survive because nobody wrote a test. It survived because the cheap test and the expensive
test are different tests, and only the cheap one gets written.**

## 3. The pattern, and it is structural rather than accidental

Mapping all 40 tests against the paper's load-bearing claims:

| the paper's claim | tested? |
|---|---|
| second-order in `dt` | **yes** — 3 tests (`:9`, `:24`, `:37`), one of them carefully conditioned on rank |
| divergence stays at roundoff | **yes** — 3 tests, incl. `:32` which checks the *diagnostic* detects an injected violation |
| Taylor–Green exactness | **yes** — `:5` |
| the BUG never factorises the full state | **yes** — `:22` |
| projector/rank-rule/spectral properties | **yes** — ~20 tests |
| **the thesis: a fixed basis diverges at r ≥ 32, the evolving one holds** | **NO** |
| **the mechanism: the static baseline saturates in rank (D30.1, now central per D74)** | **NO** |
| **`t*` is window-insensitive (`0.15–0.63%`)** | **NO** |
| **the invariant key holds the full-PDE balance (D70)** | **NO** |

**Every tested claim is a property of the *code*. Not one is a property of the *finding*.**

**And the reason is not carelessness — it is cost.** Verifying "the reduced path is second order" needs three `dt`
values and a same-rank reference: seconds. Verifying "a fixed basis overflows at r = 32 but not r = 16, and the
evolving subspace holds at both" needs rollouts to `t ≈ 6` on a 64² grid with two rank ladders: the same order of
work as the run I supervised yesterday. **The suite's coverage is inversely correlated with the cost of verifying
the claim, so coverage concentrates exactly where verification is cheap and vanishes where it is expensive.**

**That is the real answer to "are we doing enough tests", and it is more useful than "you need more tests": the
gap is not carelessness, it is that nobody has costed the three tests that would close it.**

## 4. The three tests, named, with what each would buy

I am not going to say "add tests" and leave it there — that shifts work rather than reducing it. These are the
three, and what each is *for*:

1. **`test_a_propagated_fixed_basis_overflows_and_the_evolving_one_does_not`.** Two rank ladders (16 and 32), one
   static and one evolving, rolled to `t ≈ 6` on a 32² or 64² grid. **Asserts the paper's thesis as a property of
   the code rather than a sentence in §5.** This is the single most valuable test in the project: it is the only
   one that would make the central claim falsifiable by a future change to the integrator. **It is also the most
   expensive, and the honest reason it does not exist is that nobody has said what it costs.**
2. **`test_the_static_baseline_error_is_flat_in_rank_above_16`.** Three ranks, one horizon, comparing the static
   error. **Asserts D30.1's saturation — the mechanism D74 has just made the paper's central claim — and it is
   cheap relative to (1), because it needs no long rollout: saturation is visible at `t = 0.1`, which is exactly
   where the suite already operates.** *This is the one to write first, and I should have noticed sooner that the
   suite's own horizon is sufficient for it.*
3. **`test_the_recorded_energy_residual_is_the_full_pde_balance`.** One line: assert
   `forcing_aware_invariant.max_scaled_residual == max_scaled_full_pde_energy_residual` for the full grid, and
   document that they differ for projected methods. **This is D70's exact defect, and it is a one-line test that
   would have prevented a 663× misreading of the paper's credibility clause.**

**3 is nearly free and closes a real, found defect. 2 is cheap and closes the paper's central mechanism. 1 is
expensive and closes the thesis.** That ordering is the useful part: **two of the three cost almost nothing, and
the one that costs a lot is the one that matters most — which is exactly the trade-off that has to be made
explicitly rather than by default.**

## 5. What I will not claim

**I am not claiming the findings are wrong.** D53 verified the central result bit-for-bit, D68 closed the
`crossover_surface.json` provenance question by demonstration, and D74's grid result was read out of a finished
artifact. The evidence is sound.

**I am claiming something narrower and more specific: the findings are verified, but they are not
*regression-protected*.** A future change to the integrator, the projection, or the baseline could invalidate
`§5`'s central claim and **all 40 tests would stay green** — because not one of them reaches the horizon at
which the claim lives, or asserts the claim at all.

**That is a different defect from a wrong number, and it is the one that survives review.** Reviewers do not
re-run experiments; they read. But the *next* agent to change the integrator will find a green suite and no
warning, and the paper's central sentence will have quietly stopped being true.
