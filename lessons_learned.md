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
