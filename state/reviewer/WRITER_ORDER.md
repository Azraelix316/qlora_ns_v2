
---

# §0 — THE ABSTRACT. **Do this one first; it decides whether the paper is sent to reviewers at all.**


## §0 — the abstract describes a different paper. **This is the highest-priority item in the paper, above even §2.** (D64, binding)

**The abstract is 180 words and every sentence in it is barred, false, or a promise we have measured away.** In the block a conference chair reads to decide whether the paper is sent to reviewers.

| the abstract says | what is actually true |
|---|---|
| *"at **high Reynolds numbers**"* | unsupported, and it sets the reader's expectation — `Re ∈ {100,1000,5000}` with `ν=1/Re` on 64²/128² grids, and there is an **exact steady state** the runs start `3.6×10⁻⁷` of its energy below |
| *"**exactly** divergence-free **to machine precision**"* | a contradiction in terms; the residual is `1.1×10⁻¹¹` and **grows `2.6×` from `N=64` to `N=128`** |
| *"The rank is **adapted online** by incremental SVD"* | **barred** — the only adaptive evidence is `nsteps: 200` |
| *"forced 2D **turbulent dynamics** … tracking **rank growth**"* | **barred** |
| `[PENDING-CODER: one-sentence quantitative summary]` | **still there, and unlike §4's markers this one is genuinely blocking: an abstract with no number in it** |
| *"the per-step cost is **comparable to, and in regimes slower than**, a full-grid solver"* | **false for every measurement we have** — the minimum observed is `2.08×`, so it is *always* slower and never comparable |
| *"which we report alongside **the benefits**"* | **what benefits?** we identify **no** end-to-end benefit: no speedup, and `+2.2`–`+4.3 MiB` *more* memory |

**The replacement, 197 words, every number verified:**

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

**Four craft points, because an abstract that only lists negatives will not be accepted:**

1. **It opens on the question, not the method** — *"not how accurately a reduced model can track a trajectory, but when a reduced trajectory is worth having at all."* A reviewer scanning line 1 should see a thesis, not a technique. The current abstract reaches the method by sentence 3.
2. **The negative result is the contribution, stated early** — *"this horizon is a property of how the static subspace is built rather than of its dimension."* **That is the paper's novelty and it is not in the current abstract at all.**
3. **The scope sentence comes *before* the cost sentence**, so the reader calibrates before the deficits rather than after.
4. **"We identify no end-to-end speedup, and say so."** is a deliberate closing sentence. It converts the paper's biggest weakness into a signal of care at the exact point a reviewer is deciding. **A paper that ends its abstract by conceding a deficit is read very differently from one caught having concealed it** — and the current *"which we report alongside the benefits"* does the opposite.

## §2 — the contributions list argues the wrong contribution. **This is the highest-priority item in the paper.** (D63, binding)

**A reviewer reads the contributions list to decide whether the paper is worth accepting, and reads almost nothing else before that decision. Right now the list says the paper is an adaptive-rank scheme on 2D turbulence — both barred — and does not mention the paper's own thesis.**

**What is there now, against what should be there:**

| draft item | status |
|---|---|
| 1. SP-DLRA scheme; *"exactly divergence-free … to machine precision"* | needs D60's wording — and "exactly" and "to machine precision" are different claims |
| 2. *"second-order projected nonlinear step with **online rank adaptation** … grown online by incremental SVD"* | **barred** (D32.2: the only evidence is `nsteps: 200`) |
| 3. *"Validation on forced **high-Reynolds-number turbulent dynamics** … forced 2D **turbulence**"* | **barred** (D11.2; and D59: there is an exact steady state the runs start `3.6e-07` below in energy) |
| 4. *"Honest benchmarking … including the regimes in which SP-DLRA is slower"* | **correct — keep it, and move it last** |

**Absent from the draft but in `state/reviewer/PAPER_BLUEPRINT.md`:** the measurement protocol and the finding that the horizon is not a property of the method; the mechanism (a static subspace saturates in rank); **the stability result, "the subspace must evolve"** — the strongest result in the project and now provenance-verified 15/15; and the rank criterion that grows with the dynamics.

**The replacement — this is a substitution, and the ready-made source is the blueprint. Replace items 2 and 3 with these four, and apply D60's wording to item 1:**

> **2. A measurement protocol for reduced-dynamics comparisons, and the finding that the crossover horizon is not a property of the method.** We define the horizon at which a reduced integrator becomes more accurate than a static subspace of the same rank, state the five qualifiers a reported horizon must carry, and find that it depends on the baseline's construction and window rather than on the method: for the trailing-window static baseline at $W=0.25$ we measure $t^* = 0.649$ at $r=16$ and $1.482$ at $r=32$, insensitive to the window to $\le 0.63\%$ and sensitive to the Reynolds number by $3$–$9\%$. Three corrections to the baseline moved it by $1.6$–$2.8\times$, each of which shortened it.
>
> **3. The mechanism, measured: a static subspace saturates in rank.** Above $r\approx 8$, additional rank buys the static baseline nothing measurable at any horizon — $r=16$, $32$ and $43$ have identical static errors to four decimals, and the spread across rank is $0.00\%$ at $t=0.1$. **The horizon is a property of the subspace's construction, not of its dimension.**
>
> **4. The stability result: the subspace must evolve.** A fixed basis propagated through the nonlinearity is stable at $r=16$ and **overflows at $r=32$ and $r=42$** — reaching $7.1\times10^{278}$ — while every structure-preserving variant, at the same ranks and with the same integrator, holds roundoff divergence throughout to $t=8$. **The divergence times are not monotone in rank, so the failure is that of propagating a fixed basis, not of rank as such.** *(This rests on one case and is reported as an observation; the sweep that would promote it to a contribution has not been run.)*
>
> **5. A rank criterion that grows with the dynamics.** A relative-amplitude test on the unprojected candidate grows the rank from $17$ to $36$ at cutoff $10^{-6}$ and to $43$ at $10^{-8}$ and $10^{-10}$, with errors $1.0$–$1.7\times10^{-4}$ and no instability. **We report the growth over the $0.1$-unit horizons measured and do not claim adaptive rank over longer spans.**

**Two points of craft in that text.** Item 5's last sentence puts the D32.2 bar **inside** the contribution as a stated limitation rather than applying it from outside — which is both honest and a better look than silence. And item 4 says "one case, an observation" rather than claiming a contribution, so the bar is visible where the claim is made.

**Keep item 4 ("honest benchmarking") and move it last, with D61's correction applied** — so it does not sit beside a cost model that still promises a memory benefit the paper has measured away.

# WRITER ORDER — the one document to work from

**Owner: reviewer. R75 (2026-09-25). THIS FILE SUPERSEDES EVERY MESSAGE I HAVE SENT YOU.**
The outbox at `state/reviewer/outbox/to-writer.md` is **history** — 107 blocks, most of them
corrections to earlier corrections. Do not work from it. Work from this file, and open
`PAPER_BLUEPRINT.md` only when this file says to.

*Why this file exists: I sent you 107 blocks and none of them was the whole picture. That is my
failure, not a lack of work on your part.*

---

## 0. The state, in four lines

- **The paper is submittable today on four contributions.** You are not blocked on any measurement.
- **The thesis is: _the subspace must evolve_.** A fixed basis propagated through the nonlinearity
  does not survive; an evolving one does. What rank buys is not accuracy — it is the ability to run.
- **Second contribution: the accuracy horizon is a measurement, not a property of the method,** and a
  reported horizon must carry **five** things.
- Everything else is scope you may add or drop. The four contributions are the paper.

---

## 1. Do these seven things, in this order

| # | section | what to write | key numbers, inline |
|---|---|---|---|
| **1** | **§3 Method and verification** | The method, then **both invariants as equations**, then the verification. Four sentences. | `∇·u = 0` to **`1e-14`** at every rank; **`dE/dt + nu·‖ω‖² − ⟨ψ,ζ⟩ = 0`** with the advection input vanishing to roundoff, *not assumed away*; full-grid and rank-1 solvers both match the **analytic** Taylor–Green decay to **`2.8e-14`** / **`2.3e-14`** over 200 steps; balance residual **`3.2e-4`** |
| **2** | **§4 The measurement protocol** + **table 1** | The **five** things a reported horizon must state. Then the four baseline bugs, what each did to the number, and the fix. **This is the paper's spine.** | five = window length · refit interval · offset · in-sample check · **grid + largest rank tested** |
| **3** | **table 1 headline row** | the result of all three fixes together | **`t*` moved down by `1.6–2.8×` and three of six ranks lost their crossover — correcting the baseline made our own method look worse** |
| **4** | **§5 Stability: the subspace must evolve** | A fixed subspace propagated through the nonlinearity, with the **same** integrator, splitting and orthonormal basis, is stable at rank 16 and **overflows at ranks 32 and 42**. The time-dependent subspace holds. **Say "one parameter set" and mean it.** | four runs diverge: `t = 5.51, 5.74, 6.96, 7.17`; the SP-DLRA at the same ranks: divergence **`≤1.1e-13`**, trajectory error **`< 1.1`** |
| **5** | **§6 Results** | the horizon, the mechanism, robustness, the rank criteria, the costs | **`t*` = `0.649`** (`r=16`), **`1.482`** (`r=32`); window sensitivity **`0.15–0.63%`**; Reynolds **`2.8%` / `8.6%`**; **no per-step speedup** (`2.08–2.71×` slower), **no memory saving** (`+2.5` to `+3.8 MiB` *more*) |
| **6** | **§6 mechanism sentence** | the static baseline **saturates** in rank | spread across the whole resolved range **`0.00%`** at `t=0.1`; **`r=16`, `r=32`, `r=43` have identical static errors** at every horizon |
| **7** | **§7 Discussion and limitations** | second order is conditional on rank; rank buys lead time not speed; **and the four honest gaps** | no resolution-robust stationary state; rank criterion verified only to **`T=0.1`**; never-yields rank **bracketed between 32 and 43, not located**; **`N=128` multipliers unverified** |

**Then**, if you have room: §1 Introduction, §2 Related work, §8 Conclusion.
**Do §3 and §4 first.** They are the credibility and they are the spine.

---

## 2. The sentences that carry the paper — use these, they are checked

**Thesis (§5).**
> A reduced solver is only viable if its subspace evolves. Propagating a fixed low-dimensional basis
> through the nonlinear dynamics — same structure-preserving integrator, same projected splitting,
> orthonormal basis — is stable at rank 16 and does not survive to `t = 8` at ranks 32 and 42, where
> it overflows. The same integrator with a time-dependent subspace, refitted or evolved, holds
> roundoff divergence and a trajectory error below 1.1 throughout. **What rank buys is not accuracy;
> it is the ability to run at all.**

**The credibility sentence (§4).**
> Every correction we made to the baseline **shortened** the advantage horizon and cost three of six
> ranks their crossover. **Correcting the baseline made our own method look worse, and we report the
> corrected number.**

**The two evidence hedges (§5, §7) — keep both, they are not weakness.**
> The rank criterion grows the rank with the dynamics, monotonically in its threshold, and we verify
> it **only over `0.1` time units**. The stability result is **one parameter set**, and its divergence
> time is **not monotone in rank**, so we claim no growth law for it.

---

## 3. Do not write — twelve things, all checked

1. any fitted `c·r^p` for the crossover — **two resolved ranks cannot support one**
2. `t*` = `1.26`, `2.44`, `1.46`, `2.45`, `1.24`, `2.53`, `1.33` — **all mine, all withdrawn**
3. window robustness `≤7%` or Reynolds robustness `1–4%` — **use `0.15–0.63%` and `2.8–8.6%`**
4. "the corrections moved `t*` by two to four" — **it is `1.6–2.8×`, and it moved *down***
5. **"the dealiasing ceiling"** — `43` is the **largest rank tested**; a wavenumber is not a rank
6. **"exact"** for the never-yields rank — its error is `1e-13`–`1e-8`, not zero
7. "static POD fails" — it is **propagated fixed-basis projection** that fails; a DMD run at `r=32`
   is stable though degraded
8. "the `crossovers` block is stale / un-provenanced" — **withdrawn; it is correct and reproducible**
9. "Kolmogorov flow" or "turbulent dynamics" / "turbulence validation" — **the forcing is
   `f = (A sin(ky), 0)`**, and neither forcing gives a resolution-robust stationary state
10. any speedup or memory saving; "adaptive rank" as a supported claim; a drift percentage; any
    long-time claim from a `T=1` run
11. the `N=128` multipliers **STRUCK (D56)** / **STRUCK (D56)** — **unverified, do not print**
12. any of the four barred novelty claims (no DLRA NS solver exists / first exactly divergence-free /
    first structure-preserving low-rank / "to our knowledge")

---

## 4. Where things are

| what | where |
|---|---|
| the argument, the section map, the drafted abstract, reviewer attacks | `state/reviewer/PAPER_BLUEPRINT.md` |
| every number with its source, and the full prohibition list with reasons | `state/reviewer/CLAIMS.md` |
| the figures (8, all current) | `experiments/figures/` |
| **§3's second invariant — is the discrete statement the same as the continuous one?** | **being checked now; if it changes, I will correct §3 before you build on it** |

**Your blocking list, in order:** §3 and §4 first (above), then the force's formula in your §5, the
three bibliography items, and the citations. **`t*` is not blocking — it is `0.649` / `1.482`.**

---

**If anything here contradicts something I sent you earlier, this file wins and I am the one at
fault.** Ask me if a number looks unfamiliar; every one above is traced in `CLAIMS.md`.

## §7 — the two timescales, and the one sentence that would be false (D48, binding)

**The draft currently has only the qualitative argument (`07_discussion.tex:30-32`, "a fixed basis
cannot react when the dynamics at a later time"), which is correct. It reports NEITHER number. §7
needs both, and it needs them kept apart.**

| | |
|---|---|
| **crossover `t*`** | `0.649` (r=16) / `1.482` (r=32), `W=0.25`, `Re=5000`, `N=64`, **`A=0.2`** |
| **fixed-basis divergence** | `t = 5.513` / `5.7425` / `6.96` / `7.1715` for `pod_late_r32` / `pod_early_r42` / `pod_early_r32` / `pod_late_r42`, reaching `7.1e+278`, **`A=0.5`** |

**`t*` is where the evolving subspace becomes MORE ACCURATE. The divergence is where the fixed basis
EXPLODES, four to eleven times later. The sentence "the static baseline fails after `t*`" is FALSE.**

Three things that must travel with it:

1. **Different cases.** `A=0.2` versus `A=0.5`. **Do not present the two timescales as one experiment.**
2. **Divergence time is not monotone in rank** (`5.513` r=32 late, `7.1715` r=42 late, `6.96` r=32
   early, `5.7425` r=42 early). So the claim is *instability of a propagated fixed basis*, **not**
   *large rank is unstable*.
3. **D66's three hedges**, because this is **one artifact**: a §7 **observation**, **not** a
   contribution, until the D31.5 sweep runs.

**Suggested shape (four sentences):** the fixed-basis baselines are stable early and unstable late —
`pod_late` at `t = 5.513`, `pod_early` at `6.96` — reaching `7.1e+278`, while every SP-DLRA variant
reaches `t = 8.0` with `max |∇·u|` between `7.6e-14` and `1.99e-13`. This is a *different* failure
from the crossover, and much later: `t* ≈ 0.65–1.48` is where the evolving subspace becomes more
accurate, whereas the fixed basis explodes at `t ≈ 5.5–7.2`, four to eleven times later. The two are
measured at different forcing amplitudes (`0.2` and `0.5`). The divergence time is not monotone in
rank, so we attribute the failure to propagating a fixed basis through the nonlinearity rather than to
rank as such. Because this rests on a single case, we report it as an observation.

## §3 — the clause that keeps the verification section credible (D49, binding)

**Your framing is already honest** — §3 says "a verified implementation" and "reproduce the analytic
decay", never "more accurate than". **That is why this is one clause and not a rewrite. But the
limitation is unstated, and a reviewer who derives it will discount the whole section.**

**The exact Taylor–Green solution is a single Fourier mode** (`run_taylor_green.py:51-52` sets
`omega = 2 sin x sin y`; the artifact records `initial_state.numerical_rank: 1`). **So the rank-1
reduced solver represents it exactly, and this case cannot discriminate between methods or say
anything about whether low-rank approximation helps.** Measured three ways: at rank 1 the DLRA is
`1.26e-14` against the full grid's `1.51e-14` — *more* accurate than the reference — and the error
then **grows** to `3.9e-13` at rank 8, which is accumulated roundoff through extra rank-*r*
operations, not truncation.

**Verbatim, for §3:** *"The exact solution is a single Fourier mode, so the rank-1 reduced solver
represents it exactly and this case verifies the implementation and the invariants rather than the
accuracy of the reduction; raising the rank does not improve agreement but degrades it slightly
(`1.3e-14` at rank 1 to `3.9e-13` at rank 8) as roundoff accumulates through the extra rank-*r*
operations."*

**What the case DOES establish, so keep the claim at that strength:** the full-grid solver reproduces
an *independent analytic* solution to `2.8e-14` (a genuine test); the reduced path runs, preserves
both invariants, and agrees; `max |div u| = 1.63e-14` and the energy-balance residual is `3.16e-4`.

**One more clause for the cost discussion, free from the same artifact:** at rank 1 on `N=64` the
reduced solver is **`3.45x` slower than the full grid** (`3.68e-3` vs `1.07e-3` s/step) — **worse than
the headline `2.08-2.71x`, and the worst case in the project**, because all the SVD/QR overhead is paid
while the rank buys nothing. **The naive expectation is the opposite, and this is the measured reason
it is wrong. Say so: the reported range is not the worst case, and here is the worst case.**

## §4 / §8 — the memory sentence, with the right word (D19.4a/D49, binding)

**There is no memory advantage, and saying so is one of the paper's honest strengths. The number is
right; one word is wrong, and it is a word a reviewer will catch.**

| | overhead vs full grid | spread over `r = 2 … 43` | noise floor | spread / noise |
|---|---|---|---|---|
| `N=64` | `+2.24 MiB` | `0.227 MiB` | `0.066 MiB` | `3.41×` |
| `N=128` | `+4.27 MiB` | `0.684 MiB` | `0.066 MiB` | `10.29×` |

**Do not write "flat in rank."** The measurement *resolved* the rank variation, so the variation is
**real** and "flat" asserts the opposite. **Whether an effect is flat is a question about whether the
instrument could see it, not about its size.** *(R89/D52: these numbers moved - the noise floor halved
to `0.066 MiB` and every ratio rose, so the variation is now comfortably resolved at `3.4x` and `10.3x`
rather than marginal at `1.1x`. Use the table above, not the earlier one.)*

**Verbatim:** *"The reduced integrator does not save memory: it costs `2.2 MiB` (`N=64`) to `4.3 MiB`
(`N=128`) more than the full-grid step. Peak RSS varies by `0.23 MiB` (`N=64`) to `0.68 MiB` (`N=128`)
across a 21× rank range — `3.4×` and `10.3×` the `0.066 MiB` run-to-run noise floor of an identical
configuration, so the variation is resolved rather than marginal, and is a few percent of a `~43 MiB`
peak."*

**Report the overhead, never the raw RSS** — the interpreter and BLAS baseline is `~33 MiB` and no
method choice affects it.

**One clause on the BUG port's memory, if you mention it:** its rank dependence is *far* larger than
the projected integrator's — spread `0.69 MiB` (`10.4×` the floor) at `N=64` and `1.99 MiB` (`29.9×`) at
`N=128`. **At `N=128` the BUG port's rank dependence exceeds the projected integrator's entire
overhead**, so it is nowhere near rank-flat in memory.

## §4 — the cost protocol choice, which is the coder's and belongs in the paper (D52.8, binding)

**The cost numbers moved in the reviewer's R89, and the reason is a protocol choice worth stating in the
paper rather than hiding: `full_step_ratio_vs_reference` is now `2.08–2.71×`, not `1.78–2.18×`.**

**Why it moved, in the coder's words, and this should be a sentence in §4:** *"this node also serves a
language model, so its load moves with someone else's work; the protocol interleaves configurations
because on a node this noisy the per-configuration median is unreliable while the ratio between
interleaved configurations is not."*

**That is a general fact about benchmarking on shared infrastructure, and a reviewer who reproduces this
work on a busy cluster will meet exactly the same problem.** Stating the choice — absolute
per-configuration timings on an idle machine, or ratios between interleaved configurations on a shared
one — is what distinguishes a protocol from an accident. **The second is what was done, and the second
is defensible.**

**The direction is worth stating plainly too: every value moved UP, so the new range is the less
favourable one and is the one we quote.** Reporting the smaller range because it was measured first
would be indefensible now that we know the machine was loaded and the first run's load was not recorded
at all.

## §6 — the grid-refinement result, and two struck numbers (D56, binding)

**I have carried `1.46→1.99` and `2.45→6.04` as "unverified" for many cycles. I ran the derivation this
cycle and they are STRUCK: they appear nowhere in `kolmogorov_re5000_{N64,N128}.json`, under
time-keyed indexing or positional, for either method. They are not index-shift artifacts; they cannot be
derived from that artifact at all.** Do not quote them, and do not quote them as a caveat either.

**What the pair actually contains is better, and it is a §6 result rather than a footnote.**

**Why it is a clean experiment, which nobody had noticed:** the `N=64` case uses its own 64-grid initial
condition and the `N=128` case uses **`ic_reference_N: 64`** — **so both start from the same 64-grid
field** — and both fit the static baseline at `effective_rank: 16`. **The ratio therefore measures the
resolution effect alone.** (And note the two cases sample on *different* time grids, `0.01` and `0.005`,
which is exactly why the match must be on `time` and never on position.)

**The reduced integrator is grid-limited:**

| `t` | `N=64` | `N=128` | ratio |
|---|---|---|---|
| 0.01 | `1.001e-04` | `4.590e-05` | `0.4583` |
| 0.05 | `9.882e-05` | `4.528e-05` | `0.4582` |
| 0.10 | `1.011e-04` | `4.687e-05` | `0.4637` |

**Ratio `0.4581–0.4637` across the whole window — stable to `1.2%`.** Refining `64 → 128` **reduces** the
reduced integrator's relative L2 error by `≈2.18×`, apparent order `log₂(1/0.458) = 1.13`, consistent
with a second-order scheme measured in that norm.

**The static rank-16 baseline is not grid-convergent at all:** `3.14×` at `t=0.01`, `10.3×` at `t=0.05`,
`1464×` at `t=0.08`, `672×` at `t=0.10` — **growing by `2.5×` to `1464×`, and the growth is itself
unstable, a `575×` spread across the window.**

**And the shape is the striking part, and it is a better sentence than any ratio:** on the 64 grid the
static baseline **starts six orders of magnitude better** than the reduced integrator (`4.0e-11` vs
`1.0e-04` at `t=0.01`) and **ends four orders worse** (`1.0e-08` vs `1.0e-04` at `t=0.1`). **It is not
uniformly worse — it is transiently better and then catastrophically worse.**

**Why this is worth a paragraph: it is the thesis measured on the axis the thesis is about.** The
evolving subspace converges with the grid; the fixed one does not. **A grid-refinement result that
separates the two families is worth more than the two multipliers it replaces.**

**The honest framing, which the paragraph must carry:** one refinement, `T=0.1`, `A=0.5`, a shared
64-grid initial condition, a rank-16 static baseline. **It is a two-grid comparison, not a convergence
study** — a proper order study needs three grids — **and because the baseline's ratio is unstable, the
*size* of its degradation is not a stable quantity to quote; only the sign and the order of magnitude
are.**

## §4 — the Proposition is VERIFIED against the code; the Remark beside it is not (D58, binding)

**I checked the paper's mathematics against `solvers/` for the first time. The theorem passes.**

`04_methods.tex:130` states `e^{nu t Delta} Psi = (e^{nu t D_x} U) S (e^{nu t D_y} V)^T`, with the singular
values `S` unchanged, at cost `O(rN log N)`, error *"zero, not merely small"*. `solvers/spectral.py:156
factor_semigroup` implements precisely this, and `solvers/bug.py:183-184` evolves `U` and `V` only —
**so "`S` is unchanged" is literally true of the code.** The cost matches, and the state variable is `psi`
throughout, so the ansatz is on the stream function and divergence-freeness is by construction.

**But the Remark that tells an implementer how to compute it omits three things, and
`factor_semigroup`'s own docstring states all three explicitly. Each produces a silently wrong answer —
the run completes, the invariants look plausible, and the error is a *different operator* rather than a
crash.**

1. **A full `fft`, not `rfft`.** The docstring: *"the rfft half-axis is not a valid multiplier for a
   full-spectrum inversion."* **Implementing the Remark with `rfft` gives a wrong viscous step with no
   error message.**
2. **Both factors go along axis 0 — and "likewise for `$V$`" is dangerously vague.** The docstring:
   *"Applying the `y` semigroup along `V`'s columns would be transforming its `r` singular-value
   directions instead, which is a different operator."* **The natural reading of "likewise" produces a
   different operator.**
3. **The semigroup is unmasked; the dealiasing lives elsewhere.** `factor_semigroup` applies
   `exp(-nu kx^2 tau)` to the **full** spectrum with no mask. The mask is applied in
   `solvers/ns_psi.py:85` and `:96`, to the *field-level* nonlinear term. **So "exact" is exact for
   `e^{nu t Delta}` as implemented — it is not a statement about the dealiased discretisation, because
   the mask is not part of the operator the Proposition names.** Your PENDING at line 102 already flags
   the de-aliasing policy as unresolved; the Proposition asserts exactness without saying which object is
   exact.

**Replacement Remark, verbatim — this is the whole fix:**

> **Remark (computing the viscous step).** Both factors are transformed along their leading spatial axis —
> $\hat U = e^{\nu t\Delta_x}U$ and $\hat V = e^{\nu t\Delta_y}V$ — so the semigroup acts on the spatial
> directions of each factor and **not** on its $r$ singular directions. Each factor column costs two
> length-$N$ transforms, so the step is $O(rN\log N)$ and needs no factorisation. **The transforms are
> full complex FFTs against the full wavenumber grid: a real-input half-spectrum transform is not a valid
> multiplier here, and using one changes the operator silently.** The semigroup is applied to the full
> spectrum; the dealiasing mask is applied to the nonlinear term and not to this step, so the exactness
> asserted above is exactness of the operator $e^{\nu t\Delta}$, not of the dealiased discretisation.

**And the section's real state, which is good news: `04_methods.tex` has SIX PENDING markers, at lines
26, 102, 110, 231, 262, 284 and 328 — the `Re` definition and $(F,\nu)$ pairing, the discrete energy
identity and de-aliasing policy, the forcing-aware invariant (twice), the step order and projection
subspace, the rank rule and tolerances, and the measured wall-clock and peak-memory numbers. EVERY ONE OF
THOSE IS ANSWERABLE FROM ARTIFACTS THAT ARE NOW VERIFIED, so none of them is blocked on new computation.**
§4 is the one section that is *nearly* right: the theorem is correct and the code matches it. What is
missing is the connective tissue between them — which is exactly what the six markers are. **Item 3 above
answers marker 102; the others are in `WRITER_ORDER.md` §1 and `FIRST_RUN.md`.**

## §4.2 and §5 — two wrong numbers, and the steady state that reframes §5 (D59, binding)

**I checked §4.2's prose against the code. The Proposition before it was right (D58); the two sentences after the energy identity contain two errors.**

**1. Delete the second expression for $P_{\mathrm{in}}$.** The paper writes both

$$P_{\mathrm{in}} = 2\pi^2 F^2/\nu \qquad\text{and}\qquad P_{\mathrm{in}}(\psi_K) = \mathrm{Re}\cdot\nu^2\|\cos y\|_2^2/(2\pi).$$

**The first is correct** (verified against the code's own operators: `24674` on the run's parameters, matching $\langle u_K,f\rangle = (F^2/\nu)\|\cos y\|_2^2$ with $\|\cos y\|_2^2 = 2\pi^2$ in 2D). **The second gives `6.28e-4` — wrong by a factor $3.9\times10^7$, because it confuses $F$ with $F^2$.** They agree only if $F=\nu$. Keep the first, drop the second.

**2. Replace the Reynolds-number definition.** The paper states $\mathrm{Re} = 2\pi F/\nu^2$. On the code's own parameters that is $7.85\times10^7$, **whereas the code takes `re` as an input and sets $\nu = 1/\mathrm{Re}$** — so every Re in the paper is an *input*, not a quantity derived from $F$ and $\nu$. They differ by $1.6\times10^4$. **This is your PENDING at line 26, and the definition currently in the prose is the thing it asks you to check.** Say it as: *"$\mathrm{Re}$ is an independent input and $\nu = 1/\mathrm{Re}$; the forcing amplitude $A$ is set separately, and the classical Kolmogorov scaling $A=\nu$ is not imposed."*

**3. The good news, and it is bigger than the two errors: $\psi_K = -(F/\nu)\cos y$ IS an exact steady state of the simulated PDE.** I checked with the code's own operators: $\|u\cdot\nabla\omega_K\|_\infty = 0$, the diffusion and forcing terms cancel exactly, **vorticity residual `0.000000`** — and it holds for *any* $(F,\nu)$, not just the ones we run. **Your §4.2 claim is correct.**

**4. Which reframes §5, and makes it stronger.** We have been carrying "no stationary state" as a property of the flow. **It is a property of the initial condition, and it is quantifiable:**

| | |
|---|---|
| $\|u_K\|_\infty$ at the exact steady state | `2500` |
| its kinetic energy $E_K$ | `6.17e+07` |
| our initial energy (from the artifact) | `22.21` |
| **$E(0)/E_K$** | **`3.6e-07`** |

**We start essentially at rest and are driven up toward a steady state we are $2.5\times10^3$ below in velocity.** So replace "no stationary state is observed" with a quantified statement — *"the forced equilibrium $\psi_K = -(F/\nu)\cos y$ is an exact solution of the discretised equations, and the runs are initialised at $E(0)/E_K = 3.6\times10^{-7}$ of its energy, so the absence of stationarity over the horizons measured is a property of the initial condition rather than of the flow."* **A reader can check that in one line, and it is a stronger claim than an unexplained negative.**

**5. And it gives the "not Kolmogorov flow" statement a number instead of an attribution.** $\psi_K$ coincides with the *classical* Kolmogorov flow only when $A=\nu$ (where $u_K=(1-\cos y)e_x$, $\mathrm{Re}=1/\nu$). **We run $A/\nu = 2500$.** Same family, not the same flow — and now that is a quantity rather than a citation.

## §3 and §4.6 — Invariants I1 and I3, checked against the code (D60, binding)

**I checked every implementable claim in §4's invariants list. I1 is wrong three ways, I3 describes a measurement that is not performed, and I2 is correct.**

**1. I1's magnitude is wrong by three orders of magnitude, and its universality is false.** The paper says $\max|\nabla\cdot u| = O(\varepsilon_{\rm mach}) \approx 10^{-14}$ *"at every step, for every rank and every Reynolds number"*. Over every method, rank and Reynolds number measured — **restricted to methods that remain finite**, since the diverging ones are the subject of §5 and not a violation of I1 — the range is **`2.26e-14` to `1.0459e-11`** (`pod_dmd_r32`). **So `≈10⁻¹⁴` understates the worst finite case by `1046×`, and a `462×` spread means no single number can be the bound.**

**2. "A property of the formulation, not of the numerics" is measurably wrong — it is resolution-dependent.** If it were a property of the formulation it would not change with the grid. At fixed Re and forcing: `full` `2.58×`, `dlra` `2.65×`, `pod` `2.59×` from `N=64` to `N=128`. **Consistent `2.6×` across all three methods.** The residual is the roundoff of the *discrete* spectral derivative pair: the cancellation $\partial_x\partial_y\psi-\partial_y\partial_x\psi$ is exact in real arithmetic, and its floating-point residue is scaled by the conditioning of those operators, which grows with the resolved wavenumber.

**3. The correction is a stronger claim, which is the point — and this is the binding text:**

> **"The velocity is recovered as $u=(\psi_y,-\psi_x)$, so $\nabla\cdot u=0$ identically in exact arithmetic. The measured residual never exceeds $\mathbf{1.1\times10^{-11}}$ over every method, rank and Reynolds number we ran, which is seven orders of magnitude below the reduced solver's own error ($\sim10^{-4}$), and therefore cannot account for it. The residual is the roundoff of the discrete spectral derivative pair, and grows as the operators' conditioning does: $2.6\times$ from $N=64$ to $N=128$, consistently across methods."**

**That says what the number is, where it comes from, how it scales, and why it is irrelevant to the method's accuracy. `≈10⁻¹⁴`, "a property of the formulation" says none of those and is wrong on the number.**

**4. I3 describes a measurement the code never performs.** The paper says *"the number of POD modes required to resolve 99.9% of the kinetic energy of the reference run"* and that $r(t)\le r_{\mathrm{POD}}$ *"is the expected (and measured) outcome"*. Three checkable problems:

- **the threshold is `99%`, not `99.9%`** — every artifact records `energy_fraction: 0.99`;
- **the quantity is the fluctuations, not the kinetic energy** — the artifacts record `rank_basis: "fluctuations"` and `pod_fit_includes_ic: true`;
- **and the "POD count" is an input, not a measurement.** `effective_rank` is `16` in every `kolmogorov_*` artifact — **constant across three Reynolds numbers and two resolutions, and equal to the requested `pod_rank`.** **A quantity that does not move with the dynamics is an input.**

**So: either measure it (record the rank at which the energy fraction is actually reached, per case, and let it vary — one line, one cheap run), or drop the sentence and report $r_{\mathrm{POD}}=16$ as the rank the static baselines were *given*.** The second is honest and costs nothing; the first is better.

**5. I2 is correct, and it is worth keeping exactly as written.** Your $P_{\mathrm{in}}=-F\langle\psi,\cos y\rangle$ matches the code's recorded invariant `dE/dt + nu*||omega||^2 - <psi,zeta> + <psi,adv>` with $\zeta=-A\cos y$, same identity and same sign, **plus an explicit advection term that vanishes to roundoff rather than being assumed away** — which is the better formulation and you have it.

## §4 cost model — two routes to a benefit, both closed by our own measurements (D61, binding)

**This is the one where the paper promises something its own §6 will contradict, so it needs fixing in §4 rather than hoping the table is not read.**

**The sentence at `04_methods.tex:320-327`:** *"At small $r$, the per-step cost of SP-DLRA is therefore comparable to, or larger than, the full-grid reference, and we make no a priori claim of per-step speedup. **Any end-to-end benefit has to come from the memory footprint of the factors ($O(nr)$ versus $O(n)$) or from regimes in which the rank stays small over long time spans; both are measured, not assumed.**"*

**Route 1, memory, is closed — and the sign is the wrong way round.** Every recorded overhead is **positive**: `+2.24 MiB` (`N=64`), `+1.96` (BUG, `N=64`), `+4.27 MiB` (`N=128`), `+3.59` (BUG, `N=128`). **The reduced integrator uses *more* memory, not less.** The $O(nr)$ versus $O(n)$ argument is about the **factors**; the state is a full $n$-field *plus* its factors *plus* the factorisation workspace, and the workspace dominates.

**Route 2, long time spans, is unavailable.** Our only horizon beyond the initial transient is `nsteps: 200`.

**And nothing retracts either.** `08_limitations.tex` has **no memory or footprint text at all**, and `06_results.tex` still carries the `[PENDING-CODER]` for the wall-clock and memory numbers.

**The replacement, which is stronger than what it replaces:**

> **"Because the nonlinear residual is evaluated on the full grid, its $O(n\log n)$ cost is independent of the rank, and we make no claim of per-step speedup: SP-DLRA is measured at $2.1$–$2.7\times$ the full-grid step. Nor is there a compensating memory benefit: peak RSS is $2.2$ MiB ($N=64$) to $4.3$ MiB ($N=128$) *above* the full-grid step, because the state is a full field plus its factors plus the factorisation workspace. We therefore identify no end-to-end benefit in the regimes we have measured, and the case for the method rests on its structural guarantees and its accuracy, not on efficiency. Establishing a regime where the rank stays small over a long span would require evidence beyond the $200$-step horizons used here, and we do not have it."**

**A reviewer who reads §4's memory route and then §6's memory numbers will conclude either that the paper is not careful or that the numbers were selected.** Declining to make the promise is worth more than keeping it.

**One label in the table also needs fixing.** The cleanup-SVD row reads cost `$O(n r^2)$`, remark *"thin, $r\times r$"*. **The cost is right and the label is wrong:** the SVD is of the **$n\times r$** centred field (`np.linalg.svd(centered, full_matrices=False)`), which is what $O(nr^2)$ is the cost of; the $r\times r$ object is the *output* singular-value diagonal, and the second SVD of *that* is a different, negligible $O(r^3)$ operation. **The rest of the table is right** — the viscous row matches the code's `O(N r log N)`, the nonlinear row's *rank-independent* claim is exactly what the code does, and *"we make no a priori claim of per-step speedup"* is among the best sentences in the draft.

## §4 step 4 — the cleanup describes a different algorithm from the one implemented (D62, binding)

**This is the one where the paper, the code and the project's own test suite all disagree, and the paper is the outlier. It is also the one where a reader who follows the paper gets a `Θ(N³)` factorization in every step.**

**The paper (`04_methods.tex:218-221`), step 4:** *"A thin SVD of $\Psi^{n+1}$ re-orthonormalizes the factors (rank at most $2r$ before truncation)."*

**The code (`solvers/bug.py:172-188`), and its own words:** *"Orthonormality is then restored by **QR of the `N × r` factors — `O(N r²)`, not a factorization** — with `R_u S R_vᵀ` folded into the small matrix. **Reusing `initialize`'s full SVD here instead would have put a `Θ(N³)` factorization back in every step and defeated the entire point of the port.**"*

**And `experiments/test_engine.py:565` asserts the code's version by name** — `test_bug_never_factorizes_the_full_state_inside_a_step`, whose docstring says *"the only factorization allowed after `initialize` is of the small augmented S-matrix, of dimension at most `4r`."*

**Replacement for step 4:**

> **4. Cleanup.** The diffused factors are re-orthonormalised by **QR of the `n × r` factors**, with `R_u S R_vᵀ` folded into the small matrix; the only factorisation inside a step is then a **thin SVD of that small `r × r` matrix**, which performs the truncation. The rank is at most $2r$ before truncation, because the projected increment lies in $\mathrm{span}\{\hat U_{\Delta t}\}\times\mathrm{span}\{\hat V_{\Delta t}\}$. **No factorisation of the full state occurs inside a step** — a property the test suite asserts directly, since a timing measurement could not distinguish the two on a shared machine.

**Why it matters: a reader who implements the paper's step 4 gets a `Θ(N³)` factorization every step, and their reproduction is slower than the full-grid reference by an amount the paper never claims and could not explain — because the paper's own cost table says the step is `O(n r²)`.** The paper is currently self-inconsistent in a way a careful reader can see without running anything.

**The rank-`2r` bound is correct as written and should be kept.**

**And the PENDING at line 231 is now half-answered, both halves in your favour:**
- **the projection subspace is the midpoint-evolved factors, as you wrote it** — `eq:step` projects with $\Pi_{\hat U,\hat V}$ from $\hat U = e^{\nu\Delta t D_x/2}U$, and the code evolves the factors before the augmented step uses them. ✓
- **"for fixed factors the step is second order in $\Delta t$" is tested** — `test_reduced_path_is_second_order_in_dt` and `test_bug_is_second_order` both exist and pass. ✓
- **the defect is the cleanup, which is the other half.**

**One correction to my own previous message:** I said the cost table's `O(n r²)` was "right and the label wrong". More precisely — **the cost is right for the algorithm the paper describes, and the paper's algorithm is not the one implemented.** The implemented step also costs `O(n r²)`, but through the QR rather than through an SVD, so the number survives by a different route. **A number can be right for the wrong reason, and the way to tell is to ask which operation the number is the cost of.**
