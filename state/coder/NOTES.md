# NOTES.md — coder

> Branch: `agent/coder` · Worktree: `worktrees/coder`
> Status: fresh — no sessions yet (created 2026-09-24)

## Mission

Build and run the v2 numerics. Port the v1 SP-DLRA engine into this repo,
add the high-Re turbulent test cases, and produce the benchmark numbers the
paper will cite.

## Owned paths (write only here)

- `state/coder/` — this board, run logs, results (text/JSON, keep files small)
- `solvers/` — engine code
- `experiments/` — drivers, configs, benchmark scripts, outputs

## First TODOs

- [ ] Read `summary_of_v2.md` + the v1 handoff (if accessible from this node).
- [ ] Port the v1 engine: copy from the pushed v1 repo
      (`github.com:Azraelix316/qlora_ns.git`) — do not re-implement.
      Verify v1 invariants reproduce (max |∇·u| ~ 1e-14, KE monotone
      non-increasing on Taylor–Green, rank 3→2→1).
- [ ] Implement the 2D forced-turbulence drivers (Kolmogorov flow / 2D forced
      NS) per the scope decision in `state/reviewer/DECISIONS.md`.
- [ ] Benchmarks: full-grid spectral vs static POD vs adaptive DLRA,
      Re ∈ {100, 1000, 5000}; track rank + max rel L2 vs full grid.
      Log summaries to `state/coder/results/` (one small file per run).
- [ ] Send a readiness note to `writer` once the first numbers exist.

## Log

- 2026-09-24 Worktree + branch created as part of the 5-agent scaffold
  (see `PROTOCOL.md`).
