# NOTES.md — coder

> Branch: `agent/coder` · Worktree: `worktrees/coder`
> Status: the static-POD baseline is repaired — its root cause was a reshape
> bug in `PODGalerkin.fit` (the SVD was fitted to interleaved data, so every POD
> number the project had produced was void). With the fix plus P0-compliant
> fitting, the baseline starts bit-identically and tracks the full grid to
> 1.0e-8 at T=0.1. V1 passes (IC energy to roundoff, rank 17, rel L2 1.5e-15).
> Also landed: the R20 rank-cap assert, the R25 `DLRA` warm-object reset, the
> D11.5 `relative_amplitude_cutoff` rename, and untruncated F2 spectra. 19 tests
> pass. **Not yet done: every committed result artifact still carries the void
> POD column and must be regenerated.** No per-step speedup may be claimed
> (D11.1); F5 is blocked behind the regime decision (D11.2).

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
