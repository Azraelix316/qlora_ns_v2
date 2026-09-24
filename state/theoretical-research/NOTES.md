# NOTES.md — theoretical-research

> Branch: `agent/theoretical-research` · Worktree: `worktrees/theoretical-research`
> Status: fresh — no sessions yet (created 2026-09-24)

## Mission

Research the **theory** behind v2: dynamical low-rank (DLRA) incompressible
Navier–Stokes at high Reynolds number. The v1 engine (SP-DLRA, stream-function
form, exact ∇·u = 0) is validated only on laminar decaying Taylor–Green (rank
3→2→1). v2 needs turbulent, forced dynamics: rank ≫ 3, slow singular-value
decay. This agent develops the theoretical case and concrete improvement
ideas; the coder implements them.

## Owned paths (write only here)

- `state/theoretical-research/` — this board, ideas, derivations (markdown)
- `docs/theory/` — theory write-ups

## First TODOs

- [ ] Read `summary_of_v2.md` (this repo) and the v1 handoff
      (`/home/jaredc/HANDOFF_qlora_ns.md`, v1 repo `/home/jaredc/qlora_ns` —
      if accessible from this node) plus the v1 math spec.
- [ ] Outline `docs/theory/rank-growth.md`: what happens to rank under forced
      turbulence; when and how the adaptive rank strategy must grow; candidate
      strategies (residual-driven, energy-fraction threshold).
- [ ] Outline `docs/theory/stability-error.md`: a priori error / stability of
      the tangent-space split under forcing; KE monotonicity breaks under
      forcing — state what replaces it as the invariant to verify.
- [ ] Send a first scope/ideas summary to `reviewer` and `coder`
      (`scripts/agent.sh send theoretical-research reviewer "..."`).

## Log

- 2026-09-24 Worktree + branch created as part of the 5-agent scaffold
  (see `PROTOCOL.md`).
