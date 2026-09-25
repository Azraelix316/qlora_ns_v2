# R11 — The premise test: the rank is the **dealiasing mask**, not the dynamics. Plus a correction to my own R8 configuration claim

**Cycle:** R11
**Scope:** `solvers/spectral.py` (dealias mask), `solvers/dlra.py` (rank rule),
`experiments/run_kolmogorov.py` (defaults), `state/coder/results/*.json`
**This is the most important finding about the paper's central premise since D4 was
settled.** One part is good news and one part is serious.

---

## Part 1 — Good news: the premise is *not* confounded by the mean flow

R8a established that the zonal mean carries 52–99% of the total energy. That raised an
obvious worry: if most of the energy is in a growing mean, then "rank ≫ 3 with slow
singular-value decay" might be a statement about the mean rather than about turbulence,
which would confound the paper's premise.

**Measured, it does not.** Decomposing the state into zonal and fluctuating parts and
taking singular values of each (full grid, Re=1000/5000, A=0.2, N=64, tol 1e-10):

| Re | t | rank of total | rank of **zonal** | rank of **fluctuation** | E_zonal/E_total |
|---|---|---|---|---|---|
| 1000 | 2 | 43 | **1** | 42 | 30.0% |
| 1000 | 20 | 43 | **1** | 42 | 90.3% |
| 5000 | 2 | 43 | **1** | 42 | 27.0% |
| 5000 | 20 | 43 | **1** | 42 | 52.1% |

**The zonal mean is exactly rank 1** — as it must be, a profile `φ(y)` broadcast along
`x` is an outer product of rank one. So **42 of the 43 retained modes are fluctuations.**
The energy-weighted dominance of the mean does *not* translate into rank dominance, and
the adaptive rank is not merely tracking the mean. The slow decay lives in the
fluctuations: σ₃₂/σ₁ of the *fluctuation* field is 7.4e-3 → 2.4e-4 over t=2 → 20 at
Re=5000, while the zonal spectrum is numerically zero past rank 1 (σ₈/σ₁ ~ 1e-64).

This also makes S1 (statistics on `ψ′ = ψ − x-avg(ψ)`) structurally natural rather than
a workaround: the decomposition is exact, cheap, and separates a rank-1 object from the
turbulence.

## Part 2 — Serious: the rank is the grid's, not the dynamics'

The rank above is **43 at every tolerance from 1e-6 to 1e-14, at every time from t=0.5
to t=20**. A rank that is invariant across five orders of magnitude in tolerance *and*
across a factor of 40 in time is not measuring anything dynamic. And

**2·floor(N/3) + 1 = 43** at N=64.

I tested that across grid sizes. Numerical rank of the developed state (Re=5000, A=0.2,
t=5, tol 1e-10):

| N | 32 | 48 | 64 | 96 | 128 |
|---|---|---|---|---|---|
| measured rank | **21** | **33** | **43** | **65** | **85** |
| 2·floor(N/3)+1 | **21** | **33** | **43** | **65** | **85** |

**Exact match at every N.** The reason is structural: a state band-limited to
`|k| ≤ floor(N/3)` in the dealiased directions has its x-Fourier support confined to
`2·floor(N/3)+1` distinct wavenumbers, and that bounds the matrix rank. So the state is
**full-rank within the band the grid admits**, with no internal spectral gap.

Four consequences, and the second is the one that reaches the paper's title.

**(i) The "adaptive rank growth" in every committed run is the rank-2 initialisation
artifact meeting a grid ceiling.** The rank rises from its initial value to exactly
`2·floor(N/3)+1` and then never moves. The spec's F3 already suspected this — "a
monotone jump to 43 then flat, which is a transient artefact" — and this is the
mechanism. There is no dynamical rank adaptation to report.

**(ii) The premise as stated is not supported.** "Turbulent dynamics need rank ≫ 3, with
slow singular-value decay and adaptive rank growth" is, on this evidence: rank is large
because the grid admits `≈2N/3` x-modes, not because the turbulence is complex; the
decay is slow *within* a grid-imposed subspace; and the growth is an initialization
artifact. The honest reformulation is narrower and still interesting — **the state is
spectrally full-rank within the admitted band, so rank truncation is not spectrally
motivated, but the tail is energetically negligible (σ_last/σ₁ = 7.5e-5 at N=64, 2.0e-6
at N=128), so low-rank approximation is energetically accurate.** That is a different
claim, and it is defensible. It also matches R5m's observation that trajectory error is
nearly insensitive to rank across a 2× range.

**(iii) The method is never in a genuinely low-rank regime on these grids.** The
available rank is capped at `≈2N/3`, so `r/N ≈ 2/3` at best. A genuine low-rank regime
(`r ≪ N`) needs `2N/3 ≫ r`, i.e. a much larger grid — or a coarser dealiasing mask.
This is a real structural limitation and it is the reason F6's cost story is hard: the
rank cannot be small relative to the state dimension on a dealiased 2D grid.

**(iv) The two committed runs are limited by *different* ceilings, which breaks their
comparability.** At N=64 the grid ceiling is 43 and `dlra_max_rank` is 48, so **the cap
is not binding — the grid is.** At N=128 the grid ceiling is 85 and the cap is 48, so
**the cap is binding.** The N=64 and N=128 runs are therefore not varying the grid
alone; they are also varying which constraint limits the rank. This is a third,
independent reason the "grid check" is not a grid check (after the t=0.1 transient in
R8 and the 2.25× enstrophy gap in R5m).

## Part 3 — Two smaller findings

**Dealiasing is load-bearing for stability, not only accuracy.** Re-running Re=5000 with
`dealias=False` **overflows to NaN** within t=5 (warnings in `ns_psi.py:94`, then
`LinAlgError: SVD did not converge`). Worth stating in the paper as a methodological
point rather than discovering it in a review, and worth a regression test that the
undealiased path is not silently used.

**The full-state slow-decay metric is contaminated by the growing mean in its
denominator.** At Re=5000, t=2: σ₃₂/σ₁ is **1.94e-3 on the full state but 7.39e-3 on
the fluctuations** — a factor 3.8 — because σ₁ of the full state is 3.60e1 while σ₁ of
the fluctuations is 9.23e0. The two converge only once the mean stops dominating
(t=20: 2.26e-4 vs 2.36e-4). The project's verified figure σ₃₂/σ₁ = 1.45e-3 is a
full-state, early-time value and therefore **understates the fluctuations' slow decay**.
Any spectrum claim must state which field it was computed on.

## Part 4 — Correction to my own R8: the committed runs used A=0.5, not 0.2

I told coder, writer and theoretical-research in R8 that "the committed configuration" is
`force_amplitude=0.2`, and I measured the stationarity finding at 0.2. Checking the
artifacts rather than the driver signature:

| artifact | force_amplitude |
|---|---|
| `kolmogorov_re100_N64.json` | **0.5** |
| `kolmogorov_re1000_N64.json` | **0.5** |
| `kolmogorov_re5000_N64.json` | **0.5** |
| `kolmogorov_re5000_N128.json` | **0.5** |
| `kolmogorov_re5000_N64_long.json` | **0.5** |

The **driver default** is 0.2 (`run_kolmogorov.py:393`) but **every committed artifact
was produced at 0.5**. Both statements are true and I conflated them: I read the
function signature and called it the committed configuration.

**The finding survives and is in fact conservative.** At A=0.5 the non-stationarity is
*worse* than what I reported: Re=5000 reaches E=3747 by t=40 (169× E₀) with
`E_in/E_visc` still 125, where at A=0.2 it is 7–8× with ratios 10–173. So R8's and R8a's
conclusions stand, and the runs that actually produced the committed numbers are further
from stationarity than the ones I measured. But coder must re-run the pilot at **A=0.5**,
and the "S3 pilot" must use the amplitude the experiments actually use.

This is the **fourth** time the "which configuration is actually committed" question has
changed a conclusion (R5q cost model, R8 amplitude, R8a mechanism, R11 amplitude again).
The rule I keep relearning is not "measure more" — it is that **a default in a function
signature is not a record of what was run, and `state/*/results/*.json` is.**

## What this asks of the project

The premise question is now sharp and cheap to answer, and it should be answered before
any more method work:

**Is there a spectral gap below the dealiasing ceiling at high N?** If a gap opens at
N=256/512 — dynamic rank well below `2·floor(N/3)+1` — then low-rank approximation is
spectrally motivated, adaptive rank has something to track, and the paper has its
premise. If the rank is *always* exactly the grid ceiling, then there is no spectral
gap, the "adaptive rank" contribution is empty, and the paper must rest on the
**filtering/accuracy** argument that R5q already identified as the strongest available
claim. That is a legitimate paper, but it is a different paper, and the team should know
which one they are writing before the method work continues.

This is measurable in minutes: run the full grid to a developed state at N=256, take
`np.linalg.svd`, and compare the numerical rank against `2·floor(256/3)+1 = 171`.
