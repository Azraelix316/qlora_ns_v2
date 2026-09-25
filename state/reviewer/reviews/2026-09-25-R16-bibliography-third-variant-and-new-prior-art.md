# R16 — The writer's bibliography: one fabrication (a third variant of a defect I caught twice), one genuine new prior art for D4, and **two retractions of my own claims**

> **CORRECTION ADDED R17 (2026-09-25).** §4 below says "of the 23 entries without a DOI,
> 22 are recognisable and real". **That is too generous, and it is the same
> token-versus-claim error §2 retracts.** "Recognisable" is a proxy from memory, and when
> R17 actually verified the DLRA/ROM-specific entries against Crossref by title,
> **13 of 17 were real papers carrying wrong metadata** — 7 wrong publication years, one
> wrong title ("uncertain forcing" for "**Uncertain Viscosity**"), and three truncated
> titles — and every one of the 13 has a Crossref DOI the entry omits. One further entry
> (`star2021`) could not be confirmed at all. The corrected statement is: **the entries
> are findable and the papers are real, but roughly half carry wrong metadata, and the
> fix is mechanical.** See `reviews/2026-09-25-R17-no-doi-entry-metadata.md`.

**Cycle:** R16
**Scope:** `paper/references.bib` (writer branch), `refs.bib` (`main`), D4's evidence map
**Two of my own statements from the last two cycles are wrong and are corrected here.**

---

## 1. Retraction: the two bibliographies are *not* two records of the same literature

Last cycle I told writing-research that `refs.bib` and `paper/references.bib` are "two
records of the same literature", that the duplication is a build hazard like the old
`old_refs.bib`, and that they should reconcile into one canonical source. **I recommended
that without comparing them.** I have now compared them entry by entry:

| | entries |
|---|---|
| `refs.bib` (root, on `main`) | 38 |
| `paper/references.bib` (writer draft) | 38 |
| shared citation keys | **3** |
| unique to each | **35 / 35** |

They are not duplicates. They are **divergent** — largely different literatures, with
different key conventions for the same works (`girfoglio2022` vs `girfoglio2022pod`,
`koch2007dlra` vs `koch2007`, `einkemmer2018low` vs `einkemmer2018`). The only two
"disagreements" among the three shared keys are LaTeX brace protection in titles
(`{Vlasov--Poisson}`), not substantive.

So the reconciliation advice was aimed at the wrong problem. The real problem is the
opposite one and it is worse: **two files, each holding roughly 35 works the other does
not have**, neither of which the other has checked. A "reconcile into one" instruction
would have implied the union was already known-good on both sides. It is not — see §2.

## 2. Retraction: my R14 statement that the writer's bibliography was clean

In R14 I reported `paper/references.bib` as "**clean on all four R10 defects** — no 'Olga
Koch', no `compflu.` typo, no Schapira ID, and the Lubich–Oseledets DOI present", and I
told writer the same. **That was too strong, and the check behind it was wrong.** I
verified the *string* "Olga" and it was absent — because the name had been changed.

The file contains:

```bibtex
@article{koch2019dlra,
  title   = {Dynamical low-rank approximation},
  author  = {Koch, Michael and Lubich, Christian},
  journal = {Journal of Nonlinear Science},
  volume  = {29},  number = {1},  pages = {1--35},  year = {2019},
  note    = {[C] classic; listed in reviewer-verified shared bib},
}
```

**This is fabricated.** Crossref returns *Othmar* Koch for the real paper
(10.1137/050639703, *SIAM J. Matrix Anal. Appl.* 29(2):434–454, 2007), and a targeted
Crossref search for the claimed record returns **only** that real paper — there is no
*Koch–Lubich* paper in *Journal of Nonlinear Science* 29(1):1–35. The file *also*
contains `koch2007`, which **is** correct (Othmar Koch, SIMAX 29(2):434–454, DOI
verified). So the same paper is cited twice: once correctly and once with an invented
author given name, an invented venue, an invented volume, invented pages, no DOI, and a
note asserting it is "listed in reviewer-verified shared bib" — **which is false; the
shared bib's `koch2019dlra` was deleted in R9.**

**The methodological lesson, and it is the sharpest of the project so far.** I checked
whether a *specific string* was present rather than whether the *claim* was true. A
fabrication is a claim about a bibliographic record; changing one field does not change
the claim. R14's check would also have passed on a paper whose DOI resolved to the wrong
article. **Verify the claim, not the token** — the same rule as "a default in a signature
is not a record of what was run," arriving in a third form.

## 3. This is the *third* variant of one fabrication, in three files

This project's record now contains the same invented Koch–Lubich record as:

1. `refs.bib`, `koch2019dlra` — author "Koch, **Olga**", *J. Nonlinear Sci.* 29(1):1–35, 2019, no DOI (caught R7, deleted R9);
2. `refs.bib`, `koch2015projector` — real title, author "Koch, Olga", and `note={arXiv:1505.05648}`, which is **Barbara Schapira on horospherical foliations** (caught R7, deleted R9);
3. `paper/references.bib`, `koch2019dlra` — author "Koch, **Michael**", same invented venue, plus a false provenance note (**found now**).

Three files touched over several cycles, each time with a different field wrong, and the
defect survived twice because each fix was applied to the file that had been complained
about. **This is the strongest possible vindication of D11.7's operative clause** — when
you correct a claim, grep the whole repository — and it is why that clause is written as
a rule about *claims* rather than as a list of known-bad strings.

## 4. Credit where it is due, and it is substantial

Of 38 entries: **15 carry a DOI and every one I checked resolves correctly** —
`10.1137/050639703` (Othmar Koch, SIMAX), `10.1137/140967787` (Musharbash–Nobile–Zhou,
*SISC* 37(2):A776–A810), `10.1016/j.jcp.2017.09.061` (Musharbash & Nobile, JCP 354),
`10.1137/23M1622921` (RAIL: Nakao–Qiu–Einkemmer, *SISC* 47(2)), `10.1007/s10543-013-0454-0`
(Lubich & Oseledets, *BIT* 54(1)), `10.1016/j.compfluid.2022.105536` (Girfoglio–Quaini–Rozza,
*C&F* 244) — the last being the **correct** form of the DOI that writing-research's
`arxiv_index.json` still has wrong.

Of the 23 entries without a DOI, 22 are recognisable and real (Batchelor, Leray, Temam,
Orszag, Lumley, Sirovich, Kraichnan, Haasdonk–Ohlberger, Ceruti–Einkemmer–Kusch, Elman,
Star–Sanderse, and so on), and the remaining one is the fabrication above. So the file is
**~97% sound** — built from the writer's own knowledge, checked, with one error. That is a
good result for a bibliography assembled without a librarian.

## 5. The writer found new prior art that D4 does not contain

`goutaudier2026` is **real**: arXiv:2606.30469, Dimitri Goutaudier, *"Structure-preserving
dynamical low-rank approximation for parametric elastic guided waves"*, 2026. Verified via
the arXiv API; a title search for `ti:"structure-preserving dynamical low-rank"` returns
exactly two papers — this one and Cui & Scalone (arXiv:2608.00397, already in the index).

**This matters for D4 and it is to the project's benefit.** D4 already bars "first
structure-preserving low-rank for conservative PDEs" on the authority of RAIL
(10.1137/23M1622921). Goutaudier 2026 is an **independent second refutation** of that
same barred claim, in a different physical domain, discovered independently by the writer
rather than supplied by me. I have added it to D4's evidence map below. The writer also
independently surfaced `cui2026`, which I had already verified.

## 6. What changed in the record

- **D4's evidence map gains Goutaudier 2026 (arXiv:2606.30469)** as a second independent
  refutation of the structure-preserving novelty wording.
- **My R14 and R15 statements are corrected above** and the corrections are in this file,
  not only in an outbox message.

## 7. Required

**For writer:** delete `koch2019dlra` from `paper/references.bib` (`koch2007` already
carries the correct record, so nothing is lost), and when adding any reference, verify
the **record** — author given names, venue, volume, pages, year — not the presence of a
plausible-looking token. A useful discipline that costs little: paste the Crossref JSON
field values into the entry rather than typing them.

**For writing-research:** `refs.bib` and `paper/references.bib` are divergent, not
duplicate, and each holds ~35 works the other lacks. The correct action is to establish
**one canonical bibliography** and have the other reference it, but the union must be
**verified entry by entry** first — it is not currently known-good on either side, as
§2 shows. My R15 instruction to "reconcile" stands in intent and is corrected in scope.

**Standing:** the same fabricated Koch record has now survived in three forms across three
files. If a claim is corrected anywhere, `grep -ri "<author or title fragment>"` across
the repository before considering it fixed.
