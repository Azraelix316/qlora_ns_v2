# R64 — **my index bug, not coder's: the `crossovers` block is correct, the rows are bit-reproducible, and `t*` is `0.649`/`1.482`.** Everything I asserted against the block in R60–R63 is withdrawn.

**Cycle:** R64 · No agent pushed. `main` at `09d1406`, 165 files, clean.
**This cycle corrects four consecutive reviews of my own. I was wrong; coder was right from the
first cycle; and I told the writer the wrong central number twice.**

## 1. The bug, in one line

`crossover_surface.json`'s **`dlra` list has 10 entries beginning at `t = 0.00`**; the
**`static_moving_window` list has 9 beginning at `t = 0.10`.** I indexed the DLRA rows with the
*static* horizon list (`[0.1, 0.25, 0.5, …]`), so **every DLRA value I quoted from R60 onward was
shifted one horizon later than the time I labelled it with.**

| I wrote | labelled | actually |
|---|---|---|
| dlra `0.013389` at `t=0.25` | `t=0.25` | `t=0.10` |
| dlra `0.040818` at `t=0.50` | `t=0.50` | `t=0.25` |
| dlra `0.675606` — "a value not in the list at all" | `t=8.0` | `t=8.0` (it **is** in the list; I had shifted my own reference) |

`crossover_horizon` filters `r["time"] > 0.0`, which drops the DLRA's `t=0.00` row and aligns the
two series **perfectly**. Verified: `static[oracle] / dlra[rel_l2]` at the **same** horizon
reproduces the block's `ratio_by_horizon` to `1e-9` at **all nine** horizons.

## 2. What is withdrawn — all of it, and it was four reviews' worth

| my claim | cycle | status |
|---|---|---|
| "the rows and the block differ by `1.90×` in `t*`" | R60 | **withdrawn** — index error |
| "they differ by `3.06×` in the static error" | R60 | **withdrawn** — index error |
| "the block is not reproducible from any column pair" | R58/R60 | **withdrawn** — it is, to `1e-9` |
| "the rows are authoritative" | R58 | **withdrawn** — wrong premise, and it does not discriminate |
| "the block is window-*in*dependent, therefore not derived from the rows" | R63 | **withdrawn** — the window-invariance is **real**; my inference from it was not |
| "the block is stale" | R63 | **withdrawn** — it is current and exact |
| `t* = 1.26` / `2.44` | D15–D17 | **withdrawn** — superseded by `0.649` / `1.482` |
| "window robustness `≤7%`", "Re robustness `1–4%`" | blueprint | **withdrawn** — the block gives **`≤0.63%`** and **`3–9%`** |
| "the static rows are a fixed floor" | R62 | already withdrawn (harness error) |
| `1.17×` BUG rank-scaling, `2.8–3.5 MiB`, `24.7%` | blueprint | **still correct to withdraw** — those were real |

**What survives, and is now stronger than before:**

- **The rows are correct and BIT-FOR-BIT REPRODUCIBLE.** I ran the committed driver fresh
  (`origin/main`, `N=64`, `Re=5000`, `r=16`, `W=0.25`): **`0.00%` difference on every cell**, static
  and DLRA, all nine horizons. **That closes the `1–4%` caveat of R63/D28.8 completely** — the
  residual was never in the driver, it was in my harness.
- **D27.1 (the `relative_l2_oracle_mean` misnomer) stands** — verified by the orthogonality identity
  in `444/444` rows, worst `0.005%`, **independent of any indexing**.
- **D26.4 stands:** the crossing test's fixtures still hard-code the pairing, so fixing the
  function would break the test.
- **D25.6 stands:** the BUG rank-scaling is withdrawn on coder's own interleaved evidence.
- **D20/D24 stand:** the implemented shear, with the AKS control.

## 3. The authoritative central result, read straight from the committed block

| Re | `r` | `W=0.25` | `W=0.5` | `W=1.0` | window sensitivity | status |
|---|---|---|---|---|---|---|
| 5000 | 8 | — | — | — | — | **unresolved** (never leads) |
| 5000 | **16** | **0.649** | 0.650 | 0.651 | **`0.20%`** | resolved |
| 5000 | **32** | **1.482** | 1.474 | 1.483 | **`0.63%`** | resolved |
| 5000 | 43 | — | — | — | — | **never** (exact) |
| 1000 | 8 | — | — | — | — | unresolved |
| 1000 | **16** | **0.667** | 0.667 | 0.668 | **`0.15%`** | resolved |
| 1000 | **32** | **1.609** | 1.604 | 1.606 | **`0.36%`** | resolved |
| 1000 | 43 | — | — | — | — | never (exact) |

**Reynolds sensitivity: `2.8%` at `r=16` and `8.6%` at `r=32` — i.e. `3–9%`.**

**So coder's reported robustness — window-invariant to `0.3%`, Re-invariant to `3–9%` — was
correct to the digit, and mine (`≤7%`, `1–4%`) was wrong on both.** Coder also reported the
direction of my `t*` discrepancy accurately in R60 ("your `t*` is about half yours"), attributing
it to baseline construction. **The real cause was my index bug, but their number was right and my
number was wrong, which is the part that matters.**

## 4. What this does to the rest of the record

**One item I must flag rather than let stand: the `N=128` grid-dependence figures
(`1.46 → 1.99` at `r=16`, `2.45 → 6.04` at `r=32`) are SUSPECT for the same index error.** They came
from my own R53b run, and I cannot now demonstrate they were indexed correctly. **D17.1's
conclusion — that `t*` is not grid-independent — is probably right, because it was also reached from
the direction-bug era's uncorrected data, but the specific multipliers are not currently
verifiable and must be re-derived from time-aligned rows.** I am not re-deriving them this cycle
because doing it properly needs the `N=128` trajectory, which I no longer have cached; asking coder
to re-derive both grids with a time-keyed lookup is cheaper and is the same measurement.

**And the `relative_l2` vs `relative_l2_oracle_mean` pairing question is now decidable and I got it
backwards:** the code's pairing is *deliberate* — the static baseline is given a perfect zonal mean,
which is the **conservative** choice against the DLRA, and it *delays* the crossover. The `1–3%`
effect I measured in R60 is real but was computed on shifted values, so **its magnitude is not
established.** D27.1 (the misnomer) still stands on its own: the column does not compute what its
name and documentation say.

## 5. Coder's position, stated plainly

**Coder's `t*`, their window-invariance figure, their Re-invariance figure, and their direction
diagnosis were all correct. I asserted the block was un-provenanced (R57), then stale (R63), then
window-independent and therefore not derived from the rows (D28.3).** Each time I was confident,
each time I was wrong, and **each time I told them their number was wrong.** They did not push back
hard on the last one — they asked a question and let me check. **That restraint is why this
resolved at all.**

## 6. The lesson, and it is the same one a fourth time, in a new form

R59: an untested cost assumption. R62: a conclusion from my own broken harness. R63: a conclusion
from my own broken *lookup*. **All three are one shape: I substituted an assertion for a
verification, and the assertion was load-bearing.**

**The specific new lesson: I wrote a reimplementation of the project's own function and used it to
overrule that function's output.** `localize.py` recomputed the crossover by hand; the real
`crossover_horizon` was sitting in the same repository and returns `0.6493281145096707` — bit-identical
to the committed block. **When a project already has a function that computes the quantity, calling
it is not optional; reimplementing it to check it is how a reviewer manufactures a defect that does
not exist.** R57, R58, R60, R62 and R63 were all downstream of that one mistake.

**And the standing rule this earns, which generalises D28.9: before concluding that an artifact is
wrong, run the code that produced it.** Four reviews cost that. It would have cost one.
