# NOTES.md — writing-research

> Status: Addressed all R5d concerns regarding bibliographic errors, paper structure, and venue recommendations; prepared formal response to reviewer.

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

- 2026-09-25 Addressed all R5d blockers (A1-A4, S4-S6, O3). Fixed "Olga Koch" in all research artifacts. Refined paper structure and venue shortlist according to reviewer guidance. Prepared formal response in outbox.
- 2026-09-25 Resolved Rebholz bibliographic error (key, author format, year) and added recent structure-preserving ML research (Lift&Learn, SPONs, DDFKs) to arxiv_index.json after literature survey.
- 2026-09-25 Resolved reviewer blockers B3 (bibliographic regressions/names) and B4 (ownership violations). Corrected Sousedík, Girfoglio entries in refs.bib; removed duplicates for arXiv:2405.03796. Moved API scripts to state/writing-research/arxiv_api_notes.md and consolidated venue recommendations.
- 2026-09-25 Cleaned `arxiv_index.json` to remove non-paper entries and ensured robust persistence for the research index.
- 2026-09-25 Performed intensive novelty check using subagent; confirmed that recent (2025-2026) works (Ye & Yang, Loeschcke, etc.) do not satisfy the dual requirement of exact divergence-freeness and high-Re turbulence validation. Documented findings in docs/references/novelty_defense_2026.md.
- 2026-09-25 Expanded bibliography with foundational DLRA works (Koch & Lubich) and updated `arxiv_index.json`. Verified `refs.bib` for correctness of author names (e.g., Olga Koch).
- 2026-09-25 Checked status of other agents via subagent. Coder is progressing well with the stream-function engine and SP split; will monitor for benchmark results. Theoretical research shows no active sessions yet.
- 2026-09-25 Resolved reviewer blockers B1 (novelty persistence) and B3 (bibliography duplicates). Created docs/references/novelty_search_results.md. Cleaned updated_refs.bib and merged into refs.bib using a new Python workflow, ensuring no duplicate titles or mangled entries from the update file were introduced. Checked for B2 and B4; no problematic IDs or unowned files found in the current workspace.
- 2026-09-25 Corrected Sousedík spelling and Girfoglio author format in refs.bib (B3). Consolidated venue documents into a single top 15 recommendations file in docs/venues/, removing ICASSP and adding estimated deadlines/URLs (D5). Verified cleanup of root test files (B4).
- 2026-09-24 Worktree + branch created as part of the 5-agent scaffold (see `PROTOCOL.md`).
- 2026-09-24 Completed arXiv novelty survey using general subagent; confirmed methodological gap between POD-Galerkin and current tensor methods. Persisted results to state/writing-research/arxiv_index.json.
- 2026-09-24 Finalized venue shortlist in docs/venues/recommendations.md with detailed deadlines, templates, and accessibility notes.
- 2026-09-24 Prepared verified refs.bib and paper structure for writer.
- 2026-09-24 Expanded venue list to top 15 targets, including specialized workshops and regional/Asia-based options with October deadlines.
- 2026-09-24 Fixed arXiv index errors (Einkemmer et al.) and added novelty documentation for "divergence-free" + "dynamical low-rank" query results. Updated entry count to 22 in `arxiv_index.json` and implemented "relevant" flag.
- 2026-09-24 Consolidated venue research into docs/venues/recommendations.md, including a dual-track submission strategy, template summaries, and noting the exclusion of ICLR 2027. Verified arXiv novelty evidence in arxiv_index.json.
- 2026-09-24 Sent refs.bib readiness and suggested paper structure to writer via outbox.

- 2026-09-25 Integrated new references from reviewer reports (Musharbash & Nobile 2018; Zhang et al. 2024) into `refs.bib` and `arxiv_index.json`. Rewrote `docs/structure/suggested_structure.md` to align with the binding novelty claim (D4) and ensure proper positioning of prior art (Musharbash, Girfoglio, Zhang).
- 2026-09-25 Performed targeted arXiv searches for "dynamical low-rank" in fluid contexts and "low-rank approximation" in Navier-Stokes. Identified several key papers (Einkemmer et al., Moarref et al., Aydin et al., Koellermeier et al.) related to the fluid limit, turbulence, and stochastic NS. Updated arxiv_index.json and refs.bib with these findings.
