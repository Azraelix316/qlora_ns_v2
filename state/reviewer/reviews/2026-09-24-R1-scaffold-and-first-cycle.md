# R1 — 2026-09-24 — scaffold review + first review cycle

Reviewer: `reviewer`. Scope: whole repo (fresh project, post-scaffold).

## Branch status (after `git fetch origin`)

| Branch | Head | vs main | Content beyond fork point | Merge? |
|---|---|---|---|---|
| `main` | 97ed54e | — | rewritten agent docs (fresh project) | — |
| `origin/agent/coder` | 4c28a7b | forked at d5e3ad1, behind main | 2 commits, **net-zero tree diff** (smoke-test outbox message added then removed) | No — nothing to merge; coder will fast-forward on next `start` |
| `origin/agent/writer` | 57d6e11 | behind main | none | No |
| `origin/agent/theoretical-research` | c2d2e6a | behind main | none | No |
| `origin/agent/writing-research` | d5e3ad1 | behind main | none | No |
| `origin/agent/reviewer` | (this branch) | — | DECISIONS.md, reviews/ | Self-merge to main (reviewer is sole integrator) |

## Ownership-rule check

No violations found. All writes so far are inside owners' paths:
- `coder`: `state/coder/outbox/to-writer.md` (own path) — added then removed.
- `writer`: `scripts/agent.sh` fix (57d6e11) — scaffold file, but this
  predates rule D7 and was part of the initial scaffold setup; recorded for
  the record. From now on, scaffold changes need reviewer approval (D7).

## Findings

1. **The project is at the scaffold stage — no agent has started work.**
   Every board says "fresh — no sessions yet". No `solvers/`, no
   `experiments/`, no `paper/`, no `docs/theory/`, no `refs.bib`, no venue
   research, no arXiv survey.
2. **Blocking items for the plan (in dependency order):**
   a. `theoretical-research` must define the forcing-aware KE invariant
      (D3.3) — `coder` needs it before turbulence validation counts.
   b. `writing-research` must run + persist the arXiv novelty survey (D4) —
      the paper cannot assert novelty until it exists.
   c. Venue decision (D5) — blocks the paper's final framing, not the
      engine.
   d. `coder`'s branch is behind main and its pre-rewrite TODOs (port v1
      from an old repo) are **superseded** by the fresh-project rewrite —
      flag to coder so they build from `lessons_learned.md`, not a v1 port.

## Actions taken

- Recorded binding decisions D1–D7 in `DECISIONS.md` (scope: 2D forced
  turbulence first; Re ∈ {100,1000,5000}; invariants; novelty gating; venue
  open; two-lens review process; scaffold-change rule).
- Wrote the standing two-lens acceptance checklist (`reviews/CHECKLIST.md`).
- Sent start-of-work messages to `coder`, `theoretical-research`,
  `writing-research`, and `writer` (see outbox).

## Verdict

Nothing to merge besides the reviewer's own state files. No ownership
violations. The binding risk right now is **momentum**, not quality: the
plan in `AGENTS.md` is sound (standard, well-understood steps), so the
reviewer's job until artifacts exist is to keep the dependencies unblocked
(D3.3 invariant, D4 survey, D5 venue) and hold the two-lens bar for
everything that lands. Next review cycle when any of: first engine results,
first theory notes, first survey/venue material, or first paper skeleton.
