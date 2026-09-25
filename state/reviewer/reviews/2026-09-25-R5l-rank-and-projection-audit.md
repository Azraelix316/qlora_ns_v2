# R5l — independent audit of the rank/projection logic: one contract violation, no dynamical effect

**Date:** 2026-09-25 · **Reviewer cycle:** R5 (addendum 6) · **Target:**
`solvers/dlra.py` (`SVDProjector`, rank adaptation) and `solvers/pod.py`
(`PODGalerkin`) on `main` · **Companion:** `reviews/2026-09-25-R5k-engine-operator-audit.md`

R5k audited the spectral operators and deliberately left the rank/projection
logic uncovered — that is the component the paper's *adaptive rank* claim rests
on, so it deserved the same treatment.

## Result

35 checks written; 27 passed as written. **Seven of the eight failures were
defects in my harness** (five used an inverted boolean encoding, two used a
zero tolerance where roundoff was expected). **One real finding**, appearing as
two checks, below. The rank logic itself is sound.

### Verified correct

- **Rank rule** is exactly `#{σ_i > tol·σ_1}`, clipped to `[min_rank, max_rank]`,
  with an all-zero spectrum falling back to `min_rank` — checked against
  brute-force counts on hand-built spectra.
- **`project` is the Eckart–Young rank-r truncation.** For r = 1, 3, 5 the
  reconstruction matches an independent `numpy.linalg.svd` truncation to
  **0.0**, and its residual equals `sqrt(Σ_{i>r} σ_i²)` to ~3e-15 — i.e. it is
  not merely *a* rank-r approximation, it is the *optimal* one.
- Factor bookkeeping: `U` and `V` columns orthonormal to 9e-16 / 3e-15;
  `last_stats.target_rank` tracks `projector.rank`; `numerical_rank` matches a
  brute count; `last_singular_values` is a copy, not an alias.
- **Mean/gauge handling is correct in `SVDProjector`**: the reconstruction stays
  at numerical rank r (the docstring's claim that no mean is re-added is true).
- **Rank adaptation reads the retained candidate, not the projected state**:
  `adapt_candidate` sets the rank from the candidate's own spectrum and returns
  exactly its tolerance-truncation (0.0 difference), and it grew the rank from
  2 as expected. This is the specific R4 checklist item, independently confirmed.
- **Stage candidates are retained separately per stage**, and `candidate()`
  returns the right one.
- Input validation: `max_rank` is clamped to the grid size; non-integer rank,
  `rank < min_rank`, tolerance outside `(0,1)`, non-finite states and
  wrong-shaped states all raise (I confirmed each raises the expected exception).
- `PODGalerkin.fit`: basis equals the top left singular vectors (0.0), singular
  values match (0.0), mean equals the snapshot mean, `fit_pod` agrees with the
  class, `effective_rank` is as requested.

## The finding: `PODGalerkin.project` is not a projection

`project` ends with

```python
return out - np.mean(out)
```

The stored mean is spatially mean-free, but the **basis columns are not** (in my
test the second column had spatial mean 3.4e-3). So `mean + basis @ coeff`
generally has a nonzero spatial mean, and that trailing line shifts the result
*out* of the subspace `mean + span(basis)`. Consequences, measured:

- `max |project(q) − least-squares projection| = 2.2e-3` — it is not the
  orthogonal projection that `relative_error()` assumes it is.
- `max |project(project(q)) − project(q)| = 1.4e-3` — **not idempotent**. A
  projection should satisfy `P² = P`; this one does not.
- The discrepancy is *exactly* a constant: `out = project(q) + mean(out)` to
  3.5e-18.

Deleting that one line restores both properties exactly: the projection equals
the least-squares projection to **0.0** and is idempotent to **2.2e-16**.

## Scope: a contract bug, not a dynamical one — and a hypothesis I tested and dropped

My first thought was that a non-idempotent projection applied at every POD step
might help explain V4's finding that the POD baseline reaches 11.4× the
reference energy. **It cannot.** The mean of ψ is a pure gauge for
`u = ∇⊥ψ`, and the velocity difference between the shifted and unshifted
projections is **1.3e-15**; `StreamFunctionNS.step` also re-centres the state at
the start of every step. V4's cause remains what the R5 report identified: the
POD run replaces its initial state with `mean + top-r modes` fitted on a
transient window, changing the state by an order of magnitude before `t=0`.

So the finding is bounded and honest: it affects the **contract** of
`project` — and therefore the POD reconstruction errors that
`relative_error()` reports and the sense in which a "POD-Galerkin" step is a
Galerkin step — but not the trajectories. Since the POD baseline is being rebuilt
anyway under V4, this should be fixed before it is used, not after.

**Recommended fix** (coder's call): drop the trailing `out - np.mean(out)`; the
gauge is already handled by `step`. If a spatially mean-free basis is wanted
instead, subtract each basis column's spatial mean at fit time, which keeps the
subspace and the idempotence consistent.

## Checklist consequence

Added to `CHECKLIST.md` §1.4: a projection API must be **idempotent** and must
match an independent least-squares reference, checked on a field whose basis
vectors are not mean-free. The engine's `SVDProjector` passes both; `PODGalerkin`
currently fails, and no existing test would have caught it because the test
fields are all single-mode or two-mode combinations whose projections happen to
be mean-free.
