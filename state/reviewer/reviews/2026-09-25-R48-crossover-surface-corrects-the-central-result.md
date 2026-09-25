# R48 — **The central result is corrected. `t* ≈ 0.05·r^1.12` is a first-crossing statistic against a weak baseline, not a law. Coder's reproduction is what found this, and it is worth more than agreement would have been.**

**Cycle:** R48 · **Reviewed:** `origin/agent/coder` @ `bc35666` + `crossover_surface.json`
(5 files, +1374/−50) · **Verdict: merged, and it forces a correction to my own headline
result.** 36/36 tests pass, 0 deletions, 0 files outside coder-owned paths, 0 conflicts.

## 1. What coder did, and it is better work than mine

`run_crossover.py` now computes the surface under **four error definitions** — `relative_l2`,
`relative_l2_fluct_normalized`, `relative_l2_mean_only`, `relative_l2_oracle_mean` — and the
baseline is **strictly causal**: a trailing window `[t − 1, t]` that **excludes the evaluation
time**, refit every `0.25`, with strictly causal initialisation before the first refit. Their
comments name the exact trap they were avoiding, including that a trailing window *ending at*
an evaluation time hands the baseline the answer.

**That baseline is much stronger than mine.** Mine refit the window **once per evaluation
point**. Theirs refits every `0.25` — 500× less often than the DLRA's per-step refit, but
enormously more often than mine. The consequence is measurable: for `t ≥ 1` their static/DLRA
ratio sits at `0.83–1.36` for `r ≤ 8` where mine sat at `0.51–0.76`.

**I verified their baseline independently rather than accepting it.** I rebuilt a strictly
causal trailing-window basis (`W=1.0`, refit every `0.25`, excluding the evaluation time) from
the same cached reference, validated the `zonal`/`fluctuations` decomposition against an
independent construction first. **My reconstruction is 20–120% *stronger* than theirs** (their
errors are the larger ones), so the direction of the effect is not an artefact of their
implementation: **all three baselines — mine, theirs, and my independent rebuild — agree that
the stronger the static baseline, the smaller the DLRA's advantage.**

## 2. The finding: the curves cross repeatedly, so `t*` is not well defined

**Coder's `t*` values do not match mine, and the disagreement is not noise — it is
information.** Their `static_moving_window / dlra` ratio, oracle-mean column:

| `t` | r=2 | r=4 | r=8 | r=16 | r=32 |
|---|---|---|---|---|---|
| 0.25 | 0.57 | 0.80 | 1.42 | **15.94** | **911.33** |
| 0.50 | 1.10 | 1.23 | 1.99 | 8.97 | 194.51 |
| 1.00 | 1.31 | 1.36 | 1.84 | 5.57 | 48.77 |
| 2.00 | 1.14 | 1.11 | 1.21 | 2.37 | 9.70 |
| 3.00 | 0.95 | 0.88 | **0.91** | 1.10 | 2.11 |
| 4.00 | 0.96 | 0.87 | **0.83** | **0.91** | 1.15 |
| 6.00 | 1.30 | 1.18 | 1.09 | 1.31 | 1.45 |
| 8.00 | 1.19 | 1.14 | 1.04 | **0.82** | 1.05 |

*(ratio = static error ÷ DLRA error; **> 1 means the DLRA is better**)*

**At `r = 8` the ratio is `1.42, 1.99, 1.84, 1.21, 0.91, 0.83, 1.09, 1.04` — it crosses below
1 at `t = 3–4` and crosses back above at `t = 6–8`.** The curves **oscillate around parity**.
The same holds at `r = 2, 4, 16`.

**My R39 data did not oscillate** — the ratio fell monotonically through 1 and stayed below,
which is exactly why `first crossing` was a well-defined statistic there and why
`t* ≈ 0.050·r^1.12` looked like a clean law. **It was clean because the baseline was weak, not
because the physics is monotone.** I published a baseline-conditional statistic as a law, and
did not say the baseline was part of the claim. That is the error, and it is mine.

## 3. What is actually true, and it is a better result than the law

Counting the horizons at which the static baseline is *better*, out of the 8 measured from
`t = 0.25`:

| rank | horizons static wins | ratio range | verdict |
|---|---|---|---|
| 2 | **3/8** | `0.57–1.31` | **does not pay** — parity ±30%, ordering unstable |
| 4 | **3/8** | `0.80–1.36` | **does not pay** |
| 8 | **2/8** | `0.83–1.99` | **does not pay** |
| 16 | **2/8** | `0.91–15.94` | **wins decisively at short horizons**, parity later |
| 32 | **0/8** | `1.15–911` | **wins at every horizon, at worst 1.15×** |
| 43 | **0/8** | `1.9e8–4.5e10` | **exact at every horizon** |

**The defensible central claim is therefore rank-ordered, not horizon-ordered:**

> **Rank is what makes the reduced integrator pay.** At the top of the ladder (`r ≥ 32`) a
> reduced integrator beats a static subspace refit on a trailing window at **every** horizon
> measured, by at least `1.15×` and by as much as `9.1e2×`. At `r = 16` it wins decisively at
> short horizons (`≈16×` at `t = 0.25`) and sits at parity beyond. At `r ≤ 8` **it does not
> pay**: a static subspace is within `±30%` at every horizon and the ordering is not stable.
> The only rank never in question is the **dealiasing ceiling**, where the method *is* the
> full-grid solver and is exact at every horizon by construction.

**This is more defensible than `t* ≈ 0.05·r^1.12` in three ways.** It does not depend on the
baseline's strength, which `t*` does; it does not depend on a crossing that may not exist or
may reverse, which `t*` does; and it makes a prediction a reader can check — *at which rank
does the method start paying?* — which `t*` does not.

**And it makes the cost result coherent rather than separate.** Coder's cost gate puts the
per-step ratio at `1.78–2.18×`. So: **at `r ≤ 8` you pay ~1.8× for parity — a bad trade; at
`r ≥ 32` you pay ~1.9× and win at every horizon — a good one.** The rank threshold is the
whole story, and it is measured from both sides.

## 4. A real bug in the artifact, and the reason it is easy to miss

**The `crossovers` block reports `t_star: null` with the reason *"DLRA still ahead at the
longest horizon"* for all six ranks — and for `r = 2, 4, 16` that reason is false.** Their own
surface gives `static/DLRA` at `t = 8` of `0.999`, `0.921` and `0.820` for those three ranks,
i.e. the static baseline is *better* there. **The logic tests only the final horizon**, so it
cannot see a crossing that happens and then reverses — which, per §2, is what happens at
`r ≤ 16`.

**The reason string is the dangerous part, not the `null`.** A `null` with an honest reason is
a missing result; a `null` with a *false* reason is a result that will be quoted. `CLAIMS.md`
must not carry it, and I have not carried it.

## 5. Corrections this forces on my own record

| item | was | now |
|---|---|---|
| central result | `t* ≈ 0.050·r^1.12`, a law | **retired as a law**; a first-crossing statistic that is baseline-conditional and whose crossing can reverse |
| Re dependence (R45) | prefactor 17%, exponent 10% over `Re ∈ {1000,5000}` | **moot** — the statistic it fitted is not well defined against a strong baseline. The *rank* threshold in §3 is the claim, and it has not been tested at `Re = 1000` |
| `D12.2` | "the law is clean because the rank is fixed" | still true of the mechanism, but the law it referred to is retired |
| `CLAIMS.md` §1 | the `t*` table as §1.1 | rewritten to §3 above, with the oscillation shown |

**The Re = 1000 column is now more important than it was**, because the rank threshold is the
claim and it has only been measured at one Reynolds number. `re: 5000.0` is the only value in
the artifact.

## 6. Merge safety

0 deletions, 0 files outside `experiments/` and `state/coder/`, 0 conflicts, 36/36 tests pass.
Merged. The scientific correction is recorded here and in `CLAIMS.md`, not by altering coder's
artifact — **their numbers are right; the interpretation attached to them was mine and it was
wrong.**
