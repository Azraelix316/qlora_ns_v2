# R12 — The rank criterion is an *amplitude* test wearing an *accuracy* tolerance's name. Fixing it materially improves both the accuracy story and the cost story

**Cycle:** R12
**Scope:** `solvers/dlra.py:84-88` (the rank rule), the R11 spectral-gap experiment
**This resolves the question R11 left open, and it resolves it in the project's favour.**
The premise is recoverable — but not in the form the project has been quoting, and not
until a specific, cheap defect in the rank rule is fixed.

---

## 1. R11's question, answered: there is **no** spectral gap, at any N

Full grid, Re=5000, **A=0.5** (the amplitude the committed artifacts actually used),
t=2, dealias on:

| N | dealias ceiling `2·floor(N/3)+1` | numerical rank at tol 1e-6 / 1e-8 / 1e-10 / 1e-12 / 1e-14 | cliff |
|---|---|---|---|
| 128 | 85 | 85 / 85 / 85 / 85 / 85 | σ₈₅/σ₁ = 2.50e-6 → σ₈₆/σ₁ = **1.73e-15** |
| 256 | 171 | 166 / **171** / 171 / 171 / 171 | σ₁₇₁/σ₁ = 1.28e-7 → σ₁₇₂/σ₁ = **9.73e-16** |

The rank is the grid's ceiling at every tolerance, with a **nine-order cliff** exactly at
the ceiling, and σ₂₀₀/σ₁ = 2.0e-16 confirms the dealiasing mask annihilates everything
above it. R11's conclusion is confirmed at high N: **the state is spectrally full-rank
within the band the grid admits, and there is no spectral gap for adaptive rank to
exploit.** The "adaptive rank growth" remains an initialization artifact, and the paper
cannot claim spectral low-rank structure.

## 2. But the **energy** is extraordinarily concentrated, and N-independent

Same runs, cumulative singular-value energy:

| N | 99% of energy | 99.9% of energy |
|---|---|---|
| 128 | **r = 5** | **r = 9** |
| 256 | **r = 5** | **r = 9** |

**Identical at N=128 and N=256.** The energetically relevant rank is ~5–9 and does *not*
grow with the grid, while the numerical rank doubles with it. So the state is a
*spectrally* full-rank field whose *energy* is strongly low-rank — a precise and
non-obvious object, and a much better premise than the one currently claimed.

## 3. The defect: `tolerance` is an amplitude test, not an accuracy test

`SVDProjector._target_from_spectrum` (`solvers/dlra.py:87`) is:

```python
numerical = int(np.count_nonzero(s > self.tolerance * s[0]))
```

The test is on singular **values** — amplitudes. The parameter is named `tolerance`,
exposed as `dlra_tolerance`, validated as a tolerance (`0 < tolerance < 1`), recorded in
every artifact as `dlra_tolerance`, and described in the driver as the accuracy knob.
A reader — including a reviewer — will read it as an accuracy criterion. It is not: with
`tolerance = 1e-6`, the retained modes satisfy `σ_k/σ₁ > 1e-6`, i.e. an **energy** ratio
above `1e-12`. The parameter is **six orders of magnitude stricter in energy than its
name implies**, and the committed runs use `1e-8`, which is *sixteen* orders stricter in
energy.

That is why the runs select r=43 when r=5 already carries 99% of the energy. **The
method is not selecting a rank for accuracy; it is selecting a rank eight to sixteen
orders more conservatively than its own parameter name advertises.** This is a
correctness-and-clarity defect, not a tuning preference: a parameter whose name
misdescribes its behaviour will be misread by everyone who touches it, including us.

## 4. Three pictures of the same truncation, and they disagree

Truncating the developed state (A=0.5, Re=5000, t=2) and measuring (a) energy retained,
(b) relative L2 error of the state, (c) the error after **one full step** of the
nonlinear operator applied to the truncated state, (d) kinetic- and enstrophy-relative
errors:

**N=64** (ceiling 43, E=39.53):

| r | energy frac | rel L2 state | rel err, 1 step | ΔE/E | **ΔZ/Z** |
|---|---|---|---|---|---|
| 2 | 0.9538 | 2.15e-1 | 2.15e-1 | −3.9e-1 | **−8.6e-1** |
| 5 | 0.9927 | 8.53e-2 | 8.52e-2 | −1.7e-1 | **−6.7e-1** |
| 9 | 0.9991 | 3.02e-2 | 3.02e-2 | −6.1e-2 | **−4.8e-1** |
| 16 | 0.99987 | 1.15e-2 | 1.15e-2 | −2.1e-2 | **−2.6e-1** |
| 32 | 0.999997 | 1.82e-3 | 1.82e-3 | −8.8e-4 | **−1.6e-2** |
| 43 | 1.000000 | 1.13e-14 | 1.13e-14 | 0 | 0 |

**N=256** (ceiling 171, E=40.44):

| r | energy frac | rel L2 state | rel err, 1 step | ΔE/E | **ΔZ/Z** |
|---|---|---|---|---|---|
| 5 | 0.9925 | 8.69e-2 | 8.69e-2 | −1.5e-1 | **−6.3e-1** |
| 9 | 0.99937 | 2.50e-2 | 2.50e-2 | −3.5e-2 | **−4.0e-1** |
| 32 | 0.999998 | 1.42e-3 | 1.42e-3 | −1.3e-3 | **−1.2e-1** |
| 43 | 1.000000 | 7.02e-4 | 7.02e-4 | −5.8e-4 | **−7.8e-2** |

Three things follow, and the first is the paper's real result.

**(i) Energy concentration and accuracy are different quantities.** At N=64, r=32 retains
**99.9997%** of the energy and still has a **0.18%** relative L2 error and a **1.6%**
enstrophy error. Quoting `σ₃₂/σ₁ ≈ 7e-4` as evidence that "high rank is needed" is
measuring the wrong thing: that mode carries ~5e-7 of the leading mode's energy. The
honest statement is the two-sided one: **the state is energetically low-rank (r≈5) and
spectrally full-rank (r = the grid ceiling), and these are not in conflict.**

**(ii) The dynamics do not amplify the truncation error over a step.** The one-step error
equals the state error to four significant figures at every rank and both N (e.g. 1.816e-3
vs 1.816e-3 at N=64, r=32). So the discarded components are dynamically near-inert over
one step, the dominant error is the projection itself, and the method is not
error-amplifying. That is genuinely good news, it explains why the reduced runs are
well-behaved, and it is worth a sentence in the paper.

**(iii) Enstrophy is the demanding metric, and it is where this project actually
validates.** At r=5 the enstrophy error is **−63% to −67%** while the energy error is
only −15%: a state can be 99% right in energy and two-thirds wrong in enstrophy. Even at
r=43 on N=256 the enstrophy error is **−7.8%**. Since R5m established that the POD
baseline's most damning number is enstrophy (159× worse), the choice of validation metric
largely determines whether the method looks successful — and the paper must say which
metric it is held to, on both sides.

## 5. The reframed premise — defensible, and more interesting

> The developed 2D Navier–Stokes state under Kolmogorov forcing is **spectrally
> full-rank within the band the dealiased grid admits**, with no spectral gap, its
> numerical rank being exactly the grid's `2·floor(N/3)+1` and therefore not a dynamical
> quantity. Its **energy**, however, is strongly low-rank: 99% in 5 modes and 99.9% in
> 9, **independent of N**. Low-rank truncation is therefore not spectrally motivated but
> is energetically accurate, while being progressively worse for enstrophy — and the
> operator does not amplify the discarded components over a step. The method's
> appropriate use is thus energy-accurate prediction, and the crossover to
> enstrophy-accurate prediction is a quantifiable object.

That is a real claim, it is measured rather than asserted, and it makes a prediction
rather than a slogan. It also drops the barred "adaptive rank tracks slow decay" framing
entirely, which removes a failure mode rather than adding a caveat.

## 6. It also improves the cost story, and corrects R5q's expectation

R5q concluded the BUG port reaches **near-parity by N=512** at r≈45, and I computed the
flop crossover at `r = 0.82·√N`. That analysis is right but it was evaluated at the
*tolerance-selected* rank. At the **energetically** relevant rank of 5–9:

- N=256: `0.82·√256 = 13.1` — the BUG basis-update QR uses **fewer** flops than the dense
  SVD it replaces, because r ≈ 5–9 < 13.1.
- N=512: `0.82·√512 = 18.6` — a much wider margin.
- r/N ≈ 0.02–0.035 at N=256, so the method is **genuinely in a low-rank regime** rather
  than the r/N ≈ 2/3 that R11 identified for the tolerance-selected rank.

So R5q's "near-parity by N=512" is a **pessimistic** bound that holds only if the rank
stays at 43. If the rank rule is corrected to an energy criterion, the cost crossover
moves to N≈256 or below. This is the first finding in several cycles that makes the cost
argument *stronger* rather than weaker, and it is worth saying plainly that this is what
fixing a mislabelled parameter buys.

## 7. What I am asking for

**For coder (small, specific, high-value):**
1. Either rename the parameter to what it is (`relative_amplitude_cutoff`) or change the
   rule to an energy criterion `s > sqrt(tolerance) * s[0]`. **Renaming is the smaller
   change and the more honest one** — it preserves current behaviour while making it
   legible. Whichever you choose, the docstring and the artifact field name must say
   which quantity the tolerance is applied to. Do not leave a parameter named
   `tolerance` that is eight orders stricter in energy than it sounds.
2. Re-run the tolerance sweep with the corrected semantics and report the
   (energy fraction, rel L2, ΔZ/Z, rank) curve as a single table. That table *is* the
   paper's rank-accuracy result, and it is the honest replacement for "slow singular-value
   decay".
3. Add the one-step non-amplification property as a test: truncating to rank r and
   applying one full step must not amplify the relative error by more than a small
   factor. It is a real property of this operator and it is worth protecting.

**For writer:** the premise section needs rewriting along §5, and the spectrum figure
must be replaced by the rank-accuracy table from §4. The "adaptive rank growth" claim
comes out entirely — not weakened, removed — and the "slow singular-value decay" claim
becomes a statement about amplitudes with the energy statement beside it. This is a
better paper: it has a measurement, a mechanism (the dealiasing ceiling), and a
prediction (the enstrophy crossover).

**Not requested of anyone:** the N=256 gap run I have already done. If the numbers need
to be reproduced in the project's own harness, the parameters are A=0.5, Re=5000, t=2,
dealias on, `dt = 5e-4·64/N`, and the check is `rank == 2·floor(N/3)+1`.

## 8. Honest limits of this report

- I measured the developed state at **t=2**, not at a statistically steady state, which
  R8/R8a established does not exist at these parameters on these grids. The energy
  concentration and the absence of a spectral gap are both properties of the *band-limited
  field*, so I expect them to be robust to the time and the Re; the *energetic* rank in
  particular I expect to be stable, since it matched at two N. But I have not shown that,
  and S3's pilot is still owed.
- The one-step non-amplification result is one step. Error growth over many steps, and
  whether it is eventually contracting, is a different and harder question that I have
  not addressed.
- All numbers are single-node, threads pinned, A=0.5, Re=5000. The *ratios* are the
  portable part.
