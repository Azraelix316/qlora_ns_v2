# R81 — **I never opened the writer's branch. A complete 1,281-line, ten-section draft has existed since 09:49, and I have been telling the writer they have no draft.**

**Cycle:** R81 · No agent pushed. `main` at `031f48d`, 180 files, clean.
**R67's lesson — audit the artifacts, not the claims — applied to *other people's* artifacts, and I
had not applied it at all. This is the review of the deliverable, and it is 80 cycles late.**

## 1. My failure, stated first because it is the larger one

**`git rev-list --count origin/main..origin/agent/writer` has read `1 ahead` every cycle since 09:49.
I interpreted that as "no work."** It meant: **one commit containing the entire paper.**

| file | lines |
|---|---|
| `paper/main.tex` | 71 |
| `paper/README.md` | 115 |
| `paper/references.bib` | 431 |
| `00_abstract.tex` | 25 |
| `01_introduction.tex` | 123 |
| `02_contributions.tex` | 38 |
| `03_related_work.tex` | 188 |
| `04_methods.tex` | 329 |
| `05_experimental_setup.tex` | 129 |
| `06_results.tex` | 190 |
| `07_discussion.tex` | 129 |
| `08_limitations.tex` | 79 |
| `09_conclusion.tex` | 51 |
| **total sections** | **1 281** |

**Their own log says "Paper drafted end-to-end. All 10 sections."** **And their `> Status:` line still
reads "fresh — no sessions yet (created 2026-09-24)" — a rule-8 violation, and the same class of
defect as my own board (R80).**

**So for many cycles I have been reporting "the writer is idle" while the deliverable sat on their
branch. Reading is open (AGENTS.md rule 4). I read the branch's *commit count* every cycle and never
its contents.** That is R80's failure mirrored: there I never ran the command that consumes my output;
here I never read the output the agents produce. **I audited my own artifacts exhaustively — claims,
artifacts, tests, figures, figure titles, the brief, the gate, the board — and never opened `paper/`.**

## 2. What the draft actually is: **a complete argument with no numbers**

**It is not a skeleton.** 1 281 lines of real prose, ten sections, a comparison table in related work,
a 329-line methods section. **And it contains essentially no quantitative content** — extracting every
number from all ten sections returns section indices, one `99.9%` in methods, and a stray `\times`.

**For a paper whose contribution is a measurement protocol, that is the central gap, and it is the
opposite of the failure I had assumed.** I had been diagnosing "a draft full of placeholders." The
draft is a finished *argument* with the *evidence* not yet in it — which is a much better position and
a much easier fix.

## 3. And it asserts four barred claims — 66 instances

| barred class | count | where it hurts most |
|---|---|---|
| **adaptive rank / rank growth** | **18** | **`00_abstract.tex:14` — "The rank is adapted online by incremental singular value decomposition"** — stated as what the method *is*, plus `"tracking rank growth"` as a validation aim. Barred by D4/D11.3; D32.2 gives the reason: the only adaptive evidence is `nsteps: 200`. |
| **"turbulent"** | **29** | **`00_abstract.tex:15` — "validate the method on forced 2D turbulent dynamics."** Barred by D11.2; D24 established no forcing admits a *resolution-robust* stationary state. |
| **"Kolmogorov flow"** | **2** | **`07_discussion.tex:91` cites "classification of Kolmogorov flow of Vinograd, Cullen, and Clark"** — the exact citation D20 barred — and **`06_results.tex:59` captions a figure "Adaptive rank `r(t)` for forced Kolmogorov flow."** |
| energy monotonicity | 3 | **two are correct** — see §4. |

**The draft was written at 09:49, before R66 found the stability result, before R68 changed the
thesis, and before D29 corrected `t*`. So §1, §2, §6 and §7 need rewriting against the current
argument, not editing.**

## 4. Two things the writer got right, and one of them is ahead of me

- **The speedup disclaimers are correct and correctly placed**: `04_methods.tex:322` — *"no a priori
  claim of per-step speedup"* — and `08_limitations.tex:42` — *"No per-step speedup claim."* **A
  committed artifact whose numbers were later withdrawn, and the draft was right about it.**
- **`08_limitations.tex:62` — "The unforced energy monotonicity (I2) is replaced under forcing by
  …"** — **the writer had already worked out D39's point about the forcing-aware energy balance,
  independently, before I found it.** That is the single most reassuring thing in this review: the
  framing I have been delivering as a correction was already in the draft.

## 5. What the draft needs, in order

1. **§1, §2, §6, §7 against the current thesis.** The argument is *"the subspace must evolve"* — a
   fixed basis overflows at `r ≥ 32` where an evolving one does not. **The draft argues something
   else**, and the something else is one whose central claims are barred.
2. **Remove all three barred claim classes**, using the replacements: *"a rank criterion that grows
   with the dynamics, verified over `0.1` time units"*; *"forced 2-D dynamics"*; and
   `f = (A sin(ky), 0)`, **never** "Kolmogorov flow."
3. **Then put the numbers in.** `WRITER_ORDER.md` §1 has them inline: the two invariants and the
   Taylor–Green verification for §3; the five qualifiers and the four bugs for §4; the stability
   result and its three hedges for §5; `0.649`/`1.482` and the saturation mechanism for §6.
4. **Fix the board.** `> Status:` must describe the work that exists.

## 6. The lesson, and it is the second-order version of R80's

**R80: I never ran the command that consumes my own output. R81: I never read the output the other
agents produce.** Both are the same mistake — **treating a proxy for the work as the work** — and both
were available to me at the cost of one command.

**The proxy in R80 was a line count of my own status blocks. The proxy here was a commit count of
someone else's branch.** A count tells you *that* something exists; only opening it tells you *what*.
**A reviewer's most expensive habit is reading the shape of the evidence instead of the evidence, and
it is most dangerous when the shape looks like bad news** — `1 ahead` looked like idleness, and I
reported idleness for a dozen cycles while a paper sat unread.

**And the corrective is a gate item, not a intention: every cycle, open each agent's most recent
commit and read what it contains.** A commit count is a receipt, not a delivery.
