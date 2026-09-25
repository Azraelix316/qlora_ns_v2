
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
