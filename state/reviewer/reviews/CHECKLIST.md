# CHECKLIST.md — standing acceptance criteria (two lenses)

Used by the reviewer in every review cycle (D6). A merge to `main` requires
the applicable items to pass, or an explicit recorded waiver in the review
report.

## Lens 1 — Correctness

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

### 1.4 Tests (do we do enough?)
- [ ] Unit tests exist for the core routines: SP split /
      structure-preserving projection, divergence-free enforcement, rank
      update + adaptive threshold logic.
- [ ] Edge cases covered: rank growth from a low initial rank, stagnation /
      no-growth behavior, restart from checkpoint, long-time runs (no drift
      in invariants).
- [ ] Tests are committed and runnable (`experiments/`), not just ad-hoc
      scripts.

### 1.5 Honesty
- [ ] Where we are slower / less accurate, it is reported, not hidden.
- [ ] No cherry-picked runs; if multiple seeds/forcings, the spread is
      reported.
- [ ] Paper claims do not exceed what the logged results show.

## Lens 2 — Writing

### 2.1 Contribution framing
- [ ] The contribution statement says exactly what we do: DLRA on the
      low-rank manifold + SP split + **exact** divergence-freeness +
      high-Re turbulent validation. No overclaim, no underclaim.
- [ ] Novelty stated with the persisted-survey citation (D4); closest prior
      art (Girfoglio–Quaini–Rozza) explicitly positioned.
- [ ] Related work covers DLRA (Osepko et al.), POD-Galerkin ROM, and
      structure-preserving / divergence-free discretization literature.

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

### 2.5 Readability
- [ ] Method → experiments is followable in one pass by a competent
      numerical-methods reviewer who has not seen our code.
