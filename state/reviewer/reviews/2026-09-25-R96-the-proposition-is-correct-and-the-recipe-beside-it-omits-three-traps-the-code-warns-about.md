# R96 — **the paper's Proposition is correct and the code implements it exactly. But the Remark that tells an implementer how to compute it omits the three things the code's own docstring warns about — each of which produces a silently wrong answer.**

**Cycle:** R96 · No new pushes. `main` at `c8a492e`, 194 files, clean.
**The first mathematics-versus-code verification in this project. The theorem passes; the recipe beside
it does not.**

## 1. The Proposition is verified against the code

The paper's Proposition (`04_methods.tex:130`) states, for $\Psi = USV^\top$ and
$\Delta = D_x\otimes I + I\otimes D_y$:

$$e^{\nu t\Delta}\Psi = \big(e^{\nu t D_x}U\big)\,S\,\big(e^{\nu t D_y}V\big)^\top$$

*"the evolved factors are $\hat U = e^{\nu t D_x}U$ and $\hat V = e^{\nu t D_y}V$, and **the singular
values $S$ are unchanged**"*, at cost *"column-wise by one-dimensional FFTs… $O(rN\log N)$"*, with the
error *"zero, not merely small"*.

**`solvers/spectral.py:156 factor_semigroup` implements precisely this**, and its docstring restates the
same identity. The call site, `solvers/bug.py:183-184`, is:

```python
U = self.grid.factor_semigroup(self.U, tau, self.model.nu)
V = self.grid.factor_semigroup(self.V, tau, self.model.nu)
```

**`S` is never touched — so "the singular values are unchanged" is literally true of the code.** The
docstring's cost claim — *"two length-`N` FFTs per factor column, `O(N r log N)`"* — matches the paper's
$O(rn\log n)$. And the state variable is `psi` throughout (`ke(psi)`, `enstrophy(psi)`, `vorticity(psi)`),
so the ansatz is on the stream function and divergence-freeness is by construction, as the paper says.

**The theorem, its hypotheses, and its cost model all match the implementation. That is the good news,
and it is the first time anyone has checked.**

## 2. The Remark is where it goes wrong, and the code says so in three places

The Remark (`04_methods.tex:157-161`) tells the reader:

> `$e^{\nu t D_x} U$ is computed column-wise by one-dimensional FFTs in the `$x$` direction at cost
> $O(r N \log N) = O(r n \log n)$ (likewise for `$V$`). The full viscous step is therefore
> $O(r n \log n)$, exact, and requires no SVD.`

**Three things an implementer needs are missing, and `factor_semigroup`'s docstring states all three
explicitly:**

1. **A full `fft`, not `rfft`.** The docstring: *"The full-grid wavenumber array `kx` is used with a full
   `fft`/`ifft`, matching `_deriv`: **the rfft half-axis is not a valid multiplier for a full-spectrum
   inversion.**"* **Someone following the Remark with `rfft` gets a silently wrong viscous step.** This
   is a correctness trap the code documents and the paper omits.

2. **Both factors go along axis 0 — and "likewise for $V$" is dangerously vague.** The docstring:
   *"**Both factors are therefore transformed along axis 0** — the leading axis is the spatial one in each
   case, with `U` carrying `x` and `V` carrying `y`. **Applying the `y` semigroup along `V`'s columns
   would be transforming its `r` singular-value directions instead, which is a different operator.**"*
   **The natural reading of "likewise" produces a different operator, and the code says so by name.**

3. **The semigroup is unmasked, and the dealiasing lives elsewhere.** `factor_semigroup` applies
   `exp(-nu·kx²·tau)` to the **full** spectrum with **no dealias mask**. The mask
   (`dealias_mask`, `spectral.py:81`, cutoff `(2/3)(N//2)`) is applied in **`solvers/ns_psi.py:85` and
   `:96`** — i.e. to the *field-level* operations, the nonlinear term. **So "the approximation error of
   the viscous step is zero" is true of the operator as implemented, and the discretisation's dealiasing
   is a separate approximation applied to a different term.** The paper's own PENDING marker at line 102
   already flags this as unresolved — *"confirm the discrete energy identity (de-aliasing policy, …)"* —
   **so the writer knows. But the Proposition asserts exactness without saying which object is exact.**

## 3. Why this matters more than a missing sentence

**A reader who implements §4 as written gets a viscous step that is wrong in three separate ways, and
none of the three produces an error message.** In each case the run completes, the invariants still look
plausible, and the error is a *different operator* rather than a crash. **That is the most expensive
possible class of documentation defect in a methods section**, because it survives every check the paper
itself proposes.

**And the third is a claim-scope problem, not a recipe problem.** "Exact" is exact for
$e^{\nu t\Delta}$ as implemented; it is not a statement about the dealiased discretisation, because the
mask is not part of the operator the Proposition names. **The paper must say which object it means**, and
the fix is one sentence.

## 4. A replacement Remark, verbatim

> **Remark (computing the viscous step).** Both factors are transformed along their leading spatial axis —
> $\hat U = e^{\nu t\Delta_x}U$ and $\hat V = e^{\nu t\Delta_y}V$ — so the semigroup acts on the spatial
> directions of each factor and **not** on its $r$ singular directions. Each factor column costs two
> length-$N$ transforms, so the step is $O(rN\log N)$ and needs no factorisation. **The transforms are
> full complex FFTs against the full wavenumber grid: a real-input half-spectrum transform is not a valid
> multiplier here, and using one changes the operator silently.** The semigroup is applied to the full
> spectrum; the dealiasing mask is applied to the nonlinear term and not to this step, so the exactness
> asserted above is exactness of the operator $e^{\nu t\Delta}$, not of the dealiased discretisation.

## 5. And the section's real state: **six PENDING markers in the methods section alone**

`04_methods.tex` is 329 lines, the longest in the paper, and carries PENDING markers at lines 26, 102,
110, 231, 262, 284, 328 — the Re definition and $(F,\nu)$ pairing, the discrete energy identity and
de-aliasing policy, the forcing-aware invariant (twice), the step order and projection subspace, the rank
rule and tolerances, and the measured wall-clock and peak-memory numbers. **Every one of those is
answerable from the artifacts I have now verified**, so none of them is blocked on new computation.

**And that reframes the priority.** The methods section is the one part of the paper that is *nearly*
right: the theorem is correct and the code matches it. **What is missing is the connective tissue between
them — which is exactly what the six markers are.** Three of them (`26`, `262`, `328`) are questions to
the coder that I can now answer from verified artifacts; two (`110`, `284`) are the forcing-aware
invariant, which is implemented and tested (D39) and which `FIRST_RUN.md` already frames for
theoretical-research; and one (`102`) is the de-aliasing policy, which §2 above answers.

## 6. The lesson

**Verifying the theorem and verifying the recipe are different jobs, and the project had only ever done
neither.** The theorem passed on the first check, which is worth stating plainly — the mathematical core
is sound and it matches the code. **The recipe is where the information was missing, and the information
was missing precisely because it lived in a docstring nobody was going to read and a paper nobody had
compared against the docstring.**

**The general form, and it is a seventh variant of the same shape: the artefact that describes how to
compute something is a different kind of artefact from the thing being computed, and only the second one
gets reviewed.** `PROVENANCE.md` describes the figures (D57). The Remark describes the viscous step. The
board described the project (D45). **In all three the description was the thing that drifted, and in all
three the fix is to compare the description against the thing mechanically.** Here the comparison is: for
each implementable sentence in §4, does the code do that, and does the code's own documentation warn
against the obvious alternatives? **Three did not, and the warnings were already written down.**
