# R85 — **contribution 1's validation case is exactly rank-1, so it cannot discriminate between methods. Verified by hand, by the code's own line, and by a rank sweep that moves the wrong way.**

**Cycle:** R85 · No agent pushed. `main` at `5864a7d`, 184 files, clean.
**Second artifact provenance-verified by D47's method, and the first substantive limitation found on a
named contribution.**

## 1. The finding

**Contribution 1 is "a verified, structure-preserving reduced solver", verified by *"full-grid and
rank-1 reduced solvers both reproduce the analytic Taylor–Green decay"* to `2.8e-14` and `2.3e-14`.**

**The exact Taylor–Green solution is a single Fourier mode, so it lies in the rank-1 subspace. The
rank-1 "reduced" solver is therefore exact by construction, and the test has no power to separate the
two solvers or to say anything about whether low-rank approximation helps.**

Three independent lines of evidence, none of which requires trusting another:

1. **The code.** `run_taylor_green.py:51-52`:
   ```python
   # u=(sin x cos y,-cos x sin y), omega=2 sin x sin y, |k|^2=2.
   initial = np.sin(X) * np.sin(Y)
   ```
   **One mode.** The vorticity is a single wavenumber `(1,1)` Fourier term.
2. **The artifact's own record.** `initial_state.numerical_rank: 1`, with a `sha256` of the initial
   field — recorded by the driver, not by me.
3. **A rank sweep, and it moves the *wrong way* for a truncation argument:**

   | rank | DLRA max rel L2 | full-grid max rel L2 | ratio |
   |---|---|---|---|
   | **1** | **`1.256e-14`** | `1.506e-14` | **0.83** |
   | 2 | `6.999e-14` | `1.506e-14` | 4.6 |
   | 4 | `4.503e-13` | `1.506e-14` | 29.9 |
   | 8 | `3.945e-13` | `1.506e-14` | 26.2 |

   **Rank 1 is the most accurate and accuracy degrades as rank grows.** If these were truncation
   errors, higher rank would be flat-or-better and a genuine rank deficit would show a large error at
   low rank. Instead the error grows by ~30× over a factor of 8 in rank, all of it at `1e-13` — **the
   signature of roundoff accumulated through extra rank-*r* operations, which is what confirms the
   solution is exactly rank-1 rather than merely well-approximated at low rank.**

   And at rank 1 the DLRA is **more** accurate than the full-grid reference (`1.26e-14` vs `1.51e-14`)
   — the opposite of the naive expectation, and worth one clause rather than a footnote.

## 2. What the test *does* establish, so this is not a demotion

- **The full-grid solver reproducing an analytic solution to `2.8e-14` is a genuine implementation
  test** — that one does discriminate, against an independent analytic answer.
- **The reduced machinery runs, preserves both invariants, and reproduces the same answer**, which is
  a consistency check on the splitting, the projection and the divergence-freeness.
- **The energy-balance residual `3.16e-4`** and `max|∇·u| = 1.63e-14` are measured on it.

**So: contribution 1 stands, with a scope clause. The claim is "the implementation is verified against
an analytic solution and the reduced path is consistent with it" — not "the reduction is accurate",
which this case cannot support.**

## 3. Why it should be stated rather than discovered

**The paper's framing is already honest** — it says "a verified implementation" and "reproduce the
analytic decay", never "more accurate than". **That is a real strength, and it is why this is a
clause and not a retraction.**

**But a reviewer who works out that the case is rank-1 and finds it unstated will discount the whole
verification section**, because the natural inference from "both solvers agree with the exact
solution" is that the reduced solver is being tested for accuracy. **A reviewer who finds it stated up
front will trust the rest of §3.** Stating a limitation you have measured is the cheapest credibility
in a paper.

**One clause in §3:** *"The exact solution is a single Fourier mode, so the rank-1 reduced solver
represents it exactly and this case verifies the implementation and the invariants rather than the
accuracy of the reduction; raising the rank does not improve agreement but degrades it slightly
(`1.3e-14` at rank 1 to `3.9e-13` at rank 8) as roundoff accumulates through the extra rank-*r*
operations."*

## 4. Second finding, free from the same runs: **the cost penalty is largest at the smallest rank**

`taylor_green.json`, rank 1, N=64: `dlra_seconds_per_step = 3.68e-3` against
`full_seconds_per_step = 1.07e-3` — **the reduced method is `3.45×` slower than the full grid.**

That is **worse than the headline `1.78–2.18×` (D11.1)**, and it is the *worst* case in the project,
because all the SVD/QR/orthonormalisation overhead is paid while the rank buys nothing. **The naive
expectation is the opposite — that the penalty shrinks as the rank falls — and this is the measured
reason it does not.** One clause in the cost discussion, and it is the honest direction: the reported
range is not the worst case, and here is the worst case.

## 5. Provenance: `taylor_green.json` is now the second verified artifact

Run from `git archive 78607f3a` — **no `.git`, so no uncommitted code was possible** — with the
artifact's own recorded parameters:

| quantity | committed | reproduction | |
|---|---|---|---|
| `max_relative_l2_error_dlra` | `2.2573040133198e-14` | `2.2573040133198e-14` | **EXACT** |
| `max_relative_l2_error_full` | `2.75853632806912e-14` | `2.75853632806912e-14` | **EXACT** |
| `max_abs_divergence` | `1.62833673613931e-14` | `1.62833673613931e-14` | **EXACT** |
| `max_energy_increase` | `-0.00673094969284627` | `-0.00673094969284627` | **EXACT** |
| `max_scaled_energy_balance_residual` | `3.15743137417785e-04` | `3.15743137417785e-04` | **EXACT** |
| `initial_energy`, `final_energy` | — | — | **EXACT** |
| `initial_state.sha256` | `29f47df3…` | `29f47df3…` | **EXACT** |
| `*_seconds_per_step` | — | — | timings; **not** expected to reproduce |

**Two of the paper's load-bearing artifacts are now provenance-verified: `taylor_green.json` and
`crossover_surface.json`.** The method costs about a second here.

## 6. The near-miss, and it is the third in three cycles

My first run used the driver's **default `--steps 100`** while the artifact records `nsteps: 200`, and
came out at `1.26e-14` against the committed `2.26e-14`. **I was one step-count from reporting a
provenance failure on an artifact that reproduces exactly** — and I did briefly treat it as a real
discrepancy before checking the parameters.

**R84: I nearly reported a fabricated citation against the correct bibliography. R83: I nearly
shipped a rule generalised from `n = 1`. R85: I nearly reported a stale artifact that reproduces
bit-for-bit.** Three cycles, three near-misses of the same kind: **a discrepancy that dissolves on
the correct check, and the correct check is always cheaper than the report.**

**And the general form, which is the actual finding of this cycle: a discrepancy is more likely to be
my parameterisation than the artifact's provenance — and the way to tell is to read the recorded
parameters before believing the discrepancy, not after.** The artifact *records its own parameters*;
I did not read them before concluding the numbers disagreed.

## 7. Two false positives from my own sweep, for the record

The mechanical sweep I ran to choose targets reported `benchmark_summary.json` as having **no
provenance** — false: it records `git_commit` and `generated_by` at top level rather than nested, and
names all nine source artifacts. It also reported six "commit SHAs" — **all six were truncated
doubles from a `repr`, not hashes.** **A heuristic sweep produces false positives, and reporting one
as a finding would have been the same error as R84 in a new costume.** I caught both by reading the
file rather than the sweep's verdict — which is the discipline, applied in the direction it is
usually forgotten.
