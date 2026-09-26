# R99 — **the §4 cost model offers two routes to an end-to-end benefit, and the paper's own measurements have closed both. Neither §6 nor §8 says so. Plus a table row that names the wrong operand while quoting the cost of the right one.**

**Cycle:** R99 · No new pushes. `main` at `ae9eb09`, 197 files, clean.
**The fourth defect found in §4 alone, and the one with the widest blast radius: it is a claim the
paper's own §6 will contradict.**

## 1. The cost model's two routes, and both are closed

`04_methods.tex:320-327` says:

> *"because the nonlinear residual is evaluated on the full grid, its $O(n\log n)$ cost is independent of
> the rank. At small $r$, the per-step cost of SP-DLRA is therefore comparable to, or larger than, the
> full-grid reference, and **we make no a priori claim of per-step speedup. Any end-to-end benefit has to
> come from the memory footprint of the factors ($O(nr)$ versus $O(n)$) or from regimes in which the rank
> stays small over long time spans; both are measured, not assumed**, and Section~\ref{sec:results} reports
> wall-clock time and memory explicitly…"*

**Route 1 — memory — is closed by the measurement, and the sign is the wrong way round:**

| | overhead vs full grid |
|---|---|
| `N=64`, projected | **`+2.24 MiB`** |
| `N=64`, BUG | `+1.96 MiB` |
| `N=128`, projected | **`+4.27 MiB`** |
| `N=128`, BUG | `+3.59 MiB` |

**Every overhead is positive: the reduced integrator uses *more* memory, not less** (D19.1, re-derived in
D52.6 at the new noise floor). The $O(nr)$ versus $O(n)$ argument is about the **factors**; the state is
a full $n$-field *plus* its factors *plus* the factorisation workspace, and the workspace dominates. **So
the only route §4 offers to a benefit is a route the paper's own §6 will report as a deficit.**

**Route 2 — long time spans — is barred by D32.2.** The only horizon beyond the initial transient is
`nsteps: 200`. *"Regimes in which the rank stays small over long time spans"* is precisely the claim
`rank_growth_sweep.json` cannot support.

**And nothing retracts either.** I grepped all three sections: `08_limitations.tex` contains **no memory
or footprint text at all**; `04_methods.tex:322` has the correct *"no a priori claim of per-step
speedup"*; `06_results.tex` still carries the `[PENDING-CODER]` marker for the wall-clock and memory
numbers. **So the paper currently promises a benefit in §4 and does not withdraw it in §6 or §8.**

## 2. And the fix makes the paper stronger, not weaker

The sentence *"both are measured, not assumed"* is an invitation to a reviewer to check. **Checked, both
come back negative.** The strong position is to say so first:

> **"Because the nonlinear residual is evaluated on the full grid, its $O(n\log n)$ cost is independent of
> the rank, and we make no claim of per-step speedup: SP-DLRA is measured at `2.1–2.7×` the full-grid step.
> Nor is there a compensating memory benefit: peak RSS is `2.2 MiB` (`N=64`) to `4.3 MiB` (`N=128`) *above*
> the full-grid step, because the state is a full field plus its factors plus the factorisation
> workspace. We therefore identify no end-to-end benefit in the regimes we have measured, and the case for
> the method rests on its structural guarantees and its accuracy, not on efficiency. Establishing a regime
> where the rank stays small over a long span would require evidence beyond the `200`-step horizons used
> here, and we do not have it."**

**That is a stronger paper than one that hedges with a possible benefit its own §6 will contradict.** A
reviewer who reads §4's memory route and then §6's memory numbers concludes either that the paper is not
careful or that the numbers were selected — and the fix is one paragraph.

## 3. A table row that names the wrong operand and quotes the cost of the right one

| Component | Cost | Remark |
|---|---|---|
| Cleanup SVD | `$O(n r^2)$` | *"thin, $r \times r$"* |

**The cost is right and the label is wrong.** `solvers/bug.py:134` is
`U, s, Vt = np.linalg.svd(centered, full_matrices=False)`, where `centered` is the **`n × r`** centred
field — a thin SVD of an `n × r` matrix, which is what `O(n r²)` is the cost of. **The `r × r` object is
the *output* singular-value diagonal `S`, and the second SVD at `bug.py:193`
(`np.linalg.svd(S, full_matrices=False)`) is of that `r × r` matrix at `O(r³)`, which is negligible at
small $r$ and is a different operation from the one the cost is quoting.**

**So the row names the operand it does not factorise and quotes the cost of the one it does.** That is D36
— a name standing in for a quantity — and it survived because the number is correct. **The rest of the
table is right**: the viscous row matches `factor_semigroup`'s `O(N r log N)` (D58), the nonlinear row's
*rank-independent* claim is exactly what the code does, and *"we make no a priori claim of per-step
speedup"* is among the best sentences in the draft. **One label in four rows.**

## 4. The pattern, and it is now unmistakable

**Four defects found in §4 alone across R96–R99, and not one of them is in the Proposition:**

| cycle | what | kind |
|---|---|---|
| R96 | the viscous-step Remark omits three things the code's docstring warns about | recipe omissions |
| R97 | §4.2's second $P_{\mathrm{in}}$ expression wrong by $3.9\times10^7$; the Re definition contradicts the code | wrong numbers |
| R98 | I1 wrong three ways and resolution-dependent; I3 describes a measurement never performed | wrong claims about measurements |
| R99 | the cost model's two benefit routes are closed by the paper's own measurements; one row names the wrong operand | claim contradicted by the paper's own §6 |

**The Proposition — the one piece of §4 that is a theorem — is correct and matches the code exactly. Every
defect is in the prose around it.** R97 named the mechanism: *review attention goes to the theorem because
theorems are checkable and sentences are not.* **Four cycles of evidence for it, all in one section.**

**And the aggregate is a measurement, not an anecdote: of the implementable claims in §4 that I have now
checked against the code, the theorem is right, one remark is right, one invariant is right, and four
blocks are wrong.** The section is not bad — it is *unverified*, which is a different diagnosis and has a
different remedy: not rewriting, but checking.

## 5. The lesson

**A claim that the paper promises to measure is the most dangerous kind, because the promise transfers
responsibility from the sentence to a table somewhere else — and the table may not agree.** §4 offers two
routes to a benefit and says *"both are measured, not assumed."* That sentence is an invitation, and the
measurements came back negative on both. **Declining to make the promise is worth more than keeping it and
hoping the table is not read.**
