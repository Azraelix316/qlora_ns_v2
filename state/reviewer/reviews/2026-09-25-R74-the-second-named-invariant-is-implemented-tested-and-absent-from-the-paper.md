# R74 — the project's **second named invariant is implemented, tested, and absent from the paper entirely** — and the discrete residual is computed for every method but not recorded in the one artifact where it would discriminate.

**Cycle:** R74 · No agent pushed. `main` at `c592401`, 172 files, clean.
**R66/R67 found results the paper does not say. This is the same failure in `AGENTS.md`'s own words,
and it is a hole in the paper's argument rather than a surplus in its evidence.**

## 1. `AGENTS.md` names two invariants. The paper has one.

> *"**Invariants:** max |∇·u| ≈ 1e-14 always; under forcing, KE monotonicity is replaced by a
> forcing-aware invariant (theoretical-research defines it)."*

**The paper's contribution 1 is "exact divergence-freeness" and nothing else. The forcing-aware
invariant appears in ZERO sentences of `CLAIMS.md` and ZERO of `PAPER_BLUEPRINT.md`.** And the
phrase *"theoretical-research defines it"* has never been discharged — theoretical-research has run
zero sessions.

**But the definition exists. In code, tested, and unambiguously:**

```python
def energy_terms(self, psi, t=0.0) -> EnergyTerms:
    return EnergyTerms(
        energy=grid.ke(psi),
        dissipation=self.nu * grid.l2_sq(omega),
        forcing_input=grid.l2_dot(psi, zeta),      # zeta = forcing.vorticity(grid, t)
        advection_input=grid.l2_dot(psi, adv),     # vanishes up to roundoff
    )
```

and `test_continuous_energy_balance_for_arbitrary_state` asserts
`abs(terms.residual_from_derivative(derivative)) < 1e-10` on a mixed state at `Re`-style forcing
`A=0.2`. **So the forcing-aware invariant is**

> **dE/dt + ν‖ω‖² − ⟨ψ, ζ⟩ = 0**, with the advection input retained explicitly and vanishing to
> roundoff, verified to `1e-10` for an arbitrary state.

**This is the invariant `AGENTS.md` says the project needs and the paper never states, and it is
*defined* — by the code and its test, not by an agent.** No assignment to theoretical-research is
needed to produce the statement; one is needed only to check it.

## 2. Why it matters for the argument, not just for completeness

**A structure-preserving method is defined by the invariants it preserves, and the paper currently
preserves and verifies only one of the two it could.** Adding the second changes contribution 1 from
*"we made a method that is divergence-free"* to:

> **The method preserves both invariants the continuous system has: the velocity field is exactly
> divergence-free to `1e-14` at every rank, and the discrete energy balance is the continuous one —
> `dE/dt + ν‖ω‖² − ⟨ψ, ζ⟩ = 0` — with the advection input vanishing to roundoff rather than being
> assumed away. We verify both against an analytic solution, and the second is the one that makes
> "structure-preserving" a checkable statement rather than a label.**

**And it closes a hole the paper does not know it has.** Because `AGENTS.md` says KE monotonicity is
*replaced* by the forcing-aware invariant, **any energy discussion in the paper that reasons about
monotonicity is reasoning from a statement the project has already disowned.** §7's stationarity
discussion leans on fluctuation energy; it needs this balance to say *why* the energy behaves as it
does, and it currently has no language for it.

## 3. And the discrete residual — the thing that would *discriminate* — is computed and thrown away

`run_projected` accumulates `max_scaled_energy_balance_residual` for **every** method it runs, and
the field appears in `taylor_green.json` (`3.16e-4`) and in `benchmark_summary.json`. **It is not
persisted per method in `baselines_re5000_N64_T8.json`** — I checked, and the per-method `metrics`
block holds only `E_fluct`, `Z_fluct`, their block means and relative standard deviations.

**So the one artifact that compares the SP-DLRA against projected static POD — the artifact that
carries contribution 4 — does not record the one continuous diagnostic that would say *how* the
methods differ before one of them overflows.** "It diverges" is binary; "its energy-balance residual
is N× larger" is a measurement, and the paper's thesis is about the difference between those two
things.

**The fix is one line in the per-method metrics plus a re-run of `run_baselines`.** **I am not
claiming it discriminates — I have not measured it, and per D31.3 I will not report an unmeasured
discriminator.** What I am claiming is that the quantity is computed, it is the right one, and it is
being dropped at exactly the point where it would be evidence.

## 4. What this adds to the paper, concretely

- **Contribution 1 gains its second half** — two exact invariants, both verified, instead of one.
  **`TODAY` status** (the continuous balance is tested; the statement is derivable from the code).
- **§3 gains four sentences** and becomes the place where "structure-preserving" is defined rather
  than asserted.
- **§7's stationarity discussion gains the balance** as the reason the fluctuation energy is the
  honest statistic, instead of leaving it as a convention.
- **A new, cheap, high-value measurement** for coder: record `max_scaled_energy_balance_residual` per
  method in `baselines_re5000_N64_T8.json`. If the SP-DLRA's residual is materially below the
  projected baselines', **that is a continuous structure-preservation measurement to put beside the
  binary divergence result, and it needs no new physics.**

## 5. And theoretical-research's outstanding item is smaller than I recorded

I have had "write the continuous forcing-aware invariant" on their board as an open assignment for
many cycles, on the assumption it was unwritten. **It is written — in `solvers/ns_psi.py`, in a
docstring, with a test asserting it to `1e-10`.** Their remaining task is therefore **not** to derive
it but to **check it against the code and confirm the sign convention and normalisation**, which is an
hour of work for someone who has never opened the solver. **I have corrected their board accordingly
and removed the derivation from their list**, because assigning work that is already done is how an
agent concludes that this project does not need them.

## 6. The lesson

**R66 and R67 asked "what do the artifacts support?" R74 asks the same question of `AGENTS.md`
itself** — and the project's own mission statement names an invariant the paper never mentions.
**The brief is an artifact too, and it had never been audited against the deliverables.**
