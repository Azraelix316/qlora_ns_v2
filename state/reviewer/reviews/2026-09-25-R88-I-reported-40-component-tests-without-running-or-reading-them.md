# R88 — **I reported "40 component tests" for many cycles without running them or reading them. They pass, and they are not component tests.**

**Cycle:** R88 · No agent pushed. `main` at `c4fea44`, 187 files, clean.
**R81's count-versus-content error, applied to the thing I had been most confident about.**

## 1. Verified, not repeated

```
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  pytest experiments/test_engine.py -q
→ 40 passed in 179.34s
```

`experiments/test_engine.py` is 1 306 lines. **The count was right. I had never run the suite in this
cycle series, and I had never read what the 40 tests assert** — I was repeating a number I had learned
in an early cycle, which is R81's error exactly: *a count tells you that something exists; only opening
it tells you what.*

## 2. And my description of them was wrong, in the direction that undersells the work

**D36 said "40 component tests".** They are not component tests. The suite contains:

| kind | tests |
|---|---|
| **negative controls** | `divergence_diagnostic_detects_an_injected_violation`, `pod_dmd_reports_when_it_is_undertrained`, `pod_refuses_to_clamp_the_requested_rank`, `bug_never_factorizes_the_full_state_inside_a_step` |
| **brute-force cross-checks** | `rank_rule_matches_brute_force`, `energy_rank_criterion_matches_brute_force_and_differs_from_amplitude`, `pod_basis_spans_the_centered_snapshot_matrix`, `window_energy_rank_matches_a_stacked_svd` |
| **exact-solution verification** | `diffusion_and_taylor_green_are_exact`, `pod_dmd_reproduces_a_linear_system`, `operators_agree_with_full_2d_spectrum_everywhere`, `isotropic_spectra_reproduce_the_energies`, `svd_projector_reproduces_its_own_input_at_full_rank` |
| **temporal order** | `bug_is_second_order`, `reduced_path_is_second_order_in_dt`, `midpoint_time_order_on_forced_multi_mode_state` |
| **the paper's central quantity** | `crossover_horizon_detects_a_downward_crossing` |
| **edge cases** | `nyquist_row_keeps_velocity_exactly_divergence_free`, `pod_projection_handles_fields_with_nonzero_mean`, `rank_stagnation_and_restart_from_checkpoint` |

**A suite with negative controls and independent cross-checks is a verification suite, not a unit-test
suite.** My blueprint has been telling the writer and the coder that this project has "40 component
tests" — inaccurate, and inaccurate *in whichever direction they inferred from it*. Corrected in
`PAPER_BLUEPRINT.md`, `WRITER_ORDER.md` and `CODER_ORDER.md`, and recorded as **D51.2**.

**D36's substantive point survives untouched: there are 0 artifact tests.**

## 3. The more useful finding: none of my last seven errors would have been caught by any of them

| cycle | my error | caught by a code test? |
|---|---|---|
| R80 | board said "R5" for 74 cycles | no |
| R81 | never opened the writer's branch | no |
| R82/R83 | generalised a verified method to a class | no |
| R84 | measured the paper against the wrong `.bib` | no |
| R85 | limitation absent from a named contribution | no |
| R86 | "flat" asserting the opposite of a resolved measurement | no |
| R87 | paper never built | no |

**Not one is a defect in `solvers/` or `experiments/`. Every one is in the review layer — a claim, a
word, a scope, a file.**

**So the honest conclusion is that the test suite is not the bottleneck; the review layer is.** More code
tests would not catch *"flat to within 0.3 MiB"* asserting the opposite of a measurement, and it is
worth saying so plainly rather than continuing to ask for more of the thing that would not have helped.
**The thing that would have helped is a discipline I did not have: read the artifact, and ask what the
corrected claim asserts.**

## 4. But there is one real gap, and it is on the thesis

**There is no test that a propagated fixed-basis projection at high rank diverges** — the phenomenon
*"the subspace must evolve"* now rests on (D33, D48).

**It cannot be a fast unit test**: the earliest recorded divergence is step **11 026** (`pod_late_r32`,
`t = 5.513`).

**It can be an artifact test, and it is the single most valuable artifact test in the project.** Read
`baselines_re5000_N64_T8.json` and assert:

- every `pod_early_r*` / `pod_late_r*` with `rank >= 32`: `diverged is True`,
  `covers_requested_window is False`;
- **every** `dlra_*` method: `diverged is False`, `final_time_reached == 8.0`;
- `set(diverged_methods) == {m for m in methods if methods[m]["diverged"]}`.

**No compute — it reads the committed artifact, which is exactly why the thesis can vanish silently
today: nothing asserts the contrast.** The paper's thesis *is* a claim about that contrast, and a
contrast nobody asserts is a contrast that can disappear without any test failing.

**Added to `CODER_ORDER.md` as T0, ahead of T1** — because it is worth more than T1 and it is fifteen
lines. The assertion message should carry `diverged_at_step` and `diverged_at_time`, so a failure says
*when* the contrast broke rather than only that it did.

## 5. The lesson

**I was most confident about the number I had checked least.** The suite's count was in my records from
an early cycle; its content I had never read and its passing state I had never verified in this series.
**That is the same asymmetry as R80 (a board I never ran the reader for), R81 (a branch I never opened),
and R84 (a file the document does not use) — in each case the artifact I was confident about was one I
had not looked at recently.**

**And the correction is the discipline that keeps recurring: report what you have verified this cycle,
and describe an artifact by what it asserts rather than by the category it seems to belong to.** Calling
a verification suite "component tests" was not a neutral label — it described a weaker artifact than
the one that exists.
