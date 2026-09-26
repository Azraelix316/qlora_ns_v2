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
- **What we do not claim.** No per-step speedup: the reduced integrator is `2.08–2.71×` the full-grid
  step in every regime measured, and uses `+2.24`/`+4.27 MiB` *more* memory. **The paper says so.**

## 4. Run these three checks before you trust anything

```
python3 state/reviewer/claims_registry.py        # every load-bearing number vs an artifact key path
python3 state/reviewer/check_order_withdrawn.py  # candidates: claims later decisions withdrew
python3 -m pytest experiments/test_engine.py -q  # 40 tests, ~180 s (pin OMP/OPENBLAS/MKL=1)
```

**`claims_registry.py` currently reports one finding — the draft's `99.9%` where the runs used `99%` —
and `14/18` verified, the four failures being an artifact that has not landed.** `check_order_withdrawn.py`
is a **candidate list, not a pass/fail**: a "clean" from it means *no candidates*, not *no defects*.

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
