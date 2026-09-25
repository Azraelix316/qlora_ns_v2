# R5p — what structure is actually preserved by the established SPDLRA integrators, and what that means for D3

**Date:** 2026-09-25 · **Reviewer cycle:** R5 (addendum 10) · **Purpose:** answer,
from the literature, the question I asked `theoretical-research` in R5c/R5e —
namely how big their job is. All abstracts read directly from arXiv on
2026-09-25.

## The finding

**Every established structure-preserving DLRA result is about *Hamiltonian*,
*non-dissipative* systems, and the preserved structure is *symplecticity*.** The
Hamiltonian SPDLRA line states its scope explicitly and repeatedly:

- Pagliantini, Hesthaven & Ripamonti, *Rank-adaptive structure-preserving model
  order reduction of Hamiltonian systems* (arXiv:2007.13153) — "for
  finite-dimensional parametrized **Hamiltonian** systems modeling
  **non-dissipative** phenomena… the reduced dynamics is prescribed by
  approximating the **symplectic** projection of the Hamiltonian vector field…
  ensures that the **canonical symplectic structure** is preserved".
- Pagliantini, *Dynamical reduced basis methods for Hamiltonian systems*
  (arXiv:2008.07427) — "parameterized **Hamiltonian** systems describing
  **nondissipative** phenomena… **symplectic** projection".
- Pagliantini & Vismara, *Fully adaptive structure-preserving hyper-reduction of
  parametric Hamiltonian systems* (arXiv:2308.16547) — combines "symplectic
  dynamical low-rank" with adaptive rank, for **nonlinear Hamiltonian** systems.

The BUG line is more careful with its claims and, notably, does **not** assert
an energy identity:

- Ceruti, Kusch & Lubich (arXiv:2104.05247) retain "exactness, robustness and
  **symmetry-preserving** properties" — symmetry, not a balance law.
- The BUG midpoint paper (arXiv:2402.08607) says BUG integrators "often have
  favourable **structure-preserving** properties" — deliberately qualitative —
  and its theorem is a **robust error bound**, not a conservation law.

## Why this matters for us: symplecticity is the wrong structure

Our problem is **dissipative and forced**: 2-D viscous NS with a Kolmogorov pump,
where the meaningful structure is the kinetic-energy balance

```
dE/dt + nu*||omega||^2 - <psi,zeta> + <psi,adv> = 0,    E = 1/2*||grad psi||^2
```

Symplecticity cannot be the right target: a contracting, forced flow has no
nontrivial symplectic structure to preserve, and the Hamiltonian line above
*restricts itself to non-dissipative problems for exactly this reason*. So
"SPDLRA is structure-preserving" does **not** transfer to our setting by
citation — anyone reading the BUG and Hamiltonian abstracts carefully will see
that the established results address a different regime.

## The closest prior theorem, and the regime gap that is ours

The nearest result on the **dissipative** side is Kazashi, Nobile & Vidličková,
*Stability properties of a projector-splitting scheme for the dynamical low rank
approximation of random parabolic equations*, Numer. Math. 149(4):973–1024,
2021, DOI 10.1007/s00211-021-01241-4. Their schemes "satisfy a **discrete
variational formulation**", from which they obtain conditional stability under
a **parabolic-type CFL condition** independent of the smallest singular value,
and unconditional stability for the implicit variant.

So the landscape splits cleanly:

| regime | established result | preserved structure |
|---|---|---|
| non-dissipative / Hamiltonian | SPDLRA (2007.13153, 2008.07427, 2308.16547) | symplecticity |
| dissipative, **diffusion-dominated** (parabolic) | Kazashi et al. 2021 | discrete variational formulation + stability |
| **dissipative, advection-dominated, forced** (ours: Re ≤ 5000, ψ-formulation, exact div-free) | **nothing found** | — |

**That third row is the project.** The theory contribution is therefore not
"port an existing energy identity" — none exists to port — but a well-posed
increment on a named predecessor: extend the discrete-variational analysis from
the parabolic regime to the advection-dominated forced regime, in a
representation where the divergence constraint is exact and the rank is
adaptive. That is a contribution a reviewer will recognise as a theorem rather
than an implementation note, and it is sized like a short paper, not a treatise.

## What I am asking `theoretical-research` for, concretely

1. **What does the Galerkin step do to the kinetic-energy balance** in the ψ
   formulation — i.e. derive the projection term rather than measuring it. This
   is the discrete counterpart of the continuous identity already verified, and it
   is the natural statement for a basis-update-and-Galerkin scheme, where the
   coefficient matrix is evolved in the augmented basis.
2. **Is the residual bounded** by that projection work, and under what
   assumptions (this is the analogue of Kazashi et al.'s stability result, and the
   question a reviewer will ask).
3. **Does a defect correction restore a controlled balance?** Kazashi et al.'s
   implicit variant is unconditionally stable where the explicit one is
   conditional; whether an analogous statement holds for an energy balance in the
   forced setting is the natural second result.
4. **D3's invariant should then be stated in discrete form**, with the
   projection term derived rather than measured — which is only possible after
   the BUG port (V6), so the two pieces of work are sequential, not parallel.

A partial answer is genuinely useful: a proposition for the Galerkin step's
energy contribution under a stated assumption, plus a numerical verification of
its residual, is enough for the method section to promise a proposition. If only
a numerical observation is available, the paper says so. I have told the writer
which of the two it may promise, and will keep them informed.

## Reviewer note

This is the same lesson as R5c, applied to the *other* open question: I had
framed the theory task as an undefined "forcing-aware invariant" that was
supposed to be defined from scratch, when the literature already tells us (i)
that the established structure-preserving results are for a different regime and
a different structure, and (ii) exactly which prior theorem to extend. Scoping a
question against the literature before assigning it is worth doing — it is the
difference between "go figure out what the theory slot is" and "here is the
slot, here is its predecessor, here is the gap".
