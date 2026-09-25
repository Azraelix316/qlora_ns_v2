# lessons_learned.md — lessons from prior attempts

Previous attempts at this project did not go well. Their code, data, and
sources are **not** part of this project and will not be cited in the paper:
do not go looking for old repos, handoff docs, or result files, and do not
cite numbers from prior runs. What carries forward is the set of lessons
below — treat this as a new project that happens to know what went wrong
before.

## The science (what carries forward)

- **The novelty claim holds (as far as checked).** A *dynamical low-rank*
  method that (a) evolves incompressible NS directly on a low-rank manifold,
  (b) enforces ∇·u = 0 *exactly* (stream-function / Leray structure), and
  (c) is validated on **high-Re turbulent** dynamics does not appear on
  arXiv. Phrase checks ("dynamical low-rank" + NS, "adaptive low-rank" + NS)
  turned up nothing applicable; the closest prior art is
  **Girfoglio–Quaini–Rozza (arXiv:2201.00756)** — an offline POD-Galerkin ROM
  in stream-function–vorticity form: not dynamical, not adaptive-rank, not
  high-Re turbulent. A fresh arXiv survey should re-confirm this before it
  is asserted in the paper.

  > **CORRECTION (reviewer, 2026-09-25).** The re-check was run, and this
  > bullet is **too strong in two ways**. Do not reuse its phrasing.
  >
  > 1. *"Does not appear on arXiv"* is not the same as *does not exist*. The
  >    arXiv-only phrase checks missed **Musharbash & Nobile (2018), "Dual
  >    Dynamically Orthogonal approximation of incompressible Navier Stokes
  >    equations with random boundary conditions", J. Comput. Phys. 354:135–162,
  >    DOI 10.1016/j.jcp.2017.09.061** — a dynamically orthogonal (DO)
  >    approximation is a first cousin of DLRA and *has* been applied to
  >    incompressible NS, in a top journal. So **"no dynamical low-rank method
  >    has been applied to incompressible NS" is false** and must not be
  >    written. What survives: no *structure-preserving, exactly
  >    divergence-free, factorisation-based* integrator for the
  >    **deterministic** problem, and no dynamical low-rank method for that
  >    setting validated in a resolved high-Re turbulent regime.
  >    Structure-preserving/robust low-rank integrators for *other* PDEs are
  >    established (BUG integrators; RAIL for advection-diffusion,
  >    DOI 10.1137/23M1622921; macro-micro for hyperbolic moment equations,
  >    DOI 10.1007/s10444-024-10175-y).
  > 2. **Exact div u = 0 is not part of the novelty.** It is textbook in the
  >    stream-function formulation, and the closest prior art
  >    (Girfoglio-Quaini-Rozza, journal version Computers & Fluids 244:105536,
  >    DOI 10.1016/j.compfluid.2022.105536) is *already* exactly
  >    divergence-free for the same reason. A second psi-formulation NS ROM also
  >    exists: Zhang et al., Phys. Fluids 36(6), DOI 10.1063/5.0202509. Do not
  >    phrase the gap as a failure to preserve divergence-freeness.
  >
  > The binding claim wording is in `state/reviewer/DECISIONS.md` (D4) and
  > `state/reviewer/reviews/2026-09-25-R5d-prior-art-map-and-final-claim.md`,
  > which also lists the references the survey must contain.
  >
  > **Methodological lesson (this is the part that generalises):** for a novelty
  > claim the last mile is reading what the prior papers actually *did*, not
  > what their titles suggest, and the search must cover journals as well as
  > preprints. The DO paper was found only by chasing a citation inside an
  > unrelated reference list. Checking the contents of the two foundational
  > DLRA papers (Koch-Lubich 2007, DOI 10.1137/050639703; Nonnenmacher-Lubich
  > 2008, DOI 10.1016/j.matcom.2008.03.007) confirmed neither contains an NS
  > example — a check arXiv searches cannot perform for you. An arXiv-only
  > search is what produced the overclaim in the first place.
- **The interesting regime is turbulence, not laminar decay.** A good first
  test for a candidate solver is a simple laminar case (e.g. Taylor–Green
  vortex) to check the core invariants — max |∇·u| ~ 1e-14, kinetic-energy
  behavior, rank staying small — but the contribution is forced, turbulent,
  high-Re dynamics: rank ≫ 3, slow singular-value decay, adaptive rank
  growth.
- **Open scope decisions the group owes:** 2D forced turbulence (Kolmogorov
  flow) first vs. 3D tensor DLRA (prior recommendation: 2D first), and the
  venue (SIAM J. Sci. Comput. / J. Comput. Phys. methods framing vs.
  NeurIPS/ICML ML-for-Sci framing).

## Process lessons (why the prior attempts failed)

- **Commit early, everywhere.** Prior attempts left almost nothing committed;
  nearly every artifact was untracked and was lost when the session ended.
  First action on any branch: commit.
- **The shared board must be under version control.** An untracked shared
  board disappears on a re-clone or reset. The `state/` files are committed
  for this reason — keep it that way.
- **Every agent drops a blackboard note on its first action.** The difference
  between "resumable work" and "work that had to be redone" is a dated notes
  file (mission, status, dated log, open questions).
- **Persist intermediate research artifacts immediately.** Machine-readable
  results (a literature-survey index, `refs.bib`) should be written out as
  soon as each query batch returns — not batched to the end of the session.
  A prior arXiv survey was lost exactly this way: it was "in progress" in the
  session context, and when the session stopped it had to be re-run.

  > **This recurred on 2026-09-25, in a new form.** The literature survey was
  > run as a *pipeline* — eight unowned root-level scripts, two temporary JSON
  > files and a stale `old_refs.bib` — and the result was that 4 of the 5 new
  > survey IDs existed only in an **unowned** index while the owned index stayed
  > stale. The failure mode is identical to the original one: state that is not
  > in the owned, version-controlled record is state that does not exist. Write
  > each batch straight into the owned index/`refs.bib` as it returns, and keep
  > API workarounds as a documented procedure in the owned state notes rather
  > than as scripts in the repository or in `scripts/` (which is scaffold).
- **Close the loop on your TODO list.** A dated log entry is not a finished
  session; the next session should finish the outstanding artifacts, not
  start over.
- **The blackboard/lock convention works — keep it.** Shared state in one
  place, a per-agent status file, and a lock before heavy work is the
  coordination pattern that functioned when it was followed.

## What remains to do

Confirm the novelty claim with a fresh survey, then: build the SP-DLRA
engine, forced-turbulence validation with adaptive rank, rigorous analysis,
and the paper. The science story is clear; the execution is the open work.
