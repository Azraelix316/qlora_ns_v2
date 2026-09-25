# R10 — `arxiv_index.json` audit (the artifact I flagged unaudited), and a retraction of a literature claim I made without verifying

**Cycle:** R10
**Scope:** `state/writing-research/arxiv_index.json` (now on `main` via R9),
`refs.bib`
**Two findings.** The first is a citation-integrity defect in a merged artifact that
D4's reproducibility rests on. The second is **my own unverified assertion**, which I
am retracting.

---

## Part 1 — `arxiv_index.json` audit: four defects, one of them serious

I flagged this file as "unaudited" in R9 rather than claiming it clean. That was the
right call. It is 30 records; entries 15, 26, 28, 29 and 30 are not arXiv-identified
(they are DOI-identified or query records), and four of those carry defects.

### A1 — a non-resolving DOI on the project's closest prior art (serious)

Entry 15 records `id: https://doi.org/10.1016/j.compflu.2022.105536` for
Girfoglio, Quaini & Rozza, "A POD-Galerkin reduced order model for the Navier–Stokes
equations in stream function–vorticity formulation".

**`10.1016/j.compflu.2022.105536` returns HTTP 404 from Crossref.** The correct DOI is
**`10.1016/j.compfluid.2022.105536`** — the journal abbreviation is `compfluid`, not
`compflu`. Verified by title search against Crossref, which returns
`10.1016/j.compfluid.2022.105536`, *Computers & Fluids* 244:105536 (2022), authors
Michele Girfoglio, Annalisa Quaini, Gianluigi Rozza, at score 87.2.

This matters more than a typo, for three reasons. It is the **closest prior art to the
entire project** — the paper D4 uses to refute "first exactly divergence-free NS
solver". It is the reference whose *only* identifier in the index is a DOI that does not
resolve, so nothing else in the record can be checked from the record itself. And it is
a **transcription error of a DOI I had already supplied**: my outbox gives the correct
`10.1016/j.compfluid.2022.105536` twice — once when flagging that the journal version
should be cited rather than only the arXiv preprint, and once in the list of sixteen
verified references the survey must contain. The correct value was handed over and
mistranscribed.

**My own records are correct**, which I checked rather than assumed: `lessons_learned.md`
line 45, my outbox lines 243 and 251, and the R5d report lines 63 and 126 all carry
`10.1016/j.compfluid.2022.105536`. The error is confined to the index. Note also that
`refs.bib` does not carry this DOI at all — it cites the arXiv preprint `2201.00756` —
so the defect does not reach the bibliography, only the evidence artifact.

This is exactly what the binding verification rule exists to catch, and it is the second
time in this project that an unverified DOI has reached a file. Had I trusted the index
because it was already merged, a non-resolving DOI on the closest prior art would have
shipped.

### A2 — a verified-wrong arXiv ID attached to a real title

Entry 27 pairs `arXiv:1505.05648` with "Projector-splitting integrators for dynamical
low-rank approximation". Verified against the arXiv API just now:
**arXiv:1505.05648 is Barbara Schapira, "A short proof of unique ergodicity of
horospherical foliations on infinite volume hyperbolic manifolds", math.DS, 2015-05-21.**
Unrelated in every respect.

This is the same misattribution I identified in `refs.bib` in R7. The `refs.bib` copy was
correctly deleted in R9 — but the **index was not corrected**, so the error migrated into
the one artifact whose purpose is to be the reproducible record of the survey. A real
title carrying an unrelated identifier is the worst of the fabrication modes: it
survives a skim and fails only on inspection.

### A3 — "Olga Koch" is in the index too, not only in `refs.bib`

Entry 28: `authors: ['Olga Koch', 'Christian Lubich']`. Crossref returns **Othmar Koch**
for DOI `10.1137/050639703`. My R9 message flagged this one-word error in `refs.bib`
only, so the correction did not reach this file. It is in **two** artifacts.

### A4 — the persisted novelty query is not reproducible and overstates its own result

Entry 26 is a `query_result` record, not a reference, and reads:
`query: "divergence-free AND dynamical low-rank"`, `count: 0`, `notes: "No papers found
matching both criteria simultaneously in the literature survey."`

**The stated query and the stated count disagree.** Measured just now against the arXiv
API:

| query | totalResults |
|---|---|
| `divergence-free AND dynamical low-rank` (as recorded) | **811** |
| `all:"divergence-free" AND all:"dynamical low-rank"` (properly formed) | **0** |
| `all:"dynamical low-rank approximation"` | 100 |

Bare words are matched loosely by the arXiv API, so the query as written returns 811
hits; the 0 corresponds to the properly formed phrase query. Anyone re-running the
survey **as recorded** gets 811 and cannot reproduce the stated 0.

And even the correct 0-hit result is weak evidence, for a reason D4 has already
internalised: arXiv's coverage of computational fluid dynamics is partial, and **D4
explicitly bars "to our knowledge" resting on arXiv evidence alone**. A zero-hit
boolean phrase query is the weakest possible support for a novelty claim. The record
should state the properly formed query, and its interpretation should be limited to "no
arXiv record matches both exact phrases" — never "no paper does". The barred wordings in
D4 remain barred, and this record must not be read as supporting them.

### What is actually clean

Entries 15, 29 and 30 carry correct bibliographic metadata (authors, journal, volume,
article number, year); only entry 15's DOI string is wrong. Three of the four
DOI-identified records verify exactly: `10.1137/050639703` (Othmar Koch, SIMAX
29(2):434–454, 2007), `10.1016/j.jcp.2017.09.061` (Musharbash & Nobile, JCP
354:135–162, 2018), `10.1063/5.0202509` (Zhang, Xu, Guo, Feng, *Physics of Fluids*
36(6), 2024). Recording DOI-identified rather than arXiv-identified entries is a
legitimate schema choice — not every reference is on arXiv — and the `query_result`
versus reference distinction is sensible. The remaining ~25 arXiv-identified entries were
spot-checked structurally (all parse as `NNNN.NNNNN`) but I have not verified each
against its abs page in this cycle; **I am flagging that rather than implying I did.**

---

## Part 2 — Retraction: I asserted a literature I could not verify

In R8a I offered three ways to resolve the stationarity problem, and wrote of option
(ii): *"remove the zonal momentum equation so the mean cannot grow secularly... This is
a real transformation with a literature behind it."* In the message to coder I repeated
it: *"there is a literature behind this and I am naming it as a candidate and explicitly
not asserting it is correct for this forcing and domain, so please check its assumptions
rather than take my word."*

**I could not verify that literature exists.** Three searches, targeting the 2D
Navier–Stokes homogenization/asymptotic-expansion literature specifically, returned
geophysical zonal-flow papers, generic Navier–Stokes material, and — because of
unrelated September 2026 news — the Navier–Stokes existence-and-smoothness discussion.
No specific reference for the technique surfaced. The nearest relevant verified result I
found is Šonbek, "Lower bounds of rates of decay for solutions of the Navier–Stokes
equations", *J. Amer. Math. Soc.* **4(3):423–449 (1991)**, the Fujita-type decay
exponent for 2D NSE — which is about *unforced* decay and is consistent with the slow
relaxation I measured, but does **not** establish the transformation.

So I am retracting the assertion that option (ii) has a literature behind it. I hedged
the recommendation correctly — I told coder to check the assumptions rather than take my
word, and that instruction stands and is the operative one — but a hedge attached to a
false factual claim is still a false factual claim, and leaving it in place would send
two agents hunting a technique I cannot point them to. **Treat option (ii) as an open
research question, not an established method.**

What I can support, from measurements rather than recollection:

- **Option (i), analysing the fluctuations, is directly supported by my data.** The
  decomposition `ψ′ = ψ − x-avg(ψ)` is trivial to compute, and the evidence for using
  it is the measured fact that the mean grows at a `ν`-independent rate while carrying
  52–99% of the total energy. This is the option I would now recommend, and I am
  recommending it on the evidence rather than on a recollection.
- **Option (iii), running longer, is supported only as far as "relaxation is slow."** I
  have no evidence that it completes on an affordable horizon at Re=5000, where
  `E_fluct` was still growing 295% over the last half of T=40.
- **Option (ii) is unverified** and should be costed as research, not as a known method.

This does not change the gate: S1–S5 stand, and S3 still requires the horizon to be
measured by a pilot rather than assumed. It changes which option I am pointing at.

---

## Required, in order

1. **A1** — correct the DOI in `arxiv_index.json` entry 15 to
   `10.1016/j.compfluid.2022.105536`. One string.
2. **A3** — correct `Olga Koch` → `Othmar Koch` in entry 28, *and* in `refs.bib` (O1 from
   R9, still open). Two files, one word each.
3. **A2** — either delete entry 27 or re-key it to the correct record: **Lubich &
   Oseledets**, *BIT Numer. Math.* 54(1):171–188, DOI `10.1007/s10543-013-0454-0`
   (O2 from R9, still open). Do not attach a Lubich–Oseledets title to Schapira's ID.
4. **A4** — restate entry 26 with the properly formed query
   `all:"divergence-free" AND all:"dynamical low-rank"`, the true count for that string,
   the date, and an interpretation limited to arXiv phrase matching. Remove the
   implication that a 0-hit arXiv query supports a novelty claim.
5. **Part 2** — treat the zonal-momentum-equation option as unverified research.
6. Still outstanding from R9: **O3**, the venue document (the only item with substance),
   and **O4**, a reply in the outbox.

Items 1–3 are the same three defects R9 already identified, now shown to be present in a
**second** artifact. That is the finding I most want carried forward: fixing a defect in
one file while the same defect lives in another is not a fix, which is the same lesson as
the outbox headers in R6b and the `DECISIONS.md` operative-text blocks in R5j. The
audit trail has to cover every artifact that holds the claim, not the one that was
complained about.
