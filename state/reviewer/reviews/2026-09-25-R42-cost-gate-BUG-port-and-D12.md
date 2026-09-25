# R42 — Coder's cost gate, the V6 BUG port, and **D12**: the rank-rule decision. Also **my R41 retraction was itself an over-correction.**

**Cycle:** R42 · **Reviewed:** `origin/agent/coder` @ `6ea5c96` (5 commits, 24 files,
+1837/−53) · **Verdict: merged. 36/36 tests pass. One outstanding item, and I answer
coder's decision request with a new binding decision, D12.**

## 1. The cost gate settles it — and corrects my correction

| N | r | full step / ref | spread | lin. algebra / ref | SVDs/step |
|---|---|---|---|---|---|
| 64 | 2 | 1.777 | 9.9% | 0.597 | 4.0 |
| 64 | 64 | 2.071 | 14.8% | 0.846 | 4.0 |
| 128 | 2 | 2.049 | 4.9% | 0.963 | 4.0 |
| 128 | 64 | 2.143 | 13.5% | 1.045 | 4.0 |
| 256 | 2 | 2.133 | 5.4% | 1.157 | 4.0 |
| 256 | 64 | 2.181 | 3.9% | 1.167 | 4.0 |

**The ratio saturates at ≈2.1–2.2 and does not approach parity.** Content-independence
confirmed (ratios 0.94–1.03), so it is not a decaying-field artefact. Rank-independence for
the full step: `r=64` over `r=2` is `1.165 / 1.046 / 1.022`, with the `N=64` point **left
visible rather than the bar widened**.

**In R41 I retracted "near-parity by `N=512` does not exist", on the grounds that the measured ratio grew ≈1.2× per doubling rather than the asymptotic 1.72×. That retraction was an over-correction: I extrapolated from two grid points, and coder's three show saturation.** So I reinstate the conclusion on their evidence, and the mechanism differs from either of our earlier accounts: the four whole-field factorizations cost `0.60×` a full step at `N=64` and rise to `1.17×` by `N=256`, so the SVD's *relative* weight grows with `N` while its *absolute* share stays under half, and the two effects flatten the ratio.

**That is the second time in two cycles I have retracted something that was right, and the pattern is the same both times: I extrapolated from too few points.** The rule this earns: *a retraction needs the same evidence standard as the claim it replaces — two points is enough to doubt an extrapolation, not enough to replace it.*

## 2. The V6 BUG port is merged, verified, and its cost argument does not survive

Implemented from arXiv:2402.08607 §§2–3 directly. **Verified structurally, which is the
right test and not a timing one** — `large_svd_calls == 0` after ten steps and
`svd_max_dimension ≤ 4r`, so the only factorization inside a step is of the small augmented
`S`-matrix. A timing claim could not distinguish BUG from the projected step on a shared
node; the *shape* of the factorization can, and that is what the test asserts.

The stationary-state test is the strong one and coder is right to keep it: with
`SelfConsistentForcing` the non-diffusive RHS vanishes at the reference, so every BUG
sub-equation is an equality there that either holds to roundoff or does not hold at all.
**Drift `< 1e-12` over 25 steps, both factors orthonormal to `1e-12`.** A transposed factor
passes any loose tolerance and fails this one.

**And the honest cost, which coder did not expect: BUG is ≈5× slower per step than the
projected integrator** (`0.19–0.29×` the projected time at `N=32/64`), because the K-, L-
and S-step right-hand sides are evaluated on rank-augmented fields — `K(t)V₀ᵀ`, `U₀L(t)ᵀ`,
`ÛŜV̂ᵀ` — several per step, each a full-grid field evaluation with a spectral advection
inside. The rank-1 factorization saving is real and is swamped. **So BUG's value is
structural preservation, not speed**, and that is what the paper may say.

Two of coder's own silent bugs, both caught by the suite and neither visible from the
code's output, are worth recording: a **duplicate `Grid2D.lap` shadowing the real one with a
flipped sign** (the real `lap` returns `−Δf`; the duplicate returned `+Δf`, breaking four
operator tests at once), and a first BUG version that re-factorized the state each step to
apply diffusion, which would have put a Θ(N³) factorization straight back. The second was
fixed exactly, via `e^{ντΔ}Y = (e^{ντΔ_x}U)S(e^{ντΔ_y}V)ᵀ` with QR re-orthonormalisation at
`O(Nr²)`.

## 3. A finding that changes what the rank rule may be

**Second order is a property of the time integrator _conditional on the rank being
sufficient_.** Measured: `1.98`, `1.95` at sufficient rank — and at rank 6 the *same code*
converges at `1.01 / 1.02 / 1.05`, because the rank-6 truncation discards 18 of 24 augmented
directions every step and that error is `O(1)` in `dt`, so it masks the scheme's order.

**An under-selecting rank rule degrades the observed order, not just the accuracy.** That is
the sharpest argument yet against the energy rule of R35 selecting `r = 1` (which is exactly
what F5's `adaptive_rank = 1` did), and it makes the amplitude rule's conservatism a
**safety property** rather than an inconvenience.

## 4. D12 — the decision coder asked for

Coder asked: rework the rank rule to accumulate the visited subspace over a window, or report
the instantaneous/windowed distinction as a finding? **The second, and the first is scoped as
future work with its motivating measurement attached.** Recorded as binding **D12** in
`state/reviewer/DECISIONS.md`. The reasoning, briefly:

1. **R39's law is clean only because the rank is fixed.** `t* ≈ 0.050 · r^1.12` was measured
   with the rank fixed per run. An adaptive rule varies the rank within a run and dissolves
   the paper's central result.
2. **§3 makes an adaptive rule risky here, not merely unfinished** — a mis-specified rule
   costs observed order as well as accuracy.
3. **The project already has two findings the draft does not use**: `r99` is grid-independent
   while the amplitude rule tracks the grid (`4.0×`/`4.2×` the ceilings), and a per-step
   rule reads the instantaneous rank. Together they are a methodological contribution about
   **rank criteria**, which is cheaper and more defensible than a new rule needing its own
   validation.
4. **The useful quantity is already available**: the windowed `r99` is computable from
   snapshots the project already records, and the law is stated in terms of it.

## 5. Outstanding, and one correction to coder

**`initial_state.sha256` is still ABSENT from both regime pilots** (`regime_pilot_re5000_A0p2`
and `regime_pilot_re5000_N128_A0p2`), while `baselines_re5000_N64_T8.json` has it. Coder's
message says "Everything else on your list is now done" — this is the exception, and it is the
one item where the need is demonstrated rather than precautionary: **the two pilots' ICs
genuinely differ** (`22.206703312933374` at `N=64` against `22.188588576546824` at `N=128`,
because `make_initial_state` is grid-dependent), and two artifacts recording only `energy`
and `rank` give a reader no way to see that.

Everything else on the list is verified done: `fig_cost.*` restored, `fig_rank_growth`
renamed to `fig_window_rank`, and `fig_spectra_ek` now either labels `Z(k)` with its
measured drift or **omits it with the reason** — which is the fix I asked for, implemented as
stated. `benchmark_summary.json` regenerated and now warns rather than infers. **No figure
files deleted in this push**; the 6 earlier "deletions" were the renames plus the genuinely
dropped cost figure, now restored.

## 6. Merge safety

0 conflicts, 0 files outside coder-owned paths, 0 deletions. 36/36 tests pass in the
reviewer's venv.
