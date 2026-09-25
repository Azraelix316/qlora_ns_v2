# NOTES.md — coder

> Branch: `agent/coder` · Worktree: `worktrees/coder`
> Status: core engine, adaptive DLRA/POD drivers, provenance-aware experiment scripts, and 10 correctness tests are implemented; final Re benchmark artifacts are being regenerated.

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
- [ ] Benchmarks: full-grid spectral vs static POD vs adaptive DLRA,
      Re ∈ {100, 1000, 5000}; track rank + max rel L2 vs full grid.
      Log summaries to `state/coder/results/` (one small file per run).
- [ ] Send a readiness note to `writer` once the first numbers exist.

## Log

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
