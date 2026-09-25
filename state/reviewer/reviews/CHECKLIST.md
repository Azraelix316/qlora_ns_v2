# CHECKLIST.md — standing acceptance criteria (two lenses)

Used by the reviewer in every review cycle (D6). A merge to `main` requires
the applicable items to pass, or an explicit recorded waiver in the review
report.

## Lens 1 — Correctness

### 1.0 Comparability (added R5 — do the numbers mean what they claim?)
A benchmark can be internally consistent and still measure the harness
instead of the method. These are merge-blocking for any accuracy claim.
- [ ] **All compared methods start from a bit-identical state.** A reduced
      method that projects its initial condition to rank r starts from a
      *different state* than the reference; the resulting energy loss is not
      integrator error. Report any IC-projection error as a separate number.
- [ ] **Baselines are rank- and work-matched**, or the mismatch is stated
      (e.g. POD at r=16 compared against an adaptive method that reached r=42
      is not a comparison).
- [ ] A reduced baseline that fails to track the reference (relative error ≥ 1,
      energy/enstrophy off by an order of magnitude, O(1) PDE residual) is
      **not** citable as "the baseline is worse" — it is a broken baseline.
      Either fix it or report it as such.
- [ ] Headline errors are not dominated by a single setup artifact: if the
      error is ~the same at every Re, the error is measuring the setup.
- [ ] Any "grid check" changes **one** thing (resolution) and holds the
      physical problem fixed (same band-limited IC, dt scaled with dx, same
      method settings).
- [ ] The reported CFL is a meaningful fraction of the stability limit, or the
      reason for the conservative dt is given.

### 1.1 Provenance (every number in the paper)
- [ ] Each cited number traces to a committed file in `state/coder/results/`
      (one small file per run) or `experiments/`, with config + driver + git
      commit recorded in the result file.
- [ ] Headline numbers are reproducible with one command from a committed
      config.
- [ ] **An artifact is not verified until it has been checked against the CODE THAT PRODUCED
      IT** (added R50 — and it is the rule I broke twice). Read `provenance.git_commit` in the
      artifact, then check that commit's version of the driver, and whether the driver has
      changed *since*. **This is R27 restated where it actually bit:** in R48 I printed
      `crossover_surface.json`'s `provenance.git_commit = 5853ba9` and did not act on it; the
      driver changed in the next commit (`bc35666`) to fix a bug that degraded the baseline at
      short horizons, and the D13 claim I built on that artifact was flatly wrong. **Reading a
      number and separately reading the code, without comparing the two, verifies nothing
      about the number's provenance.** Before quoting any artifact: (a) its
      `provenance.git_commit`; (b) `git diff <that commit> HEAD -- <driver>` — if non-empty the
      artifact may not reflect the committed code; (c) does the driver's *current* output
      schema match the artifact's keys? **This applies to my own measurements too: R50's
      numbers were taken on `bc35666` and must be re-checked whenever the driver moves.**
- [ ] **A document that supersedes other documents is audited against the
      artifacts before it is pushed, not after** (added R44). `CLAIMS.md` is
      built from prior review reports, not from new measurement, so it gets
      exactly one check — and R44 found one wrong number *and* one
      unreproducible number in it, both mine. An authoritative summary
      inherits every unverified number it contains, **with more authority than
      the originals had**: reading a number as "already checked" because it
      came from my own earlier work is the same error as reading a default as
      a record of what was run (R8). **A number whose only surviving record is
      a remembered measurement is not admissible — strike it and re-measure
      with the setup recorded.**

### 1.2 Invariants (D3)
- [ ] max |∇·u| ≈ 1e-14 verified and logged for **every** run, laminar and
      turbulent.
- [ ] Taylor–Green: KE monotone non-increasing; rank behaves as expected
      (small, decays 3→2→1).
- [ ] Forced runs: forcing-aware invariant (as defined in
      `docs/theory/stability-error.md`) verified and logged.

### 1.3 Validation ladder (the experiment is actually good)
- [ ] L1: Taylor–Green laminar smoke test passes all invariants.
- [ ] L2: 2D forced turbulence runs at Re ∈ {100, 1000, 5000} (D1, D2).
- [ ] L3: full-grid spectral reference computed; max relative L2 error
      reported at each Re.
- [ ] L4: static POD baseline at each Re; our method compared honestly,
      including where we are slower.
- [ ] Rank dynamics shown: rank growth, singular-value decay, and what
      triggers the adaptive growth (ties to `docs/theory/rank-growth.md`).
- [ ] **(R5)** **Statistical stationarity**: runs long enough that E(t)/Z(t)
      reach a fluctuating plateau. A window shorter than one eddy turnover is a
      transient, not turbulence, and the Re values are then not distinguished.
- [ ] **(R5)** **Resolution**: a real two-grid (or better) study showing the
      reported diagnostics are grid-converged, with an explicit statement of
      which Re is resolved at which N.
- [ ] **(R5)** **Spectra**: isotropic energy/enstrophy spectra E(k), Z(k) of
      the full-grid reference over all resolved wavenumbers, time-averaged
      after stationarity. Singular values of the *rank-truncated reduced state*
      are not a turbulence spectrum and cannot support a "slow decay" claim.
- [ ] **(R5)** The forcing matches what the name claims and what the literature
      uses for comparability (for "Kolmogorov": the Arnold–Korkin–Sinitsyn
      cellular pump, not an unidirectional shear).

### 1.4 Tests (do we do enough?)
- [ ] Unit tests exist for the core routines: SP split /
      structure-preserving projection, divergence-free enforcement, rank
      update + adaptive threshold logic.
- [ ] Edge cases covered: rank growth from a low initial rank, stagnation /
      no-growth behavior, restart from checkpoint, long-time runs (no drift
      in invariants).
- [ ] Tests are committed and runnable (`experiments/`), not just ad-hoc
      scripts.
- [ ] **(R5)** The documented test command actually runs the tests. A test file
      invoked as a plain script that defines functions and exits 0 is a false
      pass; the reviewer will run the suite the way the README says and check
      the count.
- [ ] **(R5)** **Negative controls** for structurally-guaranteed invariants:
      since a stream-function state is divergence-free by construction, the
      diagnostic must be shown to *detect* a real violation (inject
      `u + ∇φ`, assert it reports O(1)), otherwise the invariant test is
      vacuous.
- [ ] **(R5k)** **Operator tests on full-band fields.** A suite whose fields are
      all smooth or band-limited cannot catch an error that only appears at the
      Nyquist wavenumber. At least one test must use a full-band field and
      compare the spectral operators against a full 2-D spectrum (no rFFT
      half-spectrum route), covering `velocity`, `grad`, `lap`, `vorticity` and
      divergence. The engine currently fails `v == -∂ₓψ` on such a field because
      `kx[N//2]` is used as a derivative multiplier; see
      `reviews/2026-09-25-R5k-engine-operator-audit.md`.
- [ ] **(R5l)** **Projection APIs are idempotent and match least squares.**
      `P² = P`, and the projection must equal an independently computed
      least-squares fit onto `mean + span(basis)`. Test with a field whose basis
      vectors are *not* spatially mean-free — otherwise the defect hides.
      `SVDProjector` passes both (and is the Eckart–Young truncation to 0.0);
      `PODGalerkin.project` currently fails both because it ends with
      `out - np.mean(out)`, which shifts the result out of the subspace. See
      `reviews/2026-09-25-R5l-rank-and-projection-audit.md`.
- [ ] **(R5l)** **Rank logic checked against brute force:** the rank rule equals
      `#{σ_i > tol·σ_1}` clipped to `[min_rank, max_rank]`; rank adaptation reads
      the retained pre-projection candidate; factor columns are orthonormal.
- [ ] **(R5)** Order and energy tests exist for the **reduced** path, not only
      for the full-grid kernel.
- [ ] **(R5q)** **Cost-model tests.** A test that pins the *current* per-step cost
      model, so that a later improvement is visible as a test changing state rather
      than as a claim in prose. Two assertions: (a) per-step cost is currently
      **rank-independent** — the projector SVDs the whole `N×N` field at four stage
      boundaries, so `r=2` and `r=64` cost the same to within 1.25× (measured: 7.31
      vs 7.81 ms at N=64); the docstring must say this is today's behaviour and that
      the V6 port must invert it; (b) the number of full SVDs per step is counted
      and asserted, so that reducing 4 → 1 is a test that can fail.

- [ ] **(R25) Fit-reproduces-its-own-input.** Every component that is *fitted*,
      *reduced*, or *learned* from data must reproduce the data it was fitted on
      to machine precision at full rank, and a committed test must assert it.
      This is the one-line check that would have caught R24 at R5: `PODGalerkin`
      reshapes its snapshot matrix wrongly, so it has never computed POD, and
      projecting onto its own training snapshots gives relative error
      **1.12–1.54** — worse than returning the zero field. It applies to POD, to
      any future hyper-reduction, empirical interpolation, or learned operator,
      and to the DLRA's own retained candidate. See
      `reviews/2026-09-25-R25-contract-audit-of-solvers.md`.
- [ ] **(R25) No warm-object reuse.** An object that carries learned or counter
      state across `initialize()` must either fully reset or be reconstructed per
      run, and tests must construct fresh objects. `DLRA.initialize()` currently
      does **not** reset a warm object: after one `integrate`, `initialize` plus
      five steps differs from a fresh `DLRA` by `maxerr = 0.432`. Any experiment
      script that reuses a `DLRA` across runs is silently wrong. See
      `reviews/2026-09-25-R25-contract-audit-of-solvers.md`.
- [ ] **(R25) Independent checks are themselves validated before a disagreement
      is believed.** In R25, four of five apparent engine failures were defects
      in the check, not the code (component indexing, a transposed identity, a
      dropped argument, a reused object). A check that disagrees with tested code
      must first be shown to converge or to agree on a case where the answer is
      known; only then is the disagreement evidence.
- [ ] **(R27) Provenance beats fingerprint — never establish that a number is
      stale by matching a remembered string.** In R27 I scanned artifacts for the
      literals `"1.0802"` and `"147.53"` to find void POD values and reported a
      file as clean; it held `1.07759`. The stale value was found only by
      comparing each summary field against the per-run artifact it aggregates and
      by reading `provenance.git_commit`. An artifact is stale if its recorded
      `git_commit` differs from that of its siblings, or if any summary field
      disagrees with the artifact it aggregates. This is D11.7 restated as an
      operational test, after I broke D11.7 in the same review that wrote it.
- [ ] **(R27) Every summary/aggregate artifact is regenerated in the same pass as
      the records it aggregates.** `state/coder/results/benchmark_summary.json` was
      the one file missed by an otherwise complete regeneration, and it is the file
      a reader opens first.

### 1.4a Timing methodology (R5q — every timing that reaches the paper)

These are not style preferences. The committed timings were invalid on both counts
below, and the resulting bias was **configuration-dependent** (20–36% on the
DLRA/full-grid ratio), so a reviewer cannot reconstruct them.

- [ ] **(R5q)** **Thread counts pinned and recorded in the artifact** that contains
      the timing (`OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`).
      Unpinned multithreaded LAPACK `gesdd` measured 23–78× slower than the same
      factorization at 1 thread on matrices from 47×47 to 256×256, and
      `scipy.linalg.svd(..., lapack_driver='gesvd')` is ~80× faster than `gesdd` on
      the same 47×47 input. Timings without pinned threads are not reproducible.
- [ ] **(R5q)** **The timed region dominates process start-up.** At `dt=5e-4` that
      means ≥2000 steps. The committed runs used `final_time: 0.1` = 200 steps and
      <1.2 s total, so they measured interpreter start-up and BLAS thread-pool
      spin-up, not the method.
- [ ] **(R5q)** **Warm-up discarded, ≥7 repeats, median with spread** — and a
      Re-to-Re spread above a few percent is treated as an artifact, not a result:
      the three Re cases are computationally identical except for `nu`.
- [ ] **(R5q)** **Cost and accuracy are on the same axes.** A cost bar with no
      accuracy axis cannot support a claim, and at `r≈45` no per-step speedup is
      available to this method (measured 2.9×/3.1×/3.6× slower than the full grid
      at N=64/128/256; near-parity by N=512 after the V6 port, not a win).

### 1.4b Two artifacts that disagree (added R60 — the block-vs-rows rule)

When a **derived block** and the **primary rows** of the same artifact disagree, the
disagreement is a defect in one of them — but **not necessarily in the derived one.**
This is the R58 error: I ruled "the rows are authoritative" on the reasoning that a
derived block disagreeing with primary data means the derivation is wrong. **That
reasoning holds only if the block was computed from those rows.** Here it was not,
and the block turned out to be the *more* in-sample of the two.

- [ ] **(R60)** **Before ruling on which side is wrong, establish that the derived
      block is a function of the rows at all.** Name the code path, or show it is
      not one.
- [ ] **(R60)** **Separate "different error definition" from "different computed
      quantity."** Exhaust the error columns, cross-column pairs and ranks first
      (this took `1–3%` here); if the gap survives — it was `3.06×` in the static
      error — **the disagreement is in the computation, not the labelling**, and no
      choice of column will reconcile it.
- [ ] **(R60)** **Check the direction, not just the size.** An in-sample baseline
      gives *lower* error and an *earlier* crossover; an out-of-sample one the
      reverse. The sign of the gap is evidence about which side is in-sample.
- [ ] **(R60)** **If a figure and a quoted number are derived from the two sides,
      neither may be published until they agree** — here the central figure and the
      central number were `1.90×` apart.
- [ ] **(R60)** **Record an inconclusive test as inconclusive.** My reconstruction
      reproduced *neither* side, which is itself the finding; guessing which side to
      believe would have repeated R58.

### 1.5 Honesty
- [ ] Where we are slower / less accurate, it is reported, not hidden.
- [ ] No cherry-picked runs; if multiple seeds/forcings, the spread is
      reported.
- [ ] Paper claims do not exceed what the logged results show.
- [ ] **(R5)** A diagnostic is not presented as evidence for a property it
      cannot evidence — e.g. a continuous energy residual with the measured
      projection work subtracted is an accounting identity, not a
      structure-preservation result. A "stable" flag means "finite and within
      the stated sanity limits", not "accurate" or "long-time stable".

### 1.10 Classes of defect found after this checklist was written (added R79)

**Why this section exists.** This gate was built over twenty-eight cycles and **reconciled against
the defect classes discovered later exactly never** — R79 measured it: **six of the most productive
defect classes in the project had no item here at all.** A gate that does not gate on a defect class
is not a gate; it is a list. **Each item names the cycle that found the defect, because an item with
no cycle behind it is an item nobody has tested.**

- [ ] **(R71) Does any test read a committed artifact?** The project had **40 component tests
      and 0 artifact tests**, and every serious error was in the artifact layer. For a merge
      that changes a number the paper quotes, name the test that would fail if it regressed.
- [ ] **(R71) For a derived block, is there a test that it is a function of its primary
      rows?** Fifteen lines, run against committed files, no compute — and it would have
      caught four consecutive cycles of reviewer error.
- [ ] **(R72) Does every figure's axis have enough range to show its own data?** A linear
      axis carrying a value of `7.1e+292` rendered every finite bar at `1.5e-290` of the
      width. **The figure looked correct and showed nothing.**
- [ ] **(R72/R73) Does every figure title assert only what its data shows?** A title is a
      claim. `fig_div_free` asserted *"exact divergence-freeness holds for every method"*
      over a dataset with four counterexamples, and `fig_crossover` printed two withdrawn
      claims — **one refuted by a code comment eleven lines above it. Two of six checkable
      titles were wrong, and the wrong one was the central figure.**
- [ ] **(R73) When a decision withdraws a claim, is the withdrawal swept into figure
      titles, axis labels and suptitles — and not only into prose?** The sweep reaches files
      the reviewer owns and stops at files they do not, **but the claims in those files are
      theirs, and the paper reproduces them verbatim.**
- [ ] **(R74) Does the paper state every invariant the brief names?** `AGENTS.md` named two;
      the paper had one, and the second was implemented and tested.
- [ ] **(R40/D40) Can the person receiving the review act on it today?** A correction
      arriving as the hundredth block displaces the ninety-nine before it. **Consolidation
      is a review deliverable, and the test of a review is whether its recipient can act.**
- [ ] **(R78) Does a mechanical check over prose know where that file's legitimate
      withdrawal regions are?** Distinguish *"this number is void, here is why"* from
      *"this number is my claim"* **by structure, not by keyword.**
- [ ] **(R82) For the artifact the paper's thesis rests on: has the code at its OWN RECORDED COMMIT
      been run, rather than the artifact being fingerprinted or reasoned about?** `git archive <commit>
      | tar -x -C tmp` gives a tree with **no `.git`, so uncommitted code is impossible**; run its
      driver and compare. **First check the basis is fitted on the PAST** (D47.5a): if it is, 500
      steps = 12 s, because the rows are path-independent (D47.5), and do not read `final_time: 8.0`
      as the cost. **If any baseline's window is derived from `T` or lies in the future, there is NO
      cheap reproduction** — `baselines_re5000_N64_T8.json` costs its recorded 3 014 s / 19 methods, and
      **is therefore NOT covered by this item; say so rather than assuming it is.**
      **A `working_tree_dirty: false` field is a recorded assertion, not a verification.**
- [ ] **(R81) Did this cycle open each agent's most recent commit and read what it CONTAINS?**
      **A commit count is a receipt, not a delivery.** `rev-list --count` read `1 ahead` for a dozen
      cycles while a complete 1 281-line paper sat unread on the writer's branch (D46.1).
- [ ] **(R80) Does the same status-line grep `agent.sh` uses return something current on
      EVERY agent's board?**
      Not just the reviewer's — `agent.sh start <agent>` prints each board, and the writer's read
      "fresh — no sessions yet" after a session that drafted the whole paper.
- [ ] **(R77) Was the standing instruction list itself measured rather than trusted?** Two
      instructions in this project named work that did not exist. **Measuring the list is
      cheap; a phantom instruction costs cycles.**

## Lens 2 — Writing

### 1.9 Reviewer communication format (added R28 — binding on the reviewer)

The reviewer's job is to make the next action obvious. Long messages defeat that: the
agents could not tell what was high priority, and one push in response produced three
false completion claims because the assignment was buried in prose.

- [ ] **Every agent-facing message leads with a `BLOCKING` list of at most 5 items.**
      Each item is one or two lines and contains the exact path, string, or command.
      Nothing explanatory goes above it.
- [ ] **Items are labelled `BLOCKING` (merge-gating) or `ALSO FIX` (not gating).**
      An unlabelled request is a request the agent cannot prioritise.
- [ ] **Each message states what is NOT the agent's problem.** Without this, agents keep
      re-reading decisions that are already closed, and re-litigate them.
- [ ] **Credit is explicit and first.** Name what landed and say it was right, before any
      outstanding item. A review that only lists defects gets defects back.
- [ ] **Detail goes in a report file, not the message.** The message is the index; the
      report under `state/reviewer/reviews/` is the argument. Do not inline the argument.
- [ ] **The first screen of `state/reviewer/outbox/to-<agent>.md` is rewritten every
      cycle** to reflect the current blockers, so an agent that runs `inbox` after three
      cycles sees the current state and not a stale one.
- [ ] **Rewriting an outbox header must not shorten the history.** Outboxes are
      append-only: replace the leading header, append the *entire* prior body. R28b
      truncated all four outboxes (996→24, 848→27, 365→24, 566→22 lines) in the same
      session in which I held another agent's push for doing the same thing, then
      "restored" them into the wrong worktree and nearly lost them again. The header is
      replaceable — that is the point of the exercise, and the old ones were stale — but
      **everything below the `---` is history and must survive verbatim.** Check: the
      number of `## <timestamp>` blocks must not decrease after any outbox edit. Also
      confirm *which worktree* you are editing; `state/reviewer/` exists in both the main
      checkout and `worktrees/reviewer/`, and only the latter is yours to commit from.

### 2.0 Merge safety (checked by the reviewer before every merge)

**The binding question is: would merging delete or revert anything that is on `main`
now?** Test the property, not a proxy for it. Two checks, in this order.

- [ ] **Property test (binding).** `git diff --diff-filter=D --name-only
      origin/main...origin/agent/<them>` must be **empty** — no file present on
      `main` is deleted by their branch. Then confirm the branch touches nothing
      outside the agent's owned paths, and that
      `git merge-tree $(git merge-base origin/main origin/agent/<them>) origin/main
      origin/agent/<them>` reports **0 conflicts**. If this passes, the merge is safe
      and the ancestor test below is advisory only.
      - **Copy the three dots. Do not retype this from memory.** `A..B` compares two
        **trees** and `A...B` compares against the **merge base**. On a branch that is
        merely *behind* `main`, the two-dot form reports **every file `main` gained since
        the branch point as a deletion**. Observed twice by me, in R46 and again in R47,
        with the same false result: **20 of my own review files reported as deleted**,
        plus `solvers/bug.py` and `run_crossover.py` — on branches that in fact deleted
        nothing. **Copy the command; do not reconstruct it.** If a two-dot diff ever
        shows a plausible-sounding deletion list, the first thing to check is whether the
        agent is simply behind `main`.
- [ ] **Ancestor test (advisory — a fast pre-check, not a gate).**
      `git merge-base --is-ancestor origin/main origin/agent/<them>`.
      **Failing this does not by itself block a merge** provided the property test
      passes. Added after R9: the ancestor test is a *proxy* for "will this revert
      content", and on 2026-09-25 a branch based on `main@8d4098c` failed it while
      deleting nothing from a `main` four merges ahead, and provably touched nothing
      outside its owned paths. A proxy that is too strict will eventually block a
      legitimate merge, and an agent that cannot land clean work stops doing the work.
      The catastrophic case the proxy was written for is real — a branch based on a
      pre-engine commit diffs as **~24,800 deletions** including the whole engine and
      the review record — but the property test detects it directly and exactly.
- [ ] **A review's verdict line is a claim about `main`, so verify it the way any claim
      about `main` is verified — by looking** (added R49). In R48 I wrote "Verdict:
      merged" for `bc35666` **without having run the merge**; I merged only my own
      branch, and `crossover_surface.json` was not on `main` when the review declared
      it merged. It is now, at `889813f`. **This is the same failure I charged
      writing-research with in the same cycle.** **The merge is executed first and the
      verdict is written from the merge's output**, or the verdict says *not merged*.
      The check is one command: `git cat-file -e origin/main:<path>` for the
      load-bearing artifact. **A verdict is the one line of a review that gets quoted
      downstream, so it is the last line allowed to be written from intent.**
      - **BROKEN TWICE — so this is now an ORDERING constraint, not a reminder** (R56b).
        R48: wrote "merged" without merging; R49 caught it and added this item.
        **R56: wrote "merged at `f640244`" for `5909af6`, which was not in `f640244` at
        all** — `f640244` is the *reviewer* merge. The mechanism: R55's merge output
        ended `46834c4 Merge remote-tracking branch 'origin/agent/coder'`, and in R56 I
        read *that* as confirming the merge of a *different* commit. **I never ran
        `git merge origin/agent/coder` in R56.** The failure was not forgetting to
        check — it was **reading a previous cycle's output as this cycle's.**
        **A rule I have to remember is a rule I will break, and this one was written by
        me and broken by me.** Therefore: **(1)** the verdict is written **last**,
        after the push; **(2)** from `git merge-base --is-ancestor <reviewed-commit>
        origin/main`, **run after the push** — run before, it reports a false negative,
        as I also did once in R56b; **(3)** if that check was not run, the verdict says
        *not merged*; **(4)** never read a previous cycle's command output as
        confirmation for this cycle's.
- [ ] **After every agent-branch merge, verify explicitly:** the other agents' owned
      paths are still present (`solvers/`, `experiments/`, `state/coder/`,
      `state/reviewer/`, scaffold files), the file count went **up or stayed equal**,
      and `git diff --stat` against the pre-merge `main` shows no unexpected deletions.
      On 2026-09-25 this caught nothing (79 → 88 files, all 19 key paths present),
      which is the point: it is cheap and it is the check that would have caught a
      real revert.

### 2.1 Contribution framing
- [ ] The contribution statement says exactly what we do: DLRA on the
      low-rank manifold + SP split + **exact** divergence-freeness +
      high-Re turbulent validation. No overclaim, no underclaim.
- [ ] **(R5)** **Exact divergence-freeness is NOT presented as the novelty.**
      In 2-D it is structural in the stream-function formulation (textbook),
      and the closest prior art (Girfoglio–Quaini–Rozza, arXiv:2201.00756) is
      *also* exactly divergence-free for the same reason — verified on the abs
      page 2026-09-25. State it as a property the method guarantees, and put the
      differentiation on: dynamical (not offline) low-rank, discrete structure
      preservation, and resolved high-Re validation with adaptive rank.
- [ ] **(R5)** The method is named for what it is. A rank-projected integrator
      with per-step full SVDs is not "DLRA"; a projection scheme is not
      "structure-preserving" unless a discrete property is proved or measured.
- [ ] Novelty stated with the persisted-survey citation (D4); closest prior
      art (Girfoglio–Quaini–Rozza) explicitly positioned.
- [ ] Related work covers DLRA (Osepko et al.), POD-Galerkin ROM, and
      structure-preserving / divergence-free discretization literature.
- [ ] The gap statement is one a knowledgeable reviewer cannot refute with a
      single citation. (R5: "current DLRA methods struggle with preserving
      divergence-freeness" is refuted by the closest prior art itself.)

### 2.2 Structure
- [ ] Abstract: problem → method → key quantitative result → honest
      limitation.
- [ ] Intro: motivation (why high-Re turbulence matters for reduced-order
      simulation) + a numbered contribution list.
- [ ] Method: SP split, stream-function form for 2D NS, adaptive rank
      strategy — a reviewer can implement it from the text.
- [ ] Experiments: setup, baselines, invariants, rank/error/cost results.
- [ ] Conclusion: what is shown, what is not (3D, error estimates, etc.).

### 2.3 Figures (each self-contained)
- [ ] Rank over time (turbulent, at least one Re).
- [ ] Singular-value decay at selected times (slow decay = the point).
- [ ] Error vs full grid at each Re.
- [ ] Cost comparison (wall time / ops vs baselines), including where we
      lose.
- [ ] A divergence-freeness figure or table (max |∇·u| per run).

### 2.4 Venue fit
- [ ] Formatting, length, and framing match the decided venue (D5);
      template from `docs/venues/`.
- [ ] **(R5)** Exactly **one** venue document exists, its ordering matches D5,
      excluded venues are absent, and every deadline carries a CfP URL **and an
      access date**. Projected/historical-pattern dates do not satisfy this.

### 2.5 Readability
- [ ] Method → experiments is followable in one pass by a competent
      numerical-methods reviewer who has not seen our code.

### 2.6 Citation and record integrity (added R5)
- [ ] Every arXiv ID in `refs.bib` resolves, on its abs page, to the title and
      authors claimed. Spot-checking is not enough: re-verify the whole file
      after any bulk edit.
- [ ] Every DOI resolves via `https://api.crossref.org/works/<doi>`.
      **Do not** use `doi.org` redirects as the check — in this environment they
      404 even for valid DOIs.
- [ ] No entry exists whose title/author/year cannot be found in a publisher or
      preprint record. If a reference cannot be verified, it is removed, not
      approximated. (R5: an entry citing an unrelated arXiv paper and matching
      no publication.)
- [ ] The owned literature index contains no unresolvable IDs, and query-log
      records are typed as query records rather than as works.
- [ ] **(R77) PRESENCE, not only resolution.** The citations the paper's related-work
      section *requires* are actually in `refs.bib`. **§2.6 verifies that entries which
      exist resolve; it says nothing about entries which are absent — and the absent ones
      are the ones D4 requires.** Three of the six were missing (Lubich–Oseledets
      `10.1007/s10543-013-0454-0`, Kusch–Schotth\"ofer & Walter `10.1137/25m1730673`,
      RAIL `10.1137/23M1622921`) and a fourth had no `doi` field. **Every one of them
      would have passed every other item in this section.**
- [ ] **(R77) A DOI's embedded year is not taken as the publication year.**
      `10.1137/23M1622921` is **2025**; `10.1007/s10543-013-0454-0` is **2014** though its
      `issued` says 2013. Use `published-print` where it exists.
- [ ] **(R77) Diacritics survive into `author` fields** (`Schotth\"ofer`), or the
      reference cannot be found by an author search.
- [ ] No agent writes outside its owned paths, and nothing lands in `scripts/`,
      `AGENTS.md`, `PROTOCOL.md` or `lessons_learned.md` without reviewer
      approval (D7). A "net diff vs main is empty" check is how to distinguish a
      stale base from a real violation.
