
## 2026-09-25T04:33:19+00:00 — from coder

First measured numbers are ready in state/coder/results/benchmark_summary.json and per-case kolmogorov_re{100,1000,5000}_N64.json (commit 8e45ea1). N=64, dt=5e-4, T=0.1, shared periodic Kolmogorov driver: full/DLRA max divergence ~2e-14; DLRA rank grows 2->14/15, max relative L2 ~0.315-0.316; static POD max relative L2 ~1.10-1.25 and large forcing-balance residual at high Re; DLRA is slower due explicit SVD projections. Taylor-Green is in taylor_green.json. Please treat the turbulence invariant wording as provisional until theoretical-research confirms D3.

## 2026-09-25T04:35:39+00:00 — from coder

Additional rank evidence: state/coder/results/rank_growth_sweep.json (Re=5000,N=64,dt=5e-4,T=0.1) records relative singular thresholds 1e-6/1e-8/1e-10 -> max ranks 2/3/15, all finite; tighter thresholds expose slow singular decay. benchmark_summary.json now references it.

## 2026-09-25T04:49:52+00:00 — from coder

Audit-hardened results are regenerated from commit a0640a7. benchmark_summary.json now distinguishes uncorrected full-PDE residual from projection-work-corrected reduced balance, and records scale-aware stability/CFL flags. Sustained T=1 Re=5000 N=64 artifact: full and DLRA finite/stable, DLRA rank 2->43, max relative L2 0.324; short Re suite remains Re=100/1000/5000 with honest POD limitations.

## 2026-09-25T04:56:30+00:00 — from coder

Final regenerated benchmark summary is in state/coder/results/benchmark_summary.json; per-Re files now carry commit c5fc827 and include strict stability/CFL flags plus separate full-PDE/projection-work residuals. The N=64 suite remains finite at Re=100/1000/5000; N=64 T=1 sustained full/DLRA artifact is also committed. Please use benchmark_summary.json as the canonical table.

## 2026-09-25T04:59:56+00:00 — from coder

Generated reproducible paper figures under experiments/figures/ (fig_rank_error, fig_singular_values, fig_cost; PDF+PNG) via experiments/make_figures.py. They read the committed JSON and highlight rank growth, slow singular decay, error, and honest SVD cost.

## 2026-09-25T13:13:06+00:00 — from coder

**Two pieces of news, one of which voids numbers you may have drafted around. Plus direct answers to your Section 04 scheme questions (A1-A7), all read off the code, not memory.**

## Read this first: the static-POD baseline was broken, and every POD number was void

`PODGalerkin.fit` reshaped the snapshot stack `(n,N,N)` to `(N*N,n)` in C order, which **interleaves** snapshots instead of stacking them. The SVD was fitted to scrambled data, so the "POD basis" was meaningless. That is the source of the ~1.08 rel L2 and the 11x energy figures — not a property of POD. The old unit test passed *because* it asserted the buggy behaviour.

Fixed, plus one protocol change: the offline fit now includes `t=0` so the static baseline starts from the same bit-identical IC (P0). Corrected, N=64/Re=5000/200 steps/rank 16:

| | buggy | corrected |
|---|---|---|
| step-0 rel L2 | 1.0802 | **1.8e-17** |
| step-0 KE | 11.25x full | **1.0000x** (bit-identical) |
| max rel L2 vs full | ~1.08 | **1.0e-8** |

**Consequence for the draft: the corrected static-POD baseline is *more* accurate than adaptive DLRA at T=0.1 (1.0e-8 vs 1.0e-4), and a rank-1 POD already reaches 1.3e-2.** So do not write that DLRA beats static POD on accuracy at this horizon. The reviewer has ruled (D11.2) that no statistic may come from a `t<=0.1` run, and F5 is blocked behind the regime decision. I will not produce a matched-rank comparison until there is a horizon where the flow is genuinely multi-dimensional. I am also not claiming any per-step speedup (D11.1): per-step cost is Theta(N^3) and rank-independent, measured 2.9-3.6x *slower* than the full grid.

## Your A1-A7, verified against `solvers/`

1. **Nonlinearity.** Yes, stream-function form: `d_t psi = nu Lap psi + Lap^{-1} J(psi, omega) + zeta_forcing` with `omega = -Lap psi`, `J(a,b) = a_x b_y - a_y b_x`, and `Lap^{-1}` applied on the zero-mean subspace only (`inv_lap` sets the `k=0` coefficient to zero). Base shear stream function is `-U cos y`, so the Kolmogorov forcing is `f = F sin(k y) e_x`; at the committed amplitude `A=0.5` with `k=1`. The exact (F, nu) pairing is **not** the textbook `Re = 2*pi*F/nu^2`: each Re is set independently by `nu = 1/Re` with `A` held at 0.5, so the three cases are *not* on a constant-Reynolds forcing curve. Worth stating explicitly in Section 05 — do not write the textbook relation for these runs.
2. **Domain/forcing/Re.** `T^2 = [0,2*pi)^2`, periodic, `N x N` uniform, `dx = L/N`. Committed: `A=0.5`, `k=1`, `nu = 1/Re` for Re in {100,1000,5000} (so `nu = 1e-2, 1e-3, 2e-4`).
3. **Forcing power sign.** The code's energy identity is `dE/dt = P_in - P_diss` with `E = 0.5*||grad psi||^2` and `P_diss = nu*enstrophy_dissipation_integrand`. For the power term, the vorticity convention is `omega = -Lap psi` with `u = (psi_y, -psi_x)`, so for a forcing stream function `chi` with `(chi_y, -chi_x) = f` the input power is `P_in = -F * <psi, cos(k y)>`-equivalent, i.e. the code pairs the sign consistently with `dE/dt = P_in - P_diss`; the existing `test_energy_balance_for_self_consistent_state` and `test_continuous_energy_balance_for_arbitrary_state` pin it to roundoff. If you need the exact expression as written in `forcing.py` I will send the line rather than have you paraphrase it.
4. **De-aliasing.** Rectangular 2/3 rule: `cutoff = (2/3)*(N//2)`, mask `|k_x| <= cutoff and |k_y| <= cutoff`, applied to the nonlinear product before projection. Note this is a **box** half-width, so the highest radial wavenumber retained is `floor(cutoff*sqrt(2))`. The numerical rank of any state is therefore exactly the dealias ceiling `2*floor(N/3)+1` (43 at N=64) with a nine-order cliff at the boundary — there is **no spectral gap and no adaptive rank growth** (reviewer D11.3 retires that claim; the committed "rank 2->43" is the rank-2 init meeting a fixed ceiling).
5. **Step order.** Exact-diffusion Strang split with a dealiased midpoint treatment of the nonlinearity: the nonlinear residual is evaluated by the full spectral operator at the midpoint and then projected. Four stage projections per step (five on adaptation steps). Per D11.6 the methods section must describe *this* scheme, not the canonical published one; the difference belongs in limitations as the planned V6 port.
6. **Rank rule and "tolerances".** There is no residual-based error indicator and no incremental-SVD growth in what is implemented. The rule is: SVD the **whole N x N field** (rank-independent, Theta(N^3) per stage), then retain `count(s > cutoff * s[0])` modes, clamped to `[min_rank, max_rank]`. The parameter is now named **`relative_amplitude_cutoff`** (renamed per D11.5) because it is a test on singular *values*: `1e-6` is an **energy** ratio of `1e-12`. Do not describe it as an accuracy criterion or as a tolerance. The Taylor-Green run exercises 3 -> 2 -> 1.
7. **Operators and divergence.** `lap`/`inv_lap`/`vorticity` apply the true `k^2`; first derivatives multiply by the true `kx`/`ky` (see below). `max_div_velocity` builds `u,v` from `psi`, round-trips them through real space, and re-differentiates spectrally, so it measures floating-point roundoff only: measured **2.5e-14 to 2.7e-14** for full grid, DLRA and POD at N=64. Exact divergence-freeness is by representation (`u = grad_perp psi`), not by projection.

**One correction to your framing of E (R5k/R5l addenda).** I implemented R5k's Nyquist fix and it is **wrong for this engine** — zeroing the Nyquist multiplier deletes `v`'s Nyquist row while keeping `u`'s, making the real velocity field non-divergence-free (spectral div u = 8.0 at N=16 vs 5.5e-15 with the true wavenumbers). SVD projections populate that row, so it would have broken I1 everywhere. R5l's mean-contract item I did fix, and the rank cap (R20) and `DLRA` reset (R25) are done. Full detail and measurements are in my message to the reviewer.

**What is not ready for you yet:** every committed result JSON still carries the void POD column and is being regenerated from the new commit, so no artifact should be cited until that lands. Per D11.2 no turbulence statistic may be drawn from a `t<=0.1` run, so the KE/enstrophy/spectral-agreement panels and the stationarity window are waiting on the regime decision.
