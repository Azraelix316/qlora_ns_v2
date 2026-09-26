# R97 — **§4.2's second expression for $P_{in}$ is wrong by $4\times10^7$, its Reynolds-number definition does not describe the code, and the "no stationary state" framing is a statement about the initial condition, not the flow — because the exact steady state exists in closed form and is $2.5\times10^3$ times larger than where the runs start.**

**Cycle:** R97 · No new pushes. `main` at `71b97b7`, 195 files, clean.
**The first outright mathematical error found in the paper's prose, and a reframing of a claim the
project has been carrying for twenty cycles.**

## 1. Two errors in two sentences of §4.2

`04_methods.tex:98-101` says:

> *"at which (eq.energy) gives $P_{\mathrm{in}} = P_{\mathrm{diss}} = 2\pi^2 F^2/\nu$; for the definition
> $\mathrm{Re} = 2\pi F/\nu^2$ this reads $P_{\mathrm{in}}(\psi_K) = \mathrm{Re}\cdot\nu^2
> \|\cos y\|_2^2/(2\pi)$."*

**The first value is CORRECT and the second is wrong by a factor $3.9\times10^7$.** Checked both ways —
by hand with the 2D norm, and with the code's own operators:

| | value on the code's numbers ($F=0.5$, $\nu=2\times10^{-4}$) | |
|---|---|---|
| $P_{\mathrm{in}} = 2\pi^2F^2/\nu$ | `24674` | **correct** — matches the direct computation $\langle u_K,f\rangle=(F^2/\nu)\|\cos y\|_2^2$ with $\|\cos y\|_2^2=2\pi^2$ in 2D |
| $P_{\mathrm{in}} = \mathrm{Re}\,\nu^2\|\cos y\|_2^2/(2\pi)$ | `6.28e-4` | **wrong**, off by $3.93\times10^7$ |

**It is what you get confusing $F$ with $F^2$.** The two expressions cannot both hold: they agree only
if $F=\nu$.

**And the Reynolds-number definition does not describe the code.** The paper states
$\mathrm{Re}=2\pi F/\nu^2$; on the code's own parameters that is $7.85\times10^7$, **whereas the code runs
`re = 5000` and sets $\nu = 1/\mathrm{Re}$** — Reynolds number is an *input*, not a quantity derived from
$F$ and $\nu$. They differ by $1.6\times10^4$. **This is exactly the PENDING at line 26** (*"confirm the
`Re` definition and the exact $(F,\nu)$ pairing"*) — the writer flagged it and then wrote a definition in
the prose that the code contradicts.

## 2. And the paper is right about $\psi_K$ being a steady state — which is the interesting part

I hand-analysed this, got the sign wrong, and the numbers corrected me: with the code's own operators,
$\psi_K = -(F/\nu)\cos y$ has

- $\|u\cdot\nabla\omega_K\|_\infty = 0$ (advection vanishes: $\omega_K$ depends only on $y$, $u_K$ only on $x$),
- $\nu\|\Delta\omega_K\|_\infty = \|\zeta\|_\infty = 0.5$, **cancelling** ($\zeta = -A\cos y$ per D20.1),
- **vorticity residual exactly `0.000000`.**

**So $\psi_K$ is an exact steady state of the simulated PDE, and it is so for *any* $(F,\nu)$.** The paper's
§4.2 claim is correct.

**And that reframes D20/D24's "no stationary state" — which the project has carried since R20.** The exact
steady state is not merely available, it is in closed form, and the experiments start **2 500 times below
it**:

| | |
|---|---|
| exact steady state's velocity $\|u_K\|_\infty$ | `2500` |
| exact steady state's energy $E_K$ | `6.17e+07` |
| the runs' initial energy (from the artifact) | `22.21` |
| **$E(0)/E_K$** | **`3.6e-07`** |
| `perturbation_velocity_rms` | `1.0` |

**The runs are initialised essentially at rest and then driven up toward a steady state they are $2.5\times10^3$
below in velocity. So "no stationary state is observed" is not a property of the flow — it is a statement
about the initial condition, and it is quantified.** That is a far better position than an unexplained
negative: the reader can see exactly how far from equilibrium the computation starts, and the equilibrium
is something they can verify in one line.

**It also gives D20's bar a mechanism rather than a citation.** D20 bars the name "Kolmogorov flow" by
pointing at the forcing's form. The sharper statement is in the parameterisation: $\psi_K$ coincides with
the **classical** Kolmogorov flow only when $F=\nu$ (where $u_K=(1-\cos y)e_x$ and $\mathrm{Re}=1/\nu$),
**and the code runs $A/\nu = 2500$.** Same family, not the same flow — and now that is a number.

## 3. What I got wrong in this cycle, since it is the third time in three

**I computed $\|\cos y\|_2^2 = \pi$ — a *one-dimensional* norm — and was about to report the paper's
$2\pi^2F^2/\nu$ as wrong by $2\pi$.** In 2D on $[0,2\pi]^2$ it is $2\pi^2$, and the paper is right.

**And my analysis script printed a hard-coded narrative line — "they ADD in the vorticity equation instead
of cancelling, so $\psi_K$ is NOT a steady state" — directly contradicted by the `0.000000` printed above
it.** A printed conclusion that is not computed is the same error as a remembered string: it survives
because it is prose. **The numbers were right and the sentence was wrong, in the same output, and only
because both were printed could I see it.**

**Three cycles, three near-misses of one kind: R84 (a citation contradicted by a second file), R93 (a
multipliers label standing in for a derivation), R97 (a 1-D norm and a hard-coded conclusion). The
discipline that catches all three is the same: compute it, print it next to the claim, and let the number
decide.**

## 4. The lesson

**A paper's prose is where its mathematics is least checked, because the code is checked and the
sentences around the code are not.** R96 verified the Proposition against `solver`. This cycle verified
the two sentences *after* the energy identity and found one wrong by seven orders of magnitude and one that
contradicts the code's own parameterisation. **The Proposition was right; the paragraph after it was not.**
That is not a comment on the writer — it is a comment on where review attention goes, and it went to the
theorem because theorems are checkable and sentences are not.

**And the substantive win is bigger than the errors: the exact steady state exists, it is in closed form,
and the runs start $3.6\times10^{-7}$ of its energy below it.** A paper that says *"we initialise at
$E(0)/E_K = 3.6\times10^{-7}$ and the forced equilibrium $\psi_K = -(F/\nu)\cos y$ is an exact solution, so
the observed absence of stationarity is a property of the initial condition and is quantified"* is
strictly stronger than one that says *"no stationary state was found."*
