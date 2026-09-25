# Experiment specification — what the paper needs, and what counts as passing

**Owner:** reviewer · **Date:** 2026-09-25 · **Status:** acceptance criteria for
D10 (V1–V7) and the D6 checklist, made concrete
**Companion documents:** `DECISIONS.md` (D3, D9, D10),
`reviews/2026-09-25-R5-coder-b2f78fd.md` (evidence behind each item),
`reviews/CHECKLIST.md` (standing gate)

**Why this exists.** D10 lists seven requirements; the writer and coder have
otherwise been waiting on each other to agree what to produce. This document
fixes the target: for each figure and table the paper needs, the run that
produces it, what it must show, and the bar it must clear. The point is that
each agent can start now, and that the next review is a mechanical comparison
against this list rather than a judgement call.

**The bars below are my judgement as reviewer, not physics.** Any of them may be
met differently or waived, but a waiver must be written down in the review
report with a reason — silently missing a bar is the failure mode this project
has already produced once (the 0.315 error number).

---

## P0 — The comparability protocol (applies to every run in the paper)

Until these hold, no accuracy number is interpretable. This is V1 and it comes
first because everything else depends on it.

1. **Identical initial state, verified mechanically.** Every method in a
   comparison starts from a bit-identical state array. To make this checkable
   without re-running anything, each result artifact must record
   `initial_state_sha256` (SHA-256 of the initial state's bytes, plus dtype and
   shape). The reviewer can then compare hashes across artifacts. This one field
   would have caught the current 65% energy loss immediately.
2. **Report the IC's numerical rank** at the working tolerance. The current IC
   is **exactly rank 17**, verified 2026-09-25 from the committed long run: the
   normalized full-grid spectrum at `t=0` has sigma_16 = 2.6e-2, sigma_17 =
   2.5e-4, sigma_18 = 8.2e-17, and the numerical rank is 17 at every tolerance
   from 1e-8 to 1e-14. That matches the band limit exactly — the field is
   supported on |k_x|,|k_y| <= 8, which is 17 modes per axis, so it factors
   through the 17 resolved modes in each direction and its matrix rank is bounded
   by 17. (The base Kolmogorov shear `psi = -U cos y` has support at `(0,+-1)`,
   *inside* that box, so it adds no rank; an earlier reviewer note that said
   "17 + 1 for the shear = 19" was wrong and is corrected here.) The consequence
   for V1 is stronger than "low-rank": the IC is **exactly representable at rank
   17**, so an adaptive integrator at any sane tolerance should capture it at
   initialization, and the current 65% energy loss is unambiguously a harness
   choice. If a method cannot represent the IC at its own tolerance, that is
   part of its result, not a hidden initialisation detail.
   **Acceptance test for the V1 fix:** because the IC is exactly rank 17, a
   rank-adaptive initialisation at tolerance 1e-10 should recover the full-grid
   initial energy (22.207 at Re=5000, N=64) **to roundoff** — the projection is
   then lossless. This is a far sharper criterion than "the error went down",
   and it should be the check the reviewer applies first. Record the initial
   rank, the initial energy, and `initial_state_sha256` in every artifact.
3. **Same physical problem across grids.** For a two-grid comparison, hold the
   IC's spectral content, the final time, and the method settings fixed; scale
   `dt` with `dx`; change only `N`.
4. **Time-step policy stated once:** the CFL target and the largest stable `dt`
   actually used, per run. The present `dt=5e-4` sits at CFL 0.0147, ~34× below
   the 0.5 limit.
5. **Provenance per artifact:** driver, full parameter set, git commit, seed,
   strict JSON (no NaN/Inf). Already the practice — keep it.

## P0 — What counts as an accuracy metric in a chaotic regime

This is the methodological point behind V1/V2 and it changes what the paper
should report. **Pointwise relative L2 against a reference trajectory is not an
accuracy measure** once the two solutions decorrelate: it measures how long
the pair stays in phase, not how well the reduced model reproduces the dynamics.
The current 31.5% is such a number, and it is why the Re-independence
(0.3152/0.3164/0.3165) was diagnostic rather than coincidental.

So each validation run must report, in this order of importance:

1. **Predictability horizon** — relative L2 versus time, short horizon, showing
   the error growth and where it saturates. Label it as trajectory divergence.
2. **Time-averaged kinetic energy and enstrophy** over the stationary window,
   with the spread, for full-grid and each reduced method.
3. **Spectral agreement** — isotropic `E(k)` and `Z(k)` of the full-grid
   reference against the reduced method, over the resolved range.
4. Pointwise L2 at the end point, reported last and labelled as trajectory
   divergence, not error.

## The figures and tables the paper needs

**F1 — Laminar exactness (already met; extend to the new integrator).**
Source: `taylor_green.json`. Content: rank-1 exactness, monotone energy decay,
divergence. Current values: 2.26e-14 relative L2, `max_energy_increase =
−6.7e-3`, `max|div u| = 1.6e-14`, rank 1 throughout. **Bar:** unchanged after
the BUG port, *and* the same result for the ported integrator — this is the
paper's opening result and it must be airtight. Add the
`SelfConsistentForcing` stationary-state test (machine-precision hold from a
rank-representable start) as the sharpest algebraic check. *Closes: nothing new;
protects what exists.*

**F2 — Why low-rank is hard here (the premise figure).**
Full-grid **state** singular-value spectrum at the developed state, plus the
isotropic `E(k)`/`Z(k)`. Current evidence: σ₃₂/σ₁ = 1.5e-3, σ₁₀/σ₁ = 3.2e-2 —
under three decades across 32 modes. **Bar:** plot the *untruncated reference*
spectrum (never the rank-truncated reduced state), over all resolved modes, and
state the truncation threshold at which >32 modes are still required. This is
the figure that justifies adaptive rank; it must not be circular. *Closes V7.*

**F3 — Rank dynamics.**
Adaptive rank over a stationary run, and a tolerance→(rank, accuracy, cost)
sweep. Current evidence is a monotone jump to 43 then flat, which is a transient
artefact. **Bar:** rank varies with the developed state; the sweep shows a real
trade-off curve, not three points with identical error (the present sweep gives
0.31653509/0.31653308/0.31653308 for ranks 20/38/42 — i.e. the error is
insensitive to rank, which is itself the finding that must be explained, not
hidden). *Closes V2 (partly).*

**F4 — Validation against the reference, at each Re.**
Re ∈ {100, 1000, 5000}, per the P0 metric order.

> **STATIONARITY CLAUSE SUSPENDED BY R8 — DO NOT RUN F4 UNTIL RE-ISSUED.**
> The bar below ("a fluctuating plateau in E and Z before statistics are taken") is
> **not achievable at the committed parameters.** Measured full-grid, A=0.2, N=64,
> T=20: E grows 6.9–8.1× over the initial energy and the mean energy over the final
> 20% of the run is still **+35% to +49%** above the prior 20%, with
> `E_in/E_visc` = 10 / 82 / 173 at Re = 100 / 1000 / 5000. The trajectory has not begun
> to turn over, so no plateau exists at T=20 and the operational test below cannot be
> satisfied. T=20 is **withdrawn as a target**, not relaxed: a coder following this
> clause literally would burn a day on a matrix that fails a criterion that was never
> satisfiable, or would quietly relax the criterion and report a transient as
> stationary. I will re-issue this clause against a *measured* forcing amplitude and
> re-cost it then. Evidence and reasoning:
> `reviews/2026-09-25-R8-no-stationary-state.md`.
>
> **Consequences already binding, pending re-issue:** no turbulence statistic
> (spectra, time-averaged E/Z, singular-value decay) may be reported from the
> committed `final_time: 0.1` runs, which are pure spin-up transients; and the
> full-grid reference must itself be stationary before it can adjudicate a reduced
> model at all.

**Bar (to be re-issued):** runs reach a fluctuating plateau in E and Z before
statistics are taken (operationally:
relative standard deviation of E over the final quarter of the run below ~5%);
the three Re are actually distinguished (they must not produce near-identical
trajectories, which is what happens now); results reported at N where the
resolution study says that Re is resolved. *Closes V2, V1.*

**F5 — Baselines, rank- and work-matched.**
Full-grid spectral; static POD at r = 16/32/42 and at the adaptive rank;
**POD-DMD (dynamic data-driven ROM) at the same matched ranks** — added at R5h
because a 2017+ scicomp venue will expect it and Peherstorfer & Willcox
(CMAME 291:21–41, 2015, DOI 10.1016/j.cma.2015.03.018) is its reference; the
method itself; a fixed-rank variant to isolate adaptivity from rank.
**Bar:** identical IC (hash-verified), same dt policy, same forcing and
spectrum. The method must beat both static POD and POD-DMD at matched rank on
time-averaged E/Z and on spectra in the resolved range — if it does not, report
that; it is a publishable result but the claim must change. The current POD
numbers (11.4× energy, 159× enstrophy, rel L2 > 1, O(1) PDE residual) are a
broken baseline and may not be cited. POD-DMD is cheap: project the snapshot
window onto a POD basis, fit the linear operator, advance the modal
coefficients, reconstruct — it reuses `solvers/pod.py`. *Closes V4.*

**F6 — Cost and memory.**
Error versus wall time and peak memory versus `N` and versus `r`, for full grid,
rank-matched POD, POD-DMD, and the method. **Bar (revised by R5q — this supersedes
the earlier "state the crossover" wording, which is retained as a sub-requirement):
** *no per-step speedup is available to this method at r≈45 and the paper must not
imply one.* Both methods evaluate the same nonlinear term on the full grid, so both
pay Θ(N² log N); the reduced linear algebra adds Θ(N²r²) on top, and `r > log N` for
every `(N, r)` this project will use. Measured today: **2.9×/3.1×/3.6× slower than
the full grid at N=64/128/256.** After the V6 port the measured expectation is
**near-parity by N=512, not a win.** What F6 must therefore deliver is the
**matched-accuracy** comparison (error on one axis, wall time on the other), which is
the only comparison in which a filtering method can win, plus the resolution
dimension. Sub-requirements, all binding: report **both** accountings — the linear
algebra alone (`4×SVD` vs `1×QR + r̂×r̂`, whose crossover at r≈43 lies between N=64
and N=128) and the full step — and never present the linear-algebra win as a per-step
win; state the `2N²r²`-versus-⅔N³ flop counts, because BUG does *more* arithmetic
than the dense SVD it replaces at these ranks and wins only on arithmetic intensity;
report where we are slower, as the project's own honesty rule requires. *Closes the
cost item in V4/V6; see `reviews/2026-09-25-R5q-cost-model-audit.md`.*

**F7 — Resolution study.**
E, Z, and spectra at N = 64/128/256 with the physical problem fixed. **Bar:**
an explicit statement of which Re is resolved at which N. The present "grid
check" changes six parameters at once and shows 2.25× enstrophy disagreement
between N=64 and N=128, so N=64 cannot currently support a high-Re claim.
*Closes V5.*

**T1 — Invariants table (every run, in the paper).**
`max|div u|`, the forcing-aware energy-balance residual, rank range, CFL, and
whether the run is finite. **Bar:** `max|div u| ≤ 1e-13` for every run, full and
reduced, laminar and turbulent. The forcing-aware residual must be
theoretical-research's definition (D3), with the projection-work term *derived*
from the Galerkin step after the port rather than measured post hoc.

**T2 — Forcing-aware invariant statement.**
The definition, its provenance, and what it does and does not guarantee. Blocked
on D3.

## The minimum publishable set, if time is short

In priority order: **F1** (done — protect it), **F2**, **F4**, **F7**, **F5**,
**F6**, **F3**, then T1/T2. A paper with F1+F2+F4+F7 and honest T1 is a solid
scicomp submission; F5/F6 make the method's *value* legible; F3 is the most
enjoyable and the least essential, and should not be rushed at the cost of the
others.

## What is already met, so nobody redoes it

- `max|div u| ≈ 1e-14` across all runs (D3's first requirement) — met.
- Taylor–Green laminar exactness and monotone energy decay — met (F1).
- Test suite: 13/13 passing, independently re-run by the reviewer in a clean
  environment.
- Provenance, strict JSON, honest documentation of limitations.
- The premise measurement (F2's numbers) — obtained, needs the full spectrum
  recorded rather than the top 32 values.
- The method port path and its verbatim algorithm — specified in
  `reviews/2026-09-25-R5c-premise-and-v6-literature.md` and the reviewer's
  message to `coder`; sources are open access.

## Is the gate affordable? Costed order of work (R5o)

> **SUPERSEDED IN PART by R5q** (`reviews/2026-09-25-R5q-cost-model-audit.md`).
> The per-step costs quoted below were taken from the committed artifacts, which R5q
> showed are **not reproducible**: they come from 200-step, sub-1.2-second runs timed
> under default multithreaded LAPACK, whose `gesdd` is 23–78× slower than the same
> factorization at `OMP_NUM_THREADS=1`. **Use the R5q measured figures below, not
> these.** The sequencing conclusions still hold and are confirmed.

A gate that cannot be executed gets quietly relaxed, so the reviewer costed the
required runs from the committed per-step timings (full 1.84 ms, POD 2.95 ms,
DLRA 4.60 ms per step at N=64). Full reasoning in
`reviews/2026-09-25-R5o-gate-costing.md`. Three conclusions that change the
sequencing:

- **Stationarity is cheap.** T=20 at N=64 is 40,000 steps: ~1.2 min (full) and
  ~3.1 min (DLRA). The whole three-Re x four-method matrix is ~20 minutes. The
  stationarity requirement is not a reason to defer anything.
- **The resolution study does not want long runs.** Its purpose is grid
  convergence of the diagnostics, which needs the same physical problem at
  N=64/128/256, not a long horizon; at T=0.1 that is minutes. High N *and* long
  T together is the expensive combination, and it is not required — which removes
  the apparent tension between V2 and V5.
- **The committed timings are not yet trustworthy.** The N=64 -> N=128 DLRA ratio
  is 3.11x, below the ~3.85x that N^2 log N alone predicts, so the N=64 number
  is overhead- or warm-up-dominated (the R5n cost-figure artifact). Cost
  projections are therefore order-of-magnitude planning figures; N=256 must be
  **measured**, not extrapolated (a two-component fit from two points degenerates
  and returns a physically impossible ordering).

### Measured costs (R5q — replaces the projections above)

Median of 7 repeats after 2 discarded warm-up calls, `OMP_NUM_THREADS=1`, real
workload, working rank as reached:

| N | full-grid step | DLRA step | ratio | T=20 steps | T=20 full | T=20 DLRA |
|---|---|---|---|---|---|---|
| 64 | 2.87 ms | 8.38 ms (r=43) | 2.9× | 40,000 | 1.9 min | 5.6 min |
| 128 | 7.79 ms | 24.52 ms (r=48) | 3.1× | 80,000 | 10.4 min | 32.7 min |
| 256 | 25.87 ms | 93.91 ms (r=46) | 3.6× | 160,000 | 69.0 min | 250.4 min |

The full T=20 matrix (full + DLRA at working rank, three Re, all three N) is
**18.5 h**, of which **16.0 h is N=256**. Two consequences: stationarity at N=64 is
even cheaper than R5o estimated and remains not a reason to defer anything; and any
long high-N run is genuinely expensive, so the N=256 decision must be made from the
matched-accuracy result rather than assumed.

**Timing protocol, now binding (R5q):** thread counts pinned *and recorded in the
artifact*; warm-up discarded; ≥7 repeats; median plus spread; and a timed region that
dominates process start-up — at `dt=5e-4` that means **≥2000 steps, not the 200 the
committed runs used**. A timing that does not meet this is not a measurement.

**Order of work:** (1) re-time properly, to the R5q protocol; (2) V1; (3) **R8:
choose a forcing amplitude that actually reaches stationarity on N=64, with a
one-paragraph physical justification, and re-issue the F4 stationarity clause —
this now precedes every other item, because F4 and everything downstream of it are
blocked on it**; (4) V2 at N=64, T=20; (5) F2
with the full spectrum recorded — `normalized_spectrum` currently caps at 32
values, which is the binding constraint on the slow-decay claim and must become
a parameter; (6) V5 at short T; (7) V4; (8) V6, then re-run 4–7 with the new
integrator; (9) decide any long high-N run from the measured cost. Steps 1–2 and 4–6
are a few hours in total. **Added at R5q, and cheap enough to do during step 1:** a
test asserting that per-step cost is currently *rank-independent* (`r=2` versus
`r=64` within 1.25×), with a docstring saying this is today's behaviour and that V6
must invert it — so the port's improvement shows up as a test going from pass to fail
to pass, rather than as a claim in prose.

## Figures — per-figure requirements (R5n)

The three committed figures were rendered and inspected by the reviewer. **None
is usable as committed.** These are the requirements; the reasoning and the
evidence are in `reviews/2026-09-25-R5n-figures-audit.md`.

- **Rank/error figure.** The error panel must be labelled *trajectory
  divergence*, not accuracy, and must start from the **computed** step-0 value
  (0.319, not 0). It must be accompanied by the accuracy measures (time-averaged
  E and Z, spectral agreement). The broken POD baseline must not be shown as a
  comparison result. If the rank panel is shown, note the achieved rank as a
  fraction of the cap and the fraction of the run spent there — "adaptive rank
  growth" that saturates at 88% of the cap in the first 3% of the run is not
  support for the claim, and the figure should say so rather than imply
  otherwise. Do not fade non-primary curves to invisibility while claiming them.
- **Spectrum figure (the premise figure).** Plot the **untruncated full-grid**
  state spectrum, never the rank-truncated reduced state — a rank-r state has r
  retained values and decays smoothly by construction. Use the measured
  reference values: sigma_32/sigma_1 = 1.45e-3, sigma_10/sigma_1 = 3.17e-2 at
  the developed state. The preferred version pairs the IC spectrum (exactly rank
  17, with a clean cliff) against the developed-state spectrum (no cliff out to
  32 modes), which is the before/after statement that motivates adaptive rank.
- **Cost figure.** Discard warm-up and repeat timings; report a median with a
  spread bar. Annotate N, dt, achieved rank, and thread pinning. Do not present
  a Re-dependence that is a measurement artifact — the three Re cases are
  computationally identical except for `nu`, so cost should be Re-independent.
  **R5q additions, binding:** pin and *record* `OMP_NUM_THREADS` in every artifact
  containing a timing (unpinned LAPACK `gesdd` is 23–78× slower here and biases the
  DLRA/full-grid *ratio*, not just the absolute numbers); time ≥2000 steps so the
  timed region dominates start-up; and plot error against wall time rather than cost
  alone, since a per-step win is not available to this method (F6). Add a
  rank-dependence panel — the current implementation's cost is **flat in r** (7.31 ms
  at r=2 versus 7.81 ms at r=64, N=64, because the projector SVDs the whole N×N field
  four times per step), and that flatness is the single most important fact about the
  present cost model. It should be visible in the figure and pinned by a test.
- **All figures.** No paper-quality typesetting on a provisional figure: either
  mark it superseded in `experiments/README.md` or move it out of
  `experiments/figures/`.

## Known traps, collected

- The reduced state spectrum is not a spectrum of the problem (V7/F2).
- `max_relative_energy`/`max_relative_enstrophy` are stability ratios, not
  accuracy numbers (naming).
- `stable` means finite and within broad sanity limits — not accurate, not
  long-time stable.
- An energy-balance residual with the measured projection work subtracted is an
  accounting identity, not a structure-preservation result.
- A rank-2 start on a rank-17 IC throws away 65% of the energy before `t=0`.
- An SVD of the truncated state will always look like it has slow decay.
- Comparing a reduced method at rank 42 against a baseline at rank 16.
- Comparing only against *static* POD: a scicomp reviewer will ask why DMD /
  dynamic data-driven ROM is absent (R5h).
- Citing a DMD or operator-inference record from memory: the Williams–Kevrekidis–
  Rowley paper is in *J. Nonlinear Sci.*, not SIAM JADS, and the
  Peherstorfer–Willcox reference to use is *Dynamic data-driven reduced-order
  models*, CMAME 291 (2015), DOI 10.1016/j.cma.2015.03.018.
