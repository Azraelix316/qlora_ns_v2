# R66 — **the project's strongest positive result is unremarked in a committed artifact: a fixed-basis projected static POD run diverges to overflow at `r ≥ 32`, and the structure-preserving DLRA does not.**

**Cycle:** R66 · No agent pushed. `main` at `5b92b5e`, 167 files, clean.
**Applying R65's rule to a *supporting* claim rather than a structural one — and it is the most
consequential thing I have found for the paper's framing.**

## 1. The finding

`state/coder/results/baselines_re5000_N64_T8.json` (`Re=5000`, `N=64`, `T=8`, `A=0.2`) records
**sixteen methods. Four of them diverge to floating-point overflow, and none of them is a DLRA
run.**

| method | outcome | died at | `max\|∇·u\|` | final trajectory error |
|---|---|---|---|---|
| `pod_early_r32` | **diverged** | `t=6.96` | `4.6e+64` | 6.31 |
| `pod_early_r42` | **diverged** | `t=5.74` | `3.8e+199` | 4.05 |
| `pod_late_r32` | **diverged** | `t=5.51` | `7.1e+278` | 42.52 |
| `pod_late_r42` | **diverged** | `t=7.17` | `2.0e+182` | 11.94 |
| `dlra_fixed_r32` | stable | — | `9.4e-14` | 0.652 |
| `dlra_fixed_r42` | stable | — | `7.6e-14` | 0.510 |
| `dlra_fixed_r16`, `dlra_fixed_r1`, `dlra_adaptive` | stable | — | `≤1.1e-13` | `0.51–1.09` |
| `full_grid` | stable | — | `7.6e-14` | 0 |
| `pod_early_r16`, `pod_late_r16`, `pod_early_r1`, `pod_late_r1` | stable | — | `≤2.0e-13` | `0.47–1.18` |
| `pod_dmd_r32` | stable but **degraded** | — | `1.05e-11` | **60.69** |
| `pod_moving_r1` | stable | — | `6.5e-14` | 0.398 |

**So: fixed-basis static POD is stable at `r ≤ 16` and does not survive to `T=8` at `r = 32` or
`42`, for both an early and a late window. The structure-preserving DLRA is stable at every rank,
with a divergence at roundoff and a trajectory error under `1.1`.**

## 2. I checked whether this is a harness artefact, and it is not

This is the check that matters, because "the baseline blew up" is exactly the kind of claim a
referee discounts as a bug.

- **Same code path.** `run_projected` is documented as *"a projected run: static POD or fixed-rank
  DLRA share this path"*, and both call `model.step(old, dt, t=..., projector=projector)`. **The
  integrator, the splitting and the projection application are identical.** Only the subspace
  differs — fixed versus time-dependent.
- **The basis is orthonormal.** `PODGalerkin(grid, rank).fit(early_snaps)` is an SVD basis, so
  there is no conditioning defect to blame.
- **Coder already knew and coded for it.** `run_projected`'s docstring says: *"A baseline that goes
  non-finite is a **result**, not a harness failure: it is recorded with the step it died at and
  the time it reached... Aborting the whole comparison because one baseline diverged would discard
  every other method's numbers, and 'POD is worse' is not a citable claim unless the divergence is
  itself reported (R24's lesson)."*

**So the divergence is a recorded, deliberate result with the right caveat attached — and it is
absent from the paper.** The mechanism is the paper's own thesis: a fixed subspace is not invariant
under the nonlinear term, so projecting every step injects error that accumulates, while a
time-dependent subspace — refitted (static) or evolved (DLRA) — does not.

## 3. The caveats, which are substantial and which I am not going to soften

- **It is ONE artifact at ONE parameter set** (`Re=5000`, `N=64`, `T=8`, `A=0.2`). **It does not
  replicate, because there is nothing to replicate against** — `baselines_*.json` contains exactly
  one file. **This cannot be a paper claim yet.**
- **The divergence time is NOT monotone in rank**, so there is no clean instability-growth story to
  tell: `pod_early_r42` dies at `t=5.74`, *before* `pod_early_r32` at `t=6.96`, while
  `pod_late_r42` dies at `t=7.17`, *after* `pod_late_r32` at `t=5.51`. **The honest statement is
  the weak one: at `r ≥ 32`, with these windows, the fixed-basis projected run does not survive to
  `T=8`.** I will not dress that as a scaling law.
- **It is specifically *propagated fixed-basis* projection that fails.** `pod_dmd_r32` is stable,
  though degraded (`60.7` error, `1.05e-11` divergence), and the *refitted* moving-window baseline
  is stable. So the claim is not "static POD fails" — it is "**a fixed** subspace, propagated, does
  not survive at high rank".
- **It does not touch the crossover result.** That comparison's baseline is the *refitted*
  moving-window one, which does not diverge. The two results are complementary, not in conflict.
- **A referee will ask whether the DLRA is "the same method" at `r=32`.** It is the same integrator
  with a *time-dependent* subspace. **So the claim must be framed as the distinction between a fixed
  and a time-dependent subspace — in stability terms, not accuracy terms.**

## 4. Why this matters more than anything else I have found for the paper

The paper is currently organised around a **methodological** contribution (the crossover horizon is
baseline-conditional) plus a list of things it cannot claim: slower per step, more memory, no
turbulence validation, no adaptive rank, no fitted law. `AGENTS.md` describes the intended
contribution as *"DLRA with a structure-preserving split that enforces exact divergence-freeness"* —
and **the evidence for that is the one result nobody has written up.**

**The framing this supports is both more intuitive and better evidenced than the one the paper is
built on:**

> **A reduced solver is only viable if its subspace evolves.** Propagating a fixed low-dimensional
> basis through the nonlinear dynamics — even with the same structure-preserving integrator, the
> same splitting, and an orthonormal basis — is stable at rank 16 and does not survive to `t = 8`
> at ranks 32 and 42, where it overflows. The same integrator with a time-dependent subspace, either
> refitted or evolved, stays at roundoff divergence with a trajectory error below `1.1` throughout.
> **What rank buys is not accuracy but the ability to run at all.**

**And it offers a legitimate route to the framing `AGENTS.md` wants without the barred claim.** The
project cannot say *"adaptive rank"* (D4/D12 bar it, and `rank_policy: "fixed per run"` in every
artifact). **But "the subspace must evolve, and here is what happens when it does not" is a
different, supportable, and considerably more compelling statement** — and it is a *stability*
result, which is a far more natural fit for a scientific-computing venue than a crossover
sensitivity.

## 5. The sweep that would make it citable, and it is cheap

`run_baselines` already does everything needed. **Re-run it over `Re ∈ {1000, 5000}`,
`N ∈ {64, 128}`, `T ∈ {8, 20, 40}`, `r ∈ {16, 24, 32, 42}` with both window placements, and report
the divergence time per configuration.** That answers the three questions this observation raises:
does the threshold depend on `Re`? on resolution? and **does the divergence time fall as `T` grows,
or is `T=8` simply where it happens to appear?** The third is the one that decides whether this is
a real instability or a coincidence of the horizon.

**Until that sweep exists, the paper may state this as an observation in §7 (limitations/setting)
with the artifact cited, and not as a contribution.**

## 6. The lesson, and it is the mirror of R65's

R65 caught me asserting a mechanism I had never tested. **R66 catches the opposite failure: a real,
recorded, well-caveated result sitting in a committed artifact that nobody — including me, across
sixty-six review cycles — has surfaced, because the paper was being organised around a different
contribution and I was auditing the claims rather than the artifacts.**

**Auditing a claim means asking what would falsify it. Auditing an artifact means asking what it
would support.** I did the first for twenty cycles and not the second. **A committed artifact whose
docstring says "this is a result, not a harness failure" is telling you it is a result — and the
reviewer's job is to notice that the paper does not contain it.
