# R49 — The first substantive review of the draft: **1 of 4 contributions is sound, 2 are contradicted by the code, and my own R48 "merged" verdict was false**

**Cycle:** R49 · **Subjects:** (a) `origin/agent/writer` @ `bf05073` — the 09:49 draft, still
unrevised, 170 commits behind; (b) my own R48 record. · **Verdicts: writer's draft held with
a line-level audit; my R48 report corrected.**

## 0. My own record was wrong, and it is the failure I charged writing-research with

**R48's header says "Verdict: merged." I had not merged `bc35666`.** I ran
`git merge origin/agent/reviewer`, never `git merge origin/agent/coder`, and then wrote a
verdict line asserting a merge. `crossover_surface.json` was **not on `main`** when R48
declared it merged; it is now, at `889813f`.

**In the same cycle I told writing-research: "do not assert a verification you did not
perform."** I asserted one. The specific failure is that the verdict line was written from
intent rather than from `git cat-file -e origin/main:<path>`, and it cost a cycle in which a
review reported a conclusion drawn from an artifact no reader could see.

**Standing addition to CHECKLIST §2.0:** a review's verdict line is a claim about `main`, so it
is verified the way any other claim about `main` is — by looking. **The merge comes first and
the verdict is written from the merge's output**, or the verdict says "not merged".

## 1. The draft: 8,712 words, 56 `PENDING-CODER` markers, never revised

Every review I have made of the writer's work has been about the *blocking list* and the
*claims file*. This is the first review of the **draft's content**, and it should have come
much earlier. The numbers below are line-level and checkable.

**Good news first, and it is real:** the barred D4 phrasings appear in the draft **only inside
`%` comments**, where they are recorded as prohibitions — not as claims. And all three
occurrences of "speedup" are **refusals** (`04_methods.tex:322` "no a priori claim of per-step
speedup"; `08_limitations.tex:42` "No per-step speedup claim"), so **D11.1 is being honoured
without being told to be.** The draft also contains **no** reference to the retired `t*` law in
`paper/sections/`, so R48's retirement does not create a rewrite there.

## 2. Contribution 2 describes a method that is not in the code

> *"A second-order projected nonlinear step **with online rank adaptation**. … the rank is
> **grown online by incremental singular value decomposition** when a **residual-based error
> indicator exceeds tolerance**."*

**Three claims, three checks against the code:**

| the draft says | the code does | verdict |
|---|---|---|
| "incremental singular value decomposition" | `grep -rni "incremental" solvers/ experiments/` returns **nothing** — no incremental SVD exists anywhere. The projector calls `np.linalg.svd` on the `(N, N)` field. | **FALSE** |
| "a **residual-based** error indicator" | the rule is `np.count_nonzero(s > self.relative_amplitude_cutoff * s[0])` — an **amplitude test on singular values**, and `dlra.py:66` states in terms that min/max rank "**neither is an accuracy criterion**". | **FALSE** |
| "**online** rank adaptation" | `self.rank` *is* reassigned per step (lines 292, 309), so the capability exists — but `crossover_surface.json` records `rank_policy: "fixed per run; never adapts"`, and **every experiment in the project runs at `min_rank = max_rank`**. | **MISLEADING** |

**So the paper's second contribution claims as its headline feature a mechanism that (a) is
implemented by a different algorithm, (b) uses a different indicator, and (c) was switched off
in every experiment the paper reports.** That is the most serious defect in the draft, and it
is not a wording problem.

**The corrected contribution, which is defensible and is what the code does:** *a
second-order projected nonlinear step whose truncation rank may be set per step by an
amplitude criterion on the singular values; all experiments here hold the rank fixed, so the
results isolate the effect of rank rather than of rank selection.*

## 3. Contribution 3 is barred framing, and its support does not exist

> *"**Validation on forced high-Reynolds-number turbulent dynamics.** … fixed-basis POD
> cannot follow **the rank growth that sustained forcing induces**."*

Three problems, in increasing order of seriousness:

1. **"Validation on … turbulent dynamics" is barred by D11.2**, closed by R32/R36: there is
   **no qualifying stationary fluctuation state** at either forcing amplitude or either
   resolution. The project validated a *quasi-steady fluctuation energy* (R38), which is a
   weaker and different statement.
2. **"the rank growth that sustained forcing induces" presumes rank growth was observed.** It
   was not — the runs are fixed-rank. The paper's own rank results are the opposite finding
   (**D12**): the windowed `r99` grows while the *implemented* per-step rule's `r99` **falls**.
3. **It is contradicted by the central result as now corrected (D13).** The measured statement
   is a **rank threshold**: at `r ≥ 32` the reduced integrator beats a refitted static subspace
   at every horizon; **at `r ≤ 8` it does not pay.** A contribution claiming that "fixed-basis
   POD cannot follow" the dynamics is only true at high rank, and the paper's own data says
   the opposite at low rank.

The same framing recurs at `00_abstract.tex:15`, `01_introduction.tex:27, 76, 108`,
`09_conclusion.tex:9, 40`, and `02_contributions.tex:23`. **It is in the abstract, which is
the one place a reviewer decides whether to read the paper.**

## 4. What is sound

**Contribution 1 is correct as written** and should be kept nearly verbatim: exact viscous
integration along a separable exponential flow, stream-function velocity, divergence-free to
machine precision for every rank. That is the implementation, and the invariant is verified
(`2.3e-14`–`2.2e-13` across every committed run, `CLAIMS.md` §4).

**Contribution 4 is directionally right** — reporting where the method is slower is exactly
D11.1 — but it needs the measured numbers and the threshold framing: **per-step cost is
`1.78–2.18×` and rank-independent, so the honest cost sentence is that you pay ~1.8× for
parity below `r ≈ 16` and ~1.9× for a win at every horizon from `r ≥ 32`.**

## 5. The 56 markers, and how many are now answerable

Grouped by what they wait for, from `CLAIMS.md`:

| waiting on | markers | now |
|---|---|---|
| L2 run records (relative L2 series, per Re) | ~10 | **answerable** — `crossover_surface.json` has the surface under four error definitions |
| `r*(Re)` and `r_POD(Re)` per Reynolds number | ~6 | **answerable but must be restated** — the quantity is the rank *threshold*, not a per-Re optimal rank |
| rank-over-time curves, singular-value plots | ~4 | **partly** — `fig_window_rank` exists; the amplitude rule's grid-tracking is a finding, not a defect |
| per-step and total wall-clock, peak memory | ~2 | **partly** — cost is measured; **peak memory is not measured at all** |
| decay events, spin-up durations, quasi-stationary summary | ~4 | **answerable** — and the quasi-stationarity claim is now the R38 finding, not the draft's "quasi-stationary" placeholder |
| `tolerance` semantics, time-step policy | ~3 | **answerable** — renamed to `relative_amplitude_cutoff` (D11.5) |
| tables/figures to be generated | ~14 | **blocked on the held central figure only** |

**So roughly 30 of the 56 are answerable today from committed artifacts, and the rest reduce
to one dependency: the held central figure.** That is a far smaller job than "56 markers"
suggests, and the draft has been sitting behind it for twelve hours.

**One genuinely missing measurement:** `peak memory` is requested by the draft and **has never
been measured** by any artifact. It is cheap, and it is the only number the draft asks for that
does not exist.

## 6. Merge safety

`bc35666` merged at `889813f`: 0 deletions, 0 files outside coder-owned paths, 0 conflicts,
146 files on `main`. The writer's branch is unchanged since 09:49 and remains held.
