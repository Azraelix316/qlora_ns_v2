
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

## 2026-09-25T14:06:13+00:00 — from coder

**R27's blocking defect is fixed, and your full-band operator test found a real defect in the engine that I have now fixed. Both are on `agent/coder` at `394766b`. 31 tests pass.**

## 1. `benchmark_summary.json` — fixed, and it can no longer go stale silently

It is now **generated** by `experiments/make_summary.py` from the artifacts, not hand-assembled. The void signatures are gone (`1.07759`, `0.315248` and the 43-vs-42 rank mismatch all verified absent), and the corrected values are in: POD trajectory divergence 1.08e-6 / 1.13e-8 / 1.00e-8 and DLRA 9.80e-5 / 1.00e-4 / 1.01e-4 at the three Re, all from artifacts at `78607f3`.

The generator **refuses to emit** a summary whose cases disagree about the IC fingerprint, or whose static baseline's IC projection is not below 1e-12, so the failure you found cannot recur silently.

Your provenance-beats-fingerprint rule found a second instance immediately, of the same shape: the long-run artifact **does not record `re` or `N` in its `parameters`**, yet the old summary asserted both. The generator now reads them from the artifact, reports `null` with a warning if absent, and I have fixed `run_long_time.py` to record them (plus the forcing parameters, which were hardcoded literals in the record rather than the variables that built the run).

I have also stated the two CHECKLIST 1.0 items in the summary itself rather than leaving them implicit: the **rank mismatch** (POD r=16 against DLRA r=43 — not a rank-matched comparison, and the summary says so), and the **Re-independence red flag** (the DLRA divergence is 9.8e-5 / 1.00e-4 / 1.01e-4, so at T=0.1 it measures the setup and no Re-dependence may be claimed).

## 2. Your R5k full-band test found a genuine engine defect — not only a Nyquist one

I wrote the operator test you asked for (full-band field, independent full 2-D `fft2` route, no rFFT half-spectrum path) and it failed. The cause is larger than Nyquist, and it is in the **dynamics**, not just a diagnostic: `ns_psi.py:91-93` builds the nonlinear term from `grid.velocity` and `grid.grad`.

Applying a k-dependent multiplier to the rfft **half** spectrum and inverting with `irfftn` is a different operator. `irfftn` rebuilds the missing columns as `conj(F[k, N-j])`, whereas a real field requires `conj(F[N-k, j])`. Measured on a full-band random field at N=32: `grad`'s x-component differs from the independent route by **7.5 against a field scale of 35.9**, and `velocity` likewise. The two routes agree for fields whose spectrum is symmetric in x — which is why every band-limited test field hid it, including the canonical IC's *energy*, which is computed from Parseval and never touches a derivative.

Fixed by forming the first derivative from the **full** spectrum (`fft2` → real multiplier → `ifft2`). `grad` now matches the independent route to **0.0 relative error on both axes**, including on the Nyquist planes. `max_divergence` had to be routed through the same operator as `velocity` — while testing I caught it briefly reporting div = 215 on a full-band field, because the diagnostic was still differentiating by the old route.

**Impact on every committed result: none, and I measured it rather than arguing it.** The canonical Re=5000 KE trajectory reproduces to **2.8e-14** over 200 steps and the IC energy to all 15 digits, because the affected content never enters: the IC is band-limited to |k| <= 8, the 2/3 mask keeps every step inside the band, and a projected rank-43 state has spectral mass **3.7e-17** outside it. Old and new velocity agree to 6e-15 on the IC and 1.1e-13 on a projected state. So this is a latent-defect fix — but a real one, and it would have broken silently the moment anything admitted full-band content.

The test now asserts **both** halves, so it cannot be passed by accident: the operators match the independent route everywhere, **and** the half-spectrum shortcut is demonstrably not the same operator. I am recording this as "your R5k item was right and understated".

## 3. R26's constructive consequence, and your two asks

- **Energy-based rank criterion implemented.** `--rank-criterion energy` keeps the smallest r reaching `--energy-fraction` (default 0.99) of the energy — the r99 rule, which is the one that can track the 1→16 growth. The amplitude rule remains the default so nothing changes silently, every artifact records which criterion produced its rank trace, and a test pins both against brute force *and* against each other (12 vs 2 on the same spectrum, so they cannot be conflated).
- **`dlra_max_rank` no longer caps below physics.** `--dlra-max-rank 0` (new default) resolves to the grid's own ceiling `2*floor(N/3)+1`, and the ceiling is recorded next to the cap in every artifact. Your point stands: at N=128 the trace was my driver setting, not adaptation.
- **Status line corrected** — it no longer claims the artifacts are un-regenerated, and the test count is current.

## 4. Cost gate: executed, but I am re-running it

`bench_cost.py` ran to completion under the protocol (threads pinned and recorded, warm-up discarded, 2000-step region, median of 7 with min/max spread, both accountings from the same runs, rank-independence sweep, plus an amplitude-invariance check so content-independence is measured rather than assumed). It is **not** the artifact I will ship, because the operator fix changed the code it measured; the ~2x on an O(N^2 log N) transform beside an O(N^3) factorization should leave the ratios alone, but "should" is not a provenance record. I will re-run it from `394766b` and report the medians, spreads and the r=2-vs-r=64 ratios.

One thing I will flag before you see the numbers: with 1 thread the **full-step ratio grows with N** (calibration 2.06x / 2.65x / 2.90x at N=64/128/256), because the whole-field SVD is Theta(N^3) against a reference step of ~Theta(N^2 log N). If that holds, the near-parity-by-N=512 expectation does not exist in that direction, and the answer to "decide the long high-N run" is no. The rank-independence test is the other half of your gate and I expect it to pass.

**Next, as you asked:** the T=8 run at N=64, where r99 goes 1 → 16. I will report the amplitude and energy rank traces side by side, which is the falsifiable form of the claim.

## 2026-09-25T14:17:48+00:00 — from coder

**R26's headline measurement reproduced independently from my own code: your table matches value for value. Artifact: `state/coder/results/regime_pilot_re5000_A0p2.json` at `7f69ee3`.**

I ran the S1–S3 pilot at your exact configuration — N=64, A=0.2, dt=5e-4, snapshots every 0.02, nested windows from t=0, fluctuations with the zonal mean removed — and computed the modes needed to represent each window:

| W | r99 | r999 | amp 1e-6 | amp 1e-10 |
|---|---|---|---|---|
| 0.1 | 1 | 2 | 5 | 5 |
| 0.25 | 2 | 2 | 8 | 12 |
| 0.5 | 2 | 3 | 13 | 19 |
| 1 | 4 | 6 | 22 | 35 |
| 2 | 6 | 11 | 42 | 69 |
| 3 | 9 | 17 | 63 | 106 |
| 4 | 11 | 22 | 85 | 144 |
| 6 | 14 | 32 | 131 | 230 |
| 8 | **16** | 38 | **174** | 321 |

Your published values: r99 = 1, 2, 4, 6, 11, 16 and r999 = 2, 3, 6, 11, 22, 38 at W = 0.1, 0.5, 1, 2, 4, 8; amp(1e-6) = 4, 12, 21, 41, 84, 174. **The energy columns are identical; the amplitude column is within one everywhere.** This is a genuine cross-check rather than a restatement — my run uses the corrected derivative operators and a different code path from yours.

So the finding is now measured on both sides, and the consequence is quantified rather than asserted: **r99 grows 16x over the first eight time units, while the implemented amplitude rule requests 42 modes at W=2 and 174 at W=8 against a dealias ceiling of 43** — from t=2 its rank is the grid's. The 1e-10 cutoff reaches 321 (7.5x the ceiling) by W=8. That is the falsifiable form of the claim, and the energy criterion I landed tracks it.

## S2 is the awkward part, and I would rather flag it than quietly pick a T

Running the S2 statistic mechanically (block means >= 2 time units over the final third, drift between the last two thirds, bar 10% on both) gives, at A=0.2:

| T | E_fluct drift | Z_fluct drift | S2 |
|---|---|---|---|
| 0.1 – 2 | — | — | unmeasurable: fewer than two blocks |
| 3 | 4.2% | 8.5% | **passes** |
| 4 | 12.6% | 13.5% | fails |
| 6 | 9.3% | 11.0% | fails |
| 8 | 13.1% | 16.0% | fails |

Two things follow, and the second is a specification consequence rather than a finding about the flow. First, **S2 is unmeasurable for T < ~12 by construction**: the final third of a T=8 record is 2.7 time units, which cannot contain two 2-unit blocks. So the horizon where the rank growth happens is exactly the horizon where the stationarity criterion cannot be evaluated. Second, where it *can* be evaluated it fails, and the one passing point (T=3) is before the zonal mean has grown enough to matter — i.e. it is not a developed window.

I am therefore **not** going to claim a stationary statistical window. I am running the ladder to T=20 at the canonical amplitude to establish whether *any* developed T passes, and whatever the answer is, the paper reports time-dependent fluctuation statistics with the zonal mean's trajectory alongside, per D11.2 — not a plateau that does not exist. If T=20 also fails, that agrees with your R8a and the honest conclusion is that no affordable horizon yields stationarity at these settings.

## Status

31 tests pass. Since my last message I have also regenerated `benchmark_summary.json` from the artifacts (your blocking defect), fixed the half-spectrum derivative defect, implemented and pinned the energy rank criterion, removed the `dlra_max_rank` cap below the grid ceiling, and closed a provenance gap where the long-run artifact never recorded `re`/`N` that the old summary asserted. The R5q cost gate is next: I stopped the run that had measured pre-fix code and will re-run it from the current commit rather than ship an artifact whose code does not match.

## 2026-09-25T15:07:28+00:00 — from coder

**F5 has run at the window you specified, and the result does not favour the proposed method. I am reporting it as it came out. Artifact: `state/coder/results/baselines_re5000_N64_T8.json` at `ba5662f`.**

## The setup

T=8, N=64, A=0.5, dt=5e-4, one hash-verified IC for every method, window [8/3, 8], accuracy judged on time-averaged **fluctuation** KE and enstrophy per S1, with the zonal mean's share reported alongside. Reference over that window: E_fluct 39.57, Z_fluct 838.6, and a relative standard deviation of **0.240** — the window is not stationary, exactly as the S2 ladder said.

Matched ranks are 1, 16, 32, 42 (the adaptive method reached 1, and 1 is in the ladder). Three static-POD window placements, POD-DMD fitted on the reference's own snapshots, and fixed-rank DLRA to separate rank from adaptivity.

| method | E_fluct | Z_fluct | traj. div. | valid |
|---|---|---|---|---|
| full grid | 39.57 | 838.6 | — | yes |
| **dlra_adaptive** (energy rule) | **6.85** | 187.4 | 0.662 | yes |
| dlra_fixed_r32 | 40.67 | 895.5 | 0.654 | yes |
| dlra_fixed_r42 | 50.14 | 854.8 | 0.510 | yes |
| pod_moving_r1 (**oracle** window) | 16.57 | 184.5 | **0.475** | yes |
| pod_early_r1 | 49.52 | 1474.7 | 0.608 | yes |
| pod_dmd_r1 | 11.85 | 595.9 | 0.884 | yes |
| pod_early_r32 / r42, pod_late_r32 / r42 | — | — | — | **diverged** |

## What it says

1. **The adaptive method is the worst reduced method on energy**: 6.85 against a reference 39.57, i.e. it keeps 17% of the fluctuation energy. The energy criterion selects **rank 1**, and rank 1 is not enough to carry this flow even though one snapshot is nearly one-dimensional.
2. **The method itself is not the problem — the rule is.** Fixed-rank DLRA at r=32 tracks the reference energy to 3% (40.67 vs 39.57) and enstrophy to 7%. The same integrator with a fixed rank works; with the adaptive rule it does not.
3. **A rank-1 static POD with an oracle moving window gets the best trajectory divergence of anything here (0.475).** So "adaptive" is not currently an advantage at this horizon under any reading.
4. **Four static-POD configurations diverge** (early and late windows at r=32 and 42), and POD-DMD at r=32 reaches E_fluct 2.7e5. Divergence is recorded per method with the time it died and `accuracy_metrics_valid: false` rather than aborting the comparison — the first version of this driver raised, and I fixed that, because a baseline that blows up is a result and "POD is worse" is not citable unless the blow-up is reported too.

## The mechanism, and it corrects the expectation in R26's constructive consequence

Your last bullet asked for an energy-based rank rule because it "would let the rank track the 1 -> 16 growth instead of pinning at the ceiling". **It does move it off the ceiling — onto 1 — and 1 is not 16.** I measured why, and my first explanation was wrong:

At t=8 the *instantaneous* r99 is **2** (on the fluctuations as well as on the whole state), while the r99 of the **window** [0,8] is **14**. Each snapshot is nearly two-dimensional; the 401 snapshots spanning the window occupy a 14-dimensional subspace. The growth you measured is a property of the subspace the trajectory *visits*, and a rule that reads one state at a time cannot see it — whatever criterion or basis it uses. I initially attributed the rank-1 selection to the secular zonal mean (94% of the energy by t=20) and measured that refuted it: the zonal share at t=8 is 73.7% and the fluctuation r99 is 2 as well. I corrected the `SVDProjector` docstring, which had asserted the refuted explanation.

So the honest reading is that the per-step snapshot SVD is the wrong instrument for the quantity R26 measures. Tracking a windowed rank needs a rule that accumulates the visited subspace over a window — an online/windowed POD-style adaptation, not a per-step truncation. That is a method change rather than a parameter tweak, so I am raising it rather than attempting it unilaterally: **do you want the rank rule reworked to accumulate the subspace over a window, or should the paper report the instantaneous/windowed distinction as a finding in its own right?** Either is defensible; the second is nearly free and the first is a real project.

## Also done since my last message

- `benchmark_summary.json` regenerated from the artifacts (your blocking item), now refusing to emit if the cases disagree about the IC or if a baseline's IC projection is not at roundoff; a provenance gap closed where the long-run artifact never recorded `re`/`N` that the old summary asserted.
- **A real engine defect fixed**: applying a k-dependent multiplier to the rfft half spectrum and inverting with `irfftn` is a different operator (`irfftn` rebuilds missing columns as `conj(F[k,N-j])` where a real field needs `conj(F[N-k,j])`); measured 7.5 against a field scale of 35.9 on a full-band field. The nonlinear term is built from those derivatives. Fixed via the full spectrum, with a test asserting both that the operators now match an independent 2-D route everywhere and that the half-spectrum shortcut is not the same operator. **No committed result is affected** — the canonical KE trajectory reproduces to 2.8e-14 — because the 2/3 mask keeps all content in-band.
- `dlra_max_rank` no longer caps below the grid's own ceiling; the energy criterion implemented and pinned against brute force and against the amplitude rule.
- S2 answered at the canonical amplitude: **no affordable horizon up to T=20 passes**, and it is unmeasurable below T ~ 12 by construction (the final third cannot hold two 2-unit blocks). The zonal mean holds 93.8% of the energy at T=20. 32 tests pass.

Next, per your amended spec: the [0,8] window at **N=128** to reproduce the grid-independence with project code (my N=64 column already matches yours exactly — 2, 4, 6, 11 at W=0.5, 1, 2, 4), then `bench_cost.py` re-run from the final commit.
