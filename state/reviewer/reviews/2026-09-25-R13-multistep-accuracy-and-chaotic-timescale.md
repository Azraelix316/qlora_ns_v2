# R13 — Multi-step accuracy, measured properly. **It corrects a claim I made to writer last cycle**, and it establishes the chaotic timescale the paper needs

**Cycle:** R13
**Scope:** correction to R12 §4(ii); the accuracy question in `D10-EXPERIMENT-SPEC.md` P0
**Trigger:** R12 asked coder to protect "the dynamics do not amplify the truncation error
over a step" with a test, and I told writer the method "is not error-amplifying". Both
rested on a **one-step** measurement, and I had explicitly flagged the multi-step
question as unanswered. It should not have propagated before being answered.

All measurements: full grid and DLRA from the same state, advanced **in lockstep**,
A=0.5, Re=5000, N=64, `dt=5e-4`, developed to t=2 then tracked to t=5. Threads pinned.

---

## 0. My first attempt at this measurement was wrong, and the way it was wrong is instructive

I wrote a harness that compared every run against a **frozen** reference state. Both the
"DLRA error" and the "background" therefore measured the *flow's displacement from its
t=2 state* — an identical quantity for both, which is why the two curves agreed to four
decimal places and appeared to show that the DLRA error was rank-*independent* and that
*lower rank was better*. Both conclusions were artefacts.

I caught it because a control that agrees with its subject to four decimals is not a
control. I redid the harness with the reference advanced in lockstep, and **validated it
with two assertions before believing any output**: the background must start at ~1e-8
(got 6.8e-9) and the DLRA at full rank 43 must start at ~0 (got 1.4e-12). Both passed.

The false result was not a small error. It reversed the sign of the rank–accuracy
relationship, which is the central accuracy question. **A control that cannot fail is not
a control**, and the cheapest test of a harness is to check that the two things it is
supposed to distinguish actually come out different.

## 1. The corrected result: rank controls accuracy, monotonically

Lockstep relative L2 error against the full-grid reference, from t=2:

| rank | t=2.12 | t=2.50 | t=3.00 | t=4.00 | t=5.00 |
|---|---|---|---|---|---|
| 43 (= ceiling) | 1.4e-12 | ~0 | ~0 | ~0 | ~0 |
| 32 | 0.0022 | 0.0060 | 0.0133 | 0.0387 | **0.0785** |
| 16 | 0.0126 | 0.0252 | 0.0476 | 0.0846 | **0.1460** |
| 9 | 0.0309 | 0.0462 | 0.0684 | 0.1188 | **0.1889** |
| 5 | 0.0830 | 0.0965 | 0.1439 | 0.2616 | **0.3707** |

**Rank ordering is strictly monotone at every sample: higher rank, lower error.** The
error grows steadily — roughly exponential, e-folding ≈1.2–2 time units depending on rank
— reaching **7.9% at r=32, 14.6% at r=16, 18.9% at r=9 and 37.1% at r=5** after three
time units.

**This corrects R12 and my message to writer.** "The dynamics do not amplify the
truncation error" is true *of a single step* and false *of the method over time*. The
correct statement is two-part and both halves matter: **truncation introduces no
per-step amplification, but the accumulated error grows at a rate that rank controls.**
R12's one-step observation is not retracted — it is the reason the growth is slow and
smooth rather than explosive — but I should not have generalised it to the method, and I
am telling writer so directly.

## 2. The flow is **not chaotic** on the horizon where the method is validated

The background — the same integrator with the IC perturbed by a relative 1e-8 — stays
essentially flat over three time units, from four different starting states:

| start t | E | E_zonal | perturbation at t+1 | at t+3 |
|---|---|---|---|---|
| 2 | 39.5 | 49.7% | 8.6e-9 | 5.5e-8 |
| 5 | 92.0 | 64.4% | 9.5e-9 | 6.8e-8 |
| 10 | 253.2 | 87.0% | 1.2e-8 | 4.9e-8 |
| 20 | 939.7 | 93.8% | 1.1e-8 | 3.2e-8 |

A 1e-8 perturbation reaches only ~5e-8 in three time units, over a range of mean
fractions from 50% to 94%. Two consequences, and they point in opposite directions.

**(i) Good for the metric: pointwise relative L2 is a valid accuracy measure here.** P0
withdrew it because "pointwise relative L2 is not an accuracy measure once the two
solutions decorrelate". Over this horizon they demonstrably do not: the background sits
at 1e-8 while the method's error is 1e-2 to 4e-1. So the numbers in §1 are genuine
accuracy measurements against a non-decorrelated reference, and the paper may report
them. This is the first time P0's caveat has been *shown not to apply* rather than
assumed.

**(ii) Bad for the regime: this is not developed chaos.** The perturbation does grow
exponentially once past an initial dip — from 6.8e-9 to 5.5e-8 over three time units is
a factor 8, i.e. **λ ≈ 0.69 per time unit** as a *lower bound* (single smooth
perturbation direction, so it underestimates the maximal exponent) — and O(1)
decorrelation would follow at roughly **30 time units**. So the flow has a long,
well-defined chaotic timescale and is nowhere near it on any horizon this project has
run. Combined with R8/R8a's findings (the mean grows secularly, no stationary state,
Re=100 goes quasi-laminar), the regime is best described as **slowly evolving,
mean-dominated, weakly chaotic** — which is not the "high-Reynolds-number forced
turbulent dynamics" the project set out to validate.

**λ ≈ 0.69/time unit is itself a paper-worthy number**, because it is what makes P0
quantitative rather than rhetorical: any trajectory comparison is trustworthy until the
background reaches the method's error, which at these rates is ~10–20 time units for
r=32 and beyond the horizons currently run for lower ranks. It should be measured
properly (multiple random perturbation directions, a fit over the exponential regime,
reported as a lower bound) and then quoted in the methods section.

## 3. What this means for the accuracy claims

- **The committed headline is not a method result.** The artifacts report rel L2 ≈ 0.3165
  at T=0.1; at r=5 the method reaches 0.083 after just 0.12 time units from an already
  developed state. The committed number is dominated by the rank-2 initialization on a
  rank-17 IC (R5m), as already diagnosed — but now there is a *proper* accuracy number
  to replace it, and it is 5–40× smaller.
- **The rank–accuracy curve is now measured, not assumed**, and it is monotone, which is
  what a rank-truncation method should look like. Combined with R12's energy table, the
  paper gets a coherent pair of statements: energy is captured at r≈5, trajectories are
  accurate at r≈32, and enstrophy is the demanding metric in between.
- **No accuracy claim should be made beyond ~10 time units** without re-measuring the
  background, and the background has not been measured at all until now.

## 4. Requests

**For coder:** the lockstep harness is the right instrument and should become the
standard accuracy measurement, with the two validation assertions built in (full-rank
error ≈ 0, background start ≈ the perturbation size) so the harness can never again be as
silently wrong as mine was. Please report the rank–accuracy curve at N=64 and N=256, and
add a test that the background control behaves as expected — a test on the *harness*,
which is the lesson of §0.

**For writer:** correction to what I sent you in R12. Please do **not** write that the
method "is not error-amplifying". The accurate sentence is: *truncation introduces no
per-step amplification of the discarded components, but the accumulated trajectory error
grows smoothly, at a rate controlled by rank, reaching 8% at r=32 over three time
units.* And the regime description should be **slowly evolving, mean-dominated, weakly
chaotic** with λ ≳ 0.69/time unit and O(1) decorrelation only beyond ~30 time units —
not "turbulent dynamics", and specifically not at any horizon the project has run.

## 5. Limits

- λ is a lower bound from one smooth perturbation direction; a proper estimate needs
  several random directions and a fit, and I have not done it.
- The error growth was measured over 3 time units from t=2. Longer horizons will show
  whether the growth stays exponential or turns over, and I have not tested that.
- All measurements are A=0.5, Re=5000, N=64. The rank ordering should hold elsewhere but
  I have not verified it at Re=1000 or at N=256, and Re=100 is quasi-laminar (R8a) so
  the ranking there is not obviously meaningful.
