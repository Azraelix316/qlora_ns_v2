# NOTES.md — writing-research

> Branch: `agent/writing-research` · Worktree: `worktrees/writing-research`
> Status: Monitoring other agents; ready to expand literature/venue research as needed.

## Mission

Research **conferences/venues and references** for the paper. Venue
selection (NeurIPS/ICML ML-for-Sci framing vs SIAM J. Sci. Comput. /
J. Comput. Phys. methods framing), templates, deadlines — and the literature
base: run the arXiv API survey (a prior one was lost — see
`lessons_learned.md`), persist it, and maintain `refs.bib`.

## Owned paths (write only here)

- `state/writing-research/` — this board, `arxiv_index.json`
- `docs/venues/` — venue research
- `docs/structure/` — suggested paper structure
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
- 2026-09-24 Completed first arXiv survey batch using multiple queries focusing on DLRA and structure preservation. Collected 15 unique entries. Added relevant papers to `refs.bib` and persisted results to `state/writing-research/arxiv_index.json`.

- 2026-09-24 Completed final broad arXiv sweep (Navier-Stokes/incompressible + low-rank). Findings strongly support the novelty claim regarding exact divergence-freeness in DLRA. Created preliminary venue shortlist in docs/venues/ and suggested paper structure in docs/structure/. Ready to communicate with writer.

- 2026-09-24 Performed broad arXiv search for incompressible Navier-Stokes/low-rank ROMs to enrich background literature. Added 7 verified citations (including Girfoglio et al. as key prior art) to refs.bib and updated arxiv_index.json.

- 2026-09-24 Checked other agents' status boards; no new work detected from `coder` or `theoretical-research`. Standing by to assist with literature or venue research once progress is made.
