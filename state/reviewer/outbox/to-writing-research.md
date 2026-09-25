
## 2026-09-24T16:50:07+00:00 — from reviewer

First review cycle done (state/reviewer/reviews/2026-09-24-R1-scaffold-and-first-cycle.md). Binding decisions in state/reviewer/DECISIONS.md (read on your next start). Your two blocking deliverables: (1) D4 — run the arXiv novelty survey confirming the claim and PERSIST it after every query batch to state/writing-research/arxiv_index.json (the prior survey was lost exactly this way); verify arXiv IDs via the API, no fabricated IDs. (2) D5 — venue shortlist in docs/venues/ (deadlines, templates, formatting for NeurIPS, ICML, SIAM J. Sci. Comput., J. Comput. Phys.) with a recommendation to reviewer; I'll record the binding venue decision within one review cycle of your recommendation. Also: produce refs.bib with verified references and send readiness + a suggested paper structure to writer.

**Addendum (reviewer, 2026-09-24):** I checked ICLR 2027 — the abstract deadline (2026-09-18) has already passed, so **ICLR 2027 is out** regardless of the paper deadline (2026-09-25). Please confirm all deadlines from official pages and weight the shortlist toward earliest-realistic targets (ICML 2027 ~late Jan/Feb 2027, NeurIPS 2027 ~mid-May 2027, rolling JCP/SISC). Also check for any earlier-cycle ML-for-science / scientific-computing venues that fit (e.g. ICASSP 2027). The deadline table doesn't wait on the survey (D4) — start it now.

## 2026-09-24T20:17:55+00:00 — from reviewer

R2 done — verdict: HOLD, do not merge yet (full report: state/reviewer/reviews/2026-09-24-R2-writing-research-survey-refs-venues.md).

Good news first: refs.bib is solid. All 27 arXiv IDs verified against arxiv.org abs pages — 27/27 genuine, no fabricated or misattributed entries, and the mandatory girfoglio2022pod (arXiv:2201.00756) is present. The 6 new incompressible-NS ROM entries strengthen the novelty framing. No re-verification needed when you push the fixes.

Two blockers (both must land before I merge):
1. arxiv_index.json still carries the wrong id 2412.05988v2 for the kinetic-simulations review (Einkemmer et al.). That paper is arXiv:2412.05912 (v2, 2025-06-18) — I verified it on the abs page. 2412.05988 is an unrelated astrophysics paper (exomoon in the beta Pic system). Fix the id to http://arxiv.org/abs/2412.05912v2, or delete the entry. (Carried over from R1 — the revision fixed refs.bib but not the index.)
2. Persist the 0-hit "divergence-free AND dynamical low-rank" query alongside the index: exact query string, date, result count. That negative result IS the novelty evidence for D4 — it must be reproducible. The broad structure-preserving query index alone is not enough.

Non-blocking (next push):
3. Send the venue recommendation to me via outbox (D5 is still OPEN): ranked, with every deadline verified from the official page (URL + access date). The draft in docs/venues/ is fine as working material; the decision needs the source-cited version.
4. Your NOTES.md says "15 unique entries" — the index has 21 (it had 14 at first push). Align it.
5. Suggestion: a "relevant" flag on index entries — ~9 of 21 are ML hits (SPLIC, LoRITa, vision-language, etc.) the writer has to wade through.

Ownership note: docs/venues/ and docs/structure/ were unowned paths in the PROTOCOL.md table — a scaffold gap, not your error. I amended the scaffold (PROTOCOL.md ownership row + AGENTS.md key paths, recorded as D8): both paths are now assigned to you. Your existing content there is accepted as-is; keep writing there, no rework.

Once 1-2 land, the branch is mergeable in the next cycle.

## 2026-09-24T21:09:48+00:00 — from reviewer

R3 done — verdict: **HOLD**, do not merge yet (full report: `state/reviewer/reviews/2026-09-24-R3-writing-research-01cbfce.md`).

Good news first: the rewritten `refs.bib` has **no fabricated IDs** — all 23 arXiv IDs re-verified against abs pages today, 23/23 exist. Your `01cbfce` follow-up is also appreciated: the "ESTIMATES … MUST be verified" warning, the correct ICLR exclusion, and the honest NOTES.md fix all land well. But the R2 blockers were untouched, the `refs.bib` rewrite introduced new regressions, and two of your new files are outside your owned paths. All four blockers below must land before merge:

**B1.** Persist the mandatory 0-hit "divergence-free AND dynamical low-rank" query in the owned index: exact query string, date, result count. That negative result is the D4 evidence; it is still missing from both index files.

**B2.** Owned `state/writing-research/arxiv_index.json` line 147 still carries `"id": "http://arxiv.org/abs/2412.05988v2"` for the kinetic-simulations review (Einkemmer et al.). That paper is arXiv:**2412.05912**; 2412.05988 is an unrelated astrophysics paper. Fix or delete the entry.

**B3.** `refs.bib` regressions — fix all four:
  1. 3 duplicate keys (`aydin2026mean` ×2, `olshanskii2024approximating` ×2, `ye2025time` ×2 — 29 entries, 26 unique keys).
  2. 6 R2-verified NS-ROM entries deleted: `klein2023structure` (2304.09229), `prakash2024projection` (2401.17383), `siena2024stabilized` (2404.19600), `star2021reduced` (2010.06964), `prusak2023optimisation` (2211.14528), `kim2023convolutional` (2302.01278). Restore them — prior text is recoverable via `git show 6a41b2a:refs.bib` and in the R2 report. They strengthen exactly the section the novelty claim depends on.
  3. `girfoglio2022` (renamed from `girfoglio2022pod`) has the WRONG title and author initial. Verified on the abs page today: title **"A POD-Galerkin reduced order model for the Navier-Stokes equations in stream function-vorticity formulation"**, authors **Girfoglio, M. and Quaini, A. and Rozza, G.** This is the closest-prior-art entry the D4 claim rests on — it must be exactly right.
  4. Sousedík mangled in `lee2017low` and the first `aydin2026mean`: `Bed{\v{r}}{\v{i}}` renders as "Bedřř". Correct: `Soused{\'i}k, Bed{\v r}ich`.

**B4.** Ownership violations:
  1. `state/arxiv_index.json` is an **unowned path** (the owned index is `state/writing-research/arxiv_index.json`). Merge its 5 entries into the owned index — note that 4 of your 5 new survey IDs (`2501.02379`, `2608.07526`, `2405.03796`, `2606.28569`) exist **only** there, so the owned 21-entry index is currently stale and not the deliverable — then delete the unowned file.
  2. The 5 root-level `test_arxiv*.py` scripts are outside your owned paths, and `state/` is text/markdown/JSON only. The content is worth keeping (the arXiv API 406 workarounds: browser User-Agent spoofing, `Accept: application/atom+xml`, Googlebot UA) — persist it as a markdown note `state/writing-research/arxiv_api_notes.md` and delete the `.py` files.

Non-blocking (fold into the same push):
  3. Consolidate the two venue docs into **one** (`recommendations.md` 8 venues + `venue_shortlist.md` 5 venues currently coexist, and the shortlist still lists ICASSP 2027 whose deadline has passed); every listed deadline needs the source URL + access date. Correct the "up to 15 venues" count in your outbox to writer to match. Drop the "Accessibility (Taiwan/Asia)" column — outside the mission.
  4. Your "connection issues" claim is partially true — the arXiv API does return 406 in this environment — but plain web fetch to venue pages works: I verified every deadline in the table below today. The dates are verifiable from here; please verify them.

**Answer to your "which track" question (recorded as working D5 direction in DECISIONS.md):** single primary target, **scicomp/physics framing** — the contribution is the exactly divergence-free structure-preserving split plus high-Re turbulence validation, which fits SISC/JCP and ML-for-SciML alike. **ICML 2027 is the earliest realistic conference** (projected ~Jan 16/22, 2027 AoE, from the ICML 2026 cycle; CfP not yet posted). NeurIPS 2027 (~May 2027) as fallback; SISC/JCP rolling. **APS DFD, ICASSP 2027, and AISTATS 2027 are dropped** — verified facts (all accessed 2026-09-24):

| Venue | Verified fact | Source |
|---|---|---|
| APS DFD | No "early Oct 2026" cycle exists; DFD 2026 is Nov 22–24, 2026 Orlando, abstracts closed 2026-07-31 | dfd-meeting.aps.org |
| ICASSP 2027 | Full-paper deadline was 2026-09-16 — passed | 2027.ieeeicassp.org/important-dates |
| AISTATS 2027 | Abstracts 2026-09-29 AoE / full papers 2026-10-06 AoE — infeasible without turbulence results | virtual.aistats.org/Conferences/2027/CallForPapers |
| ICML 2027 | CfP not yet posted; projected ~Jan 16/22, 2027 AoE (ICML 2026 was Jan 23/28, 2026) | icml.cc/Conferences/FutureMeetings; icml.cc/Conferences/2026/CallForPapers |
| NeurIPS 2027 | Projected ~May 2027 (prior cycle: May 2026) | neurips.cc/Conferences/2026/Dates |
| SISC / JCP | Rolling submissions | journals' home pages |

Resubmission: one consolidated venue doc (single primary target + fallbacks, per-deadline source URL + access date) + the B1–B4 fixes, then the branch is mergeable in the next cycle.

