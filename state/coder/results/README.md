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
rank rule should be re-engineered to *accumulate a visited subspace* — to retain
modes the trajectory has passed through — instead of reporting the rank the
current window needs. The answer from measurement is that accumulating makes it
**much worse**, and `state/coder/results/rank_rule_energy.json` now carries the
measurement (D18.6 made the earlier, message-only numbers inadmissible).

The driver scores each rule on the same target field, using columns that
**exclude** that target, at four gaps between the rule's columns and the target.
Both details are load-bearing and both were found by getting them wrong first:
scoring the instantaneous rule on the target is tautological — it retains the
field it is shown — and a gap of one check is uninformative, because consecutive
candidates `0.0025` apart are nearly parallel, so rank 1 spans the next one and
the rule looks perfect because the flow is slow rather than because the rule is
good.

Fraction of the target's fluctuation energy left outside the retained subspace,
at the amplitude cutoff `1e-10` the DLRA actually applies:

| gap (time units) | instantaneous | windowed | windowed, best window by hindsight |
|---|---|---|---|
| 0.0025 | r=1, **0.00%** | r=12, 97.24% | r=11, 75.38% |
| 0.05 | r=1, 0.23% | r=13, 97.99% | r=11, 75.38% |
| 0.25 | r=1, 2.93% | r=11, 99.68% | r=11, 75.38% |
| 1.00 | r=1, 14.50% | r=13, 95.92% | r=11, 75.38% |

**The mechanism is the centring, and it is definitional rather than a tuning
failure.** The project's windowed spectrum (`run_regime_pilot.window_rank_table`)
removes the across-window mean before the SVD, so the windowed rule retains a
*variation* subspace — the directions along which the window's fields differ —
and a variation subspace cannot represent the fields themselves. That is why the
windowed rule holds **more** rank (11–13 against 1) and is nonetheless two orders
of magnitude worse: the extra modes are extra *variations*, not extra field. The
instantaneous rule has no window to centre, so its subspace contains the field.

**The window placement is refuted as the explanation** — which D18.3 recorded as
refuted, and which this artifact now supports. Handed the best window available,
chosen with hindsight, the windowed rule still leaves **75.38%** outside, and that
number does not move with the gap at all, because it is limited by what a
variation subspace can span rather than by where the window sits.

**What is reported instead is the distinction**, which is a finding: the
instantaneous per-step rank and the window rank are different quantities, they
answer different questions, and conflating them is what made "adaptive rank"
look like a grid artifact. The window rank grows `1 -> 16` over `[0, 8]` and is
grid-independent; the per-step amplitude rule's request tracks the grid. Both are
recorded, and the `rank_quantities` block says which is which.
## What separates a propagated static basis from the re-derived one (C6)

`state/coder/results/static_basis_construction_N32.json`, at `N=32`, rank 16,
`dt=0.002`, `T=6.0`:

| arm | basis | stepper | outcome |
|---|---|---|---|
| 1 | raw window snapshots | static | **overflows** at `t = 5.388` |
| 2 | zonal-mean-removed snapshots | static | **overflows** at `t = 4.438` |
| 3 | re-derived from the current field each step | rank fixed | reaches `T`, 0 rebuilds |
| 4 | re-derived from the current field each step | rank adapting | reaches `T`, 600 rebuilds |

**The contrast is propagated versus re-derived**, and that is the claim the paper
makes. Two things this rules out, both of which had been written down as
conclusions before the arms were run:

- **The zonal mean is not the mechanism.** Arm 2 removes it and *still* overflows,
  sooner than the raw basis. Removing the mean does not rescue a propagated basis.
- **The rank rule is not what keeps the runs alive.** Arms 3 and 4 agree exactly,
  and the reason is structural rather than coincidental: `SVDProjector.project`
  recomputes `self._svd(field)` on **every** call, so the per-step projection is a
  fresh rank-`r` truncation of whatever field it is handed. `check_every` gates
  the **rank**, not the projection. A large `check_every` freezes the rank while
  the subspace keeps tracking the state, because tracking it is what the
  projection does.

**The overflow time is not monotone in rank, and which basis survives flips.** Raw
survives at `r=18`; fluctuations survive at `r=17` -- the two swap. Overflow times
run 5.478, 3.922, 5.388, 2.952 for the raw basis at ranks 14-17. So rank is *not*
a threshold here, and an artifact reporting only "the rank at which it fails"
would mislead: the rank at which one basis fails is not the rank at which the
other does. All six seed/basis combinations of the propagated baselines overflow
across seeds `20260925`, `7`, `991`, so the failure is not one initial condition.

**A correction worth recording.** An earlier version of this section, and of the
test that backs it, concluded the difference was the basis **construction**
(fluctuation basis, energy criterion, proper initialisation) rather than
evolution. That was inferred from a "frozen DLRA" control arm which turned out
not to control what it looked like: with `check_every=10**9` the rank is fixed
but the projection still re-derives per step, so the control was a second
instance of the same arm. The narrower claim the artifact actually earns is the
one above.

The files are intentionally compact JSON rather than raw field snapshots.

## The zonal share and the fluctuation share are complements, not two quantities

`zonal_energy_fraction` is `(energy_history - fluctuation_energy_history) /
energy_history` — the share of the kinetic energy in the **zonal** (x-independent)
mode. That definition was ambiguous until 2026-09-26, when the reviewer formed
the *other* ratio from the same two series, got ≈82%, and read the recorded
≈20% as a different quantity "a factor of 4 apart with the Re trend inverted".
Neither is true. The two are exact complements, because

    E(psi) = E(zonal) + E(psi')    exactly,

since the Parseval inner product of `grad(psi_zonal)` with `grad(psi')` vanishes —
the zonal mode occupies only kx=0 and `psi'` occupies only kx≠0. Measured, not
argued: on a random field at N=16/32/64 the defect is 1.5e-16, 0, 0 relative;
on the runs the two shares sum to 100.0000% at the final step at every Re.

So ≈20% and ≈82% are the *same* measurement with the halves named in opposite
order, and the Re trend is the same trend seen from the other side:

| | Re=100 | Re=1000 | Re=5000 | N=128 |
|---|---|---|---|---|
| zonal share of total E (recorded) | 20.089% | 18.533% | 18.398% | 17.283% |
| fluctuation share of total E (complement) | 79.911% | 81.467% | 81.602% | 82.717% |

**Three things were added because of this**, all in `run_kolmogorov.py` and all in
every artifact:

- `zonal_fraction_semantics` — the formula, the numerator, the denominator and
  the index as separate keys, so the definition is read rather than inferred;
- `zonal_energy_fraction_fluctuation` — the complement, recorded so nobody takes
  it by hand;
- `zonal_energy_fraction_components` — the raw total/fluctuation/zonal energies
  at each index, so the stored share can be recomputed and *checked* against
  the stored definition rather than trusted.

Asserted by `test_the_zonal_share_and_the_fluctuation_share_are_exact_complements`
and `test_the_energy_is_additive_under_the_zonal_split`. Four suite cases were
re-run natively so the keys come from the driver that records them; all four came
back bit-identical on every physical value, which is also the check that the
configuration was reproduced.

**What the share is, and is not, good for.** It *is* a Re-dependent observable,
and it *decreases* with Re at fixed N and T: 20.089% → 18.533% → 18.398% across
50× in Re, an 8.4% change. But it is weak, and two of its dependencies are larger
than the Re effect, so it cannot carry a Re-dependent claim alone:

- **horizon**: 16.21% at t=0 → 18.40% at T=0.1 → **32.16%** at T=1.0
  (`run_long_time.py`, A=0.2), i.e. it nearly doubles over the first unit of time
  while Re is fixed;
- **grid**: 18.398% at N=64 vs 17.283% at N=128 at the same Re — a 6.1% change,
  comparable to the whole Re range.

The enstrophy share is flat in Re over the same range, so this is specific to the
energy, not to the split.

## C8-2: the legacy runs reproduce bit-for-bit

Four artifacts named a commit but recorded no `reproducible`, so nothing had ever
checked the driver that produced them. All four were re-run with the parameters
each one's own `parameters` block records, and all four came back **identical in
every physical value** — the equality is the check:

| artifact | physical values | what differs |
|---|---|---|
| `regime_pilot_re5000_A0p2.json` | identical | nothing (byte-identical) |
| `regime_pilot_re5000_N128_A0p2.json` | identical | nothing (byte-identical) |
| `baselines_re5000_N64_T8.json` | identical | nothing (byte-identical) |
| `regime_pilot_re5000_A0p5.json` | identical | provenance + 3 `wall_seconds` (≤1.8% timing noise) |

Not one energy, enstrophy, divergence, rank, singular value or spectrum entry
moved in any of the four. The only non-determinism anywhere is wall-clock time,
which is the one quantity that is not supposed to be reproducible.

The first attempt at this re-run *did* change a number, and the reason is worth
recording: the shell script put `--dt` in a shared argument list *and* per case,
and argparse takes the last occurrence, so the N=128 case ran at twice its
recorded `dt` and with a freshly-generated initial condition instead of the
`--ic-reference-N 64` one — a different case written under the same filename. It
was caught by the fingerprint failing (17.485% against a recorded 17.283%), the
committed artifact was restored, the driver was committed so
`driver_matches_HEAD` could be true, and the re-run then reproduced 17.283% exactly.
**A fingerprint that fails is doing its job; the bug was in the invocation, not
in the driver.**

## The memory "noise floor" was one sample, and three verdicts were resting on it

`peak_memory.json` reported a "run-to-run noise floor" of 0.0039 MiB, and four
verdicts in its `interpretation` rested on it at a threshold of
`spread_over_rank > 2 x floor`. Two defects, one on top of the other.

**The floor was a single sample.** `bench_memory.py` re-measured one configuration
twice and took `max()` over a dict **keyed by configuration** — so the repeats
overwrote each other and only the last survived, whatever the repeat count. The
artifact read as though it carried an estimate. The *same quantity*, re-measured
on this problem, has been observed at:

| measurement | noise floor (MiB) |
|---|---|
| `dfd1a0b` | 0.1328 |
| `896b3bf` | 0.0664 |
| `dcc4a64` (what the registry row is pinned at) | 0.0977 |
| `e59e790` (what the artifact carried) | **0.0039** |

**A factor of 34**, and the value the artifact shipped was the *smallest* of the
four — the one that makes every verdict come out resolved.

**Fixed at the source, not annotated.** The repeats are now a **list** (a
distribution stored in a dict keyed by the thing it varies over is a distribution
of size one), the default is 8 repeats, the artifact records
`noise_floor_samples_mib` with min/median/max and the sample values, and the
verdicts are taken against the **maximum** — the conservative side, since a
larger floor can only turn "varies with rank" into "not established", never the
reverse.

**What that did to the verdicts.** With 8 samples the floor is **0.324 MiB**
(0.0781 to 0.3242, factor 4.2 within the run alone):

| | spread over rank | margin vs threshold 2x | old verdict | new verdict |
|---|---|---|---|---|
| N=64, projected | 0.29 MiB | **0.44x** | RESOLVED | **NOT resolved** |
| N=64, BUG | 0.52 MiB | **0.80x** | RESOLVED | **NOT resolved** |
| N=128, projected | 0.50 MiB | **0.77x** | RESOLVED | **NOT resolved** |
| N=128, BUG | 1.77 MiB | 2.73x | RESOLVED | RESOLVED |

**So the old sentence — "the variation with rank is RESOLVED at every grid, so
'flat in rank' would assert the opposite of the measurement" — was false.** Three
of the four pairs are not resolved. The honest reading is the *opposite* of the
old one and is stated in the new artifact: no variation with rank is established
for the projected integrator at either grid, and the spread is *consistent with
zero without demonstrating it*. That is not "flat in rank" either — and
`test_the_memory_noise_floor_is_a_distribution_and_not_one_sample` is what keeps
it from drifting back.

The robust part of D19.4 is untouched: **the reduced integrator does not save
memory — it costs more than the full-grid step at both grids**, and that is
several times any of the four noise floors ever measured.

The registry row `mem_noise_floor_mib` is pinned at 0.0977 MiB, one of the four
single-sample values above, and cannot be satisfied by any correct measurement of
this quantity. It needs re-pinning against the distribution, or replacing by a
claim about the distribution — see the message to the reviewer.

## Driver drift: which artifacts are actually in question

`provenance.py` sets `driver_matches_HEAD` by comparing the driver on disk with
the one in the recorded `git_commit`, and `reproducible` follows it. That is the
right check and it is unforgiving on purpose. But it currently conflates two very
different situations:

* the driver's **computation** changed, so the recorded numbers may no longer be
  what the code produces — re-run required; and
* only the **command-line wiring** changed, so the computation is byte-identical
  and the numbers still are what the current code produces.

The second case is real. On 2026-09-26 all 17 list-valued flags across 8 drivers
gained `action=ListOnce` so that a repeated flag fails loudly instead of silently
running half the parameter space (see `experiments/_cli.py`). That touched seven
drivers and so invalidated the recorded provenance of every artifact they
produced — including a T=8 baseline and a T=20 pilot — while changing no
arithmetic.

`experiments/check_driver_drift.py` separates them **by parsed structure**: it
recovers the driver at the recorded commit, strips `action=ListOnce` and its
import from the current file, and compares `ast.dump` of the two. Identical means
the computation is unchanged; different means name what changed.

A *line-based* comparison is the obvious implementation and it is wrong: adding
`action=ListOnce` to an `add_argument` that already spanned two lines pushes its
`default=` onto a continuation line, so a pure wiring change produced
`+ default=[64, 128])` and **13 of 20 artifacts were mislabelled "substantive"**.
Comparing parsed structure cannot have that failure, because a continuation line
is not a node.

At the time of writing: **7 current, 9 wiring-only, 4 substantive.** All four
substantive ones are changes to what is written or described rather than to the
arithmetic — two gained a description string, one gained the zonal-share keys,
and one (`json_safe`) changes non-finite floats to `null`, which only bites
artifacts that contain one.

## Flags that do not exist, checked before the run

`experiments/check_driver_flags.py` asks each driver for its own `--help` and
verifies every flag in a launch script against it. It exists because two bad
invocations cost real time on 2026-09-26, both of the same shape — an argument
the parser does not have, or has differently — and **neither failed loudly**: a
shared `--dt` plus a per-case `--dt` ran one case at twice its recorded timestep,
and `--re 5000 --re 1000` ran half the parameter space and overwrote a complete
artifact. Both produced complete-looking files from runs that did not do what
their names said.

The first draft of the refresh script that this check validated contained two
flags that do not exist (`--seed` on `run_static_basis_construction.py`, which
takes `--seeds` only, and `--adaptive-rank` on `run_baselines.py`, whose adaptive
rank is read off the adaptive run rather than given). Both would have failed at
parse time, so they were caught for free — but they were caught by *asking the
parser*, not by reading the driver, which is the point.

**What the check cannot see:** a flag the parser *has* but means differently
still runs happily and still produces a wrong artifact. Every argument list in
these runs is transcribed from the artifact's own recorded `parameters` block
for that reason, and written out in full rather than assembled from a shared
block — the shared block is what produced the duplicated `--dt`.

## Registry rows that need re-pinning, with the values (2026-09-26)

Run against the reviewer's `claims_registry.py` with the writer's draft from
`origin/agent/writer`: **23 rows OK, 16 FAIL.** Every failure is accounted for,
and none of them is a number that moved for a reason we do not know.

**Seven `tstar_*` rows — the block fix, 3.9% to 9.3%.** The rows-derived `t*` is
above the value quoted from the un-provenanced crossover block, consistently and
in one direction. These are the values to pin, at full precision:

| row | value | was | change |
|---|---|---|---|
| `tstar_r16` | `0.7076762337623602` | 0.6493281145096707 | +8.99% |
| `tstar_r32` | `1.5981858222903682` | 1.4816252539052939 | +7.87% |
| `tstar_r32_W0p5` | `1.5899768518577335` | 1.4739544217813643 | +7.87% |
| `tstar_r32_W1p0` | `1.5995931156857837` | 1.4832176727372877 | +7.85% |
| `tstar_r16_re1000` | `0.7283236032445684` | 0.6665645808117523 | +9.27% |
| `tstar_r32_re1000` | `1.7200204892865198` | 1.6094633714766546 | +6.87% |
| `tstar_N128_r16` | `0.9754557646562387` | 0.9386425215032279 | +3.92% |

Brackets are unaffected and exact under both derivations: `[0.5, 1.0]` for r=16,
`[1.0, 2.0]` for r=32. The legacy block sat 6.4–8.5% below the rows in all 18
resolved cases across both Reynolds numbers, so the direction and the size are
both systematic rather than scatter.

**Four `zonal_share_energy_*` rows — a bug in `resolve`, predating today.** The
rows use `field="zonal_energy_fraction.at_final_step"`, and `resolve` looks a
plain `field` up as a **literal key**; it only descends on `.` inside the
`@min:`/`@max:` form. The artifacts have always been nested, so these rows have
never resolved against any version of the data. Verified against the pre-change
artifacts, so it is not from the zonal-share work. Either descend on `.`
generally, or point the rows at the new sibling keys
(`zonal_energy_fraction_fluctuation`, `zonal_energy_fraction_components`) —
which would also let a row check the value *and* its definition.

**Five `mem_*` rows — the rows are pinned to a quantity that is not reproducible.**
`mem_noise_floor_mib` is pinned at 0.0977 MiB, one of four single-sample values
that quantity has taken (0.1328 / 0.0664 / 0.0977 / 0.0039 — a factor of 34), and
no correct measurement of it can be 0.0977: it is now the **maximum of eight
re-measurements** by construction. The four `mem_overhead_*` rows are 1.3–5.5%
out, which the gate itself calls "plausibly a re-run" — and it is: across three
independent measurements the overhead of the projected integrator at N=64 moved by
**+136%**. These rows need a stated tolerance or a distribution, not a point
pinned to `sf=8`.

## The cost ratios are not reproducible to better than ~15% on this node

Five committed versions of `cost_retiming.json`, all the same configuration
(N=64/128/256, ranks {2, 64}, 7 interleaved repeats of 2000 steps), with the
maximum per-configuration `full_step_ratio_vs_reference`:

| committed | OMP threads | load at end | N=64 | N=128 | N=256 |
|---|---|---|---|---|---|
| 09-25 16:17 | 1 | – | 2.071 | 2.144 | 2.181 |
| 09-25 23:23 | 1 | 1.36 | 2.426 | 2.710 | 2.308 |
| 09-26 02:42 | 1 | 1.33 | 2.480 | **2.740** | 2.346 |
| 09-26 10:31 | 2 | 2.27 | 2.562 | 3.640 | 3.048 |
| 09-26 13:xx | 2 | 1.82 | 2.437 | 3.543 | 2.400 |

**At a fixed thread count the N=128 ratio has ranged 2.14 – 2.74, a 28% spread
on an identical configuration**, and the within-run spread over 7 interleaved
repeats is only 0.17 – 0.35 (7–10%). So the protocol's precision is roughly a
third of the between-run uncertainty, and quoting a cost ratio as a point
overstates what was measured.

**The thread count moves it by 43% at N=128** (2.57 at one thread, 3.54 at two),
which is larger than every other effect here and is a property of the node rather
than of the method. `bench_cost.py` now records `threads_match_canonical` and
`threads_differing_from_canonical`, because a 1-thread re-run landed within 6% of
the 2-thread pinned value at one grid — close enough to look like agreement, and
not agreement.

**One measurement failure was mine and is worth recording.** The 10:31 re-run was
launched while three other streams were using the same twelve cores. Its N=128
ratio of 3.640 is the highest in the table, and interleaving only controls for load
that arrives *within* a run — it cannot control for load that was already there.
`cost_retiming.json`'s `shared_node_note` says as much, and I ran it anyway. The
re-run at 13:xx was done with nothing else on the machine and gave 3.543, so
contention accounts for about 3% of that particular gap and the rest is the
thread-count and machine-state effects above.

**What the paper can honestly say.** The ratio of projected-DLRA step time to
full-grid step time is **2.1–2.7 at one thread** and **3.4–3.6 at two threads**,
N=128, on this node, with a between-run spread comparable to the thread-count
effect. Any cost claim needs its thread count and load stated next to it, and
should be a range rather than a value. That is not a weakness in the
interleaving — the interleaving is what makes the *ratio* usable at all on a noisy
node — it is a statement about what the ratio can be resolved to.
