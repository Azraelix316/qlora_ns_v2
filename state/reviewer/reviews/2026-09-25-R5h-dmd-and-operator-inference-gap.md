# R5h — the DMD / operator-inference gap in our prior art and baselines

**Date:** 2026-09-25 · **Reviewer cycle:** R5 (addendum 4) · **Trigger:** a gap I
had flagged but never searched
**Outcome:** the permitted novelty claim is **unchanged**, but the baseline set
(F5) and the related-work obligation both change, and a reviewer who knows this
literature will ask "why not DMD?" — so the paper needs an answer.

---

## 1. What I searched and found

R5d mapped the *low-rank integrator* prior art thoroughly. It did not cover the
adjacent **data-driven model-reduction** literature for incompressible flows and
turbulence, which is large, well known, and the first thing a scicomp reviewer
will reach for. All records below verified 2026-09-25 (arXiv abs pages; Crossref
works API).

| Work | What it is | Verified ID |
|---|---|---|
| Peherstorfer & Willcox (2015), *Dynamic data-driven reduced-order models*, Comput. Methods Appl. Mech. Engrg. 291:21–41 | the canonical DMD-for-CFD-snapshots paper — dynamic data-driven ROM with interpolation to incomplete data | DOI 10.1016/j.cma.2015.03.018 |
| Williams, Kevrekidis & Rowley (2015), *A data-driven approximation of the Koopman operator: extending DMD to the Koopman spectral modes*, J. Nonlinear Sci. 25:1307–1346 | DMD/Koopman extension | DOI 10.1007/s00332-015-9258-5 (journal; arXiv:1408.4408 is the preprint) |
| Benner, Goyal, Heiland & Pontes Duff (2021), *Operator inference and physics-informed learning of low-dimensional models for incompressible flows*, ETNA 56:28–51 | learns **structured** low-dimensional models for incompressible flow, "utiliz[ing] the intrinsic structure of the Navier–Stokes equations"; decouples velocity and pressure dynamics | DOI 10.1553/etna_vol56s28 (arXiv:2010.06701) |
| Benner, Heiland & Werner (2022), *Robust output-feedback stabilization for incompressible flows using low-dimensional models*, Comput. Optim. Appl. 82(1):225–249 | stabilisation of such low-dimensional models | DOI 10.1007/s10589-022-00359-x |
| Goyal, Pontes Duff & Benner (2025), *Guaranteed stable quadratic models and their applications in SINDy and operator inference*, Physica D 483:134893 | **guaranteed** stability for quadratic model structures | DOI 10.1016/j.physd.2025.134893 |
| Moore, Tsai, Gruber, Farcaş, Wentland, Tezaur & Iliescu (2026), *Learning long-term stable operator inference reduced-order models of fluid flows through online spatial filtering*, arXiv:2609.14812 (13 Sep 2026) | current state of the art on long-term stability of OpInf fluid ROMs | arXiv:2609.14812 |

Searches that came back empty are themselves informative: `"dynamic mode
decomposition" AND "stream function"` and `"low-rank" AND "2D turbulence" AND
"Navier-Stokes"` return nothing on arXiv, i.e. **nobody appears to have combined
DMD-style data-driven reduction with a stream-function (exactly
divergence-free) representation of 2-D periodic turbulence.** That is a small
but real niche the paper can own, and it is adjacent to — not inside — the gap
D4 already describes.

## 2. Why the novelty claim is unchanged

DMD and operator inference are **data-driven, offline** reduced models: they fit
a low-dimensional operator to a snapshot database. Our method is
**factorisation-based and on-the-fly**: it evolves factors of the state, needs no
snapshot database, and adapts its rank during the simulation. The Benner line
comes closest in *spirit* — it exploits intrinsic NS structure to learn a
structured low-dimensional model — but it is learned from data for a channel
flow with an engineered ansatz, not a deterministic integrator in a
representation that makes the constraint exact.

So the claim permitted in D4 stands unchanged. What changes is the **obligation
to distinguish**, and there is a crisp and favourable distinction available:

> Our structure comes from the *representation* — a stream-function state makes
> ∇·u = 0 exact for the full-grid and every reduced state, at every step, with no
> constraint to enforce and nothing to learn — whereas the data-driven
> structured models obtain their constraints from an engineered ansatz fitted to
> snapshots, and the operator-inference line targets controlled/engineering
> settings rather than resolved turbulent validation.

That is a better argument than "we are the only ones": it says *why* the
structure is cheaper and unconditional here.

## 3. Two changes this forces

**(a) F5 gains a baseline: POD-DMD.** Static POD is the wrong sole data-driven
comparison for a 2017+ scicomp venue; dynamic data-driven ROM (POD-DMD) is the
standard, and Peherstorfer & Willcox is its reference. It is cheap to add on top
of the existing `solvers/pod.py` machinery: project the snapshot window onto a
POD basis, fit the linear operator by (exact or SVD) DMD, advance the modal
coefficients, and reconstruct. Report it at the same matched ranks as the static
POD baseline, from the identical initial state, under the same `dt` policy. This
is a genuine strengthening: a reviewer can no longer say the comparison was made
against a strawman, and if our method loses to POD-DMD on some metric, that is
information we would rather have now than at review.

**(b) Related work must position this literature.** Five records minimum: the
two Peherstorfer/Willcox/Kevrekidis DMD papers, the Benner line (ETNA 2021 plus
the stabilisation and guaranteed-stability follow-ups), and the 2026
long-term-stability OpInf paper. The paper needs a short subsection on
data-driven reduced models for incompressible flows, and an explicit answer to
"why not DMD/OpInf?" — the points above are the answer.

## 4. A correction to my own earlier work, for the record

While verifying these I found that the reference I had in mind for the
Peherstorfer–Willcox DMD line ("Dynamic mode decomposition for prefetching CFD
snapshots") could not be confirmed in Crossref under that title, and that the
Williams–Kevrekidis–Rowley paper I would have cited as a SIAM J. Appl. Dyn. Syst.
article is in fact *Journal of Nonlinear Science* 25:1307–1346. Neither is cited
anywhere in the project, so nothing downstream is wrong — but it is the second
time in this review cycle that a plausible-looking citation failed verification
(the first was `koch2015projector`), which is why the rule in the checklist is to
verify every ID rather than trusting recall. The verified list above is what
should enter `refs.bib`.

## 5. What this does *not* change

- The D10 requirements V1–V7 are unaffected; F5's bar is unchanged in substance
  ("beat the baselines at matched rank, or report that you do not").
- The method decision (BUG port) is unaffected — nothing here argues for a
  different integrator.
- The permitted novelty wording in D4 stands. This addendum adds related-work
  obligations and one baseline, not a new claim.
