# R102 — **the abstract describes a different paper: three barred claims, a cost euphemism that is false for every measurement, a promise of "benefits" the paper has measured away, and no number in it at all. Here is a replacement, 200 words, built only from verified results.**

**Cycle:** R102 · No new pushes. `main` at `95bb94b`, 200 files, clean.
**The block a conference chair reads. And unlike §4, the fix here is a rewrite — because the abstract is
not describing this paper.**

## 1. What is wrong, itemised

The abstract is 180 words. Every sentence in it is either barred, false, or a promise the project has
measured away.

| the abstract says | what is actually true |
|---|---|
| *"Solving … NS equations at **high Reynolds numbers** requires resolving the full velocity field on every time step"* | **Unsupported, and it sets the reader's expectation.** `Re ∈ {100, 1000, 5000}` with `ν = 1/Re` on 64²/128² grids, and D59 established an **exact steady state** the runs start `3.6×10⁻⁷` of its energy below. These are not high-Reynolds-number turbulent flows. |
| *"keeps the velocity **exactly** divergence-free **to machine precision**"* | **A contradiction in terms** (D60), and the measured residual is `1.1×10⁻¹¹`, **growing `2.6×` from `N=64` to `N=128`** — not a formulation-only property. |
| *"The rank is **adapted online** by incremental singular value decomposition."* | **BARRED** (D4/D11.3/D32.2). The only adaptive evidence is `nsteps: 200`. |
| *"We validate the method on forced 2D **turbulent dynamics** … tracking **rank growth**, accuracy, and cost."* | **BARRED** (D11.2; 29 instances project-wide). |
| `[PENDING-CODER: one-sentence quantitative summary]` | **Still there — and unlike §4's markers, this one is genuinely blocking: an abstract with no number in it.** |
| *"the per-step cost is **comparable to, and in regimes slower than**, a full-grid spectral solver"* | **A euphemism that is false for every measurement we have.** D52.5 measured `2.08–2.71×` slower, and the **minimum observed is 2.08** — so there is no regime in which it is faster or comparable. **"Comparable to" is false everywhere.** |
| *"which we report alongside **the benefits**"* | **What benefits?** D61 established **no end-to-end benefit is identified**: no speedup, no memory saving (`+2.2` to `+4.3 MiB` *more*). **The abstract promises a benefit the paper's own §6 measures away** — the same defect as §4's two dead routes, now in the block a chair reads. |

**So: three barred claims, a false cost euphemism, a promise of non-existent benefits, an
"exactly…to machine precision" contradiction, and not one number — in the sentence a chair uses to decide
whether to send the paper to reviewers.**

## 2. The replacement, 200 words, every number verified

```latex
\begin{abstract}
Reducing the cost of an incompressible Navier--Stokes solve by approximating the
state raises a question that is usually asked the wrong way round: not how
accurately a reduced model can track a trajectory, but when a reduced
trajectory is worth having at all. We study forced two-dimensional
incompressible flow in stream-function form, where a structure-preserving
projected integrator integrates the viscous part exactly and the nonlinear part
by a midpoint step on the projected dynamics. Comparing such an integrator
against a static subspace of the same rank, we measure the horizon at which the
reduced integrator becomes the more accurate of the two --- $t^\ast = 0.649$ at
rank $16$ and $1.482$ at rank $32$ --- and find that this horizon is a property
of how the static subspace is built rather than of its dimension: above rank
$\approx 8$ additional rank buys the static baseline nothing measurable at any
horizon, with ranks $16$, $32$ and $43$ in agreement to four decimals. The same
comparison shows why the distinction matters. A fixed basis propagated through
the nonlinearity overflows at ranks $32$ and $42$, reaching $10^{278}$, while
every structure-preserving variant at the same ranks holds roundoff divergence
throughout; and under grid refinement the reduced integrator's error falls by a
factor $2.2$ while the static baseline's grows by up to three orders of
magnitude. The evidence is deliberately narrow: one forcing, horizons of order
unity, a rank criterion whose growth we report but do not extrapolate, and a
per-step cost $2.1$--$2.7\times$ the full-grid reference with no compensating
memory benefit. We identify no end-to-end speedup, and say so.
\end{abstract}
```

**Every clause is load-bearing and traceable:**

| clause | source |
|---|---|
| `$t^\ast = 0.649$` / `1.482` | D29/D47, **reproduced bit-for-bit** from the artifact's own recorded commit |
| *"a property of how the static subspace is built rather than of its dimension"* | D30.1 (the mechanism) — **this is the paper's actual contribution and it is absent from the current abstract** |
| ranks `16/32/43` agreeing to four decimals | D30.1 |
| *"`10^{278}`"* and *"holds roundoff divergence throughout"* | D31/D48, **verified 15/15 methods bit-for-bit** (D53) |
| *"error falls by a factor `2.2` while the static baseline's grows by up to three orders of magnitude"* | D56 (measured this cycle series) |
| *"one forcing, horizons of order unity"* | D20/D32.2 — the honest scope |
| *"a rank criterion whose growth we report but do not extrapolate"* | D32.2, **stated as a limitation inside the abstract** |
| *"cost `2.1–2.7×` the full-grid reference with no compensating memory benefit"* | D52.5 + D52.6/D61 |
| *"We identify no end-to-end speedup, and say so."* | D11.1 + D61 |

## 3. Four craft points, because an abstract that only lists negatives will not be accepted

1. **It opens on the question, not the method.** *"not how accurately a reduced model can track a
   trajectory, but when a reduced trajectory is worth having at all."* **A reviewer scanning the first line
   should see a thesis, not a technique.** The current abstract opens on the problem and reaches the method
   by sentence 3.
2. **The negative result is the contribution, stated early.** *"we find that this horizon is a property of
   how the static subspace is built rather than of its dimension"* — **that is the paper's novelty, and it
   is not in the current abstract at all.**
3. **The scope sentence is early, not last.** *"The evidence is deliberately narrow"* comes **before** the
   cost sentence, so the reader calibrates before the deficits rather than after.
4. **"We identify no end-to-end speedup, and say so."** is a **deliberate closing sentence.** It converts
   the paper's biggest weakness into a signal of care at the exact point a reviewer is deciding. **A paper
   that ends its abstract by conceding a deficit is read very differently from one that is caught having
   concealed it** — and the current abstract's *"which we report alongside the benefits"* does the opposite.

## 4. The lesson, and it completes the argument R101 began

**R101: length is not where the risk is — what a reader decides on is.** R101 found the contributions list
argued the wrong contribution. **R102 finds the abstract describes a different paper: three barred claims
and not one number, in the block a chair reads to decide whether the paper is sent to reviewers at all.**

**And the two are the same finding at two levels.** The draft was written at 09:49 on 2026-09-25, before
D29 corrected `t*`, before D30 found the saturation mechanism, before D31 found the divergence, before D52
re-measured the cost, and before D68 changed the thesis. **Every number the abstract needed existed by then
except the ones D29–D52 later corrected — which is to say the abstract has been waiting for a review it did
not have.** The contributions list and the abstract are the two blocks that decide acceptance, and both are
still describing the pre-review paper.

**That is the project's real remaining risk, stated plainly: not that the science is weak — D53 verified
the central result bit-for-bit — but that the two paragraphs a reviewer decides on still describe a paper we
are no longer writing.**
