# READ THIS FIRST — reviewer, updated R28

**BLOCKING (2 items, both small):**
1. **Delete this line from your board's First TODOs:** "Read `summary_of_v2.md` ... and the
   v1 handoff (`/home/jaredc/HANDOFF_qlora_ns.md`, v1 repo `/home/jaredc/qlora_ns`)".
   `AGENTS.md` forbids prior-run artifacts. It may not exist on your node. One-line commit.
2. **Write the continuous forcing-aware invariant** in `docs/theory/stability-error.md`:
   `dE/dt + nu*||omega||^2 - <psi,zeta> = 0`, plus what a run measures, at what tolerance,
   and what it rules out. **Not blocked.** I have already verified this identity, so you
   ratify rather than re-derive. Owed since R1; it is a paper blocker (D3).

**DO NOT START:** the reduced-model discrete invariant. It needs the V6 BUG port. Record
it as blocked; do not approximate it.

**NEW DATA FOR rank-growth.md (I said wait; the premise survived, so start now):**
`r99` over nested windows, Re=5000, N=64: 1, 2, 4, 6, 11, **16**, 14, 11, 9, 6 for
W = 0.1...40. Re=1000 agrees. At N=128, r99 at W<=8 matches N=64 to within one mode, so
the 1->16 growth is grid-independent; beyond t~8 it is not (14 at N=64 vs 24 at N=128 at
W=16). Three testable questions: does saturation time scale as 1/lambda (R13 measured
lambda ~ 0.69/time-unit)? Why does rank keep growing with resolution? Why is the
implemented amplitude rule blind to all of this? Full report:
`state/reviewer/reviews/2026-09-25-R26-rank-versus-horizon.md`.

---
