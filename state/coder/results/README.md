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
| `regime_pilot_re5000_A0p2.json` | `run_regime_pilot.py` | S1-S3 pilot at A=0.2: the grid-independent `r99` growth R26 measured, reproduced independently |
| `regime_pilot_re5000_A0p5.json` | `run_regime_pilot.py` | the same at the canonical A=0.5, plus the S2 ladder to T=20 |
| `baselines_re5000_N64_T8.json` | `run_baselines.py` | F5: full grid, static POD on early/late/moving windows, POD-DMD and fixed-rank DLRA at matched ranks, T=8 |
| `crossover_surface.json` | `run_crossover.py` | the advantage horizon `t*` as a function of rank, 6 ranks × 9 horizons, with the error split into mean and fluctuation parts |
| `cost_bug_port.json` | `bench_cost.py` | the BUG port's cost on the same protocol as `cost_retiming.json`, against the projected integrator |
| `cost_retiming.json` | `bench_cost.py` | R5q re-timing: pinned threads, warm-up discarded, median of repeats with spread, two accountings, rank-independence |
| `taylor_green.json` | `run_taylor_green.py` | F1 laminar exactness and monotone decay |

## Rank: two different quantities, both recorded

`r99` in `window_rank_table` is the number of modes needed to represent a
**window** of the trajectory (nested windows from t=0, on
`psi' = psi - x-avg(psi)`). It grows 1 -> 16 over the first eight time units
and is grid-independent there. The rank a **per-step** rule selects is a
different quantity -- the rank of one state at one instant, which is ~2 at
t=8 -- because a rule that reads one snapshot at a time cannot see the subspace
a trajectory accumulates. Both are in the artifacts
(`window_rank_table` and `instantaneous_rank_series`, plus each run's
`rank_history`), and the two must not be conflated in the paper.

## A rank without its quantity is ambiguous

Three different quantities are called "rank" in this project's artifacts, and
conflating them is how the dealiasing ceiling came to be read as adaptivity:

| quantity | where | what it is |
|---|---|---|
| per-step spatial rank | `dlra`'s `rank_history`, `baselines_*.json`'s `adaptive_rank` | the dimension one candidate field needs at one stage; what an adaptive rule can return |
| windowed rank | `regime_pilot_*.json` → `window_rank_table` | the modes needed to represent a whole window of the trajectory; grows 1 → 16 over [0, 8] and is grid-independent |
| dealiasing ceiling | `2·floor(N/3)+1` | 43 at N=64, 85 at N=128; what the amplitude rule returns, because its request tracks the grid |

Only the middle one is a property of the dynamics. The `rank_quantities` block
in each artifact states which one its own numbers are.

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
- **No stationary window exists at these settings.** The S2 statistic (block
  means of >= 2 time units over the final third, drift between the last two
  thirds, bar 10% on both E_fluct and Z_fluct) passes at **no** affordable
  horizon up to T=20, and cannot even be evaluated below T ~ 12 because the
  final third is then shorter than two blocks. The flow is mean-dominated: the
  zonal mean holds 94% of the total energy at T=20. Statistics are therefore
  time-dependent and reported with the zonal mean's trajectory alongside.
- **A baseline that diverges is reported as diverging.** Methods carry
  `diverged`, `diverged_at_time`, `final_time_reached` and
  `accuracy_metrics_valid`; a truncated run's statistics cover only the window
  it reached. "POD is worse" is not a citable claim unless the divergence is
  itself reported.
- **No turbulence statistic from `t <= 0.1`** (S5/D11.2). At that horizon the
  regime is not turbulence, and the corrected static-POD baseline is *more*
  accurate than adaptive DLRA because its offline window is a prefix of the
  evaluated trajectory.
- **`relative_amplitude_cutoff`** is a test on singular *values*, so a cutoff
  of 1e-6 is an energy ratio of 1e-12. It is not an accuracy tolerance and
  must not be described as one.

## The rank rule: an order finding, not a change (D12)

**Recorded here rather than implemented, per D12.** The question was whether the
rank rule should be re-engineered to *accumulate a visited subspace* — to
retain modes the trajectory has passed through — instead of reporting the rank
the current window needs. The answer from measurement is that accumulating makes
it **worse**, and the reason is specific:

- The instantaneous rule at cutoff `1e-10` keeps **1.5%** of the fluctuation
  energy outside the retained subspace. A windowed criterion (Gram-based stacked
  spectrum over the same snapshots) keeps **27.5%** — nearly twenty times worse —
  at the same cutoff.
- The obvious explanation, that a bad window *placement* is responsible, is
  **refuted by an oracle-window control**: giving the windowed criterion the
  best window available, chosen with hindsight, still leaves **1.3%** outside.
  So the loss is not the window's fault; it is the criterion.

The mechanism is that this problem's spectrum decays slowly and the energy sits
in *low* modes, so a stacked window spectrum is dominated by the modes the
trajectory already occupies and under-weights the tail that the instantaneous
criterion resolves. The windowed rule would also have been self-reinforcing —
a wider window raises the computed rank, which keeps more modes, which widens
the apparent window — and the oracle control is what rules that out as the
explanation rather than merely being consistent with it.

**What is reported instead is the distinction**, which is a finding: the
instantaneous per-step rank and the window rank are different quantities, they
answer different questions, and conflating them is what made "adaptive rank"
look like a grid artifact. The window rank grows `1 -> 16` over `[0, 8]` and is
grid-independent; the per-step amplitude rule's request tracks the grid and
returns the dealiasing ceiling at tight cutoffs. Both are recorded, and the
`rank_quantities` block says which is which.

## What separates a propagating static basis from the DLRA is construction, not refresh (C6-1)

Measured at `N=32`, rank 16, `dt=0.002`, `T=6.0`, three arms on the same runner
and the same rank:

| arm | outcome | max \|∇·u\| |
|---|---|---|
| raw-snapshot static basis, propagated | **overflows** at `t = 5.388` | 2.14e+191 |
| DLRA, `check_every=5` (subspace refreshes) | reaches `T` | 2.287e-14 |
| DLRA, `check_every=1e9` (subspace frozen) — control | reaches `T` | 2.287e-14 |

**The frozen control survives, identically.** So at this configuration the
difference from a raw-snapshot static basis is in how the subspace is
*constructed* — fluctuation basis, energy criterion, proper initialisation — and
not in whether it is refreshed. `check_every` gates the basis refresh, not only
the rank, so a test that sets it to "never" and calls the result "adaptive" is
measuring construction while reporting evolution.

This is consistent with the configuration rather than surprising: rank 16 on an
N=32 grid is 16 of the 21 alias-free modes, so there is little room for a
refresh to matter. **The open question is whether the refresh matters at higher
rank**, where the T=8 artifact shows the static basis overflowing at `r ≥ 32`;
that is where construction and evolution could come apart.

Two claims, pinned in two different places, and neither asked to do the other's
job:

- **construction** — `test_a_propagated_fixed_basis_overflows_and_the_evolving_one_does_not`
  (live, ~27 s), whose assertions record which way the control fell so the test
  fails if the two arms ever become distinguishable;
- **evolution** — `test_the_subspace_must_evolve_contrast_is_present_in_the_artifact`,
  from the shipped T=8 artifact, where fixed-basis POD overflows at `r ≥ 32` and
  the DLRA at the same rank does not.

The files are intentionally compact JSON rather than raw field snapshots.
Large trajectories and figures should be regenerated from the recorded
parameters; no result is treated as authoritative unless its provenance,
finite-value checks, and scale-aware stability flags are present.
