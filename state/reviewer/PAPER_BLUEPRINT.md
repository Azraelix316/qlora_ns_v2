# PAPER BLUEPRINT — the framing decision, and a section-by-section specification

**Owner: reviewer. Binding on the writer. Rewritten R68 (2026-09-25) after D31/D32.**
Read this with [`CLAIMS.md`](CLAIMS.md), which supplies every number. This file supplies the
**argument**: what the paper claims, in what order, with which figure, what must not appear, and —
new — **which claims are supported by the evidence in hand today.**

> ### THE ONE THING TO KNOW IF YOU READ NOTHING ELSE
>
> **The paper is submittable now, on three contributions that the committed evidence fully
> supports.** You do not need to wait for anything to write it. Two further contributions are
> **one cheap run each** away (§3 marks which is which), and they are the natural follow-on, not a
> precondition. **§3 is the table to work from.**

**Why this was rewritten.** The previous thesis was *"the reported accuracy advantage is not a
stable quantity"* — a methodological framing chosen because the obvious one (a fast SP-DLRA) was
unavailable. **R66 and R67 then found a better one in the project's own artifacts:** a
fixed-basis projected static POD run **diverges to overflow at `r ≥ 32`** where the
structure-preserving DLRA does not, and a rank criterion that grows with the dynamics exists and
works. That is the paper `AGENTS.md` was written for, and it was sitting unremarked in a committed
artifact.

---

## 1. The thesis

> **In a reduced Navier–Stokes solver, whether the subspace evolves is the difference between a
> method that runs and one that does not.** Propagating a fixed low-dimensional basis through the
> nonlinear dynamics — with the *same* structure-preserving integrator, the *same* projected
> splitting, and an orthonormal basis — is stable at rank 16 and does not survive to `t = 8` at
> ranks 32 and 42, where it overflows. The same integrator with a time-dependent subspace, whether
> refitted (static) or evolved (DLRA), holds roundoff divergence and a trajectory error below `1.1`
> throughout. **What rank buys is not accuracy; it is the ability to run at all.** And the accuracy
> advantage against a refitted static baseline, which is the number this literature reports as a
> property of the method, turns out to be a measurement that must be reported with five qualifiers
> or not reported at all.

**Why this framing and not the obvious one.** "A fast structure-preserving DLRA" is unavailable:
`2.08–2.71×` **slower** per step, `+2.5` to `+3.8 MiB` **more** memory, and no stationary
fluctuation state to validate against. A paper built on that would have to retract its own headline.

**Why this framing is stronger, for four reasons.** (i) It is the only framing under which the
project's *most* striking measurement — an overflow to `1e+278` — is a contribution rather than an
inconvenience. (ii) **It is a stability result, and stability is what a reduced method is *for*.**
A reader who does not care about crossover horizons still cares that their solver runs. (iii) It
gives a legitimate route to what `AGENTS.md` asks for **without any barred claim**: the project
cannot say *"adaptive rank"*, but **"the subspace must evolve"** is supportable today, in stability
terms. (iv) It makes the methodological contribution (§3.2) *sharper* rather than competing with it,
because the crossover fragility is then the second half of one argument — *the subspace must evolve,
and here is how carefully the evolution-free comparison has to be constructed to measure it.*

**Venue fit (D5: SISC/JCP rolling first).** A stability finding plus a measurement protocol, backed
by an implemented method, a verified implementation, and four documented harness bugs, is a
recognised genre. **ICML/NeurIPS are wrong for this** (D5).

---

## 2. An honest inventory

| the paper has | the paper does **not** have |
|---|---|
| **a fixed-basis projected POD run that overflows at `r ≥ 32` where the DLRA does not** — same integrator, same splitting, orthonormal basis (`baselines_re5000_N64_T8.json`; **ONE artifact, D31.3**) | **a sweep confirming it** — `baselines_*.json` contains exactly one file, so **this is a §7 observation today, not a contribution** |
| **a verified implementation**: full-grid and rank-1 reduced solvers both reproduce the **analytic** Taylor–Green decay to `2.8e-14` / `2.3e-14` over 200 steps (`taylor_green.json`; **fully supported, D32.1; provenance verified bit-for-bit from its own recorded commit `78607f3a`, D49.6**) — **and a stated limit (D49): the exact solution is a single Fourier mode (`numerical_rank: 1`), so the rank-1 solver is exact by construction; this case verifies the code and both invariants, NOT the accuracy of the reduction** | a manufactured-solution test at the resolutions or Reynolds numbers studied |
| **a crossover-horizon protocol** — five required qualifiers — **and the finding that the horizon is not a property of the method** (`t* = 0.649` at `r=16`, `1.482` at `r=32`; window-insensitive to `≤0.63%`, Re-sensitive by `3–9%`, but moved `1.6–2.8×` by three baseline corrections — **each of which shortened it**; **fully supported**) | a fitted `t*` law — **two resolved ranks cannot support one** |
| **the mechanism, measured not asserted**: the static baseline **saturates in rank** — `r=16`, `32`, `43` have *identical* static errors to four decimals at every horizon, and the spread across rank is `0.00%` at `t=0.1` (**fully supported, D30.1**) | a **located** never-yields rank — it is **bracketed between 32 and 43** at `N=64`, and `r=85` is untested (D30.4) |
| **a rank criterion that grows with the dynamics**: rank `17 → 36` at cutoff `1e-6`, `17 → 43` at `1e-8`/`1e-10`, error `1.0–1.7e-4`, stable (`rank_growth_sweep.json`) | **evidence beyond `T = 0.1` (200 steps)** — that is the initial transient, so **"adaptive rank" stays barred (D32.2)** |
| exact divergence-freeness, `2.3e-14`–`2.0e-13` across every committed run | any per-step **time** advantage — `2.08–2.71×` **slower** |
| second-order time integration, `1.98/1.95`, *conditional on sufficient rank* | any **memory** advantage — `+2.5` to `+3.8 MiB` **more**; peak RSS **varies by `0.29 MiB` across a 21× rank range at both grids, resolved at `2.2×` the `0.13 MiB` run-to-run noise floor** — so the variation is *real though small*, and **not** "flat" (D19.4a) |
| a BUG port that is structure-preserving, verified structurally (`large_svd_calls == 0`, `svd_max_dimension ≤ 4r`) and stationary to `< 1e-12` | BUG's speed case — **`3.3–5.1×` slower**, and **its cost rank-scaling is NOT claimed** (`1.366` at `N=64` vs `1.043` at `N=128`; memory spread not reproducible — D25.6) |
| four documented harness bugs, each fixed and recorded | a stationary fluctuation state at any `A` or `N` (D24.4: **neither** forcing admits a *resolution-robust* one) |
| | verified `N=128` grid multipliers — **`1.46→1.99` and `2.45→6.04` are mine and suspect** (D29.7). **Write the grid caveat qualitatively.** |

---

## 3. Contributions, in order, with evidence status

**`TODAY` = fully supported by committed artifacts; write it as a contribution. `ONE RUN` = one cheap
run away; put it in §7 now and promote it when the run lands.**

| # | contribution | status | source |
|---|---|---|---|
| **1** | **A verified, structure-preserving reduced solver — preserving BOTH invariants the continuous system has.** (i) The velocity field is **exactly divergence-free to `1e-14` at every rank**; (ii) the discrete energy balance **is** the continuous one, **`dE/dt + nu*||omega||^2 − <psi,zeta> = 0`**, with the advection input retained and vanishing to roundoff rather than assumed away (residual `< 1e-10` for an arbitrary state). **Both verified against the analytic Taylor–Green decay, where the full-grid and rank-1 reduced solvers agree with the exact solution to `2.8e-14` and `2.3e-14`.** The second is what makes "structure-preserving" a checkable statement rather than a label. | **`TODAY`** | **D39**, D32.1 |
| **2** | **The measurement protocol, and the finding that the crossover horizon is not a property of the method.** `t* = 0.649` (`r=16`) / `1.482` (`r=32`), insensitive to the baseline's *window* (`≤0.63%`) and to `Re` (`3–9%`), but moved **`1.6–2.8×`** by three individually reasonable corrections to a sixty-line baseline, which cost it three of six ranks — **and every correction made `t*` SMALLER, so fixing the baseline made our own method look worse (D34).** **A reported horizon must carry five things:** window, refit interval, offset, an in-sample check, and the grid with the largest rank tested. | **`TODAY`** | D15–D17, D26, D30.5 |
| **3** | **The mechanism, measured: a static subspace saturates in rank.** Above `r ≈ 8`, additional rank buys the static baseline **nothing measurable at any horizon** (`r=16`, `32`, `43` identical to four decimals); the spread across rank is `0.00%` at `t=0.1`. **This is why a horizon exists, and it is what makes (2) mechanistic rather than anecdotal.** | **`TODAY`** | D30.1 |
| **4** | **The stability result: the subspace must evolve.** A fixed basis propagated through the nonlinearity is stable at `r=16` and **overflows at `r = 32` and `42`** (`7.1e+278`), for both an early and a late window, with the same integrator, splitting and orthonormal basis; the time-dependent subspace holds roundoff divergence and error `< 1.1`. **§7 today; contribution when the sweep lands.** | **`ONE RUN`** — D31.5: `Re ∈ {1000,5000}`, `N ∈ {64,128}`, `T ∈ {8,20,40}`, `r ∈ {16,24,32,42}` | D31 |
| **5** | **The criterion that makes the subspace evolve, with its horizon stated.** An amplitude criterion grows the rank with the dynamics — `17 → 36` at cutoff `1e-6`, `17 → 43` at `1e-8` — monotonically in the cutoff, at `1.0–1.7e-4` error. **§7 today with the 200-step horizon stated; contribution when it runs to `T = 8` (≈ 2 minutes).** | **`ONE RUN`** — D32.2 | D32.2 |
| **6** | **Honest costs and boundaries.** No time or memory advantage at any rank. No resolution-robust stationary state, so the honest statistic is a **window-dependent** quasi-steady fluctuation energy. BUG buys structure preservation at a `3.3–5.1×` cost with **no measured offsetting benefit**, and we say so. The never-yields rank is **bracketed, not identified**. | **`TODAY`** | D11, D19, D24.4, D25.6, D30.4 |

**Write 1, 2, 3 and 6 as the contributions. Write 4 and 5 in §7 with their evidence status stated
plainly. If the two runs land before submission, promote them and move the crossover material to
second place — the argument survives either order.**

---

## 4. Section-by-section

| § | what it argues | sources | figure/table |
|---|---|---|---|
| **1 Introduction** | Reduced Navier–Stokes solvers are used at ranks where nobody checks whether the *subspace* is viable. We show a fixed basis does not survive at `r ≥ 32` where an evolving one does, and that the accuracy horizon this literature reports as a property of the method is a measurement with five qualifiers. | D31, D15.3 | — |
| **2 Related work** | Cite **and distinguish**: Koch–Othmar (SIMAX 2007, `10.1137/050639703`); Lubich–Oseledets, *projector splitting* (`10.1007/s10543-013-0454-0`); **Kusch–Schotthöfer–Walter 2026** (`10.1137/25m1730673`) — closest modern prior art, cite it; Musharbash–Nobile (refutes "no DLRA NS solver"); Girfoglio–Quaini–Rozza (refutes "first exactly divergence-free"); RAIL + Goutaudier (refute "first structure-preserving low-rank"). | D4 | — |
| **3 Method and verification** | Stream function ⇒ exact divergence-freeness. Projected splitting: exact viscous, projected nonlinear. Second order, **conditional on sufficient rank**. **Then the two invariants, stated as equations: `∇·u = 0` to `1e-14` at every rank, and `dE/dt + nu*||ω||² − ⟨ψ,ζ⟩ = 0` with the advection input vanishing to roundoff rather than assumed away — the second is the forcing-aware replacement for energy monotonicity, and it is what "structure-preserving" means here.** **Then the verification: both solvers reproduce the analytic Taylor–Green decay to `2.8e-14` / `2.3e-14` at rank 1 over 200 steps, balance residual `3.2e-4`. Every claim that follows is about the method, not the code.** | **D39**, D32.1, D12.3 | `fig_div_free` |
| **4 The measurement protocol** | **The methodological spine.** The five things a reported horizon must state. The four bugs we found, each with the symptom it produced. | D15.3, D16.3, D16.5, D30.5 | **table 1** |
| **5 Stability: the subspace must evolve** | Fixed vs time-dependent subspace, same integrator. The overflow at `r ≥ 32`. **Stated as an observation with its single artifact until the sweep lands** (D31.3). | D31 | `baselines` table |
| **6 Results: the horizon and its mechanism** | 6.1 the crossover surface; 6.2 the rank-saturated static floor; 6.3 robustness to window and Re; 6.4 the sensitivity across baseline corrections; 6.5 rank criteria **with the 200-step horizon stated**; 6.6 costs. | D29.4, D30.1, D32.2 | `fig_crossover`, `fig_window_rank`, `fig_cost`, `fig_spectra_ek`, `fig_divergence` |
| **7 Discussion and limitations** | Second order is conditional on rank, so an under-selecting rule costs *order*. Rank buys lead time, not speed. **The forcing-aware balance is why the fluctuation energy — and not total energy — is the honest statistic here: with a body force, total KE is not monotone even for the exact solution.** Where the method does not help: `r ≤ 8`, both cost axes. **No resolution-robust stationary state; the rank criterion verified only to `T=0.1`; the never-yields rank bracketed, not located; the `N=128` multipliers unverified.** | D12.3, D24.4, D30.4, D32.2, D29.7 | — |
| **8 Conclusion** | The subspace must evolve, or the solver does not run; and the horizon is a measurement, not a property. | — | — |

---

## 5. The abstract, from verified numbers only

> Dynamical low-rank approximation of the incompressible Navier–Stokes equations is usually
> reported as a fast and accurate replacement for a full-grid solve, with a crossover time against
> "a static baseline" quoted as a property of the method. We build a structure-preserving
> projected-splitting DLRA for the 2-D stream-function formulation that **preserves both invariants of
> the continuous system — exact divergence-freeness to `1e-14` at every rank, and the forcing-aware
> energy balance `dE/dt + nu||omega||^2 - <psi,zeta> = 0`, with the advection input vanishing to
> roundoff rather than assumed away — and we verify both against the analytic Taylor–Green decay,
> where the full-grid and rank-1 reduced solvers agree with the exact solution to `2.8e-14` and
> `2.3e-14`. We then ask what a reduced solver must have to be viable at all. **Propagating a fixed low-dimensional basis through the nonlinear dynamics, with the same
> integrator, the same splitting and an orthonormal basis, is stable at rank 16 and overflows at
> ranks 32 and 42, where the same integrator with a time-dependent subspace holds roundoff
> divergence and a trajectory error below 1.1 throughout: what rank buys is not accuracy but the
> ability to run.** An amplitude criterion that grows the rank with the dynamics does so
> monotonically in its threshold, tracking the full grid to `1e-4`, though we verify it only over
> `0.1` time units. Measuring the accuracy horizon against a refitted static subspace, we find it
> *insensitive* to the baseline's window (`0.15–0.63%` over a fourfold change) and to Reynolds
> number (`2.8–8.6%`) but *moved by a factor of `1.6` to `2.8`* by three successive corrections to a
> sixty-line baseline — **every one of which made the horizon shorter, so correcting the baseline
> made our own method look worse** — so we argue a reported horizon must carry five things: the baseline's window
> length, refit interval, offset, an explicit check that no basis contains its evaluation time, and
> the grid with the largest rank tested. We report the per-step cost (`2.08–2.71×` the full-grid
> step) and peak memory (`+2.5` to `+3.8 MiB` *above* it) with **no speedup claim**, and we do not
> claim a robust stationary state, because neither forcing admits one at these parameters.

**Every number above is traced in `CLAIMS.md`. If you edit one, re-trace it.** The two
evidence-status hedges (`T=0.1`, single artifact) are **load-bearing honesty, not weakness** — do
not remove them.

---

## 6. Figures and tables

| figure | artifact | section |
|---|---|---|
| `fig_crossover` | `crossover_surface.json` | 6.1 — **the central figure**; reads the rows, which are **bit-reproducible** (D29.3) |
| `fig_window_rank` | `regime_pilot_*.json` | 6.5 |
| `fig_cost` | `cost_retiming.json` | 6.6 |
| `fig_bug_cost` | `cost_bug_port.json` | 6.6 |
| `fig_spectra_ek`, `fig_spectrum` | pilots | 6.2 — `Z(k)` **omitted**, reason printed |
| `fig_divergence`, `fig_div_free` | pilots / drivers | 3, 6 |
| **table 1** | **the four baseline bugs** — what each did to the number, and the fix | 4 — **the paper's spine** |
| **table 2 (new)** | **fixed vs time-dependent subspace**: 16 methods, 4 overflow, none a DLRA run | 5 — **write from `baselines_re5000_N64_T8.json`; mark it as one artifact** |

**Table 1's rows** (from scratch, and the most important object in the paper): (1) off-by-one
sample — every row shifted; (2) initial basis fitted on the future — zero error at every rank;
(3) short window silently skipping the refit — a rank-`r` baseline reduced to rank 1; (4) refit at
an evaluation time — in-sample error. **Headline row: all three fixes together moved `t*` down by
`1.6–2.8×` and cost three of six ranks their crossover — i.e. fixing the baseline made the method
look worse, not better (D34).**

**Table 2's rows**: method · rank · diverged (and at what `t`) · `max|∇·u|` · final trajectory error.
**Its caption must say "one parameter set"** (D31.3).

---

## 7. What must not appear — with the decision that bars it

**Do not write:** any fitted `c·r^p` (D15.2) · `0.05·r^1.12` (R39) · `0.11·r^0.95` (R50) ·
`t* = 1.26` or `2.44` (**withdrawn, D29.2 — mine, from an index bug**) · "the curves cross
repeatedly" (R48) · any speedup, in time **or memory** (D11.1, D16.4) · "turbulent dynamics" or
"turbulence validation" (D11.2) · **"adaptive rank" or "rank growth" as a supported claim** (D32.2 —
the only evidence is 200 steps) · **"only the dealiasing ceiling leads at every horizon, because at
that rank the method is the full-grid solver"** (D30.2 — **false in every part**; `43` is the largest
rank *tested* and a *wavenumber* is not a rank) · "exact" for the never-yields rank (its error is
`1e-13`–`1e-8`, not zero) · "the `crossovers` block is stale/un-provenanced" (**withdrawn, D29.2**)
· "static POD fails" (**it is *propagated fixed-basis* projection that fails**; `pod_dmd_r32` is
stable though degraded, D31.3) · an instability-growth law for the divergence (**the divergence time
is not monotone in rank**, D31.3) · a drift percentage for the fluctuation energy (**the `24.7%` has
no source**) · any long-time or long-horizon claim from a `T=1` run (D32.3) · the `N=128` multipliers
`1.46→1.99` / `2.45→6.04` (D29.7) · any of the four D4 barred novelty claims · raw RSS as the memory
figure.

---

## 8. What a reviewer will attack, and the answer

| attack | the answer, with evidence |
|---|---|
| *"Your method is 1.8× slower and uses more memory. Why publish it?"* | We do not claim otherwise. **What rank buys is the ability to run**: a fixed basis overflows at `r ≥ 32` where the evolving one holds roundoff divergence. The costs are stated with numbers in §7. |
| *"One artifact. The divergence could be a bug."* | **Agreed, and it is in §7 as an observation, not a contribution.** It is the same `run_projected` path, the same `model.step(..., projector=)`, and an orthonormal SVD basis, so only the subspace differs. The sweep is running; the sentence gets stronger when it lands. |
| *"Your crossover depends on the baseline, so it is meaningless."* | **Agreed, and that is contribution 2.** `0.15–0.63%` across a 4× window change, `2.8–8.6%` across `Re`, `1.6–2.8×` across changes to its *correctness* — **and every correction shortened the horizon, so the honest baseline is the one that makes our own method look worst.** Table 1 shows what each correction did. |
| *"Two data points is not a scaling law."* | **Agreed; we do not fit one.** We report the two values and say why there are only two. |
| *"Exact divergence-freeness is textbook in a stream-function formulation."* | **Agreed, and we say so.** D4 bars the novelty claim. It is a property we verify against an analytic solution (§3), not one we claim. |
| *"How do you know the code is right?"* | **§3: both solvers reproduce the analytic Taylor–Green decay to `2.8e-14` and `2.3e-14` at rank 1 over 200 steps.** **And we say what that does not show (D49): the exact solution is one Fourier mode, so the rank-1 solver is exact by construction — the case tests the code and the invariants, not the accuracy of the reduction. We volunteer this, because a reader who derives it and finds it unstated discounts §3.** |
| *"No stationary state — so what is validated against?"* | A **window-dependent** quasi-steady fluctuation energy, reported with its window and drift (D24.4). **And we add the control:** the AKS pump *does* admit a qualifying window at `A=0.2`, so the negative is not merely asserted — **but the window shrinks under refinement and none exists at `A=0.5`, so no forcing gives a resolution-robust one.** |
| *"Is the rank criterion adaptive, then?"* | **It grows with the dynamics, monotonically in its threshold, and we verify it over `0.1` time units only** (`rank_growth_sweep.json`, 200 steps). We say so rather than claim more. |
| *"Is `t*` grid-convergent?"* | **We do not know, and we say so.** The `N=128` multipliers we had were not verified and are withdrawn (D29.7); the requirement to report the grid stands regardless. |
| *"Is the BUG port needed?"* | No, and we say so: **`3.3–5.1×` slower**, cost rank-scaling **not** claimed (withdrawn, D25.6). **BUG buys structure preservation at a `3.3–5.1×` cost with no measured offsetting benefit, and that is what we say.** |

---

**My assessment (R68).** This is publishable at **SISC or JCP** in the framing of §1, and it is not
publishable as a fast SP-DLRA. **Contributions 1, 2, 3 and 6 are supported by the evidence in hand
today and the paper can be submitted on them.** Contributions 4 and 5 would make it a stronger paper
and each needs one run of a few minutes. **The framing is no longer the missing piece — it is
written down here. What is missing is the draft.**
