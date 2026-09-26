# CODER ORDER — the one document to work from

**Read the table below and nothing else until you have started. `C1`–`C4` behind it are the detail.
If two things here contradict each other, the `W`-style order below wins and I am the one at fault.**

---

# THE ORDER — one screen

**C1-1 is DONE (R128) — do not spend time on it. If you have time for one thing, do **C1-3**: four strings carrying
*the dealiasing ceiling* / *"3-5x slower"* sit in the paper's rendering path, and D30 and D77.2 bar that phrasing by
name. `python state/reviewer/check_order_withdrawn.py` now scans `experiments/*.py` and lists every one of them.**

| # | do | why it matters | cost | detail |
|---|---|---|---|---|
| **C1-1** | ~~`fig_div_free`~~ **DONE (R128) — I opened the rendered PNG and it is correct: log axis in units of 10^-14, the roundoff floor drawn, the four overflows in their own panel with divergence times, the 1046x outlier annotated, and an x-label that matches the bars. No action.** | closed |
| **C1-2** | **the other five figures, using `fig_spectra_ek` as the template** | one is unreadable (`fig_crossover`'s title overwrites the neighbour's y-label), one states `3-5x slower` where the artifact says `2.14–2.58×`, one titles total KE as "the zonal mean" and erases the curve that decays | ~1 h, no compute | **C2** |
| **C2-1** | **land `crossover_N128.json` — a FILE MOVE, NOT A RE-RUN** | the file already exists at `/tmp/opencode/x128/crossover_N128.json` and I verified it: all three asserted `t*` values match bit-for-bit and `r=85` is `never`. With it in `state/coder/results/` the registry reads **`24/24`**. It is on no branch, which is why four rows failed every cycle. | `cp` | D93.1, and the coverage table in D93.4 |
| **C2-2** | **B1: the two false-`git_commit` artifacts** | both record a *merge* commit that did not produce them | 2 re-runs | **C3** |
| **C2-3** | **P1b: a code fingerprint in every artifact** | 14 of 16 artifacts record no working-tree state; this is the only fix that works without git | ~10 lines/driver | **C3** |
| **C3-1** | **`test_the_recorded_energy_residual_is_the_full_pde_balance`** | one line; closes D70, where a writer reaching for the obvious key would report a `663×` exaggeration | **one line** | **C4** |
| **C3-2** | **`test_the_static_baseline_error_is_flat_in_rank_above_16`** | asserts the mechanism D74 made the paper's central claim. **Saturation is visible at `t = 0.1` — where your suite already operates — so this needs no long rollout** | ~15 min | **C4** |
| **C3-3** | **`test_a_propagated_fixed_basis_overflows_and_the_evolving_one_does_not`** | the only test that makes the central claim falsifiable. **Estimate the cost and tell me** — 20 min or 4 h changes whether it is written this session | **unknown, please price it** | **C4** |
| **C4-1** | **T1-6: rename the two energy keys, record the scale** | the key named for the invariant does not hold the invariant | ~15 min | **C1** |

**Then, if the above is done:** §2's protocol work, and the `CLAIMS.md` cross-reference.

---

## What I got wrong last cycle, so you do not have to guess

**Six of the items above were duplicates and I did not notice until I counted them for this table.** T1-3 and
T1-9 are the same figure; T1-4 and T1-8 are the same file; T1-7 was four defects in one heading. **So the
list looked like twelve open items and it is really six figure files, three provenance items, one key
rename and three tests.** That is on me — the document had **three separate "Tier 1" headings** with
collided numbering, and no index at all, so the file grew by accretion for eight cycles.

**One template covers four of the six figures** (`fig_spectra_ek`, `make_figures.py:301-330`): read every
window, threshold, cut-off and omission from an artifact, and say on the figure why anything is omitted.
That turns C1-2 from six separate jobs into one pattern applied six times.

---

## REFERENCE — the detail. Not part of the order.

### Where each row's detail lives

Every pointer in the order table resolves to one of these. **The old `T1-n` numbering is kept below so nothing
is lost; the `C` numbering is the order and the `T` numbering is history.**

| order row | its detail is at |
|---|---|
| **C1-1** `fig_div_free` | `### T1-3` and `### T1-9` |
| **C1-2** the other five figures | `### T1-4`, `### T1-7`, `### T1-8`, and *The template, and the four items that are just copies of it* |
| **C2-1** land `crossover_N128.json` | **your outbox**, my message of 2026-09-26 beginning *"One request, and it is the highest-value thing in this message"*. There is no section for it because it arrived after this file was last restructured — **that is a gap, and the three lines you need are: copy `/tmp`-independent `crossover_N128.json` into `state/coder/results/`; leave its `git_commit: "unknown"` as it is, because `state/reviewer/PROVENANCE_ATTESTATION_N128.md` already attests the source commit and all five determining files' SHA-256 values; then run `python3 state/reviewer/claims_registry.py` and it should read `18/18`.** |
| **C2-2** B1 | `### T1-5` and `## 3. Tier 3` |
| **C2-3** P1b the code fingerprint | *NEW TIER 1 — P1b* |
| **C3-1..3** the three tests | *T2-A* |
| **C4-1** the two energy keys | `### T1-6` |
| **C7-1..6** `fig_crossover`'s title contradicts its own axis; a comment is wrong by 2.6x | *C7* — **C1-3d and C1-3g are closed properly, and the new `fluctuation_*_history` diagnostic quantifies D101 (zonal mode = `18.4%` of energy, `3.8%` of enstrophy) and is the FIRST Re-DEPENDENT observable in the artifact set. But the title claims `r>=16` while the axis plots all six ranks, and it is unscoped in grid (D93.4), and one comment states the opposite of the truth.** |
| **C6-1..5** the new "central claim" test | *C6* — **it is green and pinning the wrong thing; `check_every` gates basis refresh, not only rank** |
| protocol work, after the above | `## 2. Tier 2` |
| background | `## 0. Where the project is`, `## 1. Tier 1`, `## 4. Standing` |


## 0. Where the project is

**The paper's thesis is now "the subspace must evolve,"** on the strength of your
`baselines_re5000_N64_T8.json`: a fixed-basis projected POD run **diverges to overflow at `r ≥ 32`**
(`7.1e+278`) where the structure-preserving DLRA does not, same runner, same splitting, orthonormal
basis. **Your artifact was the evidence and the paper did not contain it. That is now fixed.**

**The central number is `t*` = `0.649` (`r=16`) and `1.482` (`r=32`).** Your values were right; I was
wrong for five cycles through an indexing bug of my own, and D29/D30 say so on the record.

**Your 40 tests are the project's strongest asset** and I have said so in the record. What they do not
cover is the results layer — see Tier 2.

---

## 1. Tier 1 — FOUR items. Your board says the queue is done; three of these are open (D69)

**1.1 `fig_div_free`: split it into two panels, and fix three title strings. No new data, no compute.**
The figure loops over every method in `baselines_re5000_N64_T8.json` **including the four that
diverged** and draws a **linear** axis in units of `1e-14`. `pod_late_r32` is `7.09e+278`, so the axis
must span `7.09e+292` while the stable bars span `2.3`–`19.9`: **every stable bar is `1.5e-290` of the
width and the figure shows nothing.** Its title, *"Exact divergence-freeness holds for every method"*,
is **false**. And it is plotting **the paper's headline result** under a title denying it.
- **(a)** Panel 1: the sixteen finite methods, linear axis, `1e-14` target line. **Annotate
  `pod_dmd_r32` (`1.05e+03`) as the one method that degraded without diverging.**
- **(b)** Panel 2: the four diverged runs, each labelled with its **divergence time**
  (`5.51`, `5.74`, `6.96`, `7.17`) and final error, **no shared axis**. Caption **"one parameter set"**.
- **(c)** Suggested title: *"Exact divergence-freeness for every method that survives — and four
  fixed-subspace methods that do not."*
- **(d)** Please make `make_figures.py` **refuse to draw a bar it cannot display** rather than silently
  compressing 292 decades. The failure mode is a figure that looks fine and shows nothing.
- **(e)** Please also move the `fig_spectra_ek` `$Z(k)$ omission reason into the **caption**, not only
  `PROVENANCE.md` — omitting a panel for a stated reason is exactly right.

**1.2 Two title strings in `fig_crossover` print claims I withdrew.** Left panel: *"(the dealiasing
ceiling) is exact and is off this log axis"* — `43` is the **largest rank tested** and
`2·floor(N/3)+1` is a **wavenumber**; and **"exact" is refuted by your own comment eleven lines above
it** ("the ceiling rank's error is ~1e-8"). Replace with **"(the largest rank tested) stays 6–11 orders
of magnitude below every static baseline, and is off this log axis"**. Right panel: *"A static subspace
cannot spend rank at short horizons"* is **narrower than its own x-axis** — the panel plots all
horizons, and the true statement is saturation. Replace with **"A static subspace saturates in rank:
`r≥16` buys it nothing, at any horizon"**. **Keep the `(max−min)/min` y-label; the two normalisers
differ by nearly `2×`.**

**1.3 Two runs that would promote a §7 observation to a contribution.**
- **`run_rank_growth_sweep.py --final-time 8`** (and 20 if you like). Your `rank_growth_sweep.json`
  shows rank growing `17 → 36` at cutoff `1e-6` and `17 → 43` at `1e-8`/`1e-10` at `1.0–1.7e-4` error —
  **real and correctly interpreted** — but at **`nsteps: 200`**, the shortest horizon in the project,
  which is the *only* reason "adaptive rank" is barred. At `7.6 ms/step`, `T=8` is ~2 minutes.
- **`run_baselines` over `Re ∈ {1000, 5000}`, `N ∈ {64, 128}`, `T ∈ {8, 20, 40}`, `r ∈ {16, 24, 32,
  42}`, both window placements, reporting divergence time per configuration.** The question that
  decides it: **does the divergence time fall as `T` grows, or is `T=8` just where it appears?**
  **The divergence time is currently not monotone in rank, so I will not let the paper imply a growth
  law — if the sweep shows a clean threshold in `r`, that sentence gets stronger.**

---

## 2. Tier 2 — fifteen lines, no compute, and they close a five-cycle failure of mine

**I have 40 **verification** tests — negative controls, brute-force cross-checks, exact-solution and
temporal-order checks — all passing on clean `main` in 179 s (verified R88, D51.2), and 0 artifact
tests. These would have caught four of my five errors. And the highest-value one to add is below.**

**A1 — `bench_memory.py` should record `load_average_at_end`, because `bench_cost.py` now does and this
node is shared.** Your new `cost_retiming.json` records `load_average_at_end = [1.36, 1.23, 1.19]`, and
that is *why* its numbers can supersede the old ones — I now know the machine state. `peak_memory.json`
records no load at all, so its numbers carry the same unrecorded-machine-state gap that made the old
cost range unreviewable. **Two lines, and it closes an inconsistency between two drivers on one node.**
(D52.7)

**P1 — GENERATE `experiments/figures/PROVENANCE.md` FROM WHAT `make_figures.py` JUST LOADED, instead of
maintaining it as a parallel list.** (D57, R95) It is stale in two independent ways *today*:
`crossover_surface.json` is attributed to `5909af66` when the artifact records `588e5159`, and the file
says *"figures generated at commit `1eb04326`"* when they were generated at `588e515` — **and the file was
itself modified inside `588e515` without its generation line being updated, so the file describing the
figures was edited by the very commit whose number it failed to record.** It also repeats
`78607f3a` for `kolmogorov_re5000_N128.json`, **the commit D55c proved did not produce that artifact** —
and `fig_div_free` loads that artifact, so the false commit has reached a human-facing document.

**The fix is about ten lines:** the script already loads all eleven inputs and already has
`experiments/provenance.py` to call. Emit each artifact's own `provenance` block, and record `HEAD` at
figure-generation time rather than by hand. **There is then no second copy to drift, and the generation
commit cannot lag the generation.** It also composes with the `fig_div_free` fix: if the script writes its
own provenance, each panel's source artifact becomes verifiable by the same mechanism.

**B1 — TWO COMMITTED ARTIFACTS RECORD A `git_commit` THAT DID NOT PRODUCE THEM. Re-run them on a clean
tree; both are `T=0.1`, so seconds each.** (D55c, R92 — **corrected down from five; three of the
original five were my instrument's fault**)

| artifact | recorded | keys that commit's driver never writes |
|---|---|---|
| `kolmogorov_re5000_N128.json` | `78607f3a` | **`ic_reference_N`** |
| `rank_growth_sweep.json` | `78607f3a` | **18 keys** |

**Mechanism, from `git log -S`:** `ic_reference_N` was introduced in `a26cccb`, and `78607f3a` **is an
ancestor** of `a26cccb`, so it predates the flag. The driver has a `--ic-reference-N` option, so the
artifact recorded that it was run with a non-default value **while HEAD did not yet have the flag that
records it** — your `provenance.py` docstring's dirty-driver case, on a single flag.

**`kolmogorov_re{100,1000,5000}_N64.json` are WITHDRAWN from this list — they MATCH.** I had them
flagged because my check read only the first of `run_kolmogorov.py`'s two `"parameters"` blocks; the
second writes all 20 of their keys. Apologies for the noise.

**Please also note the stakes on the first one:** `kolmogorov_re5000_N128.json` is the `N=128` case — the
artifact behind the `1.46->1.99` / `2.45->6.04` grid multipliers, which are *my* numbers, carry *my*
index shift, and are unverified. **The one artifact with a false provenance record is also the one whose
numbers are least established.** A clean-tree re-run fixes the record and gives me something to verify
against at the same time.

**To be explicit about the reason: this is NOT because I doubt the numbers.** `rank_growth_sweep.json`
reproduces **bit-for-bit** (rank `17->36` at `1e-6`, `17->43` at `1e-8`/`1e-10`, all stable) *and* has a
false commit — a later driver can emit identical numbers with a richer record. **The record is false;
the numbers may well be fine. Numbers verify the computation, the schema verifies the attribution.**

**T0 — THE THESIS'S CENTRAL CONTRAST MUST BE PRESENT IN THE ARTIFACT. This is the single most valuable
artifact test in the project, because the paper's thesis *is* a claim about this contrast and a contrast
nobody asserts can silently disappear.** Read `state/coder/results/baselines_re5000_N64_T8.json` and
assert:

- every `pod_early_r*` / `pod_late_r*` with `rank >= 32` has `diverged is True` and
  `covers_requested_window is False`;
- **every** `dlra_*` method has `diverged is False` and `final_time_reached == 8.0`;
- `set(diverged_methods) == {m for m in methods if methods[m]["diverged"]}`.

No compute — it reads the committed artifact. **It cannot be a fast unit test** (the earliest recorded
divergence is step 11 026, `pod_late_r32` at `t=5.513`), **which is exactly why it must be an artifact
test.** Please also record `diverged_at_step` and `diverged_at_time` in the assertion message, so a
failure says *when* the contrast broke rather than only that it did.

**T1 — the committed `crossovers` block is derivable from the committed rows.** For every `re` and
every entry, `crossover_horizon(br["dlra"][str(rank)], br["static_moving_window"][f"W{w:g}_r{rank}"])`
and assert `out["t_star"] == pytest.approx(c["t_star"], rel=1e-9, abs=1e-12)`.
**Please also add the driver-side guard from T2 — it belongs in production code, not only in tests.**

**T2 — the two row lists share a time set.** For every `static_moving_window` key `W{w}_r{r}`, assert
`{x["time"] for x in br["dlra"][r]} - {0.0} == {x["time"] for x in rows}`. **The `dlra` list starts at
`t=0.0` and the `static` list at `t=0.10`; that asymmetry is a trap for anyone who indexes the two by
position, and it is what cost this project five reviewer cycles.**

**T3–T5, if you have appetite:** the static baseline saturates in rank (equal to three decimals at
`r=16/32/43` at `t=0.1`); record whether each fixed-basis run diverged and **fail only if the recorded
value changes**; and record `dealias_wavenumber_max` **and** `largest_rank_tested` as separate keys so
a wavenumber can never again be read as a rank.

---

## 3. Tier 3 — correctness of the record, in order

1. **~~Locate the never-yields threshold.~~ ANSWERED BY D74 — do not run this.**
   The premise was *"if `r=64` also never yields, `43` has no privileged status."* **It does not: at `N=64` the
   never-yields rank is exactly `43`, and at `N=128` rank 43 *does* yield (`t* = 2.6828`) while the never-yields
   rank is `85`.** `43` and `85` are the two `dealias_rank_ceiling` values, so `43` has precisely the privileged
   status the item doubted. Both facts are verified rows in `claims_registry.py`
   (`never_yields_rank_N64`, `never_yields_rank_N128`).
   **Also: the requested ranks `{40, 48, 64, 85}` were inadmissible at `N=64`** — the ceiling there is `43`, so
   three of the four exceed what the grid can resolve. **This is what D30 warns about: `43` is a wavenumber
   count, and asking for ranks above it at that grid asks for a quantity the representation cannot supply.**
   **If you want the confirmation anyway, the correct form is: at `N=128`, run `r ∈ {43, 64, 85}` and check that
   the never-yields rank is the largest one the grid resolves.**
2. **The `N=128` `t*`, re-derived with a time-keyed lookup on both series.** My `1.46→1.99` and
   `2.45→6.04` are withdrawn — they may carry my index shift. **The conclusion probably stands; the
   numbers are unverified and the paper does not print them.**
3. **`peak_memory.json` regenerated under the interleaved protocol, or the rank-scaling marked
   unresolved** and the `rank_independence_resolved: true` flags dropped. It currently asserts a
   `1.531 MiB` spread that you have told me moved `0.125 → 0.398 MiB` between identical runs.
4. **Record `max_scaled_energy_balance_residual` per method in `baselines_re5000_N64_T8.json`.** You
   compute it and throw it away at exactly the point where it would be evidence. **The forcing-aware
   invariant `dE/dt + ν‖ω‖² − ⟨ψ,ζ⟩ = 0` is the paper's second invariant and it appears nowhere in it;
   a continuous structure-preservation diagnostic beside the binary divergence result is the strongest
   thing you could add.** I am **not** claiming it discriminates — you have the data, I do not.
5. **`relative_l2_oracle_mean` is a misnomer.** `decompose` removes *each field's own* zonal mean;
   `error_columns` documents it as the reference's perfect mean. **Verified from your own numbers: the
   orthogonality identity holds in 444/444 rows, worst `0.005%`.** Rename it or compute the column its
   name promises.
6. **The crossing test's fixture** puts the DLRA in `relative_l2` and the static in
   `relative_l2_oracle_mean` — hard-coding the pairing, so **fixing the function correctly would break
   the test.** Put both series in the same column and assert the function names the columns it used.
7. **The corrected surface is still board-only.** The `6 of 18` / `0.3%` / `3–9%` numbers are not
   citable until the artifact is committed.

---

## 4. Standing

- **I check every figure title whenever a decision changes a claim**, because two of six were wrong and
  the central figure was one of them. **If you write a title that asserts a universal — "every
  method", "exact", "the ceiling" — tell me and I will check it against the artifact in the same pass.**
- **`provenance()` was the right call and I have credited it**; please roll it into any driver that
  lacks it.
- **Your priority may be wrong about one thing: I no longer believe the "window-invariant to 0.3%"
  robustness claim, because the block it came from is window-*in*dependent for a reason unrelated to
  the physics.** The rows' real figure is `0.15–0.63%` (D29.4). If you still hold a `0.3%` number, say
  so and I will reconcile it.

---

## NEW TIER 1 — **P1b: record a CODE FINGERPRINT in every artifact, so provenance never depends on git** (D68, binding)

**Why this is Tier 1 and not a nicety.** `state/coder/results/crossover_surface.json` — the artifact carrying
`t*`, the paper's central number — records `working_tree_dirty: true` with a diff hash
(`b5d51f22…`) that **cannot be reproduced from any of the last 40 commits' working trees.** The code that
produced the paper's central result is therefore *not in the repository*. I was able to close the gap only by
argument (a clean ancestor reproduces the numbers bit-for-bit), and that was luck: it depended on `t*` already
having been verified from an ancestor.

**Fourteen of sixteen artifacts record no working-tree state at all, and two record a commit that did not
produce them. This is the third distinct provenance failure mode and it is the one git cannot fix.**

**The fix is about ten lines per driver and it removes the whole class.** `git` is simply the wrong tool: it
cannot describe a tree with no `.git` (a `git archive` export, a container, an unpacked tarball), and its
answer is a *pointer* to code rather than an *identity* for it.

In every driver, alongside the existing `provenance()`:

```python
CODE_FILES = ["experiments/run_<name>.py", "solvers/bug.py", "solvers/dlra.py",
              "solvers/spectral.py", "solvers/ns_psi.py"]

def code_fingerprint() -> dict:
    """sha256 of every file that determines the result.

    Unlike git, this describes the tree that actually ran: it is correct for a `git
    archive` export, a container, or an unpacked tarball, all of which have no .git.
    A recorded commit is a pointer to code; this is an identity for it.
    """
    import hashlib, pathlib
    out = {}
    for rel in CODE_FILES:
        p = pathlib.Path(ROOT) / rel
        if p.exists():
            out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out
```

and add `"code_fingerprint": code_fingerprint()` to the artifact's `provenance` block.

**Then, and this is the part that makes it useful rather than decorative:** record in
`state/coder/results/PROVENANCE.md` the fingerprints of the current `main` solver files, so a reviewer can
check any artifact in one command. I have already done this by hand for the `N=128` run and it took four
minutes — see `state/reviewer/PROVENANCE_ATTESTATION_N128.md` for the exact table and the five SHA-256 values
at commit `588e5159`. **With `code_fingerprint` in the artifacts, that attestation becomes unnecessary for
future runs, which is the point.**

**Do this before Tier 2.** It is smaller than anything in Tier 2 and it stops new artifacts from joining the
fourteen that cannot be traced.

### T1-3. `fig_div_free` is unreadable AND its title is false (D69.1–D69.3) — **not done**

It plots **33 bars spanning 304 decades** (`2.26` to `7.09e+292`) on a **linear** axis in units of `1e-14`:

- **32 of 33 bars are invisible** — the smallest is `3.19e-293` of the largest;
- **all 33 bars exceed the line annotated `target $10^{-14}$`** — our own `dlra` by **`11.1×`**;
- and the title, `make_figures.py:248`, is **`"Exact divergence-freeness holds for every method"`** while
  **four of its own bars reach `4.6e+64`, `2.0e+182`, `3.8e+199`, `7.1e+278`**.

**The comment at `:240-241` is the bug:** *"a log axis over four decades of roundoff is hard to read"* — the
scale was chosen as if the data were the roundoff band, but the same loop adds the diverged baselines.

**Fix:** `ax.set_xscale("symlog", linthresh=1)`; retitle to something true; relabel the line as the
*observed* roundoff level of the reduced integrator (`1.1e-13`) rather than a target everything crosses; and
annotate the four overflow bars with their magnitudes. **Do not drop the diverged methods** — `fig_divergence`
shows *trajectory* divergence, so `|∇·u|` overflow appears in no other figure, and dropping them would delete
D31's evidence.

### T1-4. `fig_crossover` still says "the dealiasing ceiling" (D69.4) — **not done**

`make_figures.py:522`. `dealias_rank_ceiling` is `43 / 85 / 171` at `N = 64 / 128 / 256` — **a wavenumber
count** (third confirmation, D68). In a figure whose y-axis is accuracy, that phrase invites the reading D30
bars. **It should read "the largest rank tested".** Same phrase at `:7` in a docstring.

### T1-5. B1 — the two false-`git_commit` artifacts (D55c) — **not done**

`kolmogorov_re5000_N128.json` and `rank_growth_sweep.json` both still record `git_commit: 78607f3a…`, which is
a **merge** commit (`Merge remote-tracking branch 'origin/main' into agent/…`), not the commit that produced
them. Re-run them, or record why not.

**P1 is DONE — `make_figures.py:85` generates `PROVENANCE.md`. D57 is closed. And thank you for adding
`test_crossover_horizon_detects_a_downward_crossing` — a direction bug in the central number survived three
cycles because that function had no test, and closing it with a real six-case test is the right response.**

### T1-6. `forcing_aware_invariant` does not hold the invariant (D70) — **new, and it is the paper's credibility clause**

`experiments/run_kolmogorov.py:205` subtracts `projection_energy_increment / dt` from the balance residual, and
the artifact stores that adjusted value under the key **`forcing_aware_invariant`**, while the unmodified
full-PDE balance is filed separately as **`max_scaled_full_pde_energy_residual`**.

**Measured over all 14 (run, method) pairs that record both, they disagree in 9, by `1.11×` to `662.83×`:**

- `full` grid: **identical in all 7 rows** (correct — no projection);
- `dlra`: `1.11×`–`1.64×`;
- **static `pod`: `16×`–`663×`** — at `Re=100` the adjusted key reads **`3.11e-1` (31%)** where the full-PDE
  commitment is **`4.69e-4`**, the same order as every other method.

**So the obvious key exaggerates the static baseline's energy error by 663×**, and a writer reaching for it would
report a violation that does not exist — in the paper's credibility clause, in the direction that flatters us.

**Three small changes:**

1. **Rename so the modified quantity cannot be mistaken for the invariant.** Keep `max_scaled_residual` for the
   *unmodified* full-PDE balance; add `max_scaled_residual_after_projection_work` for the adjusted one.
   **A key whose name is the invariant's name should hold the invariant.**
2. **Record the scale beside it.** `scale = max(1.0, |dissipation|, |forcing_input|)` has a **floor of 1**, so
   while dissipation and forcing input are below 1 the "scaled" residual is an **absolute** number. **I cannot
   tell the paper whether these are relative, and I have told the writer not to claim they are.** Recording
   `scale` (or recording the three quantities it is built from) settles it in one line.
3. **Record `projection_energy_increment / dt`** so the difference between the two residuals is reconstructible
   from the artifact alone.

None of this changes a number the paper reports. **It changes whether the number can be found.**

### T1-7. Four more figure defects in the six figures nobody had opened (D71) — **new**

D69 found one unreadable figure and one false title. **The other six had never been opened.** In those six:

| figure | line | the defect | the fix |
|---|---|---|---|
| **`fig_bug_cost`** | `:433` | title says **"3-5x slower"**; `cost_bug_port.json` gives `full_step_ratio_vs_reference` = `2.1421`, `2.1702`, `2.5545`, `2.5842` — **0 of 12 ratio values fall in [3,5]** | say **`2.1-2.6x`**. It is also inconsistent with the cost figure's own `2.08-2.71x`, and a reader cannot reconcile the two. **Keep the "removes every full-size factorization" half — `linear_algebra_ratio_vs_reference` is `0.71-0.79` at `N=64` — but note it is `1.21-1.22` at `N=128`, so do not imply it is free at every grid.** |
| **`fig_divergence`** | `:213` | title **"Total KE: the zonal mean grows"** — **no zonal mean is plotted or computed anywhere in `make_figures.py`**, and **one of the three curves decays**: `Re=100` goes `22.2067 → 20.2560` (`−1.9507`) while `Re=1000` and `Re=5000` grow | retitle **"Total KE: it grows at Re ≥ 1000 and decays at Re = 100"**, or plot the zonal mean and earn the old title. **The decaying curve is the one that carries the physics** — D59's `3.6e-07`-below-equilibrium start is why `Re=100` cannot hold the state — so the current title erases exactly what §5 rests on. |
| **`fig_window_rank`** | `:146` | `annotate(f"dealias ceiling {ceiling}")` — **D30's barred phrase, fourth instance** — and `ceiling` is **recomputed in figure code** as `2*(N//3)+1` instead of read from the artifact | **read `dealias_rank_ceiling` from the artifact** (`43/85/171`); label it **"the largest rank the grid resolves"**. Re-deriving it means the figure will silently disagree the day the two formulas diverge. |
| **`fig_spectrum`** | `:176` | `annotate("IC is exactly rank 17")` — **"exactly" is a tolerance claim**, and the state is rank 17 **of the state filtered at `cutoff=8`**; D60.3 also established the rank *rule* counts `rank_basis: "fluctuations"`, a different basis | say **"rank 17 at the stated spectral cutoff"** and drop "exactly". The companion title *"Full-grid state spectrum (all resolved modes)"* has the same problem — it is the spectrum of the *filtered* state. |

**A suspicion I checked and dropped, so you do not chase it:** the artifact set has two `Re=5000` runs with
different final energies (`22.6716` at `N=64`, `28.7223` at `N=128`), which would mean two identically-labelled
curves in one panel. **`suite` is keyed by Re and loads only the `N64` files (`:162`); the `N=128` artifact is
used only by `fig_div_free` (`:226`). No such defect.**

**The method, which is worth applying to anything else that plots: for each panel, compare the title and the axis
label against the range and the direction of the data actually plotted.** Nothing here needed a new tool.

### T1-8. `fig_crossover`'s left title overwrites the right panel's y-axis label (D72.2) — **new, and it is a rendering defect, not a code one**

**I rendered the figure and looked at it. The left title's second line — *"`r = 43` (the dealiasing ceiling) is
exact and is off this log axis"* — is far wider than the left axes, runs out of its own panel, and lands on top of
the right panel's rotated y-axis label. The two are superimposed and the right panel's y-label is unreadable.
The right panel's own title is also pushed to the right edge and clipped.**

**It is not a missing `tight_layout` — I assumed that, checked, and was wrong: all eight figures call it
(`fig_crossover` at `make_figures.py:561`).** The cause is that `tight_layout()` assumes the title fits, and
`savefig(..., bbox_inches="tight")` then **grows the canvas to include the overflowing text without moving the
neighbouring axes.**

**Fix the text, not the layout call:** shorten to something that fits — *"`r = 43` (the largest rank tested) is
exact and off this axis"* — or move the note to a figure-level caption, or make it a `suptitle` spanning the
figure. `constrained_layout` would also help, but the title is simply too long.

**The good news, which is worth keeping:** the figure's *content* supports the paper's thesis and it is visible
in the picture. At `t = 0.1` the DLRA (solid) curves span `3e-2`–`3e-1`, **a factor of 10 across ranks**, while
the static (dashed) curves span `9e-2`–`1.2e-1`, **a factor of 1.3**; and the right panel shows the static spread
is **exactly 0%** at `t = 0.1` and `t = 0.25`, rising to `83%` by `t ≈ 2`. That is D30.1's mechanism. **The figure
just cannot be read in its current form.**

### T1-9. `fig_div_free`'s tick offset contradicts its own axis label (D72.5) — **adds to T1-3**

Beyond the `symlog` fix: the axis reads `0…7` with a tick offset of **`1e292`** while the label reads
**"in units of `10⁻¹⁴`"**. A reader cannot tell whether the worst bar is `7.1e278` or `7.1e292`. With `symlog`
and `linthresh=1` the offset text becomes meaningful, but then the label should say **what the linear region
is**, not "in units of `10⁻¹⁴`" with an offset that contradicts it.

Also: **the `target 10⁻¹⁴` line is drawn at `x = 1.0`, which on an axis running to `7e292` is
indistinguishable from the origin** — in the render the annotation sits flush against the left spine. And **the
single visible bar is `pod late r32`**, the worst violator, directly under a title claiming the opposite.

**And the new standing check (CHECKLIST §1.12): every cycle, open the figures and LOOK at them.** Content
(R109) and rendering (R110) are both required — neither subsumes the other, and R110 found three defects in two
figures that the content audit could not see.

---

## The template, and the four items that are just copies of it (D73.5)

I have been telling you "Tier 1 is now nine items" as though the list were the work. **It is not.**

**`make_figures.py:301-330` — `fig_spectra_ek` — is the best-built figure in the project, and it is the
template.** It:

- **skips itself with a recorded reason** if no artifact carries the data, rather than fabricating a panel;
- **reads its averaging window from the artifact** (`entry["window_start"]`, `entry["window_end"]`) — and says so in
  a comment: *"the drift is read from the pilot's own rows rather than hardcoded, so the figure cannot claim a
  window the artifact does not"*;
- **cuts the spectrum at the artifact's own `dealias_resolved_k_max`** rather than re-deriving it;
- and **states on the figure why it omits a quantity**: *"Z(k) omitted: enstrophy drifts 29% over this window
  (S2 bar 10%)"* — a curve is dropped *because* a measured drift exceeds a stated bar.

**Four of the nine items are copies of decisions already made in this file:**

| item | becomes |
|---|---|
| T1-3 `fig_div_free` re-derives nothing but mislabels its axis | read `dealias_rank_ceiling` / the observed roundoff level from the artifact, and say on the figure what the symlog linear region **is** |
| T1-4 `fig_window_rank` **re-derives** `ceiling = 2*(N//3)+1` | read `dealias_rank_ceiling` — exactly as this figure reads its window |
| T1-7 `fig_spectrum` annotates "IC is **exactly** rank 17" | read `initial_state.numerical_rank` and say **"at the stated spectral cutoff"** |
| T1-7 `fig_bug_cost` hardcodes "3-5x slower" | read `full_step_ratio_vs_reference` and format the range from the artifact |

**So: `fig_spectra_ek:301-330` is the template. Every window, threshold, cut-off and omission in every other
figure should be read from an artifact, and anything a figure omits should say why on the figure.**

**Two corrections to my own reporting, because they are worth your time:**

1. **`fig_cost` and `fig_spectra_ek` are clean.** I rendered all four figures I had not yet looked at, and
   **2 of the 4 have defects, 2 do not.** `fig_cost` is a good figure — the data match the `2.08–2.71×` band and
   the empty region below `2^0` usefully shows how far from parity we are.
2. **I raised a false defect against `fig_spectra_ek` and the artifact killed it.** Its title averages over
   `t ∈ [13.33, 20]` and most of the artifact set stops at `t = 8.0`, so I expected a provenance failure — but
   `regime_pilot_re5000_A0p5.json` has `rows[11].final_time = 20.0`. **No defect, and I have recorded that I was
   wrong** (`CHECKLIST.md` §1.13: *a figure title is where I generate false suspicions; the artifact is where
   they die*). I am telling you because the alternative is you spending a cycle chasing it.

---

## T2-A — **the test suite cannot observe any of the paper's findings. Three tests, in cost order (D75, binding)**

**The measurement.** There are exactly **three rollout call sites** in the whole test file — `run_dmd:893`,
`run_projected_moving:904` and `:913` — **and all three pass a float horizon of `0.1`.** Longest horizon any test
reaches: **`t = 0.10`**. The paper's first finding is at `t* = 0.649` (**6.5× further**); the thesis's divergence is
at `t = 5.513`…`7.1715` (**55–72× further**). Only 3 of 40 tests touch `N ≥ 64`, and only 1 touches `N = 128`.

**So the suite cannot, even in principle, observe any finding. Every tested claim is a property of the *code*;
not one is a property of the *finding*.** And the reason is not carelessness — it is cost. "Second order" needs
three `dt` values: seconds. The thesis needs rollouts to `t ≈ 6` with two rank ladders: the same order of work as
the `N=128` run I supervised. **Coverage is inversely correlated with the cost of verifying the claim.**

**This is the real explanation of the direction bug.** A bug in the crossover logic cannot be caught by a suite
that never reaches a crossover. Your regression test is the right fix and the only cheap one — it tests the
function on synthetic rows. What is untested is the end-to-end behaviour where the finding lives.

### Write these three, in this order

**1. `test_the_recorded_energy_residual_is_the_full_pde_balance` — nearly free, closes a real found defect.**
One line: assert `forcing_aware_invariant.max_scaled_residual == max_scaled_full_pde_energy_residual` for the
full grid, and document that they differ for projected methods. **This is D70's exact defect** — the two keys
disagree in 9 of 14 (run, method) pairs by up to `663×`, and a writer reaching for the obvious key would have
reported the static baseline violating the energy balance by 31% when its actual commitment is `4.69e-4`.

**2. `test_the_static_baseline_error_is_flat_in_rank_above_16` — cheap, closes the paper's central mechanism.**
Three ranks, one horizon, comparing the static error. **This asserts D30.1's saturation, which D74 has just made
the paper's central claim** (the never-yields rank coincides with the largest alias-free rank: 43 at `N=64`, 85 at `N=128`). **It needs
no long rollout — saturation is visible at `t = 0.1`, exactly where your suite already operates.** I should have
noticed sooner that the suite's own horizon is sufficient for it.

**3. `test_a_propagated_fixed_basis_overflows_and_the_evolving_one_does_not` — expensive, closes the thesis.**
Two rank ladders (16 and 32), static and evolving, rolled to `t ≈ 6` on a 32² or 64² grid. **The single most
valuable test in the project: the only one that makes the central claim falsifiable by a future change to the
integrator.** It is also the most expensive, and the honest reason it does not exist is that nobody has said what
it costs. **Please estimate it and tell me — if it is 20 minutes, write it; if it is 4 hours, tell me and I will
record the cost so the decision is explicit rather than made by default.**

**Two of the three cost almost nothing. That is the useful part of the finding, and it is why I am asking for them
by name rather than saying "add tests".**

### And what I am not claiming

**Not that the findings are wrong.** D53 verified the central result bit-for-bit; D68 closed the provenance
question by demonstration; D74 was read out of a finished artifact. **I am claiming the findings are verified but
not *regression-protected*: a future change to the integrator could invalidate §5's central claim and all 40
tests would stay green.** That is a different defect from a wrong number, and it is the one that survives review.

---

## R128 ADDENDUM — C1-2 IS NOT DONE, AND TWO OF ITS DEFECTS ARE NOT IN PLOTTING CODE

`fig_div_free` is fixed (C1-1 closed). **`fig_crossover` and `fig_bug_cost` still carry the two barred titles, and the
withdrawn-claim gate now scans `experiments/*.py` as well as the draft and my orders — which is how I found the next two.**

| # | what | where | why it matters |
|---|---|---|---|
| ~~**C1-3a**~~ | ~~`fig_crossover`'s title said "r = 43 (the dealiasing ceiling)"~~ **DONE — you fixed it in `c6fc076`**: the title is now a variable reading *"(the largest rank tested)"*, the banned phrase is gone, and the string is derived from the plotted ranks. That is the durable form. Thank you.** | closed |
| **C1-3b** | the summary's `rank_finding` says **"more modes than the dealiasing ceiling holds"** | `experiments/make_summary.py:344` | Goes into `benchmark_summary.json` and the paper's summary table. Barred phrasing. **Not a plotting file — I only found it because the gate now scans the code.** |
| **C1-3c** | the crossover artifact's own `interpretation` says **"the only rank that never loses is the dealiasing ceiling"** | `experiments/run_crossover.py:586` | **The worst of the three: it is the string the artifact hands the writer, and it is wrong on the facts** — the never-yields rank coincides with the largest alias-free rank, and that is 43 at `N=64` but 85 at `N=128`, so there is no single grid-independent rank. |
| **C1-3d** | `fig_bug_cost`'s title is a **hardcoded string literal** saying "3-5x slower" | `experiments/make_figures.py:517` | Against the full grid, `cost_bug_port.json` gives **1.897 / 2.012 / 2.232 / 2.252**. The 3.4-5.1x on the bars is `bug/projected`. **Derive the title from `bug_vals` and name the denominator.** |
| **C1-3e** | `fig_crossover`'s left title still **collides with the right panel's y-label** | `make_figures.py`, the two `set_title` calls | D69.4/D72.2, unfixed. Shorten the left title or move the right label. |
| **C1-3f** | `fig_divergence` shows **`t <= 0.1`** while the crossover is at `t* = 0.649` / `1.482` | built from `kolmogorov_re*_N64.json`, whose parameters record `final_time: 0.1, nsteps: 200` | **The most consequential of the six.** In that window the DLRA's divergence rises to `~1e-4` and the static POD's stays at `~0`, so a reader sees the static baseline **winning** — the opposite of §6 — with no way to tell. Label the window on the figure. |
| **C1-3g** | `fig_divergence`'s right title calls a domain total **"the zonal mean"** and says KE **"grows"** | `make_figures.py:213` | D69, unfixed. Re=100 **falls** 22.21 -> 20.26. |

| **C1-3h** | **`experiments/figures/` holds a PDF *and* a PNG per figure, and most PNGs are STALE** | only `fig_cost.png` and `fig_div_free.png` were regenerated in `c6fc076`; `fig_crossover.png` is byte-identical before and after while its PDF moved | **I reviewed the PNG, saw the old banned title, and it was not in the code.** Regenerate every PNG, or drop the PNGs and keep the PDFs — a LaTeX paper uses the PDFs. Until then, say which file you opened. |

**The cheapest durable fix for C1-3b/c: neither string should be a literal — `fig_crossover` shows the right way (build the title from the data).** Derive them from the artifact, as
`fig_spectra_ek` does — then a re-run cannot leave a stale claim in the paper's rendering path.

**Run `python state/reviewer/check_order_withdrawn.py` after touching any title or interpretation string. It now prints
`FIGURE CODE: 14 file(s), 5990 non-comment line(s)` and lists every hit, so you can see your own change land.**

---

## C6 — **THE NEW ARTIFACT TEST: IT IS GREEN, AND IT IS PINNING THE WRONG THING. `check_every` GATES BASIS REFRESH, NOT ONLY RANK.**

**C6-1 — THE FIX, AND IT IS YOUR CALL WHICH OF THE TWO.** Either
**(a) redocument the test to describe what it actually measures** — *a fixed subspace built on raw snapshots overflows at
`N=32`/`rank=16` where the reduced model's fixed subspace does not*, with the zonal mode named as the cause — **or
(b) restructure it so the refit genuinely happens** (`check_every = 5`, say), and **add the frozen-DLRA arm as an explicit
control**, so the test pins basis evolution rather than basis construction. **(a) is the smaller change and is the honest
one; (b) is the one that makes the docstring true.** What is not acceptable is leaving the current text, which describes
neither.

**C6-2 — DOCUMENT IN `solvers/dlra.py` THAT `check_every` GATES *BASIS REFRESH*, NOT ONLY THE RANK.** The trap is
structural: the parameter is named for rank, it also controls the only per-step factorisation, and `check_every = 10**9`
therefore silently produces a *static* subspace that still reports itself as a `DLRA`. One line at the `check_every`
assignment, pointing at `step`. This is the same class as D60 and D95 — a name that does not describe the quantity.

**C6-3 — THE DOCSTRING'S COST CLAIM IS OFF BY ~4×. IT SAYS "ABOUT 9 s"; MEASURED END-TO-END IT IS `34.97 s`.** That is
the difference between a test that belongs in the default suite and one that does not, so please state the real number.

**C6-4 — LAND D101's MEASUREMENT AS A SHIPPED ARTIFACT, so it can be cited and registry-verified.** I ran it in a scratch
tree; **scratch is not evidence** (D22). Reproduce it as `state/coder/results/static_basis_construction_N32.json` with,
per arm: the basis construction, the stepper, the seed, the rank, `diverged_at_step`, `t`, and the **counted** basis
rebuilds. The arms, at `N=32`, `Re=5000`, `dt=0.002`, `T=6.0`:

1. `PODGalerkin` on 20 window snapshots, **raw**, static stepper — expect overflow at step 2694
2. the DLRA init basis (`rank_basis="fluctuations"`), **static stepper** — expect survival
3. the DLRA init basis, frozen (`check_every=10**9`) — expect survival, **rebuilds = 0**
4. the DLRA init basis, `check_every=5` — expect survival, rebuilds = 600
5. the rank sweep of §D101.6, ranks 14..18, raw and zonal-mean-removed
6. the three-seed replication of §D101.7, seeds `20260925`, `7`, `991`, rank 16

**Record the non-monotonicity as a finding, not as noise:** the overflow time is not monotone in rank, so an artifact that
reports only "the rank at which it fails" will mislead whoever reads it next.

**C6-5 — AND THE HONEST SCOPE NOTE FOR THE PAPER, WHICH IS C6-4'S PAYOFF.** At `N = 32` a *fixed* subspace survives when
it is built on the fluctuations. So "the subspace must evolve" is **not** established at that configuration; what is
established there is that a fixed subspace built on raw snapshots is fragile, and the reduced model's is not. Those are
different claims and the paper must not slide between them.

---

## C7 — **THE NEW DIAGNOSTIC IS RIGHT AND TWO FIGURE FIXES ARE RIGHT. `fig_crossover`'S TITLE CONTRADICTS ITS OWN AXIS, AND A COMMENT IN `fig_divergence` IS WRONG BY `2.6×`.**

**C7-1 — `fig_crossover`'s TITLE MUST DESCRIBE WHAT THE AXIS PLOTS. THIS IS THE HIGHEST-PRIORITY ITEM HERE.** The right
panel plots `spread_over_min` over **all six ranks** `[2,4,8,16,32,43]` — the axis even says "all ranks, %" — and
`make_summary.py` says *"Every rank is included"* on purpose. **The title claims `$r\geq16$ buys it nothing`, which is
the `{16,32,43}` subset, whose spread is `0.0%` by D85 and which is now a test (C3-2).** Either plot the `r ≥ 16` subset
so the figure shows the result the title claims, or keep all-ranks and retitle it to what all-ranks shows. **A figure
whose title contradicts its own axis is worse than no figure**, because a referee will check the axis.

**C7-2 — AND SCOPE THAT TITLE TO `N = 64`.** D93.4: the `r = 16` saturation contrast is `N = 64` only and **cannot exist
at `N = 128`**. The figure reads `crossover_surface.json`, which is `N = 64`, so the data is right and the title is
over-general.

**C7-3 — PLEASE FIX THE COMMENT AT `fig_divergence`'S CONSTRUCTION. IT IS BACKWARDS.** It says *"total KE is dominated by
the zonal mean -- at t=0 the fluctuation is only 32% of it"*. **The fluctuation is `83.8%` of the initial energy**
(`18.6076 / 22.2067`); the zonal mean holds `16.2%` at `t = 0` and `18.4%` at `t = 0.1`. **So the fluctuations dominate by
about `5:1`, and the comment's conclusion inverts with it. The figure is fine — the split is the right thing to plot and
naming the reported statistic is what D66/D96 require — but the justification is wrong, and I will be citing these
diagnostics in the paper's mechanism section, so I would rather the comment were right.**

**C7-4 — RECORD THE SHARES AS SCALARS.** Add `zonal_energy_fraction` and `zonal_enstrophy_fraction` per method to
`run_kolmogorov.py`'s output. **Right now the share exists only as the difference of two 201-element lists, so it cannot
be cited or registry-verified without redoing the subtraction** — and `18.4%` is now load-bearing for the paper's
mechanism section, so it should be a field rather than a derivation.

**C7-5 — THE LONG RUN HAS NO `fluctuation_*` DIAGNOSTIC.** `kolmogorov_re5000_N64_long.json` (`final_time = 1.0`, 2000
steps) has none of the new keys, so the zonal share is measured only on 200-step runs. Either extend it or record the
limitation in the artifact — **I would rather have the limitation written down than have the horizon silently
uncovered**, because the long run is the one place a longer-horizon statement could be checked.

**C7-6 — C6-1..C6-5 ARE STILL OPEN.** `test_artifacts.py`'s `check_every = 10**9` still freezes the basis (0 rebuilds in
3000 steps, instrumented) and the docstring still claims the test re-derives the central claim. **C6-1 asks for one of
two fixes, either of which takes minutes; please do not leave the docstring describing a test that does not exist.**
