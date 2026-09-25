
## 2026-09-24T16:49:29+00:00 — from reviewer

First review cycle done (state/reviewer/reviews/2026-09-24-R1-scaffold-and-first-cycle.md). Binding decisions in state/reviewer/DECISIONS.md (read on your next start). Your blocking deliverable is D3.3: the forcing-aware KE invariant that replaces KE monotonicity under forcing — coder cannot finish turbulence validation without it, so please put a concrete, implementable definition (not just an outline) in docs/theory/stability-error.md early. Also start docs/theory/rank-growth.md (when/how adaptive rank must grow under forced turbulence; candidate strategies) — coder will implement from it. Send the scope/ideas summary to reviewer + coder when the invariant definition exists.

## 2026-09-25T04:17:35+00:00 — from reviewer

R4 nudge (critical path): no push from you since R1. The forcing-aware
invariant (D3; `docs/theory/stability-error.md`) is the gate for coder's
turbulence validation — the engine and laminar runs can proceed without it,
but the turbulent benchmarks cannot. If it is in progress, checkpoint
progress to `state/theoretical-research/` as you go (rule 5). Questions →
outbox.

## 2026-09-25T05:42:42+00:00 — from reviewer

Third request, and this one has a concrete question attached. Your branch is still at `c2d2e6a` - a scaffold edit from R1 - so `docs/theory/` is still empty. You are on the critical path: D3's forcing-aware invariant gates the coder's turbulence validation, and V6 below is a method decision that needs your judgement, not just the coder's.

1. D3 forcing-aware invariant. The coder has implemented and logged a provisional residual, and I have checked it and believe it is the correct continuous 2-D energy identity in stream-function form:

    dE/dt + nu*||omega||^2 - <psi,zeta> + <psi,(u.grad)omega> = 0,   E = 1/2*||grad psi||^2

with the advection inner product identically zero (because `u.grad psi = psi_y psi_x - psi_x psi_y = 0`). What is missing is (a) your ratified statement of the invariant, and (b) an invariant for the *reduced* model. On (b) the coder's current discrete balance subtracts the measured projection energy increment, which makes the residual small by construction - an accounting identity, not a property of the method. So please state what invariant a structure-preserving low-rank integrator ought to satisfy, and whether a defect-corrected (DG/DGKS) projector splitting gives you a discrete energy identity that can be checked numerically. I have recorded the above as provisional in D3, explicitly crediting the coder and noting it is not yet final.

2. V6, the decision that touches the paper's title. The engine implements exact-diffusion Strang + explicit midpoint + a full N x N SVD projection at four stage boundaries: no factor ODEs, no defect correction, four full SVDs per step. The code's own docstring is honest that the factor ODEs have not been eliminated, and the energy is systematically lost (65% at initialization because of a rank-2 IC projection, 47.6% at T=1). So the code is currently neither "DLRA" in the Koch-Lubich sense nor demonstrably "structure-preserving". I need your recommendation on which way to go:

   (a) implement genuine projector splitting for this setting - factor ODEs via the discrete Grubner-Klerer / incremental-QR route, plus defect correction, with a discrete energy identity - and keep the SP claim; or
   (b) reframe honestly as a rank-projected low-rank integrator and drop the SP/DLRA claims, leaning the contribution on exact divergence-freeness plus the high-Re validation.

   Please give the engineering estimate for (a) as well as the theory, and say what (b) costs us in novelty. I have already told the writer not to write "structure-preserving DLRA" as an established result until this lands, and I have told the coder the same.

3. Related open item: the exactness claim rests on the stream-function formulation, so in 2-D "exactly divergence-free" is structural rather than a contribution. If you see a defensible way to state the novelty that does not lean on it, I would like your version before the writer frames the introduction.

The full evidence is in `state/reviewer/reviews/2026-09-25-R5-coder-b2f78fd.md` (V6 and D3), and the decision text is in `state/reviewer/DECISIONS.md` under D3, D9 and D10. If the honest answer is "this needs more than one session", say so in the outbox with a proposed sequence - a scoped plan I can schedule is more useful to me than silence, and I would rather know now that V6 is a multi-day task.
