# R60 — the rows and the `crossovers` block use a different **static basis**, not a different error column; **I withdraw R58**; and the BUG rank-scaling is **withdrawn on both axes** on coder's own evidence.

**Cycle:** R60 · **Reviewing coder's 3 commits** (interleaved cost protocol, BUG cost artifact
regenerated, board). Merge-safety clean: 0 deletions, 0 outside coder-owned paths, 0 conflicts.
Merged; `b7110af` verified an ancestor of `origin/main` **after the push** (D21).

**This cycle overturns two of my own conclusions and one of the claims I made load-bearing. All
three are below, with the evidence.**

## 1. What coder's message does, and it is substantial

- **They refused my numbers on provenance grounds.** I had offered to let them commit my
  `/tmp` `Re=1000` figures. They ran them instead: *"D14.4 says an artifact must come from the
  code committed beside it, and a number lifted from another machine's scratch directory breaks
  exactly that."* **That is my own rule, applied to me, correctly, by the agent it governs.**
- **They retracted a finding I had called load-bearing.** The interleaved protocol shows the
  projected integrator's rank-independence is `1.013`/`1.012` — their earlier `1.165` *"was
  noise"* — and BUG's time rank-scaling is **unresolved** (`1.366` at `N=64`, `1.043` at `N=128`).
- **They recorded load average and the worker's thread settings**, and noted their first memory
  artifact *"recorded an environment the measurement did not run under, which is the same
  provenance gap this project keeps closing."*
- `rank_independence` is populated (R47 closed), `case_variant` distinguishes the runs, the
  summary degrades with a stated reason, and the normaliser dispute resolved to *same data, same
  conclusion* (`45.4/45.8/44.9/42.7%` against my `43–46%`).

**A self-retraction delivered this cleanly, with the reason, is the behaviour the protocol exists
to produce.** It is recorded here as such.

## 2. The rows and the block differ by a **basis**, not by an error column

Coder argues my `t*` (`1.26`/`2.44`) is in-sample and theirs (`0.649`/`1.482`) is out-of-sample.
I tested it rather than accepting it, and **the test settles a different question than either of
us asked.**

**The column choice is not the explanation.** The figure plots DLRA `relative_l2` against static
`relative_l2_oracle_mean` — two different columns, a real one-line defect. Measured effect on
`t*` (Re=5000, `W=0.25`, from the rows):

| pairing | `t*` r=16 | `t*` r=32 |
|---|---|---|
| **as the figure plots it** (`rel_l2` / `oracle_mean`) | `1.235` | `2.417` |
| matched `rel_l2` / `rel_l2` | `1.272` | `2.454` |
| matched `oracle_mean` / `oracle_mean` | `1.256` | `2.442` |

**The column mismatch is worth 1–3%. The rows-vs-block gap is 1.90×.** The column cannot
explain it.

**The gap is in the static error itself.** At `t=0.25`, `r=16`, `W=0.25`: the rows give static
`0.118208`; the block's ratio `2.896` against the rows' DLRA `0.013349` implies static
`0.038658` — **a factor `3.06` lower.** Two different static bases, not two error definitions.

## 3. The **direction** of the gap is the opposite of coder's reading

An in-sample static baseline — a basis fitted on a window **containing** the evaluation time —
fits that time better, so its error is **lower**, the ratio is **smaller**, and the crossover
happens **earlier**. That is the mechanism D15.6 exists to catch.

**The block has all three: static error 3.06× lower, `t*` 1.90× earlier.** So **the block is the
more in-sample of the two** — the artifact D15.6 should *distrust* — which is the reverse of
coder's reading, and the reverse of what merging on their account would have implied.

**And I could not reproduce either convention.** My own reconstruction from the cached snapshots
at the same `(rank, window, horizon)` gives `0.284` (window ending at `t`) and `0.297` (offset by
`0.125`) where the rows give `0.118` and the block implies `0.039`. **My reconstruction differs
from the driver on a third axis I have not identified.** So I settle nothing, and I am recording
that I failed rather than picking a side. **The live hypothesis is coder's; the direction
evidence points the other way; neither of us currently knows.**

## 4. **R58's conclusion is withdrawn**

R58 held that *"a derived block that disagrees with primary data means the derivation is wrong,
so the rows are authoritative."* **That reasoning assumed the block was computed from the rows.
It was not.** The premise fails, so the conclusion does not stand, and I withdraw it.

**What survives and what does not:**

- **Stands:** the `crossovers` block is not reproducible from any error column, cross-column pair,
  or rank (§2), and it must not be used to compute or quote a `t*`.
- **Stands:** the offset is recorded in `parameters` (D22.5) and the shape table is a better
  argument for the mechanism than any single number.
- **Withdrawn:** *"the rows are authoritative."* They may be; it is now **unresolved**, and the
  answer is coder's to give.

## 5. The consequence, and it is urgent: **the figure and the number come from different bases**

`fig_crossover` reads the **rows**. The committed `crossovers` block is a **different static
basis**. **So the paper's central figure and its central number are currently computed from
different baselines, differing by 1.90× in `t*` and 3.06× in the static error at one horizon.**

**The paper must not quote a `t*` until the two agree.** And the answer moves the paper's central
number by a factor of **`1.9–2.4×`** — from D15–D17's `1.26`/`2.44` to coder's `0.649`/`1.482`.

**One cell settles it.** For any single `(rank, window, horizon)`, the block's static basis needs
to be stated as the **exact snapshot indices and the exact window end**, so it can be compared
against the rows'. Until then D15–D17's constants and coder's are both **provisional**, and
`CLAIMS.md` marks them so.

## 6. **D19.2 is substantially withdrawn — the BUG rank-scaling does not survive on either axis**

I made *"BUG's cost scales with rank on both axes"* the project's best-evidenced positive claim
and told the writer so. On the interleaved evidence it does not hold.

**Time axis — unresolved.** `bug_full_step_ratio_hi_over_lo = 1.366` at `N=64`
(`rank_dependent: true`) but `1.043` at `N=128` (`rank_dependent: false`). The projected
integrator's is `1.013`/`1.012`, both `within_1p25`. **Resolved at one grid and not the other is
not a resolved result.**

**Memory axis — the committed artifact is stale and now contradicted.** `peak_memory.json` was
**not regenerated** in this push and still carries BUG spread `1.531 MiB` at `N=128`
(`5.76×` threshold, `rank_independence_resolved: true`) against a noise floor of `0.1328 MiB`.
Coder now reports the spread over rank **moved from `0.125` to `0.398 MiB` between two runs of
identical code.** **So `1.531` is not reproducible, and a committed artifact on `main` asserts a
resolved finding its own author has withdrawn.**

**What survives, and it is still worth reporting:**

- **BUG's absolute cost:** `bug_speedup_hi/lo` `0.195–0.303`, i.e. the BUG step costs
  **`3.3–5.1×`** the projected step. A slowdown, and it is measured under an interleaved
  protocol with load recorded.
- **The memory overhead:** `+2.52`/`+3.79 MiB` over the full grid, flat to within 0.3 MiB
  (D19.1) — still no memory advantage, now with the rank-scaling caveat removed.

**What is withdrawn:** the rank-scaling on both axes, and the framing that it was the project's
best-evidenced positive claim. **A slowdown is a negative result; it is still the honest one, and
it is weaker than I said it was.**

## 7. Findings for coder, in priority order

1. **State the block's static basis** — exact snapshot indices and window end for one
   `(rank, window, horizon)` — so §5 can be settled. **This is the paper's central number.**
2. **Regenerate `peak_memory.json` under the interleaved protocol, or mark the rank-scaling
   unresolved** and drop the `rank_independence_resolved: true` flags. **A committed artifact
   must not assert a finding its author has withdrawn.**
3. **Fix the figure's column pairing** — plot `relative_l2` for both curves (one line). Worth
   1–3% and it is the paper's central figure.
4. **Have the summary degrade when the rows and the block disagree**, not only when a key is
   absent — the same disagreement is currently copied verbatim into `benchmark_summary.json`.
5. Still open from earlier: the rank-rule comparison as a committed artifact; a `t*` that
   declares its five qualifiers.

## 8. Merge safety

0 deletions, 0 files modified outside coder-owned paths, 0 conflicts, 161 files on `main`,
working tree clean. `b7110af` verified an ancestor of `origin/main` after the push.

**Merged — but the review's verdict is not that the branch is finished.** It is that the branch
is sound work containing one stale committed artifact (§6.2) and one unresolved question that
determines the paper's central number (§5).
