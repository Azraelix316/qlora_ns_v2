# R98 — **Invariant I1 is wrong three ways, and the correction is a *stronger* claim. I3 describes a measurement the code never performs.**

**Cycle:** R98 · No new pushes. `main` at `61c4af7`, 196 files, clean.
**Continuing the R96/R97 method: every implementable claim in §4, checked against the code.**

## 1. I1 (exact divergence-freeness) — three errors, and it is resolution-dependent

The paper says:

> *"The velocity is always recovered as $u = (\psi_y, -\psi_x)$ from the (low-rank) stream function, so
> $\nabla\cdot u = 0$ holds **identically at the discrete level**: $\max|\nabla\cdot u| =
> O(\varepsilon_{\mathrm{mach}}) \approx 10^{-14}$ **at every step, for every rank and every Reynolds
> number**. This is a property of the formulation, **not of the numerics**."*

**(a) The number is wrong by three orders of magnitude.** Over every method, rank and Reynolds number
measured, and **restricted to methods that remain finite** — the diverging ones are excluded on purpose,
since their divergence is the *subject* of §5 and not a violation of I1:

| | |
|---|---|
| minimum | `2.26e-14` |
| **maximum** | **`1.0459e-11`** (`pod_dmd_r32`, `baselines_re5000_N64_T8.json`) |
| spread | **462×** |

**`≈10⁻¹⁴` understates the worst finite case by `1046×`.** And a 462× spread means **no single number can
be the bound** — so *"at every step, for every rank and every Reynolds number"* is false as stated, and
falsified by the paper's own artifact.

**(b) "A property of the formulation, not of the numerics" is measurably wrong.** If it were a property of
the formulation it would be resolution-independent. **It is not:**

| method | `N=64` | `N=128` | ratio |
|---|---|---|---|
| `full` | `2.6807e-14` | `6.9122e-14` | **2.58** |
| `dlra` | `2.4689e-14` | `6.5502e-14` | **2.65** |
| `pod` | `2.4594e-14` | `6.3718e-14` | **2.59** |

**Consistent 2.6× across all three methods, at fixed Reynolds number and fixed forcing.** The residual is
the roundoff of the *discrete* spectral derivative pair — the cancellation $\partial_x\partial_y\psi -
\partial_y\partial_x\psi$ is exact in real arithmetic, and its floating-point residue is scaled by the
conditioning of those operators, which grows with the resolved wavenumber. **So the honest attribution is
"a property of the formulation, times the conditioning of the discrete operators" — and the 2.6× is the
measurement that says so.** (Reported as measured: `k_max²` would predict 4× and linear-in-`k_max` 2×, and
it came in at 2.6×.)

**(c) And the correction is a stronger claim, which is the point.** `1.05e-11` is not a defect — it is
**seven orders of magnitude below the reduced solver's own error** (`1.0e-4`, the DLRA's relative L2 at
`N=64`). So:

> **"The velocity is recovered as $u=(\psi_y,-\psi_x)$, so $\nabla\cdot u=0$ identically in exact
> arithmetic. The measured residual never exceeds $\mathbf{1.1\times10^{-11}}$ over every method, rank and
> Reynolds number we ran, which is seven orders of magnitude below the reduced solver's own error
> ($\sim10^{-4}$), and therefore cannot account for it. The residual is the roundoff of the discrete
> spectral derivative pair, and grows as the operators' conditioning does: $2.6\times$ from $N=64$ to
> $N=128$, consistently across methods."**

**That sentence says what the number is, where it comes from, how it scales, and why it is irrelevant to
the method's accuracy. "$\approx10^{-14}$, a property of the formulation" says none of those, and is wrong
on the number.**

## 2. I3 (rank economy) describes a measurement that is not performed

> *"**I3 (rank economy).** The adaptive rank $r(t)$ against the static POD count: **the number of POD
> modes required to resolve 99.9% of the kinetic energy of the reference run.** Static bases cannot follow
> rank growth, so $r(t)\le r_{\mathrm{POD}}$ at late times is the expected (and measured) outcome."*

**Three problems, all checkable against the artifacts:**

1. **The threshold is 99%, not 99.9%.** Every artifact records `energy_fraction: 0.99`.
2. **The quantity is the fluctuations, not the kinetic energy.** The artifacts record
   `rank_basis: "fluctuations"`, and `pod_fit_includes_ic: true`.
3. **And the "POD count" is an input, not a measurement.** `effective_rank` is recorded as **16** in
   `kolmogorov_re{100,1000,5000}_N64.json` and in `kolmogorov_re5000_N128.json` — **constant across three
   Reynolds numbers and two resolutions, and equal to the requested `pod_rank`.** **A quantity that does
   not move with the dynamics is an input, not a measured count.** So *"the number of POD modes required
   to resolve … "* is not something the project measures, and *"is the expected (and measured) outcome"*
   has no measurement behind it.

**Either measure it — one line: record the rank at which the energy fraction is actually reached, per
case, and let it vary — or drop the sentence and report $r_{\mathrm{POD}}=16$ as the rank the static
baselines were *given*.** The second is honest and costs nothing; the first is better and is a cheap run.

## 3. I2 is correct, and it is worth saying so

**I2's forced form checks out.** The paper writes $P_{\mathrm{in}} = -F\langle\psi,\cos y\rangle$ and
$dE/dt = P_{\mathrm{in}} - P_{\mathrm{diss}}$; the code's recorded invariant is
`dE/dt + nu*||omega||^2 - <psi,zeta> + <psi,adv>` with $\zeta = -A\cos y$, so
$-\langle\psi,\zeta\rangle = +A\langle\psi,\cos y\rangle$ — **the same identity, with the same sign, plus
an explicit advection term that D39 established vanishes to roundoff rather than being assumed away.**
The paper's §4.2 and §4.6 are mutually consistent here, and consistent with the code. **That is three
sections checked and one of them right, which is the base rate I should expect from prose that has never
been compared to the code.**

## 4. What I got wrong first, and it is the same family as R97

**My first sweep reported that the paper understated the invariant bound by a factor of $7\times10^{292}$.**
That was **my** error: I took the maximum over *all* methods including the four that diverge to
$7.1\times10^{278}$ — **conflating "the invariant holds" with "the method did not blow up."** Those are
different questions and I answered the wrong one, then nearly reported the answer.

**That is a category error in exactly the family R97 named**, and it has a name here: **a sweep that does
not exclude the cases the claim is about will report the claim's counterexample as its magnitude.** The
fix is mechanical — partition the population first, and print the partition with the number — and it is
the third time in three cycles that the discipline that caught it was *print the number next to the
claim, including the population it was taken over*.

## 5. The lesson

**An invariant stated as a single number, with "identically", "at every", and "not of the numerics", is
making four separate claims: a magnitude, a universality, an attribution, and a mechanism. Three of the
four were wrong, and the one that was right — that the residual is irrelevant to the method's accuracy —
was not stated at all.** The measurement was available the whole time; it was one artifact field, and it
says something more interesting than the sentence it was supposed to support.
