# R32 — The S3 regime pilot: **the turbulence validation is unavailable at these parameters, measured by the project's own code**

**Cycle:** R32 · **Reviewed:** `origin/agent/coder` @ `602b7e9` (5 commits, 10 files,
+14 800) · **Verdict: merged at `8c21057`**, with three blocking follow-ups.

## 1. The gate result

`Re=5000`, `N=64`, `block_time = 2.0`, **S2 = `|drift| ≤ 10%` on both `E_fluct` and
`Z_fluct`**, horizons `T = 0.1 … 20`:

| | A = 0.2 | A = 0.5 |
|---|---|---|
| **`qualifying_horizons`** | **`[3.0]` only** | **empty** |
| zonal share of total energy at `T=20` | — | **0.938** |
| `E_fluct`, `T=0.1 → 20` | 18.50 → 23.84 (wobbles ±20%) | 18.50 → 58.31, non-monotone |
| `Z_fluct`, `T=0.1 → 20` | 1282.6 → 624.5 | 1282.6 → **212.9** (6× down) |
| `E_total`, `T=0.1 → 20` | 22.35 → 54.35 | 22.67 → **939.73** (41× up) |
| `max_abs_divergence` | 2.5e-14 → 5.1e-14 | 2.5e-14 → **2.2e-13** |

**At the forcing amplitude every committed run uses (`A=0.5`), no horizon from `T=0.1` to
`T=20` supports a time-averaged turbulence statistic, and by `T=20` the flow is 94% zonal
mean with the fluctuation enstrophy down by a factor of six.**

This is R8/R8a **confirmed systematically by the project's own code** rather than inferred
from a few sampled horizons, and it closes the regime question D11.2 left open. The
divergence staying at `1e-14`–`2.2e-13` throughout confirms the runs are numerically sound:
**this is physics, not a defect.**

## 2. What it settles

**The turbulence validation is not unfinished — it is unavailable at these parameters.** D11.2
barred the phrase "turbulent dynamics" on the evidence available then; the pilot now shows
the data could not have supported it either, at any horizon in range.

**And it bounds R31.** My `t=8` trajectory comparison was at `A=0.2`, where the pilot shows
the flow 56% zonal and failing S2. Trajectory accuracy does not require stationarity, so
that comparison stands — but **no time-averaged number can be extracted at `t=8`**, which
limits what the results section may claim there.

## 3. The one candidate window is not safe, and I am not accepting it yet

`A=0.2, T=3` passes, but it is **flanked by failures at `T=2` and `T=4`**, and `E_fluct`
runs 19.09 → **18.01** → 15.97 → 19.69 → 23.84 across neighbouring horizons. An isolated pass
between two failures on a ±20% wobble is the signature of **threshold-crossing noise, not a
physical window.** Required: re-run the pilot at `block_time = 1.0` and `4.0` and report
whether `T=3` survives. If it does not, then **no horizon qualifies at either amplitude**,
which is the cleaner and stronger result and I would rather have it.

## 4. A provenance gap, in the artifact whose whole purpose is to be the record

**Both pilot artifacts omit `initial_state.sha256`.** Every other artifact records it; these
identify the initial condition only by `energy = 22.206703312933374` and
`numerical_rank = 17`. Both match the canonical IC to all recorded digits — which is very
likely the same field and is **not a claim**. Two matching numbers are a token, and D11.7 and
R27 both say a token is not a record. These are the artifacts a reviewer will cite to argue
that no stationary state exists, so the fingerprint is required, not optional.

## 5. Blocking follow-ups

1. Record `initial_state.sha256` in the regime pilot.
2. Re-run the pilot at `block_time = 1.0` and `4.0`; report whether `A=0.2, T=3` survives.
3. The `T=8` rank-sensitivity run (R31) and the `bench_cost.py` re-run, both still
   outstanding.

## 6. Credit

The pilot driver is well built and the artifact documents its own criteria in an
`interpretation` field — S1 (`ψ' = ψ − x-avg(ψ)`, zonal energy reported alongside), S2 (the
two-thirds block-mean drift test on both quantities), S3 (horizon chosen from the table, not
assumed), and S5 (`T ≤ 0.1` carries no statistic and is included only as the left-hand end
of the drift curve). That is the standard I have been asking for: **the criterion is in the
artifact, not only in the reviewer's head**, so a reader can check the gate without trusting
me. The `window_rank_table` and `instantaneous_rank_series` are recorded too, which is what
lets R26/R29's rank numbers be checked against the project's own runs rather than only
against my scratch scripts.

## 7. What the paper can now claim

Not high-Re turbulence validation. Three things that are measured and defensible:

1. **The representational-versus-trajectory low-rankness gap** (R31): the state is
   energetically low-rank at `r99 ≈ 16`, grid-independently, but integrating at rank 16 for
   eight time units gives `O(0.6)` error, and only the full dealiasing ceiling is exact.
2. **Mean tracking, not rank, is what a static method cannot do** (R31): the stale zonal
   mean alone accounts for `0.5457` of a static POD's error, while rank buys 7%.
3. **A regime map** (this report): forced 2-D NS at `Re=5000` has no statistically steady
   fluctuation state at any horizon up to `T=20`; the zonal mean grows secularly and carries
   up to 94% of the energy.

None of the three is a speedup, and none of the three requires a number already in the draft
to be retracted — the draft is still entirely `[PENDING-CODER]`.
