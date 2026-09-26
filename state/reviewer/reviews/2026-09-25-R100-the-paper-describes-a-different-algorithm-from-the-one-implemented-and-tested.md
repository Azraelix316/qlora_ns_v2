# R100 — **§4's step 4 describes a different algorithm from the one implemented, and the test suite asserts the implemented one. The paper describes the version that costs `Θ(N³)` per step.**

**Cycle:** R100 · No new pushes. `main` at `b70be75`, 198 files, clean.
**The fifth defect in §4, and the one with the sharpest consequence: the paper's algorithm and the
implementation differ, and the project's own test suite says so.**

## 1. What the paper says, and what the code does

**Paper, `04_methods.tex:218-221`, step 4 ("Cleanup"):**

> *"A thin SVD of $\Psi^{n+1}$ **re-orthonormalizes the factors** (rank at most $2r$ before truncation);
> singular values below tolerance are dropped (decay)…"*

**Code, `solvers/bug.py:172-188`, `_diffuse_factors`:**

> *"Orthonormality is then restored by **QR of the `N × r` factors — `O(N r²)`, not a factorization** —
> with `R_u S R_vᵀ` folded into the small matrix. **Reusing `initialize`'s full SVD here instead would have
> put a `Θ(N³)` factorization back in every step and defeated the entire point of the port.**"*

**Three differences, and they are not cosmetic:**

| | paper, step 4 | code |
|---|---|---|
| re-orthonormalisation | **thin SVD of $\Psi^{n+1}$** | **QR of the `n × r` factors**, with `R_u S R_vᵀ` folded in |
| factorization in the step | of the `n × r` state | **of the small `r × r` matrix `S`** (`bug.py:193`, in `_truncate`) |
| cost of that operation | `O(n r²)` | `O(n r²)` (QR) **+ `O(r³)`** (small SVD) |

**The rank-`2r` claim is correct** — the projected increment lies in span$\{\hat U_{\Delta t}\}\times$span$\{\hat V_{\Delta t}\}$, so the sum has rank at most `2r`. That part is fine. **The algorithm that produces the orthonormal factors is not the one described.**

## 2. And the test suite already asserts the code's version, not the paper's

`experiments/test_engine.py:565`, `test_bug_never_factorizes_the_full_state_inside_a_step`:

> *"The port's entire purpose is a structural one, so it is asserted. A timing claim cannot distinguish a
> BUG step from a projected one on a shared node, but **the *shape* of the factorization can**: the only
> factorization allowed after `initialize` is of the small augmented S-matrix, of dimension at most `4r`
> (or `3r` for the Remark-1 variant)."*

**So the project has a test whose stated purpose is to assert precisely the property the paper's step 4
violates.** The code is right, the test is right, and **the paper is the only artefact in the project that
describes the expensive algorithm.** That is an unusual and clean configuration: the defect is isolated,
and the fix is a paragraph.

## 3. And it propagates into the cost model, which is where D61.5 needs correcting

**D61.5 said the cleanup-SVD row's cost `O(n r²)` is right and its label *"thin, `r × r`"* is wrong. That
needs a second sentence: the cost is right *for the algorithm the paper describes*, and the paper's
algorithm is not the one implemented.**

- For the **paper's** thin SVD of an `n × r` matrix: `O(n r²)` ✓
- For the **code's** small SVD of `S`: `O(r³)` — negligible at small `r`

**The number survives by a different route, which is why nobody caught it: the implemented step also costs
`O(n r²)`, but through the QR rather than through an SVD.** So the cost model's *figure* is right and its
*attribution* is wrong — and the Remark on the viscous step (D58) correctly credits the `O(N r log N)`
factor semigroup, which is the part that actually matters for the headline cost.

**Nothing in the cost table is arithmetically wrong. What is wrong is the algorithm the table is a table
of.**

## 4. Why this one matters more than the other four

**The other §4 defects are wrong sentences about a correct algorithm. This one is a description of a
different algorithm — one the project deliberately rejected, documented the reason for rejecting, and
wrote a test to prevent.**

**And the failure mode is specific and expensive: a reader who implements the paper's step 4 gets a
`Θ(N³)` factorization in every step** — at `N=128`, `n = 16384`, `Θ(n^{3/2})`-class work per step that the
code never does. **Their reproduction would be slower than the full-grid reference by an amount the paper
never claims and could not explain**, because the paper's own cost table says the step is `O(n r²)`.

**So the paper contains a self-inconsistency that a careful reader can see without running anything: step 4
describes a thin SVD of the state, and the cost table charges `O(n r²)` for it, while the implementation
and its test both say no such factorization happens.** Three artefacts, three positions, and the paper is
the odd one out.

## 5. Two things that are right here, and they are worth keeping

- **The rank-`2r` bound is correct.** The projected increment lies in
  span$\{\hat U_{\Delta t}\}\times$span$\{\hat V_{\Delta t}\}$, so $\Psi^{n+1}$ has rank at most `2r` before
  truncation.
- **The projection subspace is the midpoint-evolved factors, as the paper says** — which answers the
  PENDING at line 231. `eq:step` projects with $\Pi_{\hat U,\hat V}$ built from
  $\hat U = e^{\nu\Delta t D_x/2}U$, not the frozen $U$, and the code's `_diffuse_factors` evolves the
  factors *before* the augmented step uses them. **The PENDING's first question is answered: midpoint, as
  written.**
- **"For fixed factors the step is second order in $\Delta t$" is tested** —
  `test_reduced_path_is_second_order_in_dt` and `test_bug_is_second_order` both exist and pass.

**So of the PENDING at line 231 — "confirm the exact step order and the projection subspace" — one half is
confirmed correct as written, and the other half (the cleanup) is the defect.**

## 6. The lesson, and the correction to my own R99

**D61.5 caught a label attached to a correct cost. R100 finds that the cost was correct *by coincidence*,
attached to an algorithm that is not implemented.** The distinction matters and I did not make it: a number
can be right for the wrong reason, and the way to tell is to ask **which operation the number is the cost
of** — not whether the number matches.

**And the general form, which is the sharpest version of the §4 pattern yet: the paper describes an
algorithm, the code implements a different one, and a test asserts the code's. Three artefacts, three
positions, and the outlier is the one nobody checked against the others.** That is not a prose problem. It
is a *consistency* problem, and it is the kind that survives every check aimed at a single artefact —
because each of the three is individually defensible and only their disagreement is informative.
