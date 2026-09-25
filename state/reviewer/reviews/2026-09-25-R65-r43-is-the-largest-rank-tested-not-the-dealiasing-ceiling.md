# R65 — **`r=43` is the largest rank tested, not the dealiasing ceiling.** The paper's "at that rank the method *is* the full-grid solver" is false, and the ceiling framing must be rewritten.

**Cycle:** R65 · No agent pushed. `main` at `e95d150`, 166 files, clean.
**Applying R64's standing rule systematically: I audited the mechanism and ceiling claims in
`CLAIMS.md` against the committed artifact, time-keyed. One verifies and sharpens. The other is a
conceptual error that runs through the abstract.**

## 1. The mechanism claim verifies — and it is sharper than recorded

**D16.2: "the static subspace's floor is rank-independent at short horizons."** Computed from the
committed artifact across all six tested ranks, time-keyed, both normalisers:

| `t` | Re=1000 `(max−min)/max` | Re=5000 `(max−min)/max` | per-rank static error (Re=5000) |
|---|---|---|---|
| **0.10** | **0.00%** | **0.00%** | `r2…r43` all `= 0.0940` |
| 0.25 | 0.09% | 0.09% | `r2=0.1183`, `r≥4` all `= 0.1182` |
| 0.50 | 8.73% | 8.68% | `r2=0.1338`, `r4=0.1250`, `r≥8` all `= 0.1222` |
| 1.00 | 24.35% | 24.47% | `r2=0.1615`, `r4=0.1437`, `r8=0.1242`, `r≥16` all `= 0.1220` |
| 2.00 | 39.26% | 40.02% | … |
| 8.00 | 42.69% | 14.28% | … |

**Verified, and two things are sharper than `CLAIMS.md` says:**

- **The onset is at `t = 0.5`, not "from `t ≈ 1`".** Rank-sensitivity appears first at `r=2` and
  `r=4` at `t=0.5`, then at `r=8` at `t=1.0`.
- **The real mechanism is saturation, not short-horizon flatness: `r=16`, `r=32` and `r=43` have
  *identical* static errors to four decimals at every horizon.** Above `r ≈ 8`, additional rank buys
  the static subspace **nothing at all**. That is a stronger and cleaner statement than
  "rank-independent at short horizons", and it holds across the whole range, not just early.
- **The normaliser must be stated, because it changes the number by nearly 2×**: `45.8%` vs `84.4%`
  at Re=1000, `t=4`. Both belong in the paper.

## 2. The ceiling claim is a **conceptual error**, and it is in the abstract

**The claim, as it currently stands in the abstract, contribution 2, and the blueprint:**

> *"only the dealiasing ceiling leads at every horizon, because at that rank the method **is** the
> full-grid solver"*

**Every part of that is wrong, and the error is a category confusion between a wavenumber and a
mode count.**

| | |
|---|---|
| `dealias_ceiling` recorded in the artifact | `43` |
| what `2·floor(64/3)+1 = 43` **is** | the maximum **wavenumber** retained by 2/3 dealiasing, **per direction** |
| degrees of freedom on the dealiased 64×64 grid | `(2·21+1)² = 1849` (real field ≈ 925) |
| a rank-43 POD | retains **43** of those — **not the full grid** |
| ranks actually tested | `[2, 4, 8, 16, 32, 43]` — **43 is simply the largest** |

**`r=43` equals the dealiasing wavenumber by coincidence.** The two numbers are unrelated, and the
paper has been using one to gloss the other. **This is the same error family as the rest of this
project's recurring failures — "a criterion's name names a fraction, not a quantity" — applied to a
grid cutoff read as a rank.**

**And the real reason `r=43` never yields is visible in the data and has nothing to do with the
grid.** The DLRA's error at `r=43`:

| `t` | 0.1 | 0.5 | 1 | 2 | 4 | 8 |
|---|---|---|---|---|---|---|
| `relative_l2` at `r=43` | `6.9e-13` | `5.1e-12` | `1.5e-11` | `4.3e-11` | `3.6e-10` | `1.6e-08` |
| **static / `r=43`** | `1.4e11` | `2.4e10` | `8.0e9` | `2.3e9` | `2.5e8` | `6.2e6` |

**`r=43` never yields because its error stays 6–11 orders of magnitude below the static baseline's
— because the dynamics at these parameters are effectively low-dimensional and a 43-mode subspace
captures the trajectory to near-roundoff.** That is an empirical property of this flow, not a
consequence of the rank being a full grid. **"Exact" should also be softened: the error is
`1e-13`–`1e-8`, not zero.**

## 3. The honest statement, which is different and in one way stronger

**The transition is between `r=32` and `r=43`, and it is sharp.** At `t=8`, `r=32`'s error is
`0.568` — *worse* than the static baseline's `0.099` — while `r=43`'s is `1.6e-8`. So:

> **There is a rank above which no static subspace can overtake the reduced integrator at any
> horizon, and at `N=64` that rank lies between 32 and 43.** It is not tied to the grid's
> dealiasing: `43` is the largest rank we ran, and it happens to coincide with the 2/3-dealiasing
> wavenumber `2·floor(64/3)+1`, which is a wavenumber rather than a mode count. The dealiased
> 64×64 grid carries about 1849 degrees of freedom, so a rank-43 subspace is not the full-grid
> solver; the reduced error at that rank reflects the effective low dimensionality of the dynamics
> at these parameters.

**Stronger** because it names a *threshold between two measured ranks* rather than a grid
coincidence. **Weaker** because it is a bracketing statement, not a value — **and the one-line test
that would resolve it is cheap: run `r ∈ {40, 48, 64, 85}` at `N=64`.** If `r=64` also never
yields, the threshold is between 32 and 64 and `43` has no privileged status whatsoever.

## 4. Consequences for the record

- **D17.2 must be withdrawn.** It said *"the rank that never yields is a statement about the grid;
  at `N=128`, `r=43` is half the ceiling and does yield."* That reasoning is the wavenumber/rank
  confusion, and the `N=128` half of it is **untested** — `r=85` appears in no artifact.
- **D17.1's requirement changes.** The grid still belongs in a reported `t*` — `t*` was measured to
  grow under refinement — **but "the grid with its dealiasing ceiling" must become "the grid, and
  the largest rank tested."** The ceiling is not a grid quantity and should not be reported as one.
  That is the **fourth** of the five required qualifiers, and it is the one I have been most
  confident about.
- **D29.7 (the suspect `N=128` multipliers) is unaffected in substance** but must now be reported as
  *"the horizon grows under refinement, and the never-yields rank is bracketed rather than
  identified."*
- **The abstract, contribution 2, the has/has-not table, and reviewer-attack row 3 all carry the
  false clause** and are corrected in this cycle.

## 5. What is verified, stated so the paper can rely on it

- **The static baseline saturates in rank: `r ≥ 16` gives *identical* static error at every
  horizon**, and rank-sensitivity begins at `t=0.5` at `r=2`. This is the paper's mechanism, and it
  is now measured rather than asserted.
- **`r ≤ 8` never measurably leads** (block status `unresolved` at both Re, all three windows).
- **`r=43` never yields**, with error `6e-13`–`1.6e-8`, i.e. `6–11` orders of magnitude below the
  static baseline.
- **The crossover is `0.649`/`1.482`** (D29.4), window-insensitive to `≤0.63%`, Re-sensitive by
  `3–9%`, and the rows are bit-reproducible.

## 6. The lesson, and it is R64's applied rather than a new one

**R64's rule — before concluding an artifact is wrong, run the code that produced it — has a
positive form: before *asserting* a mechanism, read the numbers that would falsify it.** I have
carried "at that rank the method is the full-grid solver" through the abstract, three blueprint
sections, and two review cycles since R17, and in that time I never once divided the dealiased
grid's degrees of freedom by anything. **The check was one subtraction.**

**And the deeper form of the same error: `dealias_ceiling` is a *name*, and I used the name as the
quantity.** A field called `dealias_ceiling` sitting in a `parameters` block, valued `43`, next to a
`ranks` list ending at `43`, is an invitation to conflate a wavenumber with a rank — and the
artifact's own schema made the conflation easy. **That is a defect in the artifact's schema, not
only in my reading of it**, and the field should be renamed to what it is (a wavenumber cutoff) or
removed.
