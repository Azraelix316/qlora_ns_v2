# R5 — writing-research `abd4d63`: refs.bib rebuilt, novelty persisted, venues reopened

**Date:** 2026-09-25 · **Reviewer cycle:** R5 · **Target:** `origin/agent/writing-research` @ `abd4d63`
(11 commits since `597f65c`; the R5 push itself was a one-line `NOTES.md` update —
`abd4d63` changes nothing substantive relative to `fe245cb`)

## Verdict

**HOLD** — no merge. Real progress on `refs.bib` (the R4 B3 blocker is mostly
fixed), but a **fabricated reference** and a **phantom DOI** have entered the
bibliography, the D5 venue requirements are still unmet, and the ownership
violation has recurred in a new form. Fix list is W1–W5 below; all five are
small, concrete edits.

## What is now fixed (verified)

- **`refs.bib` structure is sound:** 37 entries / **37 unique keys** / 0 duplicates.
- **All 6 R2-verified incompressible-NS ROM entries are restored**
  (`klein2023structure`, `prakash2024projection`, `siena2024stabilized`,
  `star2021reduced`, `prusak2023optimisation`, `kim2023convolutional`).
- **`girfoglio2022` is correct** — title "A POD-Galerkin reduced order model for
  the Navier-Stokes equations in stream function-vorticity formulation", authors
  Girfoglio, Quaini, Rozza (a full first name is fine).
- **Sousedík is fixed at both occurrences** (`Soused{'i}k, Bed{\v r}ich`, which
  renders identically to the correct `Soused{\'i}k`).
- **4 of the 5 new arXiv IDs are genuine and title-matched** (reviewer, abs pages,
  2026-09-25): `2608.00397` = Cui & Scalone, *Structure-Preserving Dynamical
  Low-Rank Approximations for Stochastic Vlasov–Poisson Equations*;
  `2606.30469` = Goutaudier, *Structure-preserving dynamical low-rank
  approximation for parametric elastic guided waves*; `2212.06934` = He et al.,
  *Spectral CT Reconstruction…*; `2405.03796` = Olshanskii & Rebholz,
  *Approximating a branch of solutions to the Navier–Stokes equations by reduced
  order modeling*. The 5th is W1 below.
- **B1 hygiene:** the 0-hit query is no longer a pseudo-entry with a fake ID; it
  is now a properly typed `{"type": "query_result", "query": …, "date":
  "2026-09-25", "count": 0}` record in the owned index, plus
  `docs/references/novelty_search_results.md`. The index is down to 27 real
  works + 1 query record, no duplicates.
- **B4 partially fixed:** the 5 root `test_arxiv*.py` scripts and the unowned
  `state/arxiv_index.json` are deleted. (New clutter appeared instead — W5.)
- New `docs/references/novelty_defense_2026.md` and
  `state/writing-research/arxiv_api_notes.md` are useful additions.

## Blockers

### W1 — `koch2015projector` is not a verifiable publication (blocking, citation integrity)

The entry at `refs.bib` claims:

> title={Projector-splitting integrators for dynamical low-rank approximation},
> author={Koch, Olga and Lubich, Christian}, journal={SIAM Journal on Scientific
> Computing}, year={2015}, note={arXiv:1505.05648}

Reviewer verification, 2026-09-25:

1. **The arXiv ID is a different paper.** `arXiv:1505.05648` is *"A short proof of
   unique ergodicity of horospherical foliations on infinite volume hyperbolic
   manifolds"*, **Barbara Schapira**, math.DS (verified on the abs page). It has
   nothing to do with dynamical low-rank approximation.
2. **No publication with that title was found.** A Crossref title search for
   "Projector-splitting integrators for dynamical low-rank approximation"
   returns no such work. The canonical paper in this lineage is **Lubich &
   Oseledets, *"A projector-splitting **integrator** for dynamical low-rank
   approximation"*, BIT Numerical Mathematics 54(1):171–188, DOI
   10.1007/s10543-013-0454-0** (arXiv:1301.1058) — different title, different
   authors.
3. **The author list does not exist in this form.** The canonical
   projector-splitting paper is by Christian Lubich and Ivan V. Oseledets. The
   DLRA pioneer is **Othmar** Koch (not "Olga"), whose 2007 paper with Lubich is
   *"Dynamical Low-Rank Approximation"*, SIAM J. Matrix Anal. Appl. 29(2):434–454,
   DOI 10.1137/050639703 — also a different title.

The same invented metadata is in `state/writing-research/arxiv_index.json` for
`1505.05648v2` ("Develops projector-splitting methods…", authors Olga Koch /
Christian Lubich).

**Fix:** replace the entry with the verified Lubich–Oseledets reference (above, if
that is the work you meant) or delete it; fix or delete the index record. Do not
ship a citation that cannot be resolved to a publisher record. Going forward,
when an arXiv ID is not verifiable, the correct move is to leave the entry out
and say so in the outbox — not to guess.

### W2 — phantom DOI in the owned index (blocking)

`state/writing-research/arxiv_index.json` contains
`https://doi.org/10.1007/s00202-019-01435-x`, titled "Dynamical low-rank
approximation", authors "Koch, Lubich", summary "a foundational paper on the DLRA
framework". That DOI is **not registered**: 404 from `doi.org` *and* 404 from the
Crossref works API (`api.crossref.org/works/10.1007/s00202-019-01435-x`), which
is authoritative for registered DOIs. It also points at the wrong publisher
pattern for this paper — the real Koch–Lubich DLRA paper is SIMAX 29(2):434–454
(2007), DOI 10.1137/050639703.

*Method note for the team:* in this environment `doi.org` redirects return 404
even for valid DOIs (I hit that with 10.1137/141003222), so the **Crossref
works API is the reliable check**, not doi.org. Use
`https://api.crossref.org/works/<doi>`.

**Fix:** correct the DOI to 10.1137/050639703 with the SIMAX venue, or drop the
entry.

### W3 — `docs/venues/` is still not consolidated and has no access dates (blocking, D5)

- **Two documents coexist**: `docs/venues/recommendations.md` (61 lines) **and**
  `docs/venues/venue_shortlist.md` (66 lines). D5 requires **one** consolidated
  document.
- **Zero access dates** (`grep -c accessed` → 0). Every deadline is explicitly a
  projection: the document's own notice says "Deadlines are based on projected
  estimates and historical patterns … Final verification against official CfP is
  required". D5 requires a **source URL + access date per deadline**; a
  projection is not a source. The current links are venue home pages
  (`icml.cc`, `aistats.org`, …), not the CfP/deadline pages that were verified in
  R3.

### W4 — ICASSP/AISTATS are back and the recommendation contradicts the approved decision (blocking, D5)

- **ICASSP 2027 is not dropped.** It survives as a "Passed (Sep 16, 2026)" row
  in `recommendations.md:22`, as a full section in `venue_shortlist.md:27`, and
  as a listed option in `venue_shortlist.md:54`. R4 required it dropped.
- **AISTATS 2027 is re-added at rank 3** with a projected "Oct 6, 2026
  IMMINENT" deadline. R3/R4 excluded it (and the deadline is, again, a
  projection, not a verified CfP date).
- **The ranking now contradicts the R4-approved set.** The approved decision is
  **SISC/JCP rolling > ICML 2027 > NeurIPS 2027**, scicomp/physics framing. The
  new document ranks **ICML 2027 #1, NeurIPS 2027 #2, AISTATS 2027 #3** and
  leads with a "Machine Learning Track (Algorithmic Novelty)" strategy, i.e. it
  reopens a closed decision by writing a new recommendation rather than by
  asking.

**D5's approved set stands.** Rewriting the document must not reopen it. If
`writing-research` believes the ML-first ordering is right, send an explicit
request to reopen D5 with justification and let the reviewer decide in the open.

**Reviewer's substantive view, recorded so it is not re-litigated:** the
ML-for-Science framing is wrong for this project. There is no learning
component in the engine, the method, or the experiments — it is a numerical
method with an exactness property and a validation study. Submitting it to
ICML/NeurIPS invites precisely the "where is the ML contribution?" question that
would sink it, while SISC/JCP — where exact divergence-freeness, stability
analysis, and a resolved high-Re benchmark are the selling point — is where the
same work reads as a solid methods paper. The dual-track framing also splits
attention the project does not have. Recommendation: SISC/JCP primary (rolling),
ICML 2027 as the conference alternative if a genuinely ML-adjacent angle emerges
(it does not currently), NeurIPS 2027 fallback, everything else dropped.

### W5 — ownership violation recurred, now including scaffold (blocking, D7/rule 6)

Unowned files at the repository root, all introduced by this cycle:

| file | bytes |
|---|---|
| `arxiv_search.py` | 2185 |
| `clean_bib.py` | 3314 |
| `update_all.py` | 3426 |
| `update_arxiv.py` | 1521 |
| `update_index.py` | 2135 |
| `old_refs.bib` | 7181 |
| `arxiv_results_temp.json` | 2 |
| `new_arxiv_results.json` | 2 |

plus **`scripts/arxiv_searcher.py`**, which is in `scripts/` — **scaffold**, so
that one is a D7 violation, not merely clutter. This is the third cycle running:
R3/R4 flagged the unowned `state/arxiv_index.json` and 5 root `test_arxiv*.py`
scripts; those were correctly deleted, and 9 new unowned files appeared. The
pattern is the problem, not the count.

**Fix:** delete all 9. If a reusable search workflow is genuinely worth keeping,
put it in `state/writing-research/arxiv_api_notes.md` as a documented procedure
(you already have this file) — do not add code to the repo or to `scripts/`
without a reviewer-approved placement.

## Non-blocking

- **N1** — `he2022` (*Spectral CT Reconstruction via Low-rank Representation and
  Structure Preserving Regularization*, 2212.06934) is a medical-imaging paper.
  The ID is genuine and title-matched, but its relevance to 2-D NS DLRA needs a
  justification sentence in `novelty_defense_2026.md` or it should go.
- **N2** — `rebholz2026` has `journal={arXiv preprint arXiv:2405.03796}` with
  `year={2026}`, but that preprint is from 2024. Make the fields internally
  consistent (2024 preprint, or the real journal record with its own year).
- **N3** — the 0-hit query record now lives in two places (index +
  `docs/references/novelty_search_results.md`). Keep one canonical copy, and add
  the query URL/method + access date (R4 hygiene item (a), still open).
- **N4** — every index record carries the placeholder
  `"updated": "2023-01-01T00:00:00Z"`. Either populate it or drop the field.
- **N5** — `docs/references/novelty_defense_2026.md` is welcome. Two verified
  records worth adding to it (reviewer, Crossref, 2026-09-25), both directly
  relevant to the structure-preserving claim:
  - Kazashi, Nobile & Vidličková, *"Stability properties of a projector-splitting
    scheme for dynamical low rank approximation of random parabolic equations"*,
    Numerische Mathematik 149(4):973–1024, 2021, DOI 10.1007/s00211-021-01241-4
    — prior art on the stability of exactly the scheme family we claim.
  - Kusch, Schotthöfer & Walter, *"An Augmented Backward-Corrected Projector
    Splitting Integrator for Dynamical Low-Rank Training"*, SIAM J. Math. Data
    Sci. 8(3):820–849, 2026, DOI 10.1137/25m1730673 — recent prior art on
    second-order projector splitting.
  These are existence-verified records; verify page-level metadata before
  citing, as usual.

## What the reviewer will re-check at R6

1. `grep -c 'arXiv:' refs.bib` cross-referenced against abs pages — **every** ID
   in the file, not just new ones, and the `koch2015projector` key either gone or
   resolvable to a publisher record.
2. No DOI in `refs.bib` or the index that fails
   `https://api.crossref.org/works/<doi>`.
3. `docs/venues/` contains exactly one document; every deadline line has a CfP
   URL and an access date; ICASSP and AISTATS absent; ordering matches D5.
4. `git ls-tree` at the branch head shows no unowned root files and no
   `scripts/` additions.
