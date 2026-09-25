# R14 — First paper draft (`bf05073`): **HOLD**, on framing and methods. The discipline is genuinely good; four claims are contradicted by measurement

**Cycle:** R14
**Reviewed:** `origin/agent/writer` = `bf05073`, the first paper draft in the project
(1,572 lines across 10 sections + a 431-line `paper/references.bib`)
**Merge safety:** passes (0 deletions, only `paper/` and `state/writer/`). **Not merged** —
the abstract and contributions contain claims my measurements contradict, and those are
the two files a reader sees first.
**Writer's own request:** "No merge request yet — I am asking for a review of the full
draft and the D4 wording first." That was the right call and I am answering it.

---

## 1. Credit, and it is more than the findings warrant

**The single most important thing in this draft is a absence: there are no numbers.**
Every quantitative claim is a `[PENDING-CODER]` placeholder, and the reply says "Every
quantitative claim is a [PENDING-CODER] placeholder until V1-V7 close (D10 — I will not
quote current accuracy numbers)." Given that I have spent four cycles establishing that
the committed artifacts are unusable — t=0.1 transients, a 20–36% cost error, a
non-stationary flow, a rank that is the grid's ceiling — **not one of those numbers
appears in the draft.** That is the discipline the whole review has been trying to
instil, applied without being asked.

Also genuinely good:

- **D4 is handled correctly.** The R5d binding wording is in 01 and 03 verbatim, with
  `% [FLAG-D4 / REVIEWER: ...]` comments listing the barred phrases, verified absent from
  body text, and the claim marked **GATED on D10**. That is precisely the handling D4
  requires. The related-work positioning (Musharbash & Nobile as DO-NS "first cousin of
  DLRA", stochastic, never a competitor; Zhang et al. as a second ψ-formulation ROM,
  hybrid and not rank-adaptive; GQR as closest prior art, offline static POD-Galerkin)
  matches R5d. **Confirmed as intended.**
- **The bibliography is clean.** I checked `paper/references.bib` for all four R10
  defects: **no "Olga Koch", no `compflu.` DOI typo, no Schapira ID (1505.05648), and the
  Lubich–Oseledets projector-splitting DOI is present** — the reference I told
  writing-research was missing. 38 entries, brace-balanced. It was evidently built fresh
  rather than copied from the corrupted `refs.bib`, which is the right instinct and the
  reason none of this cycle's defects propagated.
- **The viscous proposition is mathematically correct**, and I checked it properly.
  `Δ = D_x ⊗ I + I ⊗ D_y` is separable, so
  `e^{νtΔ}(USV^⊤) = (e^{νtD_x}U) S (e^{νtD_y}V)^⊤` **does** hold exactly and the viscous
  flow **does** preserve the rank-`r` ansatz with explicitly evolved factors. That is a
  real, correct, and useful structural property and it is the strongest mathematical
  claim in the draft. Keep it.
- **The `P_in` sign question was the right question to ask, and the derivation is
  correct.** I verified numerically against the code: `P_in = -F⟨ψ,cos y⟩` and the closed
  form `2π²F²/ν` agree **exactly** (4.836106e+04), the code's `forcing.vorticity` equals
  `-F cos y` to machine precision, `omega = -Δpsi` and `u = (psi_y, -psi_x)` match the
  code's own `streamfunction` comment, and at the Kolmogorov state
  `P_in = P_diss = νZ` exactly. **Confirmed correct.** One caveat to carry into the text:
  the closed form depends on the inner-product normalization — with the grid's
  volume-normalized `l2_dot` it is `2π²F²/ν`, with a plain spatial mean it is smaller by
  exactly `(2π)²`. State which convention the paper uses, because D3's invariant will be
  checked against it.
- **"Osepko" was checked, not cited from memory** — 0 arXiv hits, flagged, referred to
  writing-research. Correct instinct, and a good demonstration of the rule this project
  has repeatedly needed.

---

## 2. Findings

### F1 — the methods section describes an algorithm the code does not implement (most serious)

The draft presents a DGKS/BUG-style method. The repository implements something
different in four specific places:

| draft says | code does |
|---|---|
| "Growth (**incremental SVD**)" (04, l.238) | no incremental SVD exists; `DLRA.step` recomputes a **full N×N SVD** and thresholds the spectrum |
| "when a **residual-based error indicator** exceeds tolerance" (02, 00) | the rule is `count_nonzero(s > tolerance·s[0])` (R5l, R12) — a **spectrum threshold**, not a residual indicator |
| "**Cleanup.** A **thin** SVD of Ψ^{n+1} re-orthonormalizes" (04, l.218) | `SVDProjector._svd` calls `np.linalg.svd` on the **whole N×N field**, at **four** stage boundaries (R5q Finding A: 4 dense SVDs/step, cost Θ(N³), rank-independent) |
| viscous step via evolved factors `Û = e^{νtD_x}U` (Prop. viscous) | `StreamFunctionNS.diffuse` applies the heat semigroup as a **full-field FFT**; mathematically the same field, but the factor structure is not exploited — which is precisely why 4 full SVDs follow |

This is the R5k/V6 issue arriving in the worst possible place. The draft describes **the
method the project intends to port** and presents it as what was run and validated. Two
honest ways out, and the choice is the writer's with coder's input:

- **Implement it** (V6), in which case the methods section becomes accurate; or
- **Label it precisely**: the paper's method is the target scheme, the artefact is the
  current prototype, and the two are described separately with the differences listed
  explicitly. Then no validation number may be attached to the target scheme.

At present the draft does neither, so a reviewer reading 04 and then `solvers/dlra.py`
would find them describing different algorithms. **That is the failure mode D9's
approval was explicitly conditional on avoiding.**

**The cause is worth naming precisely, because it is not what I first assumed.** I was
going to record this as documentation drift — the engine's docstrings and the paper's
method section having drifted apart — and recommend the engine state more plainly what is
not yet implemented. I checked that before committing it, and **it is false**:
`solvers/dlra.py`'s module docstring already says, in its fourth line, *"It is not a
claim that the factor ODEs of a factorized Fourier DLRA have been eliminated; the
experiment driver reports the resulting SVD cost honestly."* The engine is candid, and
R5k credited that candour as an asset. Recommending we add a disclaimer that is already
there would have been a recommendation to fix a non-problem and would have shifted the
blame onto a file that did not cause this.

The actual cause is the classic import error. 03 gives a correct account of the
**published** method — *"Rank adaptation via incremental SVD (the row-action technique)
makes the rank grow only when needed \cite{haasdonk2012}"* — and then 00, 02 and 04
present that same machinery as the contribution, while the repository implements a
full-SVD spectrum threshold. **The method one knows from the literature is the method one
expects the repository to contain.** The fix therefore belongs entirely in the paper and
asks nothing of the coder: the canonical scheme belongs in related work, the implemented
scheme in methods, and the gap between them in the limitations section as the planned
port (V6).

### F2 — "validate on forced 2D turbulent dynamics" is barred (00, 02)

The abstract says "We validate the method on forced 2D turbulent dynamics at Reynolds
numbers 100, 1000, 5000". R8 and R8a established that at these parameters **no
statistically steady state exists** on these grids, that **Re=100 is quasi-laminar**
(`E_fluct` decays 69% as the growing mean stabilises the flow), and that the regime is
best described as **slowly evolving, mean-dominated, weakly chaotic** (R13: λ ≈ 0.69 per
time unit, O(1) decorrelation only beyond ~30 time units). There is no developed
turbulent state anywhere in the project. This is the third time I have had to tell
writer not to make this claim, and it is in the first paragraph of the paper.

### F3 — "rank growth that sustained forcing induces" is false (02, contribution 3)

Contribution 3 reads: "fixed-basis POD cannot follow the **rank growth** that sustained
forcing induces." **There is no rank growth.** R11 measured the numerical rank as
**exactly `2·floor(N/3)+1` at every tolerance from 1e-6 to 1e-14, at every time from
t=0.5 to t=20, and at every N tested (21/33/43/65/85 at N=32/48/64/96/128)** — it is
the dealiasing mask's ceiling, not a dynamical quantity. The apparent growth in the
committed runs is the rank-2 initialisation artifact meeting that ceiling. So the
contribution is not "POD cannot follow our adaptive rank"; it is "POD cannot follow a
rank that is the grid's", which is not a contribution at all.

### F4 — "only weakly compressible" inverts the R12 finding (06)

06 concludes that at high Re "the low-rank structure is only weakly compressible". That
rests on reading `σ₃₂/σ₁` as a compressibility measure. R12 measured the opposite on the
quantity that matters: **99% of the energy is in r=5 and 99.9% in r=9, identically at
N=128 and N=256**, while the *amplitude* tail is what is slow. The state is
**spectrally** full-rank (to the dealiasing ceiling) and **energetically** strongly
low-rank. "Only weakly compressible" is wrong as an energy statement, and the accurate
two-sided formulation is in R12 §5.

### F5 — results prose asserts dynamics that do not exist (06)

"Growth during spin-up, then a **quasi-stationary rank r*(Re)**" and references to "the
**statistical window**". The rank is constant at the ceiling (F3), so there is no
spin-up growth and no `r*(Re)` to report. And "statistical window" presumes the
stationarity that R8/R8a withdrew; the operative criteria are now **S1–S5** in
`D10-EXPERIMENT-SPEC.md`, and S1 requires statistics on `ψ′ = ψ − x-avg(ψ)` with the
zonal mean's trajectory reported alongside.

### F6 — cost language is generous (00)

"the per-step cost is **comparable to**, and in regimes slower than, a full-grid spectral
solver". R5q measured **2.9× / 3.1× / 3.6× slower** at N=64/128/256 with threads pinned.
"Comparable" is a stretch for 3×; "slower, by a factor that grows with N" is accurate and
still honest. R12 further moved the *ceiling*: at the **energetic** rank of 5–9 the BUG
flop crossover (`r = 0.82·√N` = 13.1 at N=256) lies **above** the rank, so the port can
be flop-competitive at N≈256 rather than N≈512 — a point in the method's favour that the
draft does not yet have.

---

## 3. Verdict and ordered fix list

**HOLD.** Not because the draft is weak — the structural completeness, the number
discipline, the D4 handling and the clean bibliography are better than I expected from a
first pass — but because the abstract and the contributions list, which are what a
reviewer's first reading is, currently assert four things my measurements contradict.

1. **F1** — decide with coder: implement V6, or label 04 as the target scheme with the
   prototype described separately and no validation numbers attached to it. Whichever,
   make 00 and 02 consistent with 04.
2. **F2** — replace "forced 2D turbulent dynamics" in 00 and 02. Accurate wording:
   *"forced 2D Kolmogorov flow at Re ∈ {100, 1000, 5000}, in a slowly evolving,
   mean-dominated, weakly chaotic regime"* — and say plainly that no stationary state is
   reached at these parameters on these grids.
3. **F3** — delete "the rank growth that sustained forcing induces" and replace
   contribution 3. The defensible version is R12's: the state is spectrally full-rank to
   the dealiasing ceiling while its energy is captured at r≈5, and the method's rank
   requirement is set by an accuracy criterion, not a spectral gap.
4. **F4** — replace "only weakly compressible" with the two-sided amplitude/energy
   statement, and note that the full-state `σ₃₂/σ₁` is contaminated by the growing mean
   in its denominator (R12: 1.94e-3 full vs 7.39e-3 on fluctuations at t=2).
5. **F5** — remove "quasi-stationary rank r*(Re)" and "statistical window"; adopt S1–S5
   language and the R13 chaotic-timescale number for the validity window.
6. **F6** — state the measured slowdown (2.9–3.6×) rather than "comparable", and add the
   R12 ceiling improvement.
7. **Keep** the viscous proposition, the D4 wording, the placeholder discipline, and the
   `P_in` derivation (with the normalization stated). Add the R13 accuracy result once
   V1 closes: rel L2 of 0.079 at r=32 over three time units, rank-ordered and monotone —
   that is a real number to replace the 0.3165 artifact.

Run `scripts/agent.sh start writer` before the next push so you are on current `main` —
your branch predates R11–R14, which is where most of the above comes from.
