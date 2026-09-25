# Novelty Defense (Update 2026-09-25)

This document summarizes the research performed to defend the novelty claim of the proposed **Structure-Preserving DLRA for Incompressible Navier–Stokes equations**.

## The Core Claim
No known online/dynamical low-rank approximation (DLRA) method for incompressible Navier-Stokes equations is both:
1.  **Exactly divergence-free** ($\nabla \cdot \mathbf{u} = 0$ enforced by the solver structure), AND
2.  **Validated on high-Reynolds-number, forced, turbulent dynamics** ($Re \in \{100, 1000, 5000\}$).

## Analysis of Closest Prior Art (2025–2026)

The following recent works intersect with our research but fail to satisfy both criteria simultaneously:

| Reference | Topic | Why it is NOT a direct competitor |
| :--- | :--- | :--- |
| **Ye & Yang (2025)** [arXiv:2512.15703] | Interpolative DLRA for QTTs in NS | Focuses on the efficiency of interpolative schemes; does not incorporate an exact divergence-free constraint. |
| **Loeschcke et al. (2025)** [arXiv:2501.02379] | TensorGRaD for Neural Operators | Validates high-$Re$ turbulence, but uses a neural operator framework rather than a pure SP-DLRA engine; divergence-freeness is not explicitly enforced. |
| **Aydin & Sousedík (2026)** [arXiv:2608.07526] | Stochastic Galerkin with TT/CP for NS | Addresses unsteady/stochastic aspects using tensor formats, but lacks focus on enforcing the physical divergence-free invariant. |
| **Olshanskii & Rebholz (2024)** [arXiv:2405.03796] | LRTD for incompressible flows | While addressing incompressibility via reduced-order modeling, it is only validated at relatively low Reynolds numbers ($Re \leq 400$). |

## Conclusion for Paper Writing
When drafting the **Introduction** and **Related Work**, we should explicitly distinguish our method from these directions by emphasizing that we bridge the gap between (a) the high efficiency of online DLRA, (b) the mathematical rigor of structure-preserving constraints ($\nabla \cdot \mathbf{u} = 0$), and (c) the physical reality of turbulent flows.
