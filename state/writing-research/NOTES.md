# NOTES.md — writing-research

> Branch: `agent/writing-research` · Worktree: `worktrees/writing-research`
> Status: fresh — no sessions yet (created 2026-09-24)

## Mission

Research **conferences/venues and references** for the paper. Venue
selection (NeurIPS/ICML ML-for-Sci framing vs SIAM J. Sci. Comput. /
J. Comput. Phys. methods framing), templates, deadlines — and the literature
base: run the arXiv novelty survey (a prior one was lost — see
`lessons_learned.md`), persist it, and maintain `refs.bib`.

## Owned paths (write only here)

- `state/writing-research/` — this board, `arxiv_index.json`
- `docs/venues/` — venue research
- `refs.bib` — the shared BibTeX (the writer consumes it; only you edit it)

## First TODOs

- [ ] Venue shortlist in `docs/venues/`: deadlines, templates, formatting for
      NeurIPS, ICML, SIAM J. Sci. Comput., J. Comput. Phys. → send the
      recommendation to `reviewer` for the decision.
- [ ] Run the arXiv API survey confirming the novelty claim (scope in
      `AGENTS.md` + `lessons_learned.md`). **Persist after every query batch**
      to `state/writing-research/arxiv_index.json` (lesson from a prior lost
      session — do not batch to the end).
- [ ] Produce `refs.bib` with verified references (arXiv IDs verified via the
      API — no fabricated IDs).
- [ ] Send `refs.bib` readiness + a suggested paper structure to `writer`.

## Log

- 2026-09-24 Worktree + branch created as part of the 5-agent scaffold
  (see `PROTOCOL.md`).
