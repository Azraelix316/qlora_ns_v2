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
11. the `N=128` multipliers `1.46→1.99` / `2.45→6.04` — **unverified, do not print**
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
