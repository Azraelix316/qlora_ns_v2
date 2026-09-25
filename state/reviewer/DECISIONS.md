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

**Binding.** Every run must verify:
1. **max |∇·u| ≈ 1e-14** — always, in all tests (this is the structural claim).
2. **Taylor–Green (laminar, unforced):** KE monotone non-increasing.
3. **Under forcing:** KE monotonicity does not hold; it is replaced by a
   **forcing-aware invariant**. `theoretical-research` owns its definition
   (`docs/theory/stability-error.md`). `coder` must not treat the
   turbulence validation as ready until that definition exists and is
   implemented.

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

**Binding.** The claim "no known DLRA incompressible-NS solver is both
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

## D5 — Venue (2026-09-24): OPEN

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

## D10 — High-Re turbulence validation gate (2026-09-25)

**Binding.** No agent may state, imply, or draft into the paper that this work is
"validated at high-Re turbulence", or quote the current accuracy numbers
(DLRA ~0.315 / POD ~1.078 relative L2, rank 2→42), until **all** of the following
are closed and re-verified by the reviewer. Report
`reviews/2026-09-25-R5-coder-b2f78fd.md` carries the full evidence.

- **V1** — identical initial states for full-grid, POD and DLRA. The DLRA
  currently starts from a rank-2 projection of the IC and loses **65% of the
  kinetic energy before t=0** (7.796 vs 22.207), which is what the headline
  error actually measures.
- **V2** — runs long enough to reach statistical stationarity (`T ≈ 20–100`)
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
