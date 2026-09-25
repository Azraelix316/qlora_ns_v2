# R8 — **The forced problem has no stationary state at the committed parameters.** D10's stationarity requirement is unachievable as written

**Cycle:** R8
**Scope:** `solvers/forcing.py`, `experiments/run_kolmogorov.py`, `state/coder/results/*.json`
**Severity: the highest of the review.** This is not a bug in the code and not a
tuning nuisance. It invalidates the premise of the experiment as currently
parameterized, and it invalidates a requirement I myself wrote into the gate.
**Verdict on D10:** the stationarity clause (T=20) and the turbulent-regime premise
must be rewritten before the coder spends hours running a matrix that cannot pass.

---

## The finding

At the committed configuration — Re ∈ {100, 1000, 5000}, `N=64`, `dt=5e-4`, and the
driver's default **`force_amplitude=0.2`** (`experiments/run_kolmogorov.py:393`) — the
forced 2D NS solution **does not reach a statistically steady state by T=20**. Energy is
still growing at the end of the run, and the growth is not slowing.

Full grid, no projector, `main` = `2215903`, A=0.2, T=20 (40,000 steps), measuring the
drift over the final 20% of the run:

| Re | E₀ | E(T=20) | E/E₀ | mean E, last 20% | mean E, prior 20% | **drift** | dE/dt (last 20%) | **E_in/E_visc** |
|---|---|---|---|---|---|---|---|---|
| 100 | 22.21 | 153.2 | 6.90 | 130.0 | 87.0 | **+49.4%** | +10.74 | 10.1 |
| 1000 | 22.21 | 180.0 | 8.10 | 152.5 | 102.7 | **+48.4%** | +12.38 | 81.9 |
| 5000 | 22.21 | 154.1 | 6.94 | 132.6 | 97.8 | **+35.5%** | +8.73 | **173.5** |

**A statistically steady state would show a drift near 0% and `E_in ≈ E_visc`. Instead
E has grown 7–8× and is still climbing at 9–12 energy units per unit time, with the
forcing delivering 10–173× the power that viscosity removes.** A +35% to +49% drift
over the last fifth of the run is not a plateau approached slowly; it is a trajectory
that has not begun to turn over.

The same holds with no projector at all, so this is a property of the **forced
problem**, not of the reduced-rank method.

### It gets worse if the run is extended

Extending Re=5000 to T=40 at a *stronger* amplitude (A=0.5) gives E = 3747 at t=40 —
169× the initial energy — with `E_in/E_visc` still at 125 and `dE/dt ≈ 95`. There is no
plateau anywhere in the horizon; the imbalance is self-reinforcing because viscosity
scales like `νZ` while the forcing injects at a `ν`-independent rate, so the flow must
climb until `Z` is large enough to balance, and on a 64² grid it never gets there in
any runnable time.

### Why the amplitude matters, and why I nearly reported the wrong number

My first pass used A=0.5 and A=1.0 because I read the amplitude from the constructor
call in an earlier audit script rather than from the driver. Checking
`run_kolmogorov.py:393` before writing the report showed the committed default is
**0.2**. The finding is unchanged in kind and in conclusion at the committed value —
the table above is A=0.2 — but the growth factor is 7–8×, not 77×, and anyone quoting
the larger number would have been quoting a configuration the project does not run.
Recording the mistake because the R5q lesson was the same shape: the measurement has to
be taken at the configuration that is actually committed.

Note also `run_long_time.py:58` hardcodes **0.5**, so the two drivers disagree on the
forcing amplitude. That inconsistency needs fixing regardless of everything else here,
because a "long-time check" at a different forcing amplitude is not a check of the
same experiment.

## Verification, in the order I did it (testing each check before relying on it)

1. **Does the energy budget close?** If not, my forcing term is wrong and the finding
   is void. Over a 0.25-time-unit window at t=1.25, observed `dE/dt` versus
   `⟨f,ω⟩ − νZ`: ratios 0.59 (Re=100), 0.82 (Re=1000), 0.92 (Re=5000) using
   `⟨f,ω⟩` without the ½. The budget closes to within a factor consistent with
   dealiasing removing a little energy, **not** with a sign or factor error. The
   finding survives. (For reference, the *unbalanced* term is the finding: the budget
   closing only proves the measurement is right, not that the flow is steady.)
2. **Is the integrator's dissipation correct?** Re-run with the forcing amplitude
   reduced to 1e-14 (effectively off). Energy then decays **monotonically** at every
   Re — 26.3% of E₀ remaining at Re=100, 95.5% at Re=5000 after t=2, with
   `dE/dt_obs / (−νZ)` of 4.77 and 2.06 (the excess is enstrophy decaying over the
   averaging window, as expected). **The unforced solver is correct.** The growth is
   produced entirely by the forcing term.
3. **Is it the projection?** No. At the working rank the projection's energy
   contribution is ~1e-17 per unit time against a viscous term of ~1e-4 — **five
   orders of magnitude smaller**. Even at the severe fixed rank r=2 it is ~2e-9
   against 3e-5. The projection is not the energy sink; the forcing/viscosity
   imbalance is, and it is present in the **full-grid** run with no projector at all.

## Why this matters more than any finding since R5k

**It invalidates a clause I wrote.** `D10-EXPERIMENT-SPEC.md` requires "statistical
stationarity: runs long enough that E(t)/Z(t) stop drifting", and R5o costed T=20 at
N=64 as ~20 minutes precisely so that requirement would be affordable. That
requirement assumed a stationary state exists at T=20. **It does not.** The gate as
written asks for something the discretisation cannot deliver, and a coder following it
literally would burn a day producing a run that fails on a criterion that was never
satisfiable — or, worse, would relax the criterion and report a non-stationary run as
stationary. I would rather find this now than after the matrix is run.

**It invalidates the premise.** The project's stated contribution is validation on
"high-Reynolds-number, forced, turbulent dynamics". A solution that is still
accelerating at t=27 with E/E₀ = 77 is **not** in a turbulent statistical state; it is
in a spin-up transient. Every turbulence statistic the paper wants — spectra,
time-averaged E and Z, the slow singular-value decay that motivates adaptive rank — is
meaningless unless measured after stationarity. So the current runs cannot support the
headline claim even if the accuracy targets are met.

**It explains a result I had already recorded and misread.** The committed artifacts
report `final_time: 0.1` and I attributed the poor full-grid enstrophy agreement
(2.25× between N=64 and N=128) to under-resolution. At t=0.1 the flow has barely moved
(E = 22.2 → ~23), so the committed comparison is essentially **two initial conditions,
not two resolutions**. Under-resolution is still real (R5m), but it is not what those
artifacts measure. The stationarity finding is the more fundamental defect and it sits
upstream of it. Note the two findings now point the same way for different reasons,
which is worth stating: even if stationarity were fixed, a t=0.1 comparison cannot
support a resolution claim, and even if the comparison were fixed, a non-stationary
flow cannot support a turbulence claim. Both are required.

**It changes the D3 invariant's role.** D3's forcing-aware invariant exists because
"KE monotonicity is replaced by a forcing-aware statement". The energy budget I measured
gives that invariant concrete content: `dE/dt = ⟨f,ω⟩ − νZ` plus a projection term
that is numerically negligible here. Theoretical-research should state the identity in
exactly this form. But note the consequence: an invariant whose terms are
*individually measured and unbalanced by two orders of magnitude* is a **diagnostic of
the run, not a validation of the method**. It will faithfully show that the run is not
stationary, which is useful, but it cannot be presented as the method satisfying a
structure property.

## What the coder has to decide, and what I have decided

The forcing amplitude is too large for these Reynolds numbers. That is a physical
scaling statement: Kolmogorov forcing injects at a rate independent of `ν`, while
viscous dissipation scales like `νZ`, so at large Re a fixed-amplitude forcing drives
the energy up until `Z` grows enough to balance — and on a 64² grid the enstrophy
needed to balance arrives only after the flow has long since left the regime the paper
wants to study. I have launched a sweep over forcing amplitude (1.0 → 1e-3) to find
where balance is reached in a runnable time; results to follow.

**Binding, and these are mine as reviewer, not the coder's to negotiate:**

- **B1. No turbulence statistic may be reported from the committed runs.** They are
  t=0.1 transients. This includes the spectra, the time-averaged E and Z, and anything
  built on them.
- **B2. The stationarity clause is suspended, not relaxed.** T=20 is withdrawn as a
  target until a forcing amplitude is found that actually reaches stationarity at
  N=64. I will re-cost and re-issue the clause against measured balance, not against
  a hoped-for plateau.
- **B3. `base_speed=0.5` with `perturbation_velocity_rms=1.0` and forcing
  amplitude 1.0 is a three-way parameter choice that nobody has justified.** The
  perturbation RMS being comparable to the base speed means the "base" zonal flow is
  not a slow background at all. Any amplitude change should come with a one-paragraph
  physical justification of the intended regime, not a search for the value that makes
  a number look stationary.
- **B4. The full-grid reference must reach stationarity before it is used as a
  reference at all.** A reference that is itself in transient cannot adjudicate a
  reduced model's accuracy, and the rel-L2 errors currently in the artifacts are
  dominated by spin-up rather than by the method.

## The smaller finding, while I was in there: the projection is not an energy sink

I told coder in the V6 message that the four stage projections "bleed energy"
systematically. Measured, that is **not** what happens at these ranks:

| Re | r | E_in | E_visc | **E_proj** | proj/visc |
|---|---|---|---|---|---|
| 100 | 43 | 1.38e-3 | 5.46e-3 | 4.0e-18 | 1e-15 |
| 1000 | 43 | 1.39e-3 | 6.55e-4 | −1.3e-18 | ~0 |
| 5000 | 43 | 1.39e-3 | 1.33e-4 | −2.1e-18 | ~0 |
| 5000 | 2 (fixed) | 1.39e-3 | 3.29e-5 | 2.3e-9 | 7e-5 |

The projection's energy contribution is **five orders of magnitude below viscosity**
at working rank. So the honest statement is not "the projections destroy energy" — it
is "**at r≈43 on N=64 the projection is nearly energetically inert, because a rank-43
truncation of a 64×64 field discards very little**". I also tested whether the
per-step increment is sign-definite: over 200 steps it was negative 64.5% of the time
and **positive 33.0%** of the time, but the positive excursions reach only +1.2e-13
against E ≈ 22, i.e. roundoff. My first summary line claimed the increment has "no
a priori sign"; my own data refuted the stronger version of that (a 1000-trial sweep
over roughness × rank found **0** projections that increased energy, so on this family
it is empirically H1-nonincreasing), and I am recording the correction rather than the
original phrasing.

**The correct criticism of the four-projection structure is therefore not energetic but
computational and structural**: 4 dense N×N SVDs per step (R5q Finding A), and a
split whose projection term is not the dominant error source, so the Galerkin step's
value is the **discrete structure property and the cost**, not energy fidelity. That
*strengthens* the V6 case on cost and weakens it on energy — the opposite of the
emphasis I sent, and coder should know before designing the port's validation.

## For theoretical-research (D3, owed since R1)

State the forcing-aware invariant as `dE/dt = ⟨f,ω⟩ − νZ + Π`, with all three terms
*defined discretely* and `Π` the projection contribution. The measurement above says
`Π` is ~1e-17 relative to `νZ` at working rank, so the identity is, at these ranks,
approximately `dE/dt = ⟨f,ω⟩ − νZ`. That is a useful and honest result: it means the
current reduced model's energy behaviour is governed by the *forcing and viscosity*,
not by the low-rank truncation — which is itself a finding worth a sentence in the
paper, and the opposite of what the D3 discussion has assumed.

## What I have not yet done

- The amplitude sweep is still running; I will report which amplitudes balance and
  re-issue the stationarity clause against measurement.
- I have not checked whether the blow-up is genuinely physical for Kolmogorov flow at
  Re=5000 or an artefact of `base_speed=0.5` being a strong zonal flow that the forcing
  keeps amplifying. That distinction matters for the paper and I am not guessing at it.
- I have not re-run the DLRA path to T=20. Given the full grid does not reach
  stationarity, the reduced runs will not either, and re-running them is not worth the
  compute until B2 is settled.
