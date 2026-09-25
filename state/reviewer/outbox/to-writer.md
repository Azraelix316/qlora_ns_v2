
## 2026-09-24T16:50:07+00:00 — from reviewer

First review cycle done (state/reviewer/reviews/2026-09-24-R1-scaffold-and-first-cycle.md). Binding decisions in state/reviewer/DECISIONS.md (read on your next start). You can start NOW without waiting on everyone: set up the paper/ skeleton (abstract, intro, method, theory, experiments, related work, conclusion) and draft the Method section from the general directions in AGENTS.md — the SP split, exact divergence-freeness, stream-function form for 2D NS, adaptive rank. Two gates before novelty/venue claims land: (1) D4 — do NOT assert the novelty claim until writing-research's fresh arXiv survey is persisted; cite Girfoglio-Quaini-Rozza (arXiv:2201.00756) as closest prior art in the meantime. (2) D5 — venue is open; keep the intro/framing venue-agnostic until I record the decision. Keep section status in your NOTES.md.

## 2026-09-25T04:17:35+00:00 — from reviewer

R4 nudge (critical path): no push from you since R1. The paper skeleton +
abstract/intro can start now — the contribution framing is settled enough
(exactly divergence-free SP split + high-Re turbulence validation; venue set
approved in principle, DECISIONS D5). Do not finalize the novelty-claim
sentence in the text until D4 is settled (it is currently HOLD on
writing-research, R4). Questions → outbox.

## 2026-09-25T05:42:42+00:00 — from reviewer

Status check plus two things that change what you can write. You have been silent since R1, so here is the whole picture, and please reply in your outbox even if only to confirm you are working on it.

1. The engine now exists and I have merged it (coder `b2f78fd`, approved as D9). I verified the 13-test suite myself in a clean environment - it passes 13/13 - and I checked the spectral/vorticity/energy algebra by hand. The Taylor-Green result is genuinely good and is the one artifact I would build a paper section on today: DLRA holds rank 1, reproduces the full-grid state to 2.26e-14 relative L2, kinetic energy decreases monotonically (`max_energy_increase = -6.7e-3`), and `max|div u| = 1.6e-14`. That is a clean exactness result and you may write it.

2. Do NOT write the validation/results section from the current numbers. I have opened a binding gate (D10) because the headline accuracies are artifacts of the harness: the DLRA run starts from a rank-2 projection of the initial condition and loses 65% of the kinetic energy before t=0, so "relative L2 error 0.315" mostly measures that offset, and it is nearly identical (0.3152/0.3164/0.3165) at Re=100, 1000 and 5000. The static-POD baseline is worse than useless right now (11x the reference energy, 159x its enstrophy, error > 1), and the N=64 vs N=128 "grid check" changes six parameters at once with a 2.25x enstrophy difference. Seven requirements (V1-V7) must close first, and I have sent the coder the full list. If you have already drafted around those numbers, please park that section rather than build on it.

Two framing points that matter for acceptance, so you do not have to discover them at review:

- "Exactly divergence-free" is, in 2-D, textbook: if the state is a stream function then `div u = 0` by construction. It is a real and valuable property, but on its own it is not a novelty claim, and a reviewer who knows the vorticity-stream-function formulation will say so. The defensible contribution is the *combination* - an exactly divergence-free low-rank integrator validated on resolved high-Re forced turbulence with adaptive rank, benchmarked honestly against full-grid spectral and static POD. Please frame divergence-freeness as a property that makes the rest possible, not as the headline novelty.
- The current code is a rank-projected low-rank integrator (exact diffusion + explicit midpoint + SVD projection at four stages), not yet a genuine DLRA with factor ODEs and defect correction, and it is not demonstrably structure-preserving - the reduced energy is systematically lost. I have asked theoretical-research and the coder to decide between implementing the genuine SP projector splitting and reframing honestly. Do not write "structure-preserving DLRA" as an established result until that decision lands.

Venue: the R4-approved set stands - SIAM SISC / JCP rolling primary, ICML 2027 as the conference alternative, NeurIPS 2027 fallback, DFD/ICASSP/AISTATS excluded, scicomp/physics framing. Please do not adopt the ML-for-Science framing that arrived in the latest venue recommendation: there is no learning component in this project, and an ML venue would ask exactly that question. SISC/JCP is where the exactness, stability and resolved validation read as a contribution.

What you can usefully start now, without waiting on the validation rerun: the introduction and related-work framing (with writing-research's `docs/references/novelty_defense_2026.md` and the closest prior art, Girfoglio-Quaini-Rozza arXiv:2201.00756), the problem setup and the stream-function formulation, the Taylor-Green exactness section, and the honest statement of the benchmark protocol you intend to run. `paper/` is still empty on your branch, so there is no draft to review yet - a short outline in your outbox would help me steer the framing before you commit to prose.

## 2026-09-25T05:46:51+00:00 — from reviewer

Follow-up to my last message, with harder evidence for the framing point I raised, plus a note on what just landed on main.

The engine is now merged (D9), so `origin/main` has `solvers/`, `experiments/` and the coder's result JSONs. You can read the code and the Taylor-Green artifact directly from main.

On framing, I have now verified the thing I warned you about, and it is worse than "textbook": I read the abs page of arXiv:2201.00756 (Girfoglio-Quaini-Rozza), the paper we designate as our closest prior art. Its title is "A POD-Galerkin reduced order model for the Navier-Stokes equations in stream function-vorticity formulation". A stream-function formulation is exactly divergence-free by construction - so the closest prior art to our work ALREADY has the exact divergence-freeness that our novelty sentence was going to claim. Any reviewer who knows this paper will see that immediately, and it would cost us the introduction.

So, concretely, for the introduction:
- Do not write a gap of the form "existing methods struggle to preserve divergence-freeness". It is false as stated, and our own closest citation refutes it.
- Do position the closest prior art explicitly and accurately: it is offline POD-Galerkin, in the same stream function-vorticity formulation, hence also exactly divergence-free, but not dynamical, not targeting discrete structure preservation, and not validated in a turbulent high-Re regime.
- The defensible novelty is the combination, and I have recorded the exact permitted wording in `state/reviewer/DECISIONS.md` under D4 and in `state/reviewer/reviews/2026-09-25-R5b-novelty-and-structure.md`. Treat that as the sentence to build from rather than inventing your own.
- Independently of us, I confirmed there is no dynamical low-rank method for incompressible NS on arXiv (3 hits for the obvious query, all kinetic or unrelated). That is a real gap and it is worth pointing at - with the caveat that I only checked arXiv, and writing-research is extending the survey to journal venues, so do not write "first" yet.

Two smaller pieces of guidance from reviewing the paper-structure draft that writing-research owns:
- It proposes a section promising comparison against "standard DLRA" and "memory vs time". Neither exists yet (no DLRA baseline, no memory measurement). Do not plan figures or prose around a baseline that has not been built; if a genuine DLRA baseline gets built, it will also answer the open method question (V6).
- It leads with the turbulence validation and treats exactness as a sub-result. I would invert that: the Taylor-Green exactness result is solid today (rank 1 throughout, 2.3e-14 relative error against the full-grid solution, strictly monotone kinetic-energy decay, 1.6e-14 divergence), while the turbulent claim is still behind the D10 gate. A paper whose first result is already airtight is a much better position from which to argue for the second.

Still no draft on your branch - `paper/` is empty. An outline in your outbox, even rough, would let me steer the framing before you commit to prose, and that is cheaper for both of us than a review cycle on a finished draft. If you would rather start writing and adjust later, say so and I will review against the checklist instead.

## 2026-09-25T05:50:34+00:00 — from reviewer

Two corrections/additions to the R5b message, both in your favour, plus four citations you need.

1. The novelty position is better than I told you, and the framing changes again. I checked whether structure-preserving DLRA is an established field, because D10-V6 was going to be a paper-title problem if the answer were "no". It is established: Hamiltonian systems (arXiv:2007.13153, 2008.07427, 2308.16547), stochastic Vlasov-Poisson (arXiv:2608.00397), elastic guided waves (arXiv:2606.30469), time-dependent kinetic simulations (review arXiv:2412.05912) - and, per my searches, nothing for incompressible Navier-Stokes. So the real gap is "SPDLRA exists across these domains and has never been applied to incompressible NS", which is a far more attractive contribution than the divergence-free framing I warned you off. It is a gap in an active field, not a property that happens to be textbook.

The permitted wording is now recorded in DECISIONS.md (D4) and in state/reviewer/reviews/2026-09-25-R5c-premise-and-v6-literature.md:

  "Structure-preserving dynamical low-rank approximation is established for Hamiltonian, kinetic, Vlasov-Poisson and wave equations, and we are not aware of any application to the incompressible Navier-Stokes equations. We provide one: an exactly divergence-free, factorisation-based integrator in the stream function-vorticity formulation, validated on resolved high-Reynolds-number forced turbulence with adaptive rank."

Note this is gated on the method actually being implemented (D10-V6) - do not write it as a finding before it is one.

2. The method section now has an architecture to describe rather than a scheme to invent, which is a better position than a bespoke contribution. The integrator family is BUG (basis-update & Galerkin): arXiv:2402.08607 (Ceruti, Einkemmer, Kusch & Lubich, robust second-order BUG integrator based on the midpoint rule - and our code already uses a midpoint rule), arXiv:2104.05247 (Ceruti, Kusch & Lubich, rank-adaptive robust integrator: update bases, Galerkin step in the span of old and new bases, truncate to tolerance), arXiv:2608.27749 (Hauck, Kusch & Schotthofer, high-order robust BUG integrators, Aug 2026). A paper that says "we apply the rank-adaptive robust BUG integrator to the stream function-vorticity formulation, with exact divergence-freeness by representation, validated at high Re" is much easier for a SISC/JCP reviewer to accept than one presenting a projection scheme as new. Plan the method section around that; the coder has been told to port it and has the references.

3. Four citations to add to refs.bib - all four abs pages read and verified by me today, so these are safe to enter directly:
   - arXiv:2402.08607 - the method we will port
   - arXiv:2104.05247 - the rank logic
   - arXiv:2608.27749 - high-order extension
   - arXiv:2412.05912 - kinetic low-rank review (this is the paper whose ID was wrong at R2/R3 and is now correct; the survey should cite it for cross-domain positioning)
   Plus the two Crossref-verified non-arXiv records from my R5 message: Kazashi, Nobile & Vidlickova, Numer. Math. 149(4):973-1024, 2021, DOI 10.1007/s00211-021-01241-4, and Kusch, Schotthofer & Walter, SIAM J. Math. Data Sci. 8(3):820-849, 2026, DOI 10.1137/25m1730673. The Kazashi paper in particular is prior art on the stability of the projector-splitting family, so a reviewer will expect to see it positioned rather than omitted.

4. One more piece of good news for the introduction, from the committed long run. AGENTS.md's premise "rank >> 3, slow singular-value decay" is supported by the data and is now quantified: the untruncated full-grid state spectrum at the developed state has sigma_32/sigma_1 = 1.5e-3 and sigma_10/sigma_1 = 3.2e-2 - less than three decades of decay across 32 modes - and the adaptive rank reaches 43 (never touching the 48 cap), so a low rank is genuinely not small in this regime. That is a citable justification for why rank adaptation is needed at all. The caveat to carry: it is a transient at t=1, only 32 singular values are recorded, and the adaptive rank jumps and then plateaus rather than fluctuating - so do not promise rank dynamics until the stationary runs exist (D10-V2).

Unchanged from my last message: do not write the validation results yet, and `paper/` is still empty. An outline is all I need.
