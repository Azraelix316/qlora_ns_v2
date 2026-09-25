# NOTES.md — coder

> Branch: `agent/coder` · Worktree: `worktrees/coder`
> Status: the static-POD baseline is repaired (its root cause was a reshape bug
> in `PODGalerkin.fit`), every result artifact is regenerated post-fix, and the
> stale `benchmark_summary.json` R27 flagged as blocking is now generated from
> the artifacts. 31 tests pass. Two further real defects found and fixed since:
> the first-derivative operators applied a k-multiplier to the rfft *half*
> spectrum (wrong for any field that is not k-symmetric; inert for every
> committed run, which is measured, not assumed), and `dlra_max_rank` capping
> the rank trace below the grid's own ceiling. R26's energy-based rank
> criterion is implemented and pinned. **In flight:** the R5q cost gate is
> running; because the operator fix changes the code the gate measured, it will
> be re-run from the final commit. Next: the T=8 run R26/R27 ask for, which is
> where the 1→16 rank growth is actually visible (at T=0.1, r99=1). No
> per-step speedup may be claimed (D11.1); F5 is blocked behind the regime
> decision (D11.2).

## Mission

Build and run the numerics: the SP-DLRA engine (structure-preserving split,
exact divergence-free, stream-function form for 2D NS), the high-Re
forced-turbulence test cases, and the benchmark numbers the paper will cite.

## Owned paths (write only here)

- `state/coder/` — this board, run logs, results (text/JSON, keep files small)
- `solvers/` — engine code
- `experiments/` — drivers, configs, benchmark scripts, outputs

## First TODOs

- [x] Read `lessons_learned.md` and the general directions in `AGENTS.md`.
- [x] Build the SP-DLRA engine, informed by the lessons learned. A good
      first test is a simple laminar case (Taylor–Green): check max |∇·u|
      ~ 1e-14, kinetic-energy behavior, and that the rank stays small,
      before moving to turbulence.
- [x] Implement the 2D forced-turbulence drivers (Kolmogorov flow / 2D forced
      NS) per the scope decision in `state/reviewer/DECISIONS.md`.
- [x] Benchmarks: full-grid spectral vs static POD vs adaptive DLRA,
      Re ∈ {100, 1000, 5000}; track rank + max rel L2 vs full grid.
      Log summaries to `state/coder/results/` (one small file per run).
- [x] Send a readiness note to `writer` once the first numbers exist.

## Log

- 2026-09-25 **R29's grid-independence reproduced with project code, and it is
  the cleanest statement of the whole rank question.** Running the pilot at
  N=128 (dt scaled with dx per P0 item 3, snapshots every 0.02, fluctuations
  with the zonal mean removed) and putting it beside my N=64 column:

  | W | r99 N=64 | r99 N=128 | r999 64/128 | amp 1e-6 64/128 |
  |---|---|---|---|---|
  | 0.5 | 2 | 2 | 3 / 4 | 13 / 21 |
  | 1 | 4 | 4 | 6 / 6 | 22 / 39 |
  | 2 | 6 | 6 | 11 / 11 | 42 / 77 |
  | 4 | 11 | 10 | 22 / 18 | 85 / 163 |
  | 8 | **16** | **16** | 38 / 31 | **174 / 357** |

  My N=64 and N=128 r99 columns match R29's reported 2/2/2, 4/4/3, 6/6/6,
  11/10/10 exactly at every window they tabulate. The decisive comparison is
  the last row: **r99 is 16 on both grids while the amplitude rule asks 174 and
  357** — 4.0x and 4.2x their respective dealias ceilings (43 and 85). So the
  energy fraction measures something physical and grid-independent over
  [0, 8], and the amplitude rule's demand is a property of the discretisation,
  not the flow. That is the paper's claim, and it needs no resolution story.
- 2026-09-25 S2 at N=128 also fails everywhere it is measurable (T=4: 8.8%/23.5%;
  T=8: 2.2%/24.7%), so the no-stationary-window conclusion is not a
  resolution artefact either. Consistent at both grids and both amplitudes.

- 2026-09-25 **A mechanism I nearly got wrong, caught by measuring it.** The
  first F5 run at T=8 returned an adaptive rank of **1**, not R26's 16, and my
  first explanation was the secular zonal mean (94% of the energy by t=20, so
  a 99% fraction of the whole state is reached by the mean alone). Measuring it
  refuted that: at t=8 the zonal share is 73.7%, and the *instantaneous*
  fluctuation r99 is **2** — the same as the whole-state r99. The real
  difference is **instantaneous versus windowed rank**: each snapshot at t=8 is
  nearly 2-dimensional, while the 401 snapshots spanning [0, 8] occupy a
  14-dimensional subspace. So R26's 1→16 growth is a property of the subspace
  the trajectory *visits*, and a per-step rule that reads one state at a time
  cannot approach it — the energy criterion moves the selection off the
  dealiasing ceiling onto a physically meaningful ~2, but 2 is not 16 and no
  threshold on a single snapshot makes it so. Tracking the windowed rank needs
  a method that accumulates the visited subspace, which per-step truncation is
  not. I corrected the `SVDProjector` docstring, which had asserted the
  refuted explanation with numbers.
- 2026-09-25 F5 harness hardened: a baseline that goes non-finite is now a
  **recorded result**, not an abort. The first T=8 run died when
  `pod_early_r32` went non-finite at t=6.96, discarding every other method's
  numbers. Each run now reports `diverged`, the step and time it died at, the
  window it actually covered, and `accuracy_metrics_valid: false`, and the
  artifact lists `diverged_methods`. Aborting a comparison because one
  baseline failed is the R24 lesson recurring: "POD is worse" is not citable
  unless the divergence is itself reported.

- 2026-09-25 **S2 answered at the canonical amplitude, and the answer is no.**
  The full ladder to T=20 at A=0.5 gives drift between the last two thirds of
  `E_fluct` / `Z_fluct` of 31%/9% (T=3), 40%/11% (T=4), 30%/8% (T=6), 25%/15%
  (T=8), 29%/7% (T=12), 34%/28% (T=16), 3%/29% (T=20) against a bar of 10% on
  **both**. `qualifying_horizons` is empty: no affordable horizon is stationary
  in the S2 sense. Two supporting measurements from the same run: the zonal
  mean holds **93.8%** of the total energy at T=20 (E_total 939.7 against
  E_fluct 58.3, total energy up 42x from 22.2), and the rank ladder at A=0.5
  gives r99 = 1, 2, 2, 4, 7, 10, 11, 12, 14 at W = 0.1 … 8 while the amplitude
  rule asks 46, 99 and 230 modes at W = 2, 4, 8 against a ceiling of 43. So the
  regime is mean-dominated exactly as D11.2 states, now measured at our own
  amplitude, and the paper reports time-dependent fluctuation statistics with
  the zonal trajectory alongside rather than a plateau that does not exist.
- 2026-09-25 R27's F5 spec addition implemented: **three static-POD window
  placements** (early `[0, train]`, late `[T-train, T]`, and a moving/oracle
  window refitted on a trailing window of the reference) with the comparison
  made against the best of them, because "the cost of staticity" is a function
  of window placement rather than a property of POD. `PODDMD` now also learns
  from the reference's own snapshots, so it needs no extra PDE pass.
  **That change fixed a real defect in the baseline:** fitted on a separately
  re-run trajectory, POD-DMD diverged (E_fluct 8e11 at r=8, max div 4.2e-9);
  fitted consistently with the rollout it is stable at every rank (18.8/22.3/
  19.3 against a reference 19.1). A baseline that blows up because its training
  and rollout trajectories differ is not a baseline, it is a harness error —
  which is the R24 failure mode recurring in new code, caught by the smoke run
  rather than by a test.

- 2026-09-25 **R26's central measurement reproduced independently, and it
  matches their table value for value.** Running the S1–S3 pilot at R26's exact
  configuration (N=64, A=0.2, dt=5e-4, snapshots every 0.02, nested windows
  from t=0, fluctuations with the zonal mean removed), the modes needed to
  represent a window are

  | W | r99 | r999 | amp 1e-6 | amp 1e-10 |
  |---|---|---|---|---|
  | 0.1 | 1 | 2 | 5 | 5 |
  | 0.5 | 2 | 3 | 13 | 19 |
  | 1 | 4 | 6 | 22 | 35 |
  | 2 | 6 | 11 | 42 | 69 |
  | 4 | 11 | 22 | 85 | 144 |
  | 8 | **16** | 38 | **174** | 321 |

  against R26's 1/2, 2/3, 4/6, 6/11, 11/22, 16/38 and 4/12, 12/21, 21/41,
  41/84, 84/174 — the energy columns are identical and the amplitude column is
  within one. This is a cross-check of their headline number from my own code
  with the corrected derivative operators, not a restatement of it.
  **The consequence is now measured on our side too:** r99 grows 16x over the
  first eight time units, while the implemented amplitude rule asks for 42
  modes at W=2 and 174 at W=8 against a dealias ceiling of 43 — so from t=2 its
  rank is the grid's, exactly as R26 reports, and the 1e-10 cutoff reaches 321
  (7.5x the ceiling) by W=8.
- 2026-09-25 S2 measured rather than assumed, and the honest answer is that it
  is not available at the horizon the rank question lives on: with the spec's
  >= 2 time-unit blocks over the final third, T=3 passes (E drift 4.2%, Z drift
  8.5%) but T=4, 6 and 8 fail (11–16%), and no T <= 8 can have two blocks in its
  final third below T ~ 12. So S2 is *unmeasurable* for T < 12 by construction
  and *failing* for T in [4, 8] once it is measurable. Running the ladder to
  T=20 at the canonical amplitude to see whether any developed window passes.

- 2026-09-25 **A real defect in the first-derivative operators, found by the
  R5k full-band test — and proved inert for every committed result.** Applying
  a k-dependent multiplier to the rfft *half* spectrum and inverting with
  `irfftn` is a different operator: `irfftn` rebuilds the missing columns as
  `conj(F[k, N-j])` where a real field requires `conj(F[N-k, j])`. Measured on
  a full-band random field at N=32, `grid.grad`'s x-component differed from the
  independent full-2-D route by 7.5 against a field scale of 35.9. The
  nonlinear term is built from `velocity`/`grad` (`ns_psi.py:91-93`), so this
  was a defect in the dynamics, not only in a diagnostic. Fixed by forming the
  derivative from the **full** spectrum (`fft2` → real multiplier → `ifft2`);
  `grad` now matches the independent route to 0.0 relative error on both axes,
  and `max_divergence` had to be routed through the same operator (it had been
  differentiating with the old route, which is why it briefly reported
  div = 215 on a full-band field). Cost is ~2x on an O(N^2 log N) operation
  beside the Theta(N^3) factorization, so it is immaterial.
  **Impact on committed results: none, measured not assumed.** The canonical
  Re=5000 KE trajectory reproduces to 2.8e-14 over 200 steps and the IC energy
  to all 15 digits, because the affected content never enters: the IC is
  band-limited to |k|<=8, the 2/3 dealias mask keeps every step inside the band,
  and a projected rank-43 state has spectral mass 3.7e-17 outside it. Old and
  new velocity agree to 6e-15 on the IC and 1.1e-13 on a projected state. The
  test now asserts both halves: the operators match the independent route
  *everywhere* including the Nyquist planes, **and** the half-spectrum shortcut
  is demonstrably not the same operator, so nobody reintroduces it.
- 2026-09-25 R26's constructive consequence implemented: an **energy-based rank
  criterion** alongside the amplitude one. `rank_criterion="energy"` keeps the
  smallest r reaching `--energy-fraction` (default 0.99) of the energy, i.e. the
  r99 rule, which is the criterion that can track the state's 1→16 growth; the
  amplitude rule is kept as the default so nothing changes silently, and every
  artifact records which criterion produced its rank trace. Both are pinned by
  a test against brute force, including that they provably differ (12 vs 2 on
  the same spectrum).
- 2026-09-25 R27's blocking defect fixed: `benchmark_summary.json` was still
  built from `c5fc827` and carried the void POD column (1.07759) and the old
  V1 step-0 value (0.315248). It is now **generated** by
  `experiments/make_summary.py` from the artifacts, which also refuses to emit
  a summary whose cases disagree about the IC fingerprint or whose POD IC
  projection is not at roundoff. Two of my own generator bugs surfaced and were
  fixed: it checked the DLRA block for a POD-only field, and it read
  `parameters.re`/`N` from the long-run artifact, which does not record them —
  the old hand-assembled summary had asserted values the artifact never
  contained. The generator now reports them as null and says so, and
  `run_long_time.py` is being fixed to record them.
- 2026-09-25 R27's second point fixed: `dlra_max_rank` defaulted to 48, which
  at N=128 capped the rank trace while the dealiased band holds 85 modes — a
  driver artifact plotted as adaptation. `--dlra-max-rank 0` (the new default)
  resolves to the grid's own ceiling `2*floor(N/3)+1`, and the ceiling is
  recorded in every artifact next to the cap.
- 2026-09-25 R27's instruction adopted: provenance beats fingerprint. The stale
  summary was found by comparing fields against the artifacts, not by searching
  for a remembered string, and the summary now carries each member's
  `git_commit` plus an explicit statement of the rank mismatch (POD r=16 vs
  DLRA r=43, not rank-matched) and of the Re-independent-error red flag (the
  DLRA trajectory divergence is 9.8e-5 / 1.00e-4 / 1.01e-4 at the three Re, so
  at T=0.1 it measures the setup and no Re-dependence may be claimed).

- 2026-09-25 Closing standing CHECKLIST items that were open on my side, in
  `experiments/test_engine.py`. **R5 negative control**: `Grid2D.max_divergence`
  is now exposed so a test can feed the diagnostic a velocity that is *known*
  not to be divergence-free — an injected `grad(phi)` must report ~1, and a
  divergence-free perturbation of the same size must not trip it. Without this,
  "exact by representation" would be a vacuous test that passes for any
  implementation. **R5q cost model, two assertions as the checklist words it**:
  `test_full_field_svd_is_rank_independent` (the factorization returns the full
  N-value spectrum for *any* rank, which is the structural fact behind the
  measured rank-independence, and fails when the V6 per-stage port lands) and
  `test_svd_call_count_per_step` (exactly 4 whole-field factorizations per
  step, so a 4 → 1 change is a failing test). The `SVDProjector` docstring now
  states the cost model as today's behaviour and that V6 must invert it.
  **R5k operator tests on a full-band field** against an independent full 2-D
  `numpy.fft.fft2` route covering `lap`, `vorticity`, `velocity`, `grad` and
  divergence. **R5l**: the rank rule is checked against brute force
  `#{sigma_i > cutoff*sigma_1}` clipped to the bounds, including the degenerate
  spectra; `PODGalerkin.project` is checked for idempotence and
  least-squares agreement on fields with a **nonzero mean**, which is the case
  the old trailing `out - mean(out)` defect hid in. **R5 reduced-path order**:
  Taylor–Green is exactly rank 1, so a rank-1 projector is lossless and the
  reduced step's second-order convergence in dt is measurable (halving dt must
  cut the error by ~4).
- 2026-09-25 Added `PODDMD`, the dynamic data-driven baseline F5 asks for
  (closes the "POD-DMD" half of F5's bar). One fitted linear operator on a POD
  basis, advanced exactly one solver step per application so it shares the dt
  policy. The normal equations are accumulated **online** (O(r^2) memory, not
  O(n_snapshots·r)), which matters because a long training segment is tens of
  thousands of steps. Tested against the only case whose answer is known: a
  synthetic linear system, where the least-squares fit must be exact — that
  catches a transposed normal equation or a stride error, the same class as the
  R24 reshape.
- 2026-09-25 Added isotropic `E(k)`/`Z(k)` as `Grid2D.isotropic_spectra`, with
  the shell sums required to reproduce `ke()` and `enstrophy()` exactly (a test
  asserts it, so the spectra cannot silently lose or invent energy). This is
  P0 metric 3 and the E(k)/Z(k) half of F2, and it is computed on
  `psi' = psi - x-avg(psi)` per S1. `zonal_mean`/`fluctuations` moved into
  `solvers/spectral.py` because they are operations on the state, not on a
  driver, and three drivers now share one definition.
- 2026-09-25 Wrote the two remaining drivers, both blocked on measurement
  rather than on code. `run_regime_pilot.py` implements S1–S3 mechanically:
  fluctuation E and Z, block means of >= 2 time units over the final third,
  drift between the last two thirds, the bar |drift| <= 10% on both, and the
  horizon reported as a function of T so T is chosen from a measurement. It also
  accumulates windowed E(k)/Z(k). `run_baselines.py` implements F5's bar:
  full grid, static POD and POD-DMD at r = 16/32/42 **and at the rank adaptivity
  actually reached**, plus fixed-rank DLRA to separate rank from adaptivity,
  all from one hash-verified IC, judged on time-averaged fluctuation KE/enstrophy
  and spectra with pointwise L2 last and labelled. It pre-checks the offline
  window against the largest requested rank and fails before the long run
  instead of inside it.

- 2026-09-25 Regenerated **every** committed result artifact from commit
  `78607f3`, so the POD column is no longer void anywhere. Re-suite
  (N=64, dt=5e-4, T=0.1, canonical args): all three Re bit-identical IC
  (KE 22.206703312933374, rank 17, sha `ebcef128...`), max |∇·u| 2.3–2.9e-14,
  POD IC projection 1.7–1.9e-17, DLRA rank 17→43. Corrected static-POD max
  rel L2 is 1.08e-6 / 1.13e-8 / 1.00e-8 at Re=100/1000/5000 versus DLRA
  9.8e-5 / 1.00e-4 / 1.01e-4 — the static baseline is *more* accurate at
  T=0.1 (in-sample window, effective rank 3), which is the honest result.
  Taylor–Green, long T=1, and the rank sweep regenerated too; the sweep now
  records `run_case`'s own full parameter block instead of a hand-copied subset
  (P0 item 5). Deleted `benchmark_summary_N64.json`, an orphan from an
  accidental `bench.py` default run whose parameters contradict the canonical
  suite.
- 2026-09-25 **P0 item 3 was being violated by the two-grid comparison and is
  now fixed.** With `default_rng(seed).normal(size=(N,N))`, changing `N`
  redraws the perturbation, so N=128 was a *different realization* of the same
  band (KE 22.1886 vs 22.2067), not the same physical problem at two
  resolutions. Added `make_initial_state(reference_N=...)`: draw, filter and
  normalize on a reference grid, then transfer the spectrum to the target grid
  with the explicit (N_target/N_source)² factor that unnormalized rfft
  coefficients require. N=128 with `reference_N=64` now reproduces the N=64 IC
  exactly — KE 22.206703313 both, |u| rms equal to 9 digits, normalized spectra
  agreeing to 9e-18, while the redrawn fine IC still differs. The default is
  unchanged, so the verified N=64 fingerprint is untouched. The N=128 artifact
  was regenerated under the full protocol: dt 2.5e-4 (scaled with dx), T=0.1
  held, all method settings equal; reference KE agrees with N=64 to 6 digits
  (22.671552 vs 22.671553).
- 2026-09-25 Added measured two-accounting cost instrumentation and the R5q
  gate driver `experiments/bench_cost.py`. `SVDProjector` now accumulates
  `svd_seconds`/`svd_calls`, so "linear algebra alone" is measured rather than
  estimated, and both accountings now appear in the artifacts. The driver pins
  and *records* thread counts, discards a warm-up, takes the median of 7
  repeats over a 2000-step region with min/max spread, holds the rank fixed so
  cost is not confounded with adaptation, and reports the rank-independence
  ratio r=64/r=2 at each N. Smoke test at N=64: reference 1.57 ms/step (0.2%
  spread), reduced full step 1.65–2.12× the reference, linear algebra
  0.85–0.94×, rank-independence within 1.25. No per-step speedup is claimed
  anywhere (D11.1).
- 2026-09-25 Noted for the record: at N=128 the DLRA reaches the *configured*
  `max_rank=48`, not the dealias ceiling 85, so that run is rank-limited by
  configuration. Any matched-rank comparison at N=128 needs `max_rank >= 85`.

- 2026-09-25 **V2/V4 closed by root cause: `PODGalerkin.fit` never computed
  POD.** `X = arr.reshape(N*N, n)` on a snapshot-major `(n,N,N)` array fills in
  C order, so `X[p,k] = arr.flatten()[n*p+k]` — snapshots are interleaved, not
  stacked. The stored "mean" averaged 20 consecutive pixels of one snapshot and
  the SVD factorised scrambled data. Proof: on three known fields the fitted
  mean was off by 24.3, and at full rank 3 *none* of its own training
  snapshots was reconstructed (errors 19–36, `<f−Pf,Pf> = −1549`).
  Fixed to `arr.reshape(arr.shape[0], -1).T`. The old test passed *because* it
  asserted `norm(projected − snapshot) > 1e-8` on 2 snapshots at rank 1, where
  a correct fit is exact — it was asserting the bug. Replaced with a
  fit-reproduces-its-own-input test plus an independent reconstruction of the
  snapshot matrix. After the fix, IC projection rel L2 = **1.8e-17**, POD
  `initial_energy` = **22.206703312933374** (bit-identical to full grid; was
  249.75 = 11.25×), POD max rel L2 vs full **1.0e-8** over 200 steps (was
  ≈1.08), stable. All previously committed POD numbers are void.
  P0 compliance: the offline fit now includes `t=0` so the static baseline
  starts from the same bit-identical IC (`pod.initial_projection_relative_l2`).
  **Honest consequence:** at T=0.1 the corrected static baseline (1.0e-8) is
  *more* accurate than adaptive DLRA (1.0e-4), because the training window is
  a prefix of the evaluated trajectory and is effectively rank 3. The paper
  cannot claim DLRA beats static POD on accuracy at this horizon; per R24 this
  is downstream of the regime decision (D11.2) and the S3 pilot.
- 2026-09-25 R20 rank cap: `fit` now **raises** when `requested_rank` exceeds
  the number of snapshot directions instead of silently clamping (a clamped
  "rank r" run would flatter the proposed method). `effective_rank()` is
  therefore always the requested rank; the artifact records both.
- 2026-09-25 R25: `DLRA.initialize()` now fully resets learned state
  (projector rank back to configured, retained SVD candidates, statistics,
  step counter, rank/spectrum histories). Previously a reused `DLRA` inherited
  the prior run's adapted rank and adaptation schedule and could adapt on a
  stale stage candidate. Chose the reset over documenting single-use.
- 2026-09-25 R5l mean contract: snapshots are centered into the
  zero-spatial-mean class *before* the SVD, so `mean` and every basis column are
  mean-free and `project` is the exact L²-orthogonal projection onto
  `span(mean) + span(basis)` — idempotent, with the residual orthogonal to
  both. Removed the trailing `out − mean(out)` that shifted the output out of
  the subspace. Numerically inert for the real runs (snapshot means ~1e-18):
  IC fingerprint, full-grid run and DLRA are bit-identical; the POD online
  trajectory moves by 1e-12 (roundoff amplified through 200 projected steps).
- 2026-09-25 **R5k's Nyquist fix is refuted for this engine, with
  measurements.** Zeroing the Nyquist multiplier in first derivatives (to avoid
  the self-conjugate aliasing) deletes `v`'s Nyquist row while keeping `u`'s,
  so the real velocity field stops being divergence-free: spectral div u = 8.0
  at N=16 for a Nyquist+smooth field, versus 5.5e-15 with the true wavenumbers.
  The pre-existing convention is the correct one — numpy's `irfftn` inverts
  the full x-axis as a complex spectrum, preserving 2D Hermitian symmetry, so
  no coefficient is dropped and cancellation holds mode by mode. A real-space
  central difference *cannot* check this (the stencil aliases the Nyquist mode
  to zero), which is why an FD cross-check is the wrong instrument here. SVD
  projections do populate the Nyquist row, so the change would have silently
  broken I1 everywhere. Reverted, documented in `Grid2D.__init__`, and pinned
  by a test that guards the invariant.
- 2026-09-25 D11.5: renamed `tolerance` → `relative_amplitude_cutoff`
  throughout (solver, all five drivers, tests) — a rename only, no behaviour
  change. Docstring and CLI help now state that it is a test on singular
  *values* (amplitudes), not an accuracy criterion: 1e-6 is an energy ratio of
  1e-12. The IC fingerprint's separate numerical-rank tolerance is documented
  as distinct.
- 2026-09-25 F2 infrastructure: `normalized_spectrum` no longer caps at 32; the
  default records the **full** state spectrum over all resolved modes (64 values
  at N=64) at every checkpoint, with `--spectrum-count` to truncate. The IC's
  clean rank-17 cliff reproduces (σ₁₇/σ₁ = 2.46e-4, σ₁₈/σ₁ = 8.23e-17). Per
  D11.4 the developed-state figure must be computed on fluctuations
  (ψ′ = ψ − x-avg ψ), since the full-state ratio is contaminated by the growing
  zonal mean.
- 2026-09-25 `make_initial_state`: documented that `cutoff` is a *box*
  half-width (|k_x| ≤ c **and** |k_y| ≤ c), so the max radial wavenumber is
  `floor(c√2)` (2, 5, 11 for c = 2, 4, 8) and the rank is exactly `2c+1`; both
  pinned by a test. V1 verified: IC KE 22.206703312933374, rank 17, DLRA initial
  energy to roundoff, rank 17→43, max rel L2 1.01e-4, max |∇·u| ≤ 2.5e-14.

- 2026-09-25 Final coder audit pass: 13 tests pass; regenerated canonical
  N=64 Re=100/1000/5000 table has full/DLRA max divergence 2.3--2.7e-14,
  DLRA max relative L2 0.315--0.317, and rank 2→42; the N=64 T=1 Re=5000
  check has rank 2→43 and max relative L2 0.324.  PDF/PNG figures and strict
  JSON provenance are committed for the writer.
- 2026-09-25 Added `experiments/make_figures.py` and generated PDF/PNG
  rank/error, singular-value, and cost figures from the committed JSON for
  the writer; figures explicitly show the SVD overhead and POD limitations.
- 2026-09-25 Synchronized with `origin/main` after reviewer R4 and
  rechecked the committed tree: 13 tests pass and all nine result JSON files
  are strict-finite with provenance.  The remaining external dependency is
  theoretical-research's D3 wording, not a missing coder artifact.
- 2026-09-25 Hardened the engine after an independent numerics audit:
  rank adaptation now inspects the retained pre-projection nonlinear
  candidate; inputs are 2/3-filtered before products; signed rFFT Nyquist
  wavenumbers, zero-mean frozen forcing, strict finite JSON, scale-aware
  stability/CFL flags, and explicit projection-work energy diagnostics were
  added.  Thirteen tests pass.  The sustained Re=5000, N=64, T=1 run remains
  finite for full and DLRA (rank 2->43, max relative L2 0.324), while the
  short three-Re comparison honestly records POD accuracy/residual limits.
- 2026-09-25 Added and ran `experiments/run_rank_growth_sweep.py` at
  Re=5000, N=64, dt=5e-4, T=0.1.  Relative thresholds 1e-6, 1e-8,
  and 1e-10 yield maximum ranks 2, 3, and 15 respectively (all runs
  finite), making the singular-value trigger and its cost/error tradeoff
  explicit in `state/coder/results/rank_growth_sweep.json`.
- 2026-09-25 Ran the committed N=64 suite (dt=5e-4, T=0.1,
  A_force=0.5, perturbation velocity RMS=1, POD rank 16, adaptive DLRA
  initial/min rank 2, max 48, relative singular tolerance 1e-10).  All three
  Re cases are finite and structurally divergence-free: full-grid max
  |div u|=2.4--2.5e-14, DLRA=1.9--2.1e-14; DLRA max relative L2 error is
  0.315--0.316, with rank growing from 2 to 14--15.  Static POD is finite but
  less accurate (max relative L2=1.10--1.25) and has a large forcing-aware
  residual at Re=5000; DLRA is slower than full-grid/POD because it pays for
  explicit SVD projections.  Results and provenance are in
  `state/coder/results/benchmark_summary.json` and the per-case JSON files.
- 2026-09-25 Added reproducible Taylor--Green and Kolmogorov drivers, a
  three-Reynolds benchmark wrapper, JSON provenance, singular-value snapshots,
  energy/enstrophy histories, rank traces, and finite-value stability flags.
  Corrected the stream-function constant-gauge handling so SVD rank preservation
  is not destroyed by a post-projection mean subtraction.  The test suite now
  passes 10 tests, including restart, rank-growth, continuous energy-balance,
  and SP diffusion-rank checks.  Final Re=100/1000/5000 result files remain to
  be regenerated from the committed driver.
- 2026-09-25 Implemented the initial stream-function engine: corrected the
  rFFT axis/wavenumber and Parseval conventions, exact vorticity sign, exact
  diffusion semigroup, dealiased midpoint SP split, periodic Kolmogorov source,
  manufactured self-consistent forcing, adaptive SVD DLRA, and static POD.
  `experiments/test_engine.py` passes all 8 tests, including divergence,
  exact Taylor–Green decay, fixed-point, energy terms, time order, rank, and
  POD checks. Benchmark drivers and measured Re results are still pending.
- 2026-09-24 Worktree + branch created as part of the 5-agent scaffold
  (see `PROTOCOL.md`).
