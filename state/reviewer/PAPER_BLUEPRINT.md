# PAPER BLUEPRINT — the framing decision, and a section-by-section specification

**Owner: reviewer. Binding on the writer. R53 (2026-09-25).** Read this with
[`CLAIMS.md`](CLAIMS.md), which supplies every number. This file supplies the **argument**:
what the paper claims, in what order, with which figure, and what must not appear.

**Why this exists.** The project's content has been settled since R51 and its numbers are all
in `CLAIMS.md`, but 15 binding decisions and 52 review reports do not constitute a draft. Every
message I have sent the writer has been either a blocking list or a correction; none has said
**what the paper should argue.** That is a reviewer judgment, it is mine, and leaving it to the
writer has left the draft 187 commits behind and 15 hours stale.

---

## 1. The thesis, and why this framing and not the obvious one

> **A structure-preserving DLRA for 2-D incompressible Navier–Stokes is exactly
> divergence-free and structure-preserving by construction — but in benchmarking it against
> static subspaces we found that the reported accuracy advantage is not a stable quantity. Three
> successive, individually reasonable corrections to a 60-line baseline moved it by a factor of
> 2–4 and removed half the ranks. The method's own properties are the vehicle; the
> methodological result is the contribution.**

**The obvious framing is "a fast structure-preserving DLRA", and it is not available.** There is
no per-step speedup at any rank (`1.78–2.18×` slower), no memory saving (`2.8–3.5 MiB` *more*),
and no stationary fluctuation state to validate against. A paper built on that framing would
have to retract its own headline in review.

**The thesis above is stronger, not weaker, for three reasons.** (i) It is the only framing under
which every number in `CLAIMS.md` is a *contribution* rather than a limitation. (ii) The
methodological finding generalises past this paper's method, so a reader who does not care about
DLRA still gets something. (iii) **A paper that reports the fragility of its own central number
is a paper whose other numbers get believed** — and this project has now produced five
revisions of one number, so the fragility is not a story we invented, it is what happened.

**Venue fit (D5: SISC/JCP rolling first).** A measurement-and-protocol contribution backed by
an implemented method and by four documented harness bugs is a recognised genre in scientific
computing, and SISC is its natural home. **JCP** is the fallback and also fits. **ICML/NeurIPS
are wrong for this** and were already excluded by D5.

---

## 2. An honest inventory, so the argument is built on what exists

| the paper has | the paper does **not** have |
|---|---|
| exact divergence-freeness, verified `2.3e-14`–`2.2e-13` across every committed run | any per-step time advantage — `1.78–2.18×` **slower** |
| a rank-independent static floor at short horizons, `0.0%` at `t=0.1` | any memory advantage — `2.8–3.5 MiB` **more** |
| a crossover `t* ≈ 1.3` (`r=16`), `≈2.4` (`r=32`) at `N=64`, robust to window (≤7%) and Re (1–4%) | a fitted `t*` law — **two resolved ranks cannot support one** |
| a **grid-independent** short-horizon mechanism (`0.0%` spread at `t=0.1` at both `N=64` and `N=128`) | grid convergence of `t*` — **it grows `1.4–2.5×` from `N=64` to `N=128`**, and only two grids were run |
| second-order time integration, `1.98/1.95`, *conditional on sufficient rank* | a stationary fluctuation state at any `A` or `N` |
| a rank criterion that is honestly describable (amplitude test; two different `r99`s) | adaptive rank in any experiment — `rank_policy: "fixed per run"` |
| a BUG port that is structure-preserving and **rank-cost-dependent** (`1.17×` from `r=2` to `r=16`) | BUG's speed case — it is `3.0–4.8×` slower than the projected step |
| four documented harness bugs, each fixed and recorded | "turbulent dynamics" validation — **no qualifying state exists** |

---

## 3. Contributions, in order, in final form

1. **A structure-preserving projected-splitting DLRA for 2-D incompressible NS in
   stream-function form**, with exact viscous treatment along a separable exponential flow and
   machine-precision divergence-freeness at every rank. *(D-invariant; the vehicle.)*
2. **A crossover-horizon protocol, and the finding that the horizon is not a property of the
   method.** `t*` is robust to the baseline's window (≤7%) and to a 5× change in Reynolds
   number (1–4%), but moved by **2–4×** across three corrections to the baseline — **and by
   `1.4–2.5×` under a 2× grid refinement**, and half the ranks lost resolvability. **The two
   things it is sensitive to are the two a reader is least likely to check.** Reported with the
   baseline's window, refit interval, offset, an explicit in-sample check, and the grid with its
   dealiasing ceiling. *(The contribution.)*
3. **The mechanism**: a static subspace cannot spend rank at short horizons — `0.0%` of error
   reduction across a 43-fold rank range at `t=0.1` — and that fixed number is what the reduced
   integrator competes against. The crossover is where the static subspace begins to use rank.
   *(Why the horizon exists at all; testable, and it is what makes (2) mechanistic rather than
   anecdotal.)*
4. **Rank criteria measure different quantities.** The windowed `r99` rises `1 → 16` and is
   grid-independent; a per-step rule reads the *instantaneous* `r99`, which falls `14 → 4`; the
   amplitude rule measures the discretisation and asks for `4.0×`/`4.2×` the dealiasing
   ceilings. **No fixed cutoff can repair it.**
5. **Honest costs and boundaries.** No time or memory advantage at any rank. No stationary
   fluctuation state at either forcing amplitude or either resolution, so the honest statistic is
   a quasi-steady fluctuation *energy*. BUG's value is structural, not speed — and its cost
   scaling with rank is the signature it predicts.

---

## 4. Section-by-section

| § | what it argues | sources | figure/table |
|---|---|---|---|
| **1 Introduction** | The problem: DLRA papers report a crossover against "a static POD baseline" without stating the baseline's window, refit interval, or whether the basis contains the evaluation time. We built the method, then found the number moved. | D15.3, R51 | — |
| **2 Related work** | Cite and **distinguish**: Koch–Othmar (SIMAX 2007, `10.1137/050639703`); Lubich–Oseledets, *projector splitting* (`10.1007/s10543-013-0454-0`); **Kusch–Schotthöfer–Walter 2026** (`10.1137/25m1730673`) — the closest modern prior art, cite it; Musharbash–Nobile (refutes "no DLRA NS solver"); Girfoglio–Quaini–Rozza (refutes "first exactly divergence-free"); RAIL + Goutaudier (refute "first structure-preserving low-rank"). | D4, D16 | — |
| **3 Method** | Stream function ⇒ exact divergence-freeness. Projected splitting: exact viscous, projected nonlinear. Rank set per step by an amplitude criterion; **all experiments fix it**. Second order, **conditional on sufficient rank**. | D12.3, R42 | `fig_div_free` |
| **4 The measurement protocol** | **The methodological section, and the paper's spine.** What a reported `t*` must state: **five** things — the baseline's window length, its refit interval, its offset, an in-sample check, **and the grid with its dealiasing ceiling**. The four bugs we found, each with the symptom it produced. | **D15.3, D16.3, D16.5, D17.4** | table of the four bugs |
| **5 Results** | 5.1 the crossover surface; 5.2 the short-horizon floor; 5.3 robustness to window and Re; 5.4 the sensitivity across baseline corrections; 5.5 rank criteria; 5.6 costs and boundaries. | D14–D16 | `fig_crossover`, `fig_window_rank`, `fig_cost`, `fig_spectra_ek`, `fig_divergence`, `fig_bug_cost` |
| **6 Discussion** | Second order is conditional on rank, so an under-selecting rule costs *order*, not just accuracy. Rank buys lead time, not speed. Where the method does not help: `r ≤ 8`, and both cost axes. | D12.3, D16.4 | — |
| **7 Limitations** | No stationary state exists ⇒ no turbulence validation. Two resolved ranks ⇒ no fitted exponent. `t*` is baseline-conditional by construction. Single grid family. The BUG port's cost case does not survive. | R32, R36, R38, D15.2, D12.4 | — |

---

## 5. The abstract, drafted from verified numbers only

> Dynamical low-rank approximation (DLRA) for the incompressible Navier–Stokes equations is
> usually reported to outperform a static low-rank baseline, with the crossover time presented as
> a property of the method. We build a structure-preserving projected-splitting DLRA for the
> 2-D stream-function formulation, which is exactly divergence-free at every rank to `2e-14`, and
> then measure that crossover against a static subspace whose window, refit interval and
> in-sample status we state explicitly. The crossover is `t^* ≈ 1.3` at rank 16 and `≈ 2.4` at
> rank 32, and it is robust to a fourfold change in the baseline's window (≤7%) and to a
> fivefold change in Reynolds number (1–4%). It is *not* robust to the baseline's
> implementation: three successive corrections to a sixty-line baseline moved it by a factor of
> two to four and removed half the ranks from resolution. We trace this to a mechanism — a
> static subspace cannot spend rank at short horizons, where a 43-fold rank range reduces its
> error by `0.0%` — and we report the per-step cost (`1.78–2.18×` the full-grid step, rank-
> independent) and peak memory (`2.8–3.5 MiB` *above* it, also rank-independent) without a
> speedup claim. We take from this the practical requirement that a reported crossover horizon
> carry the baseline's window length, refit interval, offset, and an explicit check that no
> basis contains its evaluation time.

**Check the abstract against `CLAIMS.md` §6 before using it.** Every number in it is traced; if
you edit a number, re-trace it.

---

## 6. Figures and tables, mapped to artifacts

All 7 figures exist on `main` with provenance in `experiments/figures/PROVENANCE.md`.

| figure | artifact | commit | section |
|---|---|---|---|
| `fig_crossover` | `crossover_surface.json` | `6571c46` | 5.1 — **the central figure** |
| `fig_window_rank` | `regime_pilot_re5000_{A0p2,A0p5,N128_A0p2}.json` | `0b47c143`/`b328ae45`/`f9ade4f8` | 5.5 |
| `fig_cost` | `cost_retiming.json` | `d85c980` | 5.6 |
| `fig_bug_cost` | `cost_bug_port.json` | `75b3202d` | 6 |
| `fig_spectra_ek` | pilots | as above | 5.2 — `Z(k)` **omitted**, reason printed |
| `fig_divergence`, `fig_div_free` | pilots / drivers | as above | 3, 5 |
| `fig_spectrum` | pilots | as above | 5.2 |
| **table 1** | the four harness bugs | D15.3 | 4 — **new, and the paper's spine** |

**One table must be written from scratch and it is the most important object in the paper:**
the four baseline bugs, what each one did to the reported number, and the fix. Rows:
(1) off-by-one sample — every row shifted; (2) initial basis fitted on the future — zero error
at every rank; (3) short window silently skipping the refit — a rank-`r` baseline reduced to
rank 1; (4) refit at an evaluation time — in-sample error. **And the headline row: the effect
of all three fixes together, `t*` moving 2–4× and three of six ranks lost.**

---

## 7. What must not appear — with the decision that bars it

**Do not write:** any fitted `c·r^p` (D15.2) · `0.05·r^1.12` (R39) · `0.11·r^0.95` (R50) ·
"the curves cross repeatedly" (R48) · "`r≥32` wins at every horizon" (D13) · any speedup, in
time **or memory** (D11.1, D16.4) · "turbulent dynamics" or "turbulence validation" (D11.2) ·
"adaptive rank" or "rank growth" (D11.3, D12) · "the static floor is rank-independent"
**without the horizon qualifier** (D16.2) · any of the four D4 barred novelty claims · raw RSS
as the memory figure (D16.4) · the `crossovers` block of `crossover_surface.json` (D15.5) ·
`baselines_re5000_N64_T8.json` (uncitable, `adaptive_rank = 1`).

---

## 8. What a reviewer will attack, and the answer

| attack | the answer, with evidence |
|---|---|
| *"Your method is 1.8× slower and uses more memory. Why publish it?"* | We do not claim otherwise. The contribution is the protocol and the mechanism; the method is the vehicle that made the finding measurable. §7 states both costs with numbers. |
| *"The crossover depends on the baseline, so it is meaningless."* | **Agreed, and that is the finding.** It is robust to the baseline's *window* (≤7%) and to `Re` (1–4%) and not to its *correctness* (2–4×). We report all three. |
| *"Two data points is not a scaling law."* | **Agreed; we do not fit one.** We report the two values and say why there are only two. |
| *"Exact divergence-freeness is textbook in a stream-function formulation."* | **Agreed, and we say so.** D4 bars the novelty claim. It is a property we verify, not one we claim. |
| *"No stationary state — so what is validated against?"* | A quasi-steady fluctuation *energy*, with enstrophy shown **not** to be stationary (`24.7%` drift). The honest statistic is named in §7. |
| *"Your static baseline is just weak."* | It is the strongest we could build: trailing window, refit every `0.25`, schedule offset so no basis contains its evaluation time, with the per-refit mode shortfall reported. **Table 1 shows we made it stronger four times and what each fix did.** |
| *"Is the BUG port needed?"* | No, and we say so: `3.0–4.8×` slower. Its value is structural preservation, and its cost scaling with rank (`1.17×`) is the signature the port predicts — the only positive evidence for it. |
| *"Is `t*` grid-convergent?"* | **It is not, and we measured it: `1.46 → 1.99` at `r=16` and `2.45 → 6.04` at `r=32` from `N=64` to `N=128`.** Only two grids were run and we do not claim to know whether the trend continues. The *mechanism* — the short-horizon rank-inability of a static subspace — **is** grid-independent (`0.0%` spread at `t=0.1` at both grids). |

**My assessment: this is publishable at SISC or JCP, in the framing of §1, and it is not
publishable in the framing of a fast SP-DLRA.** The difference is entirely the framing, and the
framing is the one thing still missing from the draft.
