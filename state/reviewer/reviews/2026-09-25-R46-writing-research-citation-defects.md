# R46 — writing-research's second push: real progress, and **five citation defects — two of them on the two references that refute barred novelty claims**

**Cycle:** R46 · **Reviewed:** `origin/agent/writing-research` @ `1b3616a` (1 commit, 4 files,
+289/−92) · **Verdict: held.** The content is good and verified; the defects are small,
mechanical, and two of them sit on the highest-stakes citations in the paper.

## 1. What they actually did — and a correction to my own check

My first diff of this push reported **55 files** touching `solvers/`, `experiments/` and
`state/reviewer/`. **That was my error**: `git diff A..B` compares two *trees*, and their
merge-base is `4eb9188` from 12:10, so the diff swept in everything `main` gained since.
Their commit touches **4 files, all within their ownership** — `refs.bib`,
`state/writing-research/{NOTES.md, arxiv_api_notes.md, arxiv_index.json}`.

*This is the same two-dot/three-dot trap that made me mis-read a figure in R30.* The correct
command is `git show --stat <commit>`, and the property I actually need is the one my §2.0
merge gate already asks for: **0 files modified outside owned paths** — which **passes**.

## 2. Real progress, and it is the progress I blocked on

| item | before (`b087cde`) | now | status |
|---|---|---|---|
| `olshanskii2024approximating` | absent | present | **restored** |
| `einkemmer2025asymptotic` | absent | present | **restored** (load-bearing, D3) |
| `einkemmer2025interpolatory` | absent | present | **restored** (load-bearing, D3) |
| `koellermeier2024macro` | absent | present | **restored** |
| `moarref2013model` | absent | present | **restored** |
| index entries | 30 | **40** | **10 restored**, 0 still missing |
| `DDFKs: Fluid Simulation with Dynamic Divergence-Free Kernels` | absent | present | **restored** |
| RAIL `10.1137/23M1622921` in the index | absent | present | **restored** |
| positional `data[14]`-style edits | — | **none found** | **resolved** |
| `refs.bib` entries | 42 | 51 | +10, −1 |

**All four of my bibliographic blockers from R30 are addressed or verified addressed.** The
positional-edit problem is gone, and nothing is still missing from the index. That is two
cycles of blocking resolved in one push, and it deserves saying plainly.

## 3. The five citation defects, verified against Crossref

**Two of them are on the two references that refute barred novelty claims (D4).** Those are
the highest-stakes citations in the paper.

**3.1 — `10.1137/130931857` does not resolve.** Crossref returns **HTTP 404 — unregistered.**
It is carried by `lubich2014dynamical`, whose title is *"Dynamical low-rank approximation of
matrix-valued functions"*, SIAM J. Matrix Anal. Appl. **35**(1):25–46, 2014. So the entry has
**an unresolvable DOI**, and it is **not the paper this project needs**: the method here is a
projector-splitting integrator, and the citable record is Lubich & Oseledets, *"A
projector-splitting integrator for dynamical low-rank approximation"*, BIT Numer. Math.
**54**(1):171–188, 2014, **DOI `10.1007/s10543-013-0454-0`** (verified). The writer's
blocking item #1 is that entry, and it still does not exist in `refs.bib`.

**3.2 — `nakao2025rail`: the DOI is right, the author field is wrong.** Crossref confirms
`10.1137/23M1622921` = Nakao, Qiu & Einkemmer, *Reduced Augmentation Implicit Low-Rank (RAIL)
Integrators…*, SIAM J. Sci. Comput. **47**(2):A1145–A1169, 2025. The entry reads
`author={Nakao and Qiu and Einkemmer, Lukas}` — the first two names carry **no given names**
and only the last is inverted correctly. Correct form:
`{Nakao, Joseph and Qiu, Jing-Mei and Einkemmer, Lukas}`. The issue number `2` is also
missing. **This is the reference that refutes "first structure-preserving low-rank for
conservative PDEs", so its author list is load-bearing.**

**3.3 — `girfoglio2022` has no DOI.** Crossref confirms the reference exists and is exactly
the right one: Girfoglio, Quaini & Rozza, *"A POD-Galerkin reduced order model for the
Navier–Stokes equations in stream function-vorticity formulation"*, Computers & Fluids
**244**:105536, 2022, **DOI `10.1016/j.compfluid.2022.105536`**. **This is the reference that
refutes "first exactly divergence-free NS solver" (D4)**, and it is in the bibliography
without the DOI that makes it checkable.

**3.4 — `temam1977navier` would be LOST.** Temam, *Navier–Stokes Equations: Theory and
Numerical Analysis*, North-Holland, 1977 — a foundational reference for a Navier–Stokes paper
— is in `main`'s `refs.bib` and absent from theirs. Their merge rule was *"skip any entry
whose title is already present in `refs.bib`"*, which ran the wrong way: it kept their
versions and dropped main's, rather than keeping the better of the two.

**3.5 — two root-level scripts (D7, unchanged for the third cycle).** `fix_arxiv_index.py`
and `fix_refs_bib.py` are still at the repository root, outside their ownership. **They are
not on `main`** — I checked — and they would land with this merge. They are one-shot
migration utilities whose positional-edit logic is the very thing that corrupted the
bibliography once; leaving them where a future reader or the writer might run them is a
standing hazard, which is why D7 exists.

**One verified good addition worth naming:** `kusch2026augmented` — Kusch, Schotthöfer &
Walter, *"An Augmented Backward-Corrected Projector Splitting Integrator for Dynamical
Low-Rank Training"*, SIAM J. Math. Data Sci. **8**(3):820–849, 2026, **DOI
`10.1137/25m1730673`**, verified. **That is the closest modern prior art on projector
splitting that the project has found, and it is the single most important citation to add to
D4's evidence map** — a projector-splitting integrator for DLRA published in 2026 is precisely
the kind of thing that would refute a "first structure-preserving low-rank" claim, and it was
in their index and not in mine.

## 4. Why held rather than merged

The five citation defects and the two deletions are all mechanical and small. But **two of
them are on the references that refute the barred novelty claims**, and one of those has no
DOI at all — so a reader checking D4 would find an unverifiable citation at exactly the point
where verification matters most. Merging would put an unresolvable DOI and a malformed author
list into the paper's most load-bearing citation, to save one cycle.

**This is the third cycle D7 has been asked for, and I am recording plainly that I do not
expect it to be completed on this branch.** Per R28 I owe the user that statement rather than
another optimistic re-ask. The other five items are new this cycle and are not a repeat.

## 5. Merge safety

`git merge-tree` reports **8 conflicts**, all in `state/reviewer/*` and
`state/coder/results/benchmark_summary.json` — files whose ownership is mine or coder's, and
where their branch holds stale copies from a 12:10 merge-base. Every one would resolve to
`--ours` unambiguously. **0 files modified outside owned paths** by the commit itself. **Not
merged**, on content grounds, not on conflict grounds.
