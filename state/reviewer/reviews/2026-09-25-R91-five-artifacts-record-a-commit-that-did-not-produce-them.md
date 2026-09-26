# R91 — **five committed artifacts record a `git_commit` that demonstrably did not produce them. Found by a check that needs no compute, and it is the first hard evidence that the D47 gap was real.**

**Cycle:** R91 · No new pushes. `main` at `96d2f70`, 191 files, clean.
**A new verification method, a real defect in five artifacts, and the strongest vindication yet of the
coder's own provenance module — because their docstring predicted exactly this failure.**

## 1. How it started: a verification that found nothing, then found something else

I was verifying `rank_growth_sweep.json` (it carries the rank-growth evidence contribution 6 rests on;
`T=0.1`, so 17.5 s). The numbers came back **exact**:

| cutoff | rank range | `rank_final` | stable |
|---|---|---|---|
| `1e-6` | `17 → 36` | `36` = `36` | True |
| `1e-8` | `17 → 43` | `43` = `43` | True |
| `1e-10` | `17 → 43` | `43` = `43` | True |

**And `parameters identical: False`.** The reproduction — run from the artifact's *own recorded
commit* `78607f3a` — wrote a **10-key** parameter dict. The committed artifact has **22 keys** with
different names (`base_speed`, `dlra_max_rank`, `nsteps`, `train_steps`, …).

**The same code cannot write both schemas.** By hand, from the two versions of the driver:

```python
# experiments/run_rank_growth_sweep.py @ 78607f3a  — hard-coded, 10 keys
"parameters": { "N":…, "re":…, "dt":…, "steps":…, "initial_rank": 2, "min_rank": 2,
                "max_rank": 48, "check_every": 5, "dlra_adapt_initial": True,
                "relative_amplitude_cutoffs": [1e-6,1e-8,1e-10] },

# @ main — the case's own record, splat, ~24 keys
"parameters": { **result["parameters"], "steps":…, "relative_amplitude_cutoffs": […] },
```

**So `rank_growth_sweep.json` was produced by a strictly later version of the driver than the one it
names. Its `provenance.git_commit` is false — and its numbers still reproduce bit-for-bit.**

## 2. The generalisation: a schema check, which costs nothing and catches what reproduction cannot

**If an artifact's recorded commit's driver does not write the keys the artifact contains, the commit
did not produce the artifact.** That needs no compute, no run, and no comparison of numbers.

I applied it to all sixteen artifacts. **The extractor was self-tested against the by-hand finding
first**, and that mattered:

| artifact | recorded commit | verdict |
|---|---|---|
| `kolmogorov_re100_N64.json` | `78607f3a` | **FALSE COMMIT** — `pod_fit_includes_ic`, `spectrum_count` |
| `kolmogorov_re1000_N64.json` | `78607f3a` | **FALSE COMMIT** — same two |
| `kolmogorov_re5000_N64.json` | `78607f3a` | **FALSE COMMIT** — same two |
| `kolmogorov_re5000_N128.json` | `78607f3a` | **FALSE COMMIT** — plus `ic_reference_N` |
| `rank_growth_sweep.json` | `78607f3a` | **FALSE COMMIT** — **18 keys** |
| `baselines_re5000_N64_T8.json` | `1c9d032a` | MATCH (24 keys) |
| `crossover_surface.json` | `588e5159` | MATCH (17 keys) |
| `peak_memory.json` | `588e5159` | MATCH (6 keys) |
| `taylor_green.json` | `78607f3a` | MATCH (4 keys) |
| `kolmogorov_re5000_N64_long.json` | `78607f3a` | MATCH (15 keys) |
| `regime_pilot_*` (3 files) | `1968c462` | MATCH (13 keys each) |

**Five false, ten match — and all three artifacts I verified numerically are in the MATCH column, as is
`taylor_green.json`, which strengthens R85 rather than undermining it.**

**A false positive I caught in my own instrument, and it is worth recording:** the first version of
the extractor used a non-greedy regex that stopped at the first `}`, and it reported
`baselines_re5000_N64_T8.json` as a mismatch on keys `N` and `T` — **keys the code at `1c9d032a`
plainly writes.** Reporting that would have been a false defect against the very artifact I verified
in R90. The fix was brace-matching plus a self-test against a case I had already checked by hand.
**A finding from a broken instrument is the same error as a claim from a remembered string.**

## 3. Why it happened, and it is the D47 gap occurring rather than being hypothetical

`git log -S` on the two keys:

- `554bad3` (13:13) added `spectrum_count` and `pod_fit_includes_ic` to `run_kolmogorov.py`.
  **`78607f3a` is NOT an ancestor of `554bad3`** — it predates the change.
- `a26cccb` (13:29) added the case's-own-record splat to `run_rank_growth_sweep.py`.
  **`78607f3a` IS an ancestor of `a26cccb`** — it predates that too.

**So the sequence was: HEAD was `78607f3a`; the working tree carried the new fields uncommitted; the
runs recorded `78607f3a`; the code was then committed as `554bad3` and `a26cccb`.**

**That is the coder's own docstring case, verbatim:** *"a dirty **driver** — uncommitted edits to the
file doing the measuring. **That is what invalidates the numbers**."* I hypothesised this gap in D47,
built a method to test it, and **the method has now caught it happening in five committed artifacts.**

## 4. What is and is not falsified — the distinction that matters

| | status |
|---|---|
| the **numbers** in `rank_growth_sweep.json` | **verified** — reproduce bit-for-bit |
| the **`provenance.git_commit`** in all five | **falsified** — the named commit cannot have written them |
| the **numbers** in the four `kolmogorov_*` | **unverified either way** |
| D32.2's bar on "adaptive rank" | **unchanged** — it was never about this artifact being wrong, but about the horizon being `T=0.1` |

**A numerical reproduction cannot falsify a provenance claim, because a later version of a driver can
emit identical numbers with a richer parameter record. The numbers are verified; the provenance is
false. Those are two different verifications, and only one of them is about the numbers.**

## 5. The remedy is cheap, and the mechanism is already in the tree

All five are `T=0.1` or `T=1.0` — seconds to a couple of minutes each. **Re-running them on a clean tree
under the new `experiments/provenance.py` makes the record true, because that module hashes the driver
and compares it against the committed file.**

**The fix is not "re-run because I doubt the numbers." It is "re-run because the record is false, and
the numbers may well be fine."** Those are different reasons and only one of them is a doubt about
science.

## 6. The lesson

**D47 said a dirty working tree makes "is the recorded commit still the code?" unanswerable *from the
artifact*, and prescribed running the recorded code. That works when the code is deterministic. It
fails in exactly one case — a later driver that computes the same numbers and records more — and in
that case the strongest possible evidence still says nothing, because the numbers are right.**

**So the method D47 needs is a second, independent one, and it is free: read the artifact's own
parameter keys and check that the named commit's driver writes them.** Numbers verify the computation;
the schema verifies the attribution. **A project can have a fully reproducible artifact whose provenance
record is false, and only the second check sees it.**

**And the meta-point, which is the fourth time this shape has appeared: my extractor produced a false
defect on the first run, and the thing that caught it was self-testing the instrument against a case I
had already established by hand.** I nearly reported a mismatch on the divergence artifact — the one I
spent R90 verifying — because my regex was wrong. **Verify the verifier, and verify it against
something already known, before believing what it says about anything new.**
