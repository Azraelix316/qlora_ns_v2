# R5o — is the gate affordable? A costing of D10, and the order to run it in

**Date:** 2026-09-25 · **Reviewer cycle:** R5 (addendum 9) · **Purpose:** a merge
gate that cannot be executed in the available time is a gate that gets quietly
relaxed, so the reviewer costed the required runs before R6 rather than
discovering at R6 that they do not exist.

## Measured basis

Wall-seconds per step, from the committed artifacts (Re=5000):

| method | N=64 | N=128 | ratio |
|---|---|---|---|
| full-grid spectral | 1.84 ms | 7.10 ms | 3.85× |
| static POD | 2.95 ms | 12.12 ms | 4.11× |
| adaptive DLRA | 4.60 ms | 14.29 ms | 3.11× |

## What this says about the gate

**Stationarity (V2) is cheap.** At N=64 with dt=5e-4, a T=20 run is 40,000 steps:
**1.2 min** for the full-grid reference and **3.1 min** for the DLRA. The whole
three-Reynolds × four-method matrix (full, DLRA, POD, POD-DMD) at N=64 and T=20
is roughly **20 minutes**; even T=100 is about 1.5 hours. My earlier concern
that "T = 20–100" implied a heavy compute budget was wrong at this resolution.

**The resolution study (V5) is also cheap, and does not need long runs.** Its
purpose is to show whether the diagnostics are grid-converged, which requires the
same physical problem at N=64/128/256 — not a long horizon. At T=0.1 those are
seconds to a couple of minutes. A resolution study run at long T would be
answering a different question at several times the cost.

**The expensive combination is the one that is not required.** High resolution
*and* long horizon together (N=256 with T=20) extrapolates to several hours,
and that combination is not needed: stationarity can be demonstrated at N=64/128
while resolution is demonstrated at short T. This dissolves the tension I had
assumed existed between the two requirements.

## A caveat that matters more than the numbers: the timings are not yet trustworthy

The N=64 → N=128 ratio for the DLRA is **3.11×**, which is *below* the ~3.85×
that `N² log N` FFT scaling alone would predict. A cost that grows more slowly
than the work it performs means the N=64 measurement is dominated by fixed
overhead or warm-up rather than by the algorithm — which is exactly the artifact
R5n found in `fig_cost.png` (a 1.7× spread across Reynolds numbers for
computationally identical work).

So these projections are **order-of-magnitude planning figures, not predictions**.
The first step of any costing-based plan must be to re-measure the per-step costs
with warm-up discarded and repeats, per R5n. I have also not extrapolated N=256
here: a two-component fit from two measured points degenerates here (it returns
a DLRA cost *below* the full-grid cost at N=256, which is not physical), so
N=256 must be measured, not modelled.

## Recommended order of work

Cheap first, in this order, so that each result de-risks the next:

1. **Re-time** the per-step costs properly (warm-up discarded, repeats, median
   + spread). Minutes of work; every later cost statement depends on it, and it
   fixes the R5n figure defect.
2. **V1** — identical initial states, with `initial_state_sha256` and per-method
   initial energies recorded, and the step-0 error computed rather than
   hardcoded (R5m). Without this every later number is uninterpretable.
3. **V2 at N=64, T=20** — stationarity for the three Reynolds numbers. ~20
   minutes for the full matrix. This is the single highest-value run in the
   project, because it is what makes "high-Re forced turbulence" a measured
   statement rather than an aspiration, and it is cheap.
4. **F2** — record the *full* state spectrum (the committed `normalized_spectrum`
   caps at 32 values; the premise claim needs the tail) and plot the IC against
   the developed state. Seconds of compute, and it produces the paper's
   motivation figure.
5. **V5 at short T** — N=64/128/256, same physical problem, dt scaled with dx.
   Minutes. Record which Re is resolved at which N.
6. **V4** — rank- and work-matched POD and POD-DMD from the identical state.
7. **V6** — the BUG port, then re-run 3–6 with the new integrator.
8. Only then consider whether any long high-N run is needed, and decide it from
   the measured N=256 cost rather than an extrapolation.

Steps 1–5 are a few hours of work in total and would leave the project with a
defensible turbulence-validation section; step 7 is the one with real
engineering risk, which is another reason not to defer it behind the runs.
