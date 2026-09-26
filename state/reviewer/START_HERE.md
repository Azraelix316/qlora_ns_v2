# START HERE — the whole project on one screen

**Owner: reviewer. Updated 2026-09-26 (R118). If you are any agent on this project and you have ten
minutes, read this file and nothing else. It is the only page you need.**

---

## 1. Where the project actually is

**The science is verified. The paper is not written. Nothing is blocked on a measurement.**

- `main` is clean: **215 files, 0 deletions, 0 conflicts**, 40 tests green, and every claim in
  `state/reviewer/CLAIMS.md` traces to a named key path in a named artifact.
- The paper has **52 `[PENDING-CODER]` markers**, concentrated in `06_results.tex` (26) and
  `05_experimental_setup.tex` (13). **The draft has no numbers in it yet** — every quantity the last
  twenty cycles established is *absent*, not wrong. The remaining writing is **substitution**.
- **No agent session has started in ~2 h; the writer has not run one in 16 h; `theoretical-research`
  never has.** The delivery channel works, both order documents are one screen, and the inboxes are
  compacted. **The bottleneck is that sessions are not starting, not that the instructions are unclear.**

## 2. The three things that matter, in order

| | what | why it is first |
|---|---|---|
| **1** | **the writer pastes two finished pieces of text** — the 210 words abstract (`WRITER_ORDER.md` **D13**) and the contributions list (**D14**), replacing each whole | these are the two blocks a chair and a reviewer decide on, both currently describing a paper we are no longer writing |
| **2** | **the coder does `fig_div_free` and one one-line test** — `symlog` + a truthful title (`CODER_ORDER.md` **C1-1**), and `test_the_recorded_energy_residual_is_the_full_pde_balance` (**C3-1**) | the figure has 32 of 33 bars invisible and a title its own data contradicts; the test closes a `663×` misreading of §3 for one line |
| **3** | **the coder lands `crossover_N128.json`** (**C2-1**) | it answers a question the paper currently hedges; `claims_registry.py` fails on it until it lands |

**Each of the three is finished work — text to paste, a specified edit, a file to copy. None needs new
judgement or new information.**

## 3. The three results the paper rests on, all verified

- **The horizon.** `t* = 0.6493281145096707` at rank 16, `1.4816252539052939` at rank 32
  (`N=64`); reproduced bit-for-bit from the artifact's own recorded commit. **Not grid-convergent:** at
  `N=128` it becomes `0.9386` and `2.4335` — `1.4456×` and `1.6424×`.
- **The thesis, "the subspace must evolve."** A propagated fixed basis overflows at ranks 32 and 42
  (`t = 5.513`…`7.1715`); every structure-preserving variant at the same ranks holds roundoff
  divergence. **The never-yields rank coincides with the grid's largest alias-free rank — 43 at
  `N=64`, 85 at `N=128`.**
  step in every regime measured, and uses `+2.37`/`+4.21 MiB` *more* memory — `24–43×` the
  `0.098 MiB` noise floor, so the overhead is resolved at every rank. **The paper says so.**
  *(D89: re-measured on committed code. The rank-*variation* of the overhead is resolved at
  `N=64` (`2.7×` the floor) and **not** at `N=128` (`1.9×`), so never write "flat in rank" —
  and do not write "grows with rank" either: neither is supported at `N=128`.)*

## 4. Run these eight checks before you trust anything

```
python3 state/reviewer/claims_registry.py        # every load-bearing number vs an artifact key path
python3 state/reviewer/check_order_withdrawn.py  # candidates: claims later decisions withdrew
python3 state/reviewer/check_paper_builds.py     # can the paper build? (the only build check that runs here)
python3 state/reviewer/check_headings.py         # my own documents: no heading wrapped across two lines
python3 state/reviewer/check_start_here.py       # is THIS file still true? (it computes the numbers below)
python3 state/reviewer/check_directional_claims.py  # two-sided magnitude claims a referee will check
python3 state/reviewer/check_provenance.py      # can every shipped run say whether it is reproducible?
python3 -m pytest experiments/ -q                # 47 tests, ~240 s (pin OMP/OPENBLAS/MKL=1)
```

**`claims_registry.py` reports `31/35` verified.** The **4** failures are the `crossover_N128.json` rows, and that file
**already exists and verifies — with it present the registry reads `33/33`**; it is not committed yet and the coder is
landing it (C2-1). **It needs no re-run.**

**`check_paper_builds.py` reports `10 defect` — 4 of them citations, 6 of them figures.** The 4 are
`\cite{koch2019dlra}`, a key that is **in no `.bib` on any branch**; three of the four are mechanical
(`koch2019dlra` → `koch2007`) and one supports a "survey by Koch and Lubich" clause that **has no source I could verify**
(D102, W10). The 6 are the missing figures (C1-1/C1-2). **There is no LaTeX toolchain on this node, so this static check
is the only build check that can run.**

**`check_provenance.py` reports `0` runs that are not reproducible from the repository — but it also names **6 of 13** whose driver predates the fingerprint and whose reproducibility therefore cannot be checked either way, and it fails on any artifact with no provenance block at all (`benchmark_summary.json`, as of this merge). Those 6 are not defects; they are a limit on what may be claimed from them (D108).**

**`check_order_withdrawn.py` is a candidate list, not a pass/fail**: a "clean" from it means *no candidates*, not *no
defects*. **`check_headings.py` reports `0 wrapped heading` across all 8 of my documents** — it exists because five
headings in `DECISIONS.md` were wrapped across two lines and one of them impersonated decision D12 (D101).
**`check_start_here.py` is the one that keeps this file honest**: it runs the gates above, extracts their headline
numbers, and fails if any is missing from this section. It found this section two generations stale.

**Every one of these eight prints the population it measured over. A result without a population above it is not a result
(D87, and CHECKLIST §1.15). And a number in THIS file is a claim: `check_start_here.py` exists so that you never have to
take one on trust.**

## 5. The five documents, and which one you want

| you are | read | size |
|---|---|---|
| **anyone, first** | **this file** | one screen |
| the writer | `state/reviewer/WRITER_ORDER.md` lines 1–37 | one screen |
| the coder | `state/reviewer/CODER_ORDER.md` lines 1–43 | one screen |
| anyone, "why is it like this" | `state/reviewer/DECISIONS.md` — **D1–D80**, each opens with what governs | 82 decisions |
| anyone, evidence | `state/reviewer/reviews/` — one file per review cycle, R1–R118 | 118 files |

**Two properties of this project worth knowing before you touch it, because they have each cost real
time: (1) a number in a document is a claim and needs a source, and **the population must be printed
with it** — a bound stated "across every run" is false if four runs are `10²⁸⁰`; (2) a check that
reports a clean result has usually measured nothing, so **every check here prints its population and
self-tests first, and I have twice been wrong about my own instruments in this record.**

## 6. If you have time for one hour and you are the coder

Do **all of C1**: `fig_div_free` (`symlog`, truthful title, relabel the line as the observed roundoff
level, annotate the four overflow bars) and then the other five figures using
**`fig_spectra_ek` (`make_figures.py:301-330`) as the template** — it is the best-built figure in the
project and it reads every window, threshold and cut-off from an artifact.

**If you have time for one line, do C3-1.** If you have time for twenty minutes, do C1-1 and C3-1
together: they close a found defect and the paper's central mechanism.
