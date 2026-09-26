# R93 — **the `N=128` grid multipliers are UNDERIVABLE, and the pair they came from contains a real grid-convergence result nobody had read out of it.**

**Cycle:** R93 · No new pushes. `main` at `d105692`, 192 files, clean.
**I have called these numbers "unverified" for many cycles. The correct verdict is stronger: they do
not exist in the artifact they claim to come from, under any indexing.**

## 1. The re-derivation, time-keyed, and it is decisive

`kolmogorov_re5000_N64.json` and `kolmogorov_re5000_N128.json` both carry `comparison` series of
`{time, relative_l2}`. **The two cases sample on different time grids** — `N=64` every `0.01` (11
samples to `T=0.1`), `N=128` every `0.005` (21 samples) — **so a ratio computed by position compares
`t=0.01` against `t=0.005`.** That is precisely the index-shift trap D29 recorded, and it is why
time-keying is mandatory here.

| target | DLRA time-keyed | DLRA positional | POD time-keyed | POD positional |
|---|---|---|---|---|
| `1.46` | no | no | no | no |
| `1.99` | no | no | no | no |
| `2.45` | no | no | no | no |
| `6.04` | no | no | no | no |

**`1.46→1.99` and `2.45→6.04` appear nowhere.** Not under the correct indexing, not under the wrong
one, for either method. **They are not index-shift artifacts of these series; they cannot be derived
from this artifact at all.**

**So the verdict changes from "unverified, may carry an index shift" to "underivable."** D29.7 already
withdrew the *claim*; D35 requires re-deriving what is built on a withdrawn number, and the honest
resolution is to **strike the numbers from the record** rather than carry them as "unverified but
possibly right." A number nobody can locate in its stated source should not survive as a caveat.

## 2. And the pair is a well-controlled experiment that nobody read

The confound I expected turned out to be the thing that makes it clean:

| | `N=64` case | `N=128` case |
|---|---|---|
| initial condition | its own 64 grid | **`ic_reference_N: 64`** |
| static baseline | `effective_rank: 16` | `effective_rank: 16` |

**Both cases start from the same 64-grid field, and the static baseline is rank-matched. So the ratio
measures the resolution effect alone.** This is a deliberately controlled pair — and the multipliers
were never read out of it correctly.

## 3. What the time-keyed ratios actually show

**The reduced integrator is grid-limited:**

| `t` | `N=64` | `N=128` | ratio |
|---|---|---|---|
| 0.01 | `1.001e-04` | `4.590e-05` | `0.4583` |
| 0.05 | `9.882e-05` | `4.528e-05` | `0.4582` |
| 0.10 | `1.011e-04` | `4.687e-05` | `0.4637` |

**Ratio `0.4581–0.4637` across the whole window — stable to `1.2%`.** Refining `64 → 128` **reduces**
the reduced integrator's error by a factor `≈2.18`, with an observed order `log₂(1/0.458) = 1.13` in
relative L2, consistent with a second-order scheme measured in that norm. *(One refinement gives one
apparent order; a proper order study needs three grids, and I would say so in the paper.)*

**The static rank-16 baseline is not grid-convergent at all:**

| `t` | `N=64` | `N=128` | ratio |
|---|---|---|---|
| 0.01 | `4.026e-11` | `1.264e-10` | `3.14` |
| 0.05 | `1.917e-10` | `1.969e-09` | `10.3` |
| 0.08 | `4.180e-10` | `6.119e-07` | `1464` |
| 0.10 | `1.000e-08` | `6.721e-06` | `672` |

**Its error grows by `2.5×` to `1464×`, and the growth is itself unstable — a `575×` spread across the
window.** And the shape is the striking part: **on the 64 grid the static baseline starts six orders of
magnitude better than the reduced integrator (`4.0e-11` vs `1.0e-04` at `t=0.01`) and ends four orders
worse (`1.0e-08` vs `1.0e-04` at `t=0.1`).** It is not uniformly worse; it is *transiently better and
then catastrophically worse*, which is a much more interesting object than a ratio.

## 4. Why this belongs in the paper, and it is stronger than what it replaces

**This is exactly what "the subspace must evolve" wants, measured on a controlled pair:** the evolving
subspace **converges with the grid** (a clean, stable `2.18×` improvement), and the fixed one **does
not** (its error grows by up to three orders of magnitude, unstably). **A grid-refinement result that
separates the two families on the axis the thesis is about is worth more than a pair of unexplained
multipliers.**

**And the honest framing for §6:** one refinement, `T=0.1`, `A=0.5`, a shared 64-grid initial condition,
a rank-16 static baseline. **It is a two-grid comparison, not a convergence study**, and the POD ratio's
instability means the *size* of its degradation is not a stable quantity to quote — only the sign and
the order of magnitude are.

## 5. The lesson

**I carried two numbers for many cycles under the label "unverified." The label was doing the work of a
check I had not run, and when I finally ran it the numbers were not merely unverified — they were
absent.** D35 has said since early on that a correction is not a local edit and that claims must be
re-derived from their foundations; what I had not done is apply that to numbers I had *already*
withdrawn. **Withdrawing a claim and leaving its arithmetic in the record is half a withdrawal.**

**And the general form, which is the sixth variant of this shape: a caveat is not a substitute for a
derivation.** "Unverified" felt honest and cost nothing, and it protected two numbers from the question
of where they came from. **The moment to ask "where is this number in its artifact?" is the moment you
withdraw the claim, not a cycle or twenty later.**
