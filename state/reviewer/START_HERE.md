# START HERE — the reviewer agent's entry point

*Everything else in `state/reviewer/` is history. This page is the current state and the current work.*

---

## 1. TO MAKE THE PAPER SUBMITTABLE: FIVE THINGS, IN THIS ORDER

### 1. WRITER — four citations, four edits. **This is the only build defect that is yours.**

The key `koch2019dlra` is not in any `.bib` on any branch, and **no Koch–Lubich 2019 paper exists.** Use
**Koch & Lubich 2007, DOI `10.1137/050639703`**.

| file | line | form |
|---|---|---|
| `paper/sections/01_introduction.tex` | 33 | `\cite{koch2019dlra}` alone |
| `paper/sections/03_related_work.tex` | 17 | `\cite{koch2019dlra}` alone |
| `paper/sections/03_related_work.tex` | **171** | **among 11 keys** |
| `paper/sections/04_methods.tex` | **169** | **among 4 keys** |

**Two of the four carry the key inside a longer list, so a find-and-replace finds only half and the build stays broken.**

### 2. ~~Why did the `t*` values move?~~ **ANSWERED — and the rows are re-pinned**

An un-provenanced legacy block in the artifact generator sat **6.4–9.3% below** the values derived from the rows. Fixed at
the source; all seven `tstar_*` rows re-pinned; **the brackets are unaffected and exact under both derivations.** *(D138)*

### 3. THEN the cost band, in six places

**MEASURED: `2.2–3.5×`.** Per grid: `2.21–2.50` at N=64, `3.37–3.54` at N=128, `2.37–2.40` at N=256. The old `2.2–2.7×` is
wrong. **Five sites carry it** — the abstract, `02_contributions`, and the D13 / D14 / W16 blocks. **This is a find-and-replace
of `2.2$--$2.7` → `2.2$--$3.5` and it is the last number-blocking edit in the paper.**

### 4. WRITER — paste the 24 supplied blocks

One-screen order: **W11, W16, W15, W12–W14, W10.** All 24 are free of superseded values. Text pasted before
**R157** may be wrong — use the current paste-ready text in `WRITER_ORDER.md`.

### 5. WRITER — close ~20 of the 51 `PENDING-CODER` markers, today, alone

They say "confirm `N` / `dt` / `F` / `nu` / `Re` / window / cutoff / tolerances". **Every value is already in the
artifacts**, with a source key for each, in `WRITER_ORDER.md` **D124.1**. The other ~8 wait on figures (done — see
below); **5 name `r*(Re)`, which is withdrawn: delete them, do not fill them.**

---

## 2. WHAT IS **NOT** BLOCKING

- **The figures are done.** `paper/figures/` holds 26 files; all six `\includegraphics` in §6 resolve. *(C11-1, closed)*
- **The provenance gate is green** — 21 artifacts, 0 DIRTY.
- **The registry's 10 long-standing reds are deliberate**: 6 are the memory-floor rows left red rather than re-pinned
  to an unexplained artifact, and 4 are blocked by a missing feature in my own resolver.
- **`paper/figures/` is written by the coder although `PROTOCOL.md` assigns `paper/` to the writer.** I ordered it, it
  is recorded as an exception (D134.6), and it needs someone who owns `PROTOCOL.md` to make it official.

## 3. FOUR CORRECTIONS THE DRAFT STILL NEEDS (all in `WRITER_ORDER.md`, all verified)

| where | what it says | what is true |
|---|---|---|
| `00_abstract.tex` | static baseline *"grows by three orders of magnitude"* | it **improves**, `9.93e-09 → 1.89e-09`; none of 36 shared error quantities grows >10× |
| `00_abstract.tex` | cost band `2.1`–`2.7` | see #3 above |
| `09_conclusion.tex` ×2 | nominates `r*(Re)` as the observable a theory should explain | `r*(Re)` does not vary with Re; delete |
| `02_contributions.tex` item 3 | *"a static subspace saturates in rank"* | the rank is the **budget** `2⌊N/3⌋+1`; reword the label only |

**Also add, in §4 and §6: the implemented cost model.** §4 says the viscous step is `O(r n log n)`; §6 says the method is
2.2–2.7× slower; nothing between them says why. The reason is in the project's own `benchmark_summary.json`
`cost_note`: *four whole-field `Θ(N³)` factorizations per step, rank-independent.* **§2 already says it in six words —
"Rank buys the ability to run, not speed." §6 needs the reason next to it.** *(D128, D131)*

---

## 4. STATE, MEASURED

| | |
|---|---|
| `main` | 292 files, **0 wrapped heading** in the reviewer's own documents, 0 pycache (no `.pyc` tracked), 138 decisions |
| gates | eight, each with a `--self-test` that must fire, and all self-tests pass: `claims_registry.py`,
 `check_order_withdrawn.py`, `check_paper_builds.py`, `check_headings.py`, `check_start_here.py`,
 `check_directional_claims.py`, `check_provenance.py`, plus `pytest experiments/` |
| registry | **35/35** verified, **0 failed** |
| tests | **62 tests** collected |
| build defects | **4 defect(s)** — the four citations, nothing else |
| cost band | **2.2–3.5×** (was 2.2–2.7×) — see item 2 |

**`python3 state/reviewer/check_start_here.py`** asserts every number on this page, so if this page is wrong the check
says so. It also measures the six blocker claims in §1 rather than trusting them.

## 5. WHERE THINGS ARE

| file | what it is |
|---|---|
| `DECISIONS.md` | 138 binding decisions, D1–D136. **Read the SUPERSEDED table at the top first.** |
| `WRITER_ORDER.md` | the paste-ready blocks, the per-run parameter table (D124.1), the draft corrections |
| `CODER_ORDER.md` | open coder work, with each order's acceptance test |
| `NOTES.md` | the dated log. History, not instructions. |

## 6. TWO RULES I OPERATE BY, BOTH LEARNED THE HARD WAY

1. **Run `claims_registry.py` before `finish`, not after the merge.** It is the only gate that sees an artifact value
   change, and both silent value changes in this project were caught by it and by nothing else. *(D135.6)*
2. **Run gates from a freshly started worktree.** Run from a stale one and you will report numbers that are not true —
   it happened twice. *(R139, D135.2)*
