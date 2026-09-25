# R25 — Contract audit of `solvers/`: the engine is sound, the POD bug is not a small one, and `DLRA` does not reset

**Cycle:** R25
**Origin:** R24 ended with the rule *"before investigating why a component behaves
oddly, confirm that it computes what it claims to."* R24 had applied that to
`PODGalerkin` alone. R25 applies it systematically, to every public method in
`solvers/`.

**Result in one line: 13 of 15 contracts pass, the single real failure is the R24
reshape — and its error is larger than returning the zero field — and a second real
defect surfaced in `DLRA.initialize()`.** Four of the five apparent failures were
defects in my own checks, which is the same failure mode R24 documented, one level
down.

---

## 1. The audit

Fifteen contracts, each built from the code's own definitions rather than from an
independent reimplementation where possible, so that the check tests the claim
rather than my guess at it.

| # | Contract | Result |
|---|---|---|
| 1 | `curl(velocity(ψ)) == vorticity(ψ)` | PASS `1.4e-14` |
| 2 | `inv_lap(-lap(f)) == f` (mod constant) | PASS `6.4e-15` |
| 3 | `lap(f) == -k²·fft(f)` (half-spectrum) | PASS `0.0` |
| 4 | `ke == ½∫|∇ψ|²` | PASS `0.0` |
| 5 | `enstrophy == ½∫ω²` | PASS `0.0` |
| 6 | **`div(velocity(ψ)) == 0`** (the paper's invariant) | **PASS `5.8e-15`** |
| 7 | `max_div_velocity(ψ) == max\|div u\|` | PASS `2.9e-16` |
| 8 | `KolmogorovForcing: (χ_y, −χ_x) == f` | PASS `2.0e-15` |
| 9 | `KolmogorovForcing: vorticity() == curl f` | PASS `2.1e-15` |
| 10 | `diffuse == exp(−νk²t)·fft` (exact heat semigroup) | PASS `0.0` |
| 11 | `SVDProjector.project` at full rank `== identity` | PASS `1.3e-15` |
| 12 | `SVDProjector.project` is idempotent | PASS `2.0e-15` |
| 13 | **`PODGalerkin.project(own training snapshot) == it`** | **FAIL `1.190`** |
| 14 | `fit_pod == PODGalerkin().fit()` | PASS `0.0` |
| 15 | `DLRA.integrate() == 5 × step()` | PASS `0.0` |

**The headline invariant holds.** `div(velocity(ψ)) = 5.8e-15`, and
`max_div_velocity` agrees with the directly computed divergence to `2.9e-16`. The
exact-divergence-free claim in the paper is real, and it is real *in the code*, not
only in the argument. That is worth stating plainly because it is the one claim in
`AGENTS.md` that everything else has been crowding out.

## 2. The POD failure is not a small one

R24 established the mechanism (a wrong reshape) and showed that fixing it makes the
baseline exact. R25 quantifies how wrong the current code is, which R24's committed
configuration did not:

| fitted rank | rel. error of `project` on each of its **own 8 training snapshots** |
|---|---|
| 4 | **1.542** |
| 8 | **1.124** |
| 20 | **1.124** |

For scale: the relative error of returning the **zero field** is `1.0`. The fitted
POD projector is **worse than discarding the state entirely**, at every rank, and
`SVDProjector` at full rank on the same data returns `0.0`. There is no rank at
which the current `PODGalerkin` does anything useful. This is not a precision
issue to be tuned; the object is not a projection of the data it was fitted on.

## 3. A second real defect: `DLRA.initialize()` does not reset a warm object

Not previously recorded. Measured with fresh objects on both sides:

```
DLRA.integrate() vs 5x step(), fresh objects:  maxerr = 0.000e+00   -> identical
after a prior run, initialize() then 5 steps vs a fresh DLRA:  maxerr = 4.323e-01
```

`DLRA.initialize()` resets some state and not all of it, so a `DLRA` that has
already run carries its learned projector basis and step counter into the next run.
**Any experiment script that reuses a `DLRA` object across runs is silently wrong**,
and produces a plausible-looking trajectory that is not the trajectory the object's
configuration describes.

This matters here more than it would in an ordinary codebase, because the project's
whole comparison methodology is *matched configurations across ranks and across
runs*. A harness that reuses one object across a rank sweep would produce a rank
sweep in which later ranks silently inherit earlier ranks' state. Nothing in the
committed drivers does this today — I checked, and the committed runs are unaffected
— but the hazard is live and the fix is cheap: either reset the projector state in
`initialize`, or document that `DLRA` is single-use and construct one per run.

It is also the second instance in two cycles of the same shape: **a silent wrong
answer where an exception or an obvious impossibility would have been better.**
R24's reshape, R25's warm state. Both would have been caught by the same discipline —
construct the object fresh, and check the output against a case whose answer is known.

## 4. Four of five apparent failures were my own checks

This is the part worth recording honestly, because it is the same mistake R24
documented and I made it again, immediately, in a different form.

| apparent failure | what was actually wrong |
|---|---|
| `div(velocity(ψ)) == 0` failed, `8.1` | `u, v = velocity(ψ)` gives two arrays; I then used `u[0]` and `u[1]`, which are **rows of the u-array**, not the velocity components. A 1-D length-`N` input broadcasts against `kx[:,None]` without error. |
| `(χ_y, −χ_x) == f` failed, `0.7` | I compared `[∂_x χ, −∂_y χ]` against `(f_x, f_y)`. The identity is `[∂_y χ, −∂_x χ]`. The error was exactly `0.7 = A`. |
| `DLRA.integrate() == 5×step()` failed, `0.432` | I reused **one** `DLRA` for both runs, so the second started warm — my own bug from §3, caught by it. And I omitted `t`, which `integrate` passes and my loop did not. |
| `ke == ½·L²/N²·Σ\|∇ψ\|²` failed, `22.2` | A deliberately malformed line I left in (`l2_sq(np.zeros((1,1)))*0`). The correct integral form, on the next line, passes at `0.0`. |

Each was caught only after reading the source, and after adding a **harness
self-validation**: a finite-difference curl that must converge as `N` grows. It does
(`0.312 → 0.150 → 0.0723 → 0.038` at `N = 32, 64, 128, 256`), which is what
established that the first version's `0.83` was truncation error and not a code
defect — the initial version of that check used full `fft2` against a half-spectrum
`k2` and did not even run.

**The rule this produces, now binding as CHECKLIST §1.4:** a check that disagrees
with already-tested code must be shown to converge, or shown to agree on a case
whose answer is known, **before** the disagreement is treated as evidence. R24's
version of the rule was "test the check first"; R25 shows that testing the check is
not a formality, it is where the work actually is. In R25 the check was wrong four
times in a single script.

## 5. A minor documentation gap, recorded not charged

`make_initial_state(..., cutoff=c)` yields an initial state whose largest populated
wavenumber is `2 → 2`, `4 → 5`, `8 → 11`. That is not a single obvious rule, and the
committed runs use `cutoff=8`. This does not affect any committed result — the IC's
rank (17) and the rank ceiling (`2·floor(N/3)+1`, R11) were both measured directly
rather than inferred from `cutoff` — so I am recording it as an undocumented detail
rather than a defect. The mask semantics should be stated in the docstring and
pinned by a test, because "band-limited to cutoff 8" currently means something a
reader would not guess.

## 6. What this changes, and what it does not

**Unchanged.** D11 in full. The R14 six. "POD is 159× worse" remains struck. F5
remains downstream of the regime decision (R24). The engine approval from R5 stands,
and R25 strengthens it: the thirteen passing contracts include every operator, every
invariant, and both projection APIs.

**Added.** CHECKLIST §1.4 now carries three items from this cycle: fit-reproduces-
its-own-input; no warm-object reuse; and validate an independent check before
believing a disagreement with tested code.

**The net position is better than R24 implied.** R24 found a bug and, in the same
breath, reported that the experiment is too easy to say anything. R25 says the rest
of the engine is sound and the headline invariant is exact. The project's difficulty
is not a broken engine. It is that at `t ≤ 0.1` a rank-1 POD solves the problem, and
that the paper has to be about something else.
