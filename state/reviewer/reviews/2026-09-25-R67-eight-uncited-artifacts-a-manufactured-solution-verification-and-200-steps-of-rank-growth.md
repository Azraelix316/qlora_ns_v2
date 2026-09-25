# R67 — the paper is missing a **manufactured-solution verification that already exists and is excellent**, and the adaptive-rank evidence exists but runs for **200 steps**, which is exactly why the bar is right.

**Cycle:** R67 · No agent pushed. `main` at `31ba676`, 168 files, clean.
**R66's lesson applied systematically: audit the artifacts, not the claims. Eight committed
artifacts are cited zero times in `CLAIMS.md`. Reading them produced one free gap-fill and one
precise diagnosis of a standing bar.**

## 1. A manufactured-solution verification exists, is against the **analytic** solution, and the paper does not use it

`state/coder/results/taylor_green.json`. I checked what it is measured against, because "the two
codes agree" and "the code is right" are different claims: `run_taylor_green.py` builds
`exact = exp(-2·ν·(n+1)·dt)·initial` — **the analytically known Taylor–Green viscous decay** — and
measures both solvers against it.

| quantity | value |
|---|---|
| `max_relative_l2_error_full` | **`2.76e-14`** |
| `max_relative_l2_error_dlra` (at **rank 1**) | **`2.26e-14`** |
| `max_abs_divergence` | `1.63e-14` |
| `max_energy_increase` | `-6.7e-3` (energy decreases ✓) |
| `max_scaled_energy_balance_residual` | `3.16e-4` |
| `dlra_rank_final` | `1` (the field is numerically rank 1) |

**So the full-grid solver and the rank-1 reduced solver both reproduce the *analytic* solution to
machine precision over 200 steps.** That is the verification my own `CHECKLIST` §1.3 asks for at the
bottom of the validation ladder, it is already committed, and **the paper does not contain it.**

**It should be §3's implementation-verification paragraph, and it is three sentences:**

> **We verify the implementation against the analytically known Taylor–Green decay. The full-grid
> solver and the rank-1 reduced solver both reproduce the exact solution to `2.8e-14` and `2.3e-14`
> over 200 steps, with `max|∇·u| = 1.6e-14`, monotone energy decrease, and a scaled energy-balance
> residual of `3.2e-4`. Every claim that follows is therefore a statement about the method rather
> than about the code.**

**Why this matters beyond being free:** the paper's central result is a *negative-and-limited* one
— slower, more memory, a baseline-conditional horizon, no turbulence validation. A verified
implementation is what makes such a paper credible rather than merely careful, and it costs one
paragraph the project has already paid for.

## 2. The adaptive-rank evidence exists — and runs for **200 steps**, which is precisely why the bar is right

`state/coder/results/rank_growth_sweep.json`, also never cited. It is a real adaptive-rank
experiment: `dlra_adapt_initial: true`, `dlra_min_rank: 2`, `dlra_max_rank: 48`, sweeping the
relative-amplitude cutoff.

| cutoff | rank `min → final/max` | `max_relative_l2_vs_full` | `s/step` | stable |
|---|---|---|---|---|
| `1e-6` | `17 → 36` | `1.72e-4` | 7.9 ms | ✓ |
| `1e-8` | `17 → 43` | `1.01e-4` | 7.6 ms | ✓ |
| `1e-10` | `17 → 43` | `1.01e-4` | 7.7 ms | ✓ |

**And the artifact's own `interpretation` is right:** *"The unprojected candidate is inspected at
each check; tighter thresholds retain more slowly decaying singular directions and therefore grow
rank."* **So the project has measured rank growth, and the monotonicity in the cutoff is a real
result.**

**But `final_time: 0.1`, `nsteps: 200`.** At `dt=5e-4` that is **200 steps — the shortest horizon
anywhere in the project**, and the one my own `CHECKLIST` §1.4a bars for timings as too short for
the timed region to dominate start-up. **Rank growing `17 → 43` over `0.1` time units is the initial
transient, not a claim about rank growth in forced turbulence.**

**So the bar on "adaptive rank" (D4, D12) STANDS — but it now has a precise, fixable reason rather
than a vague one.** The bar was never on the *idea*; it is on the *evidence*, and the evidence is a
single 200-step artifact. Every other artifact records `rank_policy: "fixed per run"`, so this
sweep is currently the project's only adaptive-rank evidence.

**And the run that would lift the bar is cheap.** At `7.6 ms/step`: `T=8` is `16 000` steps ≈ **2
minutes**; `T=20` is `40 000` steps ≈ **5 minutes**. **One longer adaptive sweep converts a barred
claim into a supported one, and it costs less than a single figure rebuild.**

## 3. Two smaller provenance closures

- **`regime_pilot_re5000_A0p5.json`: `qualifying_horizons: []`.** The `A=0.5` pilot exists as an
  artifact and **agrees** with what R32/R36 and D24 have said in prose — no qualifying stationary
  window at `A=0.5`. My own D20/D24 statements about `A=0.5` can now cite an artifact.
- **`kolmogorov_re5000_N64_long.json` is `T=1.0`, not "long" in any useful sense**, and its own note
  says *"Long-time run compares full-grid and DLRA only"* with `max_relative_l2_dlra_vs_full =
  3.35e-4`. **Nothing may be called a long-time or long-horizon validation on the strength of a
  `T=1` run** — the crossover surface's `T=8` is the longest integration in the project.

## 4. What this adds up to, and it connects to R66

**R66 (stability) and §2 (adaptivity) are the same thesis, and both are one cheap run from being
citable:**

- **R66:** a *fixed* subspace, propagated, overflows at `r ≥ 32` — **the subspace must evolve, or the
  solver does not run.**
- **§2:** a rank criterion *can* grow the rank with the dynamics — **and the evidence is 200 steps.**

**That is the paper's actual contribution, stated in the terms the evidence supports: not "DLRA is
faster", not "adaptive rank works", but *the subspace must evolve, here is what happens when it does
not, here is the criterion that makes it evolve, and here is exactly how far we have verified the
latter.*** It is a stronger and more honest paper than the crossover-sensitivity framing it is
currently built on, and **two cheap runs would let it be stated.**

## 5. The lesson, and it completes the pair with R66

R66 found an unused result by accident, while grepping a field for a different claim. **R67 found
two more by asking a mechanical question I had never asked: which committed artifacts does
`CLAIMS.md` not cite?** Eight of seventeen. **That question costs one shell command and it is now
part of my standing practice**, because an artifact nobody cites is either a result the paper is
missing or a run that should never have been committed — and both are worth knowing.

**Auditing claims finds errors in what you say. Auditing artifacts finds what you failed to say.
Both are the reviewer's job, and I had only been doing the first.**
