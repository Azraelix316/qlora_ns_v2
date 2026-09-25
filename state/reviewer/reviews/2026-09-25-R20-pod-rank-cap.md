# R20 — `PODGalerkin.fit` silently caps the rank at the snapshot count. It has not corrupted the committed runs, and it **will** corrupt F5

**Cycle:** R20
**Scope:** `solvers/pod.py`, F5 of the D10 gate
**This is a latent bug with a narrow blast radius today and a wide one the moment the
gate's matched-rank comparison is run.** It also corrects the prioritisation of R5l's
finding, and refutes the hypothesis I reached for before measuring.

---

## 1. The defect

`PODGalerkin.fit` (`solvers/pod.py`) builds `X` with shape `(N², n_snapshots)`, then:

```python
U, s, _ = np.linalg.svd(centered, full_matrices=False)
r = min(self.requested_rank, U.shape[1])
self.basis = U[:, :r]
```

For an `(N², n)` matrix with `n < N²`, `full_matrices=False` returns `U` with **exactly
`n` columns**. So `U.shape[1]` is the **number of snapshots**, not the matrix dimension,
and the requested rank is silently clamped to it. Verified directly:

| snapshots | requested 5 | 10 | 20 | 40 |
|---|---|---|---|---|
| 5 | 5 | **5** | **5** | **5** |
| 10 | 5 | 10 | **10** | **10** |
| 11 | 5 | 10 | **11** | **11** |
| 20 | 5 | 10 | 20 | **20** |

No warning, no error, and `effective_rank()` reports the clamped value — so the
information is recoverable from the artifact, but nothing forces a reader to look.

## 2. Blast radius: the committed runs are clean, F5 is not

The committed Re=5000 N=64 run used `pod_rank: 16` with `train_steps: 100` and
`snapshot_stride: 5`, i.e. **20 snapshots**, so the cap does **not** bind
(`16 ≤ 20`). **No committed POD result is affected, and I am not claiming otherwise.**

F5 is where this bites. F5 requires **static POD at matched rank** against a method whose
working rank R11 measured as `2·floor(N/3)+1` — **43 at N=64 and 85 at N=128**. At N=64
with 20 snapshots, **every matched rank above 20 is silently clamped**, so the comparison
the gate exists to make would be run at a lower POD rank than the paper states, in the
direction that flatters the proposed method. A paper reporting "POD at rank 43" when the
artifact says 20 is a straightforwardly indefensible result, and it would be produced by
code that raises nothing.

**Required, in order of preference:** (a) take at least `max_rank_of_interest`
snapshots, so the cap cannot bind for any rank the gate uses; (b) if that is too
expensive, **assert** `requested_rank <= n_snapshots` in `fit` and fail loudly rather than
clamping; (c) at minimum, record both `requested_rank` and `effective_rank` in the
artifact and have the comparison refuse to compare unequal ranks. (b) is the cheapest
correct fix and I would take it today; (a) is what F5 actually needs.

## 3. Two corrections to my own work

**R5l's prioritisation was wrong, and I am the one who set it.** R5l reported that
`PODGalerkin.project` is **non-idempotent**, and I recorded it as a finding to fix. I have
now measured it: applying the projector repeatedly drifts by **4.5e-11 at rank 5** and
**~1e-8 at ranks 10 and 20**, with the spatial mean moving by ~1e-18 per application —
i.e. roundoff. **The non-idempotence is real and dynamically irrelevant**, and it is not
worth the attention R5l and I gave it. The defect in the same class of code — the rank cap
— is the one that matters, and it is more serious. R5l found both; the ordering was mine
and it was backwards.

**My hypothesis before measuring was wrong.** Suspecting an offline-window mismatch
against the secularly growing mean (R8a), I tested it by refitting the basis on a window
that *includes* the evaluation time. The error did not improve (1.3003 → 1.2786). The
real explanation is the rank cap, and the tell was that **POD's error was flat at ~1.29
from r=5 to r=43 while the best possible rank-43 truncation of the same field is
2.4e-15**. A rank-*independent* error is not a rank problem, a window problem, or a
POD problem — it is a constant, and constants come from the rank never having changed.
Had I asserted the window hypothesis instead of testing it, I would have sent coder to
re-fit baselines and fixed nothing.

## 4. What this says about the "broken baseline", honestly

The committed POD baseline is reported as catastrophic — **11.4× energy, 159× enstrophy,
relative L2 > 1** (R5m). **This bug does not explain that**, because the cap does not bind
at `pod_rank = 16` with 20 snapshots. I am not going to attach a tidy explanation to a
number I have not accounted for.

What is *established* is that the cap is latent, that it will corrupt F5, and that the
non-idempotence I flagged in R5l is noise. The committed baseline's failure therefore
remains **unexplained**, and the leading candidates are the ones already recorded: the
`t=0.1` transient means the comparison is between two different initial conditions (V1),
and at `t=0.1` the field is nowhere near any statistical state (R8/R8a). F5 should not be
run until V1 is fixed, and **when it is run the rank cap must be fixed first**, or the
comparison will be made at ranks nobody asked for.
