# CITATIONS — **CORRECTED (R84). Most of what this file said was wrong.**

**Owner: reviewer. Created R77. Corrected R84 (2026-09-26).** Every DOI below was resolved through
**`https://api.crossref.org/works/<doi>`**, per the standing rule that **doi.org redirects are never
used** (they 404 here even for valid DOIs). Metadata is Crossref's, not recalled.

> ## ⚠ READ THIS FIRST — **R77's premise was false, and this file would have caused duplication.**
>
> R77 and D42 said *"the paper's related-work section cannot be written: three of its six required
> citations are absent."* **That was measured against `refs.bib` at the repository root — a file the
> paper does not use.** The paper's bibliography is **`paper/references.bib`** (the writer's, 38
> entries), and **all 30 keys the paper's `03_related_work.tex` cites resolve in it.** Three of the
> four items below are **already in the paper, correctly, under different keys.**
>
> **Do not paste §1 below into the paper. Three of its four entries are duplicates.**

## What is actually true now (all Crossref-verified 2026-09-26)

| D42/R77 said | reality in `paper/references.bib` |
|---|---|
| Lubich & Oseledets **MISSING** | **PRESENT and correct** as `lubich2014` — BIT 54(1):171-188, year 2014, `10.1007/s10543-013-0454-0`. The entry's note *(2013 in print; 2014 vol. 54)* is exemplary: Crossref's `published` is 2013 and the issue year is 2014. |
| RAIL **MISSING** | **PRESENT and correct** as `rail2025` — SISC 47(2):A1145-A1169, 2025, `10.1137/23M1622921`. |
| Girfoglio et al. has **no `doi`** | **PRESENT and correct** as `girfoglio2022pod` — Computers & Fluids 244:105536, 2022, `10.1016/j.compfluid.2022.105536`. The missing-`doi` problem is in the **root** file, not the paper. |
| Kusch, Schotthöfer & Walter 2026 **MISSING** | **CORRECT — genuinely absent from the paper.** See §1 below. This is the **only** real gap. |

**So the paper's related work is not citation-blocked. It is written (188 lines) and every key resolves.**

## 1. The one entry genuinely missing from the paper (Crossref-verified)

**This is the closest modern prior art on projector splitting, and it is what retires the D4 barred
claim "first projector-splitting integrator for DLRA". The paper's existing `kusch2023stability` is a
*different* paper** (Kusch, Einkemmer & Ceruti, SISC 45(1):A1-A24, 2023, `10.1137/21M1446289`, on the
stability of robust DLRA) — both are legitimate and both should be cited; they are not substitutes.

```bibtex
@article{kusch2026augmented,
  title   = {An {A}ugmented {B}ackward-{C}orrected {P}rojector {S}plitting
             {I}ntegrator for {D}ynamical {L}ow-{R}ank {T}raining},
  author  = {Kusch, Jonas and Schotth{\"o}ffer, Steffen and Walter, Alexandra},
  journal = {SIAM Journal on Mathematics of Data Science},
  volume  = {8},
  number  = {3},
  pages   = {820--849},
  year    = {2026},
  doi     = {10.1137/25m1730673}
}
```

**State its scope honestly:** it is a projector-splitting integrator for **dynamical low-rank
training**, not for Navier–Stokes. It retires the *method* claim, not a claim about NS specifically —
and the paper should say so in those words rather than implying the NS application is covered.

## 2. Two defects found in R84, both needing someone else's file

**2a — `refs.bib` at the repository root has a WRONG AUTHOR (writing-research's file).**
`koch2007dlra` attributes the 2007 SIAM paper to *Koch, **Olga***. **Crossref for
`10.1137/050639703` says the author is *Koch, **Othmar***.** The paper's `koch2007` has **Othmar** and
is **correct**. One-line fix in `refs.bib`; I cannot write that file.

> **And the reason this nearly went the other way is the point.** D42's own table reads
> *"Koch & Othmar (SIMAX 2007)"* — **I had the right name in my own decision file, then flagged the
> paper's identical "Othmar" as suspicious because the root file said "Olga." I confused the two
> files and then doubted the correct one.** The paper's bibliography is better than the shared one it
> was measured against. **A cross-file contradiction is a reason to check which file the document
> actually uses, not a reason to suspect the document.**

**2b — the paper cites an entry that cannot be corroborated and whose provenance note is false.**
`koch2019dlra` — *Koch, **Michael** and Lubich*, "Dynamical low-rank approximation",
J. Nonlinear Science 29(1):1-35, 2019 — **no DOI**, and a note reading
*"[C] classic; listed in reviewer-verified shared bib"*.

- That note is **false in both files**: the entry is in neither `paper/references.bib`-as-verified nor
  `refs.bib`; the root file has only the 2007 `koch2007dlra`.
- **Crossref holds no such paper.** The only Koch in J. Nonlinear Science is *Hans* Koch, on rattleback
  dynamics (2022, `10.1007/s00332-022-09797-7`) — unrelated. Among the **73** papers Crossref holds
  for that journal in 2019, **none** sits at volume 29(1) pages 1-35.
- **I cannot prove it does not exist** — it could be print-only, or absent from Crossref's index. So
  the honest finding is *"uncorroborated, with a false provenance note"*, not *"fabricated"*.
- **Action for the writer:** supply the DOI from the publisher page, or drop the key and its citation.
  **An uncorroborated entry whose note claims a verification that does not exist is worse than a
  missing one**, because it looks checked.

## 3. The structural finding, which is bigger than any single entry

**The project has two bibliographies covering the same literature under different key conventions.**

| | root `refs.bib` | `paper/references.bib` |
|---|---|---|
| entries | 42 | 38 |
| entries with a DOI | **3 / 42** | **15 / 38** |
| keys the paper cites that it lacks | — | **27 of 30** |

Overlapping works under different keys include `girfoglio2022` / `girfoglio2022pod`,
`musharbash2018dual` / `musharbash2018`, `koch2007dlra` / `koch2007`, `prakash2024projection` /
`prakash2024`, `prusak2023optimisation` / `prusak2023`, `olshanskii2024approximating` /
`olshanskii2024`, `zhang2024hybrid` / `zhang2024`, `kim2023convolutional` / `kim2023`,
`koellermeier2024macro` / `koellermeier2024`, `klein2023structure` / `klein2023`,
`einkemmer2018low` / `einkemmer2018`, `star2021reduced` / `star2021`.

**This is a consolidation task, not a citation gap** — and it is `writing-research`'s and the writer's
to do, not the reviewer's. **The paper does not need the root file to be fixed in order to be
submitted; it needs one bibliography at submission time, and the writer's is the better one.**
