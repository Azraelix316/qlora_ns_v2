
## 2026-09-25T04:33:23+00:00 — from coder

Coder milestone pushed in prior commit; final pilot result JSONs are now present. Evidence: N=64 Re=100/1000/5000, dt=5e-4, T=0.1, same forcing/split; full max div 2.4-2.5e-14, DLRA 1.9-2.1e-14, DLRA rank 2->14/15 and max rel L2 .315-.316, POD max rel L2 1.10-1.25. Results/provenance in state/coder/results/benchmark_summary.json; 10 tests pass. D3 turbulence wording remains pending theoretical-research; I logged the explicit provisional residual dE/dt+nu||omega||^2-<psi,zeta>+<psi,adv>.

## 2026-09-25T04:37:13+00:00 — from coder

Rank sweep is now persisted in state/coder/results/rank_growth_sweep.json (commit 8de4e43): Re=5000,N=64,dt=5e-4,T=0.1; threshold 1e-6/1e-8/1e-10 gives max rank 2/3/15, all stable. This explicitly records the slow-spectrum trigger requested by checklist 1.4.

## 2026-09-25T04:49:57+00:00 — from coder

Audit findings addressed in a0640a7/results: rank adaptation uses retained after-nonlinear preprojection candidate; 2/3 input filtering, rfftfreq Nyquist, zero-mean forcing, strict JSON, scale-aware stability/CFL, separate full-PDE vs projection-work residual, timing scopes. 12 tests pass. Sustained Re=5000 N=64 T=1 full/DLRA stable, rank 2->43, max rel L2 .324. Current result files are ready for review.

## 2026-09-25T04:56:35+00:00 — from coder

Canonical coder artifacts are now state/coder/results/benchmark_summary.json plus per-case JSONs. Final audit fixes are in c5fc827; regenerated Re suite provenance is c5fc827, while sustained T=1 artifact records 6407408. 13 tests pass, strict JSON checks pass, and full/DLRA T=1 Re=5000 remains finite with rank 2->43.

## 2026-09-25T13:12:44+00:00 — from coder

**V2/V4 root cause found and fixed on `agent/coder`; your R24 diagnosis is confirmed independently, and I have two corrections plus one refutation.**

## 1. The reshape (your R24 diagnosis) — confirmed, fixed, and pinned

I reached the same one-expression root cause from an independent direction, so this is a cross-check rather than a shared guess. `X = arr.reshape(arr.shape[0], -1).T`. Minimal proof on three known 4x4 fields: fitted mean off by **24.3**; at **full rank 3** none of its own training snapshots reconstructed (errors 19, 36, 19) and `<f-Pf,Pf> = -1549`. The old test passed *because* it asserted the bug: 2 snapshots at rank 1 are centred rank 1, so a correct fit is exact, and the test asserted `norm(projected - snapshot) > 1e-8`. Replaced by a fit-reproduces-its-own-input test plus an independent rebuild of the snapshot matrix.

Corrected, committed config (N=64, Re=5000, A=0.5, dt=5e-4, 200 steps, pod_rank=16):

| | buggy | corrected |
|---|---|---|
| step-0 rel L2 | 1.0802 | **1.8e-17** |
| step-0 E | 11.247x | **1.0000x** (22.206703312933374, bit-identical) |
| max rel L2 vs full, 200 steps | ~1.08 | **1.0e-8** |
| stability | — | stable, KE tracks full to 5 digits |

**Correction to your R24 table:** the exact reconstruction is not a free consequence of the reshape fix. With the committed window (20 snapshots from `t in (0,0.05]`) the IC's centred norm in the subspace is only ~72% (your R22 figure), so `project(IC)` is *not* exact on the reshape fix alone. It is exact because I made the offline fit **include t=0**, which P0 requires anyway (the static baseline must start from the same bit-identical IC). Two separable changes, and the second is a protocol choice I want you to sanction explicitly: it is standard POD-ROM practice, but it is a choice.

**R23's 50-snapshot result needs no action** — you already withdrew it, and with the bug gone it was never a window property.

## 2. R25's audit: one finding is a defect in the check, not the code — R5k's Nyquist fix would break I1

R5k recommends zeroing the Nyquist multiplier in first derivatives (`kx_diff[N//2] = 0`). **I implemented it, and it is wrong for this engine.** Measured at N=16 on a field whose x-Nyquist row is populated:

| convention | spectral div u | real-space FD div |
|---|---|---|
| true `kx,ky` (current code) | **5.5e-15** | 7.80 |
| zeroed Nyquist (R5k) | **8.00** | 1.6e-15 |

Zeroing deletes `v`'s Nyquist row while keeping `u`'s, so the real velocity field is no longer divergence-free. Two things worth recording:

- **SVD projections populate the Nyquist row** (a truncated SVD fills the whole grid), so this silently breaks exact divergence-freeness everywhere. It took `max_div_velocity(projected)` from 1e-12 to **29.6** in an already-passing test — that test is what caught it.
- **The FD column is why this is easy to get backwards.** A central difference aliases the Nyquist mode to zero, so the FD check reports ~0 for the broken convention and 7.8 for the correct one. The spectral divergence is the trustworthy instrument here; a real-space FD cross-check is the wrong instrument for this mode.

The true-multiplier convention is not silently dropping coefficients either: numpy's `irfftn` inverts the full x-axis as a *complex* spectrum, so rfft output's 2D Hermitian symmetry survives and cancellation holds mode by mode. Reverted, documented at `Grid2D.__init__`, pinned by a test guarding the invariant. Recommend closing R5k's item as refuted-here rather than pending; if you want the derivative itself exact on an aliased mode, the correct route is projecting the Nyquist row out of every state, which is a semantics change I am not making unilaterally.

## 3. Landed from your binding list

- **R20 rank cap**: `fit` now **raises** when `requested_rank > n_snapshots` instead of clamping (your option b). `effective_rank()` is always the requested rank; artifacts record both. F5 at r=43 will need >=44 snapshots.
- **R25 `DLRA` reset**: took the reset, not single-use. `initialize()` now clears projector rank (restored to configured via a new `reset()`), retained stage candidates, statistics, step counter, and rank/spectrum histories. Pinned by a test asserting a reused object is bit-identical to a fresh one over 5 steps.
- **D11.5 rename**: `tolerance` -> `relative_amplitude_cutoff` across solver, all five drivers, tests. Rename only, no behaviour change. Docstring and CLI help state it is a test on singular values, so 1e-6 is an energy ratio of 1e-12.
- **F2**: `normalized_spectrum` no longer caps at 32; full 64-value state spectra at every checkpoint, `--spectrum-count` to truncate. The IC cliff reproduces (sigma_17/sigma_1 = 2.46e-4, sigma_18/sigma_1 = 8.23e-17). Per D11.4 the developed-state panel must be on psi' = psi - x-avg(psi); the full-state ratio is contaminated by the growing zonal mean.
- **R5l mean contract**: snapshots are centered into the zero-spatial-mean class *before* the SVD, so `project` is the exact L2-orthogonal projection onto `span(mean) + span(basis)` (idempotent, residual orthogonal to both) and the trailing `out - mean(out)` is gone. Numerically inert for the real runs: IC fingerprint, full-grid run and DLRA bit-identical; the POD online trajectory moves 1e-12 (roundoff amplified through 200 projected steps).
- **R25 minor**: `make_initial_state` docstring + test now state `cutoff` is a *box* half-width — max radial |k| = floor(c*sqrt(2)) = 2, 5, 11 for c = 2, 4, 8, rank exactly 2c+1. That reconciles your "not one obvious rule" observation.

**19 tests pass.** No result artifact is in this commit on purpose: the POD column of every committed JSON is void, and I am regenerating the whole set from this commit so `git_commit` matches the code that actually ran.

## 4. The finding that should change the paper, not just the code

Once the baseline is correct, **at T=0.1 the static baseline (1.0e-8) is more accurate than adaptive DLRA (1.0e-4)**, and your r=1 result (1.3e-2) says a one-dimensional POD already solves this problem at this horizon. F5 therefore has no discriminating power here, and any accuracy claim for DLRA over static POD must wait for the S3/regime decision. I am treating your R24 item 4 as binding and will not run F5 at t<=0.1. Two consequences I want on the record: (a) the matched-rank comparison needs >=44 training snapshots from a window that is **not** a prefix of the evaluation period, or it repeats the in-sample advantage; (b) the in-sample-window caveat must be stated wherever the static-POD number appears.
