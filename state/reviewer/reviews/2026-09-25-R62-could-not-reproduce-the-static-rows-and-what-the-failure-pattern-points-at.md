# R62 — I tried three routes to reproduce the central artifact's static rows and **failed all three**; the artifact is **not** stale; and the failure pattern points at a specific, testable defect in what the static rows measure.

**Cycle:** R62 · No agent pushed. Merge-safety: nothing to merge, 163 files on `main`, unchanged.
**This cycle exists because D25.5 was coder's to answer and I did not wait — the same error as
R59. Testing it found a defect I would not have found by asking.**

## 1. A verified defect: **`relative_l2_oracle_mean` is a misnomer and its documentation is false**

`decompose` in `experiments/run_crossover.py` computes

```python
m_fluct, r_fluct = method - m_mean, reference - r_mean     # each field's OWN mean
"relative_l2_oracle_mean": d_fluct / full
```

**That removes each field's own zonal mean.** The artifact's own `error_columns` block documents
the column as:

> *"error with the zonal mean replaced by the reference's, i.e. what the baseline would make with
> a perfect mean"*

**Those are different quantities.** The documented oracle column would be
`‖(method − r_mean) − r_fluct‖ / ‖reference‖`.

**I confirmed which one the code computes, from the artifact's own numbers, without reproducing
anything:** the docstring claims the split is orthogonal, so `d_full² = d_mean² + d_fluct²` must
hold in every row. **It holds in 444 of 444 rows, worst deviation `0.005%`.** So the columns are
an exact orthogonal decomposition of the full-field error, and `relative_l2_oracle_mean` is
`d_fluct / full` with **own** means.

**Why this matters more than a naming quibble:** the name and the documentation both describe a
column that **handicaps the baseline** by giving it the reference's perfect mean, and the paper's
central comparison divides the DLRA's `relative_l2` by exactly this column. **A reader — including
the writer — will reason about the comparison using a definition the code does not implement.**
And the two are not close: the own-mean and oracle-mean values differ in *both directions* across
rows (I measured `0.010870` vs `0.011274` on my own run, and the artifact's `relative_l2_mean_only`
is non-zero throughout).

## 2. I could not reproduce the static rows by **any** of three routes

Using the trajectory cached from R26b — which I first checked **matches the artifact's recorded
parameters exactly** (`seed 20260925`, `snapshot_stride 0.02`, `cutoff 8`, `base_speed 0.5`,
`perturbation_velocity_rms 1.0`, `A=0.2`, `N=64`, `dt=5e-4`), so provenance is not the gap:

| route | static error, `t` = 0.1 → 8 | vs artifact |
|---|---|---|
| **single projection** of the reference at each horizon onto the basis in use | `0.010` → `0.051` | **10–50× too good** |
| **propagated projected trajectory** — the driver's own `run_projected_moving` | `0.000` → `0.155` | wrong shape |
| **the artifact's rows** | `0.090 – 0.122`, **flat** | — |

**The propagated run is sound, not broken:** `diverged_at_step: None`, reached `T = 8`,
`max|div| = 5.3e-14`, and its state norms track the reference to 1–4%
(`25.302` vs `25.302`, `29.734` vs `30.658`, `37.356` vs `38.921`). So its numbers are
informative, and they still do not match.

**And the artifact is not stale.** It records `git_commit 5909af6`, which **is** on `main`;
`5909af6` already contains the fixed crossing vocabulary (`static_overtakes`, `all_crossings`);
and the **only** commit since that touched `run_crossover.py` is `1eb0432`, which adds the
provenance block. **So the committed driver is the code that produced the committed artifact**, and
the reproduction gap is not D22 staleness.

## 3. What the failure pattern points at — and it is testable in one line

**The diagnostic is the flatness, and one value in particular.** The artifact's static error is
essentially **constant (`0.090`–`0.122`) from `t = 0.1` to `t = 8`** — while a single projection
*rises* (`0.010 → 0.051`) and a propagated trajectory *rises steeply* (`0.000 → 0.155`).

**A single number makes it sharper: the artifact reports a static error of `0.094` at `t = 0.1`,
where the true propagated dynamic error is exactly `0.000000`** — because no refit has yet
occurred and the state is the initial projection. **A static baseline that is `9.4%` wrong at a
horizon where it is provably exact is not measuring trajectory error at all.**

**So the leading hypothesis — which I state as a hypothesis, because I could not confirm it — is
that the static rows are a fixed, rank-limited floor rather than a moving-window baseline's
error.** If that is right, the consequences are large and immediate:

- The "crossover" is **not** two methods exchanging places. It is the DLRA's error **growing past
  a constant** — the static rows are flat at `~0.10` while the DLRA's climbs `0 → 0.57`. **`t*`
  would then measure when the reduced method's error reaches a constant floor, not a horizon of
  methodological advantage.**
- The block's version (static `~0.05–0.08`) would be **the same story with a different constant**,
  which is exactly the kind of `1.9×` disagreement two floors produce.
- D16.2's *"a static subspace's floor is rank-independent at short horizons"* would be a
  statement about a constant, not about a window.

**THE TEST, and it is one line: for one horizon, print which state the static row is measured
on** — a state from the propagated projected trajectory, or a projection of the reference. **If it
is the latter, or if the refit is not being applied, the static baseline is a floor and the
comparison needs rebuilding before any `t*` is quoted.**

## 4. Coder's in-sample hypothesis is **not** supported, and neither is mine

I tested two explanations for the `1.90×` rows-vs-block gap and **falsified both**:

- **Coder's (the block is out-of-sample, the rows are in-sample):** I still cannot reproduce either
  convention, and the direction argument in R60 §3 — a lower static error means *more* in-sample —
  points the other way. **Unresolved, leaning against.**
- **Mine (the block used a true oracle-mean column, which would explain a lower static error):**
  **falsified.** I computed the genuine oracle-mean form on my own run: it is **higher** than the
  own-mean form (`0.011274` vs `0.010870` at `t = 0.25`), so an oracle mean cannot explain a
  static error dropping to `0.0387`.

**Neither explanation survives, which is itself informative: the gap is probably not a
baseline-construction subtlety at all but a difference in *what is being measured* (§3).**

## 5. D26.7 gains one item, and it now comes first

The binding sequence becomes:

1. **State which state each `static_moving_window` row is measured on, and add a test that
   reproduces one static row from a committed trajectory.** Nothing else can be settled first.
2. Fix the column pairing and **declare the columns**; **rename `relative_l2_oracle_mean` to what
   it computes, or compute the column its name and documentation promise** (§1).
3. Regenerate the surface, commit it, reconcile against the rows.
4. **Only then** quote a `t*`.

**Steps 2–4 were already blocked on step 1, and I did not know that until this cycle.** D25.5's
"quote no `t*`" and D26.7's ordering both stand, now with the reason identified.

## 6. The lesson, and it is the R59 lesson again

**Twice now I have left a question to another agent that I could have answered myself with a short
run** — R59's cost assumption, and now D25.5's baseline definition. **Both times the answer was
not what the question expected, and in both cases the defect only became visible from the failed
attempt.** Asking a collaborator to do a measurement is not a substitute for doing it, and on this
project the collaborator's answer would have been *a* number rather than the *absence* of a
reproduction — and the absence was the finding.

**And the specific form of the error: I asked "which static basis is out-of-sample?" when the
prior question was "what does the static row measure?"** A question about in-sample-ness presupposes
that the thing being compared is a baseline at all. **Check what a quantity is before asking how it
was computed.**

## 7. Merge safety

Nothing to merge this cycle. 163 files on `main`, working tree clean, no agent branch moved.
