# NOTES.md — writer

> Branch: `agent/writer` · Worktree: `worktrees/writer`
> Status: all 10 sections drafted and internally consistent; D4 binding R5d wording in place (GATED on D10); every quantitative claim [PENDING-CODER] until V1–V7 close; outbox to coder / writing-research / reviewer sent 2026-09-25.

## Mission

Write the paper. Draft in `paper/`, integrating: theory from
`theoretical-research` (`docs/theory/`), numbers from `coder`
(`state/coder/results/`), and references + venue from `writing-research`
(`refs.bib`, `docs/venues/`).

## Owned paths (write only here)

- `state/writer/` — this board, section status, open questions
- `paper/` — draft, sections, figures, templates

## Section status (2026-09-25)

| File | Status |
|---|---|
| `00_abstract.tex` | drafted; one-sentence quantitative summary [PENDING-CODER] |
| `01_introduction.tex` | drafted; D4 short form (sentences 2–4, R5d binding wording, FLAG-D4) |
| `02_contributions.tex` | drafted; contributions 3–4 quantitative once results land |
| `03_related_work.tex` | drafted; D4 full form (R5d binding wording, FLAG-D4); `tab:related` High-Re cell = `target`; Osepko flagged |
| `04_methods.tex` | drafted; governing section: I1–I4 numbering, eq:pin/energy, prop:viscous, eq:step, eq:indicator |
| `05_experimental_setup.tex` | drafted; scheme parameters [PENDING-CODER] (grids, Δt, ICs, windows, hardware) |
| `06_results.tex` | drafted; all numbers/figures [PENDING-CODER]; `tab:div` placeholders; step-0 per R5m (0.319, not 0.0) |
| `07_discussion.tex` | drafted 2026-09-25 (rank as diagnostic, invariants/long-time, dimensional regimes, 3D) |
| `08_limitations.tex` | drafted 2026-09-25 (2D/periodic/Re≤5000, TG-only decay, no per-step speedup, no stability analysis, D3 open, no V2 study) |
| `09_conclusion.tex` | drafted 2026-09-25 (summary + [PENDING-CODER] headline + future work) |
| `main.tex` | venue-agnostic `article` skeleton + swap-in comment; plain `\cite`, no natbib |
| `references.bib` | 38 entries, all web-verified 2026-09-25 (15 [V] arXiv, 14 [J], 9 [C] classics) |
| `README.md` | counts, flags, placeholder legend; D4 flag = GATED on D10 |

## Consistency checks passed (2026-09-25)

- R5d barred phrases: zero in body text (hits only in intentional FLAG-D4 comments in 01/03).
- natbib: zero occurrences (plain `\cite` + `thebibliography`-style `\bibitem`-free bib; no natbib commands anywhere).
- Every cited key ∈ `references.bib` (fixed `orzag1971` → `orszag1971` typo in 01).
- Every `\ref`/`\eqref` target defined; no duplicate labels.
- All 11 `.tex` files brace-balanced (non-comment lines).
- I1–I4 tags consistent with 04's governing numbering (I1 divergence-free, I2 energy, I3 rank economy, I4 turbulent fidelity); fixed 07 (energy I3→I2, comment I3/I4→I2/I4), 09 (I3→I2), 06 (dropped wrong I3 tag from the cost subsection).
- 06 figure-caption bracket bug fixed (six captions had their closing `}` inside a trailing comment).

## Open items

- [ ] coder: scheme confirmations + per-invariant numbers + 6 figure data sets + `tab:div` + computed step-0 error (R5m) — list sent in outbox.
- [ ] writing-research: consolidated venue doc with cited deadlines (D5); reconcile shared `refs.bib` vs `paper/references.bib`; confirm R5d-priority entries; identify "Osepko et al.".
- [ ] reviewer: confirm D4 wording matches R5d intent; sanity-check the P_in sign derivation (eq:pin); venue decision.
- [ ] theoretical-research: forcing-aware invariant (D3) + turbulent rank-growth theory + dimensional-regime boundaries → fill [PENDING-THEORETICAL-RESEARCH] in 04/07/08/09.
- [ ] After V1–V7 close: replace all [PENDING-CODER] with artifacts-traceable numbers (CHECKLIST 1.1), un-gate D4, adapt template to the settled venue.

## Log

- 2026-09-25 Worktree + branch created as part of the 5-agent scaffold
  (see `PROTOCOL.md`).
- 2026-09-25 Paper drafted end-to-end. All 10 sections + main.tex +
  references.bib (38 verified entries) + README in `paper/`. D4 claim
  rewritten to the reviewer's binding R5d wording in 01 (short) and 03
  (full), each with a FLAG-D4 comment; barred phrases verified absent from
  body text. Wrote 07_discussion, 08_limitations, 09_conclusion. Consistency
  pass: no natbib, all cited keys verified against the bib, all refs defined,
  no duplicate labels, braces balanced, I1–I4 tags aligned with 04 (fixed
  energy-tag I3→I2 in 07/09 and the cost subsection in 06). Fixed the 06
  figure-caption bracket bug and the `orszag1971` key typo. Sent outbox to
  coder (scheme confirmations, I1–I4 numbers, 6 figure data sets, tab:div,
  step-0 per R5m, R5k/R5l addenda), to writing-research (venue doc with
  cited deadlines, refs reconciliation, Osepko ID), and to reviewer (draft
  review request, P_in sign sanity check, D4 wording confirmation). No merge
  request yet.
