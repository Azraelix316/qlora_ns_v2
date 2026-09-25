# R21 — The committed POD baseline's failure is **fully accounted for**: it is a step-0 artefact, and the initial condition is nearly orthogonal to the training subspace

**Cycle:** R21
**Scope:** closes the item R20 explicitly left open — "the committed baseline's 11.4×/159×
failure remains unexplained". It is now explained, with a mechanism, a measurement, and a
consequence for V1 and F5.

---

## 1. The failure is entirely at initialisation

Committed configuration reproduced exactly: N=64, Re=5000, **A=0.5**, `dt=5e-4`, 200
steps, `pod_rank=16`, 20 training snapshots from `t ∈ (0, 0.05]`, DLRA initial rank 2,
tolerance 1e-10. IC energy 22.2067, enstrophy 1.3376e3, **numerical rank 17**.

| | rel L2 at t=0 | E ratio at t=0 | Z ratio at t=0 | E ratio at t=0.1 | Z ratio at t=0.1 |
|---|---|---|---|---|---|
| **POD (r=16)** | **1.0802** | **11.247×** | **147.53×** | 11.422× | 159.05× |
| **DLRA (r=2)** | **0.3190** | **0.351×** | **0.245×** | 0.366× | 0.250× |
| full-grid reference | — | 1.000× | 1.000× | 1.000× | 1.000× |

**The step-0 error is the whole error.** 11.247× at initialisation becomes 11.422× after
200 steps; 147.53× becomes 159.05×. The dynamics contribute almost nothing on top. This
is not a baseline that degrades over a run — it is a baseline that starts in the wrong
place and stays there.

## 2. It is not a rank problem, and the tell is the flatness

Projecting the IC at increasing rank, committed basis:

| r | 5 | 10 | 16 | 17 | 20 | 32 | 43 |
|---|---|---|---|---|---|---|---|
| rel L2 | 1.1922 | 1.1205 | 1.0802 | 1.0799 | **1.0793** | **1.0793** | **1.0793** |
| E ratio | 27.12 | 16.58 | 11.25 | 11.20 | **11.22** | **11.22** | **11.22** |

**Flat from r=20 to r=43**, on a field whose numerical rank is **17**. A rank-17 field
projected onto a basis that *contains* its directions is exact at r=17. This is not, so the
basis does not contain them — and the error's *independence of rank* says so immediately.
This is the same diagnostic R20 used to find the rank cap, and it is worth stating as a
general rule: **a rank-independent error is not a rank error.**

## 3. The mechanism: the IC is nearly orthogonal to the training subspace

Direct measurement: the fraction of the IC's mean-subtracted L2 norm lying in the span of
the 20 early-snapshot fluctuation directions is

**0.000442 — 0.044%.**

The reconstruction is therefore dominated not by the fitted directions but by the
**snapshot mean**, which is a field unrelated to the IC. That reconciles the two numbers
that otherwise look inconsistent: the U-span overlap is 0.044% of the norm, while the
projected output has ~40% of the IC's amplitude (since `rel L2 = 1.0793` implies
`||P(ic)||/||ic|| = √(1.0793²−1) ≈ 0.41` **if** `P(ic) ⊥ ic`). The output is a nearly
orthogonal field built mostly from the snapshot mean — hence `rel L2 > 1` and an energy
ratio of 11×.

**Why the subspace misses the IC.** Over `t ∈ (0, 0.05]` at Re=5000 the state reorganises
fast enough that the initial condition's directions are essentially absent from the span
of everything that follows. R8/R8a established that this regime is mean-dominated and
still reorganising; this is the quantitative form of that for the baseline.

## 4. The obvious remedy does **not** work, and that matters

Including the IC as the first training snapshot — the standard POD-ROM protocol, and the
first thing one would try — **does not fix it**:

| r | 5 | 10 | 16 | 20 | 32 | 43 |
|---|---|---|---|---|---|---|
| rel L2 (IC included) | 1.0872 | 1.0036 | 1.0013 | 1.0012 | 1.0004 | **1.0004** |

Still ~1.0. Two reasons, and the second is R20's bug compounding: (i) `fit` centres by the
snapshot mean, so a single IC among 21 columns contributes `1/21` of the variance and is
not prioritised; (ii) with 21 snapshots, R20's rank cap clamps every request to **21**, so
r=43 never happens.

**So the baseline cannot be repaired by a protocol tweak alone.** It needs a training window
that genuinely spans the evaluation period — and, given the subspace rotation measured
above, that is a substantive design question, not a one-line change.

## 5. What this means, and what it does not

**V1 is the critical path, now with a mechanism.** The current protocol has each reduced
method start from *its own* projection of the IC — DLRA from rank 2 (0.319 rel L2), POD from
rank 16 (1.080 rel L2) — and the reported errors are dominated by that mismatch rather
than by anything the methods do. The correct P0 protocol is: **project the IC once, start
every reduced method from that same projected state, and compare trajectories.** Until
that is done, no method-to-method number in this project means what it appears to mean,
which is the same conclusion V1 reached from the hardcoded step-0 error — now with the
magnitude and mechanism measured.

**F5 cannot be run on this baseline**, and the reason is not the rank cap alone. Even after
the cap is fixed, a basis whose training window excludes (and is nearly orthogonal to) the
evaluation state cannot support a matched-rank comparison. Both must be fixed, and the
training-window question is the harder one.

**What I am not claiming.** POD is not a bad method, and this experiment does not show
that. It shows that **the baseline as configured is not a valid baseline** — it begins
11× off in energy and 148× off in enstrophy, before any dynamics. The "POD is 159× worse"
phrasing that appears in R5m and in the gate spec should be struck: the correct statement
is that **the POD baseline's initialisation is invalid**, which is a defect in the
protocol and not a result about the method.

**A useful side finding for the writer.** The DLRA's own step-0 error is 0.319 with a
0.351× energy ratio — also an initialisation artefact, and the same one. Once V1 is fixed
both numbers change, and the honest comparison is between two methods started from an
identical state.
