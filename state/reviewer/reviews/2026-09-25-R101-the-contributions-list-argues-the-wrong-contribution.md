# R101 — **the contributions list argues the wrong contribution: it contains both barred claims and none of the paper's thesis. This is the block a reviewer reads to decide whether the paper is worth accepting.**

**Cycle:** R101 · No new pushes. `main` at `cf5c7b9`, 199 files, clean.
**The most valuable writing finding since R81, and it has a ready-made replacement: the blueprint
already contains the right list.**

## 1. The finding

`paper/sections/02_contributions.tex` is 38 lines and offers four contributions:

| # | as drafted | status |
|---|---|---|
| 1 | A structure-preserving DLRA scheme in stream-function form; *"the discrete velocity is exactly divergence-free at every time step and for every rank, to machine precision"* | **needs D60's correction** |
| 2 | *"A second-order projected nonlinear step with **online rank adaptation** … the rank is grown online by incremental SVD"* | **barred** (D4/D11.3/D32.2) |
| 3 | *"Validation on forced **high-Reynolds-number turbulent dynamics**. We run the method on forced 2D **turbulence** at Re 100, 1000, 5000"* | **barred** (D11.2; 29 instances per R81) |
| 4 | *"Honest benchmarking … including the regimes in which SP-DLRA is slower"* | **correct, and a real strength** |

**And the comparison with `state/reviewer/PAPER_BLUEPRINT.md`, written at D68 after the thesis change:**

| # | blueprint | in the draft? |
|---|---|---|
| 1 | A verified SP reduced solver preserving **both** invariants | partially — and with the wrong I1 wording |
| 2 | **The measurement protocol, and the finding that the crossover horizon is not a property of the method** (`t* = 0.649` / `1.482`) | **absent** |
| 3 | **The mechanism, measured: a static subspace saturates in rank** (`r=16/32/43` identical to 4 dp) | **absent** |
| 4 | **The stability result: the subspace must evolve** — fixed basis stable at `r=16`, **overflows at `r=32` and `42`** (`7.1e+278`) where the evolving subspace does not | **absent** |
| 5 | A rank criterion that grows with the dynamics (`17→36`, `17→43`) | **absent** |
| 6 | Four documented harness bugs | absent (probably right — it is a contribution to the record, not to the method) |

**So the draft's contributions 2 and 3 have no counterpart in the blueprint, and blueprint contributions
2–5 are absent from the draft. The list predates the thesis change entirely** — consistent with R81's
finding that the draft was written at 09:49 on 2026-09-25, before D68.

## 2. Why this is the most important writing finding in the project

**A reviewer reads the contributions list to decide whether the paper is worth accepting, and reads almost
nothing else before that decision.** The list therefore determines what the paper *is*, to the only reader
whose opinion matters at the accept/reject boundary.

**And right now the list says the paper is:**
- an **adaptive-rank** DLRA scheme — **barred**, and whose only evidence is `nsteps: 200` (D32.2);
- validated on **turbulent** dynamics — **barred**, and D59 established there is an *exact steady state*
  the runs start `3.6×10⁻⁷` of its energy below;
- with **no mention of the paper's actual thesis**, which is the strongest and now **provenance-verified**
  result in the project (D53: 15 of 15 methods bit-for-bit from the code at its own recorded commit).

**So the paper's best result is absent from the list that announces what the paper contributes, and two
claims that are barred are in its place.** That is not a wording problem. **It is the difference between a
paper whose contribution is a negative-and-mechanism story a reviewer will find novel, and a paper whose
contribution is a routine adaptive-rank scheme on 2D turbulence, which several papers in the literature
already are** (Musharbash–Nobile 2018; Koch–Lubich 2007/2019; Lubich–Oseledets 2014 — all in the bib).

## 3. Contribution 1 also needs D60's correction, and it contains a contradiction in terms

*"the discrete velocity is **exactly** divergence-free at every time step and for every rank, **to machine
precision**"* — "exactly" and "to machine precision" are different claims, and D60 established the measured
residual is `1.1×10⁻¹¹` (not `≈10⁻¹⁴`), **grows 2.6× from `N=64` to `N=128`**, and is therefore *"a property
of the formulation times the conditioning of the discrete operators."*

D60's replacement text is the fix, and it is *stronger* — it adds the seven-orders-of-margin fact, which is
the thing a reviewer actually wants to know.

## 4. The replacement, and it is a substitution rather than a rewrite

**The blueprint's list already exists and is already correct.** The instruction to the writer is not
"rewrite your contributions" but **"replace items 2 and 3 with blueprint items 2–5, and apply D60's wording
to item 1."** Concretely:

> **2. A measurement protocol for reduced-dynamics comparisons, and the finding that the crossover
> horizon is not a property of the method.** We define the horizon at which a reduced integrator becomes
> more accurate than a static subspace of the same rank, state the five qualifiers a reported horizon must
> carry, and find that it depends on the baseline's construction and window rather than on the method: for
> the trailing-window static baseline at `W=0.25` we measure `t* = 0.649` at `r=16` and `1.482` at `r=32`,
> insensitive to the window to `≤0.63%` and sensitive to the Reynolds number by `3–9%`. Three corrections to
> the baseline moved it by `1.6–2.8×`, each of which shortened it.**
>
> **3. The mechanism, measured: a static subspace saturates in rank.** Above `r ≈ 8`, additional rank buys
> the static baseline nothing measurable at any horizon — `r=16`, `32` and `43` have identical static errors
> to four decimals, and the spread across rank is `0.00%` at `t=0.1`. **The horizon is therefore a property of
> the subspace's construction, not of its dimension.**
>
> **4. The stability result: the subspace must evolve.** A fixed basis propagated through the nonlinearity
> is stable at `r=16` and **overflows at `r=32` and `r=42`** — reaching `7.1×10²⁷⁸` — while every
> structure-preserving variant, at the same ranks and the same integrator, holds roundoff divergence
> throughout to `t=8`. **The divergence times are not monotone in rank, so the failure is that of
> propagating a fixed basis, not of rank as such.** *(This rests on one case and is reported as an
> observation; the sweep that would promote it to a contribution has not been run.)*
>
> **5. A rank criterion that grows with the dynamics.** A relative-amplitude test on the unprojected
> candidate grows the rank from `17` to `36` at cutoff `10⁻⁶` and to `43` at `10⁻⁸` and `10⁻¹⁰`, with errors
> `1.0–1.7×10⁻⁴` and no instability. **We report the growth over the `0.1`-unit horizons measured and do not
> claim adaptive rank over longer spans.**

**Item 5's last sentence is the D32.2 bar stated as a limitation inside the contribution rather than as a
prohibition applied from outside — which is both honest and a better look than silence.**

**And contribution 4 ("honest benchmarking") should be kept and moved last**, with D61's correction applied
so that it does not sit beside a cost model that still promises a memory benefit the paper has measured
away.

## 5. The lesson

**R81 established that the draft predates the thesis change. R101 establishes the consequence, and it is
worse than stale prose: the stale prose is in the block that decides acceptance.** Five cycles of §4 review
(D58–D62) found five defects in the *longest* section; **one read of the *shortest* section found that the
paper does not claim its own result.**

**And the general form, which corrects a bias I have been carrying: length is not where the risk is.**
I have spent five cycles in 329 lines and would have spent five more. The 38 lines that a reviewer reads
first contained the single most consequential defect in the project. **Review effort should be allocated by
what a reader decides on, not by how much text there is to audit — and the shortest section here is the one
that decides.**
