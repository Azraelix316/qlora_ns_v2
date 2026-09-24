# NOTES.md — coder

> Branch: `agent/coder` · Worktree: `worktrees/coder`
> Status: fresh — no sessions yet (created 2026-09-24)

## Mission

Build and run the numerics: the SP-DLRA engine (structure-preserving split,
exact divergence-free, stream-function form for 2D NS), the high-Re
forced-turbulence test cases, and the benchmark numbers the paper will cite.

## Owned paths (write only here)

- `state/coder/` — this board, run logs, results (text/JSON, keep files small)
- `solvers/` — engine code
- `experiments/` — drivers, configs, benchmark scripts, outputs

## First TODOs

- [ ] Read `lessons_learned.md` and the general directions in `AGENTS.md`.
- [ ] Build the SP-DLRA engine, informed by the lessons learned. A good
      first test is a simple laminar case (Taylor–Green): check max |∇·u|
      ~ 1e-14, kinetic-energy behavior, and that the rank stays small,
      before moving to turbulence.
- [ ] Implement the 2D forced-turbulence drivers (Kolmogorov flow / 2D forced
      NS) per the scope decision in `state/reviewer/DECISIONS.md`.
- [ ] Benchmarks: full-grid spectral vs static POD vs adaptive DLRA,
      Re ∈ {100, 1000, 5000}; track rank + max rel L2 vs full grid.
      Log summaries to `state/coder/results/` (one small file per run).
- [ ] Send a readiness note to `writer` once the first numbers exist.

## Log

- 2026-09-24 Worktree + branch created as part of the 5-agent scaffold
  (see `PROTOCOL.md`).
