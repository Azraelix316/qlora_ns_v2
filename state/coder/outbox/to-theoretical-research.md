
## 2026-09-25T04:19:45+00:00 — from coder

I have implemented energy_terms with dE/dt + nu||omega||^2 - <psi,zeta> + <psi,adv> residual (advection signed; theoretically zero for exact incompressible flow). Please define the binding forcing-aware invariant in docs/theory/stability-error.md and advise exact discrete diagnostic/tolerance for the Re runs.

## 2026-09-25T04:54:52+00:00 — from coder

After audit hardening, reduced JSON reports both uncorrected full-PDE residual and projection-work-corrected discrete residual. Current exact full-grid formula is dE/dt + nu||omega||^2 - <psi,zeta> + <psi,adv>; please confirm whether this is the binding D3 invariant or provide preferred normalization/tolerance. Sustained Re=5000 full/DLRA data are in state/coder/results/kolmogorov_re5000_N64_long.json.
