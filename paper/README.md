# paper/ — SP-DLRA for incompressible NS in high-Re turbulence

Draft of the conference paper. Venue-neutral LaTeX (`article` class with a
swap-in comment in `main.tex`). **No LaTeX toolchain exists on this node** —
these are sources only; compile on a machine with TeX Live / a similar stack.

## Build

```
pdflatex main
bibtex   main
pdflatex main
pdflatex main
```

Requires only standard packages: `amsmath`, `amssymb`, `amsthm`, `graphicx`,
`booktabs`, `hyperref`. Figure files are not present yet (coder owns the data;
see the `[PENDING-CODER]` figure placeholders below).

## File layout

| File | Content |
|---|---|
| `main.tex` | document class, preamble, section assembly |
| `references.bib` | writer-verified bibliography (see verification status below) |
| `sections/00_abstract.tex` | Abstract |
| `sections/01_introduction.tex` | Introduction |
| `sections/02_contributions.tex` | Contributions |
| `sections/03_related_work.tex` | Related work + comparison table |
| `sections/04_methods.tex` | Methods (4.1–4.7) |
| `sections/05_experimental_setup.tex` | Experimental setup, validation ladder L1–L4 |
| `sections/06_results.tex` | Results (all numbers pending coder) |
| `sections/07_discussion.tex` | Discussion |
| `sections/08_limitations.tex` | Limitations |
| `sections/09_conclusion.tex` | Conclusion |

## Pending placeholders (searchable)

- `[PENDING-CODER: ...]` — every number, figure, runtime, and scheme
  confirmation. Nothing is filled until `coder` pushes results to
  `state/coder/results/` with config + driver + commit (CHECKLIST 1.1).
- `[PENDING-THEORETICAL-RESEARCH: ...]` — forcing-aware invariant
  (`docs/theory/stability-error.md`, not yet written) and rank-growth theory
  (`docs/theory/rank-growth.md`, not yet written).
- `[FLAG-WRITING-RESEARCH: ...]` — items for writing-research (Osepko
  citation, bib reconciliation).
- `% [FLAG-D4 / REVIEWER: ...]` — the GATED novelty claim in the introduction
  and related work (see flag 3 below); contains the barred-phrase list.

## Bibliography verification status

`references.bib` was built by the writer **independently of the shared
`refs.bib`** (which was flagged at review R3 with unresolved issues B1–B4).
Every entry was verified on 2026-09-25 (38 entries total):

- **arXiv entries (15, `[V]`)** — title + authors re-verified against the
  arXiv abs page metadata on 2026-09-25: `einkemmer2018`, `lee2017`,
  `siena2024`, `star2021`, `klein2023`, `prakash2024`, `prusak2023`,
  `kim2023`, `elman2019low`, `olshanskii2024`, `ceruti2024`,
  `einkemmer2024review`, `cui2026`, `goutaudier2026`, `vinograd2026`
  (`vinograd2026` also published in PRF 11(3):034402, Crossref-verified).
- **Journal entries (14, `[J]`)** — verified via Crossref/DOI on
  2026-09-25. Original four: `hijazi2020` (10.1016/j.jcp.2020.109513),
  `loorenzi2016` (10.1016/j.cma.2016.08.006 — note: an earlier draft used the
  wrong suffix `.08.002`), `einkemmer2023` (10.1016/j.jcp.2023.112060),
  `kochkov2021` (10.1073/pnas.2101784118). Added/updated for the R5d prior
  art (9; DOIs as verified and stored in `references.bib`): `girfoglio2022pod`
  (updated from arXiv to Computers & Fluids 244:105536), `zhang2024` (Phys.
  Fluids 36(6):063609), `musharbash2018` (J. Comput. Phys. 354:135–162),
  `musharbash2015` (SIAM J. Sci. Comput. 37(2):A776–A810), `koch2007` (SIAM
  J. Matrix Anal. Appl. 29(2):434–454), `nonnenmacher2008` (Math. Comput.
  Simul. 79(4):1346–1357), `lubich2014` (BIT Numer. Math. 54(1):171–188),
  `kusch2023stability` (SIAM J. Sci. Comput. 45(1):A1–A24), `rail2025`
  (SIAM J. Sci. Comput. 47(2):A1145–A1169), `koellermeier2024` (Adv. Comput.
  Math. 50(4):76).
- **Classics (8, `[C]`)** — journal-only, no arXiv version; standard
  literature, entered from bibliographic knowledge and flagged for a final
  check by writing-research: `haasdonk2012`, `lumley1967`,
  `sirovich1987` (cited as Q. Appl. Math. 45(3):561–590, the standard POD
  reference), `orszag1971`, `kraichnan1967`, `batchelor1969`, `leray1934`,
  `temam1977`.

### Flags / known issues

1. **`einkemmer2018`** — arXiv metadata lists a single author (Lukas
   Einkemmer). The shared `refs.bib` may list a different author list;
   reconciled against the abs page, which is authoritative here. Flagged for
   writing-research.
2. **Osepko et al.** — CHECKLIST 2.1 requires related work to cover
   "DLRA (Osepko et al.)". **No author "Osepko" exists on arXiv** (0 hits,
   searched 2026-09-25), and a full-text search for
   "dynamical low-rank" + incompressible Navier–Stokes also returned 0
   results. Not cited (policy: nothing unverifiable goes in the bib). Awaiting
   the exact citation from reviewer / writing-research; a placeholder flag is
   in `sections/03_related_work.tex`.
3. **Novelty claim (D4) — binding R5d wording in place, GATED.** The old
   "to the best of our knowledge" hedge is **retired**. The introduction
   (short form) and related work (full form, all four R5d sentences) now use
   the reviewer's binding wording from R5d
   (`state/reviewer/reviews/2026-09-25-R5d-prior-art-map-and-final-claim.md`
   §2). Both locations carry a `% [FLAG-D4 / REVIEWER: ...]` comment listing
   the barred phrases. The claim stays **GATED**: the final "we provide one
   ... and validate it" sentence may not be un-gated until D10-V6 is
   implemented and V1/V2/V5/V7 are closed (results still [PENDING-CODER];
   the related-work table's "This work" High-Re cell reads `target`).
   Barred until then: "no DLRA NS solver exists"; "first exactly
   divergence-free NS solver"; any gap phrased as a failure to preserve
   divergence-freeness; "first structure-preserving low-rank method for
   conservative PDEs" (refuted by RAIL, 10.1137/23M1622921); "to our
   knowledge" / "to the best of our knowledge". Permitted hedge: "we are not
   aware of".
4. The six incompressible-NS ROM entries deleted from the shared `refs.bib`
   are recoverable via `git show 6a41b2a:refs.bib`; they are **not** cited in
   the current draft (the related-work table uses only entries in
   `references.bib`).
5. **`koch2019dlra` was a phantom key (R139/R140) — removed.** No such
   paper exists (Crossref: the only Koch–Lubich DLRA record is the 2007
   SIAM J. Matrix Anal. Appl. paper, `koch2007`); the bib entry was deleted
   and the four `\cite{koch2019dlra}` sites repaired: two repointed to
   `koch2007` (introduction, methods), one removed from a cite list
   (related work), and the "and a survey by Koch and Lubich" clause in
   related work deleted along with its cite, since no such survey could be
   sourced. Do not re-add the key.
