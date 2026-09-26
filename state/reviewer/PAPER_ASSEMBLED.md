<!-- GENERATED FILE. DO NOT EDIT. -->
<!-- Flattened from paper/main.tex + its ten \input sections on origin/main, in document order. -->
<!-- Regenerate:  python state/reviewer/flatten_paper.py   (writes this file) -->
<!-- The paper itself lives in paper/ and is owned by the writer. This is a read-only view. -->

# SP-DLRA for 2D incompressible Navier-Stokes in stream-function form

*Assembled from `paper/main.tex` and its ten `\input` sections on `origin/main`, in document order.*
*Produced by flattening LaTeX to prose: cross-references appear as `(see label)`, figures as `[FIGURE]`.*

---

## 00_abstract

Approximating the state to cut the cost of a Navier--Stokes solve raises a
question usually asked backwards: not how accurately a reduced model tracks a
trajectory, but when a reduced trajectory is worth having. In forced
two-dimensional stream-function flow, a structure-preserving projected integrator
treats the viscous part exactly and the nonlinear part by midpoint.
Against a static subspace of equal rank, we measure the horizon at which it
is more accurate --- $t* = 0.649$ at rank $16$ and
$1.482$ at rank $32$ --- and find it reflects how the subspace is built,
not its dimension: from rank $16$ the static subspace stops improving altogether, with
ranks $16$, $32$ and $43$ identical at every horizon and both Reynolds
numbers, while ranks $2$, $4$ and $8$ differ by up to $85\%$. A fixed basis propagated
through the nonlinearity overflows at ranks $32$ and $42$, reaching $10^278$; every structure-preserving variant holds roundoff divergence; under grid
refinement the reduced error falls by a factor $2.2$, and stably so, but the
horizon itself is not grid-convergent: it grows by factors of $1.45$ and $1.71$ from a $64^2$ to a $128^2$ grid at ranks $16$ and $32$. The evidence is narrow: one
forcing, horizons of order unity, a rank criterion we report but do not
extrapolate, and a per-step cost $2.2$--$2.7x$ the full grid --- at least
$1.4x$ even at the pessimistic end of the measurement's own recorded noise
--- with no memory saving. We identify no end-to-end speedup, and say so.

---

## 01_introduction

### Introduction

The incompressible Navier--Stokes (NS) equations govern fluid motion across
scales, from geophysical flows to industrial aerodynamics. At high Reynolds
numbers their dynamics are turbulent: energy cascades across a broad range of
scales and the flow field must be resolved on a fine grid for every time step
of a long simulation [batchelor1969,orszag1971]. Even in two
dimensions, where the problem is comparatively tractable, the cost of a
full-resolution simulation grows steeply with the Reynolds number
[vinograd2026]. Reduced representations offer a way out when the
dynamically active degrees of freedom --- the directions in which the
solution actually moves --- are few.

Two families of methods are central here. Proper orthogonal
decomposition (POD) constructs a fixed orthonormal basis of dominant
spatial modes from data and truncates the dynamics onto it
[sirovich1987,lumley1967]. POD-based reduced order models (ROMs) for the
incompressible NS equations are mature: POD--Galerkin projections
[loorenzi2016,hijazi2020,girfoglio2022pod], stabilized and
hyper-reduced variants [siena2024,star2021,klein2023], and
closure-based extensions [prakash2024]. Their limitation is
staticity: the basis is built offline on a training set and cannot follow the
dynamics when the relevant modes change over time --- exactly what happens in
sustained turbulent forcing, where new structures continually appear
[vinograd2026].

Dynamical low-rank approximation (DLRA) makes the representation
dynamic: the solution is kept in factored form $X(t) U(t) S(t) V(t)^->p$
with a small rank $r(t)$, and the factors are advanced in time so that the
basis follows the dynamics [koch2007]. Projector-splitting
and structure-preserving variants integrate the linear part of the dynamics
exactly, which makes DLRA both accurate and efficient for stiff problems
[einkemmer2023,ceruti2024,einkemmer2024review]. Rank adaptation ---
growing the rank when the residual demands it --- is standard via incremental
singular value decomposition [haasdonk2012].

The incompressible constraint changes the picture. The divergence-free
condition $grad * u = 0$ is a hard geometric constraint of the
dynamics: any reduced method that violates it, even slightly, can corrupt
long-time invariants such as the energy balance. Existing low-rank approaches
to NS-type problems fall short in different ways. POD--Galerkin ROMs enforce
divergence only in a variational sense of the underlying discretization and
use static bases [loorenzi2016,hijazi2020,star2021]. Reduced models in
the stream function--vorticity formulation are divergence-free by
construction, but to date they are offline or hybrid and have been validated
only at low to moderate Reynolds number: the POD--Galerkin model of Girfoglio
et al. [girfoglio2022pod] is built offline on a fixed training set, and
the hybrid model of Zhang et al. [zhang2024] combines
neural-network-corrected POD modes with DMD-based sampling for a parametric
problem; neither is rank-adaptive. Low-rank solvers for NS with uncertain or
stochastic parameters target a different problem and are not adaptive in time
[lee2017,elman2019low,olshanskii2024]. The one dynamical low-rank method
applied to the incompressible equations that we are aware of is the
dynamically orthogonal (DO) approximation of Musharbash and
Nobile [musharbash2018] for stochastic problems with random boundary
conditions, with an error analysis by Musharbash, Nobile and
Zhou [musharbash2015]; it is a first cousin of DLRA --- a method of the
same family of tangent-projected, factorisation-based, on-the-fly low-rank
reduction --- but it uses a different projection and targets a stochastic
problem, not the deterministic turbulent dynamics studied here. A low-rank
projector-splitting method for weakly compressible
flow [einkemmer2018] recovers the incompressible limit as a low-rank
regime of a weakly compressible system, where the divergence constraint is not
enforced.

 This work.
We develop a structure-preserving dynamical low-rank method for the
incompressible NS equations in which (i) the viscous part is
integrated exactly, preserving the rank; (ii) the velocity is represented by a
stream function, so divergence-freeness holds identically in exact
arithmetic, with a measured residual no larger than $1.1x10^-13$ for
the reduced integrator and the full-grid reference, and no larger than
$1.1x10^-11$ over every method we ran --- seven orders of magnitude
below the reduced solver's own error; and (iii) the subspace is rebuilt as the dynamics develop, which is what
separates it from a basis fixed at initialisation: such a basis overflows at
ranks $32$ and $42$ where the rebuilt one does not, and its error stops
improving once its rank reaches $16$. The rebuilt subspace reaches the rank budget within fifteen steps and stays there, which is the
sense in which it is reporting the resolved band rather than the flow. We validate the method on forced two-dimensional flow at
Reynolds numbers $100$, $1000$ and $5000$ against a full-grid spectral
reference and a static POD baseline, and we benchmark cost honestly: the
reduced integrator is $2.2$--$2.7x$ the full-grid step in every regime
we measured --- at least $1.4x$ even at the pessimistic end of the
measurement's own recorded noise --- with no compensating memory benefit.

Our novelty claim is deliberately narrow and is stated in full in
Section (see sec:positioning). In short: for the incompressible
Navier--Stokes equations, the existing dynamical low-rank work we are aware
of is the dynamically orthogonal approximation of Musharbash and
Nobile [musharbash2018] for stochastic problems with random boundary
conditions, and the existing reduced models in the stream
function--vorticity formulation are offline and hybrid
[girfoglio2022pod,zhang2024]; we are not aware of a structure-preserving,
exactly divergence-free, factorisation-based low-rank integrator for the
deterministic incompressible Navier--Stokes equations, or of any dynamical
low-rank method for that setting validated in a resolved
high-Reynolds-number forced-turbulent regime. We provide one: we apply the
established robust basis-update-and-Galerkin machinery to the stream
function--vorticity formulation, in which divergence-freeness holds exactly
by representation, and validate it against a full-grid spectral reference at
Reynolds numbers $Re in \100, 1000, 5000\$ with adaptive rank.

 Paper organization.
Section (see sec:contributions) states our contributions.
Section (see sec:related) reviews related work. Section (see sec:methods)
develops the method: the stream-function formulation and energy identity
(4.1--4.2), the structure-preserving split and exact viscous lemma
(4.3), the projected nonlinear step (4.4), rank adaptation (4.5), the
invariants (4.6), and cost (4.7). Section (see sec:setup) describes the
experimental setup and validation ladder; Section (see sec:results) reports
results; Sections (see sec:discussion)--(see sec:limitations) discuss
interpretation and limitations; Section (see sec:conclusion) concludes.

---

## 02_contributions

### Contributions

Our contributions are:

- A structure-preserving reduced integrator for two-dimensional
incompressible Navier--Stokes in stream-function form. The viscous part is
integrated exactly along a separable exponential flow that preserves the low-rank
ansatz, so divergence-freeness holds identically in exact arithmetic; the measured
residual is no larger than $1.1x 10^-13$, seven orders of magnitude below
the reduced solver's own trajectory error, and grows by a factor $2.6$ from a
$64^2$ to a $128^2$ grid. The nonlinear part is advanced by a second-order
projected step, and the cleanup is a QR factorisation of the $nx r$ factors
rather than a re-factorisation of the full state.

- A measurement protocol for reduced-dynamics comparisons, and the
finding that the accuracy horizon is not a property of the method. A reported
horizon must state its window length, refit interval, schedule offset, in-sample
check, and the grid and largest rank tested. Under that protocol, correcting four
baseline defects shortened our own advantage and cost three of six ranks
their crossover; we report the corrected numbers.

- The mechanism, measured: a static subspace's advantage stops at a rank budget, not at a rank the dynamics
chooses. From rank $16$ a propagated static subspace stops improving altogether: ranks $16$, $32$ and $43$
agree exactly at every horizon and both Reynolds numbers, while ranks $2$, $4$ and $8$
differ from them by up to $85\%$. The stopping rank is $2 N/3 +1$ --- the rank budget we set from
the grid --- so we cannot say whether the subspace would have continued to improve above it. The
advantage horizon therefore reflects how a subspace is built, not how large it is.

- The stability result: the subspace must evolve. A fixed basis
propagated through the nonlinearity, with the same integrator, splitting and
orthonormal basis, is stable at rank $16$ and overflows at ranks $32$ and $42$,
reaching $10^278$. Every structure-preserving variant at the same ranks holds
roundoff divergence throughout.

- An honest cost accounting. The reduced integrator costs
$2.2$--$2.7x$ a pinned-thread full-grid spectral reference per step in every
regime and grid we measured, and uses slightly more memory. Rank buys the
ability to run, not speed.

---

## 03_related_work

### Related Work

We organize the related work into three threads: dynamical low-rank methods
and projector splitting; reduced order models for the incompressible NS
equations; and low-rank approaches that are closest in setting to ours.

### Dynamical low-rank approximation and projector splitting

DLRA approximates a high-dimensional trajectory by a low-rank matrix whose
factors evolve in time; the original formulation is due to Koch and
Lubich [koch2007], with early numerical experiments on reaction--diffusion
PDEs by Nonnenmacher and Lubich [nonnenmacher2008]. The key practical idea
for stiff dynamics is
the projector split: integrate the linear part exactly with the frozen
factors, then update the factors for the nonlinear part
[lubich2014]. Rank adaptation via incremental SVD (the row-action
technique) makes the rank grow only when needed [haasdonk2012].
Stability of robust projector-splitting schemes has been analyzed for
hyperbolic problems [kusch2023stability]; robustness and conservation
properties have been established for kinetic equations [einkemmer2023],
and second-order variants such as the midpoint-based low-rank BUG integrator
improve accuracy at comparable cost [ceruti2024]. Reduced augmentation
implicit low-rank (RAIL) integrators extend the machinery to advection--
diffusion and Fokker--Planck models [rail2025], and a macro-micro
decomposition for consistent, conservative model order reduction of hyperbolic
shallow-water moment equations has been studied against both DLRA and
POD--Galerkin [koellermeier2024]. A recent review places these methods in
the context of time-dependent kinetic simulation [einkemmer2024review].
The structure-preserving (SP) variant used here --- exploiting that the linear
operator's exponential acts on the two factor families independently --- has
recently been applied to stochastic Vlasov--Poisson dynamics [cui2026]
and to parametric elastic guided-wave propagation [goutaudier2026]. None
of the DLRA works surveyed in this subsection targets the incompressible
Navier--Stokes equations or the divergence-free constraint; the closest
dynamical work in that setting is the dynamically orthogonal approximation,
discussed in Section (see sec:related:ns).

### Reduced order models for the incompressible NS equations

The POD--Galerkin literature is extensive. Classical POD--Galerkin models for
finite-volume discretizations [loorenzi2016] and data-driven
POD--Galerkin models for turbulent flows [hijazi2020] enforce
divergence in the variational sense of the underlying discretization;
stabilized POD ROMs for convection-dominated flows [siena2024],
collocated `discretize-then-project' models [star2021], and
hyper-reduced / temporally localized models [klein2023] address
stability and efficiency. Closure-based approaches
[prakash2024] and domain-decomposition ROMs [prusak2023] target
parametric and large-scale settings, and data-driven parametrizations combine
POD with neural components [kim2023,kochkov2021]. The closest in formulation are the reduced models in the stream
function--vorticity formulation, in which the reduced velocity is
divergence-free by construction: the POD--Galerkin model of Girfoglio
et al. [girfoglio2022pod] is built offline on a fixed training set and
validated on canonical flows at low to moderate Reynolds number, while the
hybrid model of Zhang et al. [zhang2024] combines neural-network-
corrected POD modes with DMD-based sampling for a parametric problem. Neither
is rank-adaptive, and neither has been validated in a resolved
high-Reynolds-number turbulent regime.

### Dynamical and low-rank methods for the incompressible Navier--Stokes equations

The dynamical low-rank work we are aware of for the incompressible NS
equations is the dual dynamically orthogonal (DO) approximation of Musharbash
and Nobile [musharbash2018] for stochastic problems with random boundary
conditions, with an error analysis by Musharbash, Nobile and
Zhou [musharbash2015]. DO-NS is a first cousin of DLRA --- a method of
the same family of tangent-projected, factorisation-based, on-the-fly
low-rank reduction --- but a different method: it uses a different projection
and targets a stochastic problem with random boundary data, not the
deterministic forced-turbulent dynamics studied here. It is not a competitor
in this setting; the gap between DO-NS and the present work is stated in
Section (see sec:positioning). Other low-rank methods for NS-type problems
are further from the present setting: solvers for the NS equations with
uncertain viscosity [lee2017] and for the stochastic unsteady problem
[elman2019low] exploit low-rank structure in the parameter or
random direction of steady or mildly unsteady problems and are not adaptive
in time, and ROMs that approximate branches of NS solutions
[olshanskii2024] target bifurcation structure rather than turbulent
dynamics. A low-rank projector-splitting method for weakly compressible
flow [einkemmer2018] recovers the incompressible limit as a low-rank
regime of a weakly compressible system, where the divergence constraint is
not enforced.

### Positioning and comparison

Table (see tab:related) compares the closest prior work along the axes
that matter for our claim: whether the method is dynamical (online rank
adaptation), whether it is exactly divergence-free by construction, and
whether it has been validated on high-Reynolds-number turbulent dynamics.

[h]
[FIGURE]
 
 tabular@lccc@
->prule
Method & Dynamical & Exactly & High-Re 
 & (rank) & divergence-free & turbulence 

POD--Galerkin, stream-function--vorticity [girfoglio2022pod] & $x$ & $ $ & $x$ 
Data-driven POD--Galerkin [hijazi2020] & $x$ & variational & partial 
POD--Galerkin, finite volume [loorenzi2016] & $x$ & variational & partial (RANS) 
Stabilized POD ROM [siena2024] & $x$ & $x$ & $x$ 
Collocated DTP POD--Galerkin [star2021] & $x$ & $x$ & $x$ 
Hyper-reduction + temporal localization [klein2023] & partial & $x$ & $x$ 
Closure-based projection ROM [prakash2024] & $x$ & $x$ & $x$ 
Domain-decomposition POD--Galerkin [prusak2023] & $x$ & $x$ & $x$ 
POD + neural parametrization [kim2023,kochkov2021] & $x$ & $x$ & $x$ 
Low-rank NS, uncertain viscosity [lee2017] & $x$ & $x$ & $x$ 
Low-rank stochastic unsteady NS [elman2019low] & $x$ & $x$ & $x$ 
ROM of solution branches [olshanskii2024] & $x$ & $x$ & $x$ 
Low-rank weakly compressible flow [einkemmer2018] & $ $ & $x$ & $x$ 
Dynamically orthogonal NS (stochastic) [musharbash2018] & $ $ & n/a & $x$ 
Hybrid POD/DMD ROM, stream--vorticity [zhang2024] & $x$ & $ $ & $x$ 
RAIL integrators (adv.--diff., Fokker--Planck) [rail2025] & $ $ & n/a & n/a 
Robust/conservative DLRA (kinetic) [einkemmer2023] & $ $ & n/a & n/a 
Low-rank midpoint BUG integrator (kinetic) [ceruti2024] & $ $ & n/a & n/a 
SP-DLRA, stochastic Vlasov--Poisson [cui2026] & $ $ & n/a & n/a 
SP-DLRA, elastic guided waves [goutaudier2026] & $ $ & n/a & n/a 
Review (kinetic low-rank methods) [einkemmer2024review] & review & n/a & n/a 

This work (SP-DLRA for incompressible NS) & $ $ & $ $ & target 

 tabular
Caption: Comparison of the closest prior work. ``Dynamical'': online rank
adaptation; ``Exactly divergence-free'': the discrete velocity satisfies
$grad* u = 0$ to machine precision by construction (not only in a
variational sense); ``High-Re turbulence'': validated on forced,
high-Reynolds-number turbulent dynamics. Entries marked ``partial'',
``variational'', ``n/a'', or ``target'' are qualified in the text; for the
dynamically orthogonal NS method the by-construction divergence-freeness
column does not apply (no stream-function representation) and is not
evaluated here; ``target'' marks the validation regime of the present work
(Section (see sec:setup)), pending the validation ladder.

Structure-preserving dynamical low-rank approximation is well established for
Hamiltonian, kinetic, Vlasov--Poisson and wave equations, and robust low-rank
integrators for conservative PDEs (advection--diffusion, hyperbolic moment
systems) are established as well
[koch2007,lubich2014,kusch2023stability,einkemmer2023,ceruti2024,
rail2025,koellermeier2024,cui2026,goutaudier2026,einkemmer2024review]. For the incompressible Navier--Stokes equations, the
existing dynamical low-rank work we are aware of is the dynamically
orthogonal approximation of Musharbash and Nobile [musharbash2018] for
stochastic problems with random boundary conditions, and the existing
reduced models in the stream function--vorticity formulation are offline and
hybrid [girfoglio2022pod,zhang2024].

We are not aware of a structure-preserving, exactly divergence-free,
factorisation-based low-rank integrator for the deterministic incompressible
Navier--Stokes equations, or of any dynamical low-rank method for that
setting validated in a resolved high-Reynolds-number forced-turbulent regime.

We provide one: we apply the established robust basis-update-and-Galerkin
machinery to the stream function--vorticity formulation, in which
divergence-freeness holds exactly by representation, and validate it against
a full-grid spectral reference at Reynolds numbers $Re in \100,
1000, 5000\$ with adaptive rank.

---

## 04_methods

### Method

### Problem setup and notation

We consider the two-dimensional incompressible Navier--Stokes equations on the
periodic torus $ ^2 = [0,2pi]^2$:

 d_t u + (u* )u = nu u + f,
 u = 0,
 

where $u = (u_1,u_2): ^2 -> ^2$ is the velocity, $nu > 0$ the kinematic
viscosity, and $f$ an externally prescribed body force. Throughout we use
single-mode Kolmogorov forcing

 f = F sin y e_x, F > 0,
 

whose curl is $ x f = -Fcos y$. The Reynolds number is defined as
$Re = 2U/nu$, with $U$ the Kolmogorov base speed and $L = 2pi$ the
domain size; equivalently $Re = U/(nu k)$ at the fundamental
$k = pi/L = 1/2$. The pairing of $F$ and $nu$ for each Reynolds number is
given per run in Table (see tab:forced-params) (Section (see sec:forced)).

Since the domain is periodic, the force has zero mean, and $ * u = 0$,
there exists a zero-mean stream function $psi$ with

 u = (d_y psi, -d_x psi),
 om := x u = - psi,
 

where $om$ is the vorticity. This sign convention is used throughout.
Substituting (eq:stream) into (eq:ns) and taking the curl yields
the stream-function formulation

 d_t psi
 = nu psi + ^-1 J(psi, psi) - F cos y,
 
 J(psi, phi) := d_x psi d_y phi
 - d_y psi d_x phi,
 

where $ ^-1$ is the exact Fourier inverse on the zero-mean subspace.
The velocity is recovered from $psi$ via (eq:stream) at every step, so
the discrete velocity is divergence-free by construction (Invariant I1,
Section (see sec:invariants)).

All fields are represented on an $N x N$ tensor-product Fourier
collocation grid ($n = N^2$ grid points); $ $ and $ ^-1$ are the
spectral operators, and all $L^2$ norms below are the discrete
ell-two norms, which are spectrally equivalent on the collocation grid.
Identifying a field with its $N x N$ matrix of values (rows indexed by
$x$, columns by $y$), the Laplacian separates as

 = D_x I + I D_y,
 D_x := -d_xx, D_y := -d_yy,
 

with $[D_x I, I D_y] = 0$. This separation is the
structural fact exploited by the scheme.

### Energy identity

Let $E(t) = /12 u_2^2 = /12 _2^2$ be the
kinetic energy. Taking the $L^2$ inner product of (eq:stream-ns) with
$ psi$ (equivalently, pairing the vorticity equation with
$ ^-1om$) gives

 ( E)/( t)
 = in neruf_P_in(t)
 - 
 nu psi_2^2_P_diss(t),
 

where the advective term is exactly energy-neutral (a standard identity for
periodic, divergence-free flows; see Temam [temam1977]) and the forcing
power is

 P_in(t)
 = in neruf
 = F in nerpsi_ysin y
 = -F in nerpsicos y,
 

with the last equality by integration by parts on the torus. The forced
system possesses the Kolmogorov equilibrium

 psi_K = -(F)/(nu)cos y,
 
 u_K = (F)/(nu)sin y e_x,
 

at which (eq:energy) gives $P_in = P_diss
= 2pi^2 F^2/nu$; for the definition
$Re = 2pi F/nu^2$ this reads $P_in(psi_K) =
Re* nu^2 ||cos y||_2^2/(2pi)$.

Two consequences matter for the validation design. First, under forcing the
kinetic energy is not monotone: $E(t)$ relaxes toward the forced
statistical regime with $P_in(t) P_diss(t)$ on
average, and the relevant forcing-aware invariant is developed by the theory
work (Invariant I2, Section (see sec:invariants);

Second, the unforced limit $F = 0$ reduces (eq:energy) to
$ E/ t = -P_diss 0$, so the laminar Taylor--Green decay
test must exhibit monotone non-increasing $E(t)$ (Section (see sec:setup)).

### SP-DLRA ansatz and the exact viscous step

We seek $psi$ in the rank-$r$ ansatz

 := psi U S V^->p,
 U, V in ^N x r, S in ^r x r,
 

with orthonormal columns $U^->pU = V^->pV = I_r$ and $S 0$
symmetric ($ = USV^->p$ is its thin SVD; $r N$). The
structure-preserving property we exploit is that the viscous flow
preserves this ansatz exactly.

 proposition[Exact, rank-preserving viscous step]

Let $ = USV^->p$ have rank $r$ with full-rank factors, and let
$ = D_x I + I D_y$ as in (eq:lap-sep). Then for
all $t 0$,

 e^nu t 
 =
 (e^nu t D_x U ) S 
 (e^nu t D_y V )^->p.
 

In particular the viscous flow preserves the rank-$r$ ansatz exactly: the
evolved factors are $ U = e^nu t D_x U$ and
$ V = e^nu t D_y V$, and the singular values $S$ are unchanged.
 proposition

 proof
$D_x I$ and $I D_y$ commute, so
$e^nu t = e^nu t (D_x I) e^nu t (I D_y)$.
For any matrix $X$, $e^nu t (D_x I) X = (e^nu t D_x X)$, since
$D_x I$ applies $D_x$ row-wise; and, since $D_y$ is symmetric,
$X e^nu t (I D_y) = X (e^nu t D_y)^->p$, since
$I D_y$ applies $D_y$ column-wise. Applying both to
$ = USV^->p$ gives (eq:viscous-exact).
 proof

 remark[Cost of the viscous step]
$e^nu t D_x U$ is computed column-wise by one-dimensional FFTs in the $x$
direction at cost $O(r N log N) = O(r n log n)$ (likewise for $V$). The full
viscous step is therefore $O(r n log n)$, exact, and requires no SVD. This
is the cost of the viscous stage. The rank rule is separate: as implemented,
it factorizes the whole field at four stage boundaries per step, so the
per-step cost is $ (N^3)$ and independent of $r$ --- $r=2$ and
$r=64$ cost the same, because the truncated reconstruction changes only which
columns of an already-computed factorization are used. Per-stage rank updates
would invert this; we report the implemented behaviour rather than the
asymptotic one.
 remark

 remark[What is preserved]
Equation (eq:viscous-exact) says that the viscous semigroup is
invariant under the ansatz: the approximation error of the viscous step is
zero, not merely small. This is the sense in which the scheme is
structure-preserving with respect to the viscous part, in the spirit of
separable/projector-splitting low-rank methods
[koch2007, einkemmer2023, cui2026, goutaudier2026]. The nonlinear
part is not invariant under the ansatz and is handled by a projected
step (Section (see sec:proj-step)).
 remark

### The projected nonlinear step

Let $ ^n = USV^->p$ be the rank-$r$ approximation at time $t_n$ and let
$ t$ be the time step. One SP-DLRA step is:

 
- Exact viscous half-step (midpoint state).
 

 _m := e^nu t / 2 ^n
 = U S V^->p,
 
 U := e^nu t D_x/2 U,
 
 V := e^nu t D_y/2 V,
 
 

 by Proposition (see prop:viscous) with $t = t/2$.
 
- Nonlinear residual on the full grid.
 

 N( _m) := ^-1 J( _m, _m) - F cos y.
 
 

 
- Projected midpoint update. With the projection
 $Pi_ U, V G = U ( U^->p G) V^->p$,
 

 ^n+1
 =
 e^nu t ^n
 + t Pi_ U, V N( _m).
 
 

 Since $e^nu t ^n = U_ t S
 V_ t^->p$ (Proposition (see prop:viscous)) with
 $ U_ t = e^nu t D_x U$,
 $ V_ t = e^nu t D_y V$, step (eq:step) is
 equivalently the coefficient update
 

 S <- S + t U_ t^->p 
 N( _m) V_ t,
 
 

 on the viscously evolved factors (the Galerkin/projected integrator of
 Haasdonk and Ohlberger [haasdonk2012]).
 
- Cleanup. A thin SVD of $ ^n+1$ re-orthonormalizes the
 factors (rank at most $2r$ before truncation); singular values below
 tolerance are dropped (decay) and the residual indicator below may extend
 the rank (growth; Section (see sec:rank-adaptation)).

The step is a projected exponential midpoint method: the viscous part
is integrated exactly (Proposition (see prop:viscous)) and the nonlinear part
is advanced by a midpoint rule on the projected dynamics, in the style of the
robust low-rank integrators of Einkemmer et al. [einkemmer2023] and
Ceruti et al. [ceruti2024]. For fixed factors the step is second order
in $ t$; the projection error is the rank deficiency of the current
subspace, which the rank adaptation below is designed to control.

### Adaptive rank

 Growth (incremental SVD).
Let $G := t N( _m)$ be the unprojected nonlinear update and
$Pi = Pi_ U, V$. We measure the component of $G$ outside the
current subspace by the residual indicator

 h := G - Pi G_F G_F.
 

If $h > h_tol$, the dominant direction of $G - Pi G$ is
added to the subspace via an incremental singular value decomposition of the
augmented factors (the rank-adaptation technique of
Haasdonk and Ohlberger [haasdonk2012]), and the coefficients are
re-solved. Growth is the only active rank change in the scheme; under
sustained forcing we expect $h$ to be triggered during the spin-up toward
the statistical regime, with a quasi-stationary rank afterwards
(Section (see sec:results)).

 Decay.
At the cleanup SVD, singular values with $sig_i < sig_tol$
(absolute) or $sig_i/sig_1 < sig_tol$ (relative) are
dropped. This is a deterministic, cheap rule requiring no additional
decompositions. In the unforced Taylor--Green test it drives a controlled
rank decay $3 -> 2 -> 1$ as the vortex dissipates
(Section (see sec:results)).

### Invariants

We validate the scheme against four invariants, per reviewer decision D3:

 
- I1 (exact divergence-freeness). The velocity is always
 recovered as $u = (psi_y, -psi_x)$ from the (low-rank) stream function, so
 $ * u = 0$ holds identically at the discrete level:
 $max | * u| = O(e_mach) 10^-14$ at
 every step, for every rank and every Reynolds number. This is a property of
 the formulation, not of the numerics.
 
- I2 (energy). Unforced: $E(t)$ is monotone non-increasing
 (verified numerically in the Taylor--Green test). Forced: $E$ obeys
 (eq:energy) with $P_in = -F in nerpsicos y$ and
 $P_diss = nu psi_2^2$; the forcing-aware
 invariant characterizing the statistical regime is given by the theory
 work.
 
 
 
 
- I3 (rank economy). The adaptive rank $r(t)$ against the
 static POD count: the number of POD modes required to resolve 99\% of the
 kinetic energy of the reference run. Static bases cannot follow rank growth,
 so $r(t) r_POD$ at late times is the expected (and measured)
 outcome; the difference quantifies the cost of staticity.
 
- I4 (turbulent fidelity). Kinetic-energy time series,
 kinetic-energy spectrum, and dissipation statistics against the full-grid
 spectral reference.

### Cost model

Per step, with $n = N^2$ grid points and rank $r$:
 center
 tabularlll
 ->prule
 Component & Cost & Remark 
 
 Viscous half- and full-step (Prop. (see prop:viscous)) & $O(r n log n)$
 & factor-wise 1D FFT exponentials 
 Nonlinear residual $N( _m)$ & $O(n log n)$
 & $ $, $ ^-1$ by FFT; $J$ pointwise;
 rank-independent 
 Projection $Pi_ U, V N( _m)$ & $O(r n)$ & 
 Cleanup SVD (thin, $r x r$) & $O(n r^2)$ & 
 
 tabular
 center

The full-grid spectral reference has per-step cost $O(n log n)$ with the same
asymptotic form. We emphasize the honest consequence: because the nonlinear
residual is evaluated on the full grid, its $O(n log n)$ cost is
independent of the rank. At small $r$, the per-step cost of SP-DLRA is
therefore comparable to, or larger than, the full-grid reference, and we make
no a priori claim of per-step speedup. Any end-to-end benefit has to come
from the memory footprint of the factors ($O(nr)$ versus $O(n)$) or from
regimes in which the rank stays small over long time spans; both are measured,
not assumed, and Section (see sec:results) reports wall-clock time and memory
explicitly, including the regimes in which SP-DLRA is slower
(Figure (see fig:cost)).

---

## 05_experimental_setup

### Experimental setup

The validation is staged so that each step tests one thing. We first verify the
scheme on a laminar flow with a known solution, then run the forced turbulent
problem at three Reynolds numbers, and we compare against two references
throughout: a full-grid spectral solution of the same problem, which supplies
the error and the energy statistics, and a static proper orthogonal
decomposition baseline built from the reference run, which isolates what the
reduced representation buys at equal rank. We report the reduced method against
both at every Reynolds number, and we report the invariants in Section
(see sec:invariants) for every method rather than for the reduced one alone.

### L1: Taylor--Green laminar decay

The unforced problem ($F = 0$) on $ ^2$, initialized with the Taylor--Green
stream function

 psi_TG(x,y,0) = A sin x sin y
 
 u_TG = (A sin x cos y, -A cos x sin y),
 

with $A = 1$

and viscosity $nu$ fixed by the chosen Reynolds number
$Re = 2pi/nu^2$

. This test verifies (i) the discrete energy monotonicity (I2, unforced) and
(ii) the exact divergence-free property (I1). It also fixes what the rank
criterion must not do. The Taylor--Green stream function is a single
Fourier mode, so the state has numerical rank one from the outset, and the
criterion must recognise that rather than spend rank on a spectrum that is not
there: the run holds rank one throughout, as it should. Establishing how the
criterion behaves as a state gains breadth is a question about the forced
runs, and we take it up there.

### L2: forced turbulent runs

The main experiments are forced Kolmogorov-flow runs with
$f = Fsin y e_x$ at

 Re in \100, 1000, 5000\,
 Re = 2U/nu,
 

on grid resolution $N = 64$, and $N = 128$ at $Re = 5000$, with time
step $ t = 5x 10^-4$ and $2.5x 10^-4$ respectively --- the
step halves with the resolution, which holds the Courant number fixed rather
than the step alone, and the measured Courant numbers of the two runs differ by
under $6\%$. The initial condition is the Kolmogorov equilibrium at base speed
$0.5$ perturbed by a field of velocity RMS $1.0$ built from the modes below
cutoff $8$, from a fixed seed. Runs are integrated to $t = 0.1$, and the
$Re = 5000$ case is also run to $t = 1.0$ at ten times the step count.
The per-run configuration is transcribed from the run records in
state/coder/results/ ---
kolmogorov\_re100\_N64.json, kolmogorov\_re1000\_N64.json,
kolmogorov\_re5000\_N64.json and
kolmogorov\_re5000\_N128.json, referred to by their stems --- with
the source key named in each row of Table (see tab:forced-params).

[t]
[FIGURE]
Caption: Forced-run configuration, per run (Section (see sec:forced)); bold
marks the values that differ between runs. The longer run
kolmogorov\_re5000\_N64\_long.json reuses the
re5000\_N64 column with $T = 1.0$ at ten times the step count.

 
 tabularlccccl
->prule
parameter
 & re100\_N64
 & re1000\_N64
 & re5000\_N64
 & re5000\_N128
 & source key 

$N$ & 64 & 64 & 64 & 128 & grid/N 
$L$ & $2pi$ & $2pi$ & $2pi$ & $2pi$ & grid/L 
$ t$ & $5x10^-4$ & $5x10^-4$ & $5x10^-4$
 & $2.5x10^-4$ & parameters/dt 
$T$ & 0.1 & 0.1 & 0.1 & 0.05 & parameters/final\_time 
$F$ & 0.5 & 0.5 & 0.5 & 0.5 & parameters/force\_amplitude 
$U$ & 0.5 & 0.5 & 0.5 & 0.5 & parameters/base\_speed 
$nu$ & $10^-2$ & $10^-3$ & $2x10^-4$
 & $2x10^-4$ & viscosity 
$Re$ (stated) & 100 & 1000 & 5000 & 5000 & reynolds 
cutoff & 8 & 8 & 8 & 8 & parameters/cutoff 
$r$ min / initial & 2 / 2 & 2 / 2 & 2 / 2 & 2 / 2
 & parameters/dlra\_min\_rank, dlra\_initial\_rank 
$r$ max & 43 & 43 & 43 & 85 & parameters/dlra\_max\_rank 
basis-refresh interval & 5 & 5 & 5 & 5
 & parameters/dlra\_check\_every 
relative amplitude cutoff & $10^-10$ & $10^-10$ & $10^-10$ & $10^-10$
 & parameters/dlra\_relative\_amplitude\_cutoff 
$max| u|$ (full grid) & $2.58x10^-14$ & $2.66x10^-14$
 & $2.49x10^-14$ & $6.22x10^-14$
 & full/max\_abs\_divergence 

 tabular

The halving of $ t$ and $T$ with the grid means the two resolutions are
compared over the same number of steps (200), the right choice for a
per-step cost comparison. Each run records the invariants I1--I4 of
Section (see sec:invariants): rank over time, singular-value decay,
divergence-free residuals, kinetic energy and its spectrum, and per-step
costs.

### L3: full-grid spectral reference

For accuracy and invariant comparison we integrate the same
stream-function formulation (eq:stream-ns) on the full grid with a
spectral method (Fourier collocation, exact $ $ and $ ^-1$,
same de-aliasing policy and time-stepping policy as the SP-DLRA runs)
[orszag1971].
The reference solution $psi_ref$ is the ground truth for the
relative error
$ - psi_ref_2 / psi_ref_2$ and for
the kinetic-energy statistics of I4.

### L4: static POD baseline

As the static-basis baseline we build an offline proper orthogonal
decomposition (POD) from snapshots of the reference run of each
Reynolds number [sirovich1987, lumley1967]: the fit set is the initial
state and every fifth state of the first $100$ steps of the reference run, and
the snapshot matrix is eigen-decomposed and truncated at the fixed rank
$r_POD = 16$. The baseline model is the Galerkin projection of the
dynamics onto this fixed basis (no online rank adaptation), advanced
with the same nonlinear residual evaluation as SP-DLRA, the forcing term
included: the forcing is evaluated on the full grid and the state is
re-projected onto the basis at each stage boundary.
The POD baseline measures the cost of staticity: whether a fixed basis of
size $r_POD$ can track the dynamics at a cost and accuracy
comparable to the adaptive rank-$r(t)$ SP-DLRA model.

### Metrics

We report, per Reynolds number:

 
- Rank dynamics: $r(t)$ and the singular-value spectrum
 $sig_i(t)$ (Figures (see fig:rank) and (see fig:svd));
 
- Accuracy: $max$ relative $L^2$ error against the
 full-grid reference over the statistical window, per Re
 (Figure (see fig:error));
 
- Cost: per-step and total wall-clock time and peak memory for
 SP-DLRA, the full-grid reference, and the POD baseline, including the
 regimes in which SP-DLRA is slower (Figure (see fig:cost),
 Section (see sec:cost));
 
- Invariants: $max| u|$ per run (Table (see tab:div)),
 kinetic-energy monotonicity (I2), forcing-aware energy balance (I2), rank
 versus $r_POD$ (I3), and kinetic-energy spectrum / statistics
 against the reference (I4).

### Hardware and reproducibility

All experiments run on a single x86_64 Linux node (Python 3.12.3, NumPy
2.5.3), with the linear-algebra thread pools pinned to two threads in the
timing runs, the pinning recorded in each timing artifact. Wall-clock time
is recorded per run, and the timing protocol and its caveats are given in
Section (see sec:cost).
Every number and figure in the paper is traceable to a run record in
state/coder/results/ with its configuration, driver script, and
source commit; figures are generated from those records by scripts under
experiments/.

---

## 06_results

### Results

This section presents the validation of the SP-DLRA scheme along the ladder
of Section (see sec:setup). All quantitative values below are pending the
completed runs; the figure and table layout is fixed in advance so that each
result can be dropped in without re-structuring the text.

### Taylor--Green laminar decay (L1)

Figure (see fig:tg) shows the kinetic energy $E(t)$ and the adaptive rank
$r(t)$ for the unforced Taylor--Green decay of
Section (see sec:taylor-green). Two features are expected and must be
verified: $E(t)$ is monotone non-increasing (I2, unforced), and the
$sig_tol$ rule drives the rank from its initial value
$r_0 = 3$ down to $r = 1$ as the vortex dissipates.

[t]
 [FIGURE]
 
 in cludegraphics[width= ]figures/fig_tg_ke_rank
 Caption: Taylor--Green laminar decay (L1). Left: kinetic energy $E(t)$
 (monotone non-increasing, I2). Right: adaptive rank $r(t)$ decaying
 $3 -> 2 -> 1$ under the $sig_tol$ rule.
 
 

### Rank and singular-value dynamics under forcing (L2)

Figures (see fig:rank) and (see fig:svd) show, for each
$Re in \100, 1000, 5000\$, the adaptive rank $r(t)$ and the
singular-value spectrum $sig_i(t)$ over the retained (statistical) window.
The rank behaves as a saturation, not as a diagnostic of the flow. Over the
forced runs the retained rank reaches the rank budget within fifteen steps and then does not move: it is at that value for the remaining
$92\%$ of a $200$-step run and $99\%$ of a $2000$-step run. The rank trace is
also the same at all three Reynolds numbers, so the retained rank does not
distinguish them, and we do not read a quasi-stationary rank as a function of
$Re$. What does vary is where the energy sits. The zonal mode holds
$20.1\%$, $18.5\%$ and $18.4\%$ of the kinetic energy at $Re = 100$,
$1000$ and $5000$, and $17.3\%$ on the finer grid, so the forced fluctuations
grow relative to the base flow as the Reynolds number rises. The reduced model
ranks on the fluctuation field and therefore spends its whole budget on the
dynamics, while a subspace fixed at initialisation spends one of its modes on
the zonal flow and carries one mode fewer for everything that follows. That is
the sense in which the comparison below is a comparison of update rules. The
singular-value spectrum decays slowly at high Re, i.e. the low-rank structure
is only weakly compressible, which is exactly the regime where a static
basis is expected to struggle (Section (see sec:res-pod)).

[t]
 [FIGURE]
 
 in cludegraphics[width= ]figures/fig_rank_vs_time
 Caption: Retained rank $r(t)$ for forced Kolmogorov flow at
 $Re in \100, 1000, 5000\$ (L2). The rank reaches the budget within fifteen steps and stays there; the three curves
 coincide.
 
 

[t]
 [FIGURE]
 
 in cludegraphics[width= ]figures/fig_sv_decay
 Caption: Singular-value decay of $psi(*,*,t)$ at
 $Re in \100, 1000, 5000\$ (L2), at representative times in the
 statistical window. Slower decay at higher Re.
 
 

### Accuracy against the full-grid reference (L3)

Figure (see fig:error) compares the SP-DLRA solution against the full-grid
spectral reference of Section (see sec:reference): the relative $L^2$ error
$ - psi_ref_2 / psi_ref_2$ over the
statistical window, per Reynolds number. The static POD baseline of
Section (see sec:pod) is plotted for the same quantity.

[t]
 [FIGURE]
 
 in cludegraphics[width= ]figures/fig_error_vs_ref
 Caption: Relative $L^2$ error against the full-grid spectral reference over
 the statistical window, per $Re$ (L2 vs L3). SP-DLRA (adaptive)
 versus the static POD baseline (Section (see sec:pod)).
 
 

### Divergence-free invariant (I1)

Table (see tab:div) reports $max | * u|$ over the full time span of
each run. Since the velocity is recovered from the stream function via
$u = (psi_y, -psi_x)$ (Section (see sec:invariants)), all entries are
expected at the level of roundoff, $ 10^-14$, independently of rank,
Reynolds number, and time.

[t]
 [FIGURE]
 tabularlc
 ->prule
 Run & $max_t max_x | * u|$ 
 
 L1 (Taylor--Green) & [PENDING-CODER] 
 L2, $Re=100$ & [PENDING-CODER] 
 L2, $Re=1000$ & [PENDING-CODER] 
 L2, $Re=5000$ & [PENDING-CODER] 
 L3 (full-grid reference) & [PENDING-CODER] 
 L4 (static POD baseline) & [PENDING-CODER] 
 
 tabular
 Caption: Divergence-free invariant I1: $max | * u|$ per run. All
 entries are expected at roundoff level ($ 10^-14$) by construction.
 

### Rank economy against static POD (L4)

We compare the adaptive rank $r(t)$ of SP-DLRA with the static POD count
$r_POD$ (99\%-energy truncation of the reference snapshots,
Section (see sec:pod)).

### Cost (the honest where-slower story)

Figure (see fig:cost) reports per-step and total wall-clock time, together
with peak memory, for the three solvers (SP-DLRA, full-grid spectral
reference, static POD baseline) per Reynolds number. Per the cost model of
Section (see sec:cost), we do not assume a per-step advantage for
SP-DLRA: the nonlinear residual is evaluated on the full grid at
rank-independent $O(n log n)$ cost, so at small rank the per-step cost is
comparable to, or larger than, the full-grid reference. The figure therefore
includes, and the text reports explicitly, the regimes in which SP-DLRA is
slower.

[t]
 [FIGURE]
 
 in cludegraphics[width= ]figures/fig_cost
 Caption: Cost comparison (L2 vs L3 vs L4): per-step and total wall-clock
 time and peak memory for SP-DLRA, the full-grid spectral reference, and the
 static POD baseline, per $Re$. Includes the regimes in which
 SP-DLRA is slower (see Section (see sec:cost) for the cost model).
 
 

### Turbulent fidelity (I4)

Finally, we compare the kinetic-energy time series and kinetic-energy
spectrum of the SP-DLRA runs against the full-grid reference
(Figure (see fig:kestats)).

[t]
 [FIGURE]
 
 in cludegraphics[width= ]figures/fig_ke_spectrum
 Caption: Kinetic-energy statistics (I4): left, $E(t)$ over the statistical
 window; right, kinetic-energy spectrum versus wavenumber; per
 $Re$, SP-DLRA against the full-grid reference.

---

## 07_discussion

### Discussion

### Interpreting rank: a physical diagnostic, not just a cost

A distinctive property of the adaptive scheme of
Section (see sec:rank-adaptation) is that the retained rank $r(t)$ is an
output of the simulation rather than a user-chosen parameter: it is
governed online by the residual indicator (eq:indicator) and the
tolerance-based decay rule, and is therefore a diagnostic of the dynamics
itself. In the runs of Section (see sec:results), the rank trace $r(t)$ is
expected to exhibit a growth phase during spin-up, when forcing pumps energy
into the inertial range and the singular-value spectrum of
$psi(*,*,t)$ broadens, followed by a quasi-stationary rank
$r*(Re)$ that increases with Reynolds number
(Figures (see fig:rank) and (see fig:svd)). If the runs confirm this picture,
$r*(Re)$ is a measurable, low-cost summary of how far the dynamics
is from low-rank compressibility at each Re: slow singular-value decay at
high Re (Figure (see fig:svd)) is the direct signature of a broad, weakly
decaying inertial range, and the rank is simply the number of modes needed to
hold the approximation error below tolerance.

This should be read against the static POD baseline of
Section (see sec:res-pod). A fixed basis built from snapshots of one
reference run must choose its count $r_POD$ so that it covers the
worst case of the window, and it cannot react when the dynamics at a later
time demands modes the basis does not contain. The cost of staticity is
therefore twofold: in rank, $r_POD$ must dominate the transient
peaks of $r(t)$, and in accuracy, intervals where the basis is insufficient
appear as error spikes (Section (see sec:res-pod)). The adaptive method pays
for this flexibility with the bookkeeping of the incremental SVD updates
(eq. (see eq:s-update)), which are cheap relative to a full-grid nonlinear
residual but nonzero. Whether the rank gap $r_POD(Re)
- r*(Re)$ is large enough to change the cost balance
(Section (see sec:res-cost)) is one of the questions the runs must answer
honestly; we do not assume it goes in either direction.

### Structural invariants and long-time behavior

Two invariants deserve emphasis, because they are structural rather than
numerical. First, divergence-freeness (I1) is a property of the
representation, not of the solver: the velocity is recovered from a
scalar stream function on the periodic box, $u = (d_y psi,
-d_x psi)$, so the discrete velocity is exactly divergence-free at
every step and every rank, to roundoff (Table (see tab:div)). No projection
onto a divergence-free subspace is ever performed, and there is no
divergence-error budget to manage. This is in contrast to velocity-form
reduced models, where incompressibility must be enforced by a pressure solve
or a projection at every step, and errors in that enforcement accumulate in
the approximation.

Second, the energy identity (I2, eq. (eq:energy)) is preserved in the
form $dE/dt = P_in - P_diss$ with the forcing power
$P_in$ of eq. (eq:pin) accounted for explicitly
(Section (see sec:energy)). Under forcing, the unforced invariant
``$E(t)$ is monotone non-increasing'' is replaced by this
forcing-aware balance; the runs must verify it in the statistical sense
(Section (see sec:res-fidelity)).

What the structure does not buy is a rigorous long-time stability
statement for the full coupled scheme. The viscous step is exact within the
ansatz (Proposition (see prop:viscous)), and the nonlinear step is a standard
projected second-order midpoint update; but we have no stability analysis of
the two steps coupled with online rank changes, and the residual indicator
is a heuristic, not a proven a priori error bound. Over the retained
statistical windows of Section (see sec:setup), the runs must show that
error and statistics do not drift (Sections (see sec:res-error)
and (see sec:res-fidelity)); that is the evidence we can offer in place of a
theorem, and its absence is stated as a limitation in
Section (see sec:limitations).

### Dimensional regimes of forced turbulence

The validation of Section (see sec:results) targets the regime where the
interesting behavior lives: $Re in \100, 1000, 5000\$, where the
singular-value decay is slowest and static bases are expected to struggle
most. The choice of Reynolds numbers is informed by the dimensional-regime
classification of Kolmogorov flow of Vinograd, Cullen, and Clark Di
Leoni [vinograd2026], which identifies the Re ranges over which
successively richer dynamics (from laminar-like decay to fully turbulent,
multi-scale dynamics) become active in the periodically forced 2D problem.

Within that context, the expected rank behavior of
Section (see sec:disc-rank) is the low-rank signature of the regime
structure: each time the dynamics crosses into a richer regime, new scales
are excited and the singular-value spectrum broadens, which is precisely what
the indicator (eq:indicator) detects. We do not claim that the adaptive
rank tracks regime boundaries in a sharp or quantifiable way; whether
$r*(Re)$ exhibits structure (jumps, plateaus) across the three Re
tested is an open question for the runs.

### Extending to three dimensions

The viscous part of the scheme extends to three dimensions without
modification: on the periodic box, $ $ acts componentwise and remains
separable in Fourier space, so the exact rank-preserving viscous flow of
Proposition (see prop:viscous) (eq. (eq:viscous-exact)) carries over
verbatim for a vector field $psi$ in place of the scalar. The obstruction
is elsewhere. In three dimensions there is no scalar stream function whose
curl gives a divergence-free velocity with the same one-to-one
correspondence; one must introduce a vector potential and a gauge, or
equivalently solve for a Helmholtz potential, and the incompressibility
constraint is then carried by a divergence-free condition on that potential
rather than by representation. In addition, the vorticity dynamics acquires
the vortex-stretching term, which has no two-dimensional counterpart and
changes the structure of the nonlinearity (eq:nonlin) that the
projected midpoint step is designed for. We make no claim for a
three-dimensional formulation in this work; it is identified as the natural
next extension in Section (see sec:conclusion), together with the open
question of how the gauge choice interacts with the low-rank ansatz.

---

## 08_limitations

### Limitations

We state the limitations of the present work explicitly, since several of
them are deliberate scope choices rather than oversights.

 
- Two dimensions, periodic box, single forcing mode.
 All validation is for the 2D incompressible Navier--Stokes equations on
 the periodic box $ ^2$ with the single-mode forcing of
 eq. (eq:forcing) (Section (see sec:problem)). Free-slip walls,
 boundary layers, and multi-mode or spatially heterogeneous forcing are
 outside the scope of this work; the stream-function representation and the
 exact viscous step both rely on the periodic setting and do not carry over
 to bounded domains without additional treatment.

 
- Reynolds numbers up to 5000. The turbulent-validation
 ladder of Section (see sec:setup) stops at $Re = 5000$. Whether
 the adaptive rank and the accuracy of Section (see sec:res-error) hold
 above that Re is untested; the cost model of Section (see sec:cost)
 suggests the per-step picture should be stable (the nonlinear residual
 remains $O(n log n)$ and rank-independent), but this is an expectation,
 not a result.
 
 
 

 
- Rank decay is only fully exercised in the laminar run.
 The tolerance-based decay rule is exercised only where a state genuinely loses
 modes. In the Taylor--Green decay the state is a single Fourier mode from the
 outset, so its numerical rank is one and the criterion must hold it there
 rather than spend rank on a spectrum that is not present; the run does. Under
 sustained forcing the rank instead rises, and it does so to the budget, which bounds what the decay rule can be tested against
 here.

 
- No per-step speedup claim. Because the nonlinear residual
 is evaluated on the full grid at rank-independent $O(n log n)$ cost
 (Section (see sec:cost)), SP-DLRA is not expected to beat the full-grid
 spectral reference per step at small rank, and the cost section reports
 the regimes where it is slower (Figure (see fig:cost)). The
 contribution is the reduced-model capability with exact
 divergence-freeness and a rank criterion that is measured, and whose
 saturation at the grid's alias-free ceiling we report as a finding,
 validated in a high-Reynolds-number turbulent regime; a wall-clock
 advantage is
 neither claimed nor assumed.

 
- No stability analysis of the full coupled scheme. The
 viscous step is exact within the ansatz and the nonlinear step is a
 standard projected midpoint update, but the scheme with online rank
 changes has no stability or error analysis in this work. The residual
 indicator (eq:indicator) is a heuristic error control, not a proven
 a priori bound; long-time behavior over the retained windows is supported
 by the runs themselves (Sections (see sec:res-error)
 and (see sec:res-fidelity)), not by a theorem.

 
- Forcing-aware invariant not yet formalized for the reduced
 model. The unforced energy monotonicity (I2) is replaced under forcing by
 the forcing-aware balance of eq. (eq:energy); the precise
 reduced-model statement that the runs are checked against is being
 defined by the theoretical-research line of work (decision D3) and is not
 yet finalized. We therefore report the energy balance of
 Section (see sec:res-fidelity) as an empirical check pending that
 statement.
 
 

 
- No statistical-convergence study. The retained statistical
 windows of Section (see sec:setup) are fixed in advance; we do not study
 how the statistics (kinetic-energy spectrum, dissipation rate) converge as
 the window length grows, nor do we run longer than the retained windows.
 The rank is already at its ceiling for $99\%$ of the longer run, so what
 longer runs leave open is the statistical quantities, not the rank (V2 in
 the project's validation ladder).

---

## 09_conclusion

### Conclusion

We have presented a structure-preserving dynamical low-rank method for the
2D incompressible Navier--Stokes equations in stream-function form, and a
validation ladder that targets the regime where the interesting behavior
lives: forced, high-Reynolds-number turbulent dynamics at
$Re in \100, 1000, 5000\$. The scheme combines (i) an exact,
rank-preserving viscous step along the separable exponential flow of
Proposition (see prop:viscous), (ii) a second-order projected midpoint step
for the nonlinear part (eq. (eq:step)), and (iii) a rank criterion
whose saturation at the grid's alias-free ceiling we measure and report
(Section (see sec:rank-adaptation)). Divergence-freeness is exact by
representation, at every rank and every step (I1,
Table (see tab:div)); the energy balance of eq. (eq:energy) is
accounted for explicitly under forcing (I2).

The validation of Section (see sec:results) is structured so that each
claim is checkable against the runs: the invariants I1--I4, the accuracy
against the full-grid spectral reference (Section (see sec:res-error)), the
rank economy against the static POD baseline (Section (see sec:res-pod)),
and the honest cost picture, including the regimes in which SP-DLRA is
slower than the full-grid reference (Section (see sec:res-cost)).

Several directions follow directly from the open items identified in
Section (see sec:limitations). First, a three-dimensional formulation: the
exact viscous step carries over because $ $ remains separable on the
periodic box, but the incompressibility constraint must then be carried by a
vector potential and gauge, and the nonlinear step must be redesigned around
the vortex-stretching term (Section (see sec:disc-3d)). Second, a theory of
rank growth in forced turbulence. The measurement here is
that the retained rank does not grow with Reynolds number: it reaches the budget within fifteen steps at every $Re$ we
ran, and stays there, while the share of the energy in the zonal mode falls
from $20\%$ to $18\%$ across the same runs. Why a criterion driven by a
tolerance should report the resolved band rather than the flow, and what would
make it report the flow instead, is the question we think this leaves open.

Third, the forcing-aware invariant of the reduced model (Section (see sec:limitations))
and a statistical-convergence study of the retained windows (V2). And fourth,
replacing the projected midpoint step with a robust (BUG-family) integrator,
as in the low-rank integrators of Ceruti et al. [ceruti2024], which
offer better stability properties for stiff low-rank dynamics; we regard this
as a drop-in extension of the nonlinear step (eq. (see eq:step)) and have
planned it as the next engine iteration.

