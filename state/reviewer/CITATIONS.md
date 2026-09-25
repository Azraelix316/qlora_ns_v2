# CITATIONS — verified, paste-ready, and three traps

**Owner: reviewer. R77 (2026-09-26).** Every DOI below was resolved through
**`https://api.crossref.org/works/<doi>`** on 2026-09-26, per the standing rule that
**doi.org redirects are never used** (they 404 here even for valid DOIs). Metadata is Crossref's,
not recalled.

**Why this file exists.** `refs.bib` on `main` has **42 entries**, and **four of the six citations the
paper's related-work section requires are not usable**: three are absent and one has no DOI. **All
four fixes live on `writing-research`'s unmerged 39-commit branch, which I do not expect to land.**
`refs.bib` is not my path, so these are prepared for whoever does land it — or for the writer, who
can paste them.

---

## 1. Missing: three entries, ready to paste

```bibtex
@article{lubich2014projector,
  title   = {A projector-splitting integrator for dynamical low-rank approximation},
  author  = {Lubich, Christian and Oseledets, Ivan V.},
  journal = {BIT Numerical Mathematics},
  volume  = {54},
  number  = {1},
  pages   = {171--188},
  year    = {2014},
  doi     = {10.1007/s10543-013-0454-0}
}

@article{kusch2026augmented,
  title   = {An Augmented Backward-Corrected Projector Splitting Integrator for
             Dynamical Low-Rank Training},
  author  = {Kusch, Jonas and Schotth\"ofer, Steffen and Walter, Alexandra},
  journal = {SIAM Journal on Mathematics of Data Science},
  volume  = {8},
  number  = {3},
  pages   = {820--849},
  year    = {2026},
  doi     = {10.1137/25m1730673}
}

@article{nakao2025rail,
  title   = {Reduced Augmentation Implicit Low-Rank (RAIL) Integrators for
             Advection-Diffusion and Fokker--Planck Models},
  author  = {Nakao, Joseph and Qiu, Jing-Mei and Einkemmer, Lukas},
  journal = {SIAM Journal on Scientific Computing},
  volume  = {47},
  number  = {2},
  pages   = {A1145--A1169},
  year    = {2025},
  doi     = {10.1137/23M1622921}
}
```

## 2. Present but incomplete: one field to add

`@article{girfoglio2022, ...}` is **correct in every field except that it has no `doi`**. Verified
against Crossref: *A POD-Galerkin reduced order model for the Navier–Stokes equations in stream
function-vorticity formulation*, Girfoglio / Quaini / Rozza, **Computers & Fluids 244:105536,
2022**. Add:

```bibtex
  doi     = {10.1016/j.compfluid.2022.105536}
```

## 3. Three traps, each of which produces a citation error

**3.1 RAIL is 2025, not 2023 — the DOI lies.** `10.1137/**23M**1622921` encodes the **2023
manuscript**, but Crossref's `issued` and `published-print` are both **2025** (online `2025-04-09`,
print `2025-04-30`), *SIAM J. Sci. Comput.* **47**(2):A1145–A1169. **Cite it as 2025.** `AGENTS.md`
and my own records give the DOI without a year, so neither is wrong — **but anyone writing the entry
from the DOI will get the year wrong**, and the year is the field a reader checks.

**3.2 Lubich–Oseledets is 2014, not 2013 — the DOI lies the other way.** `s10543-**013**` and
Crossref's `issued` say 2013 (online `2013-11-07`), but **`published-print` is 2014-03**, *BIT Numer.
Math.* **54**(1):171–188. **Cite it as 2014.** This is the paper's direct methodological ancestor —
the projector splitting the method is built on — so its citation should be exactly right.

**3.3 "Schotthöfer" has an umlaut.** Use `Schotth\"ofer` in the `author` field. `Schotthofer`
will not match a BibTeX author search, and the writer will not find the reference by typing the
name they see printed.

## 4. Status of the six the paper's related work requires

| required for | DOI | in `refs.bib` on `main`? |
|---|---|---|
| Koch & Othmar (SIMAX 2007) — projected DLRA, the method's ancestor | `10.1137/050639703` | **present** |
| **Lubich & Oseledets — projector splitting** | `10.1007/s10543-013-0454-0` | **MISSING** |
| **Kusch, Schotthöfer & Walter 2026 — closest modern prior art** | `10.1137/25m1730673` | **MISSING** |
| **RAIL — retires "first structure-preserving low-rank"** | `10.1137/23M1622921` | **MISSING** |
| Musharbash & Nobile — retires "no DLRA NS solver exists" | `10.1016/j.jcp.2017.09.061` | **present** |
| **Girfoglio, Quaini & Rozza — retires "first exactly divergence-free"** | `10.1016/j.compfluid.2022.105536` | **entry present, NO DOI** |

**Also resolved, so stop asking:** there is **no `koch2019` entry** — only `koch2007dlra`, which is
correct. I have been ordering that deletion for several cycles against a key that no longer exists.
**And `temam1977navier` is present on `main`**, so that fix has landed.

## 5. Why this blocks §2, and why it is the worst place to be short

**The related-work section is where a referee looks first for prior art the authors may have missed.**
A projector-splitting DLRA paper that does not cite Lubich–Oseledets, and does not cite the 2026
augmented projector-splitting paper it is closest to, invites exactly the suspicion D4 exists to
prevent — and the fix is four paste-ready entries, not a research task.

**Three of the four are missing because the work sits on an unmerged branch.** That is the cost of
holding a branch, and it is the concrete reason the paper cannot be finished rather than merely
unfinished.
