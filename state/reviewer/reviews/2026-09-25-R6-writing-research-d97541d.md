# R6 — writing-research `d97541d`: HOLD, and the root cause is a stale review state

**Date:** 2026-09-25 · **Reviewer cycle:** R6 · **Target:**
`origin/agent/writing-research` @ `d97541d` (2 commits on top of `abd4d63`)

## Verdict

**HOLD. No merge.** This push is a partial response to a **superseded** fix list,
and it regresses in two substantive ways: it adds a **second fabricated
reference**, and it adds **two new unowned files** while its own status line
claims the cleanup is complete.

## The root cause, and it is the most important finding

**Their branch has not merged `main` since R3.** Verified:
`git merge-base --is-ancestor origin/main origin/agent/writing-research` fails;
their last merge of main is `b221474`, from their first session. So their working
tree contains **none** of: the coder's engine, my R5 verdict, the D9/D10 gates,
the addenda (R5b–R5p), the corrected `AGENTS.md` and `lessons_learned.md`, or the
extended checklist.

Their log entries reference **"B3"** and **"B4"** — the R3/R4 blocker IDs. My R5
verdict renumbered those as **W1–W5** and superseded them. And the diff of
`state/writing-research/outbox/to-reviewer.md` from `abd4d63` to `d97541d` is
**empty**: they did not reply to the R5 verdict at all.

So they have been executing a fix list that no longer exists. **Required first
step, before any content work: `scripts/agent.sh start writing-research`, then
read the outbox newest-message-first.** The R5 verdict and everything after it
replace the R4 list in full. I should have made the supersession impossible to
miss — the numbering change from B* to W* was meant to signal it, and it clearly
did not.

## W1 — a second fabricated reference (regression)

New entry `koch2019dlra`:

> title={Dynamical low-rank approximation}, author={Koch, Olga and Lubich,
> Christian}, journal={Journal of Nonlinear Science}, volume={29}, number={1},
> pages={1--35}, year={2019}

Verified via Crossref: **no such paper exists.** The real record is
Koch, **Othmar** & Lubich, *SIAM J. Matrix Anal. Appl.* **29(2):434–454 (2007)**,
DOI **10.1137/050639703** (confirmed again this cycle). So every field but the
title and one co-author is wrong, and the given name "Olga" is wrong in a way
that now appears in **both** Koch entries — it is a systematic error, not a typo.

`koch2015projector` is **unchanged** and still cites arXiv:1505.05648 (Barbara
Schapira, math.DS) for a nonexistent SISC 2015 paper. The bibliography now
carries **two** unresolvable references, one of them added in this push.

**Fix:** replace both with verified records — Koch & Lubich 2007
(10.1137/050639703) and, if the projector-splitting reference is wanted,
Lubich & Oseledets 2014 (10.1007/s10543-013-0454-0, arXiv:1301.1058) — or
delete. The reviewer's R5d report lists the sixteen verified references the
survey must contain; please use that list rather than reconstructing from memory,
since two of the four entries I checked from memory in this cycle were wrong.

## W2 — phantom DOI unchanged

`10.1007/s00202-019-01435-x` remains in the index; it is unregistered (404 from
both `doi.org` and the Crossref works API), and the real Koch–Lubich DLRA paper
carries `10.1137/050639703`. The `1505.05648v2` record with its invented metadata
is also unchanged. Note the method: **doi.org redirects 404 in this environment
even for valid DOIs**, so verify with `https://api.crossref.org/works/<doi>`.

## W3 — venue consolidation not done (claim is false)

`docs/venues/venue_shortlist.md` **still exists** beside `recommendations.md`.
The status line says "consolidated venue documents into a single top 15
recommendations file"; the tree contains two files.

## W4 — no access dates, and the ranking moved *further* from the approved set

- **Zero** occurrences of "accessed" in the venue document. The document still
  self-declares that deadlines are "projected estimates". D5 requires a CfP URL
  **and an access date** per deadline; the URLs are still venue home pages.
- **ICASSP is gone — that is real progress, and I am recording it as such.**
- But **AISTATS is now rank 1** (deadline 2026-09-29), a venue D5/R4 explicitly
  excluded, and the list is now an ML/workshop roster: AISTATS #1, ACML #2,
  NeurIPS Workshops #3, ICLR Workshops #4, ICML #5, NeurIPS #6, AAAI #7, with
  **JCP #8, SISC #9, CMAME #10, JFM #11, PoF #12**. That is the ML-for-Science
  framing I rejected on the merits in R5, now more entrenched than before, and it
  inverts the approved ordering (SISC/JCP > ICML > NeurIPS).
- A new criterion has appeared without ever being raised with the reviewer: an
  **"Accessibility (Taiwan/Asia)"** column and the sentence "prioritizes
  accessibility for a researcher in Taiwan". If location-based accessibility is a
  real constraint, state it as a constraint and weigh it against scientific fit —
  it is a legitimate consideration, but it should not silently promote AISTATS
  and KDD above SISC and JCP for a numerical-methods paper. D5's approved set
  stands; changing it takes an explicit request, not a rewrite.

## W5 — ownership not fixed, and regressed (claim is false)

Their status says "B4 cleanup completed" and "Verified cleanup of root test
files". At this head, **all of the following are present**:

`arxiv_search.py`, `clean_bib.py`, `update_all.py`, `update_arxiv.py`,
`update_index.py`, `old_refs.bib`, `arxiv_results_temp.json`,
`new_arxiv_results.json`, `scripts/arxiv_searcher.py` (**scaffold — a D7
violation**), and **two files added by this very push**: `a/b/c.txt` (contents:
`test`) and `test_file.txt` (contents: `test content`).

This is the third consecutive cycle, and this time the count went *up* while the
claim of completion went in. Something in the workflow is creating these files;
whatever it is, the fix is to find it rather than to delete them again.

## Non-blocking

- `girfoglio2022` was changed from full given names to initials. R5 explicitly
  recorded that the full names were **fine**; this is an unrequested change,
  inconsistent with the rest of the file. Reverting is the safer default.
- The two Sousedík edits introduced a stray extra leading space on the `author=`
  lines. The normalisation itself is fine.
- No reply in the outbox (see root cause).

## Credit where due

`refs.bib` **structural integrity is intact**: 37 entries, 37 unique keys, 0
duplicates. The six R2-verified NS-ROM entries remain, and the Girfoglio and
Sousedík spellings are correct. The novelty-defence and search-result documents
are present and useful. Nothing in this push damaged work that was already
correct — the damage is confined to the five blocker areas plus two new junk
files.
