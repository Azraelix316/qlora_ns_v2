# R24 — **Root cause found: `PODGalerkin.fit` reshapes its snapshot matrix wrongly, so the "POD baseline" has never computed POD.** Fixing it makes the baseline *exact* — and reveals that F5 cannot discriminate anything at `t ≤ 0.1`

**Cycle:** R24
**Origin:** R22 left a contradiction between two of my own measurements and refused to
paper over it. Resolving that contradiction found this.
**This is the most consequential single finding in the review, and it invalidates three of
my own reports' framing while settling their measurements.**

---

## 1. The bug

`solvers/pod.py`, `PODGalerkin.fit`:

```python
arr = np.asarray(list(snapshots), dtype=float)          # (n, N, N)
X   = arr.reshape(self.grid.N * self.grid.N, arr.shape[0])   # <-- WRONG
self.mean = np.mean(X, axis=1).reshape(self.grid.N, self.grid.N)
centered  = X - self.mean.reshape(-1, 1)
U, s, _   = np.linalg.svd(centered, full_matrices=False)
self.basis = U[:, :r]
```

The correct construction is **`arr.reshape(n, N*N).T`**. Because `arr` is snapshot-major,
`arr.reshape(N*N, n)` does **not** put snapshot `k`'s pixel `p` at `X[p, k]`. It puts
`X[p, k] = arr.flatten()[n·p + k]` — demonstrated directly:

```
snapshot 0 pixel 0 = 0.0 ;  snapshot 1 pixel 0 = 4096.0
  X_wrong[0,0] = 0     X_wrong[0,1] = 1        <- should be 4096
  X_right[0,0] = 0     X_right[0,1] = 4096
  => X_wrong column k = [1. 3. 5.] instead of [4096. 4097. 4098.]
```

**Consequences, in order.** `self.mean` averages **20 consecutive pixels of a single
snapshot** — a local spatial blur, not a temporal mean. `centered` is therefore garbage.
The SVD factorises a **scrambled** matrix. **`self.basis` is not a POD basis.** Every
number the POD baseline has ever produced is meaningless.

This is the root cause of everything in R20–R23: the flat rank-independent error, the
~1.0 relative L2, the 11.25×/147.5× step-0 figures, R21's 0.044%, and R22's contradiction
(`cos(mu, ic) = −0.000144` — because `mu` was never a snapshot mean, while my `mu_raw` was,
giving `+0.999619`, and the two differ by `‖·‖ = 32.03`).

**The fix is one expression:** `X = arr.reshape(arr.shape[0], -1).T`. R20's rank cap
(`r = min(requested_rank, U.shape[1])` with `U.shape[1] = n`) is a *separate, real* bug and
still needs fixing, but it is second-order next to this.

## 2. What the corrected baseline does

Same committed configuration (N=64, Re=5000, A=0.5, `dt=5e-4`, 20 training snapshots,
200 online steps), buggy reshape versus corrected:

| | step-0 rel L2 | step-0 E | step-0 Z | final E | final Z |
|---|---|---|---|---|---|
| **committed (buggy)** | 1.0802 | 11.247× | 147.53× | 11.422× | 159.05× |
| **corrected, r=10** | **1.36e-14** | 1.0000× | 1.0000× | 1.00000× | 1.00000× |
| **corrected, r=20** | 1.17e-14 | 1.0000× | 1.0000× | 1.00000× | 1.00000× |

**The entire baseline failure was this one reshape.** The 11×/148× step-0 error and the
11.4×/159× final error do not merely shrink — they vanish to machine precision.

## 3. And then the finding that matters for the paper

Corrected baseline, trajectory error against the full-grid reference over the committed
200 steps:

| r | step-0 rel L2 | final rel L2 | final E/ref | final Z/ref |
|---|---|---|---|---|
| 1 | 1.29e-3 | 1.31e-2 | 1.0413 | 1.0641 |
| 2 | 5.94e-5 | 2.49e-3 | 1.0025 | 1.0060 |
| 3 | 3.44e-6 | 5.95e-4 | 1.0008 | 1.0013 |
| 5 | 1.18e-8 | 3.37e-5 | 1.00003 | 1.00004 |
| 10 | 1.36e-14 | 1.07e-8 | 1.00000 | 1.00000 |

**The training window is dominated by 7 significant directions** (singular values
1, 2.5e-2, 8.4e-4, 3.5e-5, 1.6e-6, 5.7e-8, 2.1e-9, 6.5e-11), and **even r=1 reproduces the
trajectory to 1.3%**.

So once the baseline is correct, **F5 cannot discriminate anything at `t ≤ 0.1`: a
one-dimensional static POD already solves the problem.** The problem is not that the
baseline is bad. **The problem is too easy.**

That is the same conclusion R8/R8a/R13 reached from three independent directions — no
stationary state, a secularly growing mean, λ ≈ 0.69/time unit with no decorrelation until
~30 time units — and the baseline bug was **masking it**. Every comparison the project has
run at `t = 0.1` has been between methods on a flow that is, to the precision that matters,
one-dimensional.

## 4. What this retracts, and what it leaves standing

**Retracted.** R21's mechanism (already retracted in R22) and R23's framing of the
Koellermeier-style "lost DOI" work are unaffected, but **R20, R21 and R23 all treated the
baseline's behaviour as a property to be understood rather than a bug to be fixed.** R23
in particular recorded the list as unchanged for a fourth push and treated the baseline as
an open design question; it was a reshape. The "rank cap pays off" observation in R23 — 20
→ 50 snapshots moving the energy ratio from 11.217× to 0.635× — was the *bug's* sensitivity
to matrix shape, not a property of the training window, and **that finding is withdrawn.**

**Standing.** Every *measurement* in R20–R23 was correct; what was wrong was the
interpretation built on them. The step-0 error is the whole error (R21 §1) — true, and now
explained. The error is flat in rank (R21 §2) — true, and now explained. **"POD is 159×
worse" must still be struck**, for a sharper reason than R21 gave: it was never a result
about POD. R20's rank cap is still a real, separate bug.

## 5. Required, and the honest order

1. **Fix the reshape.** One expression. Add a test that the fitted basis reproduces a
   snapshot it was fitted on to machine precision — that test fails today and would have
   caught this at R5.
2. **Fix the rank cap** (R20) — still real, still needed before F5.
3. **Then re-plan F5 entirely.** With a correct baseline that is exact at `t ≤ 0.1`, a
   matched-rank comparison there measures nothing. F5 needs a horizon where the flow is
   genuinely multi-dimensional, which per R13 means **substantially longer than anything
   the project has run** — and that in turn depends on the regime decision (D11.2) and the
   S3 pilot. **F5 is downstream of the regime question, not independent of it.**
4. **Re-run every committed artifact.** The POD baseline column in all of them is void.

## 6. The lesson, which is the uncomfortable one

R20, R21, R22 and R23 spent four cycles investigating a **one-reshape bug** as though it
were a subtle numerical phenomenon, and I constructed three increasingly elaborate
mechanisms — subspace orthogonality, snapshot-mean dominance, window dependence — before
testing the most basic question: *is the fitted object the thing its name says it is?*

I did not ask that once. I assumed the class was a rank-16 POD-Galerkin baseline because
the file was named `PODGalerkin` and the docstring said POD. The check costs one line
(`fit` must reproduce its own training snapshots) and would have caught this in R5.

**That is the seventh proxy in a row, and the most expensive one, because this time the
proxy was the code's own documentation.** Every previous instance was a shortcut in *my*
verification. This one was a shortcut I never thought to question: **taking a class name
and a docstring as evidence of what a class computes.** The general rule, now written where
I will meet it again: **before investigating why a component behaves oddly, confirm that it
computes what it claims to.** I have been asking "is the check right?" for seven cycles and
not "is the thing being checked real?"
