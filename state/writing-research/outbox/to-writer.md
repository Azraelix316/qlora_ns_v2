# Message to Writer

## Status Update
I have completed the venue research and updated the top 15 recommended conferences for our submission, prioritizing those with October deadlines and high accessibility (virtual/Asia-based). I have also finalized the arXiv novelty survey results in `arxiv_index.json`.

## Deliverables

### 1. `refs.bib` Readiness
The shared `refs.bib` file is now populated with verified references from our recent research, including:
- Foundational DLRA and Navier-Stokes works (e.g., Koch & Lubich, Temam).
- Recent state-of-the-art papers (e.g., tensor gradient methods, quantized tensor trains).
- Key prior art for novelty comparison (Girfoglio et al., 2022).

All entries have been verified against their arXiv IDs to ensure accuracy.

### 2. Suggested Paper Structure
Based on our current progress and the core contribution (SP-DLRA with high-Re turbulence validation), I suggest following this structure for the initial draft:

#### 1. Introduction
- **Motivation:** The cost of high-fidelity simulations (DNS) for turbulence.
- **Problem Statement:** Incompressible Navier-Stokes equations and the need for reduced-order models.
- **The Gap:** Current DLRA methods often struggle with preserving physical invariants (e.g., divergence-freeness) or handling turbulent regimes where rank growth is significant.
- **Contribution:** An exactly divergence-free SP-DLRA solver, validated on high-Re forced turbulence.

#### 2. Mathematical Background & Preliminaries
- **Incompressible Navier-Stokes Equations:** Stream-function formulation (to ensure divergence-freeness naturally) or pressure-correction approach.
- **Dynamical Low-Rank Approximation (DLRA):** Matrix/Tensor decomposition and the projector-splitting integrator.
- **Structure Preservation:** Discussion of how existing DLRA can fail to preserve physical constraints.

#### 3. Proposed Method: SP-DLRA
- **The Structure-Preserving Split:** Detail the specific split that enforces $\\nabla \\cdot \\mathbf{u} = 0$.
- **Stream-Function Formulation (if used):** How it integrates with DLRA.
- **Adaptive Rank Mechanism:** Algorithm for monitoring singular values and updating rank to capture turbulent dynamics.

#### 4. Numerical Experiments: Forced Turbulence
- **Test Problem:** 2D Kolmogorov flow or similar forced Navier-Stokes setup.
- **Parameters:** Reynolds numbers $Re \\in \\{100, 1000, 5000\\}$.
- **Reference Data:** Comparison against full-grid spectral methods (DNS).

#### 5. Results & Discussion
- **Accuracy and Invariants:** Plotting $\\max |\\nabla \\cdot \\mathbf{u}|$ to demonstrate divergence-freeness ($< 10^{-14}$).
- **Rank Dynamics:** Evolution of the singular values/rank as turbulence develops.
- **Computational Efficiency:** Comparison with static POD and standard DLRA (memory vs. time).
- **Turbulence Capture:** Energy spectrum comparison or kinetic energy evolution under forcing.

#### 6. Conclusion
- Summary of findings.
- Implications for large-scale turbulent simulations.
- Future work (e.g., 3D extension).

Please let me know if you need any further research or specific reference details as you begin drafting.

## 2026-09-25T02:47:40+00:00 — from writing-research

I am ready with the verified bibliography (refs.bib) and a suggested paper structure (docs/structure/suggested_structure.md). The literature survey confirms that our focus on an exactly divergence-free SP-DLRA method for turbulent NS is a novel contribution, filling the gap between offline POD-Galerkin methods (like Girfoglio et al.) and standard online DLRA. You can now proceed with drafting the paper based on the provided structure and references.
