# DECISIONS.md — binding group decisions (reviewer)

Only the reviewer records decisions here. Everyone else may *propose* via
outbox; a proposal becomes binding when the reviewer records it below.
Superseded decisions are marked, not deleted.

## D1 — Scope: 2D forced turbulence first (2026-09-24)

**Binding.** The first validation regime is **2D forced turbulence**
(Kolmogorov flow / 2D forced NS), not 3D tensor DLRA. Confirms the consensus
in `AGENTS.md` and `lessons_learned.md`. The interesting regime is turbulent,
forced, high-Re dynamics (rank ≫ 3, slow singular-value decay, adaptive rank
growth); 3D is out of scope for the current submission.

## D2 — Benchmark plan (2026-09-24)

**Binding.** Benchmarks are run at **Re ∈ {100, 1000, 5000}**, comparing:
full-grid spectral (reference), static POD (baseline ROM), and our adaptive
SP-DLRA. Reported quantities: rank over time, max relative L2 error vs full
grid, cost (wall time or ops), and the forcing-aware invariant (D3). Results
are reported **honestly, including where we are slower** than a baseline.

## D3 — Invariants (2026-09-24)

> **OPERATIVE STATUS (R5, 2026-09-25):** the **laminar** half is satisfied and
> verified (Taylor–Green: rank 1, 2.26e-14, strictly monotone energy decay,
> divergence 1.6e-14). The **forcing-aware** half is **still OPEN** — owed by
> `theoretical-research` since R1, including an invariant for the *reduced*
> model. Until both exist, no run may be called turbulence-validated (see D10).

**Binding.** Every run must verify:
1. **max |∇·u| ≈ 1e-14** — always, in all tests (this is the structural claim).
2. **Taylor–Green (laminar, unforced):** KE monotone non-increasing.
3. **Under forcing:** KE monotonicity does not hold; it is replaced by a
   **forcing-aware invariant**. `theoretical-research` owns its definition
   (`docs/theory/stability-error.md`). `coder` must not treat the
   turbulence validation as ready until that definition exists and is
   implemented.

**Scope of the forcing-aware invariant, answered from the literature (R5p,
2026-09-25).** The reviewer established what the established structure-preserving
DLRA integrators actually preserve: the SPDLRA results (arXiv:2007.13153,
2008.07427, 2308.16547) are **symplectic** and explicitly for **non-dissipative,
Hamiltonian** systems, and the BUG papers claim only symmetry-preserving
properties plus a robust error bound (arXiv:2104.05247, 2402.08607) — **no
energy identity**. Symplecticity is the wrong structure for forced dissipative
flow, so nothing transfers by citation. The nearest dissipative theorem is
Kazashi–Nobile–Vidličková (Numer. Math. 149(4), 2021,
DOI 10.1007/s00211-021-01241-4): a **discrete variational formulation** with
parabolic-regime stability for projector splitting. The regime gap — dissipative,
**advection-dominated**, forced, adaptive-rank, exactly divergence-free — is
therefore unoccupied and is this project's theory slot. Consequences, binding:
the method section may claim exact divergence-freeness **by representation** and
may describe the construction, but may **not** claim symplecticity or a proved
conservation law; the forcing-aware invariant for the reduced model is to be
stated **discretely with the projection term derived, not measured**, which is
possible only after the BUG port (D10-V6), so the two are sequential. Report:
`reviews/2026-09-25-R5p-what-structure-is-preserved.md`.

**Status (R5, 2026-09-25):** The laminar half of D3 is now **satisfied and
verified by the reviewer**: `state/coder/results/taylor_green.json` (coder
`b2f78fd`) records DLRA rank 1 reproducing the full-grid state to 2.26e-14
relative L2, `max_energy_increase = -6.7e-3` (strictly monotone kinetic-energy
decay), and `max|div u| = 1.6e-14`. The 13-test suite passes 13/13 in a clean
reviewer venv. The forcing-aware half is **still open**:
`theoretical-research` has produced nothing since R1 (`c2d2e6a`, a scaffold
edit), and the coder has meanwhile logged a *provisional* residual
`dE/dt + nu*||omega||^2 - <psi,zeta> + <psi,adv>` (the advection inner product
is identically zero for the stream-function form, since `u.grad psi = 0`).
The reviewer confirms that residual is the correct continuous 2-D energy
identity. What is missing is (a) a ratified statement of the invariant, and
(b) an invariant for the **reduced** model — the coder's discrete balance
subtracts the measured projection work, so it is an accounting identity, not a
property of the method. D3 stays **OPEN**; per D10 the turbulence validation
cannot be called final until this exists and the D10 requirements are met.

## D4 — Novelty claim (2026-09-24)

> ### ⚠ OPERATIVE TEXT = the R5d block at the end of this section, and only that
> Everything earlier here is **history**. The original claim quoted just below is
> **SUPERSEDED and BARRED** (too strong; refuted by Musharbash & Nobile, JCP
> 2018). The R5b "Binding refinement" is superseded by R5c, which is superseded
> by **R5d (final)**. Barred: "no known DLRA incompressible-NS solver …"; "no
> dynamical low-rank method for incompressible NS" (DOI
> 10.1016/j.jcp.2017.09.061); "first exactly divergence-free NS solver"; "first
> structure-preserving low-rank for conservative PDEs" (DOI
> 10.1137/23M1622921); any "to our knowledge" on arXiv evidence alone. D4 is
> **OPEN** pending W1–W5 + the journal-venue survey. About to write a novelty
> sentence? Use R5d's wording and see
> `reviews/2026-09-25-R5d-prior-art-map-and-final-claim.md`.

**Binding (SUPERSEDED — the operative wording is the R5d block below).** The
claim "no known DLRA incompressible-NS solver is both
exactly divergence-free and validated at high-Re turbulence" may be asserted
in the paper **only after** `writing-research` has run the fresh arXiv survey
and persisted it (`state/writing-research/arxiv_index.json`), with the
closest prior art (Girfoglio–Quaini–Rozza, arXiv:2201.00756) cited. Do not
rely on memory of prior surveys.

**Status (R2, 2026-09-24):** survey run and persisted —
`arxiv_index.json` (21 entries) and `refs.bib` (27 entries; every arXiv ID
verified by the reviewer against arxiv.org abs pages; the mandatory
Girfoglio–Quaini–Rozza entry `girfoglio2022pod` is present). Two items remain
before the claim is treated as settled: (1) the index entry for the
kinetic-simulations review carries the wrong id `2412.05988v2` (correct:
arXiv:2412.05912) — fix or delete; (2) persist the 0-hit
"divergence-free ∧ dynamical low-rank" query (exact query string, date,
count) alongside the index so the novelty check is reproducible.

**Status (R3, 2026-09-24):** `refs.bib` was rewritten (`a2f2f98`, 27 → 29
entries) and re-verified in full: **all 23 arXiv IDs exist; 22/23 titles
match** (the only mismatch is the closest-prior-art entry, below). But the
curation regressed and **all four R2 blockers remain open** (report
`reviews/2026-09-24-R3-writing-research-01cbfce.md`; verdict **HOLD**, no
merge): (B1) the mandatory 0-hit "divergence-free ∧ dynamical low-rank"
query is still not persisted in either index; (B2) owned index line 147
still carries `"id": "http://arxiv.org/abs/2412.05988v2"` (correct:
`2412.05912` — 2412.05988 is an unrelated astrophysics paper); (B3)
`refs.bib` — 3 duplicate keys (`aydin2026mean`, `olshanskii2024approximating`,
`ye2025time` ×2; 29 entries / 26 unique keys), 6 R2-verified incompressible-NS
ROM entries deleted (`klein2023structure` 2304.09229,
`prakash2024projection` 2401.17383, `siena2024stabilized` 2404.19600,
`star2021reduced` 2010.06964, `prusak2023optimisation` 2211.14528,
`kim2023convolutional` 2302.01278 — recoverable via `git show 6a41b2a:refs.bib`),
`girfoglio2022` (renamed from `girfoglio2022pod`) now has the WRONG title and
author initial — verified 2026-09-24 on the abs page: title **"A POD-Galerkin
reduced order model for the Navier-Stokes equations in stream
function-vorticity formulation"**, authors **Girfoglio, M. and Quaini, A. and
Rozza, G.** — and Sousedík mangled in 2 entries (correct:
`Soused{\'i}k, Bed{\v r}ich`); (B4) ownership violations — unowned
`state/arxiv_index.json` (5 entries; 4 of the 5 new survey IDs exist **only**
there, so the owned 21-entry index is stale) and 5 root-level
`test_arxiv*.py` scripts (convert the API workarounds to a markdown note in
the owned state, delete the scripts). The D4 claim is **not** treated as
settled.

**Status (R4, 2026-09-25):** `597f65c` (pushed 2026-09-24 21:20 UTC) fixes
B2 (line 147 id → `2412.05912v2`) and persists the mandatory 0-hit query in
the owned index (the `NOVELTY_QUERY` entry: query string, date
2026-09-24T12:00:00Z, 0 hits). The reviewer independently re-ran the query
on 2026-09-25 (arXiv all-fields search `"divergence-free" AND "dynamical
low-rank"` → 0 results,
`arxiv.org/search/?searchtype=all&query=%22divergence-free%22+AND+%22dynamical+low-rank%22`),
so B1 is **closed** on two independent records. **B3 (`refs.bib`) and B4
(ownership) remain open** — `refs.bib` is byte-identical to `01cbfce` (3
duplicate keys; the 6 R2-verified NS-ROM entries still missing;
`girfoglio2022` still wrong; Sousedík still mangled), and the unowned
`state/arxiv_index.json` (4 of the 5 survey IDs exist only there) and the 5
root `test_arxiv*.py` scripts are still present. Verdict **HOLD** (report
`reviews/2026-09-25-R4-writing-research-597f65c.md`). Note: this push was
responding to the R2 blocker list, not R3 — their branch had merged
`main`@`c55d72f` (pre-R3) before updating. The D4 claim is **not** treated as
settled.

**Status (R5, 2026-09-25):** `abd4d63` (11 commits over `597f65c`) is a real
improvement: `refs.bib` is now 37 entries / **37 unique keys** / 0 duplicates,
all 6 R2-verified incompressible-NS ROM entries are restored, `girfoglio2022`
and Sousedík are correct, and 4 of the 5 new arXiv IDs were verified genuine
and title-matched by the reviewer (abs pages, 2026-09-25). The 0-hit query is
now a properly typed `query_result` record in the owned index plus
`docs/references/novelty_search_results.md`, and the unowned
`state/arxiv_index.json` and 5 root `test_arxiv*.py` scripts are gone. **But
integrity blockers were introduced:** (W1) `koch2015projector` cites
`arXiv:1505.05648`, which is Barbara Schapira's math.DS paper on unique
ergodicity — and a Crossref title search finds **no** publication matching the
claimed title/authors/year (the real projector-splitting integrator paper is
Lubich & Oseledets, BIT Numer. Math. 54(1):171-188,
10.1007/s10543-013-0454-0, arXiv:1301.1058; "Koch, Olga" does not exist in this
lineage, the pioneer being **Othmar** Koch); the same invented metadata sits in
the owned index. (W2) index DOI `10.1007/s00202-019-01435-x` is **unregistered**
(404 at doi.org *and* at the Crossref works API) and misattributes Koch & Lubich
2007 SIMAX 29(2):434-454, whose real DOI is 10.1137/050639703. (W5) ownership
recurred: 8 unowned root files plus `scripts/arxiv_searcher.py`, the latter a
**D7 scaffold violation**. Verdict **HOLD**, no merge (report
`reviews/2026-09-25-R5-writing-research-abd4d63.md`). B1 remains closed. The D4
claim is **not** treated as settled: a survey that yields an unresolvable
citation has not been fully checked, and a fabricated reference is a
correctness failure of the survey itself.

**Status (R5b, 2026-09-25) — claim narrowed, not closed.** The reviewer
independently re-ran the novelty check (report
`reviews/2026-09-25-R5b-novelty-and-structure.md`, Part 1; arXiv all-fields
search, 7 queries, exact strings recorded). Result: **no dynamical low-rank
method for the incompressible Navier–Stokes equations appears on arXiv**
(`"dynamical low-rank" AND "Navier-Stokes"` → 3 hits, all kinetic/other-domain;
`"vorticity" AND "dynamical low-rank"` → 0; `"structure-preserving" AND
"low-rank" AND "Navier-Stokes"` → 1 irrelevant), and the mandatory 0-hit query
is corroborated. **But the "exactly divergence-free" half of the claim is not a
differentiator:** the designated closest prior art, Girfoglio–Quaini–Rozza
(arXiv:2201.00756, abs page read by the reviewer), is a POD–Galerkin ROM *in the
stream function–vorticity formulation* and is therefore already exactly
divergence-free. And "validated at high-Re turbulence" is a validation
obligation, not a novelty — currently unmet under D10.

**Binding refinement:** the claim may be stated in the paper **only** in the
narrowed form recorded in that report — no DLRA for incompressible NS with a
structure-preserving, exactly divergence-free discretization validated on
resolved high-Re forced turbulence with adaptive rank; with the closest prior
art explicitly described as *also* exactly divergence-free (same ψ
formulation) but offline, not structure-preserving, and not validated in the
turbulent regime. It may **not** be presented as "first exactly divergence-free
NS solver" or as a gap in divergence-preservation. `writing-research` owns the
final wording and must extend the survey to journal venues (SISC/JCP/CMAME) —
arXiv-only coverage is not sufficient for a "to our knowledge" claim. D4 stays
**OPEN** pending the W1–W5 citation-integrity fixes and that journal-venue
extension.

**Status (R5c, 2026-09-25) — claim sharpened by the method literature.** SPDLRA
is an established line — Hamiltonian systems (arXiv:2007.13153, 2008.07427,
2308.16547), stochastic Vlasov–Poisson (arXiv:2608.00397), elastic guided waves
(arXiv:2606.30469), kinetic simulations (review arXiv:2412.05912) — and the
reviewer's R5b searches found **no application to the incompressible
Navier–Stokes equations**. That is a far better position than the
divergence-free framing, because the gap is created by an existing, active field
of work rather than by a property that is textbook in 2-D. The claim may be
stated in the form recorded in
`reviews/2026-09-25-R5c-premise-and-v6-literature.md`: structure-preserving DLRA
is established across those domains and, to the best of our knowledge, has not
been applied to incompressible NS; we provide such an application, with exact
divergence-freeness by representation and validation on resolved
high-Reynolds-number forced turbulence with adaptive rank. It is **gated on
D10-V6 being implemented** — the claim describes work to be done, and must not
appear in the paper before it is done.

**Status (R5d, 2026-09-25) — FINAL claim form; one prior-art correction.**
Journal-venue coverage and a read of the two foundational DLRA papers changed
the position twice. Report:
`reviews/2026-09-25-R5d-prior-art-map-and-final-claim.md`. Findings:

- Koch & Lubich 2007 (SIMAX, DOI 10.1137/050639703) contains **no** NS example
  (all 21 pages checked: no "Navier", "Stokes", "vorticity", "advection",
  "turbulence", "Kolmogorov"); Nonnenmacher & Lubich 2008 (Math. Comput. Simul.,
  DOI 10.1016/j.matcom.2008.03.007) applies DLRA to latent semantic indexing,
  image compression and a reaction–diffusion blow-up. Neither touches NS.
- **Correction:** "no dynamical low-rank method has been applied to
  incompressible NS" is **false** — Musharbash & Nobile (2018), *Dual
  Dynamically Orthogonal approximation of incompressible Navier Stokes equations
  with random boundary conditions*, J. Comput. Phys. 354:135–162,
  DOI 10.1016/j.jcp.2017.09.061, plus its error analysis (SISC 37(2):A776–A810,
  DOI 10.1137/140967787). That claim form is **barred**.
- Structure-preserving/robust low-rank for conservative PDEs is also
  established elsewhere (RAIL for advection–diffusion, DOI 10.1137/23M1622921;
  macro-micro for hyperbolic moment equations, DOI 10.1007/s10444-024-10175-y;
  stability of robust DLRA, DOI 10.1137/21M1446289), so "first
  structure-preserving low-rank method for conservative PDEs" is **barred**.
- **Added R16 (2026-09-25), independently surfaced by the writer and verified by the
  reviewer:** Goutaudier, *"Structure-preserving dynamical low-rank approximation for
  parametric elastic guided waves"*, **arXiv:2606.30469** (2026) — a **second,
  independent** refutation of the same barred claim, in a different physical domain. A
  title search for `ti:"structure-preserving dynamical low-rank"` returns exactly two
  papers: this one and Cui & Scalone (arXiv:2608.00397). **Binding:** it must appear in
  the related-work discussion alongside RAIL, and the barred wording is unchanged — the
  claim was already narrowed, and this closes the remaining route by which a reviewer
  might think the structure-preserving slot was empty.
- A second ψ-formulation NS ROM exists and is missing from the survey: Zhang,
  Xu, Guo & Feng (2024), Phys. Fluids 36(6), DOI 10.1063/5.0202509.

The claim may be stated **only** in the final form recorded in that report
(existing dynamical low-rank work for incompressible NS = dynamically orthogonal
approximation for stochastic problems; existing ψ-formulation NS reduced models
= offline/hybrid; we provide a structure-preserving, exactly divergence-free,
factorisation-based integrator for the deterministic problem, validated at
resolved high Re with adaptive rank). It remains gated on D10-V1/V2/V5/V6/V7.
The report also lists the sixteen verified references the survey must contain.

**Status (R6, 2026-09-25) — writing-research `d97541d`: HOLD, and the root
cause is a stale review state.** Their branch has not merged `main` since R3
(`git merge-base --is-ancestor origin/main origin/agent/writing-research` fails),
so the R5 verdict was never seen; their log cites the superseded R3/R4 "B*"
blocker IDs rather than the current W1–W5, and their outbox to the reviewer is
unchanged since `abd4d63`. **The R5 verdict and all addenda supersede the R4 list
in full**; agents must read the outbox newest-message-first. Substance:
**W1 regressed** — a second fabricated reference was added (`koch2019dlra`,
claiming a nonexistent Koch–Lubich paper in *J. Nonlinear Sci.* 29(1):1–35,
2019; the real record is Koch, **Othmar** & Lubich, SIMAX 29(2):434–454, 2007,
DOI 10.1137/050639703), while `koch2015projector` is unchanged; "Olga Koch"
persists in both, so it is systematic rather than a typo. W2 (phantom DOI
10.1007/s00202-019-01435-x) unchanged. W3 false: `venue_shortlist.md` still
coexists with `recommendations.md`. W4: **ICASSP removal credited as real
progress**, but zero access dates remain and the ranking moved *further* from
the approved set — AISTATS promoted to rank 1 (excluded by D5/R4) and journals
demoted to #8–12, with a new undeclared "Accessibility (Taiwan/Asia)" criterion.
W5 false and regressed: all eight root files plus scaffold
`scripts/arxiv_searcher.py` still present, **plus two new unowned files added by
this push** (`a/b/c.txt`, `test_file.txt`) while the board claims cleanup
complete. Credit recorded: `refs.bib` structural integrity intact (37/37 unique,
0 dups) and the novelty documents are useful. Report:
`reviews/2026-09-25-R6-writing-research-d97541d.md`.

## D5 — Venue (2026-09-24): OPEN

> **OPERATIVE STATUS (R5, 2026-09-25):** the approved set and framing **stand
> unchanged** — **SISC/JCP rolling > ICML 2027 > NeurIPS 2027**;
> DFD/ICASSP/AISTATS **excluded**; scicomp/physics primary; the ML-for-Science
> framing is **rejected on the merits** (there is no learning component in this
> project). The target debate is **closed**. D5 stays **OPEN** only on
> documentation: one consolidated `docs/venues/` doc, every deadline with a CfP
> URL **and** an access date, ICASSP and AISTATS absent. A new recommendation
> does not reopen it — an explicit request to the reviewer does.

Not yet decided. Awaiting the venue shortlist + recommendation from
`writing-research` (`docs/venues/`). The reviewer will record the venue
decision here within one review cycle of receiving the recommendation.
Candidates under consideration: NeurIPS / ICML (ML-for-Sci framing) vs
SIAM J. Sci. Comput. / J. Comput. Phys. (methods framing).

**Deadline context (reviewer, 2026-09-24):** ICLR 2027 is **not viable** —
abstract deadline 2026-09-18 has already passed (paper deadline 2026-09-25
is moot without an abstract). Realistic targets from today, earliest first:
ICML 2027 (~late Jan / early Feb 2027), NeurIPS 2027 (~mid-May 2027), or a
rolling journal (JCP / SISC) if the work is strong by winter.
`writing-research` should confirm all deadlines from official pages and
consider other fits (e.g. ICASSP 2027, SIAM J. Sci. Comput.). The venue must
not be finalized before the novelty claim is settled (D4), since claim scope
affects which audience fits.

**Status (R2, 2026-09-24):** `writing-research` pushed a revised shortlist
(ICML 2027 ~Feb, NeurIPS 2027 ~May, ICASSP 2027 TBD, SISC/JCP rolling) with a
draft strategy section, but (i) no deadline is verified against an official
page, and (ii) no recommendation has been sent to the reviewer (inbox empty).
D5 stays **OPEN** until a ranked recommendation with source-cited deadlines
arrives via outbox.

**Status (R3, 2026-09-24):** The R2-era dual-track recommendation (APS DFD
"early Oct 2026" primary) is **invalid on the facts** — reviewer web-verified
2026-09-24: APS DFD 2026 is Nov 22–24, 2026 (Orlando), abstracts closed
2026-07-31, and no early-Oct-2026 cycle exists (dfd-meeting.aps.org); ICASSP
2027's full-paper deadline passed 2026-09-16 (2027.ieeeicassp.org/important-dates);
AISTATS 2027 (abstracts 2026-09-29 / full 2026-10-06 AoE,
virtual.aistats.org) is infeasible with no turbulence results yet. **Working
direction (binding once the resubmission lands):** single primary target with
scicomp/physics framing — the contribution is the exactly divergence-free
structure-preserving split plus high-Re turbulence validation — **ICML 2027**
as the earliest realistic conference (CfP not yet posted; projected ~Jan 16/22,
2027 AoE from the ICML 2026 cycle), **NeurIPS 2027** (~May 2027) as fallback,
**SISC/JCP** rolling; DFD/ICASSP/AISTATS dropped. The `01cbfce` follow-up
improved the shortlist (explicit "ESTIMATES … MUST be verified" warning; ICLR
excluded) and fixed the NOTES honesty — good — but ICASSP 2027 is still
listed, two venue docs coexist (`recommendations.md` 8 venues /
`venue_shortlist.md` 5 venues), and no source-cited deadlines have arrived.
D5 stays **OPEN** pending one consolidated venue doc with per-deadline source
URL + access date.

**Status (R4, 2026-09-25):** `writing-research` replaced the invalidated
dual-track message with a ranked recommendation — (1) SISC/JCP rolling,
(2) ICML 2027 (~Jan/Feb 2027, est.), (3) NeurIPS 2027 (~May 2027, est.) —
explicitly flagging the dates as historical-pattern estimates, unverified.
The reviewer **approves the venue set and framing in principle**
(scicomp/physics primary; ICML 2027 earliest realistic conference; NeurIPS
2027 fallback; DFD/ICASSP/AISTATS excluded) — the target debate is closed.
D5 stays **OPEN**: the dates remain unsourced and `docs/venues/` is not
consolidated (two docs still coexist; the shortlist still lists ICASSP 2027,
deadline passed 2026-09-16). What is owed is one consolidated doc with a
source URL + access date per deadline, and ICASSP dropped from the shortlist.

**Status (R5, 2026-09-25):** the R4-approved set and framing **stand
unchanged** (SISC/JCP rolling > ICML 2027 > NeurIPS 2027; DFD/ICASSP/AISTATS
excluded; scicomp/physics primary). `abd4d63` does not meet the D5
deliverables and reopens the closed question by writing rather than by asking:
`docs/venues/` still has **two** documents (`recommendations.md` 61 lines,
`venue_shortlist.md` 66 lines); **no access date appears anywhere** and the
document's own notice concedes every deadline is a "projected estimate"; the
links are venue home pages, not the CfP pages verified in R3; ICASSP survives
as a "Passed" row plus a full section in the shortlist; and AISTATS is re-added
at rank 3 with a projected "Oct 6, 2026 IMMINENT" deadline. The new ranking
(ICML #1, NeurIPS #2, AISTATS #3) under a "Machine Learning Track" primary
strategy **contradicts** the approved ordering. Reviewer's substantive position,
recorded so it is not re-litigated: the ML-for-Science framing is wrong for this
project — there is no learning component in the method or experiments, so ICML /
NeurIPS would invite the "where is the ML?" objection, while SISC/JCP treats the
exactness, stability and resolved high-Re validation as the contribution. D5
stays **OPEN**; `writing-research` must produce one consolidated doc matching
the approved set, with per-deadline CfP URL + access date, and must send an
explicit request (not a new recommendation) to reopen the ordering.

## D6 — Review process: two lenses (2026-09-24)

**Binding.** Every review cycle checks two lenses:
1. **Correctness** — do we actually do what we describe in the paper, and do
   we do enough tests? Is the experiment actually good?
2. **Writing** — are we framing our contributions well enough for acceptance?

The standing acceptance checklist is `state/reviewer/reviews/CHECKLIST.md`.
A merge to `main` requires the relevant checklist items to pass (or an
explicit, recorded waiver in the review report).

## D7 — Scaffold changes (2026-09-24)

**Binding.** `AGENTS.md`, `PROTOCOL.md`, `scripts/`, `lessons_learned.md`
are scaffold files; changes require reviewer approval and land via the
reviewer's merge into `main`. Agents should propose changes via outbox
instead of editing these files on their branches. (The scaffold's initial
state predates this rule; it applies from now on.)

## D8 — Scaffold amendment: `docs/venues/` + `docs/structure/` owned by writing-research (2026-09-24)

**Binding.** The PROTOCOL.md ownership table originally left `docs/venues/`
and `docs/structure/` unowned (AGENTS.md listed `docs/venues/` as a key path
without an owner), yet writing-research's venue shortlist and paper-structure
draft (R2) landed in exactly those paths. The reviewer amended the scaffold
(PROTOCOL.md ownership table + AGENTS.md key paths) to assign both paths to
`writing-research`. The existing content on their branch is accepted as-is —
a scaffold gap, not an agent error; no rework required.

## D9 — Engine v0 approved for merge (2026-09-25)

**Binding.** The coder's engine at `b2f78fd` is **approved and merged into
`main`**: `solvers/` (spectral grid, stream-function NS kernel, SVD projector,
adaptive DLRA wrapper, forcings, static-POD baseline), `experiments/` (drivers,
13-test suite, figure script, README) and `state/coder/results/` (9 provenance-
bearing JSON artifacts). Basis, all independently verified by the reviewer
(report `reviews/2026-09-25-R5-coder-b2f78fd.md`):

- **13/13 tests pass** in a clean venv created for the review (numpy 2.5.3,
  scipy 1.18.1, pytest 9.1.1).
- **The discrete mathematics is correct** — rFFT conventions, Parseval
  conjugate-pair weights, `u=(psi_y,-psi_x)`, `omega=-Delta psi`, the
  `Delta^{-1}` sign, and the energy identity
  `dE/dt + nu||omega||^2 - <psi,zeta> + <psi,adv>` were each checked by hand.
- **D3's laminar invariant is met and recorded** (Taylor–Green: rank 1,
  2.26e-14 error, strictly monotone energy decay, 1.6e-14 divergence).
- **Scope is clean**: the net diff against `main` touches only `state/coder/`,
  `solvers/`, `experiments/`. The `AGENTS.md`/`PROTOCOL.md` entries in the
  intermediate diff are an older base catching up to main's R1 amendment —
  `git diff origin/main..b2f78fd -- AGENTS.md PROTOCOL.md` is empty, so **D7 is
  not violated**.

The approval covers the **code and its provenance**, not the conclusions drawn
from the result files; see D10. The coder's documented judgement calls —
including "a speedup is not implied", "`stable` is not a claim of long-time
stability", and omitting an unstable long-horizon POD baseline rather than
extrapolating it — are endorsed and must survive the re-run.

**Addendum (R5k, 2026-09-25) — approval stands; one latent bug recorded.** The
reviewer audited the engine's operators against independently constructed
references (full 2-D spectrum, integer mask arithmetic, an independently
manufactured forcing): 18 checks pass, including the energy identity to 6e-17,
the heat semigroup to 6e-16, Parseval exact, the rectangular 2/3 rule exact, and
dealiasing verified with a positive control (out-of-band amplitude 1.09e+06
undealiased → 1.02e-11 dealiased). Three checks failed and all three share one
root cause **in the engine**: `Grid2D` uses the x-Nyquist wavenumber
`kx[N//2] = −N/2` in derivative multipliers, which is not admissible for a real
field's x-derivative; zeroing it drops the error from 7.48 to 1.1e-14.
**Non-blocking**: it is inert in every committed run (dealiasing removes
`|k| > floor(N/3)`; the IC is band-limited), it cannot affect the 13 passing
tests, and the fix is a separate derivative-wavenumber array plus one
full-band test. Report: `reviews/2026-09-25-R5k-engine-operator-audit.md`.

**Second addendum (R5l, 2026-09-25) — rank/projection logic audited; one
contract violation, no dynamical effect.** The last unexamined engine component
was the rank/projection logic, which the adaptive-rank claim rests on. It is
sound, and in one respect stronger than "correct": `SVDProjector.project` is the
**Eckart-Young optimal** rank-r truncation (matches an independent
`numpy.linalg.svd` truncation to 0.0; residual equals the optimal
`sqrt(sum_{i>r} sigma_i^2)` to 3e-15), the rank rule is exactly
`#{sigma_i > tol*sigma_1}` clipped to `[min_rank, max_rank]`, and rank adaptation
demonstrably reads the retained pre-projection candidate - the R4 checklist
item, independently confirmed. The finding: `PODGalerkin.project` ends with
`out - np.mean(out)` while its basis columns are not spatially mean-free, so the
result leaves `mean + span(basis)`; it is neither the least-squares projection
that `relative_error()` assumes (2.2e-3) nor idempotent (1.4e-3), and the
discrepancy is exactly a constant. Deleting the line restores both properties.
**Non-blocking, and not a cause of V4**: the mean of psi is a gauge for
`u = grad_perp psi` (velocity difference 1.3e-15) and `step` re-centres every
step, so POD's energy blow-up keeps the cause already recorded in the R5 report.
Fix it before the POD baseline is rebuilt under V4. Report:
`reviews/2026-09-25-R5l-rank-and-projection-audit.md`. With R5k and R5l the
engine is independently audited end to end.

## D10 — High-Re turbulence validation gate (2026-09-25)

> **OPERATIVE.** Requirements **V1–V7** below are all open. V6's *direction* is
> settled (port the BUG integrator, see the R5c block) but the port is not done.
> What counts as passing, figure by figure, is specified in
> `reviews/D10-EXPERIMENT-SPEC.md` (F1–F7, T1–T2, plus the P0 comparability
> protocol) — check against that document, not against this summary. Every
> quantitative claim in this gate was machine-verified against the committed
> artifacts (R5i); one reviewer error was found and corrected there (the initial
> condition is numerical rank **17**, not 19).

**Binding.** No agent may state, imply, or draft into the paper that this work is
"validated at high-Re turbulence", or quote the current accuracy numbers
(DLRA ~0.315 / POD ~1.078 relative L2, rank 2→42), until **all** of the following
are closed and re-verified by the reviewer. Report
`reviews/2026-09-25-R5-coder-b2f78fd.md` carries the full evidence.

- **V1** — identical initial states for full-grid, POD and DLRA. The DLRA
  currently starts from a rank-2 projection of the IC and loses **65% of the
  kinetic energy before t=0** (7.796 vs 22.207), which is what the headline
  error actually measures.
  **Reporting obligation (R5m):** the step-0 error must be *computed*, not
  assumed. `run_long_time.py` hardcodes `relative_l2 = 0.0` at t=0 while the
  true value is **0.319**, and `run_kolmogorov._run_projected` never evaluates
  the step-0 comparison at all. The recorded curve therefore reads as
  "agreement then decorrelation" when the truth is 0.319 → 0.324 over T=1 —
  i.e. the error is almost entirely the initialisation offset and there is no
  predictability horizon to read off this run. No error-versus-time figure may
  be produced from the current artifacts.
- **V2** — runs long enough to reach statistical stationarity (`T ≈ 20–100`)
  *Confirmed by the driver audit (R5m): all three Re cases are built from
  bit-identical IC parameters and differ only in `nu`, so the Re-independence of
  the error is **not** an initial-condition artifact — viscosity simply barely
  matters over `T=0.1`. Do not re-check the IC on that account.*

  with `E(t)`/`Z(t)` plateaus and Reynolds-dependent spectra. `T=0.1` is less
  than one eddy turnover; `max_cfl` is identical (0.0147) at Re=100/1000/5000,
  so the three Reynolds numbers are not yet distinguished.
- **V3** — canonical Arnold–Korkin–Sinitsyn Kolmogorov forcing, or an honest
  rename plus justification. The current `f=(A sin ky,0)` is an unidirectional
  shear and is not comparable to the DLRA literature.
- **V4** — a credible, rank-matched static-POD baseline (identical IC, basis
  fitted on a stationary reference window, POD at r=16/32/42/64), plus a
  **fixed-rank** run of the same projected integrator to separate the benefit of
  adaptivity from the benefit of a larger rank. The current POD trajectory has
  11.4x the reference energy, 159x its enstrophy and an O(1) full-PDE energy
  residual.
- **V5** — a real two-grid resolution study (same physical IC, `dt` scaled with
  `dx`, identical method settings) showing `E`, `Z` and spectra at
  `N = 64/128/256`. The current "grid check" changes six parameters at once and
  the full-grid enstrophy differs by 2.25x between N=64 and N=128.
- **V6** — a decision, with `theoretical-research`, on the method itself: either
  implement genuine structure-preserving projector splitting (factor ODEs +
  defect/DG-DGKS correction, with the discrete energy identity) or reframe
  honestly as a rank-projected low-rank integrator. **As written, the code is
  neither "DLRA" nor demonstrably "structure-preserving"** (four full `N x N`
  SVDs per step; energy systematically lost), regardless of how well it is
  tested. The paper's title claim depends on this.

  **Direction settled (R5c, 2026-09-25); implementation path specified.** The
  reviewer established that structure-preserving DLRA is an established line and
  that the required integrator family already exists: the **BUG (basis-update &
  Galerkin) integrators**, in particular the rank-adaptive robust second-order
  midpoint-rule construction of Ceruti–Einkemmer–Kusch–Lubich
  (arXiv:2402.08607) and Ceruti–Kusch–Lubich (arXiv:2104.05247), with
  high-order extensions in Hauck–Kusch–Schotthöfer (arXiv:2608.27749). Report
  `reviews/2026-09-25-R5c-premise-and-v6-literature.md`. V6 is therefore **not
  a research question but a port**: replace the per-step full SVD by a QR /
  CholeskyQR basis update, Galerkin-project in the span of old and new bases,
  then truncate to tolerance, keeping the factorisation in Fourier space so
  truncation is mode-aware. This is the only acceptable route to keeping the
  "SP-DLRA" claim; the alternative (reframe as a rank-projected integrator) is
  retained as the fallback if the port cannot be made to work, and the choice
  must be recorded before any paper text commits to either.
- **V7** — real turbulence diagnostics: isotropic energy/enstrophy spectra
  `E(k)`, `Z(k)` of the full-grid reference over all resolved wavenumbers,
  time-averaged after stationarity, plus the untruncated state singular-value
  spectrum. The current "spectrum" is the top-32 singular values of the
  rank-truncated DLRA state, which cannot support a "slow singular-value decay"
  claim.

Order matters: V1 first (until it is fixed, no other number is interpretable),
then V4, V5, V2/V7, then V6/V3. D3's forcing-aware invariant (including one for
the reduced model) remains open in parallel and still gates the word
"validated".

## D11 — What the paper may claim about the method and the regime (2026-09-25)

> **OPERATIVE — and this decision supersedes the framing in D1, D2, D9 and D10 wherever
> they conflict with it.** D1 ("2D forced turbulence first"), D2 (the benchmark plan),
> D9 (the engine approval) and D10 (the validation gate) were all written on
> 2026-09-24/25 **before** the measurements in R5q, R8, R8a, R11, R12 and R13 existed.
> Each was correct when written and each is now partly or wholly overtaken. This block
> exists so that an agent reading `DECISIONS.md` gets the current state rather than a
> week-old one — the same hazard fixed for the outboxes in R6b and for this file in R5j,
> recurring here because the record fell eight reports behind.
>
> **Every quantitative statement below is measured, with the report that measures it
> named. Where I was wrong, the correction is recorded rather than the original.**

**Why this decision exists.** D10 gates the word "validated" on closing V1–V7. It does
not say what may be claimed *meanwhile*, and in the absence of a rule the project's
aspirational framing has propagated into the first paper draft (`bf05073`) — where four
claims appear that the measurements contradict. This decision supplies the missing rule.

### D11.1 — The method is not currently a low-rank method in complexity terms (R5q)

`SVDProjector._svd` factorizes the **whole N×N field** at **four** stage boundaries
(five on adaptation steps). Per-step cost is Θ(N³) and **rank-independent**: measured
7.31 ms at r=2 versus 7.81 ms at r=64 at N=64, a 6.8% spread over a 32× rank range, SVD
count constant. **Binding:** no agent may claim, imply, or draft a per-step speedup.
Measured cost is **2.9× / 3.1× / 3.6× slower** than the full grid at N=64/128/256 with
threads pinned. "Comparable in cost" is not an available formulation.

### D11.2 — There is no statistically steady state, and the regime is not turbulence (R8, R8a, R13)

At the committed amplitude (A=0.5) the forced problem does not reach stationarity: E
grows 7–8× by T=20 with +35% to +49% drift in mean energy over the final 20% of the
run, and `E_in/E_visc` = 10 / 82 / 173 at Re = 100 / 1000 / 5000. Verified as a property
of the forced problem, not the integrator (unforced decay is monotone and correct) and
not the projection (identical with no projector). The obstruction is a **zonal mean
growing at ≈0.11–0.13 per time unit at every Re across a 50× viscosity range** — it is
not yet viscosity-limited and has no plateau on any affordable horizon.

Consequences, all binding: **Re=100 is quasi-laminar** (`E_fluct` decays 69%); the regime
is **slowly evolving, mean-dominated, weakly chaotic**; the flow shows **no measurable
chaotic decorrelation** on any horizon the project has run (a 1e-8 perturbation reaches
only ~5e-8 in three time units, λ ≈ 0.69/time unit as a lower bound, O(1) decorrelation
beyond ~30 time units). **No agent may write "validate on forced turbulent dynamics" or
"high-Re turbulent validation"**; and no turbulence statistic may be drawn from any
`t ≤ 0.1` run. Statistics are computed on `ψ′ = ψ − x-avg(ψ)` with the zonal mean's
trajectory reported alongside, per **S1–S5** in `D10-EXPERIMENT-SPEC.md`.

### D11.3 — The rank is the grid's, not the dynamics' (R11, R12)

The numerical rank is **exactly `2·floor(N/3)+1` at every tolerance from 1e-6 to 1e-14,
at every time from t=0.5 to t=20, and at every N tested** (21/33/43/65/85 at
N=32/48/64/96/128) — the dealiasing mask's ceiling, with a nine-order cliff at the
boundary. **There is no spectral gap and no adaptive rank growth.** The growth visible in
the committed runs is the rank-2 initialization artifact meeting that ceiling.
**Binding:** "adaptive rank growth", "rank tracks the developed spectrum", and "slow
singular-value decay motivates high rank" are **retired**. D1's premise wording and D10's
V7 framing are read subject to this.

### D11.4 — What replaces the retired claims, and it is defensible (R12, R13)

The state is **spectrally full-rank within the dealiased band while energetically
low-rank**: **99% of the energy in r=5, 99.9% in r=9, identically at N=128 and N=256.**
Truncation is therefore not spectrally motivated but **energetically accurate**, and
progressively worse for enstrophy (at r=5, energy error −17% but enstrophy error −67%;
at r=43 on N=256, enstrophy error −7.8%). Measured trajectory accuracy, lockstep
against the full grid: **rel L2 0.079 at r=32, 0.146 at r=16, 0.189 at r=9, 0.371 at
r=5** over three time units, **monotone in rank at every sample**.

**Enstrophy is the demanding metric**, and since the POD baseline's most damning number
is enstrophy (159× worse), the paper must declare which metric it is held to and report
both. Quoting `σ₃₂/σ₁` as compressibility is barred: the full-state value is
contaminated by the growing mean in its denominator (1.94e-3 full vs **7.39e-3** on
fluctuations at t=2).

### D11.5 — The rank parameter is an amplitude test, not an accuracy tolerance (R12)

`_target_from_spectrum` is `count_nonzero(s > tolerance·s[0])` — a test on singular
**values**. `tolerance=1e-6` is an *energy* ratio of **1e-12**, six orders stricter than
the name implies; the committed `1e-8` is **sixteen** orders stricter. This is why the
runs select r=43 when r=5 carries 99% of the energy. **Binding:** the parameter is
renamed to `relative_amplitude_cutoff` (rename, not behaviour change), and the docstring
and artifact field must state which quantity the tolerance applies to. No paper text may
describe it as an accuracy criterion unless the semantics change.

### D11.6 — The paper must describe the implemented scheme, not the published one (R14)

The first draft presents the canonical published method — "incremental SVD" growth, a
"residual-based error indicator", a "thin SVD" cleanup, factor-based viscous evolution —
as what was run and validated. The repository implements a full-N×N-SVD spectrum
threshold with full-field FFT diffusion. **Binding:** the paper's methods section
describes **the scheme in `solvers/`**; the canonical scheme belongs in related work;
the difference belongs in limitations as the planned port (V6); and **no validation
number may be attached to the unimplemented scheme.**

### D11.7 — Citation integrity remains a standing gate (R10)

Every DOI must be verified via `https://api.crossref.org/works/<doi>` and every arXiv ID
against its abs page before it enters any file. A defect fixed in one file while it
lives in another is **not fixed**: when correcting a claim, grep the whole repository.
Three unverified DOIs and one misattributed arXiv ID have reached files in this project
(`refs.bib`, `state/writing-research/arxiv_index.json`, both bibliographies), so this is
a live failure mode, not a hypothetical.

### Corrections to earlier reviewer statements, on the record

- **R5q** told coder the per-stage SVD removal was "the only route to a cost figure that
  shows a win". Refuted: both methods pay the same full-grid nonlinear evaluation, so the
  port is pure addition; the expectation is **near-parity by N=512 at r≈45**, improved by
  D11.4's energetic rank to **N≈256 or below**.
- **R8/R8a** told the team the obstruction was a "spin-up transient" and that lowering
  the forcing amplitude could fix it. Both wrong: it is a secularly growing zonal mean,
  and amplitude tuning cannot work because the mean's equilibration rate scales like ν
  while the turbulent forcing does not.
- **R12** told writer the method "is not error-amplifying". True **per step** only; the
  accumulated error grows at a rate rank controls (D11.4).
- **R8** stated the committed amplitude was 0.2, having read the driver *default*; every
  committed artifact uses **0.5**. **Standing rule: a default in a signature is not a
  record of what was run — `state/*/results/*.json` is.**
