# PROTOCOL.md — cross-node agent protocol

Five agents collaborate on this project from **different server nodes**. The git remote
(`origin`) is the only shared medium: local files are private, so everything
shared must be committed and pushed. Keep it simple — the rules below are the
whole protocol.

## Roles

| Agent | Branch | Worktree (per node) | Mission |
|---|---|---|---|
| theoretical-research | `agent/theoretical-research` | `worktrees/theoretical-research` | theories, improvements |
| coder | `agent/coder` | `worktrees/coder` | engine, simulations, benchmarks |
| writer | `agent/writer` | `worktrees/writer` | paper draft |
| reviewer | `agent/reviewer` | `worktrees/reviewer` | reviews, decisions, merges to main |
| writing-research | `agent/writing-research` | `worktrees/writing-research` | conferences, references, novelty |

One active session per agent at a time (one node per role).

## Ownership — you may write only inside your paths

| Owned paths | Agent |
|---|---|
| `state/theoretical-research/`, `docs/theory/` | theoretical-research |
| `state/coder/`, `solvers/`, `experiments/` | coder |
| `state/writer/`, `paper/` | writer |
| `state/reviewer/` | reviewer |
| `state/writing-research/`, `docs/references/`, `refs.bib`, `docs/venues/`, `docs/structure/` | writing-research |
| `AGENTS.md`, `PROTOCOL.md`, `scripts/`, `lessons_learned.md` | scaffold — reviewer approves changes |

Everything else is read-only for you. This is what prevents overwrites:
two agents never write the same file.

## Rules

1. **Work only in your own worktree, on your own branch** (`agent/<you>`).
2. **Never push to `main`; never force-push.** Only the reviewer merges into
   `main`. (Even a rule violation cannot clobber anyone: bad edits land on
   your branch and surface at review/merge time.)
3. **Session start** (in your worktree):
   `scripts/agent.sh start <you>`
   → fetches, merges `origin/main` into your branch, prints the status board
   and your inbox.
4. **Message another agent** (you write in *your* outbox, never in theirs):
   `scripts/agent.sh send <you> <them> "message"`
   → appends a dated entry to `state/<you>/outbox/to-<them>.md`.
   Run `finish` for it to be delivered: the recipient's inbox is read from
   your **pushed** branch (`origin/agent/<you>`). Recipients see it at their
   next `start`/`inbox`.
5. **Read another agent's latest work** (their branch may be ahead of main):
   `git fetch origin && git show origin/agent/<them>:<path>`
   (e.g. `state/<them>/NOTES.md`, or a file in their owned paths).
6. **Session end:** update the `> Status:` line and append a dated `## Log`
   entry in `state/<you>/NOTES.md`, then
   `scripts/agent.sh finish <you>` → commits everything and pushes your branch.
7. **Merge conflicts** (rare, by ownership design): resolve by keeping the
   other side's content intact, and flag the file's owner via outbox. Never
   delete another agent's content to make a merge pass.

## New node setup (once per role per node)

    git clone git@github.com:Azraelix316/qlora_ns_v2.git
    cd qlora_ns_v2
    git worktree add worktrees/<role> agent/<role>
    cd worktrees/<role>
    scripts/agent.sh start <role>

## Message conventions

- Inbox files accumulate; treat old entries as history. Do not edit or delete
  another agent's outbox files.
- **Read your inbox newest-message-first.** `inbox` prints an append-only file
  top to bottom, so the *oldest* verdict appears first and later verdicts
  supersede it. This has already caused one agent to spend a full cycle
  executing a superseded fix list. Concretely: after `start`, read the **last**
  `## <timestamp>` block in each inbox before anything else, and treat anything
  above it as history. Where a verdict conflicts with
  `state/reviewer/DECISIONS.md`, **DECISIONS.md wins** — each revised decision
  opens with an `OPERATIVE TEXT` block naming what currently governs.
- **Run `start` before working, every session.** A branch that has not merged
  `origin/main` is on a stale base: it will lack the current engine, the current
  review state, and any corrected `AGENTS.md` / `lessons_learned.md`.
- **Verify every identifier against a primary source** — arXiv abs pages for
  arXiv IDs, `https://api.crossref.org/works/<doi>` for DOIs. Do not write a
  citation from memory; every fabricated reference found in this project so far
  was written from memory. Note that `doi.org` redirects return 404 in this
  environment even for valid DOIs, so use the Crossref API.
- Decisions: only the reviewer records binding decisions
  (`state/reviewer/DECISIONS.md`). Everyone else may *propose* via outbox.
- Keep `state/` files small (text/markdown/JSON). Large outputs stay in the
  owner's deliverable paths (`experiments/`, `paper/`, ...).
