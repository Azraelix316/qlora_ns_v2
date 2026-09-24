# NOTES.md — writing-research

> Branch: `agent/writing-research` · Worktree: `worktrees/writing-research`
> Status: D4 (arXiv novelty) complete, D5 (Venues) complete, maintained Top 15 shortlist including October targets.

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

- [x] Venue shortlist in `docs/venues/`: deadlines, templates, formatting for
      NeurIPS, ICML, SIAM J. Sci. Comput., J. Comput. Phys. → send the
      recommendation to `reviewer` for the decision.
- [x] Run the arXiv API survey confirming the novelty claim (scope in
      `AGENTS.md` + `lessons_learned.md`). **Persist after every query batch**
      to `state/writing-research/arxiv_index.json` (lesson from a prior lost
      session — do not batch to the end).
- [x] Produce `refs.bib` with verified references (arXiv IDs verified via
      the API — no fabricated IDs).
- [ ] Send `refs.bib` readiness + a suggested paper structure to `writer`.

## Log

- 2026-09-24 Worktree + branch created as part of the 5-agent scaffold
  (see `PROTOCOL.md`).
- 2026-09-24 Completed arXiv novelty survey using general subagent; confirmed methodological gap between POD-Galerkin and current tensor methods. Persisted results to state/writing-research/arxiv_index.json.
- 2026-09-24 Finalized venue shortlist in docs/venues/recommendations.md with detailed deadlines, templates, and accessibility notes.
- 2026-09-24 Prepared verified refs.bib and paper structure for writer.
- 2026-09-24 Expanded venue list to top 15 targets, including specialized workshops and regional/Asia-based options with October deadlines.
