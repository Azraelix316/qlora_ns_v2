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
- [ ] **(R5)** Order and energy tests exist for the **reduced** path, not only
      for the full-grid kernel.

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

## Lens 2 — Writing

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
- [ ] No agent writes outside its owned paths, and nothing lands in `scripts/`,
      `AGENTS.md`, `PROTOCOL.md` or `lessons_learned.md` without reviewer
      approval (D7). A "net diff vs main is empty" check is how to distinguish a
      stale base from a real violation.
