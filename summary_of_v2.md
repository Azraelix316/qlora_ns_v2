# summary_of_v2.md — Lessons Learned per Worktree

> Scope: the v2 repo (`qlora_ns_v2`) and its two agent worktrees, as of 2026-09-24.
> Grounding: all branches (`main`, `writer/draft`, `feature/agent-lit-search`) point at the
> same initial commit (`b761512`, LICENSE only). The only substantive artifact in the repo is
> `worktrees/agent-lit-search/RESEARCHER_NOTES.md` (untracked). Everything below is derived
> from that file [S1], the shared `state/` board [S3], and what is *missing*.
>
> **Note:** the source files cited below no longer exist in this repo — they were removed
> in the 2026-09-24 cleanup. See [Sources](#sources) for what each source was and its
> current location (if any).

## 1. `main` (repo root)

**State:** skeleton only — `state/` shared board (`literature/`, `results/`, `locks/`) and the
`worktrees/` layout. Nothing committed beyond the initial LICENSE commit; `state/` and
`worktrees/` are untracked.

**Lessons learned:**

- **The blackboard convention worked.** `state/locks/agent-lit-search-research.LOCK` [S3] and the
  notes file [S1] show a functioning coordination protocol: shared state lives in one place,
  each agent takes a lock before heavy work, and status is a file other agents read first.
- **Convention gap: the board itself is not under version control.** `state/` and
  `worktrees/` are untracked in main. If the repo is ever re-cloned or reset, the shared
  board disappears. Commit the `.gitkeep`s (or a `state/README.md` documenting the
  convention) so the protocol survives.
- **v1 → v2 handoff is documented and load-bearing.** The v1 handoff
  (`/home/jaredc/HANDOFF_qlora_ns.md`, v1 repo at `/home/jaredc/qlora_ns`) [S2] is the single
  source of truth for what already exists. Lesson: v2 must not re-derive v1's validated
  numbers (invariants, ~3x speedup at 64², max rel L2 < 2% at T=100) — cite them.

## 2. `worktrees/agent-lit-search` (branch `feature/agent-lit-search`)

**State:** one session (2026-09-23), recorded in `RESEARCHER_NOTES.md` [S1]. Substantive
novelty checks done; the session **ended mid-task** — no docs committed, no branch commit,
no merge proposal, and the in-progress 16-query arXiv API survey was never persisted to
`state/literature/`.

**Lessons learned (from [S1]):**

- **The core novelty claim holds (as far as checked).** A *dynamical low-rank* method that
  (a) evolves incompressible NS directly on a low-rank manifold, (b) enforces ∇·u = 0
  *exactly* (stream-function / Leray structure), and (c) is validated on **high-Re
  turbulent** dynamics does not appear on arXiv. Six UI phrase checks: "dynamical low-rank"
  + NS → 3 hits, none applicable; "adaptive low-rank" + NS → 0 hits; closest prior art is
  **Girfoglio–Quaini–Rozza (arXiv:2201.00756)** — offline POD-Galerkin ROM in
  stream-function–vorticity form. It is not dynamical, not adaptive-rank, not high-Re
  turbulent. The API full survey was meant to confirm this; it is still outstanding.
- **The v1 gap is correctly identified as *turbulence*.** v1's Taylor–Green validation is
  laminar, decaying, rank 3→2→1. "High-Re nonlinear dynamics" in the goal means forced,
  turbulent, rank ≫ 3, slow singular-value decay. v2's contribution is the science
  (turbulent validation, adaptive-rank theory, rigorous analysis), not the engine.
- **Lesson (process): persist intermediate research artifacts immediately.** The 16-query
  arXiv API survey was "in progress" in the session context and then the session stopped —
  that work is effectively lost and would need re-running. Machine-readable intermediate
  results (`arxiv_index.json`, `refs.bib`) should be written out as soon as each query
  batch returns, not batched to the end of the session.
- **Lesson (process): close the loop on your own TODO list.** The notes' own TODO
  (curate sources, write `docs/literature_review.md`, `docs/theory_brainstorm.md`,
  `docs/novelty_and_path.md`, commit, propose merge) is entirely unfinished. A dated log
  entry is not the same as a finished session; the next lit-search session should start by
  re-running the API survey and finishing those four artifacts.
- **Open decisions the group still owes the writer:** 2D forced turbulence (Kolmogorov
  flow) first vs. 3D tensor DLRA (notes recommend 2D first), and venue (SIAM J. Sci.
  Comput. / J. Comput. Phys. methods framing vs. NeurIPS/ICML ML-for-Sci framing).

## 3. `worktrees/agent-draft-writer` (branch `writer/draft`)

**State:** empty — no notes file, no template skeleton, no commits, nothing to read.

**Lessons learned:**

- **No trace, no state.** Whatever the writer agent did (if it started at all) left zero
  artifacts. The lit-search agent explicitly handed it a question ("wire
  `state/literature/refs.bib` into the NeurIPS/ICML/SIAM template skeleton; suggested
  structure in `docs/novelty_and_path.md` §5") and got no response — that doc doesn't
  exist yet either.
- **Lesson: every agent drops a blackboard note on its first action.** The lit-search
  agent's `RESEARCHER_NOTES.md` [S1] (mission, status, dated log, questions) is the pattern to
  copy. The writer should immediately create `worktrees/agent-draft-writer/WRITER_NOTES.md`
  and a minimal paper-template skeleton commit, even before references arrive, so the
  handoff has a target to land on.
- **Sequencing risk:** the writer is blocked on lit-search's `refs.bib` and
  `novelty_and_path.md` §5, but lit-search is itself stalled. Neither agent can make
  progress alone — the next step is to unblock lit-search (finish the API survey + docs),
  then give the writer the BibTeX and proposed structure.

## Cross-worktree takeaways

1. **Nothing is committed anywhere.** Three branches, one shared initial commit. Every
   artifact (including the only notes file) is untracked. First action for the next session
   on any branch: commit.
2. **One agent followed the protocol, the other left no trace.** The difference between
   "resumable work" and "work that had to be redone" is a dated notes file. Enforce it.
3. **Intermediate state must land in `state/` while the session is alive.** Both the API
   survey results and the writer's plan should be written to the shared board
   incrementally; `state/literature/` and `state/results/` are still empty.
4. **The science story is clear; the execution is not.** Novelty claim is defensible, the
   v1→v2 gap (turbulence) is well framed, and the nearest prior art is identified. What
   remains: confirm via the full API survey, then forced-turbulence validation with
   adaptive rank and rigorous analysis, plus the paper.

## Sources

All claims in this document are drawn from the following sources, cited above in
parentheses:

1. **[S1] `RESEARCHER_NOTES.md`** — the lit-search agent's blackboard (mission, v1 context,
   novelty-check table, session-1 log, open questions).
   - Location when written: `worktrees/agent-lit-search/RESEARCHER_NOTES.md` (untracked),
     as of 2026-09-23.
   - **Status: no longer in this repo.** It was briefly preserved at `docs/RESEARCHER_NOTES.md`
     (commit `189524f`) and then deleted in the 2026-09-24 cleanup (commit `4333098`). Its
     content is cited here; to recover it, restore from commit `189524f`
     (`git show 189524f:docs/RESEARCHER_NOTES.md`).
2. **[S2] v1 handoff and repo** — `/home/jaredc/HANDOFF_qlora_ns.md` and the v1 repo at
   `/home/jaredc/qlora_ns` (pushed to `github.com:Azraelix316/qlora_ns.git`).
   - **Status: still exists locally** (outside this repo); the v1 numbers cited above
     (invariants, ~3x speedup at 64², max rel L2 < 2% at T=100) come from the v1 M3
     validation reported in the handoff.
3. **[S3] Shared state board** — `state/locks/agent-lit-search-research.LOCK` and the empty
   `state/{literature,results}/` directories in this repo.
   - **Status: deleted in the 2026-09-24 cleanup.** Only the lock's header (agent, branch,
     task, start date, "heavy web research in progress" note) is quoted above.
