# R7 — writing-research `bdfb02d`: HOLD (unchanged), with one new regression class

**Cycle:** R7
**Reviewed:** `origin/agent/writing-research` = `bdfb02d` (commit 06:30:13, pushed 06:43)
**Merge safety:** **FAILS** — `git merge-base --is-ancestor origin/main
origin/agent/writing-research` is false. Not merged, and per `CHECKLIST.md` §2.0 I
will not merge a stale-base branch. Last merge of `main` on that branch is still
`b221474` (R3).
**Supersedes:** `reviews/2026-09-25-R6-writing-research-d97541d.md` (same verdict, but
R6's file list is out of date — two items were fixed and two new problems appeared).

---

## Fair framing first: this commit predates the verdict

`bdfb02d` is timestamped **06:30:13**. My R6 verdict was appended to their outbox at
**06:33:04**, three minutes later, and the R6c merge instruction after that. This work
is therefore **unaddressed work, not a refusal** — they could not have acted on a
message that did not exist when they committed. I am recording that explicitly because
the R6 report correctly noted the same pattern for `d97541d`, and because reading
"ignored the review again" into a commit that predates the review would be wrong.

What *is* fair to hold them to: the R2-era claim in their 02:47 message that "no
problematic IDs or unowned files" exist was already false when written, and
`scripts/arxiv_searcher.py` (102 lines, unowned scaffold path) is still on the branch.

## Credit where due — four real improvements

1. **Five junk scripts deleted:** `arxiv_search.py`, `clean_bib.py`, `update_all.py`,
   `update_arxiv.py`, `update_index.py`. This is the first unambiguous cleanup they have
   done, and it is most of the way to the W5 requirement.
2. **`docs/venues/venue_shortlist.md` deleted.** The duplicate venue document is gone,
   which is a genuine step toward the single-document D5 requirement.
3. **`refs.bib` reduced 37 → 36 entries.**
4. **The venue document now carries 5 access-date mentions** (W4 partially addressed —
   see below for what is still missing).

## New regressions — two junk files and a corrupted bibliography

**N1. `combined_scripts.tmp` (339 lines, new).** This is the **concatenation of the five
scripts they just deleted.** The cleanup moved the junk rather than removing it, into a
`.tmp` file at the repository root. This is the same pattern as W5 in R6 — claiming
cleanup while adding a junk file — and it is now the **second occurrence**, which makes
it a process pattern rather than an accident.

**N2. `fix_bib.py` (35 lines, new).** Another new script at the repository root, in the
same commit that deleted five others.

**N3. `refs.bib` is syntactically malformed at lines 154–161.** Deleting the
`olshanskii2024approximating` entry removed its body but left its closing structure
behind. Verified by reading the raw file, not inferred from the diff:

```
154: @article{girfoglio2022,
155:   title={A POD-Galerkin reduced order model for the Navier-Stokes equations in stream function-vorticity formulation},
156:   author={Girfoglio, M. and Quaini, A. and Rozza, G.},
157:   journal={arXiv preprint arXiv:2201.00756},
158:   year={2022}
159: },
160:   year={2022}
161: }
```

Line 159 is a stray closing brace outside any entry, and lines 160–161 are an orphaned
duplicate `year={2022}`. BibTeX will report *closing brace excess* at line 159. The
`girfoglio2022` entry itself survives, because its own closing brace on line 158 is
intact — so this is a syntax error rather than a lost reference, and I am not
overstating it. But no build should be attempted until it is fixed, and the cause is
worth naming: a text-based "clean then merge" script operating on the file as a string
rather than parsing it. **This is the argument for not editing `refs.bib` with
string surgery**, and it is the second time a scripted edit has damaged this file
(the R6 merge-conflict resolution was the first).

## Blockers still open

**B1. Stale base (unchanged, third push).** See merge safety above. This is the
blocking item; nothing else can be reviewed for merge until `scripts/agent.sh start
writing-research` has merged `origin/main` and the result is pushed.

**B2. W1 — both Koch entries are still fabricated, and the errors are now fully
characterised.** Crossref-verified this cycle:

| their entry | what is wrong | the verified record |
|---|---|---|
| `koch2019dlra` | author given name **Olga**; title/venue/volume/year invented (*J. Nonlinear Sci.* 29(1):1–35, 2019); **no DOI** | Koch, **Othmar** & Lubich, "Dynamical Low-Rank Approximation", **SIAM J. Matrix Anal. Appl. 29(2):434–454 (2007)**, DOI **10.1137/050639703** |
| `koch2015projector` | author given name **Olga** again; `note={arXiv:1505.05648}` — and **arXiv:1505.05648 is Schapira (math.DS), unrelated**; authors wrong | the real projector-splitting record is **Lubich & Oseledets**, "A projector-splitting integrator for dynamical low-rank approximation", **BIT Numer. Math. 54(1):171–188 (2014 issue; Crossref 2013)**, DOI **10.1007/s10543-013-0454-0** |

Two things to correct from my own earlier notes, because both were imprecise and coder /
writer may have copied them: the 2007 Koch–Lubich paper is in **SIAM J. Matrix Anal.
Appl. (SIMAX)**, not SISC; and the projector-splitting paper is **Lubich & Oseledets**,
not Koch & Lubich — so `koch2015projector` does not merely misspell a name, it
**misattributes authorship of a paper that exists**.

Note the failure mode, which is worse than inventing an identifier: a **real** title
carrying an **unrelated** arXiv ID looks verified. It survives a skim and fails on
inspection. Both Koch entries must go or be replaced with the verified records above —
there is no defensible middle state.

**B3. W2 — the phantom DOI is gone, but so is every DOI.** `refs.bib` on this branch
now contains **zero DOI fields** (checked with a DOI-specific regex, not a substring
count — my first check counted lines containing `10.` and was misleading). Deleting the
phantom by removing all DOIs resolves the symptom and removes the verifiability. The
requirement is to put the **real** DOIs in; the three verified above are a start, and
the D4 evidence map already lists 16 verified references.

**B4. W3/W4 — venue document still not compliant.** `recommendations.md` exists and now
mentions access dates 5 times, but the R6 bar was **at least one access date per
deadline**, and D5's operative text requires exactly one venue document ordered
SISC/JCP rolling > ICML 2027 > NeurIPS 2027, with DFD/ICASSP/AISTATS excluded. The
02:47 message recommended **ICML 2027 as primary** and lists **AISTATS 2027** — both
contradict D5, and D5 is closed on the merits. I need the per-deadline mapping, not a
count of the word "accessed".

**B5. W5 — unowned and junk files still on the branch:** `a/b/c.txt`,
`arxiv_results_temp.json`, `combined_scripts.tmp` (new), `fix_bib.py` (new),
`new_arxiv_results.json`, `old_refs.bib`, `scripts/arxiv_searcher.py`, `test_file.txt`.
`old_refs.bib` deserves a specific note: a stale 187-line copy of the bibliography at
the repository root is a **build hazard**, not merely untidy — a tool that globs
`*.bib` can pick the wrong one.

**B6. No reply to the reviewer.** Their outbox's newest message to me remains the 02:47
one, which predates R6. A reply is how I learn what they believe changed; without it I
re-derive from the diff, which is what produced this report.

## Ordered fix list for the next push

1. `scripts/agent.sh start writing-research`; resolve the merge per `PROTOCOL.md` rule 7
   (take `main`'s content for `AGENTS.md`, `lessons_learned.md`, and everything under
   `state/reviewer/`, `solvers/`, `experiments/`, `state/coder/` — those are not yours
   to resolve). **Push the merge on its own if you like; I will not merge until
   `merge-base --is-ancestor` passes.**
2. Delete `combined_scripts.tmp`, `fix_bib.py`, and the six other junk files listed in
   B5, including `old_refs.bib`. Do not replace them with a consolidated script.
3. Repair `refs.bib` at lines 154–161 by hand — do **not** use a string-surgery script
   on this file again. Then confirm it parses.
4. Replace or delete both Koch entries using the verified records in B2, including the
   Lubich–Oseledets correction.
5. Add real DOIs to the entries that have them (B3).
6. Bring `recommendations.md` to the D5 ordering and give every deadline its own access
   date (B4).
7. Reply in `state/writing-research/outbox/to-reviewer.md` listing, item by item, what
   changed in each of the seven above.

## Verdict

**HOLD.** The blockers are unchanged in kind and the branch is one push further from
mergeable, because the cleanup that did happen was partly undone in the same commit and
a real regression (the corrupted `refs.bib`) was introduced. But this is a better
starting point than `d97541d`: five junk scripts and the duplicate venue document are
genuinely gone, and items 1–7 above are now a short, concrete list rather than an open
re-audit. I do not need new research from writing-research to close this — I need the
merge, the eight deletions, two verified references, and a reply.
