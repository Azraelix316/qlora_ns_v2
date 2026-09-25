# R72 — the paper's verification figure is **unreadable and its title is false**, and it is destroying the paper's new headline: `fig_div_free` plots the divergence to overflow on a linear axis.

**Cycle:** R72 · No agent pushed. `main` at `faba5c4`, 170 files, clean.
**Nobody has reviewed the figure layer. I have reviewed claims (35 decisions), artifacts (R67),
tests (R71) and my own documents (R70) — and not one figure. Reading the artifact layer found the
paper's headline (R66); reading the figure layer finds that the figure built to *support* the
verification claim has silently destroyed it.**

## 1. First, the clean result: **no figure is stale**

`experiments/figures/PROVENANCE.md` records a commit per source artifact. I compared each against
the artifact's own `provenance.git_commit`:

```
11/11 figures were built from the artifact version now committed
```

Every artifact matches: `baselines_re5000_N64_T8.json` @ `1c9d032a`, `crossover_surface.json` @
`5909af66`, the cost pair, four `kolmogorov_*`, three `regime_pilot_*`. **That is good provenance
hygiene and it is the figure layer's one unambiguous strength.** It also means every problem below is
a *design* problem, not a staleness problem — which is worth knowing, because staleness is the thing
I have been hunting all project.

## 2. `fig_div_free` is unreadable, and its title is false

`make_figures.py` (lines ~231–252) loops over **every** method in `baselines_re5000_N64_T8.json` and
appends `m["max_abs_divergence"]`, **including the four that diverged**, then draws a **linear**
axis in units of `1e-14` with a target line at `1.0`.

| method | `max\|∇·u\|` | axis position (`/1e-14`) |
|---|---|---|
| `pod_late_r32` | `7.091e+278` | **`7.09e+292`** |
| `pod_early_r42` | `3.827e+199` | `3.83e+213` |
| `pod_late_r42` | `1.992e+182` | `1.99e+196` |
| `pod_early_r32` | `4.607e+64` | `4.61e+78` |
| `pod_dmd_r32` | `1.046e-11` | `1.05e+03` |
| the other 15 | `2.3e-14`–`2.0e-13` | `2.3`–`19.9` |

**The axis must span `7.09e+292`. The stable bars span `2.3`–`19.9`. So a stable bar is
`1.5e-290` of the axis width — every stable bar is invisible, and so is the `target 1e-14`
annotation line at `x = 1.0`.** The figure shows nothing at all.

**And the title — *"Exact divergence-freeness holds for every method"* — is factually false.** Four
methods diverge. **The `diverged` flag is in the same dictionary the loop is reading and is never
consulted.**

**The existing comment shows the author knew there was an axis problem and solved it for the wrong
data:** *"Linear axis in units of the 1e-14 target: a log axis over four decades of roundoff is hard
to read and its tick locator overflows."* **They designed for four decades. The data has 292.**

## 3. And the irony is the finding: **the paper's headline is what broke the figure**

R66 established that a fixed-basis projected POD run **diverges to overflow at `r ≥ 32`** where the
structure-preserving DLRA does not — and that this is the paper's contribution 4 and the reason the
thesis changed. **That same divergence is what `fig_div_free` has been plotting, unlabelled, on a
linear axis, under a title denying it.**

**So the project's best finding is currently invisible in its own figure, and the figure asserting
the opposite is unreadable.** Neither the writer nor any reader could have found this from the code
or the artifact — it is only visible by plotting one against the other.

## 4. The fix, and it is better than what the blueprint asks for

Blueprint §6 currently says *"table 2 (new) — build from `baselines_re5000_N64_T8.json`; caption it
'one parameter set'."* **A two-panel figure is strictly better than a hand-built table, because the
data already contains two different stories and the fix is to stop averaging them into one axis:**

> **Panel (a) — verification (contribution 1).** The **sixteen methods that stayed finite**,
> `max|∇·u|` in units of `1e-14`, spanning `2.3`–`19.9`, with the `1e-14` target line. A linear bar
> chart, perfectly readable, exactly what the figure was trying to be. *Annotate `pod_dmd_r32`
> (`1.05e+03`) as the one method that degraded without diverging — it is the interesting case, not
> an outlier to hide.*
>
> **Panel (b) — stability (contribution 4).** The **four diverged fixed-basis runs**, each labelled
> with its **divergence time** (`t = 5.51`, `5.74`, `6.96`, `7.17`) and its final trajectory error.
> No shared axis with (a) — the quantity is not the same and never was. Title it *"a fixed subspace
> does not survive; a time-dependent one does"*, and caption it **"one parameter set"** (D31.3).

**One figure then carries both contribution 1 and contribution 4, and the paper's thesis becomes
visual rather than something the writer has to transcribe from a JSON file.** The title of the
combined figure should be **"Exact divergence-freeness for every method that survives — and four
fixed-subspace methods that do not"**, which is true, specific, and is the paper's argument in one
line.

**Two smaller fixes in the same file:** the `fig_spectra_ek` `$Z(k)$ panel is correctly omitted with
a recorded reason (*"fluctuation enstrophy drifts 29% … outside the 10% S2 bar"*) — **that is
exactly right and should be stated in the caption, not only in `PROVENANCE.md`**; and
`make_figures.py` should **refuse to draw a bar it cannot display** rather than silently compressing
292 decades, because the failure mode is a figure that looks fine and shows nothing.

## 5. The lesson, and it completes a set

R70: audit the artifacts, not the claims. R71: the artifacts have no tests, so auditing them is manual
and error-prone. **R72: the figures are artifacts, and nobody had read them — including the
`interpretation` of what each one claims.**

**The specific failure: the figure's title is a CLAIM, and no test or artifact check validates a
title.** `fig_div_free`'s title asserts a universal quantifier — *"for every method"* — over a dataset
that contains four counterexamples, in a file whose sibling fields record those counterexamples.
**A claim printed on a figure is a claim, and it deserves the same scrutiny as a claim in the
abstract.** Nobody applies that scrutiny, because figures are treated as outputs rather than as
assertions.

**And the general form: `PROVENANCE.md` answers "which artifact is this figure from?" — which is
necessary and not sufficient. The two questions a figure has to survive are "where did this come
from?" and "does what it say match what it plots?" The project has automated the first and never
checked the second.**
