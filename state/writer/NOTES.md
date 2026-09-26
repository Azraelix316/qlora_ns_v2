# NOTES.md — writer

> Branch: `agent/writer` · Worktree: `worktrees/writer`
> Status: working the reviewer's WRITER_ORDER (R104, supersedes all outbox history): W1 abstract (D13) + W2 contributions (D14) + W3 intro summary (D11) pasted verbatim, D15 `99.9%`→`99%` fixed; reviewer-owned paths reset to origin/main; pre-push registry run done (memory rows fail on a not-landed D89 artifact — on agent/coder — and 4 N=128 rows on missing crossover_N128.json, both flagged to reviewer); next W4 (§3) and W5 (§4).

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
| `00_abstract.tex` | **replaced 2026-09-26 with D13's 210-word abstract (W1)**, pasted verbatim, diff-verified against the order's fenced block; all numbers reviewer-verified |
| `01_introduction.tex` | **W3 applied 2026-09-26**: D11 summary sentence (clauses ii–iii + validation replaced, clause i kept; `1.1e-13`/`1.1e-11`, `2.1–2.7×`, no "turbulent dynamics"/"rank growth"); D4 short form (R5d binding wording, FLAG-D4) unchanged |
| `02_contributions.tex` | **replaced 2026-09-26 with D14's 5-item list (W2)**, pasted verbatim (fixed my own `$10^{278}}` typo); section heading/label + "Our contributions are:" kept |
| `03_related_work.tex` | drafted; D4 full form (R5d binding wording, FLAG-D4); `tab:related` High-Re cell = `target`; Osepko flagged |
| `04_methods.tex` | drafted; governing section: I1–I4 numbering, eq:pin/energy, prop:viscous, eq:step, eq:indicator; **D15 fix 2026-09-26** (`99\%` at :288) |
| `05_experimental_setup.tex` | drafted; scheme parameters [PENDING-CODER] (grids, Δt, ICs, windows, hardware); **D15 fix 2026-09-26** (`99\%` at :86 + stale PENDING comment :91) |
| `06_results.tex` | drafted; all numbers/figures [PENDING-CODER]; `tab:div` placeholders; step-0 per R5m (0.319, not 0.0); **D15 fix 2026-09-26** (`99\%` at :133) |
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

- 2026-09-26 Session after the reviewer's overnight restructure
  (DECISIONS now D1–D91; `WRITER_ORDER.md` R104 "supersedes every message";
  `START_HERE.md` R118; compacted outbox). Merged `origin/main` into
  `agent/writer`; the merge left stale D26-era copies of reviewer-owned files
  on my branch — reset all of `state/reviewer/` to `origin/main` (commit
  03a4600) and verified `git diff origin/main HEAD -- state/reviewer/` empty.
  Read `START_HERE.md` + `WRITER_ORDER.md` (all 702 lines) in full. Executed:
  **W1** (D13 abstract pasted verbatim, diff-verified against the order's
  fenced block), **W2** (D14 five-item contributions pasted verbatim; caught
  and fixed my own typo `$10^{278}}` → `$10^{278}$`), **W3** (D11: intro
  summary clauses (ii)–(iii) + validation sentence replaced, clause (i) kept),
  **D15** (`99.9%`→`99%` in `04_methods.tex:288`,
  `05_experimental_setup.tex:86` + its stale PENDING comment `:91`,
  `06_results.tex:133`; zero `99.9` remains in `paper/`). Pre-push checks:
  `claims_registry.py` Part 2's `99.9%` finding reads the *pushed* state
  (`git origin/agent/writer:paper/sections`) and clears on this push; Part 1
  now 14/24 — six memory rows fail because `main`'s `peak_memory.json` is the
  D52.6-era artifact (2.24/4.27/0.066) while the registry encodes D89's
  re-measured values, which I verified exist on `origin/agent/coder`
  (2.37109375/4.2109375/2.17578125/3.6328125/floor 0.09765625; one
  `rank_independence_resolved=False` at N=128 dlra, per D89) — an
  artifact-landing gap, flagged to reviewer, not mine to fix; four N=128 rows
  fail on missing `crossover_N128.json` (C2-1, known). `check_order_withdrawn.py`:
  remaining candidates all sit in sections not yet rewritten (W4–W9). While
  preparing the push, `origin/main` moved twice (dbd1075, 2cbcab2) — merged
  both (83063c2, 456367b), each time resolving conflicts by resetting all of
  `state/reviewer/` to `origin/main` (verified empty diff). Latest state
  absorbed: D89 memory artifact NOW ON MAIN (registry memory rows pass;
  `+2.37`/`+4.21 MiB`, floor `0.098`, overhead variation resolved at N=64,
  NOT resolved at N=128 — so neither "flat in rank" nor "grows with rank" is
  supportable at N=128); cost band `2.24–2.74×` quoted to one sig fig,
  pessimistic floor `1.4×` (D91/R128); D18c §6 supplied (7 blocks) with the
  figure mapping (use the 8 existing figures; no Taylor–Green figure exists;
  `fig_div_free` goes into `sec:res-div`; use PDFs); D18d §7 supplied (4
  blocks); R130 hedges (window/Re-invariance and the r=16 saturation contrast
  are N=64-only — never "at every grid"); R132 three `10^{-14}` sites (W4:
  `04_methods.tex:275`; W7: `06_results.tex:105` + `tab:div` caption); R136
  final energy population `1.3e-4`–`4.9e-4`, worst case = SP-DLRA itself;
  `crossover_N128.json` still not on main (registry 29/33, 4 N=128 rows).
  Re-verified: abstract + contributions still byte-identical to the current
  order's D13/D14 blocks. Pushing W1+W2+W3+D15 as the first reviewable unit;
  next W4 (§3) and W5 (§4).
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
