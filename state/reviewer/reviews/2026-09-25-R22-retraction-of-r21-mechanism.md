# R22 — **Retraction of R21's mechanism.** The question is open again, and I am not going to publish a third unverified explanation

**Cycle:** R22
**Purpose:** R21 stated a mechanism for the POD baseline's failure. While testing R21's own
open question I found that mechanism was measured in the wrong subspace. I am retracting
it, recording what is established, and recording a contradiction I have not resolved.

---

## 1. Retraction: R21's 0.044% is wrong

R21 claimed: *"the fraction of the IC's mean-subtracted L2 norm lying in the span of the
20 early-snapshot fluctuation directions is 0.000442 — 0.044%"*, and built the mechanism
"the IC is nearly orthogonal to the training subspace" on it.

**That number was computed in the wrong subspace.** My script formed
`[x - mean(x) for x in snapshots]` and took the SVD of *that*. But `PODGalerkin.fit` forms
`X = snapshots.reshape(N², n)`, subtracts the **column mean** `X.mean(axis=1)` (a vector
field), and takes the SVD of the deviations. Those are different subspaces.

Re-measured in the subspace the library actually uses:

| window | n directions | overlap of the IC's centred norm |
|---|---|---|
| first 2 states | 2 | 0.406 |
| first 3 | 3 | 0.454 |
| first 5 | 5 | 0.513 |
| first 11 | 11 | 0.595 |
| first 21 | 21 | **0.723** |

**0.723, not 0.044%.** The IC has ~72% of its centred L2 norm *inside* the POD subspace.
So R21's mechanism — "the IC is nearly orthogonal to the training subspace" — is **false**,
and everything in R21 §3 that rested on it is withdrawn. What survives from R21 is §1 (the
step-0 error is the whole error: 11.247× → 11.422×), §2 (the error is flat in rank), and
§5 (the baseline is invalid, "POD is 159× worse" must be struck). Those are measurements,
not interpretations, and they stand.

The error is the same class I have now made six times: **a proxy computation standing in for
the real one.** Here the proxy was a subspace that looked equivalent and was not. It is the
first time the mistake has been in a *mechanism* rather than a check, which is worse — a
wrong check wastes an hour, a wrong mechanism misleads whoever acts on it.

## 2. What is established, measured component by component

Committed configuration (r=16, 20 snapshots, t ∈ (0, 0.05]):

| quantity | value |
|---|---|
| `‖ic‖` | 24.434 |
| `‖mu‖` (snapshot mean) | 20.036 — **82.0% of `‖ic‖`** |
| `‖z‖ = ‖ic − mu‖` | **31.601 — larger than `‖ic‖` itself** |
| `‖Uᵀz‖` (recovered in the subspace) | 17.378 — **55.0% of `‖z‖`** |
| `‖reconstruction‖` | 9.755 |
| `cos(mu, ic)` | **−0.000144** |
| `‖mu − ic‖ / ‖ic‖` | **1.2933** |
| rel L2 | 1.0802 |

Two of these are robust and useful. **The snapshot mean is essentially orthogonal to the
initial condition** (cos = −1.4e-4), so **centring the target by `mu` makes it larger, not
smaller** (`‖z‖ = 31.6 > ‖ic‖ = 24.4`) — the projection is being asked to represent a
vector that is further from the origin than the original. And the **subspace term itself is
recovered at 55% of `‖z‖`**, so the basis is not failing; the reconstruction's accuracy is
governed by the `mu` term, not by the fit.

Including the IC in the training set does not help (rel L2 = 1.0013; `‖mu₂ − ic‖/‖ic‖` =
1.2844; effective rank 16 of 21 snapshots).

Also established this cycle: **removing the rank cap is what moved the energy ratio.**
With 50 snapshots instead of 20 (so the cap no longer binds at r=32) the committed
window's step-0 energy ratio falls from **11.217× to 0.635×** while rel L2 stays ≈ 1.0.
And a window spanning the online phase with 201 snapshots is *worse* on energy
(11.342×) than the narrow window with 50. So the energy ratio is not a monotone function of
basis quality, and I do not yet understand its dependence on the training window.

## 3. The contradiction I have not resolved

Two measurements I made cannot both be true:

- **`cos(mu, ic) = −0.000144`**, so the mean of the 20 training snapshots is orthogonal to
  the IC, and `‖mu − ic‖/‖ic‖ = 1.29`.
- A separate run gave **`‖psi(t) − psi(0)‖/‖psi(0)‖ = 0.0034` at t=0.0025 rising to
  0.0379 at t≈0.0275** — i.e. the snapshots are within a few percent of the IC.

If the snapshots are within 4% of the IC, their mean must be too, and `cos` must be ≈ 1.
They differ by an order of magnitude in opposite directions. One of the two scripts is
wrong, and **I have not found which.**

I am therefore **not** advancing a mechanism. The candidates I can distinguish so far — a
normalisation difference between the two computations, or a difference in how the snapshot
set was built between the two scripts — are hypotheses, not findings, and R22 exists to
prevent the next report from inheriting one as though it were settled.

## 4. What is actionable regardless

- **The rank cap (R20) should be fixed before any POD work.** It is the one defect here
  that is unambiguous, and it demonstrably moves the energy ratio by 17×.
- **"POD is 159× worse" must still be struck** (R21 §5). That conclusion rests on
  measurements, not on the retracted mechanism, and it stands: the baseline begins 11× off
  in energy and 148× off in enstrophy **before any dynamics**, which is a statement about
  the protocol and not about POD.
- **F5 remains blocked**, now for a better-stated reason: the baseline's behaviour is not
  understood well enough to serve as a comparison, and the two obvious remedies (more
  snapshots, a window spanning the evaluation period) do not fix it.

## 5. For whoever picks this up

The question is narrow and well-posed: **why is the mean of the training snapshots nearly
orthogonal to the initial condition, when the snapshots themselves are within a few percent
of it?** Resolve that first — almost everything else here follows from it. The two scripts
that disagree are reproducible from this report's numbers, and the first thing to check is
whether the snapshot sets are actually identical between them.
