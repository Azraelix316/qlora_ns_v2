# R23 — writing-research `e9a1005`: MERGED. Four real new references, one regression, and the list unchanged for the fourth push running

**Cycle:** R23 · **Reviewed:** `e9a1005` (12:05:46) · **Merge safety:** passes (0 deletions,
0 outside owned paths, 0 conflicts). Merged — the content is additive and the regression is
small and already recorded elsewhere.

## What the push did

Three files, +103/−4: four new `refs.bib` entries, `NOTES.md`, and 76 lines added to
`arxiv_index.json` (now 40 records).

**All four arXiv IDs are real — I verified them rather than asking, because asking has not
worked for six cycles.** Titles and author lists match in every case:

| entry | arXiv | status |
|---|---|---|
| `einkemmer2025asymptotic` | 2502.08951 | OK — Einkemmer, Hu, Zhang, 2025-02-13 |
| `moarref2013model` | 1302.1594 | OK — Moarref, Sharma, Tropp, McKeon |
| `koellermeier2024macro` | 2302.01391 | OK — Koellermeier, Krah, Kusch |
| `einkemmer2025interpolatory` | 2411.15990 | OK — Dektor, Einkemmer |

Credit: the survey is genuinely being extended, and every ID in this push checks out.

## Two defects, both new

**R1 — a verified DOI was lost.** `koellermeier2024` (which carried DOI
`10.1007/s10444-024-10175-y`, verified in R20) was **replaced** by `koellermeier2024macro`,
which cites the arXiv preprint and has **no DOI**. The arXiv metadata for 2302.01391
carries exactly that DOI. So an entry went from verified-and-DOI-bearing to
preprint-only. Nothing is permanently lost — the DOI is in my R20 report and in the
writer's bibliography — but the file got worse on this line.

**R2 — an author-order error, the same class as R18's.** `einkemmer2025interpolatory` lists
`Einkemmer, Lukas and Dektor`; arXiv gives **Alec Dektor, Lukas Einkemmer**. Reversed.
This is the same failure mode as the two wrong-given-name entries in R18, in a brand-new
entry, and it is the third time an author field has been wrong on a real paper.

**Two of the four entries have DOIs available and omit them:** `moarref2013model` →
**10.1017/jfm.2013.457** (*J. Fluid Mech.* 734:275–316, 2013), and `koellermeier2024macro`
→ 10.1007/s10444-024-10175-y.

## The list, for the fourth consecutive push

Verified individually on their branch just now: **A1** Girfoglio `compflu.` (404) — still
there. **A2** `arXiv:1505.05648` attached to a projector-splitting title — still there.
**A3** "Olga Koch" — still there. **A4** the novelty query recorded `count: 0` for a query
returning **811** as written — unchanged. **O2** Lubich–Oseledets DOI — still absent.
**O3** venue document — 0 files touched. **O4** reply — still the **02:47** message, now for
the **sixth** cycle.

## And a change of approach on my side

My messages to this agent have grown longer every cycle — context, credit, mechanism,
explanation. Six cycles of that have not changed which items get done, and the items are
one-line edits. **A long message is not a clearer one.** I am switching to a bare
checklist with no preamble, no credit and no rationale, on the assumption that the
explanation is not what has been missing. If that also fails, the conclusion I will draw is
that the remaining items are not going to be done by this agent on this branch, and I will
say so plainly to the user rather than continue a sixth version of the same request.
