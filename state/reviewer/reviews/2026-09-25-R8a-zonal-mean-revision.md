# R8a — Revision of R8: the mechanism is a growing zonal mean, not a spin-up transient. R8's conclusion stands; its diagnosis and my stationarity criterion were both wrong

**Cycle:** R8a (revision of `2026-09-25-R8-no-stationary-state.md`)
**Verdict:** R8's *conclusion* — no statistically steady state at T=20, so the
committed runs support no turbulence statistic — is **confirmed and strengthened**.
Its *mechanism* was wrong, and so was the criterion I suspended. Both are corrected
here, and the corrected criterion is re-issued below.

---

## What R8 got wrong

R8 said the flow was "in a spin-up transient". That is the wrong diagnosis. The energy
growth is **not** a transient that settles; it is a **slow secular growth of the zonal
(x-averaged) mean flow**, which is the physically expected behaviour of forced
Kolmogorov flow and does not settle on any horizon available here. Decomposing
E into its zonal and fluctuating parts changes the interpretation of every number in
R8, so the decomposition is now part of the gate.

## The decomposition (full grid, A=0.2, N=64, dt=5e-4, T=40, 2-time-unit block means)

| t | Re=100 E_fluc | Re=1000 E_fluc | Re=5000 E_fluc | ū_bar (Re=100 / 1000 / 5000) |
|---|---|---|---|---|
| 2 | 7.90 | 17.19 | 18.95 | 0.489 / 0.504 / 0.508 |
| 10 | 2.16 | 15.26 | 24.41 | 1.456 / 1.460 / 1.368 |
| 20 | 1.54 | 26.09 | 58.55 | 2.663 / 2.659 / 2.074 |
| 30 | 0.82 | 28.82 | 126.48 | 3.759 / 4.013 / 2.661 |
| 40 | 0.55 | 36.74 | 215.63 | 4.748 / 5.329 / 3.280 |
| **drift, last half** | **−69.4%** | **+60.6%** | **+295.1%** | growing at ≈0.11–0.13 / time unit at **every** Re |

Three things follow, and all three matter more than the headline growth rate.

**1. The mean is not yet viscosity-limited, so it has no equilibrium to relax to.**
`ū_bar` grows at essentially the **same rate** (≈0.11–0.13 per time unit) at Re=100,
1000 and 5000 — across a **50× range in ν**. If the mean were approaching a viscous
balance `ū ~ A/(νk²)` (20 at Re=100, 200 at Re=1000, 1000 at Re=5000), the approach rate
would scale with 1/ν and the trajectories would separate by orders of magnitude. They
do not. The mean is in a slow linear growth phase whose timescale is set by the forcing
ramp, not by viscosity, and at Re=5000 it has reached ū≈3.3 against an equilibrium
some two orders of magnitude higher. **On any horizon this project can afford, the
total energy has no plateau, and that is physics rather than a defect.**

**2. The three Reynolds numbers are in three qualitatively different regimes, not one
regime at three Re.** This is the finding that most affects the paper. At **Re=100 the
fluctuations are dying** (E_fluct −69%, Z_fluct 3.6e2 → 0.55): the growing mean flow
stabilises the field and it becomes quasi-laminar. At **Re=1000** the fluctuations are
noisy and slowly growing (+61%, with Z_fluct nearly steady at 35–45). At **Re=5000**
the fluctuation energy is still accelerating (+295%). A Reynolds-number sweep is
supposed to hold a regime fixed and vary the parameter; here varying Re changes the
*qualitative behaviour*, so "Re ∈ {100, 1000, 5000}" is not a sweep of one phenomenon.
In particular **Re=100 is not a turbulent case with these settings**, which removes one
of the three points the paper planned to report.

**3. R8's criterion was wrong even where its conclusion was right.** Total E and total
Z cannot plateau here, because the mean legitimately grows. A stationarity test on
total energy is therefore not merely unsatisfiable — it is the wrong test. The
meaningful test is on the **fluctuating** part, with the mean reported and explained
separately. Measured that way, no Re is stationary at T=20 **or T=40** (−69%, +61%,
+295%), so R8's practical conclusion — the committed `t=0.1` artifacts support no
turbulence statistic — is confirmed, and now for a better reason.

## There is a genuine design tension, and it is not solvable by tuning the amplitude

The paper needs high Re for interesting turbulence, and it needs the zonal mean to
equilibrate quickly so that statistics can be taken. Those pull in opposite
directions: the mean's equilibration rate scales like ν, so the Re values where
fluctuations persist (≥1000) are exactly those where the mean takes longest to settle.
R8's advice — "choose a forcing amplitude that reaches stationarity" — was therefore
under-specified, and on this evidence **amplitude tuning alone cannot resolve it**:
lowering A lowers both the mean growth and the turbulent forcing together.

Three legitimate resolutions, and **the choice is coder's and theoretical-research's to
make with a justification, not mine to impose**:

- **Analyse the fluctuations** (subtract the x-average) and report statistics on those,
  treating the mean's growth as a separately reported, separately explained feature.
  This is the cheapest and the most common practice for forced Kolmogorov flow, and it
  makes the Re=100 quasi-laminar result a *finding* rather than an embarrassment.
- **Remove the zonal momentum equation** so the mean cannot grow secularly, leaving a
  statistically steady turbulent field. This is a real transformation with a literature
  behind it; I am naming it as a candidate and **not** asserting it is the right choice
  without checking its assumptions against this forcing and domain.
- **Run much longer**, accepting that the mean grows throughout and that only
  fluctuation statistics are meaningful. This costs the most and still may not reach
  stationarity at Re=5000.

Whichever is chosen, the paper must state it explicitly. A reader who is told "Re=5000,
T=20" with no statement of what was held fixed while the mean grew for twenty time
units will draw the wrong conclusion.

## The stationarity criterion, re-issued

This replaces the suspended F4 clause. It is mechanical, as all gate criteria must be.

**S1. Statistics are computed on the fluctuating field** `ψ′ = ψ − x-avg(ψ)`, with the
zonal mean's trajectory reported alongside. Total-E stationarity is **not** a criterion
and must not be asserted; if total E is plotted, the plot must show the decomposition.

**S2. Stationarity is demonstrated per Re on `E_fluct` and `Z_fluct`**, by
block-averaged means (blocks of ≥2 time units) over the final third of the run, with
the drift between the last two thirds reported. **Bar: |drift| ≤ 10% on both
`E_fluct` and `Z_fluct`.** At the committed parameters this is met at **no** Re
(−69%, +61%, +295%), so the criterion is honest and currently failing.

**S3. The horizon is measured, not assumed.** T=20 was my assumption and it is wrong;
even T=40 does not satisfy S2. The run length must be chosen from a pilot that reports
the S2 statistic as a function of T, and the chosen T stated with the evidence.

**S4. The regime is characterised per Re, and a quasi-laminar case is reported as
such.** With the committed parameters Re=100 is quasi-laminar by t=40. Either the
configuration changes so that all three Re are in the intended regime, or the paper
reports Re=100 as a laminar/quasi-laminar control — which is a legitimate and
informative thing to have, but it cannot be presented as one of three turbulent cases.

**S5. No turbulence statistic from `t ≤ 0.1`** — unchanged from R8 and now doubly
justified.

## What is unchanged from R8

- The committed artifacts still support **no** turbulence statistic.
- The t=0.1 N=64-vs-N=128 comparison is still closer to two initial conditions than
  two resolutions.
- F4 is still not runnable — but for a **better** reason, and with a criterion that can
  actually be satisfied.

## Self-correction, recorded deliberately

R8 asserted a mechanism ("spin-up transient") that I had not isolated, and suspended a
criterion (total-E plateau) that was itself mis-specified for forced Kolmogorov flow.
The conclusion survived; the reasoning did not, and a conclusion reached by wrong
reasoning is one that should not be trusted until re-derived. This is the third time in
two cycles that measuring the committed configuration changed the answer (R5q's cost
model, R8's amplitude, R8a's mechanism), and the pattern is consistent enough to name:
**the first explanation of a surprising result is usually the one I should check
hardest, because it is the one I did not have to work for.**
