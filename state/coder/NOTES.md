# NOTES.md — coder

> Branch: `agent/coder` · Worktree: `worktrees/coder`
> Status: C11-1 closed -- all six of the paper's figures now exist as PDF and
> PNG in `paper/figures/`, generated from the artifacts, with two of the draft's
> captions corrected against measurement (`fig:tg`'s rank decay `3->2->1` cannot
> happen on a single Fourier mode and is in fact constant at 1; `fig:rank` has no
> spin-up growth and no `r*(Re)`, since `r* = 43` at every Re). Also this cycle:
> C7-4/C7-5 (zonal shares as scalars, on every arm, with the share now shown to
> be horizon-dependent -- it roughly doubles from T=0.1 to T=1.0); a real bug
> where one diverged method's `inf` destroyed a sixteen-configuration run at the
> JSON write, now sanitised and pinned by a test; D17.2 confirmed (r=43 yields at
> N=128, t*=2.885) and D118 retired; and the crossover block now *takes* its
> value from the rows rather than only comparing them. **One item I could not
> close: `check_paper_builds.py` resolves `\includegraphics` against the
> including section rather than the document root, so it cannot pass with the
> figures where `main.tex` says they belong; I have no TeX toolchain to prove the
> resolution and declined to mirror into a second directory to turn the gate
> green on a rule I believe is wrong.** In flight: both crossover surfaces
> re-running with the block fix. 41 engine tests pass.

## Mission

Build and run the numerics: the SP-DLRA engine (structure-preserving split,
exact divergence-free, stream-function form for 2D NS), the high-Re
forced-turbulence test cases, and the benchmark numbers the paper will cite.

## Owned paths (write only here)

- `state/coder/` — this board, run logs, results (text/JSON, keep files small)
- `solvers/` — engine code
- `experiments/` — drivers, configs, benchmark scripts, outputs

## First TODOs

- [x] Read `lessons_learned.md` and the general directions in `AGENTS.md`.
- [x] Build the SP-DLRA engine, informed by the lessons learned. A good
      first test is a simple laminar case (Taylor–Green): check max |∇·u|
      ~ 1e-14, kinetic-energy behavior, and that the rank stays small,
      before moving to turbulence.
- [x] Implement the 2D forced-turbulence drivers (Kolmogorov flow / 2D forced
      NS) per the scope decision in `state/reviewer/DECISIONS.md`.
- [x] Benchmarks: full-grid spectral vs static POD vs adaptive DLRA,
      Re ∈ {100, 1000, 5000}; track rank + max rel L2 vs full grid.
      Log summaries to `state/coder/results/` (one small file per run).
- [x] Send a readiness note to `writer` once the first numbers exist.

## Log
- 2026-09-26 **C8-3: the reproducibility claim is now a test, not a sentence.**
  `test_a_committed_artifact_reproduces_bit_for_bit` re-runs the canonical suite
  configuration and compares it to the committed artifact field by field,
  requiring **bit-identity** (`==`, not `isclose`) -- a tolerance would let a
  drift of any size pass provided it stayed small, which is the failure the claim
  exists to exclude. Measured: **5567 fields, 0 differences.** Positive control:
  perturbing one `energy_history` sample by **1 part in 1e15** is caught
  (`22.519825977206665` vs `22.51982597720664`), so the gate fails at the last
  bit. The timing/provenance exclusion list is written out rather than
  pattern-matched, and the test asserts it compared >500 fields so a refactor
  cannot make it vacuous. Cost 3.5 s. The canonical argument list lives once in
  `experiments/_paths.py`, because a second drifting copy is how a reproduction
  test becomes vacuous by re-running something *near* the committed setup.
- 2026-09-26 **A sixth instance of the same error shape, caught by my own smoke
  test.** Restructuring the crossover block so `t_star` comes from the rows, I
  read `crossover_horizon()["bracket"]` unconditionally -- but that key exists
  only on the *resolved* branch, so the write raised `KeyError` for exactly the
  `never` and `unresolved` ranks. `test_every_driver_runs` caught it in 3.5 s. The
  in-flight N=128 run had the broken code loaded and was at r=85, the `never`
  case, about to crash after an hour of compute; killed and relaunched only after
  verifying all three status branches write. **The running tally this cycle:
  six errors, every one of them the same shape -- taking a mechanism from a
  description instead of from the code or the artifact, and the description
  being plausible.** Four of the six would have been caught by two minutes of
  reading. Recorded rather than claimed fixed.
- 2026-09-26 **A third paper caption does not survive the artifact.**
  `fig:svd` says "slower decay at higher Re". True in direction, weak in size:
  `sigma_20/sigma_1` = 1.967e-3 / 2.310e-3 / 2.343e-3 at Re = 100/1000/5000,
  which is **+19% across a fiftyfold range of Re** and invisible on a log axis
  spanning the fifteen decades the panels cover; the mode count above 1e-10 is
  **43 at all three**. The spectra do differ pointwise (max relative difference
  up to 0.97), so these are not three identical arrays -- three arrays whose
  summary barely moves. Both numbers are now printed per panel and stated in the
  caption, so the claim is quantified rather than asserted. **That is three of
  the paper's six captions carrying claims the runs do not support** (fig:tg's
  `3->2->1`, fig:rank's spin-up and r*(Re), fig:svd's Re-dependence), so the
  remaining three deserve the same scrutiny before submission. Also: the three
  SP-DLRA curves in `fig:error_vs_ref` coincide over `t <= 0.1`, so the legend's
  six entries are three distinct curves; the caption now says so.
- 2026-09-26 **C11-1 closed: all six of the paper's figures exist, in
  `paper/figures/`, 12 PDF + 12 PNG, generated by `make_figures.py`.** The five
  the paper includes and no code wrote are `fig_tg_ke_rank`, `fig_rank_vs_time`,
  `fig_sv_decay`, `fig_error_vs_ref`, `fig_ke_spectrum`; `run_taylor_green.py` had
  to be instrumented first because it carried only scalars and a caption asking
  for `E(t)` and `r(t)` had nothing to draw from. The mirroring also fixes the
  second defect: per-figure copying would only have reached the five new ones,
  and `fig_cost` existed, was generated, and still did not resolve. The script
  now mirrors every figure it wrote and **removes any figure file in the paper's
  directory it did not write**. Only generated images go into the writer's tree;
  no prose, no .tex, and the code stays on my side of the ownership line.
- 2026-09-26 **Two of the paper's captions say things the runs do not support.**
  `fig:tg` claims the rank decays `3 -> 2 -> 1`; it is **constant at 1**, and
  cannot be otherwise, because the initial condition is a single Fourier mode
  (`sin(X) sin(Y)`, numerical rank 1) so there is nothing further to request. Its
  other claim *is* supported and is now shown rather than asserted: `E(t)` falls
  9.8696 -> 9.9108 with **0 increases in 100 steps**, printed on the figure.
  `fig:rank` claims "growth during spin-up, then a quasi-stationary r*(Re)";
  measured at all three Reynolds numbers `r` goes **17 -> 43 at the first check
  (t=0.0075) and is flat**, and `r* = 43` at Re = 100, 1000 and 5000 alike, so
  there is no `r*(Re)` and the value is the top of the band N resolves -- a
  property of the discretisation, not the dynamics. The window rank is the
  quantity that measures the dynamics and it is 16 at both grids. Both figures
  say what the runs say; `CAPTIONS.md` flags both false claims for the writer.
- 2026-09-26 **`check_paper_builds.py` cannot be satisfied and I think the rule is
  wrong.** It resolves `\includegraphics` relative to the *including section*
  (`paper/sections/figures/...`), but `main.tex` does `\input{sections/...}`
  from `paper/`, so the document root is `paper/` and LaTeX looks in
  `paper/figures/` -- where the figures are, and where the order said to put
  them. **No TeX toolchain on this node, so I cannot demonstrate it
  empirically, and I did not mirror into `paper/sections/figures/` to turn the
  gate green on a rule I believe is wrong.** Referred to the reviewer with three
  options; status reported as unverifiable rather than passed.
- 2026-09-26 **A diverged method destroyed a whole run at the write.** The
  Re=1000 rank ladder computed all sixteen configurations correctly and then
  raised `ValueError: Out of range float values are not JSON compliant: inf`:
  a diverged method gives an infinite `relative_l2`, `run_baselines.py` writes
  with `allow_nan=False` (correct), and the encoder refused the entire artifact.
  `allow_nan=False` stays; the output is now sanitised, the replacement count is
  recorded, and `test_a_diverged_method_cannot_destroy_the_whole_artifact` pins
  it -- including that the survivor's values and the *magnitude* of the
  divergence both survive. **The bug was never the infinite value; it was one
  method's infinity taking the other fifteen down with it.**
- 2026-09-26 **C7-5: the zonal share is horizon-dependent.** The long run needed
  the psi' series **sampled at the same stride as the totals** -- the totals are
  sampled every 100 steps and the fluctuations every step, so differencing the
  lists gave a silent `null` for the number the paper's mechanism section leans
  on. Second instance of the same pattern as the missing `pod` zonal block: a
  diagnostic present in the code and absent in the artifact for one arm. Fixed,
  and the share now has a horizon: **E zonal 0.1621 -> 0.1840 at T=0.1 but
  0.1621 -> 0.3216 at T=1.0**, so it roughly doubles over 10x the horizon and any
  "the zonal mean holds X%" statement has to name T. The enstrophy share is flat
  (0.0350 -> 0.0354).
- 2026-09-26 **D17.2 confirmed, D118 retired, and the block now takes its value
  from the rows.** The N=128 surface resolves **r=43 at t* = 2.885** while r=85
  never yields, so the never-yields rank is grid-dependent -- 43 at N=64, 85 at
  N=128 -- and is not a grid-free statement. My previous block fix only
  *compared* the two values and the comparison came back False every time,
  because a comparison changes nothing; `t_star` and `bracket` are now computed
  by `t_star_from_rows`, with the old implementation kept as `t_star_legacy`
  plus `agrees_with_legacy` and `legacy_relative_offset` so the 6-9%
  discrepancy stays measurable rather than being overwritten.
- 2026-09-26 **RETRACTION: "construction, not evolution" was wrong, and the arm
  that produced it was not a control.** C6-4's six arms show that a basis fitted on
  zonal-mean-removed snapshots and propagated **also overflows** (t=4.438, sooner
  than the raw basis's 5.388). So the zonal mean is not the mechanism, and C6-5's
  premise is false as stated. The deeper error: `SVDProjector.project` recomputes
  `self._svd(field)` on **every** call, so there is no stored basis and the
  per-step projection is a fresh rank-r truncation of whatever field it is handed
  whether or not `check_every` fires. `check_every` gates the **rank**, not the
  projection -- my "frozen" arm was a second instance of the adapting arm, and
  their agreement was not evidence about construction. The class has no switch
  that stops the projection re-deriving, so "hold the rank fixed and see whether
  the subspace must still move" cannot be run through it at all. **What the arms
  do establish is the paper's own claim and not a narrower one: propagated
  overflows, re-derived survives, same rank / runner / IC / splitting.** Corrected
  in the test docstring, `results/README.md`, and the C6-6 comment in
  `solvers/dlra.py` -- the last of which I had written in the reviewer's favour
  twenty minutes earlier, on a framing that measurement contradicts. Added
  `DLRA.basis_builds` so the two are distinguishable from the object rather than
  from the configuration.
- 2026-09-26 **C6-4's non-monotonicity, recorded as a finding.** Overflow time by
  rank, raw / fluctuations: 14 -> 5.478/4.080, 15 -> 3.922/4.960, 16 ->
  5.388/4.438, 17 -> 2.952/**survives**, 18 -> **survives**/2.876. Not monotone,
  and **the surviving basis flips between r=17 and r=18**, so rank is not a
  threshold here and "the rank at which it fails" is not well defined. All six
  seed/basis combinations overflow across seeds 20260925/7/991.
  `static_basis_construction_N32.json` is on committed code, `reproducible: true`,
  and its `interpretation` is **generated from the arms** so it cannot assert a
  mechanism the run does not support.
- 2026-09-26 **C9-1 and C6-3, C7-1..3.** `working_tree_dirty_paths` is now
  recorded, which is what makes the module's own exemption ("a rewritten result
  file alone does not invalidate a run") claimable by a reader rather than only by
  me. The C6-1 docstring's "about 25 s" became a range -- 17 s idle, 27 s under my
  load, 35 s and 56 s on the reviewer's node -- because a single figure implied a
  precision a load-dependent measurement does not have. `fig_crossover`'s right
  panel now plots **both** rank sets so the title matches the axis (C7-1) and is
  scoped to the grid the data is from (C7-2). C7-3: my comment there said the
  fluctuation was "only 32%" of the energy -- that is the N=32 figure, written
  into an N=64 panel where it is **83.8%**, so the comment had the direction
  backwards and the total is fluctuation-dominated.
- 2026-09-26 **The rank ladder found the threshold, and r=24 is what found it.**
  Re=5000, N=64, T=8, ranks {16, 24, 32, 42} at two window placements: r=16
  survives both; **r=24 overflows at t=6.085 with the early window and survives
  with the late one**; r=32 and r=42 overflow at both. So the threshold is
  bracketed -- (16, 24] early, (24, 32] late -- where the previous ladder
  {16, 32, 42} was merely *consistent with* a threshold anywhere in (16, 32].
  Three separate findings, not one: (a) a clean threshold in r exists; (b) at the
  threshold **window placement decides the outcome** and only at the threshold,
  which is R27's mechanism as a clean statement rather than a trend, and is the
  strongest form of "the subspace must evolve" the project has; (c) the
  divergence time is confirmed **non-monotone** in r (6.085 -> 6.960 -> 5.742),
  so no growth law may be written -- the lowest rank that diverges is the one
  that diverges *latest*. Every DLRA arm survives to t=8 at r = 1/16/24/32/42
  with max|div u| <= 1.11e-13, so the proposed method is on the surviving side
  at both ranks where a static baseline of the same rank is not. This artifact
  has **no D39.4 residual column** (launched before the fix) and is not used for
  the residual claim.
- 2026-09-26 **D22.5 made executable, and it is a two-sided result.** The
  `crossovers` block sits **6.4-8.5% below the rows in all 12 resolved cases**,
  one-signed, at both Re, all three windows, both ranks -- and I could not
  reproduce D23's 0.52-0.64x (my factor is 0.915-0.936x), so the recorded
  magnitude should be 6-9%, not 36-48%. It is not a column choice (0.5%) and not
  a convention (7%); the block is further away than the whole interpolation
  spread. **Every bracket agrees exactly**, so the qualitative statement survives
  and the point estimate does not. `t_star_from_rows(rows, rows, column,
  log_interp)` is now the single path, the column is required and never
  defaulted, and the block carries the rows' value plus both conventions plus
  `agrees_with_rows` at a 2% tolerance.
- 2026-09-26 **C8-1: the summary records what it was built from.**
  `benchmark_summary.json` now emits a `provenance` block listing every input
  with its own commit, driver and `reproducible`, assembled *after* the loads.
  Three states are distinguished rather than collapsed: `false` is a **failed
  check** (WARNING), absent is a **check never run** (NOTE -- `taylor_green.json`
  names a commit but nothing verified the driver against it), and no commit is
  **not traceable** (WARNING). Collapsing them is what made the old block
  unreadable.
- 2026-09-26 **D30.2 caught me a second time, in the fix for C1-3b.** My
  `_rank_finding` called 43 "the top of the band N=64 resolves without aliasing",
  i.e. a mode count. It is a *wavenumber*; the dealiased 64x64 grid carries ~1849
  dof. Now stated as CLAIMS.md section 2 states it: r99 grows 1->16 and measures
  the dynamics, the amplitude rule's request reaches 174 modes and measures the
  discretisation, it grows with the grid and no fixed cutoff repairs it, and the
  wavenumber is deliberately not quoted as a mode count. The `--rank-criterion`
  help text said the amplitude rule "saturates at the dealias ceiling"; it does
  not, its request grows with the grid.
- 2026-09-26 **D66: the flat `< 1e-12` divergence bound is now resolution-scaled.**
  `divergence_tolerance(grid) = 0.5*eps*N**2` in all seven divergence assertions,
  margins 15.6x/26.7x/38.7x/40.4x at N=32/64/128/256 against the flat bound's
  137x/58.8x/21.3x/**5.6x**. It is a *function* because a constant is writable: a
  future test can reintroduce the flat form by typing the number, and it would
  fail on a correct solver at N=512. Orthonormality and reconstruction tolerances
  are left flat deliberately.
- 2026-09-26 **D23 confirmed and quantified: the `crossovers` block disagrees with
  the rows it sits beside, by 6.4-8.5%, one-signed, in all 12 cases.** I
  recomputed every resolved crossover from `dlra` / `static_moving_window` under
  a declared column. The block is below the rows at both Reynolds numbers, all
  three windows, both resolved ranks. It is **not** a column choice (the column
  moves the answer 0.5%) and **not** a convention (log vs linear interpolation
  moves it 7%) -- the block is 8.2% away, further than the whole interpolation
  spread. **Every bracket agrees exactly** (to 1e-9), so the qualitative
  statement survives and the point estimate does not. I could not reproduce
  D23's 0.52-0.64x; my factor is 0.915-0.936x, so the recorded magnitude should
  be 6-9%, not 36-48%. D22.5 is now executable:
  `test_the_crossover_block_agrees_with_the_rows_it_sits_beside` fails with all
  12 disagreements listed, and the block is regenerated from a single function
  `t_star_from_rows(rows, rows, column, log_interp)` with the column required
  and never defaulted.
- 2026-09-26 **The un-provenanced block had already reached a figure caption, via
  my own C1-3f fix.** `fig_divergence`'s caption quoted `t*` from the block, so
  the number D23 calls unusable was in a rendered label. I had read
  `CLAIMS.md`'s "fig_crossover reads the rows" as covering the figures and did
  not check the one I had just written. It now computes from the rows and states
  the **bracket** (convention-free) beside the point estimate, the column and
  the interpolation. Lesson: a prohibition about a *source* has to be checked
  against every consumer of that source, including the ones I wrote this cycle.
- 2026-09-26 **`CLAIMS.md` is binding and caught a barred claim I had just
  introduced.** C1-3c asked me to fix "the only rank that never loses is the
  dealiasing ceiling"; I replaced it with a version naming the formula and then
  added "at that rank the method is doing the work of the full-grid solver at
  over twice its cost" -- which CLAIMS.md prohibits verbatim and D30.2/D30.3
  refute on every part. The dealiased 64x64 grid carries ~1849 dof, so a rank-43
  subspace is not the full-grid solver. The real reason is that r=43's error is
  already at roundoff because the dynamics are effectively low-dimensional.
  **A lesson worth keeping: fixing a barred phrase by paraphrasing it is how a
  barred claim comes back wearing different words.**
- 2026-09-26 **D39.4: the per-method energy residual existed and was thrown
  away.** `run_projected` initialised `max_residual = 0.0` and never updated it,
  and the static-POD record path then overwrote the key with `None` -- so the
  artifact holding contribution 4 lacked the one *continuous* diagnostic that
  could say how the methods differ before one overflows, and the methods that
  overflow were exactly the ones it was discarded for. Now measured for every
  arm but the DMD baseline, and it discriminates: full grid 3.2e-6, DLRA
  1.7-2.3e-3, static POD 6.1-6.4e-2 -- about 28x worse, at a horizon where
  nothing has diverged. The **adaptive** arm is reported as `None` with a
  reason: a mid-step rank change re-derives the state in a new subspace and that
  energy jump is not in `projection_energy_increment`, so the residual would
  report the rank change as an integration error (4.8e+01 against 6e-2). The
  unsubtracted value is kept for diagnosis.
- 2026-09-26 **D27.1: the central error column was misnamed and mis-documented.**
  `relative_l2_oracle_mean` is `d_fluct/||ref||` with each field's OWN zonal mean
  removed; `error_columns` described it as "the zonal mean replaced by the
  reference's", which is a different quantity. Renamed to
  `relative_l2_fluct_over_full` rather than recomputed, because the numbers are
  established (D28.5/D29.2) and moving them to fit a label would be the wrong
  trade. The N=64 surface is re-running so the artifact carries the new key.
- 2026-09-26 **D18.6: built `run_rank_rule_energy.py` to make three inadmissible
  numbers admissible, and it found the mechanism.** The instantaneous rule and
  the windowed rule are scored on the same target using columns that EXCLUDE it,
  at four gaps. Two things had to be got right first: scoring the instantaneous
  rule on the target is tautological, and a one-check gap is uninformative
  because consecutive candidates 0.0025 apart are nearly parallel. The result:
  the windowed rule holds MORE rank (11-13 vs 1) and leaves 96-99.7% of the
  target's fluctuation energy outside, against 0.00-14.50% for the
  instantaneous rule. The oracle-window control sits at 75.38% and does not move
  with the gap, so placement is refuted as the explanation. **The mechanism is
  the centring**: the windowed spectrum removes the across-window mean, so its
  subspace is a *variation* subspace, which cannot represent the fields
  themselves.
- 2026-09-26 **D19.4: `peak_memory.json`'s interpretation was a literal with stale
  arithmetic.** It claimed the rank spread was "about 1.5x the noise floor" at
  N=64 and "about 6x" at N=128; measured, it is 2.7x (resolved) and 1.9x (NOT
  resolved), and it concluded "peak memory is rank-independent", which D19.4
  prohibits because the two grids disagree about whether a variation exists at
  all. The interpretation is now computed from the run's own rows and says so
  per grid, distinguishing an unresolved variation from a resolved one.
- 2026-09-26 **The N=128 crossover landed on committed code, and t* grows under
  refinement.** `crossover_N128.json`, `reproducible: true`, offset 0.125,
  `key_schema` present, single crossing at each resolved rank: t* = 0.939
  (r=16, bracket [0.5,1.0]) and 2.526 (r=32, bracket [2,3]); r=85 `never`.
  Against N=64's 0.649 and 1.482, that is 1.45x and 1.70x -- so t* is **not**
  grid-independent and the grid must be stated with it (D30.5). Scope is
  narrower than N=64's: one window (0.25) and horizons to t=3, which brackets
  both resolved values. `claims_registry.py` reads **33/35**; the two failures
  are r=43 absent (D17.2 predicts it yields at N=128, so it is re-running) and a
  3.8% disagreement with the reviewer's attested-archive run on r=32, inside the
  15-25% spread the two interpolation conventions produce -- so the
  convention-free statement is the bracket, which both runs agree on.
- 2026-09-26 **The T=8 rank-growth sweep refutes the premise of the "adaptive
  rank" bar without promoting the claim.** At 80x the original horizon, rank still
  grows 17 -> 43 at every cutoff, so growth is not a short-horizon artifact --
  which was the only reason the claim was barred. But the error is now 5.1e-1 at
  cutoff 1e-6 and 1.0e-1 at 1e-8/1e-10, against 1.7e-4 at T=0.1, and all three
  cutoffs have saturated at the same rank. So growth is real and is not buying
  accuracy: the honest reading is that the criterion demands more modes as the
  trajectory decorrelates and paying up to the cap still leaves O(0.1) error.
- 2026-09-26 **C6-1: the control refutes the plan I had announced.** I told the
  reviewer I would restructure the central-claim test so the refit genuinely
  happens. I did, added the frozen-DLRA arm as the control, and **the frozen arm
  survives identically** (both refreshing and frozen reach T with the same
  max|∇·u| = 2.287e-14). So at N=32/r=16 the difference from a raw-snapshot
  static basis is in how the subspace is **constructed** -- fluctuation basis,
  energy criterion, proper initialisation -- and *not* in whether it is refreshed.
  `check_every` gates the basis refresh, not only the rank, so the original
  docstring described a comparison the test did not make. The test now states the
  narrower claim and its assertions **record which way the control fell**, failing
  with a message if the two arms ever become distinguishable -- so it is sensitive
  to the direction that would widen it. Construction is pinned live; evolution is
  pinned from the T=8 artifact, where fixed-basis POD overflows at r >= 32. The
  open question is whether the refresh matters at *higher* rank, which is where
  the two could come apart.
- 2026-09-26 **C1-3b/c/d/f/g/h closed (R128 addendum).** C1-3f was the
  consequential one: `fig_divergence` plotted the suite window `t <= 0.1`, where
  the static baseline looks like it *wins*, with nothing saying so. Title and
  generated caption now both carry the window and the crossover horizon, with
  `t*` read from the artifact. C1-3h became a mechanism rather than a re-run:
  `make_figures.py` now **deletes every figure file the run did not write**, so a
  stale rendered claim is impossible; verified by suppressing one figure and
  watching both its files be removed, then restored byte-identically. C1-3b/c/d
  are now derived from the artifacts instead of literals. Sweeping the tree for
  the barred `dealiasing ceiling` phrasing found four *user-facing* strings the
  gate's report had not reached (a caption, two argparse help texts, a test
  docstring); all four now say "the largest alias-free rank for this grid".
  The five remaining occurrences are comments explaining the bar.

- 2026-09-26 **`run_kolmogorov.py` — the canonical suite driver — could not run
  at all.** `dlra_max_rank=args.dlra_max_rank or 2 * (N // 3) + 1` referenced a
  bare `N` that does not exist in `main()`, introduced at `394766b`, so the
  project's primary driver raised `NameError` on every invocation for many
  cycles. Nothing caught it because the committed artifacts predate the break: a
  driver that cannot run looks exactly like one nobody ran, which is D14.4's
  failure one layer down. Fixed, and `test_every_driver_runs` now invokes all
  seven drivers as subprocesses at minimal configurations (6.7 s) so the class
  cannot recur. Building it also confirmed four preconditions the drivers
  enforce: `PODGalerkin.fit` refuses a rank the window cannot supply,
  `run_regime_pilot.py` refuses a block time under the S2 specification's 2 time
  units, and two argument floors.
- 2026-09-26 **B1 closed, and it caught a real reproducibility failure.** Both
  artifacts re-run on the committed driver; all five in that family now record
  `reproducible: true` with `driver_matches_HEAD: true`, and
  `kolmogorov_re5000_N128.json` records the `ic_reference_N: 64` whose absence
  made its old commit false. **But the N=128 numbers did not reproduce:** the IC
  is bit-identical while `full.final_energy` moved 1.05% and
  `pod.max_relative_l2_vs_full` improved three orders of magnitude
  (6.72e-6 → 1.89e-9). The N=64 suite and the sweep reproduce bit-identically on
  every non-timing field. So my earlier claim that the full-spectrum derivative
  fix was "inert for every committed run" was **false for N=128**, where a field
  that is not k-symmetric exercises the old half-spectrum path. Corrected in the
  outbox; the N=128 numbers are now the better ones.
- 2026-09-26 **C4-1/D70: the two energy-residual keys renamed to what they
  measure** — `max_scaled_pde_energy_residual` (no projection term) and
  `max_scaled_projected_energy_residual` (the balance a projected integrator
  actually satisfies) — with an `energy_residual_semantics` block in every
  artifact giving both definitions, the scale, and which to quote. Writing the
  test found the trap in *code* as well as in the key: the projection's energy
  increment is accumulated only when `track_step_diagnostics` is on, so a run
  that forgets it files a silent zero under the projection-aware name.
- 2026-09-26 **C1-1 `fig_div_free` split into two panels**, with a guard that
  **raises** rather than compressing 292 decades silently. Two findings from
  doing it: the line labelled "target 10⁻¹⁴" had **every** method above it (they
  sit at 2–20×), so it is relabelled the roundoff floor; and a linear axis was
  the wrong choice despite being specified, because `pod_dmd_r32` at 1046× would
  render the other fifteen as sub-pixel slivers — a stated deviation.
- 2026-09-26 **C3-2's number is sharper than the claim.** The static error's
  spread across ranks {16, 32, 43} is **exactly 0.0%** at every horizon and both
  Reynolds numbers, against 16–18% across {2, 4, 8}. So above r=16 the extra
  modes buy nothing measurable at all, not merely little.
- 2026-09-26 **C2-3/P1: provenance is now structural.** `experiments/provenance.py`
  records the driver's own SHA-256 and whether it equals the committed file, and
  all seven drivers use it; `PROVENANCE.md` is generated from the artifacts the
  figure run just loaded, so there is no second copy to drift. Generating it
  immediately showed 6 of 11 artifacts had no `reproducible` field, which is
  what C2-3 fixed. `bench_memory.py` records `load_average_at_end` like
  `bench_cost.py` does.
- 2026-09-26 **C2-1: the reviewer's `PROVENANCE_ATTESTATION_N128.md` verifies**
  — all five determining files hash-match `588e51592bf0` as tabulated — **but I
  am superseding it.** An artifact produced from a `git archive` extraction
  records `git_commit: "unknown"` by construction, and the attestation exists to
  explain a value I can simply avoid. The N=128 surface is running in the
  worktree at a real commit instead, which both lands the artifact
  `claims_registry.py` wants and cross-checks the attested-archive method.

- 2026-09-25 **The `crossovers` block was wrong because of a direction bug, and
  it had been wrong for three review cycles because it had no test.** I detected
  only an *upward* crossing of `R = static/DLRA` through 1, but the static
  baseline overtaking is a **downward** crossing — `R` falls through 1 as the
  DLRA's error grows while the static error stays flat — so the function found
  nothing, ever, and "no crossover" was an artefact of the test's direction
  rather than a property of the data. Rewritten to scan every horizon, locate
  every sign change, classify each as `static_overtakes` or `dlra_retakes`,
  count them, and report the bracket as the convention-independent statement with
  both the log-log and linear interpolations beside it (they differ by 15–25%).
  `unresolved` (no crossing, either method may lead) and `never` (the DLRA is
  exact at every horizon) are now distinct, and the reason strings no longer
  claim a horizon the data does not contain. **Six test cases** cover the
  downward crossing, both no-crossing directions, the exact rank, a
  triple-crossing ratio, and the consistency of every reported ratio with the
  rows it came from.
  On the corrected surface: **6 of 18 resolved** per Reynolds number (r=16 and
  r=32 at all three windows), **r ≤ 8 unresolved**, **r=43 never**, and a
  **single** crossing everywhere — which confirms the reviewer's R48
  "crosses repeatedly" over-correction was an artefact of the buggy driver.
  `t*` is window-invariant to 0.3% over a 4× window change and
  Reynolds-invariant to 3–9% over a 5× change in Re.
- 2026-09-25 **My `t*` is about half the reviewer's, and the reason is the refit
  offset they identified in their own baseline.** Mine: r=16 → 0.649
  (log-log) / 0.740 (linear), r=32 → 1.482 / 1.741. Theirs: 1.26 and 2.44, from
  a driver whose trailing window *ended at* the evaluation time, so seven of
  nine horizons were scored in-sample and the static baseline looked worse than
  it is. Since they now apply the offset check to their own numbers (D15.6),
  this is a difference of baseline construction, not of data — and it is the
  third time this baseline has moved `t*` by a factor of two to four.
- 2026-09-25 **The Re=1000 column is my own run, not their `/tmp` numbers.** They
  offered to let me commit theirs; D14.4 forbids it, since an artifact must come
  from the code committed beside it. `--re` now takes a list and the artifact is
  keyed by Reynolds, with a `key_schema` block so the keys are derivable rather
  than needing a mapping table, and the refit offset recorded in `parameters`
  (it was claimed in a docstring and absent from the artifact — the reviewer's
  point, and the second time that distinction has been load-bearing).
- 2026-09-25 **The reviewer's correction to my rank-spread claim is right, and
  the normaliser explains the whole apparent disagreement.** I quoted "a 21×
  rank range buys 2%" from a single endpoint pair. The full row is
  `0.1009, 0.0996, 0.1160, 0.0994, 0.0994, 0.0994` at t=8 — r=8 is the worst.
  Their figures (16–41% at Re=5000, 43–46% at Re=1000 for t ≥ 3) are the *same
  data* normalised by `max`; mine normalised by `min`. **Both conventions are
  now recorded** in the artifact and the summary, and the figure labels which it
  plots. Spread by horizon, `(max−min)/min`, all ranks: **0.0% at t=0.1, 0.1% at
  t=0.25, 9.6% at t=0.5, 32% at t=1, 67% at t=2, 69% at t=3, then 17% by t=8**
  at Re=5000 — against **32%, 65%, 83%, 84%, 82%, 75%** at Re=1000. So the
  corrected claim is a mechanism with a *shape*: a static subspace cannot spend
  rank at short horizons, can from t ≈ 1, and how far it gets is
  **Reynolds-dependent** — at Re=1000 it sustains ~45% (by `max`) through
  t ≥ 3 where Re=5000 falls to 14% by t=8. That Reynolds dependence is new and
  is the reason the mechanism is the better spine than any single number.
- 2026-09-25 **Peak memory measured, and it is now an artifact
  (`peak_memory.json`) rather than a number in a message.** One fresh process per
  configuration, because peak RSS is a process high-water mark. **The reduced
  method does not save memory: it costs +2.4 MiB at N=64 and +4.2 MiB at N=128,
  6–10% above the full-grid step, at every rank and for both integrators.** That
  is several times the noise floor, so it is real, and it answers the reviewer's
  "does it at least save memory?" with a clean no.
  The variation *with rank* turned out to be barely resolvable, and I nearly
  published a boolean that flips: the spread over rank moved from 0.125 to
  0.398 MiB between two runs of the same code. So the driver now **measures its
  own noise floor** by repeating one configuration — 0.086–0.133 MiB — and
  states rank-independence relative to it instead of against a fixed threshold.
  Honest statement: peak memory is rank-independent to within a few tenths of a
  MiB, not exactly constant. BUG's spread is larger, in the direction its
  construction predicts (it holds augmented factors up to 4r, not a whole-field
  factorization).
- 2026-09-25 **The cost protocol now interleaves configurations, and that was
  not cosmetic.** A sequential re-run produced a 50.2% spread on one projected
  block and 4.3% on the next, which was enough to make the BUG rank-scaling flag
  read `true` at N=64 and `false` at N=128 — an effect appearing and vanishing
  with machine load, not with the method. Repeats are now the outer loop and
  configurations the inner one, so a slow patch of machine time inflates all of
  them together. The validation is direct: under 71% and 27% individual spreads
  the **interleaved BUG/projected ratios agreed to 4%** (0.184, 0.192), where the
  sequential protocol could not support the comparison at all. The node's load
  average is now recorded in the artifact, because the node also serves a
  language model and its load moves with someone else's work.

- 2026-09-25 **The windowed rank rule is implemented, measured, and it does not
  fix the problem — which settles the question the reviewer left open.** New
  criterion `window_energy` keeps the last `rank_window` candidates and takes the
  singular values of the matrix they form as columns, computed from a small
  `n x n` Gram so no large factorization is needed (O(n N²) against the four
  Θ(N³) ones already paid). Three tests pin it: the windowed spectrum equals a
  stacked SVD to 1e-8 (a Gram eigendecomposition returns *squared* singular
  values, and using the eigenvalues directly would leave the rank right while
  scaling the spectrum), the window slides rather than accumulates, and `reset`
  clears it so a later run cannot inherit a candidate.

  **Measured at T=8, N=64, A=0.5, against a reference window E_fluct 33.0:**

  | rule | ranks seen | E_fluct | % of reference |
  |---|---|---|---|
  | per-step energy (current) | 1 … 14 | 9.06 | 27.5% |
  | windowed, W=10 | 1 … 2 | 0.50 | 1.5% |
  | windowed, W=20 | 1 … 2 | 0.50 | 1.5% |
  | windowed, W=50 | 1 … 2 | 0.47 | 1.4% |

  So the windowed rule is **worse**, and never exceeds rank 2. The cause is
  definitional and it is the useful part: R26's 1 → 16 is a window **anchored at
  t=0**, and the pilot's own table shows a 0.4-time-unit window has r99 ≈ 2
  (W=0.25 → 2, W=0.5 → 2) while the full [0,8] window has 14. A rule keeping the
  last *n* candidates sees only the last *n·dt* time units, so it measures local
  complexity, which really is ~2 — and 2 is not enough, which is the 98% energy
  loss. **A causal method cannot read the cumulative rank without accumulating an
  unbounded subspace, which is exactly what the static and offline methods do.**
  I also tested a self-reinforcing explanation (the window fills with the
  method's own already-deficient states) by seeding the window with *reference*
  states: it made no difference (1.3% vs 1.5%), so that explanation is refuted
  and I am not reporting it.
- 2026-09-25 The pilots and the T=8 baselines artifact were regenerated so the
  metadata is actually *in* them (I had told the reviewer it was, and it was only
  in the drivers — corrected in the outbox). **Verified rather than assumed: the
  only value that moved in any pilot is `wall_seconds`**; every window rank,
  instantaneous rank, S2 drift and energy is bit-identical, and the N=64 pilot's
  new `sha256` is exactly the P0 fingerprint `ebcef128…` recorded by the
  canonical suite, so the pilot and the main driver produce the same IC. The
  fingerprints also settle the reviewer's point directly: N=64 is
  `ebcef128…` (E 22.2067) and N=128 is `30a40ea4…` (E 22.1886), so the two
  grids provably do not share an initial state.

- 2026-09-25 **R39 reproduced, and the disagreement is diagnosed: the DLRA half
  agrees to four decimals, my static baseline is 2–4× stronger than the
  reviewer's, and the crossover law does not survive a stronger baseline.**
  All 54 DLRA cells agree at 8 of 9 horizons to the fourth decimal (only
  `t=0.25` differs, at `r=43` only, and their row is non-monotone there so it is
  probably a sampling offset). Sweeping the static window over 0.25/0.5/1.0 with
  a 0.25 refit, my oracle-mean error is 0.09–0.16 against their 0.22–0.43. With
  my baseline the static method is *below* the DLRA at almost every (rank,
  horizon), so `t*` is undefined for all 18 (rank, window) pairs: the DLRA wins
  only at `t ≲ 1` for `r ≥ 16` and never for `r ≤ 8`. **The mechanism survives
  and the law does not:** the static error is flat in rank (r=2 → 0.101,
  r=43 → 0.099 at `t=8`, a 21× rank range buying 2%) while the DLRA's falls from
  0.599 to 1.6e-8, so "rank buys predictability time, not accuracy" is
  supported and `t* ≈ 0.050·r^1.12` is not, on my numbers. Put to the reviewer:
  run their window configuration, or keep the mechanism and drop the exponent. I
  will not write the exponent on numbers that do not support it.
- 2026-09-25 **A fourth harness bug, subtler than the other three: a refit
  scheduled at exactly an evaluation time is in-sample.** Seven of the nine
  horizons are multiples of the 0.25 refit interval, so each coincided with a
  refit whose trailing window contained it, and the baseline was partly scored on
  data it had seen. Refits are now offset by half an interval, so every
  evaluation is at least `interval/2` beyond anything any basis could have seen.
  This is the one that most plausibly explains part of the gap with the
  reviewer's baseline, and it is flagged to them.
- 2026-09-25 Reviewer's other items closed: `fig_cost` restored now the cost
  artifact landed, with an **"Expected but not generated"** section in
  `PROVENANCE.md` so a figure can never vanish silently again (their point 1, and
  it is right — an absence is not a record); `fig_rank_growth` → `fig_window_rank`
  (their point 3, the filename was the retired framing); the `Z(k)` panel dropped
  with the reason **read from the artifact** rather than hardcoded (enstrophy
  drifts 29% over `[13.33, 20]`, outside the S2 bar), `E(k)` kept with its window
  and its measured 3% drift printed on the figure (their point 2). The four small
  items — `framing_note` on the T=8 artifact, `rank_quantities` blocks,
  `initial_state.sha256` in the pilots, and the `SVDProjector` docstring that no
  longer claims the per-step rule tracks the sixteenfold growth.

- 2026-09-25 **The crossover surface driver, and three bugs in it found before
  it produced anything.** (1) The static rows were **off by one sample** — the
  rollout's state list starts at `t=0`, so indexing it with the horizon index
  compared the `t=0` state against the `t=0.1` reference and shifted every row.
  (2) The initial projector was fitted on `[0, window]`, i.e. partly in the
  **future**, so the baseline reproduced short-horizon states exactly and
  reported an error of zero at every rank. A trailing window that *ends at* an
  evaluation time contains that time; the only strictly causal initial basis is
  rank 1 on the IC. (3) When a window held fewer snapshots than the requested
  rank, the driver **skipped the refit entirely**, silently leaving the baseline
  on the rank-1 IC basis for the whole run — which made a short window look
  catastrophic (0.42) for the wrong reason. It now fits as many modes as the
  window supports and records the shortfall. All three were found by checking a
  small case against intuition, not by a test; they are the R24 failure mode in
  new code, and the honest surface is only now being produced for the first time.
- 2026-09-25 **The window is recorded as a swept axis, because it decides the
  baseline's error.** The reviewer's static rows and mine disagree, and the DLRA
  half of the surface reproduces their table to four decimals at every cell, so
  the disagreement is entirely in the static baseline. Neither of us stated the
  window, and a static baseline's accuracy is a property of its window rather
  than of POD (the R27 point). The driver now sweeps `--window` and reports
  `t*` as a function of (rank, window), with the number of refits whose window
  held fewer snapshots than the requested rank recorded — a window can only
  supply `W / snapshot_stride` modes, so a short window cannot be a rank-43
  baseline at all.

- 2026-09-25 **V6 done: midpoint BUG implemented from the primary text
  (arXiv:2402.08607 §§2–3) and verified three ways.** `solvers/bug.py`. The
  augmented step (K/L/S with `Ŝ(t0)=M̂S₀N̂ᵀ`), then the Galerkin step in bases
  augmented by `h·F(t₁ᐟ₂,Ŷ)V̂`, then SVD truncation; the Remark-1 3r variant
  too. Verified by: (a) a stationary state held to **machine precision** over
  25 steps (the `SelfConsistentForcing` test — every sub-equation has zero
  RHS there, so the factor algebra either holds to roundoff or not at all, and
  a transposed factor fails it while passing any loose tolerance); (b) a
  **structural** assertion that the only factorization in a step is of the
  ≤4r augmented S-matrix (`large_svd_calls == 0`), which is what a timing
  claim cannot establish on a shared node; (c) **measured second order, 1.98
  and 1.95**.
- 2026-09-25 Two bugs of mine, both silent, both caught by tests rather than by
  output. A **duplicate `Grid2D.lap` shadowed the real one with a flipped sign**
  (real `lap` returns −Δf, mine returned +Δf) and broke four operator tests at
  once. And my first BUG `step` re-factorized the state every step to apply the
  diffusion — which would have put Θ(N³) back into every step and defeated the
  port. The fix is exact, not approximate: the heat semigroup acts on the
  factors, `e^{ντΔ}Y = (e^{ντΔ_x}U)S(e^{ντΔ_y}V)ᵀ`, re-orthonormalised by QR at
  O(Nr²). Both axes of the factor semigroup act on **axis 0** (U's rows are x,
  V's rows are y) — my first version applied the y-semigroup to V's *columns*,
  which is a different operator.
- 2026-09-25 **Second order is conditional on the rank, and that is a finding.**
  Same code, same test: at rank 6 the observed order is 1.01/1.02/1.05, at
  rank 16 it is 1.98/1.95. The rank-6 truncation discards 18 of 24 augmented
  directions every step and that error is O(1) in dt, so it dominates the time
  error and masks the scheme's order. So an under-selecting rank rule does not
  merely lose accuracy — it loses the scheme's order too, which is the same
  conditioning F5's rank-1 result runs into.
- 2026-09-25 **R5q cost gate complete and it settles the reviewer's open
  question in the negative.** Pinned threads (recorded), warm-up discarded,
  2000-step regions, median of 7 with min/max spread, both accountings from the
  same runs. Full-step ratio 1.78/2.07 (N=64), 2.05/2.14 (N=128), 2.13/2.18
  (N=256) for r=2/64: it **saturates at ≈2.1 and never approaches parity**, so
  the near-parity-by-N=512 expectation does not exist and I declined the long
  high-N run. The LA column shows why: 0.60× a full step at N=64 rising to
  1.17× at N=256, so the SVD's relative weight grows with N while its absolute
  share stays under half. Cost is content-independent (0.94–1.03) and
  rank-independence is measured (r=64/r=2 = 1.165/1.046/1.022), with the N=64
  point outside 1.25 left visible rather than hidden by a wider bar.
- 2026-09-25 **The BUG port is ~5× slower per step than the projected
  integrator** (0.19–0.29× the projected time), despite factorizing only an 8×8
  matrix. The K/L/S right-hand sides are evaluated on *rank-augmented fields*
  (`K(t)V₀ᵀ`, `U₀L(t)ᵀ`, `ÛŜV̂ᵀ`) and each is a full-grid field evaluation with a
  spectral advection inside, several times per step. The rank-1 factorization
  saving is real and is swamped. So the **cost** argument for BUG does not
  survive contact with this engine; what survives is the Galerkin step in the
  augmented basis and, per Remark 3, the route to norm/energy/dissipation
  preservation. My calibration run had a 64.6% reference spread and produced a
  physically impossible ordering (projected r=16 faster than r=2), so it is
  discarded, not reported; a full-protocol re-measurement is running into
  `cost_bug_port.json`.

- 2026-09-25 `make_figures.py` rewritten, because the committed figures
  violated three binding rules rather than merely being stale. It titled a rank
  trace "Adaptive rank growth" when that trace is the dealiasing ceiling
  (D11.3 retires the claim); it labelled pointwise L2 as "error" when the P0
  metric order makes it trajectory divergence; and it plotted the singular
  values of the **rank-truncated reduced state** as a spectrum, which F2/R5
  bar ("never the rank-truncated reduced state"). The two offending figure
  files are deleted rather than left for the writer to pick up. The five new
  figures are: the windowed-rank premise figure at two grids with the
  amplitude rule's grid-scaling beside it, the full-grid state spectrum with
  the IC's rank-17 cliff, trajectory divergence paired with the KE series and
  labelled, max |∇·u| for every method including all F5 baselines, and the
  fluctuation E(k)/Z(k) over the dealiased range. A `PROVENANCE.md` records
  the artifact and commit behind every figure so a figure cannot outlive its
  numbers. The cost figure appears when the gate lands.

- 2026-09-25 **R29's grid-independence reproduced with project code, and it is
  the cleanest statement of the whole rank question.** Running the pilot at
  N=128 (dt scaled with dx per P0 item 3, snapshots every 0.02, fluctuations
  with the zonal mean removed) and putting it beside my N=64 column:

  | W | r99 N=64 | r99 N=128 | r999 64/128 | amp 1e-6 64/128 |
  |---|---|---|---|---|
  | 0.5 | 2 | 2 | 3 / 4 | 13 / 21 |
  | 1 | 4 | 4 | 6 / 6 | 22 / 39 |
  | 2 | 6 | 6 | 11 / 11 | 42 / 77 |
  | 4 | 11 | 10 | 22 / 18 | 85 / 163 |
  | 8 | **16** | **16** | 38 / 31 | **174 / 357** |

  My N=64 and N=128 r99 columns match R29's reported 2/2/2, 4/4/3, 6/6/6,
  11/10/10 exactly at every window they tabulate. The decisive comparison is
  the last row: **r99 is 16 on both grids while the amplitude rule asks 174 and
  357** — 4.0x and 4.2x their respective dealias ceilings (43 and 85). So the
  energy fraction measures something physical and grid-independent over
  [0, 8], and the amplitude rule's demand is a property of the discretisation,
  not the flow. That is the paper's claim, and it needs no resolution story.
- 2026-09-25 S2 at N=128 also fails everywhere it is measurable (T=4: 8.8%/23.5%;
  T=8: 2.2%/24.7%), so the no-stationary-window conclusion is not a
  resolution artefact either. Consistent at both grids and both amplitudes.

- 2026-09-25 **A mechanism I nearly got wrong, caught by measuring it.** The
  first F5 run at T=8 returned an adaptive rank of **1**, not R26's 16, and my
  first explanation was the secular zonal mean (94% of the energy by t=20, so
  a 99% fraction of the whole state is reached by the mean alone). Measuring it
  refuted that: at t=8 the zonal share is 73.7%, and the *instantaneous*
  fluctuation r99 is **2** — the same as the whole-state r99. The real
  difference is **instantaneous versus windowed rank**: each snapshot at t=8 is
  nearly 2-dimensional, while the 401 snapshots spanning [0, 8] occupy a
  14-dimensional subspace. So R26's 1→16 growth is a property of the subspace
  the trajectory *visits*, and a per-step rule that reads one state at a time
  cannot approach it — the energy criterion moves the selection off the
  dealiasing ceiling onto a physically meaningful ~2, but 2 is not 16 and no
  threshold on a single snapshot makes it so. Tracking the windowed rank needs
  a method that accumulates the visited subspace, which per-step truncation is
  not. I corrected the `SVDProjector` docstring, which had asserted the
  refuted explanation with numbers.
- 2026-09-25 F5 harness hardened: a baseline that goes non-finite is now a
  **recorded result**, not an abort. The first T=8 run died when
  `pod_early_r32` went non-finite at t=6.96, discarding every other method's
  numbers. Each run now reports `diverged`, the step and time it died at, the
  window it actually covered, and `accuracy_metrics_valid: false`, and the
  artifact lists `diverged_methods`. Aborting a comparison because one
  baseline failed is the R24 lesson recurring: "POD is worse" is not citable
  unless the divergence is itself reported.

- 2026-09-25 **S2 answered at the canonical amplitude, and the answer is no.**
  The full ladder to T=20 at A=0.5 gives drift between the last two thirds of
  `E_fluct` / `Z_fluct` of 31%/9% (T=3), 40%/11% (T=4), 30%/8% (T=6), 25%/15%
  (T=8), 29%/7% (T=12), 34%/28% (T=16), 3%/29% (T=20) against a bar of 10% on
  **both**. `qualifying_horizons` is empty: no affordable horizon is stationary
  in the S2 sense. Two supporting measurements from the same run: the zonal
  mean holds **93.8%** of the total energy at T=20 (E_total 939.7 against
  E_fluct 58.3, total energy up 42x from 22.2), and the rank ladder at A=0.5
  gives r99 = 1, 2, 2, 4, 7, 10, 11, 12, 14 at W = 0.1 … 8 while the amplitude
  rule asks 46, 99 and 230 modes at W = 2, 4, 8 against a ceiling of 43. So the
  regime is mean-dominated exactly as D11.2 states, now measured at our own
  amplitude, and the paper reports time-dependent fluctuation statistics with
  the zonal trajectory alongside rather than a plateau that does not exist.
- 2026-09-25 R27's F5 spec addition implemented: **three static-POD window
  placements** (early `[0, train]`, late `[T-train, T]`, and a moving/oracle
  window refitted on a trailing window of the reference) with the comparison
  made against the best of them, because "the cost of staticity" is a function
  of window placement rather than a property of POD. `PODDMD` now also learns
  from the reference's own snapshots, so it needs no extra PDE pass.
  **That change fixed a real defect in the baseline:** fitted on a separately
  re-run trajectory, POD-DMD diverged (E_fluct 8e11 at r=8, max div 4.2e-9);
  fitted consistently with the rollout it is stable at every rank (18.8/22.3/
  19.3 against a reference 19.1). A baseline that blows up because its training
  and rollout trajectories differ is not a baseline, it is a harness error —
  which is the R24 failure mode recurring in new code, caught by the smoke run
  rather than by a test.

- 2026-09-25 **R26's central measurement reproduced independently, and it
  matches their table value for value.** Running the S1–S3 pilot at R26's exact
  configuration (N=64, A=0.2, dt=5e-4, snapshots every 0.02, nested windows
  from t=0, fluctuations with the zonal mean removed), the modes needed to
  represent a window are

  | W | r99 | r999 | amp 1e-6 | amp 1e-10 |
  |---|---|---|---|---|
  | 0.1 | 1 | 2 | 5 | 5 |
  | 0.5 | 2 | 3 | 13 | 19 |
  | 1 | 4 | 6 | 22 | 35 |
  | 2 | 6 | 11 | 42 | 69 |
  | 4 | 11 | 22 | 85 | 144 |
  | 8 | **16** | 38 | **174** | 321 |

  against R26's 1/2, 2/3, 4/6, 6/11, 11/22, 16/38 and 4/12, 12/21, 21/41,
  41/84, 84/174 — the energy columns are identical and the amplitude column is
  within one. This is a cross-check of their headline number from my own code
  with the corrected derivative operators, not a restatement of it.
  **The consequence is now measured on our side too:** r99 grows 16x over the
  first eight time units, while the implemented amplitude rule asks for 42
  modes at W=2 and 174 at W=8 against a dealias ceiling of 43 — so from t=2 its
  rank is the grid's, exactly as R26 reports, and the 1e-10 cutoff reaches 321
  (7.5x the ceiling) by W=8.
- 2026-09-25 S2 measured rather than assumed, and the honest answer is that it
  is not available at the horizon the rank question lives on: with the spec's
  >= 2 time-unit blocks over the final third, T=3 passes (E drift 4.2%, Z drift
  8.5%) but T=4, 6 and 8 fail (11–16%), and no T <= 8 can have two blocks in its
  final third below T ~ 12. So S2 is *unmeasurable* for T < 12 by construction
  and *failing* for T in [4, 8] once it is measurable. Running the ladder to
  T=20 at the canonical amplitude to see whether any developed window passes.

- 2026-09-25 **A real defect in the first-derivative operators, found by the
  R5k full-band test — and proved inert for every committed result.** Applying
  a k-dependent multiplier to the rfft *half* spectrum and inverting with
  `irfftn` is a different operator: `irfftn` rebuilds the missing columns as
  `conj(F[k, N-j])` where a real field requires `conj(F[N-k, j])`. Measured on
  a full-band random field at N=32, `grid.grad`'s x-component differed from the
  independent full-2-D route by 7.5 against a field scale of 35.9. The
  nonlinear term is built from `velocity`/`grad` (`ns_psi.py:91-93`), so this
  was a defect in the dynamics, not only in a diagnostic. Fixed by forming the
  derivative from the **full** spectrum (`fft2` → real multiplier → `ifft2`);
  `grad` now matches the independent route to 0.0 relative error on both axes,
  and `max_divergence` had to be routed through the same operator (it had been
  differentiating with the old route, which is why it briefly reported
  div = 215 on a full-band field). Cost is ~2x on an O(N^2 log N) operation
  beside the Theta(N^3) factorization, so it is immaterial.
  **Impact on committed results: none, measured not assumed.** The canonical
  Re=5000 KE trajectory reproduces to 2.8e-14 over 200 steps and the IC energy
  to all 15 digits, because the affected content never enters: the IC is
  band-limited to |k|<=8, the 2/3 dealias mask keeps every step inside the band,
  and a projected rank-43 state has spectral mass 3.7e-17 outside it. Old and
  new velocity agree to 6e-15 on the IC and 1.1e-13 on a projected state. The
  test now asserts both halves: the operators match the independent route
  *everywhere* including the Nyquist planes, **and** the half-spectrum shortcut
  is demonstrably not the same operator, so nobody reintroduces it.
- 2026-09-25 R26's constructive consequence implemented: an **energy-based rank
  criterion** alongside the amplitude one. `rank_criterion="energy"` keeps the
  smallest r reaching `--energy-fraction` (default 0.99) of the energy, i.e. the
  r99 rule, which is the criterion that can track the state's 1→16 growth; the
  amplitude rule is kept as the default so nothing changes silently, and every
  artifact records which criterion produced its rank trace. Both are pinned by
  a test against brute force, including that they provably differ (12 vs 2 on
  the same spectrum).
- 2026-09-25 R27's blocking defect fixed: `benchmark_summary.json` was still
  built from `c5fc827` and carried the void POD column (1.07759) and the old
  V1 step-0 value (0.315248). It is now **generated** by
  `experiments/make_summary.py` from the artifacts, which also refuses to emit
  a summary whose cases disagree about the IC fingerprint or whose POD IC
  projection is not at roundoff. Two of my own generator bugs surfaced and were
  fixed: it checked the DLRA block for a POD-only field, and it read
  `parameters.re`/`N` from the long-run artifact, which does not record them —
  the old hand-assembled summary had asserted values the artifact never
  contained. The generator now reports them as null and says so, and
  `run_long_time.py` is being fixed to record them.
- 2026-09-25 R27's second point fixed: `dlra_max_rank` defaulted to 48, which
  at N=128 capped the rank trace while the dealiased band holds 85 modes — a
  driver artifact plotted as adaptation. `--dlra-max-rank 0` (the new default)
  resolves to the grid's own ceiling `2*floor(N/3)+1`, and the ceiling is
  recorded in every artifact next to the cap.
- 2026-09-25 R27's instruction adopted: provenance beats fingerprint. The stale
  summary was found by comparing fields against the artifacts, not by searching
  for a remembered string, and the summary now carries each member's
  `git_commit` plus an explicit statement of the rank mismatch (POD r=16 vs
  DLRA r=43, not rank-matched) and of the Re-independent-error red flag (the
  DLRA trajectory divergence is 9.8e-5 / 1.00e-4 / 1.01e-4 at the three Re, so
  at T=0.1 it measures the setup and no Re-dependence may be claimed).

- 2026-09-25 Closing standing CHECKLIST items that were open on my side, in
  `experiments/test_engine.py`. **R5 negative control**: `Grid2D.max_divergence`
  is now exposed so a test can feed the diagnostic a velocity that is *known*
  not to be divergence-free — an injected `grad(phi)` must report ~1, and a
  divergence-free perturbation of the same size must not trip it. Without this,
  "exact by representation" would be a vacuous test that passes for any
  implementation. **R5q cost model, two assertions as the checklist words it**:
  `test_full_field_svd_is_rank_independent` (the factorization returns the full
  N-value spectrum for *any* rank, which is the structural fact behind the
  measured rank-independence, and fails when the V6 per-stage port lands) and
  `test_svd_call_count_per_step` (exactly 4 whole-field factorizations per
  step, so a 4 → 1 change is a failing test). The `SVDProjector` docstring now
  states the cost model as today's behaviour and that V6 must invert it.
  **R5k operator tests on a full-band field** against an independent full 2-D
  `numpy.fft.fft2` route covering `lap`, `vorticity`, `velocity`, `grad` and
  divergence. **R5l**: the rank rule is checked against brute force
  `#{sigma_i > cutoff*sigma_1}` clipped to the bounds, including the degenerate
  spectra; `PODGalerkin.project` is checked for idempotence and
  least-squares agreement on fields with a **nonzero mean**, which is the case
  the old trailing `out - mean(out)` defect hid in. **R5 reduced-path order**:
  Taylor–Green is exactly rank 1, so a rank-1 projector is lossless and the
  reduced step's second-order convergence in dt is measurable (halving dt must
  cut the error by ~4).
- 2026-09-25 Added `PODDMD`, the dynamic data-driven baseline F5 asks for
  (closes the "POD-DMD" half of F5's bar). One fitted linear operator on a POD
  basis, advanced exactly one solver step per application so it shares the dt
  policy. The normal equations are accumulated **online** (O(r^2) memory, not
  O(n_snapshots·r)), which matters because a long training segment is tens of
  thousands of steps. Tested against the only case whose answer is known: a
  synthetic linear system, where the least-squares fit must be exact — that
  catches a transposed normal equation or a stride error, the same class as the
  R24 reshape.
- 2026-09-25 Added isotropic `E(k)`/`Z(k)` as `Grid2D.isotropic_spectra`, with
  the shell sums required to reproduce `ke()` and `enstrophy()` exactly (a test
  asserts it, so the spectra cannot silently lose or invent energy). This is
  P0 metric 3 and the E(k)/Z(k) half of F2, and it is computed on
  `psi' = psi - x-avg(psi)` per S1. `zonal_mean`/`fluctuations` moved into
  `solvers/spectral.py` because they are operations on the state, not on a
  driver, and three drivers now share one definition.
- 2026-09-25 Wrote the two remaining drivers, both blocked on measurement
  rather than on code. `run_regime_pilot.py` implements S1–S3 mechanically:
  fluctuation E and Z, block means of >= 2 time units over the final third,
  drift between the last two thirds, the bar |drift| <= 10% on both, and the
  horizon reported as a function of T so T is chosen from a measurement. It also
  accumulates windowed E(k)/Z(k). `run_baselines.py` implements F5's bar:
  full grid, static POD and POD-DMD at r = 16/32/42 **and at the rank adaptivity
  actually reached**, plus fixed-rank DLRA to separate rank from adaptivity,
  all from one hash-verified IC, judged on time-averaged fluctuation KE/enstrophy
  and spectra with pointwise L2 last and labelled. It pre-checks the offline
  window against the largest requested rank and fails before the long run
  instead of inside it.

- 2026-09-25 Regenerated **every** committed result artifact from commit
  `78607f3`, so the POD column is no longer void anywhere. Re-suite
  (N=64, dt=5e-4, T=0.1, canonical args): all three Re bit-identical IC
  (KE 22.206703312933374, rank 17, sha `ebcef128...`), max |∇·u| 2.3–2.9e-14,
  POD IC projection 1.7–1.9e-17, DLRA rank 17→43. Corrected static-POD max
  rel L2 is 1.08e-6 / 1.13e-8 / 1.00e-8 at Re=100/1000/5000 versus DLRA
  9.8e-5 / 1.00e-4 / 1.01e-4 — the static baseline is *more* accurate at
  T=0.1 (in-sample window, effective rank 3), which is the honest result.
  Taylor–Green, long T=1, and the rank sweep regenerated too; the sweep now
  records `run_case`'s own full parameter block instead of a hand-copied subset
  (P0 item 5). Deleted `benchmark_summary_N64.json`, an orphan from an
  accidental `bench.py` default run whose parameters contradict the canonical
  suite.
- 2026-09-25 **P0 item 3 was being violated by the two-grid comparison and is
  now fixed.** With `default_rng(seed).normal(size=(N,N))`, changing `N`
  redraws the perturbation, so N=128 was a *different realization* of the same
  band (KE 22.1886 vs 22.2067), not the same physical problem at two
  resolutions. Added `make_initial_state(reference_N=...)`: draw, filter and
  normalize on a reference grid, then transfer the spectrum to the target grid
  with the explicit (N_target/N_source)² factor that unnormalized rfft
  coefficients require. N=128 with `reference_N=64` now reproduces the N=64 IC
  exactly — KE 22.206703313 both, |u| rms equal to 9 digits, normalized spectra
  agreeing to 9e-18, while the redrawn fine IC still differs. The default is
  unchanged, so the verified N=64 fingerprint is untouched. The N=128 artifact
  was regenerated under the full protocol: dt 2.5e-4 (scaled with dx), T=0.1
  held, all method settings equal; reference KE agrees with N=64 to 6 digits
  (22.671552 vs 22.671553).
- 2026-09-25 Added measured two-accounting cost instrumentation and the R5q
  gate driver `experiments/bench_cost.py`. `SVDProjector` now accumulates
  `svd_seconds`/`svd_calls`, so "linear algebra alone" is measured rather than
  estimated, and both accountings now appear in the artifacts. The driver pins
  and *records* thread counts, discards a warm-up, takes the median of 7
  repeats over a 2000-step region with min/max spread, holds the rank fixed so
  cost is not confounded with adaptation, and reports the rank-independence
  ratio r=64/r=2 at each N. Smoke test at N=64: reference 1.57 ms/step (0.2%
  spread), reduced full step 1.65–2.12× the reference, linear algebra
  0.85–0.94×, rank-independence within 1.25. No per-step speedup is claimed
  anywhere (D11.1).
- 2026-09-25 Noted for the record: at N=128 the DLRA reaches the *configured*
  `max_rank=48`, not the dealias ceiling 85, so that run is rank-limited by
  configuration. Any matched-rank comparison at N=128 needs `max_rank >= 85`.

- 2026-09-25 **V2/V4 closed by root cause: `PODGalerkin.fit` never computed
  POD.** `X = arr.reshape(N*N, n)` on a snapshot-major `(n,N,N)` array fills in
  C order, so `X[p,k] = arr.flatten()[n*p+k]` — snapshots are interleaved, not
  stacked. The stored "mean" averaged 20 consecutive pixels of one snapshot and
  the SVD factorised scrambled data. Proof: on three known fields the fitted
  mean was off by 24.3, and at full rank 3 *none* of its own training
  snapshots was reconstructed (errors 19–36, `<f−Pf,Pf> = −1549`).
  Fixed to `arr.reshape(arr.shape[0], -1).T`. The old test passed *because* it
  asserted `norm(projected − snapshot) > 1e-8` on 2 snapshots at rank 1, where
  a correct fit is exact — it was asserting the bug. Replaced with a
  fit-reproduces-its-own-input test plus an independent reconstruction of the
  snapshot matrix. After the fix, IC projection rel L2 = **1.8e-17**, POD
  `initial_energy` = **22.206703312933374** (bit-identical to full grid; was
  249.75 = 11.25×), POD max rel L2 vs full **1.0e-8** over 200 steps (was
  ≈1.08), stable. All previously committed POD numbers are void.
  P0 compliance: the offline fit now includes `t=0` so the static baseline
  starts from the same bit-identical IC (`pod.initial_projection_relative_l2`).
  **Honest consequence:** at T=0.1 the corrected static baseline (1.0e-8) is
  *more* accurate than adaptive DLRA (1.0e-4), because the training window is
  a prefix of the evaluated trajectory and is effectively rank 3. The paper
  cannot claim DLRA beats static POD on accuracy at this horizon; per R24 this
  is downstream of the regime decision (D11.2) and the S3 pilot.
- 2026-09-25 R20 rank cap: `fit` now **raises** when `requested_rank` exceeds
  the number of snapshot directions instead of silently clamping (a clamped
  "rank r" run would flatter the proposed method). `effective_rank()` is
  therefore always the requested rank; the artifact records both.
- 2026-09-25 R25: `DLRA.initialize()` now fully resets learned state
  (projector rank back to configured, retained SVD candidates, statistics,
  step counter, rank/spectrum histories). Previously a reused `DLRA` inherited
  the prior run's adapted rank and adaptation schedule and could adapt on a
  stale stage candidate. Chose the reset over documenting single-use.
- 2026-09-25 R5l mean contract: snapshots are centered into the
  zero-spatial-mean class *before* the SVD, so `mean` and every basis column are
  mean-free and `project` is the exact L²-orthogonal projection onto
  `span(mean) + span(basis)` — idempotent, with the residual orthogonal to
  both. Removed the trailing `out − mean(out)` that shifted the output out of
  the subspace. Numerically inert for the real runs (snapshot means ~1e-18):
  IC fingerprint, full-grid run and DLRA are bit-identical; the POD online
  trajectory moves by 1e-12 (roundoff amplified through 200 projected steps).
- 2026-09-25 **R5k's Nyquist fix is refuted for this engine, with
  measurements.** Zeroing the Nyquist multiplier in first derivatives (to avoid
  the self-conjugate aliasing) deletes `v`'s Nyquist row while keeping `u`'s,
  so the real velocity field stops being divergence-free: spectral div u = 8.0
  at N=16 for a Nyquist+smooth field, versus 5.5e-15 with the true wavenumbers.
  The pre-existing convention is the correct one — numpy's `irfftn` inverts
  the full x-axis as a complex spectrum, preserving 2D Hermitian symmetry, so
  no coefficient is dropped and cancellation holds mode by mode. A real-space
  central difference *cannot* check this (the stencil aliases the Nyquist mode
  to zero), which is why an FD cross-check is the wrong instrument here. SVD
  projections do populate the Nyquist row, so the change would have silently
  broken I1 everywhere. Reverted, documented in `Grid2D.__init__`, and pinned
  by a test that guards the invariant.
- 2026-09-25 D11.5: renamed `tolerance` → `relative_amplitude_cutoff`
  throughout (solver, all five drivers, tests) — a rename only, no behaviour
  change. Docstring and CLI help now state that it is a test on singular
  *values* (amplitudes), not an accuracy criterion: 1e-6 is an energy ratio of
  1e-12. The IC fingerprint's separate numerical-rank tolerance is documented
  as distinct.
- 2026-09-25 F2 infrastructure: `normalized_spectrum` no longer caps at 32; the
  default records the **full** state spectrum over all resolved modes (64 values
  at N=64) at every checkpoint, with `--spectrum-count` to truncate. The IC's
  clean rank-17 cliff reproduces (σ₁₇/σ₁ = 2.46e-4, σ₁₈/σ₁ = 8.23e-17). Per
  D11.4 the developed-state figure must be computed on fluctuations
  (ψ′ = ψ − x-avg ψ), since the full-state ratio is contaminated by the growing
  zonal mean.
- 2026-09-25 `make_initial_state`: documented that `cutoff` is a *box*
  half-width (|k_x| ≤ c **and** |k_y| ≤ c), so the max radial wavenumber is
  `floor(c√2)` (2, 5, 11 for c = 2, 4, 8) and the rank is exactly `2c+1`; both
  pinned by a test. V1 verified: IC KE 22.206703312933374, rank 17, DLRA initial
  energy to roundoff, rank 17→43, max rel L2 1.01e-4, max |∇·u| ≤ 2.5e-14.

- 2026-09-25 Final coder audit pass: 13 tests pass; regenerated canonical
  N=64 Re=100/1000/5000 table has full/DLRA max divergence 2.3--2.7e-14,
  DLRA max relative L2 0.315--0.317, and rank 2→42; the N=64 T=1 Re=5000
  check has rank 2→43 and max relative L2 0.324.  PDF/PNG figures and strict
  JSON provenance are committed for the writer.
- 2026-09-25 Added `experiments/make_figures.py` and generated PDF/PNG
  rank/error, singular-value, and cost figures from the committed JSON for
  the writer; figures explicitly show the SVD overhead and POD limitations.
- 2026-09-25 Synchronized with `origin/main` after reviewer R4 and
  rechecked the committed tree: 13 tests pass and all nine result JSON files
  are strict-finite with provenance.  The remaining external dependency is
  theoretical-research's D3 wording, not a missing coder artifact.
- 2026-09-25 Hardened the engine after an independent numerics audit:
  rank adaptation now inspects the retained pre-projection nonlinear
  candidate; inputs are 2/3-filtered before products; signed rFFT Nyquist
  wavenumbers, zero-mean frozen forcing, strict finite JSON, scale-aware
  stability/CFL flags, and explicit projection-work energy diagnostics were
  added.  Thirteen tests pass.  The sustained Re=5000, N=64, T=1 run remains
  finite for full and DLRA (rank 2->43, max relative L2 0.324), while the
  short three-Re comparison honestly records POD accuracy/residual limits.
- 2026-09-25 Added and ran `experiments/run_rank_growth_sweep.py` at
  Re=5000, N=64, dt=5e-4, T=0.1.  Relative thresholds 1e-6, 1e-8,
  and 1e-10 yield maximum ranks 2, 3, and 15 respectively (all runs
  finite), making the singular-value trigger and its cost/error tradeoff
  explicit in `state/coder/results/rank_growth_sweep.json`.
- 2026-09-25 Ran the committed N=64 suite (dt=5e-4, T=0.1,
  A_force=0.5, perturbation velocity RMS=1, POD rank 16, adaptive DLRA
  initial/min rank 2, max 48, relative singular tolerance 1e-10).  All three
  Re cases are finite and structurally divergence-free: full-grid max
  |div u|=2.4--2.5e-14, DLRA=1.9--2.1e-14; DLRA max relative L2 error is
  0.315--0.316, with rank growing from 2 to 14--15.  Static POD is finite but
  less accurate (max relative L2=1.10--1.25) and has a large forcing-aware
  residual at Re=5000; DLRA is slower than full-grid/POD because it pays for
  explicit SVD projections.  Results and provenance are in
  `state/coder/results/benchmark_summary.json` and the per-case JSON files.
- 2026-09-25 Added reproducible Taylor--Green and Kolmogorov drivers, a
  three-Reynolds benchmark wrapper, JSON provenance, singular-value snapshots,
  energy/enstrophy histories, rank traces, and finite-value stability flags.
  Corrected the stream-function constant-gauge handling so SVD rank preservation
  is not destroyed by a post-projection mean subtraction.  The test suite now
  passes 10 tests, including restart, rank-growth, continuous energy-balance,
  and SP diffusion-rank checks.  Final Re=100/1000/5000 result files remain to
  be regenerated from the committed driver.
- 2026-09-25 Implemented the initial stream-function engine: corrected the
  rFFT axis/wavenumber and Parseval conventions, exact vorticity sign, exact
  diffusion semigroup, dealiased midpoint SP split, periodic Kolmogorov source,
  manufactured self-consistent forcing, adaptive SVD DLRA, and static POD.
  `experiments/test_engine.py` passes all 8 tests, including divergence,
  exact Taylor–Green decay, fixed-point, energy terms, time order, rank, and
  POD checks. Benchmark drivers and measured Re results are still pending.
- 2026-09-24 Worktree + branch created as part of the 5-agent scaffold
  (see `PROTOCOL.md`).
