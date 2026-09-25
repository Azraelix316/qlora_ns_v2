# NOTES.md — reviewer

> Branch: `agent/reviewer` · Worktree: `worktrees/reviewer`
> Status: R5 complete, R6 waiting on agents (2026-09-25). **Merged:** coder's
> engine `b2f78fd` approved and integrated (D9) — 13/13 tests reproduced in a
> clean reviewer venv *from `main`*, discrete math verified by hand, Taylor–Green
> exactness satisfies D3's laminar invariant, no D7 violation, scope clean.
> **Held:** writing-research `abd4d63` (W1–W5: one fabricated citation, one
> unregistered DOI, D5 docs unconsolidated with no access dates, 9 unowned files
> incl. scaffold `scripts/arxiv_searcher.py`) and its `docs/structure/` draft
> (S1–S4). **Gates open:** D10 (V1–V7) — the headline 0.315 error is a harness
> artifact (rank-2 start on a rank-17 IC loses 65% of the energy before t=0), the
> POD baseline and the N=64/128 "grid check" are unusable, and the method is not
> yet DLRA; D3's forcing-aware invariant, owed by theoretical-research since R1.
> **V6 direction settled:** SPDLRA/BUG integrators already exist, so V6 is a port
> (arXiv:2402.08607, 2104.05247, 2608.27749), with the algorithm sent verbatim.
> **Novelty position settled at R5d and revised twice on the way** — operative
> wording is the R5d block of D4 only; "no DLRA for incompressible NS" and
> "first exactly divergence-free NS solver" are barred (Musharbash & Nobile,
> DOI 10.1016/j.jcp.2017.09.061). `AGENTS.md` and `lessons_learned.md` amended
> so no scaffold file repeats the retired claim. **Self-audit:** all 27
> quantitative claims in the gate machine-verified; one reviewer error found and
> corrected (IC rank is 17, not 19). Acceptance criteria are mechanical in
> `reviews/D10-EXPERIMENT-SPEC.md`. **Blocked on agent sessions, not on review
> work.** **R6:** writing-research `d97541d` reviewed — **HOLD**; the root
> cause is that their branch never merged `main` since R3, so the R5 verdict was
> never seen and they executed a superseded B*-numbered list. W1 regressed (a
> second fabricated Koch reference added), W3 and W5 claims verifiably false,
> W5 worse (two new junk files added while claiming cleanup complete). Credit
> recorded for refs.bib integrity and the ICASSP removal. `coder`, `writer`
> and `theoretical-research` have not run a session since the scaffold was
> created; 40+ reviewer messages are queued, delivery verified working.
> **R13 — tested my own one-step claim; it holds for one step only, and the flow
> is not chaotic on any horizon we run.** R12 told writer the method "is not
> error-amplifying" on a **one-step** measurement while flagging the multi-step question
> as unanswered in the same report. It should not have propagated. Measured properly
> (full grid and DLRA advanced **in lockstep**, A=0.5, Re=5000, N=64, from t=2 to t=5):
> rel L2 reaches **0.0785 at r=32, 0.1460 at r=16, 0.1889 at r=9, 0.3707 at r=5**, growing
> roughly exponentially with e-folding ≈1.2–2 time units, and **rank ordering strictly
> monotone at every sample**. So truncation introduces no *per-step* amplification — which
> is why the growth is smooth rather than explosive — but the accumulated error **does**
> grow at a rate rank controls. Retraction of the generalisation, not of the observation.
> **My first harness for this was wrong and the failure is the lesson:** it compared
> every run against a **frozen** reference, so the "method error" and the "background"
> measured the *same* quantity (displacement from t=2), agreed to four decimals, and
> appeared to show rank-*independence* and that **lower rank was better** — reversing the
> sign of the rank–accuracy relationship. Caught because *a control that agrees with its
> subject to four decimals is not a control*; redone and validated by two assertions
> before believing output (background starts at 6.8e-9 ≈ 1e-8 ✓; full-rank 43 starts at
> 1.4e-12 ≈ 0 ✓). Asked coder to build those assertions in and to **test the harness
> itself**. **The flow is not chaotic here:** a 1e-8 IC perturbation reaches only ~5e-8
> in three time units from starts at t=2/5/10/20, spanning E=39.5–940 and mean fraction
> 50–94%. **Good:** rel L2 is a *valid* accuracy measure on this horizon (background 1e-8
> vs method 1e-2–4e-1) — the first time P0's caveat has been **shown not to apply**
> rather than assumed, with λ ≈ **0.69/time unit** (lower bound, one smooth direction)
> and O(1) decorrelation at ~**30 time units**. **Bad:** that is weakly chaotic, not
> developed turbulence, so the honest regime is **slowly evolving, mean-dominated, weakly
> chaotic** — reinforced with R8/R8a. **Consequence:** the committed rel-L2 0.3165 at
> T=0.1 is not a method result (r=5 hits 0.083 after **0.12** time units from a
> developed state), and a proper number 5–40× smaller now exists. No accuracy claim
> beyond ~10 time units without re-measuring the background, which until now had never
> been measured at all.
> **R12 — ran R11's own experiment rather than delegating it: the premise is
> recoverable, and a mislabelled parameter was costing us the cost story.** No spectral
> gap at high N either (N=128 → rank **85** = ceiling, N=256 → **171**, both at every
> tol 1e-6…1e-14, with a **nine-order cliff** at the ceiling: σ₈₅/σ₁=2.50e-6 →
> σ₈₆/σ₁=1.73e-15; σ₁₇₁/σ₁=1.28e-7 → σ₁₇₂/σ₁=9.73e-16; σ₂₀₀/σ₁=2.0e-16), confirming
> R11 at high N. **But 99% of energy is in r=5 and 99.9% in r=9, identical at N=128 and
> N=256** — the energetic rank does not grow with the grid. **The defect:
> `_target_from_spectrum` tests `s > tolerance*s[0]` on singular VALUES, so
> `tolerance=1e-6` is an *energy* ratio of 1e-12 — six orders stricter than the name
> implies, and the committed `1e-8` is sixteen** — which is why runs select r=43 when
> r=5 carries 99% of the energy. A parameter whose name misdescribes its behaviour is
> misread by everyone, including me. **Three pictures of the same truncation disagree:**
> energy 0.999997 at N=64 r=32 yet rel L2 1.8e-3 and **ΔZ/Z −1.6e-2**; at r=5 energy
> error −1.7e-1 but **enstrophy error −6.7e-1**; at N=256 r=43 still **ΔZ/Z −7.8e-2**.
> **The dynamics do not amplify truncation over a step** (one-step error = state error to
> 4 s.f. at every rank, both N) — good news, and now a requested test. **Enstrophy is
> the demanding metric and is where this project validates** (R5m: POD 159× worse), so
> the validation metric largely decides whether the method looks good — the paper must
> declare which. **Reframed premise (defensible, with a mechanism and a prediction):**
> spectrally full-rank within the dealiased band, no gap, numerical rank = the grid's
> ceiling and not dynamical; energy strongly low-rank at r≈5, N-independent; truncation
> energetically accurate but progressively worse for enstrophy; no one-step error
> amplification. The "adaptive rank growth" claim is **removed**, not hedged. **It also
> corrects R5q and my own R11 pessimism:** R5q's near-parity-by-N=512 holds only at the
> tolerance-selected r≈45; the BUG flop crossover is `r=0.82·√N` = 13.1 at N=256, which
> is **above** the energetic rank 5–9, so the BUG basis update uses **fewer** flops than
> the dense SVD at r≈5–9, and r/N ≈ 0.02–0.035 — a **genuinely low-rank regime**. First
> finding in several cycles that *strengthens* the cost argument, and it came from fixing
> a mislabelled parameter. Told writer to drop "the method is never in a low-rank regime"
> and that the cost ceiling moves from N≈512 to N≈256 or below — while the no-speedup
> claim stands.
> **R11 — premise test: the rank is the dealiasing mask, not the dynamics.** The
> project's premise is "turbulent dynamics need rank ≫ 3, slow singular-value decay,
> adaptive rank growth". **Good news first:** R8a left an obvious worry — the mean
> carries 52–99% of the energy, so maybe the rank describes the mean, not the
> turbulence. Measured, **no**: the zonal mean is **exactly rank 1** (φ(y) broadcast
> along x is a rank-one outer product), so **42 of 43 retained modes are fluctuations**
> at every t and both high Re, and the slow decay is in the fluctuations
> (σ₃₂/σ₁ of the fluctuation field 7.4e-3 → 2.4e-4 over t=2→20 at Re=5000, zonal
> σ₈/σ₁ ~ 1e-64). **Serious finding:** the rank is **43 at every tolerance from 1e-6
> to 1e-14 and every t from 0.5 to 20** — invariant across five orders of magnitude in
> tolerance and a factor of 40 in time, so it measures nothing dynamic. And
> **2·floor(N/3)+1 = 43**. Tested across grids: measured rank **21/33/43/65/85** at
> N=**32/48/64/96/128** against 2·floor(N/3)+1 = **21/33/43/65/85** — **exact match
> everywhere**. The dealiased mask confines the x-Fourier support to that many
> wavenumbers, bounding the matrix rank, so **the state is full-rank within the band the
> grid admits, with no internal spectral gap.** Four consequences: (i) the "adaptive
> rank growth" is the rank-2 init artifact meeting a grid ceiling — F3 suspected a
> transient artefact, this is the mechanism; (ii) **the premise as stated is not
> supported** — rank is large because the grid admits ≈2N/3 x-modes, and the
> defensible reformulation is that truncation is not *spectrally* motivated but is
> *energetically* accurate (σ_last/σ₁ = 7.5e-5 at N=64, 2.0e-6 at N=128), which also
> matches R5m's rank-insensitive error; (iii) **the method is never in a genuinely
> low-rank regime on these grids** (r/N ≈ 2/3 at best), a structural reason F6's cost
> story is hard; (iv) **the two committed runs are limited by different ceilings** —
> at N=64 the grid (43) binds and `max_rank=48` does not, at N=128 the cap (48) binds
> against a ceiling of 85 — so the "grid check" varies which constraint limits rank,
> a third independent reason it is not one. Also: **dealiasing is load-bearing for
> stability** (`dealias=False` at Re=5000 overflows to NaN within t=5), and the
> full-state slow-decay metric is **contaminated by the growing mean in its
> denominator** (t=2: 1.94e-3 full vs **7.39e-3** on fluctuations, factor 3.8), so the
> project's verified 1.45e-3 understates the fluctuations' decay. **Decisive cheap
> experiment issued:** is there a spectral gap below the ceiling at N=256/512? If yes
> the premise stands in strong form; if the rank is always the ceiling, the
> adaptive-rank contribution is empty and the paper rests on the filtering/accuracy
> argument. **Correction to my own R8:** I told all three agents the committed
> configuration is `force_amplitude=0.2`, having read the *driver default*
> (`run_kolmogorov.py:393`); **every committed artifact records 0.5**. The stationarity
> finding survives and is **conservative** (at 0.5, Re=5000 reaches E=3747 = 169× E₀
> by t=40 with ratio still 125), but the S3 pilot must run at 0.5. **Fourth time the
> "which configuration is committed" question changed a conclusion** — the rule is not
> "measure more" but that **a default in a signature is not a record of what was run,
> and `state/*/results/*.json` is.**
> **R10 — audited the file I had flagged unaudited, and retracted a claim of my
> own.** `arxiv_index.json` (merged to `main` in R9) has **four defects**: (A1) a
> **non-resolving DOI on the project's closest prior art** — entry 15 records
> `10.1016/j.compflu.2022.105536`, Crossref returns **404**; correct is
> **`10.1016/j.compfluid.2022.105536`** (`compfluid`, not `compflu`), confirmed by title
> search at score 87.2. It is a **transcription error of a DOI I had already supplied
> twice** in my outbox; I checked my own records (`lessons_learned.md`, outbox, R5d) and
> they are correct, and `refs.bib` does not carry this DOI at all, so the defect is
> confined to the evidence artifact. (A2) entry 27 pairs `arXiv:1505.05648` with the
> projector-splitting title; verified via the arXiv API that 1505.05648 is **Barbara
> Schapira on horospherical foliations, math.DS** — the R7 misattribution, deleted from
> `refs.bib` in R9 but **left in the index**, so the error now lives in the one artifact
> meant to be the reproducible record. (A3) "Olga Koch" is in entry 28 as well as
> `refs.bib` — my R9 fix list named only one file. (A4) the persisted novelty query is
> **not reproducible**: entry 26 records `query: "divergence-free AND dynamical
> low-rank"`, `count: 0`, but that string returns **811** results as written (arXiv
> matches bare words loosely); the 0 belongs to the properly formed
> `all:"divergence-free" AND all:"dynamical low-rank"`, and even that is weak evidence
> since D4 already bars "to our knowledge" on arXiv alone. Three of four DOI-identified
> records verify exactly; **~25 arXiv-identified entries not individually verified this
> cycle — flagged, not implied clean.** **Retraction:** in R8a I asserted option (ii)
> (remove the zonal momentum equation) was "a real transformation with a literature
> behind it". **I could not verify it exists** — three targeted searches returned
> geophysical zonal-flow and unrelated material; nearest verified result is Šonbek,
> *JAMS* 4(3):423–449 (1991), the 2D NSE decay exponent, which is about *unforced*
> decay and does not establish the transformation. My hedge ("check the assumptions
> rather than take my word") was right in form but a hedge on a false claim is still a
> false claim, and two agents were about to act on it — retracted, and option (ii) is
> now costed as **open research**. Recommendation changed accordingly to option (i) on
> measured evidence (the mean carries 52–99% of total energy and grows at a
> `ν`-independent rate, so fluctuation variables are the natural ones). **Pattern, now
> seen four times:** fixing a defect in one file while it lives in another is not a fix —
> the audit must cover every artifact holding the claim.
> **R9 — writing-research `4086485`: MERGED to `main` (`aaa6e0c`).** First agent
> branch merged since coder's engine in R5, and the first writing-research work to
> reach `main`. **Ran `start` and merged `main`** after three pushes on an R3 base —
> the behaviour change asked for since R6c. **All eight junk files gone** (verified
> individually, then confirmed absent from `main`), including the 339-line
> `combined_scripts.tmp` and the 187-line `old_refs.bib` build hazard, and
> `scripts/arxiv_searcher.py` — an unowned file in the **scaffold** `scripts/` path,
> which is mine; deleting one's own clutter out of a path one does not own cleared a D7
> violation that survived three cycles, and I credited it. **`refs.bib` repaired and
> parsing** (214/214 braces, zero suspicious lines by depth-walk) **without** the string
> surgery that caused the damage. **Fabricated Koch entries replaced** by one correct
> record — `koch2007dlra`, SIMAX 29(2):434–454 (2007), DOI 10.1137/050639703, every
> field matching Crossref. **All three DOIs verify**, including a new
> `10.1063/5.0202509` (Zhang/Xu/Guo/Feng, *Physics of Fluids* 36(6) 2024) checked this
> session. **I merged despite the ancestry check failing**, because I tested the rule's
> purpose rather than its letter: 0 files deleted from `main`, 0 modified outside their
> owned paths, 0 conflicts, 79→88 files post-merge, all 19 key paths present. **Rewrote
> CHECKLIST §2.0** so the *property* test binds and the ancestry test is advisory — a
> proxy too strict to distinguish "stale but safe" from "dangerous" will block a
> legitimate merge, and an agent that cannot land clean work stops doing the work.
> **Four items left:** the venue doc is untouched and is the only one with substance
> (D5 order, one access date per deadline); `koch2007dlra` still says "Koch, Olga"
> (one word, must be Othmar); the Lubich–Oseledets projector-splitting record is absent
> (needed for the V6 port); and still no reply in their outbox. Not flagged as clean:
> `arxiv_index.json`, modified this commit and unaudited.
> **R8a — revision of R8: the mechanism is a growing zonal mean, not a spin-up
> transient, and my stationarity criterion was the wrong test.** R8's *conclusion*
> survives (no Re stationary at T=20 or T=40; committed t=0.1 runs still support no
> turbulence statistic) but its reasoning did not, and a conclusion reached by wrong
> reasoning is one that should not be trusted until re-derived. Measured to T=40:
> `ū_bar` grows at **≈0.11–0.13 per time unit at every Re across a 50× viscosity
> range**, so the mean is *not* approaching a viscous balance (which would separate
> the trajectories by orders of magnitude) and **has no plateau on any affordable
> horizon** — physics for forced Kolmogorov flow, not a defect. Hence total-E
> stationarity is **mis-specified, not merely unmet**, and I replaced it with S1–S5
> (statistics on `ψ′ = ψ − x-avg(ψ)`; stationarity per Re on `E_fluct` **and**
> `Z_fluct`, bar |drift| ≤ 10%; horizon **measured** not assumed; regime characterised
> per Re; nothing from t ≤ 0.1). **Biggest new finding: Re=100 is quasi-laminar**
> (`E_fluct` 7.90 → 0.55, drift **−69%**), so the planned Re sweep is **not one regime
> at three Re** — varying Re changes the qualitative behaviour, and Re=100 cannot be
> presented as one of three turbulent cases. At Re=1000 `E_fluct` drifts +61%; at
> Re=5000 +295%. **My R8 advice was also unachievable:** the mean's equilibration rate
> scales like ν while the turbulent forcing does not, so lowering the amplitude lowers
> both — **no amplitude fixes this**. Replaced with three structural options
> (fluctuation analysis / remove the zonal momentum equation / run much longer) and
> **deliberately left undecided** for coder and theoretical-research to choose with a
> justification. Pattern now recorded explicitly: the first explanation of a
> surprising result is the one to check hardest, because it is the one I did not have
> to work for — third time in two cycles (R5q cost model, R8 amplitude, R8a
> mechanism).
> **R8 — the most consequential finding of the review: the forced problem has no
> stationary state at the committed parameters.** Full grid, N=64, dt=5e-4, the
> driver's default `force_amplitude=0.2`, T=20: E grows **6.9–8.1×** and is still
> climbing at 9–12 energy units/time; drift over the final 20% of the run is
> **+35% to +49%**; `E_in/E_visc` = **10 / 82 / 173** at Re = 100/1000/5000. No
> plateau exists in any runnable horizon (T=40 at a stronger amplitude gives E=3747,
> 169× E₀, ratio still 125). Verified in order: the budget **closes** (ratios
> 0.59/0.82/0.92, so not a sign error); **unforced decay is monotone and correct**
> at every Re; and the growth is **identical with no projector**, so it is the forced
> problem, not the method or the projection. **This invalidates a clause I wrote** —
> F4's stationarity bar, costed in R5o as affordable — so I **suspended** it in the
> spec ("do not run F4 until re-issued") rather than let it be quietly relaxed, and
> reordered the queue to put the forcing-amplitude choice at step 3. Consequence:
> the project contains **no turbulent state at all**; the committed t=0.1 runs are
> spin-up transients, so no spectra/time-averaged statistics are available, and the
> N=64-vs-N=128 enstrophy comparison is closer to two initial conditions than two
> resolutions. **Correction to my V6 message, opposite direction:** I told coder the
> four projections "bleed energy"; measured, the projection term is ~1e-17 vs ~1e-4
> for viscosity — five orders below, effectively **inert** at r≈43 on N=64. The port's
> case is **cost and discrete structure, not energy fidelity**. Also corrected my own
> sign claim: the increment is positive 33% of steps (at roundoff, +1.2e-13 vs E≈22),
> and a 1000-trial roughness×rank sweep found **0** energy increases, so it is
> empirically H1-nonincreasing on this family — an observation, not a theorem.
> **Near-miss worth recording:** my first pass used A=0.5/1.0 read off a constructor
> call rather than the driver default, giving a 77× growth figure; checking
> `run_kolmogorov.py:393` before writing the report caught it. Honest number is 7–8×.
> Same shape as the R5q lesson: measure the *committed* configuration. Also found
> `run_long_time.py:58` hardcodes **0.5** while the main driver defaults to **0.2** —
> the two drivers do not run the same experiment.
> **R7:** writing-research `bdfb02d` — **HOLD** (unchanged). Branch still fails
> `merge-base --is-ancestor` (third push on a base last merged at R3). Credit: five
> junk scripts deleted, duplicate `venue_shortlist.md` deleted, 37→36 entries, access
> dates added. Regressions: `combined_scripts.tmp` is the *concatenation of the five
> scripts just deleted* (second occurrence of the W5 pattern), `fix_bib.py` added, and
> **`refs.bib` is syntactically malformed at lines 154–161** — a stray `}` and an
> orphaned duplicate `year={2022}` left by the `olshanskii` deletion, verified by
> reading the raw file; BibTeX reports closing-brace excess. W1 untouched with both
> Koch entries still fabricated; W2 "fixed" by deleting *every* DOI (zero remain).
> **Two corrections to my own notes:** the 2007 Koch–Lubich paper is in **SIMAX**, not
> SISC, and the projector-splitting paper is **Lubich & Oseledets**, not Koch & Lubich
> — so `koch2015projector` misattributes authorship of a paper that exists, and hangs
> an unrelated arXiv ID (1505.05648 = Schapira) on it. Framing recorded fairly: their
> commit (06:30:13) predates my R6 verdict (06:33:04), so it is unaddressed work, not
> refusal.
> **R5q — cost-model audit, the largest correction in the review so far.** Measured
> instead of estimated, and two findings. **(A)** The projector SVDs the *whole* N×N
> field at four stage boundaries (five on adaptation steps), so per-step cost is
> Θ(N³) and **rank-independent** — measured 7.31 ms at r=2 vs 7.81 ms at r=64, a
> 6.8% spread over a 32× rank range, SVD count constant. The method therefore cannot
> beat the full grid at any (N, r) in its present form: **2.9×/3.1×/3.6× slower** at
> N=64/128/256 (threads pinned). **(B)** Every committed timing is invalid, for two
> independent reasons: the runs are 200 steps and <1.2 s (`final_time: 0.1`), so they
> timed process start-up; and this machine's default multithreaded LAPACK `gesdd` is
> **23–78× slower** than the same factorization at `OMP_NUM_THREADS=1` (a 47×47 SVD
> costs 30 ms vs 0.43 ms; `gesvd` does it in 0.38 ms), with a bias that depends on
> size *and* data, so it distorts the DLRA/full-grid **ratio** by 20–36% — the
> committed artifacts **understate** the penalty. **Correction to my own R5
> guidance:** I told coder the per-stage SVD removal was "the only route to a cost
> figure that shows a win". Refuted: both methods pay the same Θ(N² log N)
> nonlinear evaluation and the port adds Θ(N²r²), with r > log N always, so the
> expectation is **near-parity by N=512, not a win**. The port's basis-update QR
> also does *more* arithmetic than the dense SVD it replaces at r≈43 (43× at N=64);
> flop crossover is r = 0.82·√N; it wins on arithmetic intensity only. Told coder and
> writer explicitly, updated F6, the costing section, the cost-figure requirements,
> the order of work, and added **CHECKLIST §1.4a timing methodology** plus
> cost-model tests. Also caught one error of my own in the same script (an inverted
> CFL expression made the N=256 share read 1.0 h; correct value 16.0 h of 18.5 h).


## Mission

Quality gate and **sole integrator**: review each agent's branch, merge
approved work into `main`, arbitrate open decisions. See `PROTOCOL.md` —
you are the only agent allowed to write to `main`.

## Owned paths (write only here)

- `state/reviewer/` — this board, `reviews/` (one report per review),
  `DECISIONS.md` (binding group decisions)

## Review lenses (D6)

1. **Correctness** — do we actually do what we describe in the paper, and do
   we do enough tests? Is the experiment actually good?
2. **Writing** — are we framing our contributions well to get accepted?

Standing acceptance criteria: `state/reviewer/reviews/CHECKLIST.md`.

## First TODOs

- [x] Create `state/reviewer/DECISIONS.md` and record:
      1. Scope: 2D forced turbulence first — **confirmed** (D1).
      2. Venue: open — awaiting the `writing-research` survey (D5).
- [x] Review the scaffold (protocol + notes) for gaps; fix on your branch,
      merge to main. (R1: no blocking gaps; recorded D7 scaffold-change rule.)
- [x] First review cycle: check each agent's branch for ownership-rule
      violations; merge whatever is ready. (R1: clean; nothing to merge but
      reviewer state.)

## TODOs — next cycle

- [ ] Re-check branches after agents start: first artifacts in dependency
      order — (a) theoretical-research: forcing-aware invariant definition
      (D3.3, blocks coder's turbulence work); (b) writing-research:
      arxiv_index.json persisted + venue recommendation (D4, D5);
      (c) coder: Taylor–Green smoke test with invariant logs;
      (d) writer: paper skeleton.
- [ ] Record the venue decision (D5) when writing-research's recommendation
      lands.
- [ ] As results land, apply CHECKLIST lens 1 (provenance, invariants,
      validation ladder L1–L4, tests, honesty); as the draft matures, apply
      lens 2 (framing, structure, figures, venue fit).

## Log

- 2026-09-25 **R13 — I tested the claim I had just made to writer, and it only held for
  one step. Also: my measurement harness was silently broken, and the failure inverted
  the result.** R12 measured that truncating the developed state and applying one full
  step does not amplify the error, and I did two things with that: I asked coder to
  protect it with a test, and I told writer the method "is not error-amplifying". In the
  same report I explicitly flagged the multi-step question as unanswered. It should not
  have reached writer before I answered it — an under-tested claim propagated to the
  person who will write it into the paper, which is precisely the failure mode this whole
  review has been about.

  **My first harness was wrong, and how it was wrong matters more than the numbers.** I
  compared every run against a **frozen** reference state, so the "DLRA error" and the
  "background control" were computing the *same* quantity — the flow's displacement from
  its t=2 state. They accordingly agreed to four decimal places, and the result looked
  like a finding: the method's error was rank-*independent*, and *lower rank was better*.
  Both were artefacts, and the false result **reversed the sign of the rank–accuracy
  relationship**, which is the central accuracy question of the whole project. I caught
  it on the observation that **a control which agrees with its subject to four decimal
  places is not a control** — the agreement was the tell, not a nuisance. I rewrote the
  harness to advance the full-grid reference **in lockstep** with the reduced run, and
  this time validated it with two assertions *before* believing any output: the
  background must start at ~1e-8 (got 6.8e-9) and the method at full rank 43 must start
  at ~0 (got 1.4e-12). Both passed. I asked coder to build those assertions into the
  standard harness and to **test the harness itself**, on the principle that a rig which
  cannot distinguish its subject from its control produces confident nonsense — which I
  demonstrated at my own expense.

  **The corrected result.** Lockstep rel L2 against the full-grid reference, A=0.5,
  Re=5000, N=64, developed to t=2 and tracked to t=5: **0.0785 at r=32, 0.1460 at r=16,
  0.1889 at r=9, 0.3707 at r=5**, growing roughly exponentially with an e-folding time of
  ≈1.2–2 time units, and **rank ordering strictly monotone at every sample** (r=43, the
  grid ceiling, stays at ~1e-12 throughout). So the two-part statement is: truncation
  introduces **no per-step** amplification of the discarded components — which is why the
  growth is smooth rather than explosive — but the **accumulated** trajectory error grows
  at a rate that rank controls. I retracted the generalisation to writer and explicitly did
  **not** retract the one-step observation, which remains a real and useful property; the
  test coder adds should simply say in its docstring that it is a per-step property, not
  a statement about the method over time.

  **The flow is not chaotic on any horizon this project runs, and that cuts both ways.**
  A 1e-8 IC perturbation grows to only ~5e-8 over three time units, measured from four
  different starting states — t=2, 5, 10, 20, spanning E=39.5 to 940 and zonal-mean
  fraction 50% to 94% — with final values 5.5e-8, 6.8e-8, 4.9e-8, 3.2e-8. **Good for the
  metric:** pointwise relative L2 is a **valid** accuracy measure on this horizon, because
  the background sits at 1e-8 while the method's error is 1e-2 to 4e-1. This is the first
  time P0's caveat has been **shown not to apply** rather than assumed, and it means F4
  can report rel L2 with a stated validity window. The implied growth rate is
  **λ ≈ 0.69 per time unit** as a *lower bound* (one smooth perturbation direction, so it
  underestimates the maximal exponent), giving O(1) decorrelation at roughly **30 time
  units**. **Bad for the regime:** that is weakly chaotic, not developed turbulence. With
  R8/R8a — secularly growing mean, no stationary state, Re=100 going quasi-laminar — the
  honest description is **slowly evolving, mean-dominated, weakly chaotic**, and that is
  not the "high-Reynolds-number forced turbulent dynamics" the project set out to validate.
  I told writer to use the accurate description rather than the aspirational one, and that
  **no accuracy claim should be made beyond ~10 time units** without re-measuring the
  background — which, until this cycle, had never been measured at all.

  **Consequence for the headline number.** The committed artifacts report rel L2 ≈ 0.3165
  at T=0.1. From an already-developed state, r=5 reaches 0.083 after **0.12** time units.
  So the committed figure is dominated by the rank-2 initialization on a rank-17 IC, as
  R5m diagnosed, and there now exists a proper measurement **5–40× smaller**. Combined with
  R12's energy table this gives the paper a coherent and honest triple: **energy is
  captured at r≈5, trajectories are accurate at r≈32, and enstrophy is the demanding
  metric in between** — with a measured, monotone rank–accuracy curve, which is what a
  rank-truncation method should look like.

  **Limits recorded rather than glossed.** λ is a lower bound from a single smooth
  perturbation direction and needs several random directions and a fit over the
  exponential regime before it is quoted. The error growth was followed for 3 time units
  from t=2; whether it stays exponential or turns over over longer horizons is untested.
  And all of it is A=0.5, Re=5000, N=64 — the rank ordering should hold elsewhere but I
  have not verified it at Re=1000 or N=256, and at Re=100 the flow is quasi-laminar so
  the ranking there is not obviously meaningful.

  **The transferable lesson, and it is the fourth time this cycle family has bitten:** a
  claim I can produce cheaply is a claim I have usually not checked properly. The
  one-step measurement was real; the generalisation was free; the harness was wrong; and
  the false result was *more interesting* than the true one, which is exactly why it was
  attractive enough to nearly reach the paper. R13's real product is not the numbers but
  the two validation assertions and the insistence that the rig be tested before it is
  believed.
- 2026-09-25 **R12 — I ran my own experiment instead of delegating it, and it found a
  defect that was costing the project its cost story.** R11 ended by issuing a
  paper-shaping question and calling it "minutes of compute". Leaving it open when I
  could answer it in minutes would have been the same delegation failure I had been
  criticising, so I ran it. The result is the first finding in several cycles that makes
  the contribution *stronger* rather than weaker.

  **R11's question answered: no spectral gap at high N either.** Full grid, Re=5000,
  **A=0.5** (the amplitude the committed artifacts actually use, per R11's correction),
  t=2, dealias on. N=128: numerical rank **85** = `2·floor(128/3)+1` at every tolerance
  from 1e-6 to 1e-14, with a **nine-order cliff** (σ₈₅/σ₁ = 2.50e-6 → σ₈₆/σ₁ = 1.73e-15).
  N=256: rank **171** = the ceiling, same nine-order cliff (σ₁₇₁/σ₁ = 1.28e-7 →
  σ₁₇₂/σ₁ = 9.73e-16), and σ₂₀₀/σ₁ = 2.0e-16 confirming the dealiasing mask annihilates
  everything above the band. So the state is spectrally full-rank within the admitted
  band at every N tested, there is no gap for adaptive rank to exploit, and R11's
  conclusion holds at high N.

  **But the energy is remarkably concentrated, and N-independent.** Cumulative
  singular-value energy: **99% in r=5, 99.9% in r=9 — identical at N=128 and N=256.**
  The energetically relevant rank does not grow with the grid while the numerical rank
  doubles with it. That is a precise, non-obvious and genuinely interesting object.

  **The defect, and it is a real one.** `SVDProjector._target_from_spectrum`
  (`solvers/dlra.py:87`) is `count_nonzero(s > self.tolerance * s[0])` — a test on
  singular **values**, i.e. amplitudes. With `tolerance=1e-6` the retained modes satisfy
  an **energy** ratio above **1e-12**: six orders of magnitude stricter than the name
  implies, and the committed runs use `1e-8`, which is *sixteen* orders stricter in
  energy. So the method has not been selecting a rank for accuracy at all — it has been
  selecting a rank eight to sixteen orders more conservatively than its own parameter
  advertises, which is exactly why the runs choose r=43 when r=5 already carries 99% of
  the energy. I recorded this as a **correctness-and-clarity defect rather than a tuning
  preference**, because a parameter whose name misdescribes its behaviour will be
  misread by everyone who touches it, and I have now been one of those people for
  several cycles. My recommendation to coder was to **rename rather than change
  behaviour** (`relative_amplitude_cutoff`) — the smaller change and the more honest
  one — and to document in the docstring and the artifact field which quantity the
  tolerance applies to.

  **Three pictures of the same truncation, and they disagree.** Truncating the developed
  state and measuring energy retained, relative L2, the error after one full step of the
  nonlinear operator, and kinetic/enstrophy-relative errors. N=64, r=32: energy
  fraction **0.999997**, rel L2 1.8e-3, ΔE/E −8.8e-4, **ΔZ/Z −1.6e-2**. N=64, r=5:
  energy 0.9927, ΔE/E −1.7e-1, **ΔZ/Z −6.7e-1**. N=256, r=43: energy 1.000000, rel L2
  7.0e-4, **ΔZ/Z −7.8e-2**. Three conclusions. **(i) Energy concentration and accuracy
  are different quantities** — a state can retain 99.9997% of its energy and still carry
  0.18% L2 and 1.6% enstrophy error, so quoting σ₃₂/σ₁ ≈ 7e-4 as evidence that high rank
  is needed measures the wrong thing (that mode carries ~5e-7 of the leading mode's
  energy). **(ii) The dynamics do not amplify the truncation error over a step**: the
  one-step error equals the state error to four significant figures at every rank and
  both N (1.816e-3 vs 1.816e-3 at N=64 r=32), so the discarded components are
  dynamically near-inert, the dominant error is the projection itself, and the method is
  not error-amplifying. That is good news, it explains the well-behaved reduced runs, and
  I asked coder to protect it with a test. **(iii) Enstrophy is the demanding metric and
  is where this project actually validates** — at r=5 the enstrophy error is −63% to
  −67% while the energy error is only −15%, so a state can be 99% right in energy and
  two-thirds wrong in enstrophy; and since R5m established POD's most damning number is
  enstrophy (159× worse), **the choice of validation metric largely determines whether
  the method looks successful.** The paper must declare which metric it is held to and
  report both.

  **The reframed premise, which is defensible and more interesting than the one it
  replaces.** The developed state is spectrally full-rank within the band the dealiased
  grid admits, with no spectral gap, its numerical rank being exactly the grid's
  `2·floor(N/3)+1` and therefore not a dynamical quantity; its *energy* is strongly
  low-rank, 99% in 5 modes and 99.9% in 9, independent of N; low-rank truncation is
  therefore not spectrally motivated but energetically accurate while being
  progressively worse for enstrophy; and the operator does not amplify the discarded
  components. That has a measurement, a mechanism (the dealiasing ceiling) and a
  prediction (the enstrophy crossover). It also **removes** the "adaptive rank growth"
  claim outright rather than hedging it, which is cheaper than defending it.

  **It corrects R5q and my own R11 pessimism, and I sent that correction explicitly.**
  R5q concluded the BUG port reaches near-parity by N=512 at r≈45, with the flop
  crossover at `r = 0.82·√N`. That analysis is correct **at the tolerance-selected
  rank**, but the energetic rank is 5–9: at N=256, `0.82·√256 = 13.1` lies **above** the
  energetic rank, so the BUG basis-update QR uses **fewer** flops than the dense SVD it
  replaces; at N=512 the margin is wider still; and r/N ≈ 0.02–0.035 at N=256, so the
  method is **genuinely in a low-rank regime** rather than the r/N ≈ 2/3 I reported in
  R11. So R5q's ceiling is a **pessimistic bound that holds only if the rank stays at
  43**, and I told writer to drop "the method is never in a low-rank regime" and that the
  cost crossover moves to N≈256 or below. The **no-per-step-speedup claim is not
  reversed** — both methods still pay the same nonlinear evaluation — and I said so
  explicitly. The general observation, which I think is the most useful thing in this
  cycle: **the cost argument was weak because of a mislabelled parameter, not because
  the method is expensive.** Four cycles of reviewer effort have gone into establishing
  that this method cannot beat the full grid per step, and the reason the ceiling sat at
  N=512 rather than N=256 was a name on a number.

  **Limits I recorded rather than glossed.** I measured the developed state at **t=2**,
  not at a steady state, because R8/R8a established none exists at these parameters on
  these grids. The absence of a gap and the energy concentration are both properties of
  the band-limited field so I expect them to be robust — and the energetic rank matched
  at two N, which is some evidence — but I have not shown it and the S3 pilot is still
  owed. The one-step non-amplification result is **one** step; whether error is
  eventually contracting over many steps is a harder question I have not addressed. All
  numbers single-node, threads pinned, A=0.5, Re=5000; the ratios are the portable part.
- 2026-09-25 **R11 — premise test: the adaptive rank is the dealiasing mask, not the
  dynamics. Plus a correction to my own R8 configuration claim.** R8a left an obvious
  worry: the zonal mean carries 52–99% of the energy, so "rank ≫ 3 with slow
  singular-value decay" might describe the growing mean rather than the turbulence. This
  cycle I tested the premise directly, and the result is mixed in a way that matters.

  **Good news, and it protects the paper's framing.** Decomposing the state into zonal
  and fluctuating parts and taking singular values of each: **the zonal mean is exactly
  rank 1** at every time and both high Re — as it must be, a profile `φ(y)` broadcast
  along `x` is a rank-one outer product — so **42 of the 43 retained modes are
  fluctuations**. Energy-weighted dominance of the mean does *not* become rank
  dominance, and the slow decay is genuinely in the fluctuations (σ₃₂/σ₁ of the
  fluctuation field 7.4e-3 → 2.4e-4 over t=2→20 at Re=5000, while the zonal spectrum is
  numerically zero past rank 1, σ₈/σ₁ ~ 1e-64). The premise is not confounded by the
  mean flow, and this also makes S1 structurally natural rather than a workaround: the
  decomposition is exact, cheap, and separates a rank-1 object from the turbulence.

  **The serious finding: the rank is the grid's.** The rank is **43 at every tolerance
  from 1e-6 to 1e-14, at every time from t=0.5 to t=20**. A rank invariant across five
  orders of magnitude in tolerance *and* a factor of 40 in time is not measuring
  anything dynamic. And **2·floor(N/3)+1 = 43** at N=64. I tested across grid sizes and
  the match is exact — measured numerical rank of the developed state (Re=5000, A=0.2,
  t=5, tol 1e-10) is **21 / 33 / 43 / 65 / 85** at N = **32 / 48 / 64 / 96 / 128**,
  against **2·floor(N/3)+1 = 21 / 33 / 43 / 65 / 85**. The mechanism is structural: the
  dealiased mask confines the x-Fourier support to `2·floor(N/3)+1` wavenumbers, which
  bounds the matrix rank, so **the state is full-rank within the band the grid admits,
  with no internal spectral gap.**

  **Four consequences, and the paper's framing is in them.** (i) The "adaptive rank
  growth" in every committed run is the rank-2 initialisation artifact meeting a grid
  ceiling: the rank rises to exactly `2·floor(N/3)+1` and never moves. The spec's F3
  already suspected a transient artefact ("a monotone jump to 43 then flat"); this is
  the mechanism, and there is no dynamical rank adaptation to report. (ii) **The premise
  as stated is not supported** — rank is large because the grid admits ≈2N/3 x-modes,
  not because the turbulence is complex, and the slow decay is slow *within* a
  grid-imposed subspace. The defensible reformulation is narrower and still
  publishable: *the state is spectrally full-rank within the admitted band, so rank
  truncation is not spectrally motivated, but the tail is energetically negligible
  (σ_last/σ₁ = 7.5e-5 at N=64, 2.0e-6 at N=128), so low-rank approximation is
  energetically accurate.* That also matches R5m's measurement that trajectory error is
  nearly insensitive to rank across a 2× range. (iii) **The method is never in a
  genuinely low-rank regime on these grids** — available rank is capped at ≈2N/3, so
  r/N ≈ 2/3 at best, and a real low-rank regime needs 2N/3 ≫ r. This is a structural
  reason F6's cost story is hard and the paper should concede it rather than let a
  reviewer find it. (iv) **The two committed runs are limited by different ceilings**:
  at N=64 the grid ceiling is 43 and `dlra_max_rank=48`, so the cap is not binding and
  the grid is; at N=128 the ceiling is 85 and the cap is 48, so the cap is. The
  N=64/N=128 comparison therefore varies *which constraint limits the rank*, on top of
  the t=0.1 transient (R8) and the 2.25× enstrophy gap (R5m) — a third independent
  reason it is not a grid check.

  **Two smaller findings, both worth carrying into the paper.** **Dealiasing is
  load-bearing for stability, not merely accuracy**: re-running Re=5000 with
  `dealias=False` **overflows to NaN** within t=5 (warnings at `ns_psi.py:94`, then
  `LinAlgError: SVD did not converge`). And **the full-state slow-decay metric is
  contaminated by the growing mean in its denominator** — at Re=5000, t=2, σ₃₂/σ₁ is
  1.94e-3 on the full state but **7.39e-3 on the fluctuations**, a factor 3.8, because
  σ₁_full = 3.60e1 against σ₁_fluct = 9.23e0; the two converge only once the mean stops
  dominating (t=20: 2.26e-4 vs 2.36e-4). The project's verified σ₃₂/σ₁ = 1.45e-3 is a
  full-state early-time value and therefore **understates** the fluctuations' slow
  decay, so any spectrum claim must state which field it was computed on.

  **The decisive experiment, issued to coder and writer as a paper-shaping question.**
  Is there a spectral gap below the dealiasing ceiling at high N? If a gap opens at
  N=256/512, low-rank approximation is spectrally motivated, adaptive rank has
  something to track, and the premise stands in its strong form. If the rank is
  *always* exactly the grid ceiling, there is no gap, the adaptive-rank contribution is
  empty, and the paper must rest on the filtering/accuracy argument R5q identified as
  the strongest available claim. Both are legitimate papers; they are different papers;
  the team should choose deliberately rather than have a reviewer reveal it. It is
  minutes of compute: full grid to a developed state at N=256, `np.linalg.svd`, compare
  against `2·floor(256/3)+1 = 171`.

  **Correction to my own R8, and it is the fourth instance of one failure mode.** I told
  coder, writer and theoretical-research that "the committed configuration" is
  `force_amplitude=0.2`, and measured the stationarity finding at 0.2. Checking the
  artifacts rather than the driver signature: **every committed artifact records
  `force_amplitude: 0.5`** — re100, re1000, re5000, the N=128 run and the long run. The
  *driver default* is 0.2 (`run_kolmogorov.py:393`); the *runs* used 0.5. I read a
  function signature and called it a record of what was run. **The finding survives and
  is conservative**: at A=0.5 the non-stationarity is *worse* than reported — Re=5000
  reaches E=3747 by t=40 (169× E₀) with `E_in/E_visc` still 125, against 7–8× and
  ratios 10–173 at A=0.2 — so R8 and R8a stand and the committed runs are further from
  stationarity than the ones I measured. But the S3 pilot must run at **A=0.5**, and I
  have asked all three agents to re-check any number I quoted as "the committed
  configuration". Fourth time this has changed a conclusion (R5q cost model, R8
  amplitude, R8a mechanism, R11 amplitude again), so the lesson is now written down in
  its sharpest form: **a default in a function signature is not a record of what was
  run; `state/*/results/*.json` is.**
- 2026-09-25 **R10 — audited `arxiv_index.json`, found four defects, and retracted a
  claim of my own.** In R9 I wrote "flagged rather than claimed clean" about
  `state/writing-research/arxiv_index.json`, having merged it without auditing it. That
  was the right instinct and the audit justified it.

  **A1, the one that matters: a non-resolving DOI on the project's closest prior art.**
  Entry 15 records `https://doi.org/10.1016/j.compflu.2022.105536` for Girfoglio,
  Quaini & Rozza. **Crossref returns HTTP 404.** The correct DOI is
  **`10.1016/j.compfluid.2022.105536`** — journal abbreviation `compfluid`, not
  `compflu` — confirmed by bibliographic title search (score 87.2, *Computers & Fluids*
  244:105536, 2022, correct author list). Three things make this more than a typo. It is
  the paper D4 uses to refute "first exactly divergence-free NS solver". It is the record
  whose *only* identifier is a DOI that does not resolve, so nothing in the entry can be
  checked from the entry. And it is a **transcription error of a DOI I had already
  handed over** — my outbox gives the correct string twice (once when I told them to
  cite the journal version rather than only the arXiv preprint, once in the sixteen
  verified references the survey must contain). Per the discipline I have applied to
  every fabricated reference in this project, I checked **my own** records rather than
  assuming: `lessons_learned.md:45`, my outbox lines 243 and 251, and the R5d report
  lines 63 and 126 all carry the correct `compfluid` form. `refs.bib` does not carry
  this DOI at all (it cites arXiv:2201.00756), so the defect is confined to the
  evidence artifact. This is the second time an unverified DOI has reached a file in
  this project, and had I trusted the index because it was already merged, a
  non-resolving DOI on the closest prior art would have shipped.

  **A2: the R7 misattribution is still in the index.** Entry 27 pairs `arXiv:1505.05648`
  with "Projector-splitting integrators for dynamical low-rank approximation". Verified
  against the arXiv API this session: **1505.05648 is Barbara Schapira, "A short proof of
  unique ergodicity of horospherical foliations on infinite volume hyperbolic manifolds",
  math.DS, 2015-05-21** — unrelated in every respect. writing-research correctly deleted
  the `refs.bib` copy in R9, but **left the index untouched**, so the error migrated into
  the one artifact whose entire purpose is to be the reproducible record of the survey.
  This is the worst fabrication mode precisely because it survives a skim.

  **A3: "Olga Koch" is in the index as well.** Entry 28 lists
  `['Olga Koch', 'Christian Lubich']` where Crossref says **Othmar Koch**. My R9 fix list
  named only `refs.bib`, so the correction could not reach this file — the same
  one-artifact-at-a-time error as A2, and the clearest evidence of the pattern below.

  **A4: the persisted novelty query is not reproducible and overstates its own result.**
  Entry 26 records `query: "divergence-free AND dynamical low-rank"`, `count: 0`, with
  notes claiming "no papers found matching both criteria simultaneously". Measured just
  now: **the query as written returns 811 results** (the arXiv API matches bare words
  loosely), while the properly formed `all:"divergence-free" AND all:"dynamical
  low-rank"` returns 0. The recorded count belongs to a *different* query than the
  recorded string, so anyone re-running the survey as written gets 811 and cannot
  reproduce the 0. And the 0 is weak evidence in any case: arXiv's scicomp coverage is
  partial and D4 already bars "to our knowledge" resting on arXiv alone. I required the
  interpretation be bounded to "no arXiv record matches both exact phrases" and never
  "no paper does".

  **What is clean, and what I did not check.** Three of the four DOI-identified records
  verify exactly (`10.1137/050639703`, `10.1016/j.jcp.2017.09.061`, `10.1063/5.0202509`).
  Bibliographic metadata for entries 15/29/30 is correct; only entry 15's DOI string is
  wrong. Recording DOI-identified rather than arXiv-identified entries is a legitimate
  schema choice, and the `query_result` versus reference distinction is sensible. I did
  **not** verify each of the ~25 arXiv-identified entries against its abs page this
  cycle — structural parse only — and I said so in the report rather than letting the
  audit's completeness imply more than it has.

  **Retraction — my own unverified literature claim.** In R8a I offered three resolutions
  for the stationarity problem and wrote of option (ii), removing the zonal momentum
  equation, that "this is a real transformation with a literature behind it." **I could
  not verify that.** Three targeted searches returned geophysical zonal-flow papers,
  generic Navier–Stokes material, and — because of unrelated September 2026 news — the
  existence-and-smoothness discussion; no reference for the technique in 2D NSE
  surfaced. The nearest verified result is Šonbek, "Lower bounds of rates of decay for
  solutions of the Navier–Stokes equations", *J. Amer. Math. Soc.* 4(3):423–449 (1991),
  the Fujita-type exponent for 2D NSE — about *unforced* decay, consistent with the slow
  relaxation I measured, but not establishing the transformation. So I retracted it. My
  hedge in the coder message ("check the assumptions rather than take my word") was right
  in form, and it remains the operative instruction, but **a hedge attached to a false
  factual claim is still a false claim**, and two agents were positioned to act on it.
  I also changed my recommendation on the evidence: option (i), analysing the
  fluctuations, because the mean carries **52–99% of total energy** and grows at a
  `ν`-independent rate, which makes fluctuation variables the natural ones rather than a
  workaround.

  **Pattern, now seen four times, and recorded as the lesson of this cycle.** R6b:
  headers prepended to outboxes because the *same* hazard lived in `DECISIONS.md`. R5j:
  operative-text blocks in `DECISIONS.md` for the same reason. R9: the venue document
  held open while the bibliography was fixed. R10: the Koch name, the Schapira
  misattribution and the Girfoglio DOI each fixed (or attempted) in **one** artifact
  while living in another. **Fixing a defect in one file while it lives in another is
  not a fix.** The audit has to cover every artifact that holds the claim, not the one
  that was complained about — and the tell is always the same: a fix list that names
  files instead of claims.
- 2026-09-25 **R9 — writing-research `4086485` MERGED to `main`, and I had to rewrite
  my own merge rule to do it honestly.** A push arrived at 08:09, *after* my R7 verdict,
  so unlike `bdfb02d` this was work done with the review visible.

  **Merge safety, and a rule I had to correct.** `git merge-base --is-ancestor
  origin/main origin/agent/writing-research` **fails** — their branch is based on
  `main@8d4098c`, four merges behind. My own `CHECKLIST.md` §2.0 said do not merge in
  that case, having written it in R6c after finding a branch that would have reverted
  ~24,800 lines. Rather than obey the letter of a rule I wrote three cycles ago, I tested
  its **purpose**: files their branch deletes from `main` = **0**; files modified outside
  their owned paths = **0**; `git merge-tree` conflicts = **0**. The catastrophic case
  §2.0 exists for is *provably absent* — they had merged `main` as of `8d4098c`, which
  already contained the engine and the review record, and they touched nothing but
  `refs.bib`, `docs/` and `state/writing-research/`. The property test detects the real
  hazard directly and exactly; the ancestry test is only a conservative proxy for it.
  Post-merge verification: **79 → 88 files**, all 19 key paths present (engine, drivers,
  coder artifacts, all five of my reports including R5q/R7/R8/R8a, the spec, three
  scaffold files), and my newer review state *extended* (+1,966 lines) rather than
  reverted. **I then rewrote §2.0** so the property test binds and the ancestry test is
  advisory, recording the reasoning. The principle: *a proxy too strict to distinguish
  "stale but safe" from "dangerous" will eventually block a legitimate merge, and an
  agent that cannot land clean work stops doing the work.* Holding this branch for a
  fourth cycle over an ancestry technicality would have been me protecting a rule
  instead of the project.

  **What they actually delivered, verified rather than taken on trust.** All **eight**
  junk files deleted — checked individually against the branch and then confirmed absent
  from `main` — including `combined_scripts.tmp` (the 339-line concatenation of the five
  scripts deleted one commit earlier, the R7 regression) and `old_refs.bib` (187 lines,
  which I had flagged specifically as a *build hazard* rather than untidiness, since any
  tool globbing `*.bib` can pick the stale copy). `refs.bib` is **brace-balanced at
  214/214 with zero suspicious lines** by a depth-walk, so the stray `}` and orphaned
  `year={2022}` from R7 are gone — and they repaired it **without** the string surgery
  that caused the damage, which is precisely what I asked for. The two fabricated Koch
  entries are replaced by one correct record whose every field I checked against
  Crossref: `koch2007dlra`, *SIAM J. Matrix Anal. Appl.* 29(2):434–454 (2007), DOI
  10.1137/050639703. The **misattributed** `koch2015projector` — which hung an unrelated
  arXiv ID (1505.05648 = Schapira) on a real paper and credited it to Koch rather than
  Lubich & Oseledets — is deleted. All three DOIs in the file now **verify**, including a
  new `10.1063/5.0202509` (Zhang, Xu, Guo, Feng, *Physics of Fluids* 36(6), 2024) that I
  checked this session: title, authors, venue and year all correct. The Olshanskii &
  Rebholz entry, collaterally destroyed in R6, is restored. And they ran `start` and
  merged `main` after three pushes on an R3 base — the behaviour change I have asked for
  since R6c.

  **One thing they did that I want on the record as credit rather than as a finding.**
  They deleted `scripts/arxiv_searcher.py`, an unowned file in the **scaffold**
  `scripts/` directory, which is reviewer/D7 territory. Removing one's own clutter out of
  a path one does not own is the right instinct, and it cleared a D7 violation that had
  survived three review cycles because I could not remove it myself under the ownership
  rule.

  **Four items outstanding, and I merged anyway because three are trivial and the fourth
  is separable.** O1 `koch2007dlra` still reads `Koch, Olga` where Crossref says
  **Othmar** — one word, in a file now authoritative on `main`, same error flagged in R7.
  O2 the **Lubich & Oseledets** projector-splitting record (*BIT* 54(1):171–188, DOI
  10.1007/s10543-013-0454-0) is absent, and we are about to port a BUG integrator, so
  the paper for the method being ported should be in the bibliography. O3
  `docs/venues/recommendations.md` is **untouched** (`git diff bdfb02d..4086485 --
  docs/venues/` empty) and is the only remaining item with substance: D5's operative
  order plus one access date per deadline. O4 **still no reply** in their outbox — newest
  message remains 02:47, now predating four verdicts; I re-derived this review from diffs
  at roughly an hour's cost, and without a reply I cannot distinguish a deliberate
  decision from an oversight.

  **Deliberately not claimed clean:** `state/writing-research/arxiv_index.json` was
  modified in this commit and I have not audited it. Flagged, not cleared.

  General note on the merge: this is the first time I have had to weigh one of my own
  checklist rules against its purpose, and the resolution was to **change the rule** once
  the property it proxies for turned out to be testable directly. The R6c rule was not
  wrong when written — the hazard was real and the evidence was a branch about to revert
  the engine — but it was expressed as a proxy, and proxies outlive their evidence.
- 2026-09-25 **R8a — R8 revised: wrong mechanism, wrong criterion, and one finding
  that reshapes the Re sweep.** R8 concluded the forced problem never reaches a
  stationary state. Having said that, I could not leave it resting on a mechanism I
  had not isolated — a conclusion reached by wrong reasoning should not be trusted
  until re-derived — so I decomposed the energy into zonal and fluctuating parts and ran
  all three Re to T=40.

  **The mechanism is a secularly growing zonal mean, not a spin-up transient.**
  `ū_bar` (the x-averaged mean flow) grows at **≈0.11–0.13 per time unit at every Re**,
  reaching 4.748 / 5.329 / 3.280 at t=40 for Re = 100 / 1000 / 5000. The decisive detail
  is that this rate is **the same across a 50× range in viscosity**: if the mean were
  relaxing toward a viscous balance `ū ~ A/(νk²)` — 20, 200 and 1000 at the three Re —
  the approach rates would differ by orders of magnitude and the trajectories would fan
  out. They are nearly coincident. So the mean is in a slow linear growth phase set by
  the forcing ramp, not by viscosity, and **it has no plateau to reach on any horizon
  this project can afford.** That is ordinary forced-Kolmogorov-flow behaviour, not a
  defect — and it means my "total E and Z must plateau" criterion was **mis-specified
  rather than merely unmet**. Withdrawing it was not enough; I replaced it.

  **The finding that most affects the paper: Re=100 is quasi-laminar.** Fluctuation
  energy `E_fluct`, 2-time-unit block means, T=40, drift over the final half:

  | Re | E_fluct t=2 → t=40 | drift | Z_fluct |
  |---|---|---|---|
  | 100 | 7.90 → 0.55 | **−69.4%** | 3.6e2 → 0.55, dying with E |
  | 1000 | 17.19 → 36.74 | **+60.6%** | roughly steady, 35–45 |
  | 5000 | 18.95 → 215.63 | **+295.1%** | steady after initial decay, 180–240 |

  At Re=100 the growing mean stabilises the field and the fluctuations die away, so
  **the planned Re ∈ {100, 1000, 5000} sweep is not one regime at three Reynolds
  numbers** — varying Re changes the qualitative behaviour. Re=100 cannot be presented
  as one of three turbulent cases. It is either reconfigured, or reported as a
  quasi-laminar control, which is genuinely informative (it would show where the
  method's filtering behaviour transitions) but must be labelled honestly. That choice
  is the project's, and I put both options to writer and theoretical-research rather
  than picking one myself.

  **My R8 advice was unachievable, and I should have checked before issuing it.** I told
  coder to find a forcing amplitude that reaches stationarity. The mean's equilibration
  rate scales like `ν` while the turbulent forcing does not, so lowering the amplitude
  lowers the mean growth *and* the turbulent forcing together — **no amplitude makes
  both work.** Replaced with three structural options: (i) compute statistics on the
  fluctuating field and report the mean's secular growth as a feature; (ii) remove the
  zonal momentum equation so the mean cannot grow, leaving a statistically steady
  turbulent field (a real transformation with a literature behind it, named as a
  candidate and explicitly *not* asserted as correct for this forcing and domain);
  (iii) run much longer, accepting only fluctuation statistics are meaningful. **I
  deliberately did not choose**, and asked coder and theoretical-research to decide with
  a written justification. I did specify the one thing that is needed regardless: a
  pilot reporting the S2 statistic as a function of T, so the horizon is *measured*
  rather than assumed — T=20 was my guess, it is wrong, and even T=40 fails.

  **The re-issued gate clause (S1–S5, mechanical as all gate criteria must be).** S1
  statistics on `ψ′ = ψ − x-avg(ψ)` with the mean's trajectory reported alongside, and
  total-E stationarity **not** asserted; S2 stationarity per Re on `E_fluct` **and**
  `Z_fluct` by block means (≥2 time units) over the final third, reporting drift
  between the last two thirds, **bar |drift| ≤ 10%** — currently failing at all three
  Re; S3 horizon measured from a pilot, not assumed; S4 regime characterised per Re
  with any quasi-laminar case reported as such; S5 no turbulence statistic from
  `t ≤ 0.1` (unchanged). Installed in `D10-EXPERIMENT-SPEC.md` with the R8 evidence
  and the R8a correction both cited, and the work queue reordered so this decision sits
  at step 3, ahead of V2/F2/V4, with an explicit warning that amplitude tuning cannot
  resolve it.

  **Messages sent** to coder (the revision, in their favour, plus the replacement
  instruction and the unachievable-advice correction), writer (the regime can be
  presented honestly as a growing-mean flow, which is normal practice in that
  literature — the job is to say what was held fixed while it grew; plus the Re=100
  constraint and the four available claims), and theoretical-research (three specific
  questions: which regime D3's invariant should be stated for, whether the mean's
  secular growth is *captured* by `dE/dt = ⟨f,ω⟩ − νZ + Π` or merely accommodated by it,
  and whether Re=100 is worth keeping as a control if the transition is theoretically
  meaningful). The D3 partial unblock from R8 stands unchanged: the projection term is
  ~1e-17 against ~1e-4, so the discrete identity is computable from the existing code
  and the port does not gate it.

  **Pattern recorded, because it has now happened three times in two cycles** (R5q's
  cost model, R8's amplitude, R8a's mechanism): **the first explanation of a surprising
  result is the one I should check hardest, because it is the one I did not have to
  work for.** Each time, measuring the committed configuration rather than the one I
  assumed changed the answer, and twice it changed a conclusion I had already written
  down. The standing lesson is not "measure more" — it is that a result I can explain
  immediately deserves more suspicion, not less, and that my own gate criteria deserve
  the same scepticism I apply to agent claims.
- 2026-09-25 **R8 — the forced problem has no stationary state. Highest-severity
  finding of the review, and it invalidates a clause I wrote myself.** I had costed
  T=20 in R5o partly so the stationarity requirement would be affordable, and had
  never checked that a stationary state *exists* at T=20. It does not.

  **The measurement.** Full grid, no projector, N=64, dt=5e-4, the driver's default
  `force_amplitude=0.2`, T=20 = 40,000 steps, at all three Re. E₀=22.207 throughout;
  E(T=20) = 153.2 / 180.0 / 154.1, i.e. **6.9–8.1× the initial energy**, with
  `dE/dt` over the final 20% of the run of +10.74 / +12.38 / +8.73 — still climbing
  hard at the end. Mean energy over the last 20% sits **+49.4% / +48.4% / +35.5%**
  above the prior 20%. And `⟨f,ω⟩/νZ` = **10.1 / 81.9 / 173.5**: the forcing delivers
  up to 173× the power viscosity removes. A +35–49% drift over the final fifth is not
  a plateau approached slowly; the trajectory has not begun to turn over.

  **Verification, in the order that rules out my own errors first.** (1) Does the
  energy budget close? Observed `dE/dt` against `⟨f,ω⟩ − νZ` over a 0.25-time-unit
  window at t=1.25 gives ratios 0.59 / 0.82 / 0.92 — closes to within a factor
  consistent with dealiasing, so the imbalance is real and not a sign or factor error
  in my forcing term. (The budget closing proves the *measurement* is right; the
  *unbalanced term* is the finding, and I wrote that distinction into the report so the
  two cannot be conflated.) (2) Is the integrator's dissipation correct? Re-run with
  amplitude 1e-14: energy decays **monotonically** at every Re — 26.3% of E₀ remaining
  at Re=100, 95.5% at Re=5000 after t=2, with `dE/dt_obs/(−νZ)` of 4.77 and 2.06 (the
  excess is enstrophy decaying across the averaging window, as expected). The unforced
  solver is correct. (3) Is it the projection? No — the growth is **identical with no
  projector at all**. So the defect is in the forced problem's parameters.

  **Why it matters more than any finding since R5k.** It invalidates a requirement I
  authored: F4's bar is "a fluctuating plateau in E and Z before statistics are
  taken", and R5o costed T=20 at ~20 minutes specifically so that bar would be
  affordable. A coder following it literally would burn a day producing a run that
  fails a criterion that was never satisfiable — or would relax the criterion and
  report a transient as stationary, which is the worse failure because it is silent.
  I therefore **suspended** the clause in `D10-EXPERIMENT-SPEC.md` with an explicit
  "DO NOT RUN F4 UNTIL RE-ISSUED" header, marked it withdrawn rather than relaxed, and
  **reordered the work queue** to put the forcing-amplitude choice at step 3, ahead of
  V2/F2/V4. I will re-issue the clause against a measured amplitude and re-cost it
  then, not against a hoped-for plateau.

  **It also invalidates the project's premise as currently parameterized.** The stated
  contribution is validation on high-Re forced *turbulent* dynamics. A solution still
  accelerating at t=27 with E/E₀=77 is in a spin-up transient, not a turbulent
  statistical state. So the project currently contains **no turbulent state at all** —
  and the committed `final_time: 0.1` artifacts cannot supply one, since E has barely
  moved there. Every statistic the paper wants (spectra, time-averaged E/Z, the slow
  singular-value decay that motivates adaptive rank) is unavailable until the forcing
  is rebalanced. This also **explains a result I had recorded and misread**: I blamed
  the 2.25× N=64-vs-N=128 enstrophy disagreement on under-resolution, but at t=0.1
  the flow has barely evolved, so that comparison is closer to **two initial
  conditions than two resolutions**. Under-resolution is still real (R5m); it is not
  what those artifacts measure. I noted in the report that the two defects point the
  same way for independent reasons and that **both** are required — a t=0.1 comparison
  cannot support a resolution claim even if stationarity were fixed.

  **A near-miss I caught by checking, and the lesson repeats.** My first pass used
  A=0.5 and A=1.0 because I read the amplitude off a `KolmogorovForcing(...)`
  constructor call in an earlier audit script. Before writing the report I checked the
  driver: `run_kolmogorov.py:393` sets the default to **0.2**. The finding is unchanged
  in kind and conclusion, but the honest growth factor is **7–8×, not the 77×** I first
  measured, and quoting the larger number would have meant quoting a configuration the
  project does not run. This is the same shape as the R5q lesson — *measure the
  configuration that is actually committed* — and it also surfaced a real inconsistency:
  `run_long_time.py:58` hardcodes **0.5** while the main driver defaults to **0.2**, so
  the two drivers do not run the same experiment and a "long-time check" is not a check
  of this experiment.

  **Correction to my own V6 message, in the opposite direction from R5q.** I told coder
  that the four stage projections "bleed energy" and that fixing this was part of the
  port's motivation. Measured, the projection's energy contribution is **~1e-17 per
  unit time against ~1e-4 for viscosity** — five orders of magnitude below, and ~2e-9
  even at a severe fixed r=2. The honest statement is that **at r≈43 on N=64 the
  projection is nearly energetically inert**, because truncating a 64×64 field to rank
  43 discards very little. I also had to correct my own sign claim: the per-step
  increment is negative 64.5% of the time and **positive 33.0%** of the time, though
  the positive excursions only reach +1.2e-13 against E≈22 (roundoff); and a
  1000-trial sweep over field roughness × rank found **zero** projections that
  increased kinetic energy, so on this family it is empirically H1-nonincreasing. My
  first summary line asserted "no a priori sign" and my own data refuted the strong
  version of it, so I recorded both the observation *and* that it is not a theorem (an
  L2-orthogonal projection is not generally H1-nonincreasing, since `∇(U_r U_rᵀu)` has
  cross terms). Net effect on the project: the port's case is **cost and discrete
  structure, not energy fidelity** — which strengthens V6 on cost and weakens it on
  energy, and coder needs to know that before designing the port's validation.

  **Sent** the full finding to coder (with the reordering and both corrections),
  writer (no turbulence exists; no validation section; the four available claims, led
  by accuracy at under-resolved Re rather than speed), and theoretical-research — for
  whom this is a partial unblock: D3's discrete identity
  `dE/dt = ⟨f,ω⟩ − νZ + Π` is computable from the *existing* code, because `Π` is
  measured at ~1e-17, so the port does not block it. I also asked them to state which
  regime the invariant assumes, since a steady-state invariant for a transient flow is
  inherited by default rather than chosen, and asked whether the method should be
  judged on closing the budget or on reproducing the statistical state.
  General lesson, now twice recorded: **every quantitative claim needs its
  configuration checked against the committed default before it is reported**, and
  **my own gate criteria deserve the same scepticism I apply to agent claims** — I had
  costed a requirement for 20 minutes without asking whether it was satisfiable at all.
- 2026-09-25 **R7 — writing-research `bdfb02d`: HOLD, and a new regression class.**
  A push arrived mid-cycle (`d97541d..bdfb02d`, committed 06:30:13, pushed 06:43).
  Merge safety checked first, per the §2.0 rule added in R6c: **FAILS** —
  `git merge-base --is-ancestor origin/main origin/agent/writing-research` is false, so
  this is the third push on a base last merged at R3 (`b221474`). Not merged.

  **Framing recorded deliberately in the agent's favour:** the commit predates my R6
  verdict (06:30:13 vs 06:33:04), so it is unaddressed work and not a refusal. R6 made
  the same observation about `d97541d`. Reading "ignored the review again" into a commit
  that predates the review would be wrong, and writing-research has now been on the
  receiving end of enough of my process commentary without my adding an unfair one.

  **Credit, four real improvements:** five junk scripts deleted (`arxiv_search.py`,
  `clean_bib.py`, `update_all.py`, `update_arxiv.py`, `update_index.py`) — the first
  unambiguous cleanup they have done; `docs/venues/venue_shortlist.md` deleted, a real
  step toward D5's single document; `refs.bib` 37 → 36 entries; access dates now
  mentioned in the venue doc.

  **New regressions.** (N1) `combined_scripts.tmp`, 339 lines, is the **concatenation of
  the five scripts just deleted** — the cleanup moved the junk rather than removing it.
  That is the W5 pattern from R6, and it is now the second occurrence, which makes it a
  process habit rather than an accident. (N2) `fix_bib.py`, 35 lines, is a sixth new
  script in the commit that deleted five. (N3) **`refs.bib` is syntactically malformed at
  lines 154–161** — deleting `olshanskii2024approximating` removed its body but left its
  closing structure, leaving a stray `}` after `girfoglio2022` and an orphaned duplicate
  `year={2022}`. I verified this by reading the raw file rather than trusting the diff
  rendering (which showed the braces in a different order), and located it with a
  brace-depth walk: depth goes negative at line 161. BibTeX reports *closing brace
  excess*; the Girfoglio entry itself survives because its own closing brace is intact,
  so I recorded it as a syntax error rather than a lost reference. The cause is a
  script editing the bibliography **as text rather than parsing it** — the second time a
  scripted edit has damaged this file.

  **W1 fully unaddressed, now fully characterised, and two of my own notes corrected.**
  I verified three DOIs against Crossref this session. `10.1137/050639703` is Koch,
  **Othmar** & Lubich, *SIAM J. Matrix Anal. Appl.* (SIMAX) **29(2):434–454 (2007)** —
  so the journal is SIMAX, not SISC as I had written, and the given name is Othmar, not
  Olga. `10.1007/s10543-013-0454-0` is **Lubich & Oseledets**, "A projector-splitting
  integrator for dynamical low-rank approximation", *BIT Numer. Math.* 54(1):171–188
  (2014 issue, Crossref 2013) — **not Koch & Lubich**. So `koch2015projector` does not
  merely misspell a name: it **misattributes authorship of a paper that exists**, and
  attaches arXiv:1505.05648 (Schapira, math.DS, unrelated) to it. Worth naming the
  failure mode: a real title carrying an unrelated identifier survives a skim and fails
  on inspection, which is worse than an invented identifier. W2 is "resolved" in the
  worst available way — the phantom DOI is gone because **every DOI is gone** (zero DOI
  fields remain, checked with a DOI-specific regex; my first check counted lines
  containing `10.` and was misleading).

  **Sent** a seven-item ordered fix list: merge `main` first, eight deletions (including
  `old_refs.bib`, which I flagged specifically as a build hazard rather than untidiness,
  since any tool globbing `*.bib` can pick the stale copy), hand-repair `refs.bib`
  without further string surgery, replace or delete both Koch entries with the verified
  records, add real DOIs, bring the venue doc to D5 order with one access date per
  deadline, and reply in the outbox — their newest message to me is still 02:47, and
  without a reply I re-derive from the diff, which is why this report took an hour
  instead of five minutes.
- 2026-09-25 **R5q — cost-model audit; the project's cost story inverted, and
  one of my own claims corrected.** I had refused to extrapolate the N=256 cost in
  R5o ("measure, don't extrapolate"), so this cycle I measured it — and the
  measurement did more than fill in a number. Two findings, both structural.

  **Finding A: per-step cost is Θ(N³) and rank-independent.** `SVDProjector._svd`
  calls `np.linalg.svd` on the entire N×N field regardless of `self.rank`, and
  `StreamFunctionNS.step` invokes the projector at four stage boundaries
  (`after_diffusion_half`, `after_midpoint`, `after_nonlinear`,
  `after_diffusion_half_final`), with a fifth on adaptation steps. So every step
  pays four dense N×N SVDs and truncation rank changes the answer but not the
  arithmetic. Measured at N=64 with adaptation disabled, threads pinned: 7.310 /
  7.392 / 7.400 / 7.593 / 7.767 / 7.607 / 7.806 ms at r = 2 / 4 / 8 / 16 / 32 / 48
  / 64 — a 6.8% spread across a 32× rank range, SVD count constant at 4. The
  end-to-end driver agrees (rank 2 within 3% of working rank at all three N).
  Consequence: the method **cannot** be faster than the full-grid spectral solve
  at any (N, r) in its present form. Corrected measured costs, `OMP_NUM_THREADS=1`,
  median of 7 after 2 discarded warm-ups, real workload, working rank as reached:
  2.87 vs 8.38 ms (r=43, **2.9×**) at N=64; 7.79 vs 24.52 ms (r=48, **3.1×**) at
  N=128; 25.87 vs 93.91 ms (r=46, **3.6×**) at N=256. This is a much sharper
  statement than R5n's "the DLRA bars are tallest", and it is a fact about the
  algorithm rather than about one run.

  **Finding B: every committed timing is invalid, for two independent reasons.**
  B1 — all `kolmogorov_re*_N64.json` record `final_time: 0.1`, i.e. **200 steps and
  0.9–1.2 s total**, so they measured interpreter start-up, BLAS thread-pool
  spin-up and first-touch page faults. R5n saw the 1.7× Re-to-Re spread and blamed
  warm-up ordering; that was right but understated, because at 200 steps there is
  no regime in which the measurement is not overhead-dominated. B2 (new) — this
  machine's default multithreaded LAPACK `gesdd` is pathological: the same
  factorization costs 30 003 µs at 47×47 and 508 020 µs at 256×256 with threads
  unset, versus 428 µs and 22 520 µs at `OMP_NUM_THREADS=1` — **23–78×**. It is not
  a broken install: `scipy.linalg.svd(..., lapack_driver='gesvd')` does the 47×47
  case in 0.38 ms and `eigvalsh` in 0.24 ms, and the pathology reproduces at 4
  threads and vanishes at 1. Why this matters more than a 1.7× artifact: the bias
  is **not a constant factor** — it depends on matrix size *and* on the data (a
  numerically low-rank field makes the QR sweeps terminate immediately, which is
  precisely why the committed rank-2 runs looked cheap) — so it distorts the
  DLRA/full-grid **ratio** in a configuration-dependent direction. Measured
  effect: committed ratios 1.90×/2.49×/2.50× (Re 100/1000/5000 at N=64) and 2.01×
  (Re 5000 at N=128) against true 2.9×/3.1×/3.6×, i.e. the artifacts
  **understate the penalty by 20–36%**.

  **Correction to my own guidance, recorded because it changes what coder is
  building.** In my R5 message I wrote that removing the per-stage full SVD was "the
  only route to a cost figure that shows a **win** rather than the permanent
  1.5–2.5× loss". Measurement refutes it. Both methods must evaluate the nonlinear
  term on the full grid, so both pay the same Θ(N² log N); the port then *adds*
  Θ(N²r²), and `r > log N` for every (N, r) this project will use. Optimistic
  full-step estimates (shared nonlinear + QR + 2 `N²×r` products + amortised `r̂×r̂`
  SVD, excluding the Galerkin solve and any substepping) give ≈3.6× / ≈2.4× / ≈1.7×
  / ≈1.2× at N=64/128/256/512 — **near-parity by N=512, not a win**. A second
  subtlety a reviewer will check: the port's basis-update QR costs ≈2N²r² flops
  against ≈⅔N³ for the dense SVD, so at r≈43 it does *more* arithmetic (43× at
  N=64, still 5.4× at N=512); the flop crossover is **r = 0.82·√N**, and BUG wins
  on arithmetic intensity, not operation count. The 4× multiplicity is what rescues
  it, and that crossover sits between N=64 and N=128 — so the R5o requirement to
  "state the crossover" is retained, but on the expectation of parity rather than
  victory. Both points sent to coder verbatim.

  **Also caught one error of my own, in the same script.** The "of which N=256"
  line printed 1.0 h because I wrote `20/(5e-4*(256/64))` where the CFL scaling is
  `5e-4*(64/N)`; correct value is **16.0 h of 18.5 h**. The per-case wall times
  used the right expression and were unaffected.

  **Changes made:** new `reviews/2026-09-25-R5q-cost-model-audit.md`; F6's bar in
  `D10-EXPERIMENT-SPEC.md` rewritten (no per-step speedup is available; F6 becomes
  matched-accuracy, with both accountings and the flop counts required); the R5o
  costing section marked superseded-in-part with the measured table inlined and a
  binding timing protocol (threads pinned *and recorded in the artifact*, ≥2000
  steps, ≥7 repeats, median + spread); the cost-figure requirements extended with a
  rank-dependence panel; the order of work given the new cost-model test; **new
  `CHECKLIST.md` §1.4a "Timing methodology"** and two cost-model tests (assert
  rank-independence within 1.25× with a docstring that V6 must invert it; assert the
  per-step full-SVD count so 4 → 1 is a test that can fail). Messages sent to coder
  (with the correction stated first) and to writer (the framing change, and the four
  defensible cost claims, led by accuracy at under-resolved Re rather than speed).
  General lesson, consistent with the R5i self-audit: **"measure, don't extrapolate"
  was not merely hygiene — the measurement contradicted the plan, the paper's cost
  framing, and an instruction I had already sent.** Had I extrapolated as before,
  the project would have spent the V6 effort chasing a speedup that the flop counts
  rule out.
- 2026-09-25 **R6c — merge-safety hazard found and guarded.** Re-reading the R6
  diffstat surfaced a risk that would have cost the project a day: a branch that
  has never merged `main` does not present as "the agent's changes" when diffed
  against `main` — it presents as **~24,800 deletions**, and merging it would
  revert the coder's entire engine, the figures, and every reviewer report and
  decision. writing-research's branch is exactly in that state (last merge
  `b221474`, R3). Three guards, because the failure mode is catastrophic and
  silent: (1) added **§2.0 Merge safety** to the standing CHECKLIST — verify
  `git merge-base --is-ancestor origin/main origin/agent/<them>` before *any*
  agent-branch merge, do not merge if it fails, and after merging confirm the
  other agents' owned paths are intact and `git diff --stat` shows no unexpected
  deletions; (2) sent writing-research an urgent, explicit merge procedure
  (`start` → resolve → work → `finish` → reply), naming the four files that will
  conflict (`AGENTS.md`, `lessons_learned.md`, `docs/venues/recommendations.md`,
  their own `NOTES.md`) and stating exactly what to take from `main` in each
  case, including that `state/reviewer/`, `solvers/`, `experiments/` and
  `state/coder/` are not theirs to resolve and that `main`'s version wins;
  (3) recorded that the reviewer owns this check. The general point: a stale-base
  branch is not merely *behind*, it is **actively dangerous to merge**, and the
  only reliable detector is the ancestor test, not the diffstat — the diffstat
  *looks* alarming but is easy to misread as "the agent deleted things" rather
  than "the agent never had them".
- 2026-09-25 **R6b — fixed the protocol flaw that caused the R6 regression.**
  Diagnosing why writing-research acted on a superseded verdict surfaced a
  structural defect in the protocol itself: outboxes are **append-only** and
  `agent.sh inbox` prints them **top to bottom**, so the *oldest* verdict appears
  first. `to-writing-research.md` opened with the **R1 verdict from 2026-09-24
  16:50** — five cycles stale — and the outboxes now hold 7–13 messages each
  (250–321 lines). An agent reading in the printed order sees obsolete
  instructions before current ones, which is precisely the failure mode I had
  already fixed inside `DECISIONS.md` (OPERATIVE TEXT blocks) without noticing it
  in the messaging layer. Three fixes, all in my own or scaffold paths:
  (1) prepended a **"READ THIS FIRST"** header to all four of my outboxes stating
  that the history is append-only, that the newest block at the bottom is
  authoritative, a table of where the current state actually lives
  (`DECISIONS.md` OPERATIVE TEXT, `D10-EXPERIMENT-SPEC.md`, the R5d claim
  report, `reviews/`), and a per-agent "where you stand" summary — history
  preserved intact (13/12/7/9 messages, newest timestamps unchanged, verified);
  (2) amended **PROTOCOL.md** (scaffold, D7) "Message conventions" with four
  binding conventions learned the hard way: read newest-message-first; run
  `start` every session because a stale base lacks the current engine and review
  state; verify identifiers against primary sources because *every* fabricated
  reference in this project was written from memory; and DECISIONS.md wins over
  any outbox message; (3) noted the counting gotcha — my own
  `grep -c '^## '` now sees the header, so header headings use `###`.
  The general lesson, recorded: a fix applied to one instance of a pattern is not
  a fix to the pattern. I hardened the decision record in R5j and missed the same
  hazard in the outboxes one cycle later, and an agent lost a cycle to it.
- 2026-09-25 **R6 — writing-research `d97541d`: HOLD, no merge.** They pushed
  at 06:28 after ~1.5 h of silence. **Root cause, and the most important
  finding of the cycle: their branch has not merged `main` since R3** —
  `git merge-base --is-ancestor origin/main origin/agent/writing-research` fails,
  last merge is `b221474` — so their tree contains none of the coder's engine,
  none of my R5 verdict, none of D9/D10 or the addenda, and neither corrected
  scaffold file. Their log cites the **superseded R3/R4 "B*" IDs** rather than
  the current W1–W5, and `outbox/to-reviewer.md` is byte-identical to
  `abd4d63`, so the R5 verdict was never answered. They have been executing a
  fix list that no longer exists. Required step 0 sent: `agent.sh start
  writing-research` then read the outbox **newest-first**; the R5 verdict and all
  addenda supersede R4 in full. I recorded that the B*→W* renumbering was my
  signal for supersession and it failed, and apologised for the wasted cycle.
  **Substance: W1 regressed** — a second fabricated reference added this push
  (`koch2019dlra`: "Dynamical low-rank approximation", "Koch, Olga and Lubich",
  *J. Nonlinear Sci.* 29(1):1–35, 2019; Crossref confirms no such paper — the
  real record is Koch, **Othmar** & Lubich, SIMAX 29(2):434–454, 2007,
  10.1137/050639703), so every field but title and one co-author is wrong;
  "Olga" now in both Koch entries, i.e. systematic not a typo. `koch2015projector`
  unchanged (still arXiv:1505.05648 = Schapira, math.DS). W2 phantom DOI
  unchanged. W3 **claim false**: `venue_shortlist.md` still coexists with
  `recommendations.md`. W4: **ICASSP removal credited as real progress**, but
  zero access dates remain and the ranking moved *further* from the approved set
  — AISTATS promoted to **rank 1** (excluded by D5/R4) and journals demoted to
  #8–12 (JCP #8, SISC #9, CMAME #10, JFM #11, PoF #12), plus a new undeclared
  "Accessibility (Taiwan/Asia)" criterion; I acknowledged location accessibility
  is a legitimate constraint if declared, but it must not silently outrank SISC/JCP
  for a methods paper. W5 **claim false and regressed**: all eight root files plus
  scaffold `scripts/arxiv_searcher.py` still present, **plus two new unowned
  files added by this push** (`a/b/c.txt` = "test", `test_file.txt` = "test
  content") while the board claims "B4 cleanup completed"; third cycle running,
  count went up while the claim went the other way — asked them to find what
  creates the files rather than delete them again. Non-blocking: `girfoglio2022`
  changed to author initials although R5 recorded full names as fine and it is
  inconsistent with the file; stray leading spaces on two `author=` lines.
  **Credit recorded:** refs.bib structural integrity intact (37 entries / 37
  unique / 0 dups), the six NS-ROM entries present, Girfoglio and Sousedík
  correct, novelty-defence documents useful — nothing already correct was
  damaged; the damage is confined to the five blocker areas plus the two new
  files. Also used this cycle to re-verify from Crossref that of the records I
  might have reconstructed from memory, two were wrong (a venue and a title) —
  which is why the fix list points at the R5d verified list rather than asking
  them to redo the search.
- 2026-09-25 R5p (scoped the theory question from the literature before assigning
  it — the same lesson as R5c, applied to the remaining open question). I had
  framed theoretical-research's job as "define a forcing-aware invariant", which
  sounded like a from-scratch task. Checking what the established
  structure-preserving DLRA integrators actually preserve: **all of the SPDLRA
  results are symplectic and explicitly for non-dissipative, Hamiltonian
  systems** (arXiv:2007.13153, 2008.07427, 2308.16547 all say "Hamiltonian
  systems modelling non-dissipative phenomena"; the reduced dynamics is the
  symplectic projection of the Hamiltonian vector field), and the BUG papers
  claim only symmetry-preserving properties plus a robust error bound
  (arXiv:2104.05247, 2402.08607) — **no energy identity**. Symplecticity is the
  wrong structure for forced dissipative flow (a contracting forced flow has none
  to preserve, and the Hamiltonian line restricts itself for exactly that
  reason), so nothing transfers to us by citation and a careful reviewer will
  see it. Nearest dissipative theorem: Kazashi–Nobile–Vidličková (Numer. Math.
  149(4), 2021, 10.1007/s00211-021-01241-4), a **discrete variational
  formulation** with parabolic-regime stability for projector splitting. So the
  landscape splits: non-dissipative/Hamiltonian -> symplecticity;
  dissipative+diffusion-dominated -> discrete variational + stability;
  **dissipative + advection-dominated + forced + adaptive rank + exactly
  divergence-free (ours) -> nothing found.** That third row is the project, and
  it turns the theory task into a well-posed increment on a named predecessor
  rather than an open-ended definition — a much better brief, and short-paper
  sized. Consequences recorded as binding in D3: the method section may claim
  exact divergence-freeness **by representation** and may describe the
  construction, but may **not** claim symplecticity or a proved conservation
  law; the reduced-model forcing-aware invariant is to be stated **discretely
  with the projection term derived, not measured**, which requires the BUG port
  first, so the two are sequential. Sent theoretical-research a four-item brief
  (Galerkin step's effect on the energy balance; boundedness of the residual;
  whether a defect correction restores a controlled balance; then the discrete
  invariant) with an explicit statement that a partial result is fine and that I
  will tell the writer which of "proposition" or "numerical observation" we have.
  Also warned the writer off a symplecticity claim and suggested the *absence* of
  a discrete energy identity for advection-dominated forced low-rank integrators
  can be framed as an open problem we contribute to — as an open problem, not as
  our result.
- 2026-09-25 R5o (costed the D10 gate — a gate that cannot be executed gets
  quietly relaxed, so I priced it before R6 rather than discovering at R6 that
  the runs do not exist). Measured basis: 1.84 ms (full) / 2.95 ms (POD) / 4.60
  ms (DLRA) per step at N=64. **The expensive-looking requirements are cheap:**
  T=20 at N=64 is 40,000 steps = ~1.2 min (full) and ~3.1 min (DLRA), so the
  whole three-Re x four-method matrix is **~20 minutes** and T=100 is ~1.5 h.
  My earlier framing of "T = 20-100" as a heavy budget was simply wrong at this
  resolution, and I have corrected it in the spec — stationarity is not a reason
  to defer anything. **The resolution study does not want long runs:** its job is
  grid convergence of the diagnostics, needing the same physical problem at
  N=64/128/256, which at T=0.1 is minutes. High N *and* long T is the expensive
  combination and it is **not required**, which dissolves the tension I had
  assumed existed between V2 and V5. **Caveat that matters more than the
  numbers:** the N=64 -> N=128 DLRA ratio is 3.11x, *below* the ~3.85x that
  N^2 log N alone predicts, so the N=64 timing is overhead- or warm-up-dominated
  — the same artifact R5n found in the cost figure. My projections are
  order-of-magnitude planning figures only, and I deliberately did **not**
  extrapolate N=256: a two-component fit from two points degenerates and returns
  a physically impossible ordering (DLRA cheaper than full grid), so N=256 must
  be measured. Recommended order: re-time, V1, V2 at N=64/T=20, F2 with the full
  spectrum, V5 at short T, V4, V6 then re-run 3-6, and only then decide on any
  long high-N run. Steps 1-5 are a few hours total; step 7 is the one with real
  engineering risk, which is a second reason not to leave it behind the runs.
  Also flagged that `normalized_spectrum`'s `count=32` default is the *binding*
  constraint on F2 and must become a parameter, or the slow-decay claim cannot be
  checked from the artifacts (the original V7 problem).
- 2026-09-25 R5n (figures audit — the writing lens applied to the actual
  visual artifacts). I had only ever inferred the figures' content from
  `make_figures.py`; this cycle I rendered and inspected all three committed
  figures. **None is usable in the paper as committed** — one honest with an
  artifact, two actively misleading. (1) `fig_cost.png` is honest in direction
  (DLRA tallest in every group) but the three Re groups differ by up to **1.7x
  for computationally identical work** (only `nu` differs), so it presents a
  warm-up artifact as a Re-dependence, with no spread bar and no N/dt/rank/
  thread annotation. (2) `fig_rank_error.png` is misleading three ways: the
  right panel's y-axis says "relative L2 error" for what is a
  trajectory-divergence number whose true t=0 value is 0.319 (R5m), so the flat
  line at ~0.32 reads as "tracks the reference to within 32%"; the left panel
  titled "Adaptive rank growth" is a step function that reaches 42 of a 48 cap
  within t~0.03 and is then **flat for 97% of the axis**, i.e. it argues
  *against* the adaptive-rank narrative; and the POD curves at ~1.07 (worse
  than predicting zero) are presented as a clean comparison, which is the V4
  broken baseline. Re=100/1000 are drawn at alpha 0.45 and effectively
  invisible while three Re are claimed. (3) `fig_singular_values.png` plots the
  **DLRA's own rank-truncated spectrum** to argue "slow singular-value decay" —
  near-tautological, since a rank-42 state has 42 retained values that decay
  smoothly. The premise claim needs the untruncated full-grid spectrum, already
  in the committed JSON: sigma_32/sigma_1 = **1.45e-3**, sigma_10/sigma_1 =
  3.17e-2, no cliff across 32 modes. It also advertises the V1 defect without
  explanation: the t=0.00 curve is a cliff to 1e-16 by index 3 *because the
  method starts at rank 2*, so a reader rightly asks why the paper's premise
  (rank is not small) sits next to a figure starting at 2. Fixes and a
  per-figure specification are now in `D10-EXPERIMENT-SPEC.md` and the R5n
  report; both coder and writer were sent the details, including the figure I
  want the writer to plan around: the IC spectrum (exactly rank 17, clean cliff)
  against the developed-state spectrum (no cliff) — a before/after statement
  about *this* flow that motivates adaptive rank far better than a generic
  remark about spectra, and uses data already on `main`. Also asked the coder to
  mark the three figures provisional in `experiments/README.md` or move them,
  since paper-quality typesetting currently implies paper-readiness.
- 2026-09-25 R5m (audit of the experiment **drivers** — the last unreviewed
  layer). R5k/R5l audited the library; the code that *produces the artifacts*
  had only been read at the API level, and the R5 IC-mismatch finding is exactly
  the class of defect a driver can hide. Read `run_long_time.py`,
  `bench.py`, `run_rank_growth_sweep.py`, `run_taylor_green.py` in full.
  **D1 (must fix before any error-vs-time figure):** `run_long_time.py`
  hardcodes `samples[0]["relative_l2"] = 0.0`, but the DLRA state at t=0 is the
  rank-2 projection — the true value, computed by me through the same code path,
  is **0.319034** (E(IC) 22.2067 vs E(rank-2) 7.7958). `run_kolmogorov`'s
  `_run_projected` compounds it: `checkpoints[0]` is the *projected* state and
  errors are appended only for step >= 1, so the step-0 comparison is never
  computed. Consequence: the recorded curve rises 0.0 → 0.324 and reads as
  "agreement then decorrelation", when the truth is **0.319 → 0.324** — the
  error grows by ~0.005 over T=1, so essentially all of it is the
  initialisation offset and there is **no predictability horizon to read off
  this run at all**. After the V1 fix the curve starts near zero and its
  *growth* becomes the quantity the paper needs. Sharpest statement of V1 yet,
  and it is visible in the coder's own artifact.
  **D2:** no driver records `initial_state_sha256` or per-method initial
  energies despite both using the same `make_initial_state`, so the V1 defect
  is invisible in the artifacts (confirms the spec's P0.1 as a driver-level
  omission). **D3 (latent):** `bench.py` takes the aggregate `git_commit` from
  the loop variable left over from the last iteration (Re=5000). **D4 (minor):**
  the summary records POD's *effective* rank but not the requested one.
  **D5 — strengthens V2 and saves rework:** every driver uses identical IC
  parameters across the three Re and the long run, so the cases start from a
  bit-identical state and differ only in `nu`. That **rules out** the
  alternative explanation for V2 I had not excluded — the Re-independence
  (0.3152/0.3164/0.3165) is not an IC artifact; viscosity barely matters over
  T=0.1. V2 stands; do not re-check the IC on that account. **D6:** the
  Taylor–Green driver is sound, but F1 is a *kernel* test, not a projector test
  (the field is exactly rank 1, so the projector is never exercised); the
  `SelfConsistentForcing` stationary-state check remains the sharp projector
  test. Net: the engine is now audited at all three levels — operators, rank
  logic, drivers. D1 recorded as a binding reporting obligation under D10-V1.
- 2026-09-25 R5l (independent audit of the rank/projection logic — the last
  unexamined engine component, and the one the adaptive-rank claim rests on).
  35 checks written, 27 passed as written; **7 of the 8 failures were defects in
  my harness** (5 inverted boolean encodings, 2 zero tolerances where roundoff
  was expected), **1 real finding**. The rank logic is sound and, where it
  matters for the paper, better than "correct": `SVDProjector.project` is the
  **Eckart–Young optimal** rank-r truncation (matches an independent
  `numpy.linalg.svd` truncation to 0.0 for r=1,3,5, and its residual equals
  `sqrt(sum_{i>r} sigma_i^2)` to ~3e-15), the rank rule is exactly
  `#{sigma_i > tol*sigma_1}` clipped to `[min_rank, max_rank]`, rank adaptation
  demonstrably reads the retained pre-projection candidate (the R4 checklist
  item, now independently confirmed), factors are orthonormal to ~1e-15, stage
  candidates are retained per stage, all input validation raises as intended,
  and `PODGalerkin.fit` matches the top left singular vectors to 0.0.
  **The finding:** `PODGalerkin.project` ends with `return out - np.mean(out)`,
  but the basis columns are not spatially mean-free (one had mean 3.4e-3), so
  that line shifts the result *out* of `mean + span(basis)`. The projection is
  therefore not the least-squares projection `relative_error()` assumes (2.2e-3)
  and is **not idempotent** (1.4e-3); the discrepancy is exactly a constant
  (`out = project(q) + mean(out)` to 3.5e-18). Deleting the line restores both
  properties exactly (0.0 and 2.2e-16). **A hypothesis I tested and dropped:**
  I initially suspected this explained V4's 11.4x POD energy blow-up — it cannot,
  because psi's mean is a pure gauge for `u = grad_perp psi` (velocity
  difference 1.3e-15) and `step` re-centres every step, so V4's cause is
  unchanged (the IC is replaced by mean+top-r modes fitted on a transient
  window). It is a *contract* bug affecting reported reconstruction errors and
  the sense in which a POD step is Galerkin, not a dynamical one. The engine's
  existing tests cannot catch it because their fields are single-mode or
  two-mode, whose projections happen to be mean-free; two checklist items added
  (idempotence + least-squares match on a field whose basis vectors are not
  mean-free; brute-force rank-logic checks). With R5k the engine is now
  independently audited end to end, and D9 stands with two non-blocking items
  open (`kx_diff` Nyquist fix, POD projection contract).
- 2026-09-25 R5k (independent operator audit of the merged engine). R5 verified
  the engine by re-running the author's tests and hand-checking the algebra,
  which has a blind spot by construction: the suite shares any misconception with
  the code, and every field in it is smooth or band-limited. So I audited the
  **operators** against references I built myself — a full 2-D spectrum (no rFFT
  half-spectrum route), integer arithmetic for the 2/3 mask, and an independently
  manufactured forcing. **18 checks pass**: `lap` and `vorticity` to 2.3e-13,
  `u == d_y psi` to 1.1e-14, both `inv_lap` conventions to 7.8e-15,
  `<u, grad psi> == 0` exactly, Parseval exact, the rectangular 2/3 rule exact
  (`|k| <= floor(N/3)` per direction, Nyquist dropped), dealiasing a no-op for
  resolved products, the heat semigroup to 5.6e-16, and the **energy identity to
  6.0e-17** with my own manufactured `zeta`. The dealiasing check has a working
  positive control (out-of-band amplitude 1.09e+06 undealiased → 1.02e-11
  dealiased), so it demonstrably does something.
  **One real finding, non-blocking:** three checks failed with a single root
  cause *in the engine* — `Grid2D` uses the x-Nyquist wavenumber
  `kx[N//2] = -N/2` in derivative multipliers, which is not admissible for a
  real field's x-derivative. At N=32 on a full-band field,
  `max|v_engine - (-d_x psi)| = 7.48`, and zeroing that wavenumber drops the
  error to 1.07e-14; for a field with no Nyquist content everything agrees to
  ~1e-15. Inert in every committed run (dealiasing removes `|k| > floor(N/3)`,
  IC band-limited), cannot affect the 13 tests, fix is a separate
  `kx_diff` array plus a full-band test. D9 stands; recorded as a D9 addendum
  and added to the standing checklist as §1.4's full-band operator test.
  **Process note recorded:** my first three audit runs reported failures that
  were *my* errors — wrong `inv_lap` sign expectation, a circular-vs-
  rectangular mask assumption, and an "independent" curl reference that was
  itself built through the ambiguous rFFT route (which is how the Nyquist issue
  surfaced at all). Each time the correct move was to rebuild the reference
  rather than accept the discrepancy. Second time this cycle a check failed for
  a reason on my side (the IC-rank error was the first), so the rule is now
  explicit: when an independent check disagrees with code that already passes
  its own tests, the first hypothesis to test is the check.
- 2026-09-25 R5j (integration check + fixed a hazard I created in the governing
  documents). Three things only the integrator would notice.
  **(1) `main` is coherent as a whole:** exported `origin/main` fresh; no
  conflict markers or merge artefacts anywhere in the tree, and the engine suite
  passes **13/13 from `main` itself** (not from the coder's branch export, which
  is how I verified it in R5). The integrated result of eight merges plus the
  scaffold amendment is sound.
  **(2) The decision record was unsafe to read top-down, because of my own
  iteration.** D4 contained *four* successive claim statements — the original
  (now barred), the R5b "Binding refinement", R5c, and R5d — with nothing
  marking which governed, so an agent reading from the top could have quoted the
  barred claim out of a binding document. Added an explicit **OPERATIVE TEXT**
  block at the head of D3, D4, D5 and D10, stating in one place what governs,
  what is superseded, and the barred forms; and pointed D10 at
  `D10-EXPERIMENT-SPEC.md` as the acceptance document rather than at the
  summary inside the decision.
  **(3) The same hazard was worse in `AGENTS.md`** — the entry point every agent
  reads first — which still described the too-strong claim as "defensible".
  Amended as scaffold owner (D7): it now says the earlier wording was wrong,
  names Musharbash & Nobile (DOI 10.1016/j.jcp.2017.09.061) as the refutation,
  states that exact divergence-freeness is textbook in a psi formulation and is
  already present in our closest prior art, points at the R5d wording as
  binding, and lists the barred forms. Verified afterwards that no scaffold file
  (`AGENTS.md`, `PROTOCOL.md`, `lessons_learned.md`) still asserts the retired
  claim, and that `lessons_learned.md` carries exactly one dated correction.
  General lesson recorded: when a reviewer revises a position, the *history* of
  the revision is as dangerous as the error — superseded wording must be marked
  as superseded everywhere it still appears, or the next agent will read it as
  current and act on it.
- 2026-09-25 R5i (self-audit: machine-verified my own binding numbers). Before
  R6 I re-verified **every quantitative claim** I have put into a decision,
  report or spec against the committed artifacts on `main`, rather than trusting
  transcription from earlier terminal output. **26 of 27 pass, 1 fails** — and
  the failure was mine, in a document the coder is working from. I had written
  that the project IC is "numerical rank ~19 ... plus the rank-1 shear".
  Measured: numerical rank **17** at every tolerance from 1e-8 to 1e-14, with
  sigma_17 = 2.46e-4 and sigma_18 = 8.2e-17. My reasoning was wrong: the base
  Kolmogorov shear `psi = -U cos y` is supported at `(0,+-1)`, *inside* the
  |k|<=8 box, so it adds no rank, and the 17-modes-per-axis band bound is
  attained exactly. Corrected in `D10-EXPERIMENT-SPEC.md`, `NOTES.md` and an
  erratum in the R5c report; the coder and writer were told (the outbox keeps
  the earlier wrong figures as append-only history, superseded by the later
  messages). The operative conclusion is unchanged and slightly strengthened —
  the IC is *exactly* rank 17, so the 65% initial energy loss is unambiguously
  a harness choice — and it yielded a sharper acceptance test now written into
  the spec: an adaptive initialisation must recover the full-grid initial energy
  (22.207) **to roundoff**, which is far more checkable than "the error went
  down". It also gave the writer a better premise argument than the slow-decay
  framing: the IC is 17-dimensional by construction while the developed state is
  not (sigma_32/sigma_1 = 1.45e-3 with no cliff), so the flow starts in a
  low-dimensional subspace and leaves it — a before/after statement about
  *this* flow rather than a general remark about spectra. Verified as passing:
  64.89% IC energy loss, 11.4x POD energy, 159x POD enstrophy, POD rel-L2 1.079,
  the Re triple 0.3152/0.3164/0.3165, max CFL 0.01475, 2.25x enstrophy grid
  discrepancy, 34x CFL ratio, rank 2 -> 40@step50 -> 43 with 0 steps at the cap,
  full-grid sigma_32/sigma_1 = 1.45e-3 and sigma_10/sigma_1 = 3.17e-2, DLRA
  sigma_32/sigma_1 = 3.2e-4, Taylor-Green 2.26e-14 / rank (1,1,1) / strictly
  negative energy increment / 1.63e-14 divergence, and the rank-sweep
  insensitivity (spread 2.0e-6 over ranks 20/38/42). Lesson recorded: a merge
  gate is only as good as its numbers, and the discipline I demand of the agents
  (verify against artifacts, do not trust recall or transcription) applies to
  the reviewer too.
- 2026-09-25 R5h (closed the DMD / operator-inference gap). R5d mapped the
  low-rank *integrator* prior art thoroughly but not the adjacent **data-driven
  model reduction** literature, which is what a scicomp reviewer reaches for
  first when shown a low-rank method for 2-D NS — comparing only against *static*
  POD invites the strawman-baseline objection. Verified 2026-09-25: Peherstorfer
  & Willcox, *Dynamic data-driven reduced-order models*, CMAME 291:21–41 (2015),
  DOI 10.1016/j.cma.2015.03.018; Williams, Kevrekidis & Rowley, J. Nonlinear Sci.
  25:1307–1346 (2015), DOI 10.1007/s00332-015-9258-5; Benner, Goyal, Heiland &
  Pontes Duff, ETNA 56:28–51 (2021), DOI 10.1553/etna_vol56s28 (closest paper in
  spirit — exploits intrinsic NS structure to learn a structured low-dim model);
  their stabilisation follow-up (COAP 82:225–249, 2022,
  10.1007/s10589-022-00359-x); Goyal, Pontes Duff & Benner, *Guaranteed stable
  quadratic models…*, Physica D 483:134893 (2025), 10.1016/j.physd.2025.134893;
  and a contemporaneous long-term-stability OpInf paper (arXiv:2609.14812,
  13 Sep 2026). Two useful negatives: `"dynamic mode decomposition" AND
  "stream function"` and `"low-rank" AND "2D turbulence" AND "Navier-Stokes"`
  both return 0 hits on arXiv. **Outcome: the D4 claim is unchanged** (DMD/OpInf
  are offline data-driven models, not factorisation-based integrators), but two
  obligations change: **F5 now requires a POD-DMD baseline** at matched ranks
  (cheap — reuses `solvers/pod.py`), and related work must position the
  data-driven line. Wrote the distinction that favours us: *our structure comes
  from the representation* — a stream-function state makes the constraint exact
  for the full field and every reduced state with nothing to enforce and nothing
  learned — whereas data-driven structured models get constraints from an ansatz
  fitted to a snapshot database. Also recorded a self-correction: I had the
  Williams–Kevrekidis–Rowley venue wrong (J. Nonlinear Sci., not SIAM JADS) and
  could not confirm the Peherstorfer–Willcox "prefetching CFD snapshots" title —
  the second plausible-looking citation to fail verification this cycle after
  `koch2015projector`, neither of which is cited anywhere in the project.
- 2026-09-25 R5g (R5 protocol diagnosis + the experiment specification).
  **Diagnosis first:** before assuming the agents were idle I checked whether
  inbox delivery was broken — `print_inbox` reads `origin/agent/<sender>`, and
  all 25 messages are sitting exactly there (5 coder, 7 writer, 7
  writing-research, 6 theoretical-research). Delivery works; the sessions have
  simply not been started. Recorded so no future cycle re-diagnoses it.
  **Wrote `reviews/D10-EXPERIMENT-SPEC.md`**, the document that was missing: D10
  listed V1–V7 as defects but never said what the paper must *contain*, which
  is why coder and writer were implicitly waiting on each other. The spec fixes
  F1–F7 and T1–T2 with the producing run, the content, the acceptance bar and
  the D10 item each closes, plus a priority order for when time is short
  (F1, F2, F4, F7, F5, F6, F3) and a "minimum publishable set" statement
  (F1+F2+F4+F7 with honest T1 is already a solid scicomp submission). It also
  records what is already met so nothing is redone, and collects the known
  traps. Four substantive changes it forces: (1) **every result artifact must
  record `initial_state_sha256`** (hash + dtype + shape) so V1 is checkable
  without re-running anything — that one field would have caught the 65%
  initial energy loss immediately; (2) **pointwise relative L2 is not an
  accuracy metric in a chaotic regime** — it measures phase divergence, which is
  exactly why the 31.5% is Re-independent — so the required order is
  predictability horizon, then time-averaged E/Z with spread, then spectral
  agreement, then endpoint L2 labelled as divergence; (3) the rank sweep's
  error insensitivity (0.31653509/0.31653308/0.31653308 at ranks 20/38/42)
  must be explained rather than extended, and is probably another face of the
  initialisation offset; (4) F2 must plot the *untruncated reference* spectrum,
  never the rank-truncated reduced state. Bars are labelled as reviewer
  judgement and explicitly waivable with a recorded reason, because the failure
  mode this project already produced once was a number quoted without one.
- 2026-09-25 R5f (scaffold correction — the highest-leverage fix available
  while agents are idle). Cross-checked `lessons_learned.md` against what R5d
  established and found that **the file every agent must read first still seeds
  the too-strong novelty claim** — including "does not appear on arXiv" and
  "the closest prior art is Girfoglio–Quaini–Rozza". Amended it as scaffold
  owner (D7), preserving the original text and appending a dated reviewer
  CORRECTION block: (i) arXiv-only is insufficient — Musharbash & Nobile (JCP
  2018) did apply dynamically orthogonal approximation to incompressible NS, so
  "no dynamical low-rank method for incompressible NS" is false; (ii) exact
  divergence-freeness is not part of the novelty and the closest prior art
  already has it (journal version Computers & Fluids 244:105536, plus Zhang et
  al. Phys. Fluids 36(6)); (iii) the methodological lesson — the last mile of a
  novelty claim is reading what the prior papers *did*, not their titles, and
  journals must be covered; the DO paper surfaced only by chasing a citation in
  an unrelated bibliography. Also added a process note under "Persist
  intermediate research artifacts immediately": writing-research's W5 clutter
  (8 root scripts + 2 temp JSONs + stale `old_refs.bib`) is that exact lesson
  recurring — 4 of 5 new survey IDs lived only in an **unowned** index while the
  owned one went stale. Without this amendment the next session would have
  re-derived the overclaim from the file it is told to trust.
  Separately checked the two idle boards: both honestly say "fresh — no sessions
  yet", so no rule-8 breach, but both carry **stale scaffold-seeded text** — the
  writer's mission cites a "v1 engine" (prior-attempt artifacts AGENTS.md
  forbids) and the theory board asserts Taylor–Green "rank 3→2→1" when the
  committed `taylor_green.json` records rank 1 throughout (rank_min = rank_max =
  final = 1). Flagged both, since each board is its own agent's to fix.
- 2026-09-25 R5e (critical-path de-risking while agents are between runs).
  Read the BUG paper the coder must port (arXiv:2402.08607, open-access HTML
  confirmed at arxiv.org/html/2402.08607; arXiv:2104.05247 likewise) and sent
  the coder the §2 algorithm verbatim — projected ODE and tangent projection
  `P_r(Y)Z = Z V Vᵀ − U Uᵀ Z V Vᵀ + U Uᵀ Z`; K-step `K̇=F(t,KV₀ᵀ)V₀`,
  `K(t₀)=U₀S₀`; `Û=orth(U₀,K(t₁))` by QR, `M̂=ÛᵀU₀`; L-step
  `L̇=F(t,U₀Lᵀ)ᵀU₀`, `L(t₀)=V₀S₀ᵀ`; `V̂=orth(V₀,L(t₁))`, `N̂=V̂ᵀV₀`; S-step
  `Ŝ=ÛᵀF(t,ÛŜV̂ᵀ)V̂`, `Ŝ(t₀)=M̂S₀N̂ᵀ`; then truncation by **SVD of the small
  r̂×r̂ Ŝ** — the decisive cost difference from the current four full N×N SVDs
  per step. Second order = first-order BUG half-step + Galerkin update with an
  augmented basis; their step-rejection criterion allows arbitrary rank growth
  from rank 1. Sent two expectation corrections: (i) **robustness is not the
  win** — the current projector never divides by a small singular value either,
  so the honest claims are cost, the augmented-basis Galerkin step (the
  mathematically meaningful change and the plausible route to a structure
  property), and second order with rank adaptivity; claiming a robustness
  improvement over our own code would not survive review. (ii) At N=64 with
  r≈43 the cost win may not appear (r comparable to N), so cost must be reported
  at N=128/256 with an explicit crossover statement. Also suggested a sharp new
  test: `SelfConsistentForcing` gives a stationary state, so a BUG run from a
  rank-representable start should hold it to machine precision — any wrong
  K/L/S-step or truncation destroys it immediately. Noted their §5.1 heat
  equation is the natural anchor for our exact heat semigroup.
- 2026-09-25 R5d (novelty claim settled, with a correction that matters).
  Extended the check past arXiv into journals and then into the *contents* of
  the foundational papers. Three results: (1) Koch & Lubich 2007 (SIMAX,
  10.1137/050639703) has **no** NS example — downloaded all 21 pages from the
  author's site; zero hits for "Navier", "Stokes", "stream function",
  "vorticity", "advection", "turbulence", "Kolmogorov". Nonnenmacher & Lubich
  2008 (MCS, 10.1016/j.matcom.2008.03.007) covers latent semantic indexing,
  image compression and a reaction–diffusion blow-up. Neither touches NS.
  (2) **Correction: "no dynamical low-rank method for incompressible NS" is
  false** — Musharbash & Nobile (JCP 354:135–162, 2018,
  10.1016/j.jcp.2017.09.061) apply dynamically orthogonal approximation to
  incompressible NS with random boundary conditions, with an error analysis in
  SISC 37(2):A776–A810 (10.1137/140967787). Found only by chasing a citation
  inside an unrelated bibliography. That claim form is barred.
  (3) Structure-preserving/robust low-rank for conservative PDEs is also
  established elsewhere (RAIL advection–diffusion 10.1137/23M1622921;
  macro-micro hyperbolic moment equations 10.1007/s10444-024-10175-y;
  stability of robust DLRA 10.1137/21M1446289; Burgers-with-uncertainty
  10.1615/int.j.uncertaintyquantification.2022039345), so "first SP low-rank
  for conservative PDEs" is barred too. Plus a **second** ψ-formulation NS ROM
  the survey lacks: Zhang et al., Phys. Fluids 36(6), 10.1063/5.0202509.
  **Final permitted claim** recorded verbatim in D4 and the R5d report: SPDLRA
  is established for Hamiltonian/kinetic/Vlasov–Poisson/wave equations and
  robust low-rank for conservative PDEs; for incompressible NS the existing
  dynamical work is DO approximation for stochastic problems and the existing
  ψ-formulation models are offline/hybrid; we provide a structure-preserving,
  exactly divergence-free, factorisation-based integrator for the deterministic
  problem validated at resolved high Re with adaptive rank. Gated on
  D10-V1/V2/V5/V6/V7. The report lists the sixteen verified references the
  survey must contain; all DOIs Crossref-resolved, all arXiv IDs abs-page-read.
  Process lesson recorded: for a novelty claim the last mile is reading what the
  prior papers *did*, not what their titles suggest.
- 2026-09-25 R5c (reviewer homework, again no dependency on pending fixes):
  **V6 answered — SPDLRA is standard execution, not a moonshot.** Searched the
  literature (arXiv all-fields; abs pages read directly) and found the method
  family our engine is a naive member of: **BUG (basis-update & Galerkin)
  integrators** — arXiv:2402.08607 (Ceruti, Einkemmer, Kusch & Lubich, robust
  second-order BUG via the midpoint rule, i.e. the rule we already use),
  arXiv:2104.05247 (Ceruti, Kusch & Lubich, rank-adaptive robust integrator:
  update bases, Galerkin in the span of old+new bases, truncate to tolerance),
  arXiv:2608.27749 (Hauck, Kusch & Schotthöfer, high-order robust BUG, Aug
  2026). Consequence: D10-V6 is a **port**, not a research question — replace
  the per-step full SVD with QR/CholeskyQR basis update + Galerkin projection +
  tolerance truncation, factorisation kept in Fourier space. This likely fixes
  the cost, accuracy and structure objections together, and is recorded as the
  decision with honest-reframing as the fallback if blocked. **This also
  sharpens the novelty claim**: SPDLRA is established for Hamiltonian
  (2007.13153, 2008.07427, 2308.16547), Vlasov–Poisson (2608.00397), elastic
  waves (2606.30469) and kinetics (review 2412.05912) but for **nothing** in
  incompressible NS — so the contribution is "first application of SPDLRA to
  incompressible NS, with exact divergence-freeness by representation, validated
  on resolved high-Re turbulence with adaptive rank", which is a far better
  position than the divergence-free framing. Gated on V6 being implemented.
  **Premise check on the committed long run** (AGENTS.md's "rank ≫ 3, slow
  singular-value decay, adaptive rank growth"): two of three hold. Rank 2→40 by
  step 50, 42 by 100, plateau 43, never touching the `max_rank=48` cap, so the
  growth is a real measurement. Slow decay quantified from the *untruncated*
  full-grid spectrum at step 2000: σ₃₂/σ₁ = 1.5e-3, σ₁₀/σ₁ = 3.2e-2 (<3 decades
  over 32 modes). "Adaptive rank *dynamics*" is not yet shown — the rank jumps
  and plateaus, which is the T≤1 transient, not the rank logic (D10-V2). Side
  finding: the full-grid IC spectrum has σ₁₇ = 2.5e-4 and σ₁₈ = 8.2e-17, so the
  IC is **numerical rank exactly 17** (rank 17 at every tolerance 1e-8…1e-14;
  a field band-limited to |k|≤8 factors through 17 modes per axis and attains
  the bound) — so the IC is exactly low-rank and the rank-2/65%-energy-loss
  start is a harness choice, which sharpens V1. **[Corrected 2026-09-25: this
  entry originally said "rank ≈ 19 … plus the rank-1 shear". The shear
  `ψ = −U cos y` is supported at (0,±1), inside the |k|≤8 box, so it adds no
  rank; the measured value is 17. See the erratum in the R5c report.]** The
  DLRA's own spectrum decays *faster* than the reference (σ₃₂ = 3.2e-4 vs
  1.5e-3), consistent with the projection discarding real content. **Reviewer
  note to self:** I should have run this search before writing the R5 V6 message
  — I framed a settled question as an open choice and cost the agents a round
  trip. Recorded so R6 does not repeat it.
- 2026-09-25 R5b (reviewer-initiated, no dependency on the pending fixes):
  **D4 novelty claim narrowed.** Re-ran the novelty check independently (arXiv
  all-fields, 7 queries, strings persisted in the report). Confirmed there is
  **no DLRA for incompressible NS on arXiv** (the obvious query returns 3 hits,
  all kinetic/other-domain; `"vorticity" AND "dynamical low-rank"` → 0) and
  corroborated the B1 0-hit record. But reading the abs page of
  arXiv:2201.00756 showed the designated closest prior art is a POD–Galerkin
  ROM **in the stream function-vorticity formulation** — i.e. it is *already*
  exactly divergence-free. So the "exactly divergence-free" half of the D4
  claim is not a differentiator, and "validated at high-Re" is a validation
  obligation rather than a novelty (and is unmet under D10). Recorded the only
  permitted wording (dynamical + structure-preserving + resolved high-Re +
  adaptive rank, with the closest prior art described accurately), barred
  "first exactly divergence-free NS solver", and required the survey to extend
  to journal venues since arXiv-only cannot support "to our knowledge". D4
  stays OPEN. **Writing-lens review of `docs/structure/suggested_structure.md`:
  HOLD** (S1 the gap statement is refutable by our own closest prior art; S2
  the split does not "enforce" div-free — the ψ state does, so as written the
  method section would describe a mechanism the code lacks; S3/S4 the
  contribution claims results we are blocked on and the draft predates the
  engine; S6 promises a standard-DLRA baseline and memory numbers that do not
  exist; S7/S8 recommend leading with the solid exactness result and adding
  error/resolution/limitations sections). **Standing checklist extended** with
  the criteria these reviews exposed — §1.0 comparability, §1.3
  stationarity/resolution/spectra/forcing-name, §1.4 real test execution +
  negative controls + reduced-path order/energy, §1.5 diagnostic-is-not-
  evidence, §2.1 divergence-free-is-not-the-novelty + name-the-method-for-what-
  it-is + gap-must-survive-a-counter-citation, §2.4 one venue doc with CfP URL +
  access date, and new §2.6 citation/record integrity (abs pages for every ID,
  Crossref for every DOI, no unverifiable entries, no scaffold writes).
  Noted for myself: the recurring failure across R2–R5 is claims drifting ahead
  of artifacts — in the bibliography, the structure draft, and the results.
- 2026-09-25 R5 (two reviews, one merge). **coder `b2f78fd` — APPROVED and
  merged (D9).** Verified independently: exported the branch to a scratch dir,
  built a clean venv (numpy 2.5.3 / scipy 1.18.1 / pytest 9.1.1) and ran the
  suite → 13/13 pass; hand-checked the rFFT/Parseval/vorticity/`Δ^{-1}`
  conventions and the energy identity `dE/dt+ν‖ω‖²−⟨ψ,ζ⟩+⟨ψ,adv⟩`; confirmed
  the engine's claim that exact diffusion preserves real-space rank (separable
  x/y convolution acts on the factors — checked empirically, still rank 2 at
  `νdt=2`); confirmed D3's laminar invariant via `taylor_green.json` (rank 1,
  2.26e-14, `max_energy_increase=-6.7e-3`, div 1.6e-14); confirmed scope
  (`git diff origin/main..b2f78fd -- AGENTS.md PROTOCOL.md` empty → the earlier
  diffstat lines were an older base, **no D7 violation**). **Validation NOT
  approved — new gate D10 (V1–V7):** the DLRA starts from a rank-2 IC projection
  and loses 65% of the energy before t=0 (7.796 vs 22.207), so `max_relative_l2`
  0.315 is mostly initialization offset and is Re-independent (0.3152/0.3164/
  0.3165 across Re=100/1000/5000); `max_cfl` 0.0147 everywhere and T=0.1 < one
  turnover, so the three Reynolds numbers are not distinguished; forcing is an
  unidirectional shear, not the AKS Kolmogorov pump; the POD baseline runs at
  11.4× the reference energy / 159× its enstrophy with an O(1) full-PDE residual
  and is not rank-matched (16 vs 42); the N=64↔128 check changes six parameters
  at once with 2.25× enstrophy disagreement; the scheme is exact-diffusion
  Strang + explicit midpoint + four full SVDs per step (no factor ODEs, no
  defect correction, energy systematically lost), so it is neither DLRA nor
  demonstrably SP as written; and the "spectrum" is the top-32 singular values
  of the rank-truncated DLRA state, which cannot support "slow decay". 9
  non-blocking nits (incl. a false-pass: `python experiments/test_engine.py`
  exits 0 without running anything). **writing-research `abd4d63` — HOLD**
  (report + fix list W1–W5). Good news recorded: 37/37 unique keys, 0 dups, all
  6 NS-ROM entries restored, girfoglio + Sousedík fixed, 4/5 new IDs verified
  genuine on abs pages, 0-hit query now a typed record, unowned index + 5
  `test_arxiv*.py` deleted. Blockers: `koch2015projector` → arXiv:1505.05648 is
  Schapira (math.DS, unique ergodicity) and no publication matches the claimed
  title/authors/year (real: Lubich–Oseledets, BIT 54(1):171–188,
  10.1007/s10543-013-0454-0, arXiv:1301.1058; the DLRA pioneer is **Othmar**
  Koch, not "Olga"); index DOI `10.1007/s00202-019-01435-x` unregistered (404 at
  doi.org *and* at the Crossref works API — real DOI 10.1137/050639703, SIMAX
  29(2):434–454, 2007; noted for the team that doi.org redirects 404 in this
  environment even for valid DOIs, so use the Crossref API); `docs/venues/`
  still two documents with zero access dates and all deadlines self-declared
  projections; ICASSP/AISTATS reinstated and the new ICML-first "ML Track"
  ranking contradicts the R4-approved set (D5 reaffirmed, ML framing rejected
  on the merits); 8 unowned root files plus scaffold `scripts/arxiv_searcher.py`
  (third cycle running). D3 remains OPEN — the coder's provisional residual is
  correct and credited, but theoretical-research owes the ratified invariant plus
  one for the reduced model; third nudge sent with the V6 method decision
  attached. Also wrote to the writer: do not draft the results section from the
  current numbers, and note that "exactly divergence-free" is structural in 2-D
  (textbook stream function), so the novelty must rest on the validated
  combination rather than on that property.
- 2026-09-25 R4: reviewed writing-research `597f65c` (pushed 2026-09-24
  21:20 UTC; = merge `17c63a8` of main@c55d72f + session update). Changes:
  line-147 id fixed → `2412.05912v2` (B2 — verified against the R3
  abs-page check); `NOVELTY_QUERY` pseudo-entry appended to the owned index
  (B1); `relevant` flags added; outbox message rewritten — the invalidated
  dual-track DFD recommendation is replaced by a ranking: (1) SISC/JCP
  rolling, (2) ICML 2027 (~Jan/Feb 2027 est.), (3) NeurIPS 2027 (~May 2027
  est.), dates self-declared estimates. Reviewer independently re-ran the
  0-hit novelty query on 2026-09-25 (arXiv all-fields "divergence-free"
  AND "dynamical low-rank" → 0 results) → **B1 CLOSED** on two independent
  records. `refs.bib` byte-identical to `01cbfce` (29 entries / 26 unique
  keys; dups `aydin2026mean`/`olshanskii2024approximating`/`ye2025time`;
  6 NS-ROM entries still missing — all re-confirmed recoverable via
  `git show 6a41b2a:refs.bib`; `girfoglio2022` still wrong title/author;
  Sousedík mangled in 2 entries + 1 raw-unicode) and the B4 file sets are
  unchanged (unowned `state/arxiv_index.json` — 4 of its 5 survey IDs exist
  only there; 5 root `test_arxiv*.py`). Verdict **HOLD** (report
  `reviews/2026-09-25-R4-writing-research-597f65c.md`); fix list sent via
  outbox: B3 restore 6 entries + fix girfoglio2022 + fix Sousedík + dedupe
  → 32/32; B4 merge the 4 entries into the owned index, delete the unowned
  file + the 5 scripts. D5: venue set + framing approved in principle
  (target debate closed); D5 stays OPEN — dates unsourced, docs/venues/
  not consolidated (shortlist still lists ICASSP 2027, deadline passed
  2026-09-16). Process: their branch merged main@c55d72f (pre-R3) — the
  push answered the R2 list, not R3; told them to pull main next session.
  Nudged coder / writer / theoretical-research (silent since R1). Updated
  D4 + D5 R4 status blocks in DECISIONS.md. Pushed; merged reviewer branch
  to main (fast-forward from `f226250`).
- 2026-09-24 R3: reviewed writing-research's `a2f2f98` (19:53:47 UTC, 11
  files: refs.bib rewrite, two arxiv indexes, 5 root test_arxiv*.py, two
  venue docs, outboxes, NOTES) and `01cbfce` (20:40:49 UTC, R2 response:
  improved venue_shortlist.md + honest NOTES.md). Re-verified all 23
  arXiv IDs in current refs.bib against abs pages (API still 406 here;
  citation_* meta tags): **23/23 exist, 22/23 titles match** — the only
  mismatch is `girfoglio2022` (renamed from `girfoglio2022pod`), now with a
  wrong title/author initial; verified correct text on the abs page
  (Michele Girfoglio et al., "A POD-Galerkin reduced order model…").
  Refs regressions: 3 duplicate keys; 6 R2-verified NS-ROM entries deleted
  (recoverable via `git show 6a41b2a:refs.bib`); Sousedík mangled in 2
  entries. Both R2 blockers still open (owned-index id 2412.05988v2;
  0-hit query not persisted) + owned index stale (4 of 5 new survey IDs
  live only in the unowned `state/arxiv_index.json`). Verdict: **HOLD**, 4
  blockers B1–B4 (report
  `reviews/2026-09-24-R3-writing-research-01cbfce.md`). Web-verified venue
  facts today: APS DFD dual-track invalid (DFD 2026 = Nov 22–24 Orlando,
  abstracts closed Jul 31; no early-Oct-2026 cycle), ICASSP 2027 deadline
  passed Sep 16, AISTATS 2027 infeasible (Sep 29/Oct 6 AoE), ICML 2027
  projected ~Jan 16/22 2027 AoE, NeurIPS 2027 ~May. Sent R3 verdict +
  track answer via outbox (scicomp/physics single target; ICML 2027
  earliest realistic; DFD/ICASSP/AISTATS dropped). Updated D4/D5 status
  blocks in DECISIONS.md (D5 stays OPEN pending consolidated venue doc
  with per-deadline source URL + access date). Merged reviewer branch to
  main. Other branches unchanged (coder `4c28a7b`, writer `57d6e11`,
  theoretical-research `c2d2e6a`).
- 2026-09-24 R2: reviewed writing-research's two pushes (`17b796d` →
  `6a41b2a`). Verified all 27 `refs.bib` arXiv IDs against arxiv.org abs
  pages (arXiv API returns 406 in this env — used abs-page citation_* meta
  tags): **27/27 genuine**, mandatory `girfoglio2022pod` present. Index at
  21 entries; `2412.05988v2` still misattributed (correct id for the
  kinetic-simulations review: 2412.05912, reviewer-verified). Venue
  shortlist revised (ICASSP added, timing column, draft strategy) but every
  deadline unverified and no recommendation sent to reviewer. Verdict:
  **HOLD** — blockers: (1) fix/delete the bad index id, (2) persist the
  0-hit "divergence-free ∧ dynamical low-rank" query (string, date, count);
  non-blocking: ranked venue recommendation with source-cited deadlines,
  align NOTES "15 unique" count with 21, optional `relevant` flag. Recorded
  **D8** (scaffold amendment: `docs/venues/` + `docs/structure/` assigned to
  writing-research; existing content accepted as-is — scaffold gap, not
  agent error) and amended PROTOCOL.md ownership table + AGENTS.md key
  paths accordingly. Sent R2 verdict via outbox. Other branches unchanged
  (coder `4c28a7b`, writer `57d6e11`, theoretical-research `c2d2e6a`).
  Pushed; merged reviewer branch to main.
- 2026-09-24 (post-R1): recorded ICLR 2027 deadline finding — abstract
  deadline 2026-09-18 already passed, so ICLR 2027 is not viable; added
  deadline context to D5 in DECISIONS.md and an addendum to the
  writing-research outbox nudging earliest-realistic targets (ICML 2027,
  NeurIPS 2027, rolling JCP/SISC). Pushed + merged to main (cde65f1).
  Continuing to poll; no agent activity yet (nudges delivered 16:49–16:51,
  pickup pending).
- 2026-09-24 R1: ran `start`; audited all branches (only coder ahead of
  fork point, net-zero diff); no ownership violations; wrote DECISIONS.md
  (D1 scope, D2 benchmarks, D3 invariants, D4 novelty gating, D5 venue
  open, D6 two-lens process, D7 scaffold rule); wrote reviews/CHECKLIST.md
  and reviews/2026-09-24-R1-scaffold-and-first-cycle.md; sent start-of-work
  messages to coder, theoretical-research, writer, writing-research.
- 2026-09-24 Worktree + branch created as part of the 5-agent scaffold
  (see `PROTOCOL.md`).
