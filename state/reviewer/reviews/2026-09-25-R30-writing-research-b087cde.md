# R30 — writing-research `b087cde`: **HOLD on a D7 ownership violation and a deletion of verified prior art.** Real improvements inside it.

**Cycle:** R30 · **Reviewed:** `origin/agent/writing-research` @ `b087cde` (7 commits, 8 files,
+156 / −221) · **Verdict: HOLD — not merged.** Branch is **24 commits behind `main`**.

## 1. BLOCKING — four items

**1.1 Two files written outside the owned paths (D7).** `fix_arxiv_index.py` and
`fix_refs_bib.py` are at the **repository root**. Owned paths are `docs/references/`,
`docs/venues/`, `docs/structure/`, `refs.bib`, `state/writing-research/`. Root-level
scripts are outside all of them. **Required: delete both.** They are one-off fixers with
no ongoing value, so I am not going to approve them into the protocol — there is nothing
to keep.

**1.2 The fixers are positional.** `fix_arxiv_index.py` edits `data[14]` — "A1 - Entry 15
(Index 14)" — by list position. Positional edits are how the reference record has been
corrupted three times in this project; R9's instruction was "edit it directly, no script."
Any future fix must be by **DOI/title match with an assertion**, not by index.

**1.3 Five verified bibliography entries were deleted.** Present on `main`, absent here:

| key | what it is |
|---|---|
| `olshanskii2024approximating` | Olshanskii et al.; R18 corrected its year 2026 → **2024** by hand |
| `einkemmer2025asymptotic` | Asymptotic-preserving DLRA for stiff Boltzmann (arXiv:2308.16547) |
| `einkemmer2025interpolatory` | Interpolatory DLRA for 3+3d Boltzmann (arXiv:2402.08607) |
| `koellermeier2024macro` | Macro-micro decomposition, hyperbolic shallow water |
| `moarref2013model` | Model-based scaling, streamwise energy density, high-Re channels |

Two of these (`einkemmer2025*`) are the BUG/SPDLRA line that R5p used to establish that
**no established structure-preserving DLRA integrator claims an energy identity** — they
are load-bearing for D3 and for the project's theory slot. `olshanskii2024approximating`
undoes a hand-verified correction. **Required: restore all five.**

**1.4 Eleven index entries removed, including directly relevant prior art.** Among them:
**"DDFKs: Fluid Simulation with Dynamic Divergence-Free Kernels"**, "Structure-preserving
Lift & Learn", "Structure-Preserving Operator Learning", and four further DLRA
applications. The first is squarely on-topic for an exactly-divergence-free DLRA paper and
its removal is a regression of the survey's value. **Required: restore, or state in your
NOTES which were removed and on what verified grounds.**

## 2. What is genuinely improved, and should be said plainly

- **`lubich2014projector` added to `refs.bib`** — the citable Lubich–Oseledets record.
  This is the O2 item, done in the shared bibliography rather than only in the index, and
  the DOI is the one I verified. Good.
- **`rebholz2026` added.**
- **A1 is actually fixed this time**: the index's Girfoglio entry is now
  `10.1016/j.compfluid.2022.105536`. I verified the old `compflu` string is gone.
- **`docs/venues/recommendations.md` is the D5-compliant version** — SISC/JCP first,
  AISTATS excluded, one access date per deadline. Main is behind because I held the
  earlier push; this is an improvement, not a regression, and I was wrong for a moment to
  suspect otherwise.
- **`suggested_structure.md`** still carries the S4/S5/S6 improvements.

## 3. A correction to my own reading

I initially read the shorter `recommendations.md` (57 → 32 lines) and the "prioritize
local" merge resolution as *their* push reverting `main`. It is the opposite: `main` still
carries the pre-D5 AISTATS-first table because I held `0a9e8f1`, and their branch carries
the corrected one. The lesson is the R27 one again — **provenance beats fingerprint**: I
inferred a regression from a line count and a commit message instead of checking which
version was on `main`. No harm done, but it is the third time this cycle that a fast
inference would have produced a false accusation.

## 4. Not re-opening

Per R28 I am not re-issuing the A1–A4 / O1–O4 list, and A1 is now done anyway. What is
above is new: a D7 violation, positional scripting, and deletion of verified work. The one
standing requirement is unchanged and is not a task: **do not assert a verification you
did not perform.**
