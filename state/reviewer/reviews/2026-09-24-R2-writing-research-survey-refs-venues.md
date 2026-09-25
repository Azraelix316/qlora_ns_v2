# R2 — writing-research: arXiv survey, refs.bib, venue shortlist

- **Date:** 2026-09-24
- **Branch reviewed:** `agent/writing-research` — `17b796d` (initial push, 19:06 UTC) and `6a41b2a` (revision, 19:58 UTC)
- **Reviewer:** reviewer

## Scope

First substantive deliverable from `writing-research`:

- `refs.bib` — 20 → 27 entries
- `state/writing-research/arxiv_index.json` — 14 → 21 entries
- `docs/venues/venue_shortlist.md` — draft, revised in the second commit
- `docs/structure/suggested_structure.md` — unchanged between the two commits
- outbox to writer

## Lens 1 — Correctness

### refs.bib — PASS (after the revision)

All 27 arXiv IDs verified against `arxiv.org/abs/<id>` pages (title + first
author checked): **27/27 genuine, no fabricated or misattributed IDs.**

- The mandatory D4 entry `girfoglio2022pod`
  (Girfoglio–Quaini–Rozza, arXiv:2201.00756, "A POD-Galerkin reduced order
  model for the Navier-Stokes equations in stream function-vorticity
  formulation") is **present**.
- The revision added 6 incompressible-NS ROM entries (Klein 2304.09229,
  Prakash 2401.17383, Siena 2404.19600, Star 2010.06964, Prusak
  2211.14528, Kim 2302.01278) — all verified. They strengthen the novelty
  framing: none is an *online* DLRA method with an exact divergence-free
  constraint validated at high-Re forced turbulence.

### arxiv_index.json — FAIL on one entry (blocker, unchanged from round 1)

21 entries; the 14 from the initial push are unchanged, plus the same 7
NS-ROM entries as in `refs.bib`.

- **`2412.05988v2` is still misattributed.** The entry's title, authors, and
  summary describe "A review of low-rank methods for time-dependent kinetic
  simulations" (Einkemmer, Kormann, Kusch, McClarren, Qiu) — that paper is
  **arXiv:2412.05912** (v2, 2025-06-18; reviewer-verified via the abs page).
  `2412.05988` is an unrelated astrophysics paper ("A potential exomoon from
  the predicted planet obliquity of β Pictoris b"). The ID is off by 76 —
  almost certainly a typo.
- Fix: change the id to `http://arxiv.org/abs/2412.05912v2` (the title,
  authors, and `updated` date in the entry already match 05912), or delete
  the entry.

### Novelty-claim support — PARTIAL

The 0-hit query that directly supports D4 (the "divergence-free ∧ dynamical
low-rank" search returning no results) is **not persisted** — the index only
contains hits from the broad "structure-preserving low-rank" query, which
includes many hits irrelevant to the claim (SPLIC image completion, SPMD-LRT
tensors, spectral CT, LoRITa network compression, vision-language alignment,
antisymmetric CP, gas-pipeline Kalman filters, dSDA, QTT-DLRA). The negative
result *is* the novelty evidence and must be reproducible.

### Venue shortlist — DRAFT, not yet a recommendation

The revision adds ICASSP 2027, target-timing column, and a "Submission
Strategy Recommendation" section (fast track JCP/SISC; ICML 2027 primary
conference; NeurIPS 2027 contingency).

- All deadlines remain "needs verification" — no official source cited. D5
  cannot close on unverified deadlines (D4 rule: verify before asserting).
- ICASSP 2027 at "moderate" relevance is a stretch fit for NS turbulence;
  acceptable as a long shot, but the recommendation must be ranked.
- Per their mission, the venue recommendation must be **sent to the reviewer
  via outbox**, not only left in `docs/venues/`. Inbox check: nothing
  received. D5 stays OPEN.

### Writing lens

- `docs/structure/suggested_structure.md` matches the AGENTS.md five-step
  plan; usable skeleton for the writer.
- Venue doc is readable; the summary table is useful.
- Suggestion (not a blocker): a `relevant: true/false` flag per index entry —
  ~9 of the 21 index entries are ML hits the writer must wade through for
  related work.

## Ownership audit

`docs/venues/` and `docs/structure/` were **unowned paths** in the
PROTOCOL.md ownership table (scaffold gap — AGENTS.md listed
`docs/venues/` as a key path without assigning it). The writes into those
paths were therefore violations *by scaffold gap*, not by agent error.
**Scaffold amended by the reviewer (recorded as D8):** both paths are now
assigned to `writing-research` in `PROTOCOL.md` and `AGENTS.md`. The existing
content on their branch is accepted as-is; no rework required.

## Verdict

**HOLD — do not merge.** Blockers (both must be fixed):

1. Index entry id `2412.05988v2` → `2412.05912v2` (reviewer-verified) or
   delete the entry. *(carried over from round 1 — the revision fixed
   `refs.bib` but not the index)*
2. Persist the 0-hit "divergence-free ∧ dynamical low-rank" query (exact
   query string, date, result count) alongside the index. D4 requires the
   survey to be persisted and reproducible.

Non-blocking (next push):

3. Send the venue recommendation to the reviewer via outbox: ranked, with
   deadlines verified from official pages (URL + access date).
4. Align the "15 unique entries" count in NOTES.md with the actual index
   size (21 now; 14 at first push).
5. Suggestion: `relevant` flag on index entries.

Once blockers 1–2 land, the branch is mergeable in the next review cycle
(no re-verification of the 27 bib entries needed; the index diff will be
re-checked at that time).
