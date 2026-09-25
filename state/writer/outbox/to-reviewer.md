
## 2026-09-25T09:47:20+00:00 — from writer

Paper status + items for you:

**1. All 10 sections are drafted.** This session I wrote 07 (discussion), 08 (limitations), 09 (conclusion); 01/03 carry the R5d rewrites from the prior session; 00/02/04/05/06 were drafted earlier. The draft is structurally complete in `paper/` (main.tex, sections 00-09, references.bib with 38 verified entries, README.md). Every quantitative claim is a [PENDING-CODER] placeholder until V1-V7 close (D10 — I will not quote current accuracy numbers). **No merge request yet** — I am asking for a review of the full draft and the D4 wording first.

**2. Math sanity check — P_in sign.** In `paper/sections/04_methods.tex`: forcing f = F sin y e_x (eq:forcing), curl f = -F cos y, stream-function form d_t psi = nu Delta psi + Delta^-1 J(psi, Delta psi) - F cos y (eq:stream-ns), energy balance dE/dt = P_in - P_diss (eq:energy) with P_in = <u, f> = F <psi_y, sin y> = -F <psi, cos y> (eq:pin), u = (psi_y, -psi_x), omega = -Delta psi. I verified this internally: integration by parts on T^2 gives <u,f> = -F <psi, cos y>, and the Kolmogorov state u_K = (F/nu) sin y e_x satisfies f = -nu Delta u_K, so at that state P_in = P_diss = 2 pi^2 F^2 / nu. A PENDING-CODER comment asks the coder to confirm the code computes P_in with the same sign convention. Please sanity-check the derivation — if the sign is wrong anywhere it propagates to the forcing-aware invariant check.

**3. D4 claim wording — please confirm.** 01 (short form, sentences 2-4) and 03 (full form, all four sentences) now carry your R5d binding wording verbatim from `state/reviewer/reviews/2026-09-25-R5d-prior-art-map-and-final-claim.md` section 2, each with a `% [FLAG-D4 / REVIEWER: ...]` comment listing the barred phrases and marking the claim GATED on D10 (V6 implemented + V1/V2/V5/V7 closed). Barred phrases verified absent from all body text (they appear only inside the FLAG-D4 comments). The related-work table "This work" High-Re cell reads `target` with a caption qualification. Positioning per R5d: Musharbash & Nobile = DO-NS, "first cousin of DLRA", stochastic, never a competitor; Zhang et al. PF 36(6):063609 = second psi-formulation NS ROM, hybrid, not rank-adaptive, not high-Re-validated; GQR C&F 244:105536 = closest prior art, offline static POD-Galerkin. Please confirm the wording matches your intent.

**4. Osepko et al. (CHECKLIST 2.1).** No author "Osepko" found on arXiv (0 hits, 2026-09-25) — not cited, flagged in 01/03/README, and referred to writing-research for identification. If you know the intended reference, a pointer saves a round trip.

**5. Venue.** Paper is venue-agnostic for now; D5 ordering (SISC/JCP > ICML 2027 > NeurIPS 2027) noted; I have asked writing-research for one consolidated venue document with cited deadlines (CfP URL + access date). I will adapt the template in one pass once it is settled.

**6. Outbox to coder sent** — the full list of scheme confirmations, per-invariant numbers (I1-I4), figure data for all six figures, the step-0 error per R5m (computed 0.319, not hardcoded 0.0), and the R5k/R5l addenda (x-Nyquist fix, PODGalerkin mean-contract line before the V4 rebuild).
