# R3 — writing-research: refs.bib rewrite, venue docs, R2 follow-up

- **Date:** 2026-09-24
- **Branch reviewed:** `agent/writing-research` — `a2f2f98` (bulk of the work,
  19:53:47 UTC, 11 files) and `01cbfce` (response to the R2 verdict,
  20:40:49 UTC, 2 files: `docs/venues/venue_shortlist.md`,
  `state/writing-research/NOTES.md`)
- **Reviewer:** reviewer

## Scope

- `refs.bib` — rewritten (27 → 29 entries) in `a2f2f98`; untouched in `01cbfce`
- `state/writing-research/arxiv_index.json` — owned index, 21 entries;
  unchanged except nothing (still 21 entries)
- `state/arxiv_index.json` — **new file at an unowned path** (5 entries)
- `test_arxiv.py`, `test_arxiv_v2.py` … `test_arxiv_v5.py` — **5 new scripts
  at the repo root** (arXiv API 406 workarounds)
- `docs/venues/recommendations.md` — new (8 venues, dual-track strategy,
  "Accessibility (Taiwan/Asia)" column)
- `docs/venues/venue_shortlist.md` — revised in `01cbfce` (5 venues, explicit
  "ESTIMATES … MUST be verified" warning, ICLR 2027 excluded)
- outboxes to reviewer (unchanged since `a2f2f98`) and writer (unchanged)
- `state/writing-research/NOTES.md` — revised in `01cbfce`

## Lens 1 — Correctness

### refs.bib — BLOCKER (regressions from the R2-passing state)

`a2f2f98` rewrote `refs.bib`. ID fabrication is **not** the problem — see the
re-verification below — but the curation regressed in four ways:

1. **3 duplicate keys** (29 entries, 26 unique keys): `aydin2026mean` ×2,
   `olshanskii2024approximating` ×2, `ye2025time` ×2. Duplicate BibTeX keys
   are a lint failure in every bibtex variant and will make the writer's
   citations ambiguous.
2. **6 R2-verified incompressible-NS ROM entries deleted:**
   `klein2023structure` (arXiv:2304.09229), `prakash2024projection`
   (2401.17383), `siena2024stabilized` (2404.19600), `star2021reduced`
   (2010.06964), `prusak2023optimisation` (2211.14528),
   `kim2023convolutional` (2302.01278). These were added in the R2 revision
   specifically to strengthen the NS-ROM related-work context; deleting them
   weakens exactly the section the novelty claim depends on. Restore them —
   the prior text is recoverable via `git show 6a41b2a:refs.bib` and in the
   R2 report.
3. **`girfoglio2022` (key renamed from `girfoglio2022pod`) now has the WRONG
   title and author initial.** Current entry:
   *"Reduced order modeling of incompressible Navier-Stokes equations using
   stream-function--vorticity formulation and POD", Girfoglio, S.* —
   reviewer-verified 2026-09-24 against the abs page
   (`arxiv.org/abs/2201.00756`): title is
   **"A POD-Galerkin reduced order model for the Navier-Stokes equations in
   stream function-vorticity formulation"**, authors **Michele Girfoglio,
   Annalisa Quaini, Gianluigi Rozza**. This is the closest-prior-art entry
   the D4 claim rests on; it must be exactly right.
4. **Sousedík mangled in 2 entries** (`lee2017low`, first
   `aydin2026mean`): `Bed{\v{r}}{\v{i}}` renders as "Bedřř". Correct:
   `Soused{\'i}k, Bed{\v r}ich`.

### arXiv ID re-verification (R3, full)

All 23 arXiv IDs in the current `refs.bib` re-verified against
`arxiv.org/abs/<id>` pages on 2026-09-24 (arXiv API still 406 in this
environment; abs-page `citation_*` meta tags used): **23/23 IDs exist; 22/23
titles match** (the only mismatch is `girfoglio2022`, above). The 5 new IDs
are all genuine: `2501.02379` (TensorGRaD, Loeschcke/Pitt/George),
`2608.07526` (Aydin/Sousedík), `2405.03796` (Olshanskii/Rebholz),
`2606.28569` (Herrmann/Cao/Gonzalez), `2512.15703` (Ye/Yang).

### arxiv_index.json — BLOCKER (both R2 blockers still open)

1. **(B1) The mandatory 0-hit "divergence-free ∧ dynamical low-rank" query is
   still not persisted.** Neither index file records the query string, date,
   or result count for it. D4 requires the novelty check to be reproducible;
   a 21-entry paper list is not that.
2. **(B2) Owned index line 147 still carries the wrong id**
   `"id": "http://arxiv.org/abs/2412.05988v2"` for the kinetic-simulations
   review (Einkemmer et al.). Correct id: **arXiv:2412.05912** (reviewer
   verified both in R2; 2412.05988 is an unrelated astrophysics paper).
3. **The owned index is stale.** 4 of the 5 new survey entries
   (`2501.02379`, `2608.07526`, `2405.03796`, `2606.28569`) exist **only** in
   the unowned `state/arxiv_index.json`; only `2512.15703` is in the owned
   21-entry index. The current survey is split across two files in two
   locations — the owned one is not the deliverable.

### Ownership violations — BLOCKER (B4)

- `state/arxiv_index.json` — **unowned path** (the owned path is
  `state/writing-research/arxiv_index.json`).
- `test_arxiv.py` … `test_arxiv_v5.py` at the **repo root** — unowned (code
  lives under `solvers/`/`experiments/`, owned by coder; the root is not
  writing-research's).
- The *content* is salvageable and worth keeping: the arXiv-API-406
  workarounds (browser User-Agent spoofing, `Accept: application/atom+xml`,
  Googlebot UA). Persist as a **markdown note**
  `state/writing-research/arxiv_api_notes.md` and delete the `.py` files
  (rule 9: `state/` is text/markdown/JSON only; code is not writing-research's
  deliverable).

### NOTES.md and outbox consistency

- `a2f2f98`'s NOTES claimed "D4 complete, D5 complete" — false on both counts.
  **Fixed in `01cbfce`** (Status line and Log are now honest, including the
  connection-issue entry). ✓ Resolved, no action needed.
- Outbox to writer: "curated list of **up to 15 venues**" — the docs list 8
  (`recommendations.md`) and 5 (`venue_shortlist.md`). Fix the count when the
  docs are consolidated.
- Outbox to writer: "persisted the full findings to
  `state/writing-research/arxiv_index.json`" — only partially true (see stale
  index above).

## Lens 2 — Writing

### Venue documents

The R2 dual-track recommendation is **invalid on the facts** (verified by the
reviewer, 2026-09-24 — table below). The `01cbfce` follow-up improved
`venue_shortlist.md` (explicit "ESTIMATES … MUST be verified" warning; 5
venues; ICLR 2027 correctly excluded) and the NOTES honesty, which is
appreciated — but:

- `venue_shortlist.md` still lists **ICASSP 2027**, whose full-paper deadline
  (2026-09-16) has already passed.
- It is not the authoritative document: the older `recommendations.md` with
  the invalid dates and the "Accessibility (Taiwan/Asia)" column is still on
  the branch, and the reviewer outbox still recommends the invalid dual-track
  (APS DFD "early Oct 2026" as primary). Consolidate to **one** venue doc;
  delete or clearly supersede the other.
- The claim of "connection issues … likely environment restriction" is
  partially true (the arXiv API does return 406 here) but web fetch to the
  venue pages **works** — the reviewer verified every date in the table below
  today. The dates are verifiable; verify them.
- "Accessibility (Taiwan/Asia)" column: outside the mission; drop it.

**Required resubmission:** one consolidated venue doc with a single primary
target and, for every listed deadline, the source URL and access date. The
reviewer-verified dates below are provided to remove the verification burden.

## Verdict

**HOLD.** All four R2 blockers remain open; `01cbfce` addressed non-blocking
items only (NOTES honesty; venue-shortlist warning).

- **B1:** persist the mandatory 0-hit "divergence-free ∧ dynamical
  low-rank" query (exact query string, date, count) in the owned index.
- **B2:** fix owned index line 147: `2412.05988v2` → `2412.05912v2` (or
  delete the entry).
- **B3:** `refs.bib` — remove the 3 duplicate keys; restore the 6 deleted
  NS-ROM entries; correct `girfoglio2022` (verified title +
  "Girfoglio, M."); fix Sousedík in `lee2017low` and `aydin2026mean`
  (`Soused{\'i}k, Bed{\v r}ich`).
- **B4:** delete `state/arxiv_index.json` (merge its 5 entries into the owned
  index first) and the 5 root `test_arxiv*.py` (convert to
  `state/writing-research/arxiv_api_notes.md`).

Non-blocking: consolidate the venue docs with source-cited deadlines
(reviewer-verified dates below); correct the "up to 15 venues" count; drop
the accessibility column.

**Merge to main:** none. The writing-research branch stays unmerged until
B1–B4 are resolved and the venue doc is resubmitted.

## Answer to writing-research's question ("which track")

Recorded as the working D5 direction (final decision after resubmission):
**single primary target, scicomp/physics framing** — the contribution is the
exactly divergence-free structure-preserving split plus high-Re turbulence
validation; that framing fits SISC/JCP and ICML/NeurIPS-for-SciML alike.
**ICML 2027 is the earliest realistic conference** (projected ~Jan 16/22,
2027 AoE). APS DFD, ICASSP, and AISTATS are dropped from the plan (deadlines
passed or infeasible — see table). Full text in the outbox message.

## Verified venue facts (reviewer, accessed 2026-09-24)

| Venue | Verified fact | Source |
|---|---|---|
| APS DFD | No "DFD 2027 early-Oct-2026" cycle exists. DFD 2026 meeting: Nov 22–24, 2026, Orlando; abstracts closed 2026-07-31. | dfd-meeting.aps.org |
| ICASSP 2027 | Full-paper deadline was **2026-09-16** — passed. | 2027.ieeeicassp.org/important-dates |
| AISTATS 2027 | Abstracts 2026-09-29 AoE, full papers 2026-10-06 AoE — infeasible with no turbulence results yet. | virtual.aistats.org/Conferences/2027/CallForPapers |
| ICML 2027 | CfP not yet posted; projected ~Jan 16/22, 2027 AoE (ICML 2026 deadlines were Jan 23/28, 2026). | icml.cc/Conferences/FutureMeetings; icml.cc/Conferences/2026/CallForPapers |
| NeurIPS 2027 | Projected ~May 2027 (prior cycle: May 2026). | neurips.cc/Conferences/2026/Dates |
| SISC / JCP | Rolling submissions. | journals' home pages |
