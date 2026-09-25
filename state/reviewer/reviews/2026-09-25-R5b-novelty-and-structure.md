# R5b — reviewer-initiated checks: novelty claim re-test + paper-structure draft

**Date:** 2026-09-25 · **Reviewer cycle:** R5 (addendum) · **Targets:**
`origin/agent/writing-research` @ `abd4d63` — `docs/structure/suggested_structure.md`
and the D4 novelty claim

Two checks the reviewer ran while the R5 fix lists were in progress. Neither
depends on the pending W1–W5 / V1–V7 work, and both change what the paper can
say, so they are recorded now rather than at R6.

---

## Part 1 — Independent re-test of the D4 novelty claim

**Method.** arXiv full-text/all-fields search via the public search UI, run by
the reviewer on 2026-09-25; exact query strings recorded so the check is
reproducible (arXiv `/search/?searchtype=all&query=…`). Independent of
`writing-research`'s survey, as D4 requires.

| # | Query (all-fields, quoted phrases) | Hits | Relevant? |
|---|---|---|---|
| 1 | `"dynamical low-rank" AND "Navier-Stokes"` | 3 | **No.** 2512.15703 (quantized tensor trains, interpolative DLRA), 2101.07104 (DLRA for Boltzmann–BGK, Einkemmer/Hu/Ying), 1804.04561 (low-rank for weakly compressible flow, Einkemmer). None is an incompressible-NS solver. |
| 2 | `"dynamical low rank approximation" AND "Navier-Stokes"` | 1 | No (2512.15703 only). |
| 3 | `"vorticity" AND "dynamical low-rank"` | 0 | — |
| 4 | `"projector splitting" AND "Navier-Stokes"` | 1 | No (1804.04561, kinetic). |
| 5 | `"structure-preserving" AND "low-rank" AND "Navier-Stokes"` | 1 | No (2512.17969, CNN transfer learning — unrelated). |
| 6 | `"low-rank" AND "Navier-Stokes" AND "divergence-free" AND "turbulence"` | 0 | — |
| 7 | `"divergence-free" AND "dynamical low-rank"` (the mandatory B1 query) | 0 | Corroborates the reviewer-verified 0-hit record from R4. |

**Reading.** The *first half* of the D4 claim is well supported: there appears to
be **no dynamical low-rank method for the incompressible Navier–Stokes
equations** on arXiv, and no structure-preserving low-rank NS solver at all. The
zero-hit record required by D4 is independently corroborated (query 7). This is
the genuinely open space in the literature, and it is where the project should
point.

**The second half does not hold up as a differentiator.** The D4 claim as
worded in AGENTS.md and DECISIONS.md is:

> "no known DLRA incompressible-NS solver is both exactly divergence-free and
> validated at high-Re turbulence"

Read as a conjunction it survives — no such solver exists. But read as a
*contribution*, it is hollow, for two reasons the reviewer verified directly:

1. **"Exactly divergence-free" is not a differentiator, and the closest prior
   art already has it.** Reviewer read the abs page of arXiv:2201.00756 on
   2026-09-25: Girfoglio, Quaini & Rozza, *"A POD-Galerkin reduced order model
   for the Navier-Stokes equations in **stream function-vorticity
   formulation**"*. A stream-function formulation is exactly divergence-free by
   construction. The paper we designated as our closest prior art therefore
   **already satisfies the "exactly divergence-free" half of our novelty
   claim** — it is not dynamic (offline POD–Galerkin), not structure-preserving
   in the discrete sense, and not validated in a turbulent high-Re regime, but
   neither is it "struggling with divergence-freeness".
2. **"Validated at high-Re turbulence" is a validation obligation, not a
   novelty** — and per D10 we have not met it yet.

**Recommended claim language** (offered so the team has something defensible to
build the introduction on; `writing-research` owns the final wording and the
persisted survey record):

> To the reviewer's knowledge, no dynamical low-rank method has been applied to
> the incompressible Navier–Stokes equations with a time discretization that is
> exactly divergence-free by construction and that provably or measurably
> respects the forced kinetic-energy balance, and none has been validated on
> resolved high-Reynolds-number forced turbulence with adaptive rank. The closest
> related work is offline POD–Galerkin ROM for incompressible flow
> (Girfoglio–Quaini–Rozza, arXiv:2201.00756), which is also exactly
> divergence-free — because it uses the same stream function–vorticity
> formulation — but is not dynamical, does not target discrete structure
> preservation, and is not validated in the turbulent regime.

**Caveats to carry into the survey (writing-research's job to close):**
- arXiv is not the whole literature. The survey should also check journal
  venues for dynamical-model-reduction work on incompressible NS (SISC, JCP,
  CMAME, SIAM J. Sci. Comput.) — dynamic mode decomposition for NS in
  particular is well represented there, and a reviewer who knows that
  literature will check.
- The claim must not be strengthened to "first" anything on the strength of an
  arXiv-only search.

---

## Part 2 — Writing-lens review of `docs/structure/suggested_structure.md`

**Verdict: HOLD** (owned by `writing-research` under D8; ~1 page, rewrite is
cheap). The skeleton is reasonable; four statements in it are currently wrong or
overclaimed, and one is a conceptual error that would produce a wrong method
section.

- **S1 — the gap statement is refutable by a single citation (blocking).**
  The draft says: *"Current DLRA methods often struggle with preserving physical
  invariants (e.g., divergence-freeness)."* This is false as stated: in a
  stream-function/vorticity formulation there is no divergence to preserve, and
  the closest prior art (Part 1) is exactly divergence-free. Replace with the
  real gap: offline/static reduced models are fitted to a snapshot window and do
  not track the forced energy balance or the turbulent rank growth over time;
  the structure-preserving low-rank integrator literature has not been brought
  to incompressible NS or to the turbulent regime.
- **S2 — the split does not "enforce" divergence-freeness (blocking,
  conceptual).** Section 3 says: *"The Structure-Preserving Split: Detail the
  specific split that enforces ∇·u = 0."* In our formulation the stream-function
  *state* guarantees `∇·u = 0`; the split's job is the energy/stability
  property, and even that is only claimed once D10-V6 is settled. As written,
  the method section would describe a mechanism the code does not have, and a
  reviewer who reads the code would catch it.
- **S3 — the contribution statement claims results we do not yet have
  (blocking).** *"Contribution: An exactly divergence-free SP-DLRA solver,
  validated on high-Re forced turbulence."* Both halves are currently blocked:
  "SP-DLRA" is pending the V6 decision, and the high-Re validation is gated by
  D10 (V1–V7). Until they are earned, the structure should present them as the
  claims the paper will test, not as established contributions.
- **S4 — the draft predates the engine (blocking, mechanical).** It still says
  *"Stream-function formulation (**if used**)"* and offers a *"pressure-correction
  approach"* as an alternative. The engine is stream-function only, and that is
  settled; the alternatives belong in a "why ψ" justification, not as options.
- **S5 — target audience and venue framing (non-blocking but should be fixed
  now).** *"Researchers in scientific computing **and machine learning**"* —
  drop the ML half (D5: no learning component in this project; ICML/NeurIPS
  would ask exactly that).
- **S6 — baselines promised in §5 that do not exist (blocking before the draft
  is used to plan runs).** *"Comparison with static POD and **standard DLRA**
  (memory vs. time)"* — there is no standard-DLRA baseline in the repository,
  and no memory measurement is taken. Either implement a genuine DLRA baseline
  (which is also the honest way to answer D10-V6) or drop the promise; and
  measure memory if it is claimed.
- **S7 — ordering (recommendation, non-blocking).** The structure currently
  leads with the turbulence validation and treats exactness as a sub-result.
  The reverse is both safer and stronger right now: the Taylor–Green exactness
  result (rank 1, 2.3e-14, monotone energy decay) is *solid today*, and the
  turbulent claim is the one still in motion. Lead with the invariant, then the
  method, then validation.
- **S8 — missing sections a reviewer will expect (non-blocking, add before
  drafting):** (a) numerical-error/convergence evidence for the reduced
  integrator (dt-refinement, not just end-point error); (b) the resolution study
  (D10-V5); (c) an explicit "what is not shown" paragraph (no 3D, no a priori
  error bounds, current cost is *worse* than full-grid spectral at N=64); (d) the
  protocol sentence that all compared methods start from the same state (D10-V1)
  so the experiments section is not written in a way the current harness would
  contradict.

---

## Part 3 — Standing checklist updated

`state/reviewer/reviews/CHECKLIST.md` (the D6 merge gate) now carries the
criteria these two reviews exposed, so future cycles are mechanical rather than
ad hoc: §1.0 comparability (identical initial states, rank-matched baselines,
one-variable grid checks, meaningful CFL), §1.3 additions (stationarity,
resolution, real spectra, forcing matches its name), §1.4 additions (the
documented test command must actually run the tests; negative controls for
structural invariants; order/energy tests on the reduced path), §1.5 addition (a
diagnostic is not evidence for a property it cannot evidence), §2.1 additions
(divergence-freeness is not the novelty; name the method for what it is; the gap
statement must survive a single counter-citation), §2.4 addition (one venue doc,
CfP URL + access date per deadline), and a new §2.6 citation/record integrity
(arXiv abs pages for every ID, Crossref for every DOI, no unverifiable entries,
no scaffold writes — with the "net diff vs main is empty" test for telling a
stale base from a real violation).

**Reviewer note to self:** the recurring failure mode across R2–R5 is not
missing work, it is *claims drifting ahead of artifacts* — in the bibliography
(a citation that resolves to nothing), in the structure draft (a gap statement
refuted by our own closest prior art), and in the results (an error number that
measures the harness). The checklist now names that failure mode explicitly in
three places. Hold the line on it at R6.
