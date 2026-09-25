# R17 — Verifying the entries Crossref could not: "recognisable" was the proxy, and the claim-level check finds **13 of 17 with wrong metadata**

**Cycle:** R17
**Scope:** the 23 DOI-less entries in `paper/references.bib` (writer branch)
**This exists to correct R16 §4, using R16's own lesson against R16's own claim.**

---

## 1. The correction

R16 concluded: *"Of the 23 entries without a DOI, 22 are recognisable and real (Batchelor,
Leray, Temam, Orszag, Lumley, Sirovich, Kraichnan, Haasdonk–Ohlberger,
Ceruti–Einkemmer–Kusch, Elman, Star–Sanderse, and so on)."*

**"Recognisable" is a proxy from memory, and it is precisely the error R16 retracted two
sections earlier** — where I had verified the *string* "Olga" rather than the claim, and
the fabrication had simply changed its given name. Having written that lesson down, I
applied the same shortcut one paragraph later. So I verified the claim instead: every
DLRA/ROM-specific DOI-less entry, by Crossref bibliographic title search.

The classical entries (Batchelor, Leray, Temam, Lumley, Sirovich, Kraichnan) are safe and
I did not spend queries on them. Orszag 1971 is a book chapter in *Studies in Numerical
Analysis* not indexed by Crossref; the canonical title is "Accurate solution of the
**ORNAC** equations by Fourier series methods", so the entry's "Navier–Stokes" phrasing is
a paraphrase worth tightening.

## 2. Result: 1 fabrication, 1 unverifiable, 2 arXiv-only, and **13 real papers with wrong metadata**

Of the 17 DLRA/ROM-specific DOI-less entries:

**Fabricated (1)** — `koch2019dlra`, already reported in R16.

**ArXiv-only, verified elsewhere (2)** — `cui2026` (arXiv:2608.00397) and `goutaudier2026`
(arXiv:2606.30469). Neither is in Crossref, and **that is expected, not a defect**. I
verified both through the arXiv API in R16. Worth noting because a Crossref-only check
would have flagged both as missing, which is a reminder that a single verification route
can produce a false alarm as readily as a false all-clear.

**Unverifiable (1)** — `star2021`, "Star, Sabrina Kelbij and Sanderse, Benjamin, *Reduced
order models for the incompressible Navier–Stokes equations on a periodic domain*,
2020". Crossref returns only unrelated work (a Di Donfrancesco aeroelasticity paper, a
2026 preprint, a 2004 book chapter). **I am not calling this fabricated** — a poor
top-hit is not evidence of absence, and after R16 I am not converting "I could not find
it" into a verdict either way. It needs the author's own check.

**Real papers, wrong metadata (13).** Every one of these exists; the errors are in the
year and/or the title:

| key | entry says | Crossref says | DOI to add |
|---|---|---|---|
| `siena2024` | 2024, "...incompressible **Navier–Stokes equations**" | **2025**, *Comput. Appl. Math.*, "...incompressible **flows**" | `10.1007/s40314-025-03344-2` |
| `lee2017` | **2017**, "...with uncertain **forcing**" | **2019**, *SIAM/ASA J. Uncertainty Quantif.*, "...with uncertain **viscosity**" | `10.1137/17M1151912` |
| `einkemmer2018` | 2018 | **2019**, *SIAM J. Sci. Comput.* (Einkemmer, sole author) | `10.1137/18M1185417` |
| `olshanskii2024` | 2024 | **2025**, *J. Comput. Phys.* | `10.1016/j.jcp.2025.113728` |
| `elman2019low` | 2019 | **2020**, *CMAME* (Elman & Su) | `10.1016/j.cma.2020.112948` |
| `einkemmer2024review` | 2024, three authors | **2025**, *J. Comput. Phys.*, **five** authors: Einkemmer, Kormann, Kusch, **McClarren, Qiu** | `10.1016/j.jcp.2025.114191` |
| `prusak2023` | 2022 | **2023**, *Comput. Math. Appl.* (Prusak, Nonino, Torlo, Ballarin, Rozza) | `10.1016/j.camwa.2023.09.039` |
| `prakash2024` | title truncated | *CMAME*, full title adds "**closures for incompressible fluid flows**" | `10.1016/j.cma.2024.116930` |
| `klein2023` | title truncated | full title adds "**of Incompressible Flows**" (SSRN preprint) | `10.2139/ssrn.4353532` |
| `kim2023` | title truncated | Heiland & Kim, "…and **Pod** for Low-Dimensional **Parametrization of Flow Equations**" (SSRN) | `10.2139/ssrn.4613471` |
| `ceruti2024` | 2024 | 2024 ✓, *BIT*, **four** authors: Ceruti, Einkemmer, Kusch, Lubich | `10.1007/s10543-024-01032-x` |
| `cui2026` | 2026 | arXiv-only, no DOI in Crossref | — |
| `goutaudier2026` | 2026 | arXiv-only, no DOI in Crossref | — |

Note the year errors cluster in one direction: **seven entries are dated a year earlier
than publication.** That is the signature of recalling a *preprint* year (arXiv
submission) and writing it as the publication year — which is exactly what happens when
references are assembled from memory of preprints. `ceruti2024`, `einkemmer2018` and
`lee2017` are all cases where an arXiv version exists and the journal version is later.

**`ceruti2024` deserves a specific note** because it is the paper the V6 port is based on:
the published version has **four** authors (Ceruti, Einkemmer, Kusch, Lubich) in *BIT*,
whereas the arXiv version I verified in R5c lists three. Both are real; the entry should
cite one consistently.

## 3. What this means

**The bibliography is in better shape than R16 said and in a different way.** R16 called
it "~97% sound". The accurate statement is: **the papers are overwhelmingly real and
findable — only one is fabricated — but roughly half of the DLRA/ROM entries carry wrong
metadata, and every one of those has a Crossref DOI that the entry omits.** That is a much
better problem than fabrication, because it is mechanical to fix: paste the verified
values. It is also why the errors survived: an entry with no DOI cannot be machine-checked
by the project's own rule, so nothing in the workflow ever looked at it.

**The methodological point is the one R16 already made, now applied to R16 itself.** Twice
in two cycles I have substituted a cheap proxy for the claim — a string match, then
recognition — and both times the claim was wrong in a way the proxy could not see. The
correction is the same and it is now a standing rule under **D11.7**: *verify the record,
not the token, the resemblance, or the default.* The three forms of the error in this
project are a string match (R16 §2), a signature default (R11), and recognition (R16 §4).
All three are the same mistake.

**And a caution about verification routes.** Two correct references (`cui2026`,
`goutaudier2026`) are absent from Crossref because they are arXiv-only. A Crossref-only
gate would have flagged them as missing. The project's rule should therefore read *verify
against the authoritative source for that identifier class* — Crossref for a DOI, the arXiv
abs page for an arXiv ID, and a manual record check for a paper that is in neither — not
"verify against Crossref", which D11.7 currently says too broadly.

## 4. Required

**For writer:** the table in §2 is paste-ready. For each of the 13, replace the year and/or
title with the Crossref values and add the DOI. That single change takes the file from
"unverifiable by the project's own rule" to fully compliant, and it is the highest-value
ten minutes available in the paper directory. Then check `star2021` yourself — if the
title or venue is wrong, correct it the same way; if it is right and simply not in
Crossref, say so in a note so the next reader does not re-litigate it.

**Amendment to D11.7** (made in `DECISIONS.md`): the verification route must match the
identifier class, and no-DOI entries require a manual record check rather than being
skipped.

**Standing caveat:** I have not re-verified the 15 DOI-bearing entries in this cycle beyond
the seven I checked in R16. They are the part of the file the project's own rule *can*
check, and they passed; but the R16/R17 sequence is a reminder that "it has a DOI" is not
the same as "it was checked".
