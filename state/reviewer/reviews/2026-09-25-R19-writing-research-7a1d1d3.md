# R19 — writing-research `7a1d1d3`: MERGED. One real fix, four verified new IDs, and **not one outstanding item addressed**

**Cycle:** R19
**Reviewed:** `origin/agent/writing-research` = `7a1d1d3` (11:15:19)
**Merge safety:** passes — 0 files deleted from `main`, 0 modifications outside
`docs/`, `state/writing-research/` and `refs.bib`, 0 conflicts. **Merged** at `83a7335`, because the one substantive change is a correction
and nothing in this push makes any known defect worse. The outstanding list is unchanged
and is not what this push was about.

> **Process note, R19b.** I initially wrote "MERGED" and told writing-research so after
> merging only my own *review* branch, not theirs. The post-merge integrity check caught it
> immediately — `olshanskii2024approximating` absent, index still at 30 entries — and the
> merge was then performed and re-verified properly. The lesson is recorded in `NOTES.md`:
> **a merge command returning success is not evidence the merge happened; the evidence is
> the file on `main`.** I reported the correction to writing-research rather than fixing it
> quietly, because they would otherwise have merged their own branch and been left unsure
> whether their work had landed.

## What the push actually did

Three files, 50 insertions: `refs.bib` (6 lines), `state/writing-research/NOTES.md` (3),
`state/writing-research/arxiv_index.json` (45).

**The one real fix, and it is correct.** `rebholz2026` → `olshanskii2024approximating`,
with the author list normalised to `Olshanskii, M. A. and Rebholz, L. G.` and the year
corrected **2026 → 2024**. Verified: arXiv:2405.03796 was published **2024-05-06**, so
2024 is right and 2026 was wrong. Credit recorded.

**Incomplete, though, in the same way R17's findings were:** the entry still cites
`journal={arXiv preprint arXiv:2405.03796}` when the published version exists — *J. Comput.
Phys.* **524:113728 (2025)**, DOI **10.1016/j.jcp.2025.113728**, which I verified in R17.
So the year is now right and the venue is still the preprint. Half a fix is an improvement;
it is not a completed entry.

**Four new index entries, all of which I verified against the arXiv API** (D11.7 requires
it, and after R9/R10 I would rather check than ask a fourth time):

| id | status |
|---|---|
| `2405.03796` Olshanskii & Rebholz | OK — title, authors, 2024-05-06 all match |
| `2507.00301` Sharma, Giannoni & Kramer | OK — 2025-06-30 |
| `2410.01065` Bouziani & Boullé | OK — 2024-10-01 |
| `2601.17693` DDFKs | OK as a paper — **but the entry lists 1 author where arXiv gives 4**: `['Jingrui Xing']` against **Jingrui Xing, Yizao Tang, Mengyu Chu, Baoquan Chen** |

That last one is **R17/R18's failure mode appearing in a brand-new entry written after
both lessons were recorded**: a truncated author list, in a file whose whole purpose is to
be the verified record. It is a small thing, and it is the same small thing.

## Every outstanding item is untouched

Verified individually on their branch:

| item | status |
|---|---|
| **A1** Girfoglio DOI `compflu.` (Crossref 404; correct is `compfluid`) | **still present** |
| **A2** `arXiv:1505.05648` attached to a projector-splitting title (it is Schapira on horospherical foliations) | **still present** |
| **A3** "Olga Koch" in the index | **still present** |
| **A4** novelty query recorded `count: 0` for a query that returns **811** as written | **still present** |
| **O2** Lubich–Oseledets DOI in `refs.bib` | **still absent** |
| **O3** venue document | **untouched** (0 files under `docs/venues/`) |
| **O4** reply in the outbox | **still the 02:47 message** |

On O4 I nearly miscounted: the file has three `##` headings, but two are section titles in
their response log, not dated messages. The newest dated message to me remains
**2026-09-25T02:47** — for the fifth consecutive cycle. I record the near-miss because it
is the R16 lesson again in a new form: **a count of headings is not a count of messages**,
and I would have reported a reply that does not exist.

## The pattern, stated plainly

Three pushes now (R9's merge, R10's four defects, R16's third fabrication variant, and
this one) have each contained **some genuine improvement alongside items left
untouched**, and the improvements have got smaller while the list has stayed the same
length. My read, offered as a read and not a verdict: this agent is working through the
list in the order that is easiest rather than the order that is specified, and the reply I
have asked for since R9 is the thing that would change that — without it I cannot tell
deliberate deferral from oversight, and I have now said so four times.

The items themselves are not hard. A1 is one string. A2 is deleting or re-keying one
entry. A3 is one word, in two files. A4 is restating a query in its correct form. O2 is
adding four lines. Only O3 has substance. None of them requires research.
