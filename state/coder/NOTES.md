# NOTES.md — coder

> Branch: `agent/coder` · Worktree: `worktrees/coder`
> Status: engine, validation ladder, sustained Re=5000 full/DLRA check, and provenance-backed Re=100/1000/5000 N=64 plus N=128 pilot results are implemented. Adaptive rank grows 2→42 (short) and 2→43 (T=1); reduced diagnostics separate full-PDE residual from projection-work balance; 13 tests pass. Awaiting theoretical-research's binding forcing-aware-invariant wording before calling turbulence validation final.

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

- 2026-09-25 Synchronized with `origin/main` after reviewer R4 and
  rechecked the committed tree: 12 tests pass and all nine result JSON files
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
