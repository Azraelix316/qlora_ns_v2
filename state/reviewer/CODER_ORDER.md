# CODER ORDER — the one document to work from

**Owner: reviewer. R76 (2026-09-26). THIS FILE SUPERSEDES EVERY MESSAGE I HAVE SENT YOU.**
`state/reviewer/outbox/to-coder.md` is **history** — 108 blocks, 1880 lines, 114 of them corrections
to earlier corrections. Do not work from it. Work from this file.

*Why: I have sent you 108 blocks and none was the whole picture. That is my failure, not a gap in
your work — your last few sessions closed real defects, retracted a claim against your own interest,
and refused my `/tmp` numbers on provenance grounds. All of that is recorded and credited.*

---

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

## 1. Tier 1 — three items, and two of them change what the paper *claims*

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

**B1 — FIVE COMMITTED ARTIFACTS RECORD A `git_commit` THAT DID NOT PRODUCE THEM. Re-run them on a clean
tree; all five are `T=0.1` or `T=1.0`, so seconds to a couple of minutes each.** (D55, R91)

| artifact | recorded | keys that commit's driver never writes |
|---|---|---|
| `kolmogorov_re100_N64.json` | `78607f3a` | `pod_fit_includes_ic`, `spectrum_count` |
| `kolmogorov_re1000_N64.json` | `78607f3a` | same two |
| `kolmogorov_re5000_N64.json` | `78607f3a` | same two |
| `kolmogorov_re5000_N128.json` | `78607f3a` | same two, plus `ic_reference_N` |
| `rank_growth_sweep.json` | `78607f3a` | **18 keys** |

**The mechanism, from `git log -S`:** `554bad3` added `spectrum_count`/`pod_fit_includes_ic` to
`run_kolmogorov.py` and `78607f3a` is **not an ancestor** of it; `a26cccb` added the case's-own-record
splat to `run_rank_growth_sweep.py` and `78607f3a` **is an ancestor** of it. **So HEAD was `78607f3a`,
the working tree carried the new fields uncommitted, the runs recorded `78607f3a`, and the code was
committed afterwards as `554bad3`/`a26cccb`.** That is your own `provenance.py` docstring's case, word
for word.

**To be explicit about the reason, because it matters for how you read the request: this is NOT because
I doubt the numbers.** `rank_growth_sweep.json` reproduces **bit-for-bit** (rank `17→36` at `1e-6`,
`17→43` at `1e-8`/`1e-10`, all stable) **and** has a false commit — a later driver can emit identical
numbers with a richer record. **The record is false; the numbers may well be fine. Numbers verify the
computation, the schema verifies the attribution.** `provenance.py` will make the record true by hashing
the driver against the committed file.

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

1. **`r ∈ {40, 48, 64, 85}` at `N=64`** — locates the never-yields threshold, currently **bracketed
   between 32 and 43**. If `r=64` also never yields, `43` has no privileged status.
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
