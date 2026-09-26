# PROVENANCE ATTESTATION — the N=128 crossover run (attested while in flight)

**Attested:** 2026-09-26 · **By:** reviewer · **For:** the `N=128` crossover run launched from
`/tmp/opencode/x128`, whose output artifact will record `git_commit: "unknown"`.

## Why this file exists

`experiments/run_crossover.py::_git_commit()` returns the literal string `"unknown"` when it cannot
run git (line 73). The run was launched from a tree produced by `git archive <commit>`, which contains
**no `.git` directory**. So the artifact this run produces will record:

```json
{"git_commit": "unknown", "working_tree_dirty": null}
```

**That is expected and correct, not a defect** — and without this attestation the artifact would be
indistinguishable from the fourteen others that record no usable provenance (D55c). This is the first
time a provenance gap has been closed **prospectively**, while the run was still in flight, rather than
retrospectively after the fact.

## The attestation

**Source commit:** `588e51592bf026f790c5a4148481f26f78aca577`
("`[coder] regenerated …`", 2026-09-25T23:23:31+00:00)

**Extraction:** `git archive 588e5159 | tar -x -C /tmp/opencode/x128`

- `.git` entries in the extracted tree: **0**. An archive of a commit is that commit's tree exactly,
  so **uncommitted code is impossible** — the property every provenance verification in this project
  rests on.
- Verified by fingerprint, not assumed. All five files that determine the result are byte-identical to
  the commit:

| file | sha256 (first 16) at commit | in the running tree | |
|---|---|---|---|
| `experiments/run_crossover.py` | `1a787b05d601d68f` | `1a787b05d601d68f` | MATCH |
| `solvers/bug.py` | `d48510430d1ef3f3` | `d48510430d1ef3f3` | MATCH |
| `solvers/dlra.py` | `c79a49ca6dbe5e85` | `c79a49ca6dbe5e85` | MATCH |
| `solvers/spectral.py` | `2270043bde1da969` | `2270043bde1da969` | MATCH |
| `solvers/ns_psi.py` | `58e3526947d3a367` | `58e3526947d3a367` | MATCH |

**Exact command line:**

```
experiments/run_crossover.py
  --N 128 --re 5000 --force-amplitude 0.2 --base-speed 0.5 --cutoff 8 --seed 20260925
  --perturbation-velocity-rms 1.0 --window 0.25 --ranks 16 32 43 85
  --horizons 0.1 0.25 0.5 1.0 2.0 4.0
  --output /tmp/opencode/x128/crossover_N128.json
```

**Thread pins** (required on this node; unpinned LAPACK `gesdd` is 23–78× slower):
`OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`

**Why this is a proper grid refinement and not a different experiment.** `cutoff=8` is the
initial-state spectral filter and is **held** at the `N=64` value, so the two grids start from the same
family of states; `window`, `seed`, `force-amplitude`, `base-speed` and the horizon set are all
identical to the `N=64` run. `--ranks … 85` is exactly the `N=128` dealiasing ceiling
(`cost_retiming.json:grids[{N:128}].dealias_rank_ceiling = 85`), so the largest rank tested is the
largest rank that grid permits.

## Results as of this attestation (run still in flight)

| rank | `N=64` (`t*`) | `N=128` (`t*`) | ratio |
|---|---|---|---|
| 16 | `0.6493281145096707` | **`0.939`** | `1.45×` |
| 32 | `1.4816252539052939` | **`2.433`** | `1.64×` |

Ranks 43 and 85 pending. **The horizon lengthens under refinement at both resolved ranks**, which is
what D56 predicts: the reduced integrator converges under grid refinement while the static baseline
degrades, so the gap between them widens. `t*` is therefore **not grid-convergent over `64 → 128`**,
and the paper should say so with these numbers rather than "we do not know".

**Not yet done, and required before any of this is quoted (D22):** the finished artifact must be
inspected, the values read out of it rather than from this log, and registry rows added to
`state/reviewer/claims_registry.py`.
