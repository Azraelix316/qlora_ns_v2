# R73 — the **central figure's title prints two claims I withdrew two cycles ago**, and one of them is refuted by a code comment eleven lines above it.

**Cycle:** R73 · No agent pushed. `main` at `bdd0ec8`, 171 files, clean.
**R72's lesson applied to every figure rather than one: a title is a claim. I read all of them.**

## 1. The audit, figure by figure

| figure | title/label claim | verdict |
|---|---|---|
| `fig_bug_cost` | *"BUG removes every full-size factorization and is still 3-5x slower"* | **CORRECT.** It leads with the structural fact and claims only the slowdown — which is exactly what survived D25.6. **It does not claim the withdrawn rank-scaling.** Best title in the project. |
| `fig_cost` | suptitle is the *protocol* (repeats, steps, thread settings) | **CORRECT** — and exemplary: the protocol is printed on the figure. |
| `fig_spectrum` | *"Full-grid state spectrum (all resolved modes)"* | correct and appropriately narrow. |
| `fig_divergence` | *"Trajectory divergence, not error"* | correct, and a careful distinction. |
| `fig_window_rank` | *"The amplitude rule asks for the grid"* | correct, and it is the honest restatement of the `4.0×` claim I withdrew (D35.4). |
| **`fig_div_free`** | *"Exact divergence-freeness holds for every method"* | **FALSE — R72.** Four methods diverge. |
| **`fig_crossover`** | *"$r=43$ (the dealiasing ceiling) is exact and is off this log axis"* | **TWO WITHDRAWN CLAIMS — below.** |

## 2. `fig_crossover` — the paper's central figure — prints D30's withdrawn claims

```python
title += (f"\n$r={'$, $r='.join(str(r) for r in exact)}$ "
          f"(the dealiasing ceiling) is exact and is off this log axis")
```

**Claim 1 — "the dealiasing ceiling" — is D30.2, which I withdrew.** `2·floor(N/3)+1 = 43` is the
largest **wavenumber** 2/3-dealiasing keeps per direction. It is not a mode count, and the dealiased
64×64 grid carries ~1849 dof. **`r=43` is the largest rank in the sweep.** The artifact itself records
`dealias_ceiling: 43` and `ranks: [2,4,8,16,32,43]` — the very adjacency that misled me for twenty
cycles is now printed in the central figure's title.

**Claim 2 — "is exact" — is D30.3, and it is refuted by this file's own comment, eleven lines above:**

```python
# "Exact" is judged against the scale of the other curves, not against
# an absolute constant: the ceiling rank's error is ~1e-8 while the
# others are O(0.1), so a fixed 1e-10 cut would call it inexact and put it
# back on the log axis.
```

**The comment says the error is `~1e-8`. The title says it is exact. The artifact agrees with the
comment: `r=43`'s `relative_l2` runs `6.9e-13` to `1.6e-8`.** The code's `exact` is a *plotting*
predicate — `max(relative_l2) < 1e-6 * scale` — chosen to keep a curve off a log axis dominated by
`O(0.1)` values. **That is a defensible plotting decision. Turning it into a physical claim in the
title is not, and the file contradicts itself.**

## 3. And the right panel's title is narrower than its own x-axis

> *"A static subspace cannot spend rank **at short horizons**"*

D30.1 established the stronger and better fact: **the static baseline _saturates_ in rank — `r=16`,
`r=32` and `r=43` have identical static errors to four decimals at every horizon**, and the spread
across the whole resolved range is `0.00%` at `t=0.1`. **The panel plots that spread at _all_
horizons, so its title describes only the left edge of its own x-axis.** Not false — but it is the
weaker version of a stronger true statement, which is the opposite of what a figure title should be.

## 4. The two string fixes, exactly

```python
# left panel — was: "(the dealiasing ceiling) is exact and is off this log axis"
f"\n$r={'$, $r='.join(str(r) for r in exact)}$ (the largest rank tested) "
f"stays $6$–$11$ orders below every static baseline, and is off this log axis"

# right panel — was: "A static subspace cannot spend rank\nat short horizons"
"A static subspace saturates in rank:\n" r"$r\geq16$ buys it nothing, at any horizon"
```

**The right panel's y-label already declares its normaliser, `($\max-\min$)/$\min$` — which is right,
and matters, because the two normalisers differ by nearly `2×` (D30.1). Keep it.**

## 5. The meta-finding, and it is a gap in **my own** process, not coder's

**Every figure title is a claim derived from the decisions record. D30 withdrew two claims. Nobody
propagated D30 into the figure strings** — because `make_figures.py` is coder's file and my D35 sweep
covered `CLAIMS.md` and `PAPER_BLUEPRINT.md`.

**So D34/D35's rule — "a withdrawal must be swept against everything built on it" — has a boundary I
had not noticed: it reaches the files I own and stops at the files I don't.** But the *claims* in those
files are mine, and the paper reproduces them verbatim. **The rule has to reach figure strings, axis
labels, and titles, and I have to be the one to check, because I am the one who withdrew the claim.**

**And the general form, which is the fourth in this set:** R70 — audit the artifacts, not the claims.
R71 — the artifacts have no tests. R72 — the figures are artifacts. **R73 — the figures' TITLES are
claims, and they are the only claims in the project that nobody has ever read as claims.**

**Two of the six figure titles I could check are wrong, and the wrong one is the central figure.**
That is not a bad luck rate; it is what happens when a text field is written once and never
re-examined after the science underneath it changes.
