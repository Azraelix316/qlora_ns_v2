# Suggested Paper Structure (Revised per R5d)

**Target Audience:** Researchers in scientific computing interested in low-rank methods for PDEs, specifically incompressible fluid dynamics.

## 1. Introduction
- **Motivation:** The high computational cost of Direct Numerical Simulation (DNS) for turbulent flows.
- **Problem Statement:** Incompressible Navier–Stokes equations and the necessity of reduced-order models (ROMs) for large-scale applications.
- **Literature Survey & Gap Analysis:**
    - Acknowledge that dynamical low-rank methods have been applied to incompressible NS, specifically the dynamically orthogonal (DO) approximation for stochastic problems with random boundary conditions (Musharbash & Nobile 2018).
    - Note existing reduced models in the stream function–vorticity ($\psi$-$\omega$) formulation, which are currently offline or hybrid approaches (Girfoglio et al. 2022; Zhang et al. 2024).
    - **The Gap:** Absence of a structure-preserving, exactly divergence-free, factorisation-based low-rank integrator for deterministic incompressible NS that is validated in high-Reynolds-number forced-turbulent regimes.
- **Contribution:** We propose and validate an adaptive-rank, structure-preserving DLRA solver using the robust basis-update-and-Galerkin (BUG) machinery applied to the $\psi$-$\omega$ formulation.

## 2. Mathematical Background & Preliminaries
- **Incompressible Navier–Stokes Equations:** Discussion of the stream function–vorticity ($\psi$-$\omega$) formulation as the primary choice for this work, chosen specifically because it satisfies the divergence-free constraint $\nabla \cdot \mathbf{u} = 0$ by construction, avoiding the need for pressure-correction or projection steps.
- **Robust Low-Rank Integrators (BUG):** Overview of the robust basis-update-and-Galerkin (BUG) class of integrators (Ceruti & Lubich 2022, etc.) and their ability to handle small singular values.
- **Dynamical Low-Rank Approximation (DLRA):** The projector-splitting framework and its extension to structure-preserving settings.

## 3. Proposed Method: Structure-Preserving DLRA
- **$\psi$-$\omega$ Formulation for DLRA:** How the low-rank approximation is applied directly to the stream function and vorticity fields to ensure exact divergence-freeness by construction.
- **Integrating BUG with $\psi$-$\omega$:** Detailed description of the structure-preserving split that incorporates the robust basis-update machinery.
- **Adaptive Rank Mechanism:** An algorithm for monitoring singular value decay and adjusting the rank to capture the multi-scale nature of turbulence.

## 4. Numerical Experiments: Forced Turbulence
- **Problem Setup:** 2D Kolmogorov flow or forced Navier–Stokes equations in a periodic domain.
- **Turbulence Regime:** High Reynolds numbers $Re \in \{100, 1000, 5000\}$ to ensure interesting dynamical behavior and rank growth.
- **Reference Comparison:** Validation against high-fidelity, full-grid spectral DNS data.

## 5. Results & Discussion
- **Divergence-Freeness:** Verification of the invariant $\max |\nabla \cdot \mathbf{u}| \approx 10^{-14}$ throughout the simulation.
- **Rank Dynamics and Energy Capture:** Evolution of singular values and rank as turbulence develops; comparison of kinetic energy evolution and energy spectra against DNS.
- **Accuracy vs. Efficiency:** Performance benchmarks (computational cost, memory usage) compared to full-grid DNS and static POD.

## 6. Conclusion
- Summary of the successful implementation of an exactly divergence-free, robust DLRA solver for turbulent NS.
- Implications for future work in 3D simulations and more complex geometries.

## References
(To be populated from `refs.bib`, ensuring all R5d-mandated citations are included)
