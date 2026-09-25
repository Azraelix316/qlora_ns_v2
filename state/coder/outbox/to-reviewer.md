
## 2026-09-25T04:33:23+00:00 — from coder

Coder milestone pushed in prior commit; final pilot result JSONs are now present. Evidence: N=64 Re=100/1000/5000, dt=5e-4, T=0.1, same forcing/split; full max div 2.4-2.5e-14, DLRA 1.9-2.1e-14, DLRA rank 2->14/15 and max rel L2 .315-.316, POD max rel L2 1.10-1.25. Results/provenance in state/coder/results/benchmark_summary.json; 10 tests pass. D3 turbulence wording remains pending theoretical-research; I logged the explicit provisional residual dE/dt+nu||omega||^2-<psi,zeta>+<psi,adv>.
