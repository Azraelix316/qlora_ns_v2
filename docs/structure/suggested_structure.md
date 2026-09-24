# Suggested Paper Structure

**Target Audience:** Researchers in scientific computing and machine learning interested in low-rank methods for PDEs.

## 1. Introduction
- **Motivation:** The cost of high-fidelity simulations (DNS) for turbulence.
- **Problem Statement:** Incompressible Navier-Stokes equations and the need for reduced-order models.
- **The Gap:** Current DLRA methods often struggle with preserving physical invariants (e.g., divergence-freeness) or handling turbulent regimes where rank growth is significant.
- **Contribution:** An exactly divergence-free SP-DLRA solver, validated on high-Re forced turbulence.

## 2. Mathematical Background & Preliminaries
- **Incompressible Navier-Stokes Equations:** Stream-function formulation (to ensure divergence-freeness naturally) or pressure-correction approach.
- **Dynamical Low-Rank Approximation (DLRA):** Matrix/Tensor decomposition and the projector-splitting integrator.
- **Structure Preservation:** Discussion of how existing DLRA can fail to preserve physical constraints.

## 3. Proposed Method: SP-DLRA
- **The Structure-Preserving Split:** Detail the specific split that enforces $\nabla \cdot \mathbf{u} = 0$.
- **Stream-Function Formulation (if used):** How it integrates with DLRA.
- **Adaptive Rank Mechanism:** Algorithm for monitoring singular values and updating rank to capture turbulent dynamics.

## 4. Numerical Experiments: Forced Turbulence
- **Test Problem:** 2D Kolmogorov flow or similar forced Navier-Stokes setup.
- **Parameters:** Reynolds numbers $Re \in \{100, 1000, 5000\}$.
- **Reference Data:** Comparison against full-grid spectral methods (DNS).

## 5. Results & Discussion
- **Accuracy and Invariants:** Plotting $\max |\nabla \cdot \mathbf{u}|$ to demonstrate divergence-freeness ($< 10^{-14}$).
- **Rank Dynamics:** Evolution of the singular values/rank as turbulence develops.
- **Computational Efficiency:** Comparison with static POD and standard DLRA (memory vs. time).
- **Turbulence Capture:** Energy spectrum comparison or kinetic energy evolution under forcing.

## 6. Conclusion
- Summary of findings.
- Implications for large-scale turbulent simulations.
- Future work (e.g., 3D extension).

## References
(To be populated from `refs.bib`)
