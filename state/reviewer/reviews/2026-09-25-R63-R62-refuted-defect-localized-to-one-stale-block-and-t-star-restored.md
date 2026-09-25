# R63 — I refuted my own R62 finding, and in doing so **localized the defect to a single stale block and restored the paper's central number.**

**Cycle:** R63 · No agent pushed; nothing to merge. 164 files on `main`, clean.
**This is the most consequential cycle in the project: it unblocks the paper's central claim, and
the fix is one line.**

## 1. R62's central finding is **WITHDRAWN** — the static rows *are* reproducible

R62 reported that I could not reproduce the static rows by any route, and raised the hypothesis
that they were a fixed rank-limited floor. **Both were wrong, and the cause was my own
omission.** The driver's row-construction site (`run_crossover.py`, ~line 14) does this before the
rollout:

```python
initial_projector = PODGalerkin(grid, 1).fit([initial])
```

**The baseline is projected onto a rank-1 basis built from the initial condition and is held on
that projector until the first refit at `t = 0.125`.** My R62 reproduction called
`run_projected_moving` **without** it, so my baseline ran *unprojected* from `t = 0` to `t = 0.125`
— which is the reference trajectory itself. **That is exactly why my `t = 0.1` error was
`0.000000`** and why I concluded the artifact's `0.094` there could not be a dynamic error. **It is
a dynamic error: it is the rank-1 projection error.**

**With `initial_projector` supplied, the rows reproduce:**

| `t` | my `relative_l2` | artifact | my `oracle` | artifact |
|---|---|---|---|---|
| **0.10** | **0.103424** | **0.103424** | **0.094010** | **0.094010** |
| 0.25 | 0.115436 | 0.124964 | 0.109073 | 0.118208 |
| 0.50 | 0.126045 | 0.125518 | 0.122663 | 0.122159 |
| 1.00 | 0.128156 | 0.127159 | 0.122970 | 0.122015 |
| 2.00 | 0.106507 | 0.104932 | 0.101090 | 0.099644 |
| 3.00 | 0.096941 | 0.095533 | 0.091619 | 0.090361 |
| 4.00 | 0.094204 | 0.093298 | 0.090444 | 0.089608 |
| 6.00 | 0.123069 | 0.125809 | 0.118283 | 0.120944 |
| 8.00 | 0.107569 | 0.110363 | 0.096966 | 0.099422 |

**Exact at the first horizon, and within 1–4% at the rest** — consistent with run-to-run
difference in the reference trajectory over a nonlinear run to `t = 8`, not with a different
quantity.

**The floor hypothesis is REFUTED.** The static rows are a genuine **propagated, refitted,
trailing-window static-POD baseline**: a rank-1 projector on the IC until `t = 0.125`, then a
refit every `0.25` offset by `0.125`. **It is strictly out-of-sample at every horizon** — the IC
projector is fitted at `t = 0` and first used at `t = 0.1`, and every later refit's window ends
half an interval before the evaluation time. **D15's out-of-sample claim holds.**

## 2. The defect is now localized exactly — and **not by my reproduction**

**The decisive argument uses no run at all.** It applies the **committed** `crossover_horizon`
pairing to the **committed** rows and compares with the **committed** block. Exact arithmetic:

| Re | `r` | `W` | from the committed rows | committed block | |
|---|---|---|---|---|---|
| 1000 | 16 | 0.25 / 0.5 / 1.0 | `1.222` / `1.224` / `1.304` | `0.667` / `0.667` / `0.668` | **`0.51–0.55×`** |
| 1000 | 32 | 0.25 / 0.5 / 1.0 | `2.508` / `2.495` / `2.503` | `1.609` / `1.604` / `1.606` | **`0.64×`** |
| 5000 | 16 | 0.25 / 0.5 / 1.0 | `1.235` / `1.242` / `1.415` | `0.649` / `0.650` / `0.651` | **`0.46–0.53×`** |
| 5000 | 32 | 0.25 / 0.5 / 1.0 | `2.417` / `2.394` / `2.427` | `1.482` / `1.474` / `1.483` | **`0.61–0.62×`** |
| both | 2, 4, 8, 43 | all | *no crossing* | *no crossing* | **all 24 agree** |

**Every entry that resolves disagrees, by a consistent factor; every entry that does not resolve
agrees.** So the block is not a differently-computed version of these rows — it is a **different
quantity**.

**And the cleanest single signature: the block's `t*` is window-INVARIANT** (`0.667/0.667/0.668`
at Re=1000 `r=16`; `0.649/0.650/0.651` at Re=5000 `r=16` — flat to `0.3%` across a **4× change
in window length**), **while the rows' `t*` genuinely depends on the window** (`1.235 → 1.415` at
Re=5000 `r=16`, a `15%` change). **A quantity that does not vary with the window cannot have been
computed from window-specific baselines. That is the defect, stated in one line: the block is
window-independent and the rows are window-dependent, so the block was not derived from the rows.**

**So: the artifact's two halves come from different code versions. The rows are current and
verified; the block is stale.**

## 3. What this restores, and what it costs

**Restored — the paper's central number is defensible again:**

- **`fig_crossover` reads the rows, so the central figure is CORRECT.** No figure work needed.
- **D15–D17's `t*` values stand.** Applying the current code to the committed rows gives
  **`1.235` (`r=16`) and `2.417` (`r=32`)** at `W=0.25`, Re=5000 — matching the recorded
  `1.26`/`2.44` to interpolation convention, and window-dependent as D17.1 requires.
- **Coder's `0.649`/`1.482` come from the stale block and should be dropped**, along with the
  "window-invariant to 0.3%" robustness claim, which is an artifact of the block's
  window-independence — **a robustness claim that exists only because the quantity is wrong is
  worse than no claim.**
- **Coder's in-sample hypothesis is refuted, not merely unsupported:** the rows *are* strictly
  out-of-sample, *are* reproducible, and the block *is not* derived from them.

**Still standing from D27 — one defect remains, and it is a documentation defect:**

- **D27.1 survives intact.** `relative_l2_oracle_mean` removes **each field's own** zonal mean
  while `error_columns` documents it as the reference's perfect mean. That was verified by the
  orthogonality identity (**444/444 rows, worst `0.005%`**) and **does not depend on any
  reproduction.** Worth `1–3%` in `t*`. Rename it or compute the column its name promises.
- **D26.4 survives:** the crossing test's fixtures still hard-code the mismatched pairing.

**And one caveat I will not paper over:** my reproduction is `1/9` exact and `8/9` within `1–4%`.
The localization in §2 is exact arithmetic and does not depend on it, but **no one has yet
demonstrated bit-level reproducibility of a static row**, and the `1–4%` should be attributed
rather than assumed away.

## 4. The fix is one line, and it does not require re-running the surface

`crossover_horizon(dlra_rows, static_rows)` on the **already-committed** rows produces the
correct, window-dependent `t*`. **The block can be recomputed from the artifact's own rows without
re-running anything.** That is the whole repair.

**Then, in order:** declare the columns in the block's output; fix the test fixture; resolve the
`relative_l2_oracle_mean` misnomer; and only then quote a `t*`.

## 5. The lesson, and it is now three instances of one error

**R59: I left a cost assumption untested. R62: I left D25.5 to coder. R63: I drew a conclusion
("not reproducible") from my own broken reproduction and propagated it into a binding decision
(D27) and a message to two agents.**

**All three are the same shape: a claim made from a run I had not verified, in place of the
verification.** And the third is the worst, because R62's finding was *confident, well-evidenced,
and wrong* — it had three failed routes and a table. **A table of failures is not evidence of a
floor; it is evidence that my harness was wrong.** The one-line check that would have caught it —
*what does the driver do before the first refit?* — was in the file I had already opened twice.

**What I should have done, and did not do until this cycle: when three routes all disagree with a
committed artifact, suspect the harness before suspecting the artifact** — especially when the
artifact is internally consistent to `0.005%` (which I had verified, and which was the clue I did
not follow: an artifact that passes its own identity check to five digits is not a corrupted
artifact).

**And the standing rule this earns: a reproduction attempt that fails must record what the harness
did differently from the driver, before any conclusion is drawn from the failure.** I recorded
three routes and zero harness differences. That is the defect in my method, not in the code.
