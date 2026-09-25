# R59 — I tested D20.4's cost assumption instead of leaving it as one, **and I was wrong about the cost.** The stationary-state question is now answered with evidence rather than asserted.

**Cycle:** R59 · **No agent pushed, so I tested my own assumption.** D20.4 scoped the paper to
describe the implemented shear rather than implement the Arnold–Korkin–Sinitsyn pump, on the
grounds that switching *"would invalidate every measurement in the project"*. **That is a cost
claim, and I had not tested it — I told coder to say so if changing the forcing was cheap, and
then did not wait.** Reviewer-measured, `Re=5000`, threads pinned, the project's own S2
criterion: **`|drift| ≤ 10%` on BOTH `E_fluct` and `Z_fluct`**, block-mean drift between the last
two thirds.

## 1. The forcing I implemented for the test

AKS: `f = (A sin(k y), −A k sin(k x) cos(k y))`, whose curl under the project's convention
`ω = ∂_x v − ∂_y u` is `zeta = −A k² cos(k x) cos(k y) − A k cos(k y)`.

The implemented driver uses `f = (A sin(k y), 0)`, `zeta = −A k cos(k y)`: a single-mode
unidirectional shear. **The two share the `y`-mode; AKS adds the transverse term that makes the
nonlinearity cellular.** The class is **~6 lines** against the existing interface.

## 2. The result: the Kolmogorov flow **does** have a stationary state, and the shear does not

| forcing | qualifying S2 horizons |
|---|---|
| **implemented shear** | **NONE** at any `A ∈ {0.2, 0.5}` or `N ∈ {64, 128}` (R32, R36) |
| **AKS pump** | **`N=64, A=0.2, T=4`** and **`N=128, A=0.2, T=2`** |

| `N` | `A` | `T=2` | `T=4` | `T=6` | `T=8` | `T=20` |
|---|---|---|---|---|---|---|
| 64 | 0.2 | — | **PASS** `8.9% / 6.5%` | — | fail `7.5% / 11.5%` | fail `2.1% / 27.0%` |
| 64 | 0.5 | — | fail `11.2% / 6.9%` | — | fail `38.1% / 15.4%` | fail `59.2% / 14.4%` |
| 128 | 0.2 | **PASS** `0.4% / 6.0%` | fail `8.5% / 12.2%` | fail `30.4% / 16.3%` | fail `6.6% / 19.3%` | — |

**This is the first thing that has ever distinguished the two flows, and it vindicates the
substance of D20.3** — that the absence of stationarity is a property of the *forcing* and not a
statement about the flow. **It is now tested rather than asserted: the Kolmogorov flow has
stationarity at `A=0.2`; the shear has none.**

## 3. But the qualifying window **shrinks under refinement** — so D20.4's *outcome* stands on
## different grounds

**`N=64 → T=4` passes; `N=128 → T=2` passes; `T=4` fails at `N=128` (`Z` drift `12.2%`).** And
`A=0.5` has **no** qualifying horizon at any `T` or `N`.

**That is exactly the fragility R32 found for the shear** — where a `T=3` window at `N=64`
vanished entirely at `N=128`. So switching to AKS **does not buy a robust stationary state; it
buys a narrower one that moves with resolution.** A validation window that relocates when the
grid changes is not a validation window.

**So D20.4's outcome is unchanged and its stated reason was wrong.** The paper still cannot
claim robust stationarity, and still must describe the implemented shear accurately. But the
reason is now **evidence** — *we tested the Kolmogorov pump and its qualifying window is
resolution-dependent and absent at `A=0.5`* — rather than an assumption about cost.

## 4. What this costs and what it buys, stated for the team rather than decided by me

- **The cost assumption was wrong.** AKS is ~6 lines. Switching is *cheap in code* and
  *expensive in re-measurement*: every rank-ladder, crossover, cost, memory and regime number in
  the project was measured on the shear, so switching invalidates all of it.
- **What switching would buy:** a paper that may legitimately be *about the Kolmogorov flow*, and
  a validatable quasi-steady state at `A=0.2` — which is the framing `AGENTS.md` describes and
  which D11.2 had to bar.
- **What switching would not buy:** a *robust* stationary state, because the window shrinks
  under refinement and vanishes at `A=0.5`.
- **My recommendation: do not switch.** The current framing needs no stationarity, the
  methodological contribution is the crossover sensitivity, and re-running everything would cost
  more than the framing is worth. **But that is a project-scale trade and the team may weigh it
  differently, so I record the option with its evidence rather than closing it.**

## 5. The paper's stationarity statement, now in its strongest supported form

> **Neither forcing admits a resolution-robust stationary fluctuation state at these parameters.**
> The implemented unidirectional shear admits none at any `A ∈ {0.2, 0.5}` or `N ∈ {64, 128}`;
> the Arnold–Korkin–Sinitsyn pump admits one at `A = 0.2` over `T ≈ 4` at `N = 64` and
> `T ≈ 2` at `N = 128`, so the window relocates under refinement, and none at `A = 0.5`. **The
> honest statistic is therefore a window-dependent quasi-steady fluctuation energy, reported with
> its window and its measured drift** — which is D20.3's re-attribution, now with a control.

**This is a strictly better statement than the project's current one**, because it is the
negative result *plus* the positive control that makes the negative credible.

## 6. Provenance

Reviewer-measured; the run wrote to `/tmp/opencode/r59_aks.json` and
`/tmp/opencode/r59_aks_N128.json`; **nothing was written inside the repository**, and no agent
branch moved. **Per D14.4 this is not yet citable** — it needs an artifact with a commit. **And
the AKS class would need to land in `solvers/forcing.py` for the result to be reproducible at
all**, which is coder's path and not mine; §4's recommendation is that it should not land, in
which case the result stands as a reviewer's control and the paper cites only the negative.

## 7. Merge safety

No merge this cycle. 160 files on `main`, unchanged.
