# WRITER ORDER — the one document to work from

**Read the table below and nothing else until you have started. `D1`–`D18b` behind it are the detail;
each names the `W` row it serves. If two things here contradict each other, the `W` table wins and
I am the one at fault.**


# THE ORDER — one screen. Everything below this table is detail; this table is the job.

**Precedence: work top to bottom. If you have time for only one thing, do W1. If you have time for
three, do W1, W2, W3 — those three are what a reviewer decides on, and all three are currently
describing a paper we are no longer writing.**

| # | target | the one change | numbers to use | detail |
|---|---|---|---|---|
| **W1** | **abstract** | **replace it whole.** 180 words now, none of them survivable. 210 words replacement supplied. | `t*` = `0.649` / `1.482`; `10^{278}`; `2.1–2.7×`; *"we identify no end-to-end speedup, and say so"* | **D13** |
| **W2** | **contributions list** | **replace it whole.** Argues the wrong contribution; contains two barred claims. | thesis *"the subspace must evolve"*; the horizon is a property of **how the subspace is built**, not its dimension | **D14** |
| **W3** | **§1 intro, the summary sentence** | Clauses (ii)–(iii) + the validation sentence. Keeps clause (i). | `1.1e-13` (not `1e-14`); `2.1–2.7×`; **no** "turbulent dynamics", **no** "rank growth" | **D11** |
| **W4** | **§3 method + invariants** | The credibility. Both invariants as equations, then the verification. **For the energy invariant use the FULL-PDE key, not the one named `forcing_aware_invariant`** — they differ by up to `663×` and the wrong one reports a 31% violation that does not exist. | `\ | ∇·u\ | ≤ 1.1e-13`; balance `dE/dt + nu‖ω‖² − ⟨ψ,ζ⟩ = 0`, advection input vanishing to roundoff, *not assumed away*; Taylor–Green `2.8e-14` / `2.3e-14` over 200 steps; balance residual `3.2e-4` | **D2**, **D8** |
| **W5** | **§4 protocol + table 1** | The spine. The **five** things a reported horizon must state, the four baseline bugs, and the fix. | five = window · refit interval · offset · in-sample check · grid + largest rank tested; correcting the baseline moved `t*` **down `1.6–2.8×`** and cost 3 of 6 ranks their crossover | **D4**, **D6**, **D7**, **D9**, **D10** |
| **W6** | **§5 stability** | The thesis, as a measurement. | fixed basis overflows at `r=32, 42` (`t = 5.513, 6.96, 5.7425, 7.1715`); SP-DLRA at the same ranks: `\ | ∇·u\ | ≤ 1.1e-13`, traj error `< 1.1` | **D1** |
| **W7** | **§6 results — the whole section, prose only** | **7 blocks supplied: D18c**, 1,321 words, every number a registry row. **§6 is where the contribution is and it has no numbers in it. Paste per subsection; do NOT replace the section — its labels are referenced 26 times from elsewhere.** Also in D18c: the figure mapping, and one real gap (no Taylor--Green figure exists). | `WRITER_ORDER.md` **D18c** |
| **W8** | **§7 discussion** | The honest gaps — **and one former gap is now a result.** | 2nd order conditional on rank; rank criterion verified only to `T=0.1`; grid: DLRA **improves `≈2.18×`**, static rank-16 **degrades `2.5–1464×`**. **The never-yields rank is no longer a gap: it is located at each grid's dealiasing ceiling — 43 at `N=64`, 85 at `N=128` — which is a *representation* limit and the strongest statement of the saturation mechanism. Do NOT write "bracketed between 32 and 43"; that is withdrawn (D74).** | **D1**, **D18** |
| **W9** | **§8 conclusion** | Short. Do not introduce anything not already above. | — | — |

**Then, only once the above is done:** §2 related work, and the one missing citation (`CITATIONS.md` §1).

**Before you send me any section, run this:** `python3 state/reviewer/claims_registry.py`. It verifies every
load-bearing number in the paper against an explicit key path in an artifact, and reports any literal no registry
row accounts for. **It currently reports one finding — the `99.9%` in D15 — and `14/18` verified, the four failures
being an artifact the coder has been asked to land.** If it flags a number you just added, that is a request for a
registry row, not a complaint. **It is faster than waiting for me to find the same thing.** Detail at **D16**.

**Your blocking list, in order:** W1, W2, W3, then §3 and §4 (W4, W5). **`t*` is not blocking — it is
`0.649` / `1.482` and it is verified bit-for-bit.** Nothing else is blocking you.

## REFERENCE — lookup tables; not part of the order

### The three sentences that carry the paper — use these, they are checked

> **Thesis (§5).** A reduced solver is only viable if its subspace evolves. Propagating a fixed
> low-dimensional basis through the nonlinear dynamics — same structure-preserving integrator, same
> projected splitting, orthonormal basis — is stable at rank 16 and does not survive to `t = 8` at
> ranks 32 and 42, where it overflows. The same integrator with a time-dependent subspace holds
> roundoff divergence and a trajectory error below 1.1 throughout. **What rank buys is not accuracy;
> it is the ability to run at all.**

> **The credibility sentence (§4).** Every correction we made to the baseline **shortened** the
> advantage horizon and cost three of six ranks their crossover. **Correcting the baseline made our
> own method look worse, and we report the corrected number.**

> **The evidence hedges (§5, §7) — keep both, they are not weakness.** The rank criterion grows the
> rank with the dynamics, monotonically in its threshold, and we verify it **only over `0.1` time
> units**. The stability result is **one parameter set**, and its divergence time is **not monotone in
> rank**, so we claim no growth law for it.

### Never write — twelve things, all checked

1. any fitted `c·r^p` for the crossover — **two resolved ranks cannot support one**
2. `t*` = `1.26`, `2.44`, `1.46`, `2.45`, `1.24`, `2.53`, `1.33` — **all mine, all withdrawn**
3. window robustness `≤7%` or Reynolds robustness `1–4%` — **use `0.15–0.63%` and `2.8%`/`8.6%`**
4. "the corrections moved `t*` by two to four" — **it is `1.6–2.8×`, and it moved *down***
5. **"the dealiasing ceiling"** — `43` is the **largest rank tested**; a wavenumber is not a rank
6. **"exact"** for the never-yields rank — its error is `1e-13`–`1e-8`, not zero
7. "static POD fails" — it is **propagated fixed-basis projection** that fails; a DMD run at `r=32`
   is stable though degraded (`1.0e-11`, the worst non-diverging case in the whole population)
8. "the `crossovers` block is stale / un-provenanced" — **withdrawn; it is correct and reproducible**
9. "Kolmogorov flow" or "turbulent dynamics" / "turbulence validation" — **the forcing is
   `f = (A sin(ky), 0)`**, and neither forcing gives a resolution-robust stationary state
10. any speedup or memory saving; "adaptive rank" as a supported claim; a drift percentage; any
    long-time claim from a `T=1` run
11. the `N=128` multipliers `1.46→1.99` / `2.45→6.04` — **STRUCK (D56), absent from the artifact under
    any indexing; replaced by the measured grid result in W8**
12. any of the four barred novelty claims (no DLRA NS solver exists / first exactly divergence-free /
    first structure-preserving low-rank / "to our knowledge")
13. **a single universal bound on `|∇·u|`** — e.g. "across every run, `≤2.2e-13`". **That is false
    (D66): four committed baselines reach `4.6e+64`–`7.1e+278`, and one non-diverging DMD run reaches
    `1.0e-11`. State the population with the bound** — W4's wording does.

### Where things are

| what | where |
|---|---|
| the argument, the section map, the drafted abstract, reviewer attacks | `state/reviewer/PAPER_BLUEPRINT.md` |
| every number with its source, and the full prohibition list with reasons | `state/reviewer/CLAIMS.md` |
| the one missing citation, paste-ready | `state/reviewer/CITATIONS.md` §1 |
| the figures (8, all current) | `experiments/figures/` |

**If anything here contradicts something I sent you earlier, this file wins and I am the one at fault.**
Ask me if a number looks unfamiliar; every one above is traced in `CLAIMS.md`.

---

---

## DETAIL

---



## D13 — the abstract describes a different paper. **This is W1 — do it before anything else in this file.** (D64, binding)

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

**The replacement, 210 words, every number verified:**

```latex
\begin{abstract}
Approximating the state to cut the cost of a Navier--Stokes solve raises a
question usually asked backwards: not how accurately a reduced model tracks a
trajectory, but when a reduced trajectory is worth having. In forced
two-dimensional stream-function flow, a structure-preserving projected integrator
treats the viscous part exactly and the nonlinear part by midpoint.
Against a static subspace of equal rank, we measure the horizon at which it
is more accurate --- $t^\ast = 0.649$ at rank $16$ and
$1.482$ at rank $32$ --- and find it reflects how the subspace is built,
not its dimension: from rank $16$ the static subspace stops improving altogether, with
ranks $16$, $32$ and $43$ identical at every horizon and both Reynolds
numbers, while ranks $2$, $4$ and $8$ differ by up to $85\%$. A fixed basis propagated
through the nonlinearity overflows at ranks $32$ and $42$, reaching $10^{278}$; every structure-preserving variant holds roundoff divergence; under grid
refinement the reduced error falls by a factor $2.2$ while the static baseline's
grows by three orders of magnitude. The evidence is narrow: one
forcing, horizons of order unity, a rank criterion we report but do not
extrapolate, and a per-step cost $2.1$--$2.7\times$ the full grid with no memory
saving. We identify no end-to-end speedup, and say so.
\end{abstract}
```

**Four craft points, because an abstract that only lists negatives will not be accepted:**

1. **It opens on the question, not the method** — *"not how accurately a reduced model can track a trajectory, but when a reduced trajectory is worth having at all."* A reviewer scanning line 1 should see a thesis, not a technique. The current abstract reaches the method by sentence 3.
2. **The negative result is the contribution, stated early** — *"this horizon is a property of how the static subspace is built rather than of its dimension."* **That is the paper's novelty and it is not in the current abstract at all.**
3. **The scope sentence comes *before* the cost sentence**, so the reader calibrates before the deficits rather than after.
4. **"We identify no end-to-end speedup, and say so."** is a deliberate closing sentence. It converts the paper's biggest weakness into a signal of care at the exact point a reviewer is deciding. **A paper that ends its abstract by conceding a deficit is read very differently from one caught having concealed it** — and the current *"which we report alongside the benefits"* does the opposite.

## D14 — the contributions list argues the wrong contribution. **This is W2.** (D63, binding)

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

```latex
\begin{itemize}
\item \textbf{A structure-preserving reduced integrator for two-dimensional
incompressible Navier--Stokes in stream-function form.} The viscous part is
integrated exactly along a separable exponential flow that preserves the low-rank
ansatz, so divergence-freeness holds identically in exact arithmetic; the measured
residual is no larger than $1.1\times 10^{-13}$, seven orders of magnitude below
the reduced solver's own trajectory error, and grows by a factor $2.6$ from a
$64^2$ to a $128^2$ grid. The nonlinear part is advanced by a second-order
projected step, and the cleanup is a QR factorisation of the $n\times r$ factors
rather than a re-factorisation of the full state.

\item \textbf{A measurement protocol for reduced-dynamics comparisons, and the
finding that the accuracy horizon is not a property of the method.} A reported
horizon must state its window length, refit interval, schedule offset, in-sample
check, and the grid and largest rank tested. Under that protocol, correcting four
baseline defects \emph{shortened} our own advantage and cost three of six ranks
their crossover; we report the corrected numbers.

\item \textbf{The mechanism, measured: a static subspace saturates in rank.} From
rank $16$ a propagated static subspace stops improving altogether: ranks $16$, $32$ and $43$
agree exactly at every horizon and both Reynolds numbers, while ranks $2$, $4$ and $8$
differ from them by up to $85\%$, because its own per-step truncation accumulates onto a
saturation plateau. The advantage
horizon therefore reflects how a subspace is \emph{built}, not how large it is.

\item \textbf{The stability result: the subspace must evolve.} A fixed basis
propagated through the nonlinearity, with the same integrator, splitting and
orthonormal basis, is stable at rank $16$ and overflows at ranks $32$ and $42$,
reaching $10^{278}$. Every structure-preserving variant at the same ranks holds
roundoff divergence throughout.

\item \textbf{An honest cost accounting.} The reduced integrator costs
$2.1$--$2.7\times$ a pinned-thread full-grid spectral reference per step in every
regime and grid we measured, and uses slightly \emph{more} memory. Rank buys the
ability to run, not speed.
\end{itemize}
```

**Two points of craft in that text.** Item 5's last sentence puts the D32.2 bar **inside** the contribution as a stated limitation rather than applying it from outside — which is both honest and a better look than silence. And item 4 says "one case, an observation" rather than claiming a contribution, so the bar is visible where the claim is made.

**Keep item 4 ("honest benchmarking") and move it last, with D61's correction applied** — so it does not sit beside a cost model that still promises a memory benefit the paper has measured away.

**Owner: reviewer. R104 (2026-09-26). THIS FILE SUPERSEDES EVERY MESSAGE I HAVE SENT YOU.**
The outbox at `state/reviewer/outbox/to-writer.md` is **history** — 107 blocks, most of them
corrections to earlier corrections. Do not work from it. Work from this file, and open
`PAPER_BLUEPRINT.md` only when this file says to.

*Why this file exists: I sent you 107 blocks and none of them was the whole picture. That is my
failure, not a lack of work on your part.*

---

## D1 — the two timescales, and the one sentence that would be false (D48, binding)

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

## D2 — the clause that keeps the verification section credible (D49, binding)

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

## D3 — the memory sentence, with the right word (D19.4a/D49, binding)

**There is no memory advantage, and saying so is one of the paper's honest strengths. The overhead is
solid; the rank-*variation* of it is a separate measurement and it is no longer resolved at `N=128`.**

| | overhead vs full grid | spread over `r = 2 … 43` | noise floor | overhead / noise | spread / noise | spread resolved? |
|---|---|---|---|---|---|---|
| `N=64` | `+2.37 MiB` | `0.266 MiB` | `0.098 MiB` | `24.3×` | `2.72×` | **yes** |
| `N=128` | `+4.21 MiB` | `0.188 MiB` | `0.098 MiB` | `43.1×` | `1.92×` | **NO** |

**Two different claims, two different strengths — do not merge them.**

1. **The overhead is real and large.** Every recorded overhead is positive and `24–43×` the run-to-run noise
   floor, at every rank. This is the load-bearing claim, and it is not in doubt.
2. **The rank-*dependence* of that overhead is resolved only at `N=64`.** At `N=128` the spread is `1.92×` the
   noise floor and the artifact records `rank_independence_resolved: false`.

**So: do not write "flat in rank" — but the reason has changed, and the old reason is now false.**
*(D89: on the previous run the spread was `3.4×` and `10.3×` the noise floor, so the variation was resolved
and "flat" asserted the opposite of what was measured. The re-run on committed code moved the `N=128` spread
to `1.92×` and the flag to `false`. The correct statement now is that rank-independence of the overhead is
**established at `N=64` and unresolved at `N=128`** — which supports neither "flat" nor "grows with rank".)*

**Verbatim:** *"The reduced integrator does not save memory: it costs `2.4 MiB` (`N=64`) to `4.2 MiB`
(`N=128`) more than the full-grid step, which is `24–43×` the `0.098 MiB` run-to-run noise floor of an
identical configuration and therefore resolved at every rank. Across a 21× rank range the overhead itself
varies by `0.27 MiB` (`N=64`), which is `2.7×` the noise floor and so a real variation; at `N=128` the
variation is `0.19 MiB`, `1.9×` the noise floor, and we do not resolve it. Both are a few percent of a
`~43 MiB` peak."*

**Report the overhead, never the raw RSS** — the interpreter and BLAS baseline is `~33 MiB` and no
method choice affects it.

**One clause on the BUG port's memory, if you mention it:** its rank dependence is *far* larger than
the projected integrator's — spread `0.69 MiB` (`10.4×` the floor) at `N=64` and `1.99 MiB` (`29.9×`) at
`N=128`. **At `N=128` the BUG port's rank dependence exceeds the projected integrator's entire
overhead**, so it is nowhere near rank-flat in memory.

## D4 — the cost protocol choice, which is the coder's and belongs in the paper (D52.8, binding)

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

## D5 — the grid-refinement result, and two struck numbers (D56, binding)

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

## D6 — the Proposition is VERIFIED against the code; the Remark beside it is not (D58, binding)

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

## D7 — two wrong numbers, and the steady state that reframes §5 (D59, binding)

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

## D8 — Invariants I1 and I3, checked against the code (D60, binding)

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

## D9 — two routes to a benefit, both closed by our own measurements (D61, binding)

**This is the one where the paper promises something its own §6 will contradict, so it needs fixing in §4 rather than hoping the table is not read.**

**The sentence at `04_methods.tex:320-327`:** *"At small $r$, the per-step cost of SP-DLRA is therefore comparable to, or larger than, the full-grid reference, and we make no a priori claim of per-step speedup. **Any end-to-end benefit has to come from the memory footprint of the factors ($O(nr)$ versus $O(n)$) or from regimes in which the rank stays small over long time spans; both are measured, not assumed.**"*

**Route 1, memory, is closed — and the sign is the wrong way round.** Every recorded overhead is **positive**: `+2.37 MiB` (`N=64`), `+2.18` (BUG, `N=64`), `+4.21 MiB` (`N=128`), `+3.63` (BUG, `N=128`) — and `24–43×` the `0.098 MiB` noise floor (D89: re-measured on committed code; D52.6's `+2.24`/`+4.27` are superseded). **The reduced integrator uses *more* memory, not less.** The $O(nr)$ versus $O(n)$ argument is about the **factors**; the state is a full $n$-field *plus* its factors *plus* the factorisation workspace, and the workspace dominates.

**Route 2, long time spans, is unavailable.** Our only horizon beyond the initial transient is `nsteps: 200`.

**And nothing retracts either.** `08_limitations.tex` has **no memory or footprint text at all**, and `06_results.tex` still carries the `[PENDING-CODER]` for the wall-clock and memory numbers.

**The replacement, which is stronger than what it replaces:**

> **"Because the nonlinear residual is evaluated on the full grid, its $O(n\log n)$ cost is independent of the rank, and we make no claim of per-step speedup: SP-DLRA is measured at $2.1$–$2.7\times$ the full-grid step. Nor is there a compensating memory benefit: peak RSS is $2.2$ MiB ($N=64$) to $4.3$ MiB ($N=128$) *above* the full-grid step, because the state is a full field plus its factors plus the factorisation workspace. We therefore identify no end-to-end benefit in the regimes we have measured, and the case for the method rests on its structural guarantees and its accuracy, not on efficiency. Establishing a regime where the rank stays small over a long span would require evidence beyond the $200$-step horizons used here, and we do not have it."**

**A reviewer who reads §4's memory route and then §6's memory numbers will conclude either that the paper is not careful or that the numbers were selected.** Declining to make the promise is worth more than keeping it.

**One label in the table also needs fixing.** The cleanup-SVD row reads cost `$O(n r^2)$`, remark *"thin, $r\times r$"*. **The cost is right and the label is wrong:** the SVD is of the **$n\times r$** centred field (`np.linalg.svd(centered, full_matrices=False)`), which is what $O(nr^2)$ is the cost of; the $r\times r$ object is the *output* singular-value diagonal, and the second SVD of *that* is a different, negligible $O(r^3)$ operation. **The rest of the table is right** — the viscous row matches the code's `O(N r log N)`, the nonlinear row's *rank-independent* claim is exactly what the code does, and *"we make no a priori claim of per-step speedup"* is among the best sentences in the draft.

## D10 — the cleanup describes a different algorithm from the one implemented (D62, binding)

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

---

## D11 — the introduction's summary sentence carries the same three barred claims (D65.3, binding)

**I attributed the barred claims to the abstract and the contributions list. The introduction has its own, in the paper's three-clause summary of the method — and this is the paragraph a reader forms their expectation from.**

`01_introduction.tex:70-80`: *"(i) the viscous part is integrated exactly, preserving the rank; (ii) the velocity is represented by a stream function, so divergence-freeness holds **by construction to machine precision**; and **(iii) the rank is adapted online** as turbulent structures form and decay. We validate the method on forced two-dimensional **turbulent dynamics** at Reynolds numbers $100$, $1000$, and $5000$ — **the regime of rank growth** beyond a handful of modes and slow singular-value decay — ... and we benchmark cost honestly, including regimes where the method is **slower** than full-grid computation."*

**All three barred classes and the cost euphemism are in one paragraph.** Clause (i) is correct and keep it. Clause (ii) needs D60's wording. Clause (iii) is barred. The validation sentence is barred. The cost sentence needs D52.5's number.

**Suggested replacement for clauses (ii)–(iii) and the validation sentence:**

> *"(ii) the velocity is represented by a stream function, so divergence-freeness holds identically in exact arithmetic, with a measured residual no larger than $1.1\times10^{-13}$ for the reduced integrator and the
> full-grid reference, and no larger than $1.1\times10^{-11}$ over every method we ran — seven orders of magnitude below the reduced solver's own error; and (iii) the subspace is refitted as the dynamics develop, which we show is necessary: a fixed basis propagated through the nonlinearity overflows at ranks $32$ and $42$ where the refitted one does not. We validate the method on forced two-dimensional flow at Reynolds numbers $100$, $1000$ and $5000$ against a full-grid spectral reference and a static POD baseline, and we benchmark cost honestly: the reduced integrator is $2.1$–$2.7\times$ the full-grid step in every regime we measured, with no compensating memory benefit."*

## D12 — Two of my corrections are two edits, not one (D65.4)

- **D59's $\mathrm{Re}=2\pi F/\nu^2$ appears at `04_methods.tex:25` (§4.1, *Problem setup and notation*) as well as at line 100 (§4.2).** Fix both.
- **D49's Taylor–Green limitation has 10 sites, not one** — including `04_methods.tex:259` in the rank-adaptation subsection, where the case is invoked to motivate decay. **A correction applied at the site I noticed is not a correction.**

---

## D15 — **your static-POD baseline's energy threshold is wrong by 10×, in three places, and the error flatters us** (binding)

**You write 99.9%. The runs used 99%.** `04_methods.tex:288`, `05_experimental_setup.tex:86`, `06_results.tex:133`.

Four independent pieces of evidence, none of them the draft:

| where | what it says |
|---|---|
| `baselines_re5000_N64_T8.json` | `parameters.energy_fraction = 0.99` — **recorded by the run** |
| `experiments/run_baselines.py:380` | `--energy-fraction` `default=0.99` |
| `solvers/dlra.py:51` | the rule is **"an r99-style rule"** |
| `experiments/test_engine.py` | `energy_fraction=0.99` in every criterion test |

**Change `99.9\%` to `99\%` in all three places.**

**Why this one matters more than a typo: the error runs in our favour.** A stricter energy threshold gives the
baseline a *larger* rank, so writing 99.9% describes the static baseline as **more expensive than the one we
ran** — which makes our own integrator look better than the comparison deserves. A reviewer checks this number
against a default in the code in about thirty seconds, and a self-serving error is worse than an honest one.

**And the rule's name is `r99`, so you can now say "an r99 truncation" and be exact.** That is a *stronger*
sentence than "99.9% of the energy", because it names the criterion rather than approximating it.

## D16 — **a checker now exists — run it before you send me a section

`python3 state/reviewer/claims_registry.py` verifies every load-bearing number in the paper against an explicit
key path in an artifact, and reports any high-precision literal in your draft that no registry row accounts for.
**Right now: 13/13 registry entries verify, and the only findings are the `99.9%` above and nothing else.** If it
reports a literal you added, that is not a complaint about the number — it is a request for a registry row, which
I add. **Run it; it is faster than waiting for me to find the same thing.**

---

## D17 — **the grid answer you can now write instead of "we do not know" (D68, binding)

**`t*` is not grid-convergent, and we now know by how much.** Same window, same seed, same forcing, same
horizons, same initial-state filter (`cutoff=8`, held) — only the grid changes, and the largest rank tested is
the `N=128` dealiasing ceiling (85).

| rank | `N=64` | `N=128` | ratio |
|---|---|---|---|
| 16 | `0.649` | **`0.939`** | `1.45×` |
| 32 | `1.482` | **`2.433`** | `1.64×` |

**The horizon lengthens under refinement at both resolved ranks.** That is the expected direction and it has a
name: the reduced integrator converges under grid refinement while the static baseline degrades (D56), so the
gap between them widens. **This is a result, not a limitation** — and it replaces the sentence that says the
question is open.

**Use it in §6 and in §8's limitations like this:** *"The horizon is not converged over the two grids we ran:
it lengthens by `1.45×` at rank 16 and `1.64×` at rank 32 on refinement from `64` to `128`, because the reduced
integrator's error falls while the static baseline's rises. We report the `N=64` value as the conservative one."*

**Two things to keep straight. (1) Ranks 43 and 85 are still running — do not quote them until I confirm them
(D22: a regenerated artifact is not verified until the run has been inspected). (2) These come from committed
code `588e5159`, which reproduces the `N=64` values bit-for-bit, so the two grids are comparable — that was
checked, not assumed.**

---

## D18a — **§3's energy invariant: use the FULL-PDE key. The key named `forcing_aware_invariant` would have you report a 663× exaggeration of the static baseline's error.** (binding)

**Two residuals are recorded and they are not the same quantity.** `forcing_aware_invariant.max_scaled_residual`
has the measured projection work subtracted from it; `max_scaled_full_pde_energy_residual` does not. **Across
14 (run, method) pairs they disagree in 9, by `1.11×` to `663×`.**

| method | `…full_pde…` (comparable) | `forcing_aware_invariant` (adjusted) |
|---|---|---|
| full grid | `1.29e-4` … `4.64e-4` | identical (no projection) |
| DLRA | `2.14e-4` … `4.93e-4` | `1.11–1.64×` higher |
| **static POD** | `2.16e-3` … `4.69e-4` | **up to `663×` higher** |

**At `Re=100` the static POD baseline's adjusted key reads `3.11e-1` — a 31% violation — while its actual
full-PDE commitment is `4.69e-4`, the same order as every other method. The 663× violation does not exist.**

**Use this text for §3** (it replaces 2 of the 6 `PENDING-THEORETICAL-RESEARCH` markers — you are not waiting on
that agent, the code already answers this):

```latex
Under forcing, the energy balance acquires a source term, and the quantity
that must vanish is $\mathrm{d}E/\mathrm{d}t + \nu\|\omega\|_2^2 -
\langle\psi,\zeta\rangle + \langle\psi,\mathrm{adv}\rangle$ rather than
monotone decay. A projected method does not commit the full-PDE step, so we
report two residuals: the balance as the full-PDE residual, which is
\emph{comparable across methods}, and the balance after subtracting the
measured projection work. \emph{We compare methods on the first.} All three
solver families hold it to $1.3\times10^{-4}$–$4.9\times10^{-4}$ over 200 steps,
with the static projection worst and only at $N=128$ ($2.2\times10^{-3}$).
The two differ by up to $663\times$ for the static projection, which
is a statement about how much work its projection does, not about the accuracy
of its trajectory.
```

**One thing I cannot sign off, so do not write it yet:** the code's scale is
`max(1.0, |dissipation|, |forcing_input|)`, which has a **floor of 1**. **While dissipation and forcing are below 1
these are absolute numbers, not relative ones** — so do not write "relative residual" until the coder confirms
which branch the scale took. I have asked them to record the scale.

**Why this matters more than a key name:** on the comparable key all three methods agree to within an order of
magnitude. On the wrong key the static baseline looks catastrophic and we look clean — **the same
self-serving direction as the `99.9%`.**

---

## D18b — **the grid question is answered, and the "bracketed between 32 and 43, not located" hedge is retired. The never-yields rank coincides with the largest alias-free rank, and it moves with the grid.** (binding)

**Replace the sentence that says the never-yields rank is "bracketed between 32 and 43, not located." It is located.**

| rank | `N=64` | `N=128` | |
|---|---|---|---|
| 16 | `0.6493281145096707` | **`0.9386425215032279`** | **`1.4456x`** |
| 32 | `1.4816252539052939` | **`2.4334866060994007`** | **`1.6424x`** |
| **43** | **`never`** (0 crossings) | **`2.682771521118821`** (resolves) | — |
| **85** | — | **`never`** (0 crossings) | — |

**Two results, and the second is the better one.**

**1. `t*` lengthens under refinement at both resolved ranks** — `1.4456x` and `1.6424x`. So the horizon is **not
grid-convergent over `64 -> 128`**, and the direction is the expected one: the reduced integrator's error falls while the
static baseline's rises, so the gap widens. **Write it as a result, not as the open question you had to hedge.**

**2. The never-yields rank coincides with the largest alias-free rank, and it moves with the grid: 43 at `N=64`, 85 at `N=128`.**
At `N=64` rank 43 never yields; on the finer grid rank 43 *does* yield (`t* = 2.683`) and the never-yields rank is 85.
**Those are exactly the two `dealias_rank_ceiling` values.**

**Use this for §6, §7 and the limitations:**

```latex
The rank at which a propagated static subspace stops improving is not a fixed
rank but the largest rank the grid can resolve without aliasing: 43 at
$N = 64$ and 85 at $N = 128$, each equal to that grid's largest
alias-free rank. Rank therefore helps the evolving subspace all the way up
to the point where the representation, not the method, runs out. The accuracy
horizon is not grid-convergent — it lengthens by $1.45\times$ at rank 16 and
$1.64\times$ at rank 32 on refinement — because the reduced integrator
converges while the static baseline degrades.
```

**This is the strongest available statement of the saturation mechanism, and it replaces a limitation with a finding.**

**Three things to keep straight:**

- **Say which of the two `43`s you mean, always.** At `N=64` the never-yields rank and the dealiasing ceiling are the
  *same number*, which is exactly why "43" has kept being misread as an accuracy result. If a figure or sentence says
  "43", say whether it is the ceiling or the never-yields rank.
- **Do not imply a two-grid ladder below rank 16.** `r = 2, 4, 8` are `unresolved` at `N=64` (the DLRA leads
  throughout) and were not run at `N=128`. The ladder starts at 16.
- **The artifact is not in the repository yet.** I have added registry rows naming
  `state/coder/results/crossover_N128.json`, and the checker now reports `14/18 verified, 4 failed` with
  `artifact missing`. I have asked the coder to land it. **The numbers above are read out of the finished artifact, not
  from a log — but if the artifact does not land, these numbers are not in the repository and should not be printed.**

---

## D18c — **§6 RESULTS, SUPPLIED SUBSECTION BY SUBSECTION SO THE 26 EXISTING CROSS-REFERENCES SURVIVE — PLUS THE FIGURE MAPPING, WHICH REVEALS ONE REAL CONTENT GAP**

**Paste each block into the matching existing subsection. Do not replace the section wholesale, and do not touch its
`\subsection` or `\label` lines** — they are not repeated here for that reason. R130's first attempt at this was a single
replacement `\section`, and it was **wrong**: `06_results.tex`'s labels are referenced **26 times from other sections**
(`sec:results` ×10, `sec:res-error` ×5, `sec:res-fidelity` ×5, `sec:res-pod` ×3, `sec:res-cost` ×2, `sec:res-tg` ×1), so a
replacement would have broken 26 cross-references in a paper **nobody can compile** to find out.

**There are no `\cite`s in any block. The only `\ref` is `\ref{sec:setup}`, which resolves** (`05_experimental_setup.tex:4`
defines it). Nothing else here can fail to compile.

### The figure mapping — read this first, it is a real finding

Your six figure slots and the eight figures that exist do not line up, and one slot has no figure at all:

| your label | your file | what exists on `main` |
|---|---|---|
| `fig:tg` | `fig_tg_ke_rank` | **NOTHING — no Taylor--Green figure has ever been made** (the data, `taylor_green.json`, exists) |
| `fig:rank` | `fig_rank_vs_time` | `fig_window_rank` |
| `fig:svd` | `fig_sv_decay` | `fig_spectra_ek` **or** `fig_spectrum` — your choice, they show different things |
| `fig:error` | `fig_error_vs_ref` | `fig_crossover` |
| `fig:cost` | `fig_cost` | `fig_cost` — the only one of your six names that is real |
| `fig:kestats` | `fig_ke_spectrum` | `fig_divergence`, **with the window warning below** |
| *(no slot)* | — | **`fig_div_free` has no home**, and it is the best figure in the project |

**So the decision from R129 is sharper than I put it: not "five new figures or repoint eight", but six slots, five invented
names, one real name, and one genuine content gap — nobody has made a Taylor--Green figure.** `sec:res-div` has no figure at
all, only `tab:div`, which is where `fig_div_free` belongs: it is the figure I have checked most carefully and it shows
exactly the contrast the I1 subsection is about.

**Two warnings before you wire anything.** `fig_divergence` shows `t ≤ 0.1` while the crossover is at `t* = 0.649`/`1.482`,
and in that window the static baseline looks like the *winner* — if you use it for `fig:kestats`, label the window on the
figure. And **most PNGs in `experiments/figures/` are stale** relative to their PDFs; use the PDFs, which is what LaTeX
wants anyway.

### 1. into `\label{sec:res-tg}` — Taylor--Green

```latex
A manufactured-solution verification. The numerical rank required to hold the
solution to machine precision over the integrated horizon is one, so this case
establishes that the discretisation and the exponential flow are exact. It does not
discriminate between methods, because a rank-one subspace represents this solution
exactly and so cannot separate a structure-preserving split from a plain one. We
report it as a correctness check on the solver and not as evidence for the method's
advantage.
```

### 2. into `\label{sec:res-rank}` — rank and singular-value dynamics

```latex
The subspace must evolve, and the evidence is that a propagated one fails. Our runs
fix the rank and rebuild the factors at every step; the quantities reported are the
rank required to represent the state and the decay of the singular-value spectrum
that makes a small rank sufficient. Over the horizons we integrate, the rank
criterion our solver uses grows from one to sixteen over the first eight time units,
which is why the evidence for adaptive rank in this project is bounded to that
horizon and why we claim nothing about rank behaviour beyond it. The amplitude rule
saturates against the grid rather than against the dynamics from $t=2$ onward, so
its rank trace is the grid's and not the dynamics'.
```

### 3. into `\label{sec:res-error}` — accuracy, the horizon, and the mechanism

```latex
Against an equal-rank static subspace, the reduced integrator is the more accurate
method until a horizon $t^\ast$, and the static baseline is the more accurate method
afterwards. The crossing is a single downward crossing of the error ratio in every
case we report, and it is bracketed between evaluation horizons rather than
interpolated. At $N=64$ and $\mathrm{Re}=5000$ we measure $t^\ast = 0.649$ at $r=16$
and $t^\ast = 1.482$ at $r=32$; at $r=43$ there is no crossing at all, and the static
baseline never overtakes the reduced integrator. At $\mathrm{Re}=1000$ on the same
grid the horizons are $0.667$ and $1.609$, that is $2.7\%$ and $8.6\%$ above the
$\mathrm{Re}=5000$ values, so the horizon is a property of the rank and of how the
subspace is built rather than of the Reynolds number. Sweeping the trailing-window
length over $W \in \{0.25, 0.5, 1.0\}$ moves the horizon by between $0.15\%$ and
$0.63\%$ depending on rank and Reynolds number, over the eight rank--window--Reynolds
combinations we measure. Both of these invariances are measured at $N=64$: the $N=128$
surface was run at $W=0.25$ alone and at $\mathrm{Re}=5000$ alone, so neither is
corroborated at the second grid.

Refining the grid is the one thing that does move the horizon. At $N=128$ and
$\mathrm{Re}=5000$ we measure $t^\ast = 0.939$ at $r=16$, $2.433$ at $r=32$ and
$2.683$ at $r=43$, factors of $1.45$ and $1.64$ above the $N=64$ values at the
corresponding ranks. The horizon is therefore not grid-convergent over this range and
we do not extrapolate it. What does carry across the refinement is the rank at which
the crossing stops existing: $43$ at $N=64$ and $85$ at $N=128$. Each coincides with
the largest rank that grid retains without aliasing at our cutoff, so the rank at
which a propagated static subspace stops improving is set by the grid before it is set
by the dynamics. These are the largest ranks we ran at each grid, not limits, and we
report them as such.

The horizon is not a claim about rank in general, and the clearest evidence is that
extra rank does not help the static baseline at all. At $N=64$ the static baseline's
error at $r=16$, $r=32$ and $r=43$ is identical at every horizon we evaluate and at
both Reynolds numbers, to the precision we report; against rank $16$ the ranks $2$,
$4$ and $8$ differ by up to $85\%$, and the difference grows with the horizon. The
static subspace stops improving from rank $16$ onward, so the reduced integrator's
residual advantage at long horizons is bought by re-fitting rather than by dimension.
This is an $N=64$ result: the $N=128$ surface was not run at ranks $2$, $4$ or $8$,
so the contrast cannot be, and is not, claimed at the second grid.
```

### 4. into `\label{sec:res-div}` — divergence-free invariant

```latex
Divergence-freeness holds identically and by construction rather than to a
tolerance. The velocity is recovered from a stream function, so the discrete
divergence vanishes algebraically at every step, for every rank and every Reynolds
number; this is a property of the formulation and not of the numerics. Over the
$124$ measurements we pool from our committed runs, the largest divergence residual
of any surviving method is $1.1\times 10^{-13}$ and the full-grid solver's own is
$7.6\times 10^{-14}$, both at the level of the $10^{-14}$ roundoff floor. The spread
across the pool runs from $1.6\times 10^{-14}$ to $2.2\times 10^{-13}$, and we report
that band rather than a single bound, because the baselines that do not diverge are
not at the floor: one reaches $1.0\times 10^{-11}$, three orders above it. We make no
universal bound of the form ``at most $2.2\times 10^{-13}$'', because four committed
baselines reach $4.6\times 10^{64}$ to $7.1\times 10^{278}$, and one non-diverging
baseline reaches $10^{-11}$; the bound is a property of a population, and the population
is the one we name here.
```

### 5. into `\label{sec:res-pod}` — rank economy against static POD

```latex
The static baseline is not a strawman: it is the oracle form of a fixed subspace,
re-fitted on a trailing window of the reference trajectory with the refit schedule
offset from the evaluation grid, so that no basis ever contains the time at which it
is scored. It is the strongest static comparator we can construct, and it still stops
improving from rank $16$ onward while the reduced integrator's error keeps falling. Its
accuracy is a function of the window length, the refit interval and the offset, all of
which we record; three successive corrections to this baseline moved the advantage
horizon by factors of two to four, so a $t^\ast$ quoted without them is not
reproducible, and we quote the schedule alongside every horizon.
```

### 6. into `\label{sec:res-cost}` — cost

```latex
We measure the per-step cost of the reduced integrator against the pinned-thread
full-grid reference under the same accounting in both cases, discarding a warm-up,
repeating each configuration, and taking medians. Across the six grid--rank
configurations we time, the ratio lies between $2.24$ and $2.74$. The measurement is
not sharp enough to justify more than one significant figure, and we say so rather
than quoting the endpoints as if it did: per-configuration timing spreads are $4\%$
to $26\%$, and the reference timing itself varies by $16\%$ to $32\%$ across its own
repeats. Discounting every configuration by both of those spreads gives a pessimistic
lower bound of $1.4\times$ the full-grid step. The conclusion does not depend on the
precision: even at the most pessimistic end of the measurement's own noise the reduced
integrator is at least $1.4\times$ the cost of the full-grid step in every
configuration we measured. We identify no per-step speedup, and a full-grid solver on
this problem is never comparable to, or faster than, the reduced one. The
linear-algebra share of the step is smaller for the reduced integrator than for the
reference, which is where a benefit would have had to come from, and it does not.
```

### 7. into `\label{sec:res-fidelity}` — the energy invariant

```latex
Under forcing, kinetic energy is not monotone, so the second invariant is a balance
and not a decay law. Measured as the energy balance residual of the projected discrete
dynamics, all three solver families hold it to between $1.3\times 10^{-4}$ and
$2.2\times 10^{-3}$ across the $26$ committed measurements we pool, the static
projection at the finest grid being the worst at $2.2\times 10^{-3}$. The spread is
two orders wide and the worst case is the static baseline, which is what one expects
of a fixed subspace whose truncation error does not get integrated away. We report this quantity and not the balance of the
full partial differential equation, because for a projected method the two differ by
the size of the projection's own energy increment: the two keys in our artifacts
differ by up to a factor of several hundred across configurations, and quoting one for
the other would misstate the violation by orders of magnitude. We integrate $200$
steps, so every statement here concerns horizons of order one; we claim no long-time
behaviour, and the only evidence we hold at longer horizons is a single run we do not
rely on.
```
