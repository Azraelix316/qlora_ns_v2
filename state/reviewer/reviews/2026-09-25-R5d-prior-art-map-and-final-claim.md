# R5d — the prior-art map, and the final permitted novelty claim

**Date:** 2026-09-25 · **Reviewer cycle:** R5 (addendum 3) · **Purpose:** settle
D4 with reviewer-verified evidence rather than arXiv-only searches, since the
claim is the paper's spine and a wrong claim is fatal at review.

Every DOI below was resolved through the Crossref works API on 2026-09-25 and
every arXiv ID through its abs page. Where I could obtain the paper itself, I
checked its contents (see the Koch–Lubich note).

---

## 1. What the searches found

**(a) The two foundational DLRA papers contain no Navier–Stokes.** I
downloaded Koch & Lubich (2007), *Dynamical Low-Rank Approximation*, SIAM J.
Matrix Anal. Appl. 29(2):434–454, DOI 10.1137/050639703, from the author's own
site and extracted all 21 pages: **zero** occurrences of "Navier", "Stokes",
"stream function", "vorticity", "advection", "turbulence" or "Kolmogorov". Its
three numerical examples are time-dependent data-matrix problems. Nonnenmacher &
Lubich (2008), *Dynamical low-rank approximation: applications and numerical
experiments*, Math. Comput. Simul. 79(4):1346–1357, DOI 10.1016/j.matcom.2008.03.007,
applies DLRA to (verbatim from the abstract) "latent semantic indexing for
information retrieval, … compression of series of images, and … time-dependent
partial differential equations, specifically on **a blow-up problem of a
reaction-diffusion equation** in two and three spatial dimensions." No NS.

**(b) But "no dynamical low-rank method for incompressible NS" is FALSE**, and
this is the correction that matters:

> **Musharbash, E. & Nobile, F. (2018). *Dual Dynamically Orthogonal
> approximation of incompressible Navier Stokes equations with random boundary
> conditions.* Journal of Computational Physics 354:135–162.
> DOI 10.1016/j.jcp.2017.09.061**

Dynamically orthogonal (DO) approximation is a first cousin of DLRA — same
family of tangent-projected, factorisation-based, on-the-fly low-rank
reduction — and it has been applied to incompressible NS in a top venue. With
its error analysis (Musharbash, Nobile & Zhou, SISC 37(2):A776–A810, 2015,
DOI 10.1137/140967787) this is prior art a reviewer will know. Any claim of the
form "no dynamical low-rank method has been applied to incompressible NS" would
be refuted in one sentence. Note it is *stochastic* (random boundary
conditions), a different projection (DO rather than DLRA), and not a
high-Re deterministic turbulence study — so the gap survives, but only if stated
correctly.

**(c) Structure-preserving / robust low-rank for conservative PDEs is
established elsewhere**, which narrows what "SP-DLRA" can mean as a novelty:

| Work | Setting | DOI / ID |
|---|---|---|
| Nakao, Qiu & Einkemmer (2025), *Reduced Augmentation Implicit Low-Rank (RAIL) Integrators for Advection-Diffusion and Fokker–Planck Models*, SISC 47:A1145–A1169 | implicit, structure-preserving low-rank, advection–diffusion | 10.1137/23M1622921 |
| Koellermeier, Krah & Kusch (2024), *Macro-micro decomposition for consistent and conservative model order reduction of hyperbolic shallow water moment equations…*, Adv. Comput. Math. 50 | consistency/conservation-preserving MOR, incl. DLRA | 10.1007/s10444-024-10175-y |
| Kusch, Einkemmer & Ceruti (2023), *On the Stability of Robust Dynamical Low-Rank Approximations for Hyperbolic Problems*, SISC 45:A1–A24 | stability theory for robust DLRA | 10.1137/21M1446289 |
| Kusch, Ceruti, Einkemmer & Frank (2022), *Dynamical low-rank approximation for Burgers' equation with uncertainty*, Int. J. Uncertain. Quantif. 12:1–21 | advection-dominated PDE, stochastic | 10.1615/int.j.uncertaintyquantification.2022039345 |
| Kazashi, Nobile & Vidličková (2021), Numer. Math. 149(4):973–1024 | stability of projector splitting (random parabolic) | 10.1007/s00211-021-01241-4 |
| Ceruti & Lubich (2022), BIT 62(1):23–44; Ceruti, Kusch & Lubich (2022), BIT 62(4):1149–1174; Ceruti, Kusch & Lubich (2024), SISC 46(3):B205–B228; Kusch, Schotthöfer & Walter (2026), SIMAX 8(3):820–849 | BUG / projector-splitting / backward-corrected integrators | 10.1007/s10543-021-00873-0 · 10.1007/s10543-021-00907-7 · 10.1137/23M1565103 · 10.1137/25M1730673 |

**(d) Static/hybrid ROM in the stream function–vorticity formulation for NS is
published, twice**, and the second one is not in our survey:

- Girfoglio, Quaini & Rozza (2022), Computers & Fluids 244:105536,
  DOI 10.1016/j.compfluid.2022.105536 (the journal version of arXiv:2201.00756 —
  our designated "closest prior art"; also already exactly divergence-free).
- **Zhang, Xu, Guo & Feng (2024), *A new hybrid reduced order modeling for
  parametrized Navier–Stokes equations in stream-vorticity formulation*,
  Physics of Fluids 36(6), DOI 10.1063/5.0202509** — hybrid projection/data-driven
  (neural-network correction of POD modes, DMD-based sampling), stream–vorticity
  formulation, parametric NS. Static/hybrid, not adaptive-rank, not
  high-Re-validated — but it is a second ψ-formulation NS ROM and must be cited.

---

## 2. The final permitted claim

The claim may be stated **only** in this form (D4, binding):

> Structure-preserving dynamical low-rank approximation is well established for
> Hamiltonian, kinetic, Vlasov–Poisson and wave equations, and robust
> low-rank integrators for conservative PDEs (advection–diffusion, hyperbolic
> moment systems) are established as well. For the incompressible
> Navier–Stokes equations, the existing dynamical low-rank work we are aware of
> is the dynamically orthogonal approximation of Musharbash and Nobile for
> stochastic problems with random boundary conditions, and the existing
> reduced models in the stream function–vorticity formulation are offline and
> hybrid (Girfoglio et al.; Zhang et al.). We are not aware of a
> structure-preserving, exactly divergence-free, factorisation-based low-rank
> integrator for the deterministic incompressible Navier–Stokes equations, or of
> any dynamical low-rank method for that setting validated in a resolved
> high-Reynolds-number forced-turbulent regime. We provide one: we apply the
> established robust basis-update-and-Galerkin machinery to the stream
> function–vorticity formulation, in which divergence-freeness holds exactly by
> representation, and validate it against a full-grid spectral reference at
> Re ∈ {100, 1000, 5000} with adaptive rank.

Barred, explicitly:

- "no dynamical low-rank method has been applied to incompressible NS" — refuted
  by Musharbash & Nobile (2018).
- "first exactly divergence-free incompressible-NS solver" — refuted by our own
  closest prior art (Girfoglio et al. 2022) and by the ψ formulation being
  classical.
- any gap phrased as a failure to preserve divergence-freeness.
- "first structure-preserving low-rank method for conservative PDEs" — refuted
  by RAIL (advection–diffusion) and the hyperbolic moment-equation work.
- "to our knowledge" on arXiv evidence alone; the journal-venue coverage above
  is the minimum required.

The claim is **gated on D10-V6 being implemented** and on D10-V1/V2/V5/V7 being
closed. It describes work to be done.

## 3. Reference list the survey must contain (all verified by the reviewer)

Method family (the machinery we import):
`arXiv:2402.08607` (BIT 64, 2024) · `arXiv:2104.05247` (BIT 62(4):1149–1174,
2022) · `arXiv:2608.27749` (Aug 2026) · DOI 10.1137/23M1565103 (SISC 46(3),
2024) · DOI 10.1007/s10543-021-00873-0 (BIT 62(1), 2022) · DOI 10.1137/25M1730673
(SIMAX 8(3), 2026) · DOI 10.1137/23M1622921 (RAIL, SISC 47, 2025) ·
DOI 10.1137/21M1446289 (stability of robust DLRA, SISC 45, 2023) ·
DOI 10.1007/s00211-021-01241-4 (Kazashi et al.) ·
DOI 10.1007/s10444-024-10175-y (macro-micro, Adv. Comput. Math. 50, 2024).

Prior art on the *problem class*:
DOI 10.1016/j.jcp.2017.09.061 (**Musharbash & Nobile — the one that must be
positioned explicitly**) · DOI 10.1137/140967787 (its error analysis) ·
DOI 10.1016/j.compfluid.2022.105536 (Girfoglio et al.) · DOI 10.1063/5.0202509
(Zhang et al.) · DOI 10.1615/int.j.uncertaintyquantification.2022039345
(Burgers with uncertainty).

Foundational:
DOI 10.1137/050639703 (Koch & Lubich 2007) · DOI 10.1016/j.matcom.2008.03.007
(Nonnenmacher & Lubich 2008) · DOI 10.1007/s10543-013-0454-0 (Lubich & Oseledets
2014) · `arXiv:2412.05912` (kinetic low-rank review).

Reviewer note on process: this took three addenda because I checked arXiv
first, then journals, then the *contents* of the two foundational papers. The
lesson generalises — for a novelty claim, the last mile is reading what the
prior papers actually did, not what their titles suggest. The DO paper was
found only because I chased a citation in an unrelated reference list.
