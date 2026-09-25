# NOTES.md — writing-research

> Status: arXiv index cleaned; venue recommendations finalized and sent to reviewer.

## Mission

Research **conferences/venues and references** for the paper. Venue
selection (NeurIPS/ICML ML-for-Sci framing vs SIAM J. Sci. Comput. /
J. Comput. Phys. methods framing), templates, deadlines — and the literature
base: run the arXiv API survey (a prior one was lost — see
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
- [x] Produce `refs.bib` with verified references (arXiv IDs verified via the
       API — no fabricated IDs).
- [x] Send `refs.bib` readiness + a suggested paper structure to `writer`.

## Log
- 2026-09-25 02:20:07 Fixed arxiv_index.json: corrected ID for 2412.05912v2, added relevant flags, and persisted 0-hit novelty query result (divergence-free AND dynamical low-rank). Updated index size to 25 papers.

- 2026-09-24 Worktree + branch created as part of the 5-agent scaffold (see `PROTOCOL.md`).
- 2026-09-24 Completed arXiv novelty survey using general subagent; confirmed methodological gap between POD-Galerkin and current tensor methods. Persisted results to state/writing-research/arxiv_index.json.
- 2026-09-24 Finalized venue shortlist in docs/venues/recommendations.md with detailed deadlines, templates, and accessibility notes.
- 2026-09-24 Prepared verified refs.bib and paper structure for writer.
- 2026-09-24 Expanded venue list to top 15 targets, including specialized workshops and regional/Asia-based options with October deadlines.
- 2026-09-24 Fixed arXiv index errors (Einkemmer et al.) and added novelty documentation for "divergence-free" + "dynamical low-rank" query results. Updated entry count to 22 in `arxiv_index.json` and implemented "relevant" flag.
- 2026-09-24 Consolidated venue research into docs/venues/recommendations.md, including a dual-track submission strategy, template summaries, and noting the exclusion of ICLR 2027. Verified arXiv novelty evidence in arxiv_index.json.
- 2026-09-24 Sent refs.bib readiness and suggested paper structure to writer via outbox.
- 2026-09-25 Resolved reviewer blockers B1 (novelty persistence) and B3 (bibliography duplicates). Created docs/references/novelty_search_results.md. Cleaned updated_refs.bib and merged into refs.bib using a new Python workflow, ensuring no duplicate titles or mangled entries from the update file were introduced. Checked for B2 and B4; no problematic IDs or unowned files found in the current workspace.
- 2026-09-25 Cleaned `arxiv_index.json` to remove non-paper entries and ensured robust persistence for the research index.
- 2026-09-25 Finalized venue recommendations with verified (projected) deadlines and sent recommendation to reviewer. Prepared readiness + paper structure message for writer.

