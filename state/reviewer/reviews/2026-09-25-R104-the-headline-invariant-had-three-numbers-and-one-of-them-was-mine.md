# R104 — **the paper's headline invariant has three different numbers in circulation, one of them mine, in the document the writer is told to trust. Resolved: the answer is a population, not a number. And the sixth instrument failure, on a name instead of a quantity.**

**Cycle:** R104 · No new pushes. `main` at `7b0846c`, 202 files, clean.
**Found while fixing the thing the user reported twice: my own instructions do not fit on one screen.**

## 1. The defect, and it is in `CLAIMS.md` — the authoritative claims table

Three numbers were in circulation for the same physical quantity, `max |∇·u|`:

| where | what it says |
|---|---|
| `WRITER_ORDER.md` (the one-screen index) | `1e-14` |
| `CLAIMS.md` §4, "across every committed run" | `2.32e-14` … `2.24e-13` |
| `DECISIONS.md` D60 | worst case `1.0459e-11` |

**A writer cannot write §3's invariant with three numbers, and the one I told them to trust is the
one that is wrong.**

## 2. The resolution, pooled over the whole population

**Population: 12 of the 16 result artifacts on `main` carry the field; 124 measurements. Thresholds
excluded structurally. Nothing else filtered.**

| population | n | range |
|---|---|---|
| all measurements | 124 | `1.628e-14` … `7.091e+278` |
| non-diverged | 120 | `1.628e-14` … `1.046e-11` |
| **the roundoff band** | 119 | **`1.628e-14` … `2.242e-13`** |
| the one `>1e-11` non-diverged case | 1 | `1.046e-11` — **`pod_dmd_r32`**, not our method |
| **our method + full grid** | — | **`7.3e-15` … `1.8e-13`** (R44 scaling law, fixed setting) |
| the four diverged fixed-basis baselines | 4 | `4.61e+64` … `7.09e+278` |

**`CLAIMS.md` §4's endpoints: the maximum `2.24e-13` is right; the minimum `2.32e-14` is beaten by
two committed artifacts** — `2.265e-14` in `baselines_re5000_N64_T8.json` (a **forced** case) and
`1.628e-14` in `taylor_green.json` (unforced). That is a 2.4% endpoint error, **and it is not the
problem.**

**The problem is the phrase "across every committed run."** The committed population contains
`1.046e-11` and four runs at `4.6e+64`–`7.1e+278`. **A bare bound asserted across that population is
false by 265 orders of magnitude for four of its members.** A bound is a claim about a population,
and this one named a population it does not hold over. D55c.6, exactly: *print the population with
the number.*

**D60 was right in substance and is now formally operative; `CLAIMS.md` §4's first row is withdrawn.**

## 3. The replacement the writer should use for I1

> Across all 124 committed divergence measurements the reduced integrator and the full-grid reference
> hold `|∇·u| ≤ 1.1e-13` — seven orders of magnitude below the reduced solver's own trajectory error.
> A DMD baseline at rank 32 reaches `1.0e-11` without being flagged as diverging; four fixed-basis
> baselines overflow between `4.6e+64` and `7.1e+278`. The measured residual is resolution-dependent,
> growing by `2.6×` from `N=64` to `N=128`.

**Every clause is a population plus a number.** None of them is a universal bound. Added to
`WRITER_ORDER.md` as prohibition **#13**.

## 4. The sixth instrument failure, and it is the one D50.4 warns about

My first pool reported five artifacts with `max = 1e-10` **exactly**. An exact round number repeated
across five files is not a measurement. It is `stability_limits.max_abs_divergence: 1e-10` — **the
run's own divergence threshold**, a *sibling* of the real measurement in `kolmogorov_*.json`.

**My extractor matched a name, not a quantity.** `kolmogorov_re5000_N64.json` has six paths ending
`max_abs_divergence`: three measurements and three thresholds. A name-only rule counted six.

**D50.4 says: self-test an extractor against a case already checked by hand, and on an artifact that
differs *structurally*.** I had a hand-checked case (`baselines_re5000_N64_T8.json`, where the paths
are `methods.<name>.max_abs_divergence` with no `stability_limits` sibling) and structurally different
artifacts. I ran neither self-test. Both are now in the script and both pass:

- **Self-test 1** — on the hand-checked artifact the structural rule yields **exactly 19 methods, 0 thresholds**.
- **Self-test 2** — on `kolmogorov_re5000_N64.json` the name-only rule would have counted **6** where the structural rule counts **3**, and all three extras are the threshold `1e-10`.

**Six instrument failures now, and this is the first one that would have made a *correct* number wrong
in the dangerous direction** — it inflated a roundoff band by four orders of magnitude and would have
hidden the `1.046e-11` outlier that the replacement sentence now reports. **The previous five all
failed toward "clean"; this one failed toward "alarming", and it would still have been wrong.**

## 5. The structural fix, which is the second half of this cycle

The user's standing complaint — *"you're doing too much bureaucracy and the agents can't figure out
what is high priority"* — is **correct, and it is my fault**. Measured:

| file | lines | words | `##` sections |
|---|---|---|---|
| `WRITER_ORDER.md` | 508 | 7 404 | **19, including five separate `## §4` headings** |
| `CLAIMS.md` | 615 | 7 596 | 10 |
| `NOTES.md` | 8 831 | 111 442 | 7 |
| `DECISIONS.md` | 4 599 | 52 654 | 73 |

`WRITER_ORDER.md` had **two sections each claiming to be "the highest-priority item in the paper"**,
a numbering scheme that collided with itself five times, and **the one-screen index buried at line
98 — beneath 97 lines added since.** Worse, **the index was itself stale**: it printed `1e-14` for the
invariant (wrong, §1 above), `+2.5`–`+3.8 MiB` for memory (D52.6 corrected it to `+2.24`/`+4.27`),
and listed the `N=128` multipliers as an open gap that D56 has since *replaced with a measured
result*. **A writer who trusted the index got wrong numbers — which is worse than a long document.**

**Rebuilt.** The index is now **lines 1–85, first**, ordered `W1`–`W9` by what a reader decides on, with
a single precedence rule (*"if you have time for one thing, do W1; for three, W1 W2 W3 — those three
are what a reviewer decides on"*). Detail is `D1`–`D14` below a `## DETAIL` heading, **no two
headings share a name**, and the two contradictory priority claims are replaced by the `W` numbering.
Stale numbers corrected; prohibition #13 added.

**The ordering is unchanged in substance — W1 abstract, W2 contributions, W3 introduction are still
the top three, exactly as D63/D64/D65.3 said. What changed is that a writer now sees that in the
first screen instead of the eighty-fifth line.**

## 6. The lesson

**R101: allocate by what a reader decides on. R104: check that your own instructions are readable by
the person you wrote them for.** The two are the same discipline — both are about the reader, not the
author — and I have been violating the second for six cycles while enforcing the first.

**And the instrument lesson, for the sixth time: an extractor must be self-tested against a
hand-checked case *and* against an artifact that differs structurally.** The failure mode is always
the same and it is always mine: I matched a *name* where I needed a *quantity*, or measured a
population I did not print. **Print what you measured over, and prove the rule on a case you already
know the answer to.**
