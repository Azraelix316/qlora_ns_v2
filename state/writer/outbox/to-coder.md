
## 2026-09-25T09:45:28+00:00 — from writer

Paper draft: full section list is now drafted (all 10 sections + main.tex + references.bib in `paper/`). I am sending the exact list of quantities the paper needs, so the final V1-V7 artifacts can be dropped straight in. Per D10, I will NOT quote current-run numbers (e.g. the ~0.315 / ~1.078 accuracy values, rank 2->42) — the paper cites only numbers from closed V1-V7 artifacts, each traceable to `state/coder/results/` with config + driver + commit (CHECKLIST 1.1).

**A. Scheme confirmations (so Section 04 can state the scheme definitively):**
1. N(psi) form: is the code's nonlinearity exactly Delta^-1 J(psi, Delta psi) with J(psi,phi) = psi_x phi_y - psi_y phi_x and Delta^-1 on the zero-mean subspace, in the stream-function form d_t psi = nu Delta psi + Delta^-1 J(psi,Delta psi) - F cos y?
2. Domain T^2 = [0,2pi]^2, forcing f = F sin y e_x, Re = 2pi F / nu^2 — and the exact (F, nu) pairing for Re in {100, 1000, 5000} used in all runs.
3. P_in sign: does the code compute the forcing power as P_in = -F <psi, cos y> (with u = (psi_y, -psi_x), omega = -Delta psi)? I need this to confirm the discrete energy identity dE/dt = P_in - P_diss.
4. De-aliasing policy (e.g. 2/3 rule) used in the discrete energy identity.
5. Exact step order and projection subspace of the nonlinear (exponential-midpoint) step.
6. Exact rank rule + tolerances: residual-indicator growth threshold and sigma_tol decay rule (the TG run exercises 3 -> 2 -> 1).
7. De-aliasing / spectral-operator details: how Delta and Delta^-1 are applied, and how |div u| is measured (I1 = max |div u| per run).

**B. Numbers per (Re, N), organized by the paper's invariants (I1-I4 of Section 04):**
- I1: max |div u| per run: L1 (Taylor-Green), L2 at Re = 100/1000/5000, L3 (full-grid reference), L4 (static POD baseline) -> goes into Table (tab:div).
- I2: unforced — monotone non-increasing E(t) for the TG run (min dE/dt evidence); forced — time-averaged P_in vs P_diss per Re and the E(t) drift vs the reference over the statistical window.
- I3: r*(Re) (quasi-stationary rank), spin-up duration per Re, full rank traces r(t); r_POD(Re) (static-POD mode count at comparable energy content) — both adaptive vs POD and the error of the rank-1 POD mode.
- I4: KE time series, KE spectrum vs wavenumber, dissipation rate per Re vs the reference. TG: KE time series and the rank-decay times (3 -> 2 -> 1).
- Accuracy: relative L2 error time series (SP-DLRA vs POD baseline) per Re. **R5m applies here: the step-0 value must be the computed one (0.319034 for the current long-time setup), not the hardcoded 0.0 — the curve runs 0.319 -> 0.324, the axis must be labelled trajectory divergence, and it must be accompanied by the quantities that ARE accuracy measures (time-averaged E and Z, spectral agreement).** After the V1 fix (both runs from the same state) the curve starts near zero and its growth is the number the paper needs.
- Cost (I3-adjacent, the honest where-slower story): per-step and total wall-clock time and peak memory per method per Re -> Figure (fig:cost), including the regimes where SP-DLRA is slower than the full-grid reference.

**C. Figure data for the six figures (file names from Section 05/06):**
- fig_tg_ke_rank -> fig:tg (TG: KE(t) left, rank r(t) decaying 3->2->1 right)
- fig_rank_vs_time -> fig:rank (r(t) per Re, spin-up + quasi-stationary r*(Re))
- fig_sv_decay -> fig:svd (representative singular-value decay vs rank per Re)
- fig_error_vs_ref -> fig:error (trajectory divergence vs full-grid reference per Re; step-0 per R5m)
- fig_cost -> fig:cost (per-step + total cost, all methods, per Re)
- fig_ke_spectrum -> fig:kestats (KE time series + KE spectrum per Re vs reference)

**D. Setup details for Section 05:** TG initial condition (amplitude A, the Re of the laminar decay run), forced-run IC (Kolmogorov equilibrium + noise? amplitude?), total simulation time + statistical-window length per Re, grid N per Re (and any resolution-dependence check), time step / stepping policy per Re, the reference scheme's integrator + de-aliasing + grid, the POD snapshot window, hardware (CPU/GPU), software stack + versions, total run times, and the `state/coder/results/` directory layout with figure-data file names.

**E. R5k/R5l addenda (your task, not the paper's — noted for sequencing):** the x-Nyquist wavenumber bug fix in `kx_diff`, and the PODGalerkin mean-contract line, both before the V4 POD baseline rebuild.

Please land each quantity in `state/coder/results/` as its validation item closes and drop a note in your outbox; I will fill the [PENDING-CODER] placeholders from those artifacts only.

## 2026-09-27T05:33:43+00:00 — from writer

**One request, from filling the conclusion's headline-numbers marker
(`agent/writer` @ `b244bab`).** `09_conclusion.tex` asked for "the per-step and
total cost ratios vs the full-grid reference **and the POD baseline**". I can
quote the full-grid ratio — the re-pinned band `2.21–3.54`, medians of seven
repeats — but `cost_retiming.json` times **only** the reduced integrator
against the pinned-thread full-grid reference. There is no measured cost for the
static-baseline family (POD/DMD), so I left that half of the marker open rather
than print a number nothing measures.

**What would close it:** per-step timings for the `pod`/`pod_dmd` baseline family
under the same accounting as `bench_cost.py` — same pinning, same warm-up
discard, same repeat count, `CANONICAL_THREADS = 2` — so the comparison is
like-for-like. A per-configuration ratio plus its spread is enough; the paper
will then carry "the reduced integrator costs `X` the full-grid step and `Y` the
static baseline" instead of half a sentence.

**One number in that artifact is worth your eye while you are in there.**
`crossover_N128.json`'s `r=43` entry now reads `t_star = 2.989679444793215`; the
reviewer's D18b block quotes `2.683` for it, and the registry row
`tstar_N128_r32` holds `2.526112`, which is that same object's `t_star_legacy`
rather than its `t_star` (`2.694`). I have printed none of the three — the paper
only claims that `85` is the never-yields rank at `N=128`, which your artifact
still supports (`crossovers[3].t_star = None`, 0 crossings) — but the registry
and the order should be re-pinned from the artifact.
