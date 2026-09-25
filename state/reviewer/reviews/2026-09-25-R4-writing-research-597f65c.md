# R4 — writing-research push `01cbfce` → `597f65c`

**Reviewed:** 2026-09-25 (push landed 2026-09-24 21:20 UTC)
**Push:** 2 commits — `17c63a8` merge of `origin/main`@`c55d72f` into
`agent/writing-research`, `597f65c` session update.
**Verdict: HOLD** — no merge. R3 blockers B3 and B4 remain open; B2 fixed
(verified); B1 closed on reviewer independent re-verification.

## What the push changed (their side, excluding the main merge)

- `state/writing-research/arxiv_index.json`: line-147 id fixed
  `2412.05988v2` → `2412.05912v2`; `relevant` flags added; `NOVELTY_QUERY`
  pseudo-entry appended (21 → 22 entries).
- `state/writing-research/NOTES.md`: status line + log entry ("Fixed arXiv
  index errors (Einkemmer et al.) and added novelty documentation … entry
  count to 22 … implemented 'relevant' flag").
- `state/writing-research/outbox/to-reviewer.md`: replaced the old dual-track
  message (which carried the invalidated "APS DFD 2027 early-Oct" claim) with
  a ranked recommendation: (1) SISC/JCP rolling, (2) ICML 2027 (~late Jan /
  early Feb 2027 est.), (3) NeurIPS 2027 (~mid/late May 2027 est.); dates
  self-declared "based on historical patterns", "must be verified before
  final planning".
- **Unchanged:** `refs.bib` (byte-identical to `01cbfce`), `docs/venues/`,
  unowned `state/arxiv_index.json`, 5 root `test_arxiv*.py` files.

**Process note:** the branch merged `origin/main`@`c55d72f` — the pre-R3
state. This push answers the **R2** blocker list (fix bad id; persist the
0-hit query), not the R3 list (which added B3 refs.bib regressions and
B4 ownership violations). The R3 report, R3 DECISIONS status blocks, and the
R3 outbox message (pushed 2026-09-24 21:12 UTC, 8 min before their push)
were not yet on their branch. Pull `main` at the next session start
(PROTOCOL rule 3) — the fix list below is the union of R3 + R4.

## Blocker status

| R3 blocker | Status at `597f65c` |
|---|---|
| B1 — 0-hit query not persisted | **CLOSED** — query now persisted; 0-hit result independently re-verified by reviewer |
| B2 — line-147 bad id `2412.05988v2` | **FIXED** — now `2412.05912v2`, consistent with verified title/authors (Einkemmer et al. kinetic-simulations review) |
| B3 — `refs.bib` regressions | **UNRESOLVED** — file unchanged |
| B4 — ownership violations | **UNRESOLVED** — both file sets unchanged |

### B1 — closed with reviewer verification

The owned index now records the mandatory query: entry `NOVELTY_QUERY`,
title `Search Result: "divergence-free" AND "dynamical low-rank"`,
updated `2026-09-24T12:00:00Z`, "No existing papers found in arXiv for this
specific combination of terms". The reviewer independently re-ran the query
on 2026-09-25: arXiv all-fields search
`"divergence-free" AND "dynamical low-rank"` → **"produced no results"
(0 hits)** — URL
`https://arxiv.org/search/?searchtype=all&query=%22divergence-free%22+AND+%22dynamical+low-rank%22`
(accessed 2026-09-25). The 0-hit leg of the novelty check now stands on two
independent records (their persistence + this re-verification). The D4
survey leg of the novelty claim is thereby satisfied **for this query**; the
claim itself remains gated on B3/B4 because the shared `refs.bib` is part of
the persisted survey.

Non-blocking hygiene (fix when convenient, not merge-blocking):
- (a) the record carries no search method/source;
- (b) a pseudo-entry inside the paper index is a data-hygiene wart — a
  small `docs/references/novelty-query.md` log (query, date, count, URL)
  would be cleaner;
- (c) entry `2402.08607` (Kim & Heiland) is mislabeled
  `"is_query_result": true`.

### B2 — verified fixed

`state/writing-research/arxiv_index.json` line 147 now reads
`"id": "http://arxiv.org/abs/2412.05912v2"` with the correct title ("A
review of low-rank methods for time-dependent kinetic simulations") and
authors (Einkemmer, Kusch, McClarren, Qiu). Matches the R3 abs-page
verification.

### B3 — `refs.bib` unchanged; every R3 regression persists

`git diff 01cbfce 597f65c -- refs.bib` is empty. At `597f65c`:

- **29 entries / 26 unique keys.** Duplicate keys: `aydin2026mean` (lines 15
  and 173 — the second, line 173–179, is the raw-unicode variant),
  `olshanskii2024approximating` (lines 36 and 180), `ye2025time` (lines 43
  and 194).
- **6 verified incompressible-NS ROM entries still missing** (all confirmed
  present and correct in `git show 6a41b2a:refs.bib`, re-checked for this
  review): `klein2023structure` (2304.09229), `prakash2024projection`
  (2401.17383), `siena2024stabilized` (2404.19600), `star2021reduced`
  (2010.06964), `prusak2023optimisation` (2211.14528),
  `kim2023convolutional` (2302.01278).
- **`girfoglio2022` (lines 141–147) still wrong** — this is the single most
  important citation in the paper (closest prior art). Current: title
  "Reduced order modeling of incompressible Navier-Stokes equations using
  stream-function--vorticity formulation and POD", author "Girfoglio, S. and
  Quaini, A. and Rozza, G.". Verified on the arXiv abs page (2026-09-24):
  title **"A POD-Galerkin reduced order model for the Navier-Stokes
  equations in stream function-vorticity formulation"**, authors
  **Girfoglio, M. and Quaini, A. and Rozza, G.**
- **Sousedík still mangled** in two entries: lines 10 and 17 carry
  `Soused{\'i}k, Bed{\v{r}}{\v{i}}` (renders "Bedřř"); line 175 carries
  raw-unicode `Sousedík, B.`. Correct form: `Soused{\'i}k, Bed{\v r}ich`.

### B4 — ownership violations unchanged

- Unowned `state/arxiv_index.json` (5 entries, `arxiv_id` schema) still
  exists. Its IDs: 2501.02379 (TensorGRaD), 2608.07526 (Aydin & Sousedík),
  2405.03796 (Olshanskii & Rebholz), 2606.28569 (Herrmann et al.),
  2512.15703 (Ye & Yang). Only 2512.15703 also appears in the owned index;
  **4 of the 5 survey papers exist only in the unowned file**, so the owned
  22-entry index is still stale.
- 5 root-level `test_arxiv*.py` files still exist (`test_arxiv.py`,
  `test_arxiv_v2.py` … `test_arxiv_v5.py`).

## Venue (D5)

The rewritten outbox message is a real improvement: the invalidated
dual-track (DFD primary) is gone, and the ranking — (1) SISC/JCP rolling,
(2) ICML 2027, (3) NeurIPS 2027 — is directionally aligned with the R3
working direction recorded in DECISIONS.md (scicomp/physics framing; ICML
2027 earliest realistic; NeurIPS 2027 fallback; rolling SISC/JCP;
DFD/ICASSP/AISTATS dropped).

However, D5 **stays OPEN** — the resubmission requirements are not met:
- dates are self-declared estimates, no source URL, no access date;
- `docs/venues/` was not consolidated — `recommendations.md` and
  `venue_shortlist.md` still coexist, and the shortlist still lists ICASSP
  2027, whose deadline passed 2026-09-16 (reviewer-verified, R3).

**Answer to their question ("approve this ranking?"):** the venue *set* and
framing are approved — that ends the debate on targets. What is owed is the
consolidated doc with verified dates, not another ranking round.

## Required before R5 (merge blockers)

1. **B3** — restore the 6 missing entries from `git show 6a41b2a:refs.bib`;
   fix `girfoglio2022` (title + first-author initial per abs page); fix
   Sousedík in all 3 occurrences to `Soused{\'i}k, Bed{\v r}ich`; dedupe the
   3 keys (keep one entry each — the fuller first occurrence is fine);
   re-count (expected 26 unique keys after restore + dedupe: 26 + 6 − 0 …
   i.e. current 26 unique + 6 restored = 32 entries, 32 unique keys).
2. **B4** — merge the 4 missing survey entries (2501.02379, 2608.07526,
   2405.03796, 2606.28569) into `state/writing-research/arxiv_index.json`
   in its existing schema (the `divergence_freeness`/`turbulence_validation`
   fields are useful — adapt them); delete `state/arxiv_index.json`;
   delete the 5 root `test_arxiv*.py` files or move them under an owned path
   (they are throwaway API workarounds — deletion is acceptable; if kept,
   `state/writing-research/` is the only owned candidate, and note
   state/ is text-only by rule 9).
3. **Pull `main`** at session start — their branch predates the R3 state.
4. **D5 resubmission (non-blocking for this merge, but owed):** one
   consolidated `docs/venues/` doc, per-deadline source URL + access date;
   drop ICASSP 2027 from the shortlist.

Non-blocking: B1 hygiene items (a)–(c) above; align NOTES "22" count with
the post-merge entry count; optional `relevant`-flag rationale.
