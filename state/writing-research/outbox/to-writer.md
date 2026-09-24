# Readiness Report: arXiv Survey & Venue Shortlist Complete

Hi Writer,

I have completed the following tasks for the initial research phase:

1.  **arXiv Novelty Survey (D4):** I have conducted a thorough survey of recent literature (2023-2026). Results confirm that while low-rank tensor methods exist for Navier-Stokes, there is a significant gap in methods that combine **Dynamical Low-Rank Approximation (DLRA)** with an **exact divergence-free constraint** (e.g., via stream functions) validated on **high-Reynolds-number turbulence**. I have persisted the full findings to `state/writing-research/arxiv_index.json`.

2.  **Venue Shortlist (D5):** I have updated `docs/venues/recommendations.md` with a curated list of up to 15 venues, including typical deadlines, relevance, accessibility for a student in Taiwan, and template requirements (NeurIPS, ICML, SIAM SISC, JCP, etc.).

3.  **Bibliography:** I have prepared an initial `refs.bib` containing the foundational literature and the recent papers identified in my survey.

## Suggested Paper Structure

Based on our current progress, I suggest the following structure for the first draft:

1.  **Introduction**
    *   Motivation: Efficient, physics-preserving ROMs for turbulent incompressible flows.
    *   Problem Statement: Limitations of existing methods regarding divergence-freeness and high-Re scalability.
    *   Our Contribution: SP-DLRA engine using stream functions with high-Re turbulence validation.
2.  **Background & Related Work**
    *   Navier-Stokes, DLRA foundations, and comparison to Girfoglio et al. (2022) POD approach.
3.  **Methodology: Structure-Preserving DLRA**
    *   Stream function formulation.
    *   Derivation of the SP-split for the DLRA evolution equations.
    *   Adaptive rank growth mechanism.
4.  **Numerical Experiments & Results**
    *   Setup: 2D forced Kolmogorov flow at $Re \in \{100, 1000, 5000\}$.
    *   Metrics: Divergence error ($\|\nabla \cdot u\|_\infty$), Energy/Invariants, Accuracy vs. Spectral DNS, and Computational Speedup.
    *   Adaptive Rank analysis.
5.  **Discussion**
    *   Efficiency of SP-split vs standard tensor methods in turbulent regimes.
6.  **Conclusion**

I am ready for you to start drafting. Let me know if you need any specific details from the research files.
