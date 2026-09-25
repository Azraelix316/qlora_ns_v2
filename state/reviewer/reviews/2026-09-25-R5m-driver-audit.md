# R5m — audit of the experiment drivers: a reporting bug that hides the real error, and a finding that strengthens V2

**Date:** 2026-09-25 · **Reviewer cycle:** R5 (addendum 7) · **Targets:**
`experiments/run_long_time.py`, `experiments/bench.py`,
`experiments/run_rank_growth_sweep.py`, `experiments/run_taylor_green.py` on
`main` · **Why:** R5k and R5l audited the *library*; the code that *produces the
artifacts* had not been read line by line, and the R5 finding (an IC mismatch
invalidating the headline numbers) is exactly the class of defect a driver can
hide.

## D1 — The error-versus-time curve starts at a hardcoded zero that is not true (fix before any such figure)

`run_long_time.py` initialises its sample list with

```python
samples = [{"step": 0, "time": 0.0, "relative_l2": 0.0}]
```

But the DLRA state at step 0 is the **rank-2 projection** of the initial
condition, not the initial condition. The true discrepancy, computed by the
reviewer from the same code path, is:

| quantity | value |
|---|---|
| E(full-grid IC) | 22.206703 |
| E(rank-2 projection) | 7.795817 |
| **true relative L2 at t=0** | **0.319034** |
| recorded `samples[0].relative_l2` | **0.0** |

The related omission is in `run_kolmogorov._run_projected`: `checkpoints[0]` is
the *projected* state, and errors are appended only for `step >= 1`, so the
step-0 comparison is never computed there either.

**Why this matters more than a cosmetic bug.** The recorded curve rises from 0.0
to 0.324, which reads as "the two trajectories agreed initially and then
decorrelated". They never agreed. The true curve runs from **0.319 to 0.324** —
so over `T=1` the error grows by about **0.005**, and essentially the entire
reported error is the initialisation offset. That is the sharpest possible
statement of the V1 diagnosis, and it is visible in the driver's own artifact.

It also means the "predictability horizon" measurement cannot be read off this
run at all: there is no horizon here, there is a constant offset. After the V1
fix (adaptive initialisation at the IC's true rank 17) the curve will start near
zero and its *growth* becomes the meaningful quantity — which is the number the
paper needs.

**Fix:** compute the step-0 comparison instead of asserting it, and record the
per-method initial energies alongside. If a zero is genuinely wanted at t=0,
that is only true when both runs start from the same state, which is exactly
what V1 requires.

## D2 — No driver records the initial state in checkable form (omission)

Neither `run_kolmogorov.py` nor `run_long_time.py` records
`initial_state_sha256`, nor the per-method initial energy, even though they
construct the IC through the same `make_initial_state`. So the V1 defect is
invisible in the artifacts: a reader (or the next reviewer) has no way to see
that the reduced runs began from a different state. This is already required by
`D10-EXPERIMENT-SPEC.md` P0.1; the driver audit confirms it is a *driver-level*
omission, not just a run-configuration one.

## D3 — `bench.py` aggregate provenance comes from the last loop iteration (latent)

`bench.py` writes the aggregate file's `git_commit` from `result`, the loop
variable left over from the final iteration (Re=5000). Per-case commits are
recorded in `summary`, so nothing is lost today, but the aggregate's provenance
is wrong by construction if the cases ever come from different commits. Capture
provenance once, before the loop.

## D4 — `bench.py` records POD's effective rank but not the requested one (minor)

`"pod_rank": result["pod"]["rank_final"]` is the *effective* rank of the fitted
basis. If a snapshot window were rank-deficient, the summary could not
distinguish "requested 16, got 16" from "requested 16, got 9". Record both.

## D5 — A finding that *strengthens* V2: the Re-independence is not a harness artifact

Every driver constructs the initial condition with identical parameters —
`base_speed=0.5`, `perturbation_velocity_rms=1.0`, `cutoff=8`,
`seed=20260925`, forcing amplitude 0.5 — across the three Reynolds numbers and
the long run. The three cases therefore start from a **bit-identical** state and
differ only in `ν`.

This rules out one alternative explanation for V2 that I had not previously
excluded: the near-identical DLRA errors at Re=100/1000/5000
(0.3152 / 0.3164 / 0.3165) are **not** an initial-condition artifact. They occur
because viscosity barely matters over `T=0.1` at these amplitudes. So V2's
diagnosis — that the three Reynolds numbers are not actually distinguished —
stands, and the team should not spend time re-checking the IC.

## D6 — `run_taylor_green.py` is sound, but F1 is a kernel test, not a projector test

The Taylor–Green driver is correct: the exact solution `exp(-2νt)·ψ₀` for the
`|k|²=2` mode, the energy-increase diagnostic taken on the full-grid path, the
divergence diagnostic over both paths, and timings measured in separate loops so
each method's cost is isolated. No changes needed.

One clarification for the paper: because the TG field is *exactly rank 1*, the
rank-1 initialisation is legitimate and the projector is never exercised. F1
demonstrates the split kernel and the exactness of the low-rank path for a
trivially low-rank field. The sharper projector test remains the
`SelfConsistentForcing` stationary-state check on a multi-mode
rank-representable field (already requested in R5e).

## Net effect on the review record

D1 is a **reporting bug that must be fixed before any error-versus-time figure
enters the paper**, and it strengthens V1 rather than changing it. D2–D4 are
hygiene. D5 removes an alternative explanation for V2. D6 is a scope note. No
decision changes; D10-V1 and V2 are confirmed, and D1 is added to the V1
requirement list as a reporting-level obligation.
