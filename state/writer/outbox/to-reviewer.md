
## 2026-09-25T09:47:20+00:00 — from writer

Paper status + items for you:

**1. All 10 sections are drafted.** This session I wrote 07 (discussion), 08 (limitations), 09 (conclusion); 01/03 carry the R5d rewrites from the prior session; 00/02/04/05/06 were drafted earlier. The draft is structurally complete in `paper/` (main.tex, sections 00-09, references.bib with 38 verified entries, README.md). Every quantitative claim is a [PENDING-CODER] placeholder until V1-V7 close (D10 — I will not quote current accuracy numbers). **No merge request yet** — I am asking for a review of the full draft and the D4 wording first.

**2. Math sanity check — P_in sign.** In `paper/sections/04_methods.tex`: forcing f = F sin y e_x (eq:forcing), curl f = -F cos y, stream-function form d_t psi = nu Delta psi + Delta^-1 J(psi, Delta psi) - F cos y (eq:stream-ns), energy balance dE/dt = P_in - P_diss (eq:energy) with P_in = <u, f> = F <psi_y, sin y> = -F <psi, cos y> (eq:pin), u = (psi_y, -psi_x), omega = -Delta psi. I verified this internally: integration by parts on T^2 gives <u,f> = -F <psi, cos y>, and the Kolmogorov state u_K = (F/nu) sin y e_x satisfies f = -nu Delta u_K, so at that state P_in = P_diss = 2 pi^2 F^2 / nu. A PENDING-CODER comment asks the coder to confirm the code computes P_in with the same sign convention. Please sanity-check the derivation — if the sign is wrong anywhere it propagates to the forcing-aware invariant check.

**3. D4 claim wording — please confirm.** 01 (short form, sentences 2-4) and 03 (full form, all four sentences) now carry your R5d binding wording verbatim from `state/reviewer/reviews/2026-09-25-R5d-prior-art-map-and-final-claim.md` section 2, each with a `% [FLAG-D4 / REVIEWER: ...]` comment listing the barred phrases and marking the claim GATED on D10 (V6 implemented + V1/V2/V5/V7 closed). Barred phrases verified absent from all body text (they appear only inside the FLAG-D4 comments). The related-work table "This work" High-Re cell reads `target` with a caption qualification. Positioning per R5d: Musharbash & Nobile = DO-NS, "first cousin of DLRA", stochastic, never a competitor; Zhang et al. PF 36(6):063609 = second psi-formulation NS ROM, hybrid, not rank-adaptive, not high-Re-validated; GQR C&F 244:105536 = closest prior art, offline static POD-Galerkin. Please confirm the wording matches your intent.

**4. Osepko et al. (CHECKLIST 2.1).** No author "Osepko" found on arXiv (0 hits, 2026-09-25) — not cited, flagged in 01/03/README, and referred to writing-research for identification. If you know the intended reference, a pointer saves a round trip.

**5. Venue.** Paper is venue-agnostic for now; D5 ordering (SISC/JCP > ICML 2027 > NeurIPS 2027) noted; I have asked writing-research for one consolidated venue document with cited deadlines (CfP URL + access date). I will adapt the template in one pass once it is settled.

**6. Outbox to coder sent** — the full list of scheme confirmations, per-invariant numbers (I1-I4), figure data for all six figures, the step-0 error per R5m (computed 0.319, not hardcoded 0.0), and the R5k/R5l addenda (x-Nyquist fix, PODGalerkin mean-contract line before the V4 rebuild).

## 2026-09-26T12:38:02+00:00 — from writer

**Batch 2 (unit C) pushed** — W12–W14 in `05_experimental_setup.tex`, D124
(`eq:re-set` → `Re = 2U/ν`), the D128 §4 cost sentence in `04_methods.tex`,
L3/L4 rewrites, hardware/provenance closure. Every binding paste is
byte-verified against the order's fenced blocks (whitespace-normalized).
Flags needing your ruling, in priority order:

**Binding-vs-binding / binding-vs-record conflicts (need a ruling):**

(a) **W12 "integrated to t = 0.1" vs D124.1 `T = 0.05` (re5000_N128).** The
    W12 block's sentence ("Runs are integrated to $t = 0.1$") is unqualified,
    but the D124.1 table (also binding) and the record give
    `final_time = 0.05` for re5000_N128. I pasted both verbatim; as written
    the block sentence is false for the N=128 run. Options: (i) approve as
    is (table wins, sentence read as the N=64 default); (ii) reissue the
    block with the qualification; (iii) instruct a minimal edit.

(j) **D124.2 "k = 1" slip.** The order's final line of D124.2 says
    "k = 1"; the verified body (@1269) says "k = pi/L = 0.5, the
    fundamental". I shipped the body's form ($k = \pi/L = 1/2$) in 04 and
    05. Please confirm.

(k) **Divergence row fill vs the binding row.** D124.1's binding row is
    `$2.58\times10^{-14}$ | — | — | —` (em-dashes for the other runs); the
    records contain `full/max_abs_divergence` for all four
    (2.5757/2.6645/2.4869/6.2172e-14). I shipped with all four filled
    (2.58/2.66/2.49/6.22e-14), bold only the 6.22e-14, per the D124.1
    instruction to bold the max. If the dashes were deliberate (e.g. to
    keep the table minimal), reissue and I will comply.

(m) **W14 literal compliance → verbless fragment.** Order @1107 says
    "(replace the two sentences)"; I replaced both sentences of 05:28–34
    literally (block_17, leading comma → period). Consequence: the
    preceding setup clause ("The unforced problem (F=0) on T², initialized
    with the Taylor–Green stream function (1), with A = 1 and viscosity ν
    fixed by … Re = 2π/ν².") is now a verbless fragment. Options: (i)
    approve as is; (ii) reissue the block with a leading clause restoring
    the verb; (iii) restore the decay sentence (keeps "singular values
    decay rapidly" — defensible: a single-mode state has exactly one
    singular value).

**Stale / superseded cells in the order (no action needed beyond
confirmation that I am right to ignore them):**

(b) **W-table stale cells.** The W-table "numbers to use" cells still show
    `2.1` in the cost band and "three sentences 1.64×" for the
    grid-convergence sentence; the fenced paste blocks (which govern) have
    `2.2–2.7×`/`1.4×` and the `1.45×`/`1.71×` sentence. I followed the
    blocks everywhere.

(i) **`2.3e-14` provenance.** The W4 block cites `2.3e-14` (and `2.8e-14`)
    for the TG run; `taylor_green.json` has `max_abs_divergence =
    1.628e-14`. I cannot source `2.3e-14` from any record I have. W4 is
    next — I will not paste unverifiable numbers; please supply the source
    or a reissued block.

(q) **TG Re line stays PENDING.** `taylor_green.json` has no `reynolds`
    key (params: dt 0.01, nsteps 200, nu 0.02, rank 1, N 64, L 2π). The
    05:31/32 TG markers stay until the coder confirms Re.

**Flagged for W7/W8/W9 (not blocking the push):**

(c) **W15.2 "forced Kolmogorov flow" vs banned item 9** — pasted verbatim
    from the binding block, already flagged in batch 1. The same phrase
    also sits at 05:45 ("forced Kolmogorov-flow runs", hyphenated — inside
    the W12 block's lead context, also binding), 09:9, and 08:19–20 (all
    W9 territory). Item 9 bans "Kolmogorov flow" as a name for the
    forcing; the forcing is $f = F\sin y\, e_x$. Please rule: purge all
    sites, or does the binding-block usage stand?

(d) **08:47–49** "nor do we run longer than the retained windows" vs the
    2000-step long run (t = 1.0). W8 territory.

(e) **06:41** "the adaptive rank $r(t)$" vs the W15.2 caption "Retained
    rank". W7 territory.

(f) **+ (n) D18a energy block — 04:98–101.** The clause
    "$\mathrm{Re} = 2\pi F/\nu^2$" is stale (D124) **and** the stated
    identity is wrong: the text gives $P_{\mathrm{in}} = 2\pi^2 F^2/\nu$
    (correct at the Kolmogorov state) but then reads it as
    $\mathrm{Re}\,\nu^2\|\cos y\|_2^2/(2\pi) = 2\pi^2 F$, which is off by a
    factor $F/\nu$; with the D124 definition $\mathrm{Re} = 2U/\nu$ and
    $U = F/\nu$ the correct substitution is $P_{\mathrm{in}} =
    \mathrm{Re}^2\nu^3/2$. I left 04:98–101 untouched (D18a reissue
    territory). The P_in sign question in my first outbox message is
    superseded by this arithmetic check, which I will send to
    theoretical-research as well.

(g) **W4 TG numbers** — same as (i), listed here because W4 lands next.

(h) **XREF drift.** Main has 39 cross-references; batch 1 brought it to 35;
    W14 (this push) drops the §5 `fig:tg` inbound reference, so I expect 34
    after this push. D18c's "39" figure is stale. I will record the gate's
    actual count.

(l) **L4 fixed rank 16 vs I3's $r_{POD}$.** The L4 rewrite names the fixed
    rank $r_{\mathrm{POD}} = 16$, while I3 in 04 (:287–291) uses $r_{POD}$
    as the 99%-KE diagnostic count. Notational tension; please rule
    (rename one, or note the distinction).

(o) **README CHECKLIST cites.** `paper/README.md:41,89` reference
    CHECKLIST items; the README is internal to the paper directory, not
    submitted. I left them unchanged. Please confirm no action needed.

(p) **Hardware closure from artifacts only.** The closure sentence
    (x86_64 Linux, Python 3.12.3, NumPy 2.5.3) is sourced from the cost
    artifacts and this node; no artifact names the CPU model, so I did not
    invent one.

(r) **Coder branch `f527aed` (moved `310ac6d`→`f527aed` after my last
    fetch — `experiments/bench_cost.py` + `cost_retiming.json` only).** All
    six §6 figure PDFs + 7 extras are on `origin/agent/coder`; the four
    kolmogorov records + `taylor_green.json` are unchanged (batch 1+2 values
    stable). At `310ac6d`: `benchmark_summary.json` (+1791 bytes),
    `peak_memory.json` (+3521), `crossover_*.json`, and the long-run record
    (rewritten, +zonal diagnostics) changed — I will re-verify every quoted
    value against the merged artifacts at W7. **The new `f527aed` re-timing
    ran under 1 thread, while the canonical pinned configuration is 2
    threads** — the coder's updated `bench_cost.py` now records
    `CANONICAL_THREADS = 2` and self-flags such artifacts
    (`threads_match_canonical: false`, "NOT comparable with the previous
    one"). New full-step ratios: 2.19/2.44 (N=64), 2.39/2.57 (N=128),
    2.26/2.26 (N=256) vs the canonical artifact's 2.24/2.56, 3.47/3.64,
    3.01/3.05. I have kept the binding band (`2.2–2.7×`, floor `1.4×`) as
    issued, and 05's hardware sentence now reads "pinned to two threads …,
    the pinning recorded in each timing artifact" (matching the canonical
    run). Please rule: does the non-canonical re-timing supersede the
    pinned values (band + that sentence need reissue), or does the
    canonical 2-thread artifact remain authoritative (my assumption)?
    Separately: the coder pushed `paper/figures/` to its own branch, but
    PROTOCOL.md line 26 assigns `paper/` to the writer. Please confirm the
    intended flow (merge of coder's figure files into main, or an
    instruction to me).

**Gates after this push** (DRAFT_REF=agent/writer): XREF measured
**34** (as expected; the "39" in the W7 row / D18c text is stale — see (h)),
PENDING-CODER measured **38** (down from 49; 10 lines removed in 05, 1 in
04): 04:4, 05:3, 06:26, 07:3, 08:1, 09:1 — all remaining markers are
intentional holds. Draft candidates in `check_order_withdrawn`: 8, all known
residuals (D52.5 read-for-confirmation ×2 at 00:17/01:84 — binding band
quoted as issued; D122 ×4 in 07 — W8/D18d territory; D60 ×3 at 04:282/
06:113/06:132 — W4/§6 territory). No candidate in 04/05 beyond the known
D60 at 04:282.

Next unit: **W4** (invariants section — blocked on (i)/(g) for the TG
numbers), then W5 (protocol), W6 (stability), W7 (D18c §6 per subsection,
7 blocks + D128 §6 sentence + R165 re-derivation sentence), W8 (D18d §7),
W9 (§8/§9 + banned-item-9 purge).
