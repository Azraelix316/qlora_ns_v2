# Coder result provenance

Each `kolmogorov_re*_N*.json` file is produced by
`experiments/run_kolmogorov.py` and contains its full parameter set, git
commit, the P0 initial-state fingerprint, singular-value spectra, energy and
enstrophy histories, rank history, trajectory divergence against the
full-grid reference, both cost accountings, and invariant diagnostics.
For reduced runs, `max_scaled_full_pde_energy_residual` is the unmodified
continuous-PDE diagnostic, while `max_scaled_energy_balance_residual` is the
discrete diagnostic with the measured projection energy work removed.
`benchmark_summary.json` is **generated** by `experiments/make_summary.py`
from the files below -- it introduces no measurement of its own, and it
refuses to emit a summary whose members disagree about the initial state.

| file | driver | what it is |
|---|---|---|
| `kolmogorov_re{100,1000,5000}_N64.json` | `run_kolmogorov.py` | canonical suite, N=64, T=0.1 |
| `kolmogorov_re5000_N128.json` | `run_kolmogorov.py` | two-grid check under P0 item 3 (dt scaled with dx, IC held fixed via `ic_reference_N`) |
| `kolmogorov_re5000_N64_long.json` | `run_long_time.py` | sustained full/DLRA check, T=1 (not a statistical window) |
| `rank_growth_sweep.json` | `run_rank_growth_sweep.py` | relative-amplitude-cutoff sweep (rank/error/cost) |
| `cost_retiming.json` | `bench_cost.py` | R5q re-timing: pinned threads, warm-up discarded, median of repeats with spread, two accountings, rank-independence |
| `regime_pilot.json` | `run_regime_pilot.py` | S1-S3 pilot: S2 fluctuation drift as a function of T |
| `taylor_green.json` | `run_taylor_green.py` | F1 laminar exactness and monotone decay |

## What a result is not allowed to mean

- **`max_trajectory_divergence`** (relative L2 against the reference) is
  *trajectory divergence*, not accuracy: once two solutions decorrelate it
  measures phase. The accuracy metrics are time-averaged KE/enstrophy and
  spectral agreement over a stationary window, and the regime pilot has to
  establish that window first.
- **No per-step speedup.** The reduced method pays the same full-grid
  nonlinear evaluation as the reference *plus* a whole-field SVD that is
  Theta(N^3) and rank-independent. `cost_retiming.json` reports both
  accountings; a linear-algebra win is not a per-step win.
- **No turbulence statistic from `t <= 0.1`** (S5/D11.2). At that horizon the
  regime is not turbulence, and the corrected static-POD baseline is *more*
  accurate than adaptive DLRA because its offline window is a prefix of the
  evaluated trajectory.
- **`relative_amplitude_cutoff`** is a test on singular *values*, so a cutoff
  of 1e-6 is an energy ratio of 1e-12. It is not an accuracy tolerance and
  must not be described as one.

The files are intentionally compact JSON rather than raw field snapshots.
Large trajectories and figures should be regenerated from the recorded
parameters; no result is treated as authoritative unless its provenance,
finite-value checks, and scale-aware stability flags are present.
