# R5q — Cost-model audit: the projector is Θ(N³) and rank-independent, and the committed timings are not reproducible

**Cycle:** R5q (addendum to R5n figures audit and R5o gate costing)
**Scope:** `solvers/dlra.py`, `solvers/ns_psi.py`, `state/coder/results/*.json`
**Verdict:** two findings. **A** is structural and blocks any cost claim until V6.
**B** is a measurement-methodology failure that invalidates every committed timing.
One of my own earlier statements is corrected at the end.

All timings below: reviewer venv `/tmp/opencode/revvenv` (numpy 2.5.3, scipy 1.18.1),
`main` = `8d4098c`, `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`,
median of 7 repeats after 2 discarded warm-up calls, on the real workload
(`make_initial_state`, cutoff 8, Re=5000, `dt = 5e-4·64/N`).

---

## Finding A — the projector costs Θ(N³) per step and **does not depend on rank**

`SVDProjector._svd` (`solvers/dlra.py:72`) calls `np.linalg.svd(centered,
full_matrices=False)` on the **whole N×N field**, regardless of `self.rank`.
`StreamFunctionNS.step` (`solvers/ns_psi.py:145–179`) calls the projector at **four**
stage boundaries — `after_diffusion_half`, `after_midpoint`, `after_nonlinear`,
`after_diffusion_half_final` — and `DLRA.step` adds a fifth on adaptation steps.

So every step pays **4 dense N×N SVDs** (5 on adaptation steps). The per-step cost is
Θ(N³). Truncation rank `r` changes the *answer*; it does not change the *arithmetic*.

**Empirical proof, rank-independence** (N=64, `check_every` set so adaptation never
fires, threads pinned, median of 30 steps after 5 warm-up):

| fixed rank r | 2 | 4 | 8 | 16 | 32 | 48 | 64 |
|---|---|---|---|---|---|---|---|
| ms / step | 7.310 | 7.392 | 7.400 | 7.593 | 7.767 | 7.607 | 7.806 |
| SVDs / step | 4 | 4 | 4 | 4 | 4 | 4 | 4 |

A **32× range in rank moves the cost by 6.8%**, while the SVD count is constant. This
is the cleanest available statement of the problem and it should become a test, not a
sentence in a review (see R5q requirements below).

**Consequence, stated plainly:** in its current form the method **cannot** be faster
than the full-grid spectral solve at any `(N, r)`, because it performs strictly more
work per step — four Θ(N³) dense factorizations in place of one Θ(N² log N) step. This
is not a tuning problem and no tolerance or rank setting will change it.

### Measured full-step costs (threads pinned, rank = the working rank actually reached)

| N | full-grid step | DLRA step | ratio | one field SVD | 4× SVD | non-SVD work |
|---|---|---|---|---|---|---|
| 64 | 2.87 ms | 8.38 ms (r=43) | **2.9×** | 1.02 ms | 4.09 ms | 3.99 ms |
| 128 | 7.79 ms | 24.52 ms (r=48) | **3.1×** | 3.38 ms | 13.52 ms | 9.49 ms |
| 256 | 25.87 ms | 93.91 ms (r=46) | **3.6×** | 14.19 ms | 56.77 ms | 26.46 ms |

Rank 2 and the working rank cost the same to within 3% at every N
(8.40 vs 8.38 / 24.08 vs 24.52 / 91.05 vs 93.91 ms) — Finding A, confirmed on the
end-to-end driver as well as in isolation.

Measured scaling, 64→128 and 128→256: full-grid **2.71× / 3.32×**, DLRA **2.93× /
3.83×**, against ≈3.9× / ≈4.1× for pure `N² log N`. The DLRA curve is *closer* to
`N² log N` than a true Θ(N³) method should be, which is consistent with the SVD cost
being partly overhead-bound at these sizes — another reason to report the measured
scaling rather than the nominal complexity.

---

## Finding B — the committed timings are not reproducible, for two independent reasons

### B1. The runs are far too short to time anything

`state/coder/results/kolmogorov_re*_N64.json` all record
`parameters.final_time: 0.1`. At `dt = 5e-4` that is **200 steps and 0.9–1.2 s total**,
including interpreter start-up, BLAS thread-pool spin-up and first-touch page faults.
The recorded `wall_seconds_per_step` values (DLRA 4.50/5.90/4.60 ms, full
1.81/3.10/1.84 ms) are therefore overhead-dominated. R5n saw the symptom — the 1.7×
Re-to-Re spread for computationally identical work — and attributed it to warm-up
ordering. That attribution was right but understated: at 200 steps there is no regime
in which the measurement is not overhead-dominated.

### B2. Default multithreaded LAPACK `gesdd` is pathological in this environment

This is new and it is large. With threads unset (the environment default), a single
SVD costs:

| matrix | default threads | `OMP_NUM_THREADS=1` | ratio |
|---|---|---|---|
| 47×47 | 30 003 µs | 428 µs | **70×** |
| 64×64 | 82 008 µs | 700 µs | **117×** |
| 128×128 | 174 023 µs | 3 696 µs | **47×** |
| N=256 full | 508 020 µs | 22 520 µs | **23×** |
| N=128 full | 176 980 µs | 5 410 µs | **33×** |
| N=64 full | 106 010 µs | 1 340 µs | **79×** |

A 47×47 SVD cannot plausibly cost 30 ms; `scipy.linalg.svd(..., lapack_driver='gesvd')`
does the same factorization in 0.38 ms on the same matrix, and `eigvalsh` in 0.24 ms.
The pathology is thread launch/spin overhead inside `gesdd` at these sizes, not the
algorithm. It reproduces at `OMP_NUM_THREADS=4` (30 ms → 0.58 ms at r=47) and vanishes
at 1 and 4, so it is oversubscription, not a corrupt install.

**Why this matters more than a 1.7× artifact:** the bias is not a constant factor. It
depends on matrix size *and* on the data (a numerically low-rank field makes the QR
sweeps terminate immediately — that is why the committed rank-2 runs looked cheap), so
it distorts the DLRA/full-grid *ratio* in a direction that varies with the
configuration. Measured effect: the committed ratios are 1.90×/2.49×/2.50× (Re
100/1000/5000 at N=64) and 2.01× (Re 5000 at N=128), against true pinned values of
2.9×/3.1×/3.6×. **The committed artifacts understate the DLRA penalty by 20–36%.**

**Binding:** every timing in the paper and in every artifact must be produced with
thread counts pinned and recorded in the artifact. R5n already asked for the pinning to
be annotated; R5q establishes that it must also be *enforced*, because the unpinned
numbers are not merely noisy but wrong in a configuration-dependent way.

---

## The BUG arithmetic, honestly — including a correction to my own guidance

The V6 port (basis update + Galerkin) replaces four dense N×N SVDs per step with a
reduced QR of an `N²×r` matrix plus one `r×r` SVD on adaptation steps. Measured
directly (threads pinned, generic well-conditioned input, median of repeats):

| N | dense N×N SVD | QR of N²×r, r=43 | 4× SVD vs 1× QR | `2N²r²` vs `⅔N³` flops |
|---|---|---|---|---|
| 64 | 1.34 ms | 7.76 ms | 5.34 vs 7.76 → **worse** | 43× more flops |
| 128 | 4.84 ms | 8.59 ms | 19.4 vs 8.59 → **2.3× better** | 22× more flops |
| 256 | 19.50 ms | 13.15 ms | 78.0 vs 13.15 → **5.9× better** | 11× more flops |
| 512 | 136.19 ms | 12.23 ms | 544.8 vs 12.23 → **44× better** | 5.4× more flops |

Two things follow, and the first is the one I got wrong earlier.

**(i) The flop crossover is `r = 0.82·√N`, not `r ≪ N`.** A rank-revealing QR of the
`N²×r` matrix costs `≈2N²r²` flops against `≈⅔N³` for the dense SVD. The two are
equal at `r = √(2/3)·√N`. At the ranks this project actually uses (`r ≈ 43–48`) BUG
does **more arithmetic** than the dense SVD it replaces, at every N tested: 43× more
at N=64, 5.4× more at N=512. BUG wins on *arithmetic intensity and parallelism*, not
on operation count. A reviewer who checks the flop counts will find this, so the paper
must state it rather than imply otherwise.

**(ii) The 4× multiplicity is what rescues the port, and the crossover is between
N=64 and N=128.** Because the current projector pays four SVDs per step, the
comparison that matters is `4×SVD` against `1×QR`, and that flips at N=128. This is
exactly the "explicit crossover" R5o asked for, and it is now located rather than
open.

**(iii) Correction to my own earlier guidance.** In my R5 message to coder I wrote that
"no full SVD per stage is the only route to a cost figure that shows a **win** rather
than the permanent 1.5–2.5× loss". That was wrong, and the measurements refute it. Both
methods must evaluate the nonlinear term on the full grid, so both pay the same
Θ(N² log N) evaluation; BUG then adds `Θ(N²r²)` linear algebra on top, and
`r > log N` for every `(N, r)` this project will use. Full-step estimate
(shared nonlinear evaluation + QR + two `N²×r` products + `r×r` SVD amortised over
`check_every=5`; **optimistic**, as it excludes the Galerkin solve and any substepping):

| N | full-grid step | BUG estimate (optimistic) | ratio |
|---|---|---|---|
| 64 | 3.12 ms | ≈11.2 ms | ≈3.6× slower |
| 128 | 6.79 ms | ≈16.4 ms | ≈2.4× slower |
| 256 | 21.56 ms | ≈36.7 ms | ≈1.7× slower |
| 512 | ≈90 ms *(extrapolated from the measured 2.71–3.32× trend, not measured)* | ≈106 ms | ≈1.2× slower |

So the honest expectation after V6 is **near-parity by N=512, not a win** — a large and
reportable improvement over today's 2.9–3.6×, and still not a speedup. I am recording
this now so that coder designs the V6 experiment to *find the parity point*, not to
chase a crossover that the arithmetic says does not exist at these ranks. My R5o
phrasing "report N=128/256 and state the crossover" is superseded on the expectation,
retained on the requirement to state it.

---

## What the paper's cost claim may therefore be

Not "faster". A per-step speedup over the full-grid spectral kernel is not available
to this method at `r ≈ 45` and will not become available through the port. The
defensible claims, in descending order of strength:

1. **Rank-controlled cost that decouples the method from N.** DLRA cost is
   `Θ(N²r + r³)` against the full grid's `Θ(N² log N)`; the reduced model's *state* is
   `O(r²)`. The enabling claim is that a fixed-rank method reaches N=512/1024 at a cost
   the full grid cannot afford, not that it is cheaper per step.
2. **Accuracy at under-resolved Re.** At Re=5000, N=64 is demonstrably not resolved
   (R5m: enstrophy ratio 2.25× between N=64 and N=128). A rank-adaptive method that
   *filters* can be more accurate than an under-resolved full grid at comparable cost.
   This is the strongest available argument and it is an accuracy argument, not a
   timing argument.
3. **Matched-accuracy cost curves** (error versus wall time), which is the only
   comparison in which a filtered method can win, and which F6 must therefore plot.
4. **Adaptive rank tracking a developing spectrum**, which a fixed-rank POD cannot do —
   the R5m rank history (2→40 by step 50→43) is the evidence.

Reporting "slower than full grid" alongside these is required, and R5n already credits
the coder for not hiding it. That honesty is an asset; the correction is to stop
implying a speedup is coming.

---

## Requirements this adds (coder)

1. **Timing protocol, enforced not annotated.** Pin and record
   `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS` in every artifact that
   contains a timing. Discard warm-up, ≥7 repeats, report median with spread. Runs used
   for timing must be long enough that the timed region dominates process start-up —
   at `dt=5e-4`, that means ≥2000 steps, not 200.
2. **Make rank-independence a test.** A test that times steps at `r ∈ {2, 64}` and
   asserts the ratio is within, say, 1.25×, with a docstring stating that this is the
   *current* behaviour and that V6 must invert it. That way the property is pinned by
   the suite, and V6's improvement is visible as a failing-then-passing test rather
   than a claim in prose.
3. **V6 experiment design, corrected.** Measure and report **two** accountings: the
   linear algebra alone (`4×SVD` vs `1×QR + r×r SVD`, where the crossover at `r≈43` is
   between N=64 and N=128) and the full step (where the expectation is parity near
   N=512). Report the `2N²r²`-vs-`⅔N³` flop counts alongside. Do not present the
   linear-algebra win as a per-step win.
4. **F6 becomes error-versus-wall-time**, with the full grid and rank-matched POD on the
   same axes, plus the N=512 point if affordable. A cost bar with no accuracy axis
   cannot support any of the four claims above.
5. **`initial_state_sha256`** and the D1 step-0 error fix remain ahead of all of this;
   a timing measured on a rank-2 initialisation from a rank-17 IC is not a measurement
   of the method.

## What I did not verify

- I did not measure the Galerkin solve, the ODE integration, or any substepping BUG
  requires; the estimates in (iii) exclude them and are therefore optimistic.
- The N=512 full-grid step is extrapolated, not measured.
- All numbers are single-node, threads pinned, and specific to this machine; the
  *ratios* are the portable part, the absolute milliseconds are not.
- I did not test whether the reduced model permits a larger stable `dt`. If it does,
  the per-step comparison above is not the whole story — but that must be measured,
  not assumed, and it would be a legitimate V6 follow-up.
