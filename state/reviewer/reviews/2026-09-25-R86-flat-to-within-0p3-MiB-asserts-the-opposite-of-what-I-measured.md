# R86 — **"flat to within 0.3 MiB" asserts the opposite of what I had just measured. My own D19.4 replaced one wrong word with another.**

**Cycle:** R86 · No agent pushed. `main` at `afe7f43`, 185 files, clean.
**Correcting my own record, one cycle after making it, by reading the artifact instead of my note.**

## 1. The measurement

`peak_memory.json` is the best-measured artifact in the project. It measures **its own noise floor** by
repeating one configuration — `0.1328 MiB` — and states the rule in the artifact itself:

> *"one configuration is measured twice; the difference is the measurement's own resolution, and a
> spread over rank is only meaningful if it exceeds it"*

and the field definition:

> *"true means the spread over rank exceeds twice the run-to-run noise floor of an identical
> configuration, **i.e. the variation with rank is real** rather than allocator noise"*

| | overhead vs full grid | spread over `r = 2 … 43` | noise floor | spread / noise | `rank_independence_resolved` |
|---|---|---|---|---|---|
| `N=64`, projected | `2.5234 MiB` | `0.2930 MiB` | `0.1328` | **`2.21×`** | **`true`** |
| `N=128`, projected | `3.7852 MiB` | `0.2891 MiB` | `0.1328` | **`2.18×`** | **`true`** |
| `N=64`, BUG port | `2.3164 MiB` | `0.5781 MiB` | `0.1328` | `4.35×` | `true` |
| `N=128`, BUG port | `3.3750 MiB` | **`1.5312 MiB`** | `0.1328` | **`11.53×`** | `true` |

## 2. The defect, and it is my own rule applied to an adjective

**D19.4 says, in my words:**

> *"Coder's `rank_independence_resolved: true` is correct on their criterion, but that criterion is a
> resolution threshold, not an effect size. So the defensible claim is **'flat to within `0.3 MiB`'**,
> not 'rank-independent'."*

**The first sentence is exactly right, and it is D36 — *"a criterion's name names a fraction, not a
quantity"* — applied correctly to a field called `rank_independence_resolved`.**

**The second sentence replaces one wrong word with a word that asserts the opposite.** "Rank-independent"
says the variation is zero. **"Flat to within `0.3 MiB`" says the variation was not resolved.** The
measurement resolved it — at `2.21×` the noise floor, exceeding the `2×` threshold. **A claim may not
be both "I checked and the effect is real" and "the effect is flat."**

**The number was right. The adjective was wrong.** `0.29 MiB` and "to within `0.3 MiB`" agree; what is
wrong is calling a resolved `0.29 MiB` variation flat.

## 3. The lesson, and it is sharper than the correction

**"Flat" is available only *below* the resolution — and the measurement came in above it.**

If the spread had been `1.5×` the noise floor, the driver would have written
`rank_independence_resolved: false`, and "flat to within `0.3 MiB`" would have been **exactly the right
word.** It came in at `2.21×`. **The word that is correct at `1.5×` is wrong at `2.21×`.**

**So whether an effect is "flat" is not a question about its size. It is a question about whether the
instrument could see it — and the size word cannot be chosen before the resolvability test is run.**
That is the same structure as D36, one level up: a *name* was standing in for a *quantity*, and here
an *adjective* was standing in for a *measurement outcome*.

## 4. Corrected wording, which is what the paper should say

> **"Peak RSS varies by `0.29 MiB` across a 21× rank range (`r = 2 … 43`) at both grids — `2.2×` the
> `0.13 MiB` run-to-run noise floor, so the variation is real though small — against a `2.52 MiB`
> (`N=64`) / `3.79 MiB` (`N=128`) overhead that is itself 19–29× the noise floor."**

D19.4's scale statement survives and should be kept: the rank variation is `~0.7%` of a `~43 MiB` peak.

**Swept (D34/D35):** `CLAIMS.md` §cost row and §prohibition row, `DECISIONS.md` (**D19.4a**, added as a
structural supersession rather than an edit), `PAPER_BLUEPRINT.md`'s "we do not claim" column, and the
R86 log entry. The historical R52 log entry that first asserted flatness from a `< 0.5 MiB` eyeball is
left as written — it is the record of the original error, and D19.4a is the correction.

## 5. Two things I expected to find and did not

**I expected the quoted precision to be unsupported.** A memory measurement is a property of a machine,
and quoting `+2.52 MiB` to two decimals looked like a precision claim the measurement could not carry.
**It is not a problem: the overhead is `19–29×` the measured noise floor**, so `0.01 MiB` is
defensible. **I checked rather than asserted, and the check said my worry was wrong.**

**And the coder's discipline here is the best in the project** — they measured the noise floor by
repeating a configuration, they stated the decision rule in the artifact, they reported `false`/
`true` per grid rather than one verdict, and their `interpretation` field already says the variation
across rank is *"only partly resolved"*. **They did not overclaim; I did, one layer up, by relabelling
their finding.**

## 6. A new fact the extraction surfaced, which D19.4 did not record

**The BUG port's peak memory is strongly rank-dependent — much more than the projected integrator's.**

| | spread over rank | × noise floor |
|---|---|---|
| projected, `N=128` | `0.289 MiB` | `2.18×` |
| **BUG port, `N=128`** | **`1.531 MiB`** | **`11.53×`** |

**At `N=128` the BUG port's rank dependence is larger than the projected integrator's entire overhead.**
So the BUG port is nowhere near rank-flat in memory, and one clause is warranted wherever its memory is
mentioned — the same honesty move as D19.4's *"BUG's `5.76×` is comfortably resolved and is an effect
worth claiming."*

## 7. The lesson at the level of the failure family

- **R81** — never read the output the agents produce. *A commit count is not a delivery.*
- **R82** — generalised from one artifact to a class. *A verified method is not a verified class.*
- **R84** — inferred a document's state from a file it does not use. *An intermediate artifact is not the thing.*
- **R86** — corrected the wrong noun and left the wrong adjective.

**All four are "I found the error and stopped at the first wrong word."** R84 is the sharpest cousin:
there I doubted a correct measurement because a *different file* disagreed. Here I doubted a correct
measurement because a *different word* did.

**The discipline this earns: when a claim is wrong, ask what the corrected claim asserts — not which
word was wrong. A replacement that asserts the opposite of the thing you have just measured is not a
correction; it is a second error wearing the first one's clothes.**
