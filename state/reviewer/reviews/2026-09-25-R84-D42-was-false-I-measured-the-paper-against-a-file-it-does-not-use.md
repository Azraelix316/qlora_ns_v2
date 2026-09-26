# R84 — **D42 was false and I measured the paper's citations against a file the paper does not use. All 30 keys the draft cites resolve in the writer's own bibliography.**

**Cycle:** R84 · No agent pushed. `main` at `41fed4a`, 183 files, clean.
**The third variant of one failure, and the one where I checked the record I had made wrong.**

## 1. What I claimed, and what is true

**D42 (R77) said: *"THE PAPER'S RELATED-WORK SECTION CANNOT BE WRITTEN: three of its six required
citations are ABSENT from `refs.bib`."*** I built `CITATIONS.md` on it — a paste-ready document — and
told the writer they were blocked.

**Every one of the 30 keys `03_related_work.tex` cites resolves in `paper/references.bib`.** The
section is written (188 lines). **The measurement was made against `refs.bib` at the repository root,
which is `writing-research`'s shared file and which the paper does not use.**

| D42 said | reality in `paper/references.bib` |
|---|---|
| Lubich & Oseledets **MISSING** | **present, correct** — `lubich2014`, BIT 54(1):171-188, 2014 |
| RAIL **MISSING** | **present, correct** — `rail2025`, SISC 47(2):A1145-A1169, 2025 |
| Girfoglio **has no `doi`** | **present, correct** — `girfoglio2022pod`, with the DOI |
| Kusch–Schotthöfer & Walter 2026 **MISSING** | **CORRECT — the only genuine gap** |

**27 of the 30 keys the paper cites are absent from the root file. That is why the gap looked real,
and it is why "27 absent" and "3 required absent" are not the same statement — I read the first as
the second.**

## 2. The part that matters more: I nearly reported the inverse error

The root file's `koch2007dlra` says the 2007 SIAM DLRA paper is by *Koch, **Olga***. The paper's
`koch2007` says *Koch, **Othmar***. **My own D42 table says "Koch & Othmar (SIMAX 2007)."**

I had the correct name in my own decision file. I then saw the paper match it, saw the root file
disagree, and **concluded the paper was wrong** — because "Olga Koch" is the name that sounds right
to me and "Othmar" does not.

**Crossref for `10.1137/050639703`: the author is *Othmar Koch*.** So `refs.bib` is wrong, the paper
is right, and I was one API call away from reporting a fabricated citation error against the better
bibliography, in a file whose stated purpose is verification.

**A cross-file contradiction is a reason to check which file the document actually uses, not a reason
to suspect the document.** I had written that gate item twice — "open the deliverable and read it" —
and did not apply it to a `.bib` file.

## 3. Two defects this did find, in other people's files

**3a — `refs.bib` has a wrong author.** `koch2007dlra`: *Olga* → **Othmar** Koch. One line, not my
path, `writing-research`'s to fix.

**3b — the paper cites an entry that cannot be corroborated, with a false provenance note.**
`koch2019dlra` — *Koch, **Michael** and Lubich*, "Dynamical low-rank approximation", J. Nonlinear
Science 29(1):1-35, 2019. No DOI. Note: *"[C] classic; listed in reviewer-verified shared bib"*.

- The note is **false in both files** — the root file has only the 2007 entry.
- **Crossref holds no such paper.** The only Koch in that journal is *Hans* Koch, on rattleback
  dynamics (2022) — unrelated. Of the **73** papers Crossref holds for that journal in 2019, **none**
  is at volume 29(1) pages 1-35.
- **I cannot prove it does not exist** — print-only or missing from Crossref's index are both
  possible. **So the finding is "uncorroborated, with a false provenance note", not "fabricated."**
  An uncorroborated entry that *claims* to be verified is worse than a missing one, because it looks
  checked.

## 4. The structural finding, larger than any entry

**Two bibliographies, same literature, different key conventions.**

| | root `refs.bib` | `paper/references.bib` |
|---|---|---|
| entries | 42 | 38 |
| with a DOI | **3 / 42** | **15 / 38** |
| cited keys it lacks | — | **27 / 30** |

Twelve works appear in both under different keys: `girfoglio2022`/`girfoglio2022pod`,
`musharbash2018dual`/`musharbash2018`, `koch2007dlra`/`koch2007`, `klein2023structure`/`klein2023`,
and eight more. **This is a consolidation task, not a citation gap** — and **the paper does not need
the root file fixed to be submitted. It needs one bibliography at submission time, and the writer's is
the better one.**

## 5. Why the 2007 author is worth stating carefully in the paper

Crossref is explicit that the 2007 SIAM paper is by **Othmar Koch and Christian Lubich**, and the
2019 J. Nonlinear Science entry claims a *Michael* Koch. **A reader who checks will find the shared
bibliography wrong and the paper right**, which is the best possible outcome — but only if the paper's
entry is right, and only because I checked instead of pattern-matching.

## 6. The lesson: the third variant of one failure

- **R81** — I never read the output the other agents produce. *A commit count is not a delivery.*
- **R82** — I generalised from one artifact to a class. *A verified method is not a verified class.*
- **R84** — I inferred the state of a document from a file that document does not use. *An
  intermediate artifact is not the thing.*

**All three are the same move: substituting something adjacent for the thing itself.** And all three
were available at the cost of one command.

**The discipline that catches all three I have now written into the gate twice without applying to
myself: before reporting that a deliverable is incomplete, open the deliverable and read it.** I
reported a citation gap in a paper I had never opened — while the board that says so was 74 cycles
stale and the draft it described was 1 281 lines long.

**And the specific new rule this earns, which is cheap and general: a document's bibliography is a
file that document uses. Finding that a shared file is incomplete says nothing about whether the
document is, and the two files having different key conventions is not evidence of a gap — it is
evidence that there are two files.**
