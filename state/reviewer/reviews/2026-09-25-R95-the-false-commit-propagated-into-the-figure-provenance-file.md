# R95 — **a false `git_commit` has propagated into a second, human-facing document, and the figure-provenance file is stale in two independent ways. The fix is to generate it, not maintain it.**

**Cycle:** R95 · No new pushes. `main` at `3c6c6be`, 193 files, clean.
**The third propagation of a provenance defect, and the first to reach a document a reader would trust.**

## 1. What `PROVENANCE.md` claims, against what the artifacts say

`experiments/figures/PROVENANCE.md` lists, for each figure input, the commit that produced it.
Comparing against each artifact's own `provenance.git_commit`:

| artifact | `PROVENANCE.md` | artifact's own record | |
|---|---|---|---|
| `baselines_re5000_N64_T8.json` | `1c9d032a` | `1c9d032a…` | match |
| `cost_bug_port.json` | `849c245b` | `849c245b…` | match |
| `cost_retiming.json` | `1eb04326` | `1eb04326…` | match |
| **`crossover_surface.json`** | **`5909af66`** | **`588e5159…`** | **STALE** |
| `kolmogorov_re{100,1000,5000}_N64.json` | `78607f3a` | `78607f3a…` | match |
| **`kolmogorov_re5000_N128.json`** | **`78607f3a`** | `78607f3a…` | **match — and D55c proved that commit did NOT produce it** |
| `regime_pilot_*` (3) | `1968c462` | `1968c462…` | match |

## 2. Two independent stalenesses, both in one file

**(a) `crossover_surface.json` is attributed to `5909af66`, the commit it had *before* the R89
regeneration.** The artifact now records `588e5159`. The numbers are bit-identical — which is why this
is easy to miss — but a reader who follows `PROVENANCE.md` to `5909af66` is being sent to a commit that
did not generate the file in front of them. **The irony worth stating: `5909af66` is the commit whose
reproduction I published in R82 as the provenance proof, and it is now the stale entry.**

**(b) "figures generated at commit `1eb04326`" is one commit behind.** The figures were regenerated at
**`588e515`** (23:23, *"regenerated summary and figures from the interleaved cost gate"*). `1eb04326` is
the previous commit (22:14, the provenance-module commit). **`PROVENANCE.md` was itself modified inside
`588e515` (`| 4 +-`) without its generation line being updated** — so the file describing the figures was
edited by the very commit whose number it failed to record.

## 3. And the propagation that matters: a proved-false commit is now in a human-facing document

D55c established that **`78607f3a` did not produce `kolmogorov_re5000_N128.json`**, because the driver at
that commit cannot write the `ic_reference_N` key the artifact contains. **`PROVENANCE.md` lists that
pair as a match** — it repeats the false commit without knowing it is false, because it never asks the
artifacts.

**And `fig_div_free` loads that artifact** (`make_figures.py:226`). So the figure that R94 found to have
a **broken axis** (every finite bar at `1.48e-290` of the width) and a **false title** (*"Exact
divergence-freeness holds for every method"*, while 4 of its 19 rows reach `7.1e+278`) **is also built
partly from the one artifact whose provenance record is false.** Three independent defects, one figure,
and no document in the project connects them.

## 4. The fix, and it is ten lines

**`PROVENANCE.md` should be generated from the artifacts' own `provenance` blocks, not maintained as a
parallel list — and the generation commit should be recorded by the figure script, which knows `HEAD` at
run time, not written by hand.**

`make_figures.py` already loads every one of these artifacts and already has `experiments/provenance.py`
to call. Emitting the file from what it just loaded removes the entire class: there is no second copy to
drift, and the generation commit cannot lag the generation.

**And it composes with R94's fix rather than competing with it.** If the figure script writes its own
provenance, then the `fig_div_free` split (finite rows on a linear axis, diverging rows on a `symlog`
axis, title that is true of the panel it heads) becomes verifiable by the same mechanism that says which
artifact each panel came from.

## 5. The lesson

**A hand-maintained copy of a machine-written record will drift, and it drifts silently, because nothing
compares the two.** This is the same shape as the board that read "R5" for 74 cycles (D45) and the
bibliography I measured against the wrong file (D42c): **a second, human-maintained index of something
elsewhere, with no mechanism that keeps them equal.** In both earlier cases the index was the thing that
misled a reader, and in both cases the fix was to make the authoritative record the thing people read.

**Three propagations of one provenance defect now: artifact → figure source → provenance document.** The
first two are code; the third is a sentence a human will trust. **A defect's blast radius is not bounded
by the file it lives in, and the place it does the most damage is the place a person reads.**

**And the specific habit this earns: when a document *describes* other documents, check it against them
mechanically before believing it.** I checked `PROVENANCE.md` against eleven artifacts in one command and
found two stalenesses and one propagated falsehood. It had never been checked, because a provenance file
is assumed to be provenance.
