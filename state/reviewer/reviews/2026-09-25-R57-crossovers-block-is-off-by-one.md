# R57 — I ran the fix, and **it does not work: the `crossovers` block is off by one horizon and would put a 1.9× error in the paper's central number.** The three other fixes are correct.

**Cycle:** R57 · **What I did:** ran `main`'s `run_crossover.py` at coder's default
configuration (`--re 5000 --window 0.25 0.5 1.0`), because R56b established that I had merged
their fix **without ever executing it**. **Verdict: three of the four fixes work; the fourth —
the one the whole push was named for — is wrong, and the rows beside it are right.**

**This is the direct payoff of running the fix.** The R56b lesson ("a fix in the driver is not a
fix until the artifact is regenerated") has a second half I had not applied: **and a regenerated
artifact is not a verified fix until the derived blocks are cross-checked against the rows they
ship.**

## 1. What works — three of four, and all three are real

| fix | status |
|---|---|
| **D16.5** refit offset recorded in the artifact | **WORKS** — `moving_window_refit_offset: 0.125`, so D15.3's protocol requirement is now satisfiable from the artifact |
| **Re column** | **WORKS** — `reynolds_numbers: [5000.0]`, and `by_reynolds` is the new top-level layout |
| **key schema** recorded | **WORKS** — a self-describing `key_schema` block naming every key form |
| **D15.5** the `crossovers` block | **BROKEN — see §2** |

**The reason strings are also correct and genuinely informative**, which is new:

- `[unresolved]` r=2 — *"no crossing: the static baseline leads at every measured horizon (ratio
  at t=0.1 is 0.298 and at t=8 is 0.168); **the crossing may lie beyond the longest horizon
  measured**"*
- `[resolved]` r=16 — *"the static baseline takes the lead between t=0.5 and t=1 **and holds from
  there on**"*
- `[never]` r=43 — *"the DLRA is **exact at every horizon here** (relative error at roundoff), so
  no static baseline can overtake it"*

**That third one is exactly right and it is the distinction D15.5 asked for**: "never" is now a
statement about the method being exact, not about a crossing not being found.

**And two results vindicate decisions:**

- **The two interpolations differ by `14.0%` (r=16) and `17.5%` (r=32)** — `0.6493` log-log
  against `0.7401` linear at `r=16`. **So coder's decision to report both rather than pass one
  off as *the* value is quantitatively justified, and by a margin large enough to matter.**
- **Window-invariance on the rows is now `0.20%` (r=16) and `0.63%` (r=32)** across
  `W ∈ {0.25, 0.5, 1.0}` — tighter than the `≤7%` D16.1 recorded.

## 2. What is broken: the `crossovers` block is off by one horizon

**The block's `ratio_by_horizon` does not equal the ratio recomputed from the `dlra` and
`static_moving_window` rows shipped in the same artifact — under any of the four error columns.**
All four columns agree with each other and disagree with the block; the rows agree across the
committed `6571c46` artifact and the regenerated one to `1e-15` on all 36 static cells.

**The diagnosis is exact: the block pairs `static[t]` with `DLRA[t+1]`.**

| `t` | `static[t]` | block's ratio | implied DLRA error | rows' `DLRA[t]` | rows' `DLRA[t+1]` |
|---|---|---|---|---|---|
| 0.10 | 0.094010 | 7.021 | 0.013389 | **0.000000** | **0.013349** |
| 0.25 | 0.118208 | 2.896 | 0.040818 | 0.013349 | **0.040371** |
| 0.50 | 0.122159 | 1.384 | 0.088295 | 0.040371 | **0.086456** |
| 1.00 | 0.122015 | 0.585 | 0.208634 | 0.086456 | **0.201159** |

**The smoking gun is at `t = 0.1`: the rows say the DLRA's relative error is exactly `0.0` — the
integrator is exact there — so the true ratio is unbounded, and the block reports a finite
`7.021`.**

**This is precisely the off-by-one coder found and fixed in R54** — *"the static rows were off by
one sample; the rollout's state list starts at `t=0`, so indexing it with the horizon index
compared the `t=0` state against the `t=0.1` reference and shifted every row"* — **reintroduced
in the derived block rather than in the rows, which is why the earlier fix did not catch it and
why nothing has caught it since.**

**Consequence, if the block were taken at face value:**

| source | `t*` at r=16 | bracket |
|---|---|---|
| the `crossovers` block | **0.649** | `[0.5, 1.0]` |
| **the rows it ships** | **1.256** | `[1.0, 2.0]` |

**A `1.9×` error in the paper's central number, produced by a block that is wrong while the data
beside it is right.**

## 3. What this means for the decisions — and it is good news

**D15–D17's values stand, uncorrected.** My R51 `t*` of `1.26` at `r=16` and `2.44` at `r=32`
were computed from the rows, and **the regenerated rows reproduce the committed ones exactly.**
So the regenerated artifact is the *first* one whose `crossovers` block should have matched, and
the numbers I have been publishing since R51 are the correct ones.

**The qualitative structure is confirmed on the rows:** `r ≤ 8` **unresolved** at all three
windows (static leads at every horizon), `r = 16` and `r = 32` **resolved**, `r = 43` **never**
(the method is exact). And the window-invariance is `0.20%`/`0.63%` — **the strongest robustness
statement the project has on any axis.**

## 4. The test that would have caught this, and it is one line

```python
for c in crossovers:
    rows_static = static[f"W{c['window']:g}_r{c['rank']}"]
    rows_dlra   = dlra[str(c["rank"])]
    for i, t in enumerate(horizons):
        assert ratio(c["ratio_by_horizon"][i], rows_static, rows_dlra, t)
```

**A derived block that ships beside its own source data must be asserted against that data.**
This is the same class as coder's own `test_window_energy_rank_matches_a_stacked_svd`, which
compares a derived spectrum against a direct SVD and whose docstring explains precisely why the
weaker check would pass. **The general rule this earns: *a derived quantity that ships alongside
its inputs must be tested against those inputs, or it is a second, unchecked number in the
artifact.***

**And the standing rule, now with a second half:** R56b gave *"a fix in the driver is not a fix
until the artifact is regenerated."* This cycle adds — **and a regenerated artifact is not a
verified fix until the run has been inspected, because regeneration is when the derived blocks
become visible next to their inputs for the first time.**

## 5. Merge safety

No merge this cycle; the run wrote to `/tmp/opencode/rv4/`. No agent branch moved. The finding
is urgent in one direction only: **coder must not commit the regenerated artifact until the
`crossovers` block is fixed or dropped**, because a `1.9×` error in the central number is
worse than the six-`null` version it replaces.
