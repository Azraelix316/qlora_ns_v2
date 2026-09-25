# Coder result provenance

Each `kolmogorov_re*_N*.json` file is produced by
`experiments/run_kolmogorov.py` (or the three-case wrapper
`experiments/bench.py`) and contains its full parameter set, git commit,
singular-value samples, energy/enstrophy histories, rank history, relative
errors against the full-grid reference, timings, and invariant diagnostics.
`taylor_green.json` is produced by `experiments/run_taylor_green.py`.

The files are intentionally compact JSON rather than raw field snapshots.
Large trajectories and figures should be regenerated from the recorded
commands; no result is treated as authoritative unless its provenance and
finite-value checks are present.
