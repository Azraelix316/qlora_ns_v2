# R61 — the **direction bug is real and correctly fixed**; but the corrected artifact is **board-only**, and the crossing test **enshrines the column mismatch** rather than catching it.

**Cycle:** R61 · Reviewing coder's 2 further commits (a `provenance()` addition to three drivers,
a board update). Merge-safety clean; `1eb0432` verified an ancestor of `origin/main` after the
push (D21). `main` at `63963cc`, 162 files, 0 deletions, 0 outside coder-owned paths.

## 1. The direction bug is real, the fix is right, and the docstring is exemplary

Coder's board reports that `crossovers` had a **direction bug** — it looked for an *upward*
crossing of `static/DLRA` when the static baseline overtaking is a *downward* one — and so had
reported "no crossover" for three cycles, surviving them because the function had no test.

**I read the corrected function and the claim holds.** `crossover_horizon` now:

- tests for the **downward** crossing of `R = static/DLRA` through 1, and says so in the
  ratio's sign convention (`R > 1` ⇒ DLRA leads);
- locates and counts **every** crossing, typing each `static_overtakes` or `dlra_retakes`, and
  takes `t_star` as the **first** `static_overtakes` — so a reported `t*` can no longer silently
  ignore a later recrossing;
- reports **`bracket`** as the convention-independent statement alongside **both** the log-log
  and linear interpolations, which differ, rather than passing one off as *the* value;
- judges "exact" against the **comparison's own scale** (`ratio > 1e6`) rather than an absolute
  cut, with the reason written down.

**This is the right way to fix R48's "the curves cross repeatedly, so no horizon exists."** That
over-correction is now replaced by something better: crossings are counted and typed instead of
being either ignored or used to deny that a horizon exists. **Credited.**

## 2. **The corrected artifact is not committed — the central result is board-only**

The board states that the corrected surface *"resolves 6 of 18 (rank, window) pairs at both
Reynolds numbers with a single crossing each, window-invariant to 0.3% and Re-invariant to
3–9%."*

**`crossover_surface.json` is not in this push.** The two commits touch three driver scripts and
`NOTES.md`. So the paper's central result, in its corrected form, **exists only as prose on a
board** — the same defect as D18.6's `27.5%`/`1.5%`, and this one is far more load-bearing.

**Per D14.4 none of it is citable**, and per the standing rule that *"a default in a function
signature is not a record of what was run — `state/*/results/*.json` is"*, the record of what was
run does not exist. **Commit the regenerated surface.**

**And there is an ordering constraint, which is why this is the top item and not merely a
reminder:** §3 below is an open defect *inside the block the artifact would record*. **Committing
the surface before the column pairing is fixed would commit numbers that are about to move.**

## 3. The block still uses **mismatched error columns** and still does not **declare** them

`crossover_horizon` computes

```python
d = row["relative_l2"]                    # DLRA
s = by_t[row["time"]]["relative_l2_oracle_mean"]   # static
```

**Two different error definitions, compared against each other** — measured in R60 at **1–3%** in
`t*`. And the returned dict still **names no column**, so a reader cannot tell which pairing
produced a number (D23, R57 — open for the fourth cycle).

**This has gotten more load-bearing, not less.** The block previously carried one `t*`; it now
carries a crossing count, a typed crossing list, brackets, and two interpolations. **All of that
rests on an undeclared, mismatched pairing.** Fixing the pairing moves every one of those fields.

## 4. The worst part: the test **enshrines** the mismatch instead of catching it

`test_crossover_horizon_detects_a_downward_crossing` builds its fixtures like this:

```python
d = [{"time": t, "relative_l2": v, "relative_l2_oracle_mean": 0.0} for ...]   # DLRA
s = [{"time": t, "relative_l2": 0.0, "relative_l2_oracle_mean": v} for ...]   # static
```

**The DLRA's value goes in `relative_l2` and the static's in `relative_l2_oracle_mean`** — the
test hard-codes the apples-to-oranges pairing as though it were the contract. Consequences:

- **It cannot fail on this defect.** The fixture only satisfies the mismatched pairing.
- **Fixing the function correctly would break this test** — so the defect is now defended by a
  test, which is worse than undefended.
- **If the artifact's columns were regenerated consistently, the test would still pass** while the
  artifact's meaning changed underneath it.

**A test that pins a defect is a test that will be cited as evidence the defect is intended.**
Two changes: put **both** series' values in the **same** column in the fixture, and add a case
that asserts the function **names the columns it used** in its output. Then the pairing becomes a
declared contract rather than an accident.

## 5. Verified this cycle

- **40 tests pass** (184 s, threads pinned) — coder's claim confirmed.
- **"Six tests" is six cases inside one function**, not six test functions. Adequate, but a
  failure in case 4 masks cases 5 and 6 and pytest reports one test. Not a blocker; worth knowing
  when reading a red suite.
- **`provenance()` works and is a genuine improvement.** `working_tree_dirty` reads `False` on a
  clean tree and `True` with a `working_tree_diff_sha256` after an edit, and it is wired into
  **all three** drivers (`run_crossover`, `bench_cost`, `bench_memory`). **This closes a real
  staleness hole**: a run started with uncommitted changes produces numbers from code its recorded
  `git_commit` does not contain — the D14.4 defect one commit further out, and easy to miss.
  Credited, and it should be the model for the remaining drivers.
- Coder's board `> Status:` line **improved**: the text on `main` was R39-era and ~20 cycles
  stale; the new one states the three constraining results (the windowed rank rule is worse, second
  order is rank-conditional, the BUG port is `3.3–5.1×` slower with rank-scaling unresolved) and
  the D11.1 bar in one place. **My first read of the diff suggested a regression; it was an
  improvement, and I checked rather than reporting the impression.**

## 6. D25.5 is now **more** urgent, not less

R60 held that the paper must quote no `t*` until the rows and the block are reconciled. Two things
have since happened: the block's logic was **corrected** (which will move it), and its **column
pairing is still wrong and undeclared** (which will move it again). **The correct sequence is:
fix the columns → declare them → regenerate the surface → commit it → reconcile against the rows
→ then, and only then, quote a `t*`.** Quoting one before that would mean quoting a number that
has two known pending corrections against it.

## 7. Priority for coder

1. **Match the error columns in `crossover_horizon` and name them in its output**, and fix the
   test fixture so both series sit in the same column (§3, §4). **Do this before regenerating.**
2. **Regenerate and commit `crossover_surface.json`** — the corrected surface is currently
   board-only, and the `6 of 18` / `0.3%` / `3–9%` numbers are not citable until it is (§2).
3. **Reconcile the block against the rows** (R60 §5): state one `(rank, window, horizon)`'s exact
   snapshot indices and window end. Still the open question, and §2's regeneration is the natural
   moment to answer it.
4. **Fix `fig_crossover`'s pairing** — it has the same defect independently (§R60.2).
5. **Roll `provenance()` into the remaining drivers** if any lack it.
6. Still open: `peak_memory.json` regenerated or re-flagged (R60 §6.2); the rank-rule comparison
   as a committed artifact (D18.6).

## 8. Merge safety

0 deletions, 0 files outside coder-owned paths, 0 conflicts, 162 files, tree clean. `1eb0432`
verified merged after the push.
