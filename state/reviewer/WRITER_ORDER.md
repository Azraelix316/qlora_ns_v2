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
| **5** | **§6 Results** | the horizon, the mechanism, robustness, the rank criteria, the costs | **`t*` = `0.649`** (`r=16`), **`1.482`** (`r=32`); window sensitivity **`0.15–0.63%`**; Reynolds **`2.8%` / `8.6%`**; **no per-step speedup** (`1.78–2.18×` slower), **no memory saving** (`+2.5` to `+3.8 MiB` *more*) |
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
