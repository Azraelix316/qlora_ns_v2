# Coder result provenance

Each `kolmogorov_re*_N*.json` file is produced by
`experiments/run_kolmogorov.py` (or the three-case wrapper
`experiments/bench.py`) and contains its full parameter set, git commit,
singular-value samples, energy/enstrophy histories, rank history, relative
errors against the full-grid reference, timings, and invariant diagnostics.
For reduced runs, `max_scaled_full_pde_energy_residual` is the unmodified
continuous-PDE diagnostic, while `max_scaled_energy_balance_residual` is the
discrete diagnostic with the measured projection energy work removed.
`taylor_green.json` is produced by `experiments/run_taylor_green.py`;
`kolmogorov_re5000_N64_long.json` is the sustained full/DLRA check.

The files are intentionally compact JSON rather than raw field snapshots.
Large trajectories and figures should be regenerated from the recorded
commands; no result is treated as authoritative unless its provenance,
finite-value checks, and scale-aware stability flags are present.
