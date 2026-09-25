# R56 — The highest-quality push yet, and it contains a finding I should have caught twenty cycles ago: **the flow is not the Kolmogorov flow, and the paper names it seven times without ever stating the force**

**Cycle:** R56 · **Reviewed:** `origin/agent/coder` @ `5909af6` (3 files, +215/−2241) ·
**Verdict: merged at `f640244`; 157 files, 0 deletions, 0 files outside owned paths, 0
conflicts.** Two separate things here: the best engineering in the project, and a
correctness-of-description defect that I propagated.

## 1. The best engineering in the project, and it answers two cycles of my complaints

**(a) The stale-schema guard cites D14.4 by name and makes the staleness self-describing.**
`make_summary.py` now checks for the `by_reynolds` layout and, when the artifact predates it,
emits instead of raising:

```python
"status": "stale_schema",
"reason": ("`crossover_surface.json` predates the `by_reynolds` layout, so its numbers
            cannot be read here. Regenerate with `experiments/run_crossover.py`; the
            committed artifact must come from the committed driver (D14.4)."),
"git_commit": crossover_data["provenance"]["git_commit"],
```

**So `benchmark_summary.json` now carries the staleness explicitly, with the command that fixes
it and the commit that produced the stale artifact.** For two cycles I have written that a fix
in the driver is not a fix in the repository; **coder has made the repository say so itself,
permanently, rather than relying on a reviewer to notice.** That is the correct engineering
response to a class of error I could only catch by hand.

**(b) The interpolation is now an instrument, not a convention.** The driver reports
`t_star_loglog` **and** `t_star_linear` — *"They differ, so both are reported rather than one
being passed off as the value"* — plus a **`bracket`** it calls *"the convention-independent
statement"*, plus `status: "resolved"` against `never` kept deliberately apart, and **multiple-
crossing detection**: *"a `t*` that silently ignored a second crossing would be a statement
about the first of several events."*

**That last clause is the oscillation failure mode I found in R48, and coder has engineered it
out of the measurement rather than leaving it in a report.** I diagnosed it in prose, from a
buggy artifact, and turned it into a revision of the central claim. **The right response was to
put it in the instrument, and that is what they did — so the next person cannot repeat my
error.**

## 2. The finding: the flow is not the Kolmogorov flow

`benchmark_summary.json`'s `forcing_name_caveat`, which coder wrote:

> *"The driver calls this a Kolmogorov flow, but the forcing is a periodic unidirectional shear
> `f = (A sin(k y), 0)`, not the Arnold–Korkin–Sinitsyn cellular pump."*

**I verified it against the code, and it is correct.** `solvers/forcing.py`'s own module
docstring states the force is `f = (A sin(k y), 0)`, whose curl is `zeta = -A k cos(k y)` — a
single resolved Fourier mode, divergence-free because `d_x f_x = 0` — and calls it *"the
periodic analogue of the usual Kolmogorov body-force driver."* **The Arnold–Korkin–Sinitsyn
flow is `u = (U sin(αy), -U α sin(αx) cos(αy))`, a cellular pump whose steady state is a
lattice of convection cells and whose stability boundary is the classical Vinograd–Cullen–
Clark result.** A unidirectional single-mode shear is a different flow with different dynamics.

**The naming is genuinely ambiguous in the literature** — periodic unidirectional shear is
itself often called a Kolmogorov (shear) flow in the mixing and Boussinesq-instability
literature — so this is a real hazard rather than a pure error. **But CHECKLIST 1.3 asks that
the forcing match what the name claims, and it does not.**

## 3. Where the error lives, and it is worse than a naming slip

| location | mentions | what it says |
|---|---|---|
| `paper/sections/04_methods.tex` | 2 | *"single-mode **Kolmogorov forcing**"*; *"the system possesses the **Kolmogorov equilibrium**"* |
| `paper/sections/05_experimental_setup.tex` | 1 | *"The main experiments are forced **Kolmogorov-flow** runs"* |
| `paper/sections/06_results.tex` | 1 | figure caption *"forced **Kolmogorov flow** at…"* |
| `paper/sections/07_discussion.tex` | 1 | *"classification of **Kolmogorov flow** of Vinograd, Cullen, and Clark"* |
| `solvers/forcing.py`, `run_kolmogorov.py` | — | the class is literally named `KolmogorovForcing` |
| **the draft's forcing formula** | **0** | **the draft never states the force anywhere** |

**Two consequences, and the second is serious.**

1. **The paper invokes the Kolmogorov equilibrium and the cellular-flow stability
   classification, neither of which applies to the implemented force.** The reference is
   pointing at a literature about a different flow.
2. **The error is invisible from the paper alone, because the paper never gives the force's
   formula.** It survived twelve hours, 55 review reports, and my own reading — I reviewed
   `04_methods.tex` and `05_experimental_setup.tex` in R49 and did not check what `f` was. **I
   asserted "Kolmogorov flow" in six of my own review reports (10 mentions) without ever opening
   `solvers/forcing.py`.** That is my miss, and the fix is the standing one: **I reviewed a
   claim the paper makes about itself, in the paper, and did not verify it against the code.**

## 4. The connection to D11.2 that I had not seen, and it matters

**D11.2 barred "turbulent dynamics" because R32/R36 found no qualifying stationary fluctuation
state at any forcing amplitude or resolution.** I had read that as a fact about *the flow*.

**It is a fact about the implemented force.** The Arnold–Korkin–Sinitsyn Kolmogorov flow
**has** a well-known steady cellular state, and the literature the draft cites is precisely
about it. So the absence of a stationary state is **not evidence about Kolmogorov flow at all** —
it is what one should expect from a periodic unidirectional shear, which has no steady cellular
attractor.

**This weakens one of my own findings and it should be weakened.** R32/R36/R38 remain correct
*as measurements of this forcing*, but "there is no statistically steady state" must not be
presented as a property of the flow the paper names, and the paper cannot claim to be studying
the Kolmogorov flow's transition to turbulence.

## 5. The options, and only one is feasible

**(a) Implement the AKS pump.** A real change to the forcing, and it would **invalidate every
measurement in the project** — all of which was run on a single-mode shear. Not feasible now,
and the project would be starting again.

**(b) Rename the flow honestly and re-scope every claim that used the name.** The paper
studies **forced 2-D incompressible NS with a single-mode periodic unidirectional shear**. The
setup section must **give the force's formula**, which it currently never does. The
"Kolmogorov equilibrium" and the Vinograd–Cullen–Clark classification must go, or be retained
only with an explicit statement that they describe a different flow. **And "no stationary
fluctuation state" must be re-attributed from the flow to the forcing.**

**(b) is the only honest option available, and it costs the paper its recognisability** — which
is a real trade, and one a reviewer should be told about rather than discovering. I record it as
a trade, not as a free fix.

## 6. Merge safety

0 deletions, 0 files outside `experiments/` and `state/coder/`, 0 conflicts. Merged at
`f640244`; 157 files on `main`. `benchmark_summary.json` shrank by 2 241 lines because the
summary no longer duplicates the surfaces, and gained the `peak_memory` block with its `git_commit`.
