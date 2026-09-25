# R82 — **the central number's provenance gap is closed: `crossover_surface.json` is reproduced bit-for-bit by the code at its own recorded commit.** Plus: the rows are path-independent, which had been an assumption.

**Cycle:** R82 · No agent pushed. `main` at `49cfa47`, 181 files, clean.
**Method:** R27 (*provenance beats fingerprint*) applied to the single artifact the paper rests on.

## 1. How this was found: R81's new gate item, on the same day it was written

R81 added "open each agent's most recent commit and read what it **contains**." Applied to the
coder's tip `1eb0432` (22:14), it turned out to touch **`experiments/run_crossover.py`** — the driver
that produced `t*` — which I had reviewed many times but **never in the diff that actually landed.**

The change is purely additive: a `provenance()` helper adding `working_tree_dirty` and a
`sha256` of `git diff HEAD`, in three drivers. **No change to the computation.** The coder's own
docstring names the failure it targets — *"a run started with uncommitted changes produces numbers
from code that its recorded commit does not contain, which is the staleness D14.4 is about — just
one commit further out, and therefore easy to miss."* **That is a correct diagnosis of a real gap,
arrived at independently.**

## 2. The gap it exposed, in the artifacts

| artifact | `git_commit` | `working_tree_dirty` |
|---|---|---|
| **`crossover_surface.json`** | `5909af66` | **ABSENT** |
| `baselines_re5000_N64_T8.json` | `1c9d032a` | ABSENT |
| `peak_memory.json` | `ddc72073` | ABSENT |
| `taylor_green.json` | `78607f3a` | ABSENT |
| *all 15 artifacts* | — | **ABSENT** |

**Every one of the fifteen artifacts predates the field.** So the hardening is real, correct, and
**not retroactive**: it improves runs that have not happened yet and says nothing about the runs that
produced every number currently in the paper.

**And it could have bitten.** `crossover_surface.json` records `5909af66`, and `solvers/` is
md5-identical between that commit and `HEAD` — but nothing recorded whether the tree was dirty at
launch. D14.4's check (is the recorded commit reachable? is it an ancestor of `main`?) cannot see
uncommitted edits. **This is a staleness one commit further out than the one I have been checking,
and the coder is right that it is easy to miss.**

## 3. The check — and it is a reproduction, not an argument

R27's rule is *provenance beats fingerprint*, so I did not hash the artifact or reason about the
diff. **I ran the recorded code:**

```sh
git archive 5909af66 | tar -x -C /tmp/opencode/repro5909
# no .git directory => an uncommitted modification was not even possible
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python experiments/run_crossover.py --re 5000 --N 64 --dt 0.0005 \
    --force-amplitude 0.2 --horizons 0.1 0.25 0.5 1.0 2.0 \
    --ranks 16 32 --window 0.25 --base-speed 0.5 --cutoff 8 \
    --seed 20260925 --output repro_tstar.json
```

160 s wall clock. The driver printed `t* = 0.649` and `t* = 1.482`.

| quantity | committed artifact | reproduction at `5909af66` | |
|---|---|---|---|
| `t*`, `r=16` | `0.6493281145096707` | `0.6493281145096707` | **EXACT** |
| `t*`, `r=32` | `1.4816252539052939` | `1.4816252539052939` | **EXACT** |
| ratio `@t=0.1/0.25/0.5/1.0/2.0`, `r=16` | 5 values | identical | **EXACT** |
| ratio `@t=0.1/0.25/0.5/1.0/2.0`, `r=32` | 5 values | identical | **EXACT** |
| crossing brackets | `[0.5, 1.0]`, `[1.0, 2.0]` | identical | **EXACT** |

**Every quantity bit-for-bit identical.** A run on uncommitted code would have had to produce
coincidentally identical IEEE doubles across twelve values and two interpolation results.

**So the gap is closed — and closed by a stronger method than the new field would have used. A field
that records `working_tree_dirty: false` converts an unrecorded unknown into a recorded *assertion*.
That is better than nothing and it is not verification: a self-report can be absent, wrong, or
stale. Reproduction is the third thing, and it is the only one that is evidence.**

## 4. The bonus, and it was an assumption I had never tested

The first reproduction attempt ran only to `t=0.25` (500 steps, 11.6 s) to keep the check cheap.
**It reproduced the 16 000-step run's ratios at `t=0.1` and `t=0.25` exactly — `0.00e+00` relative
difference, exact float equality.**

**So the rows are path-independent: a row depends only on the trajectory up to that time, not on the
horizon list or on `final_time`.** I had been relying on this — every "re-run the driver and compare"
claim in this project implicitly assumes it — **and had never tested it.** It holds, and the
mechanism is visible in the code: the moving-window refit loop at `run_crossover.py:226` is
forward-scheduled from `refit_step // 2`, so a shorter run performs exactly the same refits up to its
own end.

**The practical consequence is the point: a 500-step check of the central number costs 12 seconds.**
This class of verification was always affordable. **It was not affordable-looking, because the
artifact records `final_time: 8.0` and the natural reading is that checking it means 16 000 steps.**

## 5. What remains open, stated precisely

- **The other fourteen artifacts still have an unrecorded working-tree state.** That is now a
  *named, bounded* gap rather than an unknown one, and the central artifact — the only one the
  paper's thesis rests on — is verified. I do not think re-running fourteen benchmarks is worth it;
  I think naming the gap is.
- **This says nothing about the `N=128` multipliers** (`1.46→1.99`, `2.45→6.04`), which are my own
  numbers, carry my index shift, and remain unverified. Unchanged.
- **D29's basis is now stronger, not different.** D29 verified the *metric* (my reimplementation of
  `crossover_horizon` recovered every cell). D47 verifies the *artifact* (the recorded code
  reproduces it). Both are needed; they test different things — a reimplementation can be right
  about a metric the artifact never used, and a faithful reproduction says nothing about whether the
  metric is the right one.

## 6. The lesson

**D14.4 asks "is the recorded commit still the code?" A dirty working tree makes that question
unanswerable from the artifact, and every check I have built answers it from the artifact.** The
coder found this independently and fixed the mechanism for future runs. **The part neither of us
had done was to notice that the fix does not apply to the fifteen runs already in the paper — and
that the substitute for a retroactive field is not a field at all, it is re-running the thing.**

**And the general form is worth carrying: a mechanism that improves future runs is not a repair, and
a check that a human performs by hand this cycle is a check the gate should perform every cycle.**
The 12-second reproduction is now a gate item, because the thing that made it look expensive —
`final_time: 8.0` — was never the cost.
