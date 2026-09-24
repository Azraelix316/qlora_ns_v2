# AGENTS.md — read this first

You are an agent working in the **qlora_ns_v2** repository. This file is the
entry point: project context, repository structure, and the standard rules.
The detailed cross-node protocol lives in [`PROTOCOL.md`](PROTOCOL.md) — read
that too before your first session.

## What this project is

We are contributing a paper to a scientific-computing conference that improves
the current methodology for simulating the incompressible Navier–Stokes (NS)
equations: **dynamical low-rank approximation (DLRA) with a structure-
preserving (SP) split that enforces exact divergence-freeness**.

- **v1 (done, validated).** A matrix-free SP-DLRA engine for incompressible
  2D NS in stream-function form. It enforces ∇·u = 0 exactly
  (max |∇·u| ≈ 1.8e-14, not approximately), keeps kinetic energy monotone,
  tracks the full-grid spectral solution (rel L2 ≈ 1.2e-2 at t=2; 0.77% at
  32²), decays rank 3→2→1 on laminar Taylor–Green flow, and estimates a
  ~3.1× speedup vs full grid at 64².
  - v1 repo: `github.com:Azraelix316/qlora_ns` (local: `/home/jaredc/qlora_ns`)
  - v1 handoff: `/home/jaredc/HANDOFF_qlora_ns.md`
  - **Cite these numbers; do not re-derive or re-litigate them.**
- **v2 (this repo).** Extend the validated engine to **high-Reynolds-number,
  forced, turbulent dynamics** — where the interesting behavior lives:
  rank ≫ 3, slow singular-value decay, adaptive rank growth. The v1 engine is
  the foundation; the turbulence gap is the contribution.

### General directions (current consensus, see `summary_of_v2.md`)

- **2D forced turbulence first** (Kolmogorov flow / 2D forced NS), not 3D.
- **Re ∈ {100, 1000, 5000}**, benchmarked against full-grid spectral and
  static POD; report honestly, including where we are *slower*.
- **Invariants:** max |∇·u| ≈ 1e-14 always; under forcing, KE monotonicity is
  replaced by a forcing-aware invariant (theoretical-research defines it).
- **Novelty claim (defensible, verify before asserting):** no known DLRA
  incompressible-NS solver is both exactly divergence-free and validated at
  high-Re turbulence. Closest prior art: Girfoglio–Quaini–Rozza
  (arXiv:2201.00756, offline POD-Galerkin). `writing-research` is re-running
  and persisting the literature survey — do not rely on memory of it.

### The goal — and what it is NOT

**The goal is a solid conference submission that contributes to the field.**
The novelty position is already defensible. **We do not need to invent an
incredibly novel idea.** This is not a moonshot; the work is rigorous
execution of a clear, standard plan:

1. port the validated v1 engine (extend it; don't re-implement what works),
2. add forced-turbulence drivers and adaptive rank,
3. validate against the invariants and a full-grid reference,
4. benchmark honestly,
5. write a clear paper.

If a subproblem seems to require a brilliant new idea to make progress, that
is a signal to step back — the standard, well-understood approach is almost
certainly what we want. Raise the question to `reviewer` via outbox instead
of improvising.

## Repository structure

Five agents, one branch and one worktree each. `main` is the integrated,
reviewed state; an agent branch may be ahead of main until the reviewer
merges it.

| Agent | Branch | Worktree | Mission |
|---|---|---|---|
| theoretical-research | `agent/theoretical-research` | `worktrees/theoretical-research` | theory of turbulent DLRA-NS, improvement ideas |
| coder | `agent/coder` | `worktrees/coder` | engine port, turbulence drivers, benchmarks |
| writer | `agent/writer` | `worktrees/writer` | the paper |
| reviewer | `agent/reviewer` | `worktrees/reviewer` | reviews, decisions, sole merge into `main` |
| writing-research | `agent/writing-research` | `worktrees/writing-research` | venues, references, novelty checks |

Key paths:

- `state/<agent>/NOTES.md` — each agent's status board: the `> Status:` line
  is the one-line current state, `## Log` is the dated history
- `state/<agent>/outbox/to-<other>.md` — messages from `<agent>` to `<other>`
- `solvers/`, `experiments/` — code and runs (coder)
- `paper/` — the draft (writer); `refs.bib` — shared references
  (writing-research)
- `docs/theory/`, `docs/references/`, `docs/venues/` — research write-ups
- `scripts/agent.sh` — the protocol helper (`start` / `inbox` / `send` /
  `finish`); `PROTOCOL.md` — the protocol; `summary_of_v2.md` — v1→v2 history
- `worktrees/` — local per-node checkouts, gitignored, **not shared**

## Standard rules (all agents, no exceptions)

1. **Follow the method.** All communication goes through the protocol:
   `scripts/agent.sh start|inbox|send|finish` (details in `PROTOCOL.md`).
   Messages are sent from *your* outbox; delivery happens when you push.
2. **Do not create new worktrees or branches.** You have exactly one:
   `agent/<you>` in `worktrees/<you>` (created once during node setup, see
   `PROTOCOL.md`). If you think you need another, ask `reviewer` — the answer
   will almost certainly be no.
3. **Always pull.** At session start: `scripts/agent.sh start <you>`
   (fetch + merge `origin/main`). If you have been away from the repo or are
   about to commit on top of shared state, run it (or at least
   `git fetch origin`) again — always build on the current shared state.
4. **Always commit and push frequently.** Not just at session end: after each
   meaningful unit of work (a finished section, a passing benchmark, a
   resolved question) run `scripts/agent.sh finish <you>`. Long-running jobs:
   checkpoint progress to `state/<you>/` as you go, so no node's work is ever
   lost to a crash or a dropped session.
5. **Write only inside your owned paths** (ownership table in `PROTOCOL.md`).
   Everyone else's files are read-only for you. This is what prevents
   overwrites.
6. **Never push to `main`, never force-push.** `reviewer` is the sole
   integrator. Your work lands on your branch until it is reviewed and merged.
7. **Leave the board current.** Before finishing: update the `> Status:` line
   and append a dated `## Log` entry in `state/<you>/NOTES.md`.
8. **Keep `state/` small.** Text/markdown/JSON only; large outputs (data,
   figures, code) live in your deliverable paths.

## Session lifecycle (the whole ritual)

    # start of session
    scripts/agent.sh start <you>        # pull, print board + inbox
    # ... work: read anything, write only your paths, message via send ...
    scripts/agent.sh inbox <you>        # mid-session check, as needed
    # end of session
    # 1. update state/<you>/NOTES.md  (Status line + Log entry)
    # 2. checkpoint any unfinished long runs
    scripts/agent.sh finish <you>       # commit + push
