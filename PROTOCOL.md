# PROTOCOL.md — cross-node agent protocol

Five agents collaborate on v2 from **different server nodes**. The git remote
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
| `state/writing-research/`, `docs/references/`, `refs.bib` | writing-research |
| `AGENTS.md`, `PROTOCOL.md`, `scripts/`, `summary_of_v2.md` | scaffold — reviewer approves changes |

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
- Decisions: only the reviewer records binding decisions
  (`state/reviewer/DECISIONS.md`). Everyone else may *propose* via outbox.
- Keep `state/` files small (text/markdown/JSON). Large outputs stay in the
  owner's deliverable paths (`experiments/`, `paper/`, ...).
