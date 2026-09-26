# R105 — **the draft describes the static baseline's energy threshold as 99.9% where the runs used 99% — a 10× over-statement that makes the baseline look more expensive, and so flatters our own method. Found by an instrument that had to be deleted and rebuilt, and the rebuild is the deliverable.**

**Cycle:** R105 · No new pushes. `main` at `98c4732`, 203 files, clean.
**Lens 1 (correctness), and specifically "do we do enough tests": the missing test was one that checks the
paper against the artifacts. It now exists, and the first thing it found is a substantive defect.**

## 1. The finding: `99.9%` where the runs used `99%`

The draft states the static-POD baseline's truncation as **99.9%** in three places —
`04_methods.tex:288`, `05_experimental_setup.tex:86`, `06_results.tex:133`. **The runs used 99%.**
Four independent pieces of evidence, none of which is the draft:

| evidence | what it says |
|---|---|
| `state/coder/results/baselines_re5000_N64_T8.json` | `parameters.energy_fraction = 0.99` — the value **recorded by the run** |
| `experiments/run_baselines.py:380` | `add_argument("--energy-fraction", type=float, default=0.99)` |
| `solvers/dlra.py:51` | *"`rank_criterion="energy"` keeps the smallest r with `sum(s[:r]**2)/sum(s**2) >= energy_fraction` — **an r99-style rule**"* |
| `experiments/test_engine.py` | `energy_fraction=0.99` in every criterion test |

**So the rule that was run and tested is r99, and the paper describes r99.9.**

**The direction is what makes this a serious defect rather than a typo.** A *stricter* energy
threshold yields a *larger* baseline rank. The paper therefore describes the static baseline as
**more expensive than the one we actually ran** — which makes our own reduced integrator look
better than the comparison deserves. **It is a self-serving error, and it is the kind a reviewer
finds in thirty seconds** because the number is checkable against a default in the code.

This is also independent confirmation of **D60.3**, which had flagged I3 as "a measurement never
performed" with the note `energy_fraction: 0.99` not 99.9%. **D60 was right, and now there is a
number attached to it rather than a note.**

## 2. The instrument that found it, and the one that had to be deleted

**Attempt 1 — search. Deleted.** I built a checker that extracted every numeric literal from the
draft and searched a 34,775-value population of artifact leaves for a match. It reported
**134/134 EXACT** — and I distrusted it, because the population spans `-0.0087 … 7.09e+278`, so
almost anything matches something. Measuring the margins confirmed the distrust: **72 of 134
literals were "matched" by 16–351 population values.** A match satisfied by 351 candidates
verifies nothing.

Adding a topical filter made it worse before better, and this is the part worth recording:

- the same draft number was classified **DECISIVE**, then **COINCIDENCE**, then **SUPPORTED** across
  three successive fixes to the disambiguation heuristic;
- `5000 → parameters.re` — a **correct** match, since `re` is the Reynolds number — was rejected as
  a coincidence because the key name is **two characters long**;
- and the filter's first success was a **false positive of exactly the kind I was hunting**: it
  matched the draft's `99.9` to `99.89971226 = instantaneous_rank_series[575].sigma_1`, a leading
  singular value. **I had kept the values and thrown away the names, so a claim about an energy
  fraction was verified against a singular value.**

**A search over a population of nameless numbers needs semantics to disambiguate, and heuristics
for semantics are unstable. I deleted it rather than tune it further.**

**Attempt 2 — name the numbers. This one works.** `state/reviewer/claims_registry.py` inverts the
question: do not search the artifacts for the draft's numbers, **name** them. Each claim is
`(id, artifact, key path, selector, field, value, precision)`.

```
OK   tstar_r16              crossover_surface.json:by_reynolds.5000.crossovers[{rank:16,window:0.25}].t_star
     0.6493281145096707
OK   dealias_ceiling_N128   cost_retiming.json:grids[{N:128}].dealias_rank_ceiling
     85
OK   div_worst_nondiverging baselines_re5000_N64_T8.json:methods.pod_dmd_r32.max_abs_divergence
     1.0459189070388675e-11
...
13/13 verified, 0 failed
```

**No search, no semantic guessing.** Three parts: **VERIFY** every entry against its key path;
**POLICY** check thresholds the draft may over-state; **COVER** report high-precision literals in the
draft that no registry row accounts for.

**Three properties that make it trustworthy, each of which the search version lacked:**

1. **A wrong path is an ERROR, not a silent skip.** It caught **my own bad path** on the first run —
   I had written `crossovers.…` when the real key is `by_reynolds.…`. Under the search design that
   mistake would have looked like "number not found" and I would have gone looking for a typo in the
   paper instead of in my registry.
2. **Selectors instead of indices,** because these artifacts get regenerated.
   `crossovers[{rank:16,window:0.25}]` survives a re-run; `crossovers[9]` does not.
3. **It is self-verifying and it is controlled.** Positive control: injecting `1.2345` into a copy
   of the draft is reported. Negative control: injecting `0.6493` and `2.0800` is **correctly not**
   reported, because they round-match `0.6493281145096707` and `2.0800072205298386` at 4sf. **A
   detector that has never fired is not a detector, and a "0 uncovered" result from an untested
   checker is the same all-clear-from-nothing I have now produced five times.**

**Two bugs of my own, both found by the instrument refusing to report cleanly:**

- `sig_figs` counted a bare integer's trailing zeros as significant, so `1000` read as 4sf and every
  Reynolds number in the draft became a false "uncovered" finding — **25 of them.** A bare integer's
  trailing zeros are not significant figures; only a decimal point or an exponent makes them so.
- the `@min:` aggregate for the cost extremum did not descend from the grid dict into `rows`.

## 3. A bonus the registry handed me for free

`dealias_rank_ceiling` is **43 / 85 / 171** at `N = 64 / 128 / 256`. This is the *third* independent
confirmation of D30 — `43` is a wavenumber count, never an accuracy result — and it confirms the
`N=128` crossover now in flight is run at exactly that grid's ceiling (`--ranks … 85`), so the
refinement is a proper one.

## 4. The lesson

**Naming beats searching, and an unverified check is worse than no check.**

The first instrument was more sophisticated and produced nothing but false confidence, because it
tried to answer "is this number in the data?" — a question that needs semantics. The second is
dumber and answers "does this named path hold the value I claim?" — a question arithmetic can
answer. **When a check needs a heuristic to disambiguate, the check is in the wrong shape.**

And the standing process point, for the seventh time: **I built an instrument, got a clean-looking
result, and distrusted it because the population was too large to support it. That instinct was
correct and it is the only reason the `99.9` defect surfaced at all** — it surfaced as a *false
positive* inside a check I had already decided not to believe.
