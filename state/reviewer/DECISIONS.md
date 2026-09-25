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
