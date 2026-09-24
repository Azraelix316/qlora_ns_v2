# AGENTS.md — read this first

You are an agent working in this repository (local path `~/qlora_ns_v2` on
every node — the only path guaranteed to exist). This file is the entry
point: project context, repository structure, and the standard rules. The
detailed cross-node protocol lives in [`PROTOCOL.md`](PROTOCOL.md) — read
that too before your first session.

## What this project is

We are contributing a paper to a scientific-computing conference that improves
the current methodology for simulating the incompressible Navier–Stokes (NS)
equations: **dynamical low-rank approximation (DLRA) with a structure-
preserving (SP) split that enforces exact divergence-freeness**, validated on
**high-Reynolds-number, forced, turbulent dynamics** — where the interesting
behavior lives: rank ≫ 3, slow singular-value decay, adaptive rank growth.
That turbulence validation is the contribution.

This is a fresh project. There were previous attempts at this goal, and they
did not go well. Their data and sources are **not reusable** — they will not
be cited in the paper, and do not go looking for prior-run artifacts (old
repos, handoff docs, result files): they are not part of this project and may
not exist on your node. What carries forward is the set of **lessons learned**
from those runs — read [`lessons_learned.md`](lessons_learned.md) before your
first session.

### General directions (current consensus, see `lessons_learned.md`)

- **2D forced turbulence first** (Kolmogorov flow / 2D forced NS), not 3D.
- **Re ∈ {100, 1000, 5000}**, benchmarked against full-grid spectral and
  static POD; report honestly, including where we are *slower*.
- **Invariants:** max |∇·u| ≈ 1e-14 always; under forcing, KE monotonicity is
  replaced by a forcing-aware invariant (theoretical-research defines it).
- **Novelty claim (defensible, verify before asserting):** no known DLRA
  incompressible-NS solver is both exactly divergence-free and validated at
  high-Re turbulence. Closest prior art: Girfoglio–Quaini–Rozza
  (arXiv:2201.00756, offline POD-Galerkin). The literature survey must be
  run and persisted by `writing-research` — do not rely on memory of prior
  surveys.

### The goal — and what it is NOT

**The goal is a solid conference submission that contributes to the field.**
The novelty position is already defensible. **We do not need to invent an
incredibly novel idea.** This is not a moonshot; the work is rigorous
execution of a clear, standard plan:

1. build the SP-DLRA engine (structure-preserving split, exact
   divergence-free, stream-function form for 2D NS), informed by
   `lessons_learned.md`,
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
| coder | `agent/coder` | `worktrees/coder` | engine, turbulence drivers, benchmarks |
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
  `finish`); `PROTOCOL.md` — the protocol; `lessons_learned.md` — lessons
  from prior attempts
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
4. **Check other branches before building on their work.** Their branch is
   usually ahead of main — don't guess, read what's actually pushed. After
   `git fetch origin`, use `git show origin/agent/<them>:<path>`: the
   writer reads `experiments/` results and benchmark data from
   `origin/agent/coder`, theory notes from
   `origin/agent/theoretical-research`, references from
   `origin/agent/writing-research`. (Reading is open; merging another
   agent's branch into yours is not — integration goes through the
   reviewer into `main`.)
5. **Always commit and push frequently.** Not just at session end: after each
   meaningful unit of work (a finished section, a passing benchmark, a
   resolved question) run `scripts/agent.sh finish <you>`. Long-running jobs:
   checkpoint progress to `state/<you>/` as you go, so no node's work is ever
   lost to a crash or a dropped session.
6. **Write only inside your owned paths** (ownership table in `PROTOCOL.md`).
   Everyone else's files are read-only for you. This is what prevents
   overwrites.
7. **Never push to `main`, never force-push.** `reviewer` is the sole
   integrator. Your work lands on your branch until it is reviewed and merged.
8. **Leave the board current.** Before finishing: update the `> Status:` line
   and append a dated `## Log` entry in `state/<you>/NOTES.md`.
9. **Keep `state/` small.** Text/markdown/JSON only; large outputs (data,
   figures, code) live in your deliverable paths.

## Session lifecycle (the whole ritual)

    # start of session
    scripts/agent.sh start <you>        # pull, print board + inbox
    # ... work: read anything, write only your paths, message via send ...
    scripts/agent.sh inbox <you>        # mid-session check, as needed
    git show origin/agent/<them>:<path> # read others' latest pushed work
    # end of session
    # 1. update state/<you>/NOTES.md  (Status line + Log entry)
    # 2. checkpoint any unfinished long runs
    scripts/agent.sh finish <you>       # commit + push
