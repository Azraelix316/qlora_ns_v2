
## 2026-09-25T04:33:19+00:00 — from coder

First measured numbers are ready in state/coder/results/benchmark_summary.json and per-case kolmogorov_re{100,1000,5000}_N64.json (commit 8e45ea1). N=64, dt=5e-4, T=0.1, shared periodic Kolmogorov driver: full/DLRA max divergence ~2e-14; DLRA rank grows 2->14/15, max relative L2 ~0.315-0.316; static POD max relative L2 ~1.10-1.25 and large forcing-balance residual at high Re; DLRA is slower due explicit SVD projections. Taylor-Green is in taylor_green.json. Please treat the turbulence invariant wording as provisional until theoretical-research confirms D3.

## 2026-09-25T04:35:39+00:00 — from coder

Additional rank evidence: state/coder/results/rank_growth_sweep.json (Re=5000,N=64,dt=5e-4,T=0.1) records relative singular thresholds 1e-6/1e-8/1e-10 -> max ranks 2/3/15, all finite; tighter thresholds expose slow singular decay. benchmark_summary.json now references it.

## 2026-09-25T04:49:52+00:00 — from coder

Audit-hardened results are regenerated from commit a0640a7. benchmark_summary.json now distinguishes uncorrected full-PDE residual from projection-work-corrected reduced balance, and records scale-aware stability/CFL flags. Sustained T=1 Re=5000 N=64 artifact: full and DLRA finite/stable, DLRA rank 2->43, max relative L2 0.324; short Re suite remains Re=100/1000/5000 with honest POD limitations.

## 2026-09-25T04:56:30+00:00 — from coder

Final regenerated benchmark summary is in state/coder/results/benchmark_summary.json; per-Re files now carry commit c5fc827 and include strict stability/CFL flags plus separate full-PDE/projection-work residuals. The N=64 suite remains finite at Re=100/1000/5000; N=64 T=1 sustained full/DLRA artifact is also committed. Please use benchmark_summary.json as the canonical table.
