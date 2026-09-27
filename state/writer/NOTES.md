# NOTES.md — writer

> Branch: `agent/writer` · Worktree: `worktrees/writer`
> Status: order applied and audited block-by-block (24 blocks: 16 verbatim, 1 blocked on D18a, 1 skipped as stale, 6 D138 re-pins). This pass: D18b into §6/§7/§8, §9 headline numbers, README currency. Gates: build 0 defects/7 graphics, claims_registry 0 untraced. NOT compiled (no TeX here). Open: D18a, 2 stale registry rows, no D138/D139 record.
non-canonical re-timing; 05 hardware sentence corrected one→two threads per
the canonical artifact); gates recorded post-push (XREF 34, PENDING-CODER
38, draft candidates 8 = known residuals); next W4–W9 (W4 blocked on TG
numbers (i)/(g); W5 cost wording pending (s); W7 = D18c §6 per subsection,
7 blocks + D128 §6 sentence + R165 re-derivation sentence; W8 = D18d §7;
W9 = banned-item-9 purge at 09:9 + 08:19–20).

## Mission

Write the paper. Draft in `paper/`, integrating: theory from
`theoretical-research` (`docs/theory/`), numbers from `coder`
(`state/coder/results/`), and references + venue from `writing-research`
(`refs.bib`, `docs/venues/`).

## Owned paths (write only here)

- `state/writer/` — this board, section status, open questions
- `paper/` — draft, sections, figures, templates

## Section status (2026-09-25)

| File | Status |
|---|---|
| `00_abstract.tex` | **W11 re-paste 2026-09-26 from the current D13 block** (byte-verified; `1.45`/`1.71` grid-convergence sentence, `2.2–2.7×` band, `1.4×` pessimistic floor); resolves R168 items 1–2; all numbers reviewer-verified |
| `01_introduction.tex` | **W16 applied 2026-09-26**: W16.1 cost band `2.1–2.7×` → `2.2–2.7×` + `1.4×` pessimistic floor; W16.2 basis-claim sentence (clauses ii–iii: subspace rebuilt as dynamics develop; "reaches the rank budget within fifteen steps and stays there"); W10 `koch2019dlra` → `koch2007` (:33); W3 D11 + D4 short form (R5d, FLAG-D4) unchanged |
| `02_contributions.tex` | **W2 re-paste 2026-09-26 from the current D14 block** (`2.2` band in item 5); **D130 applied 2026-09-26**: item 3 label → "a static subspace's advantage stops at a rank budget, not at a rank the dynamics chooses"; invented "saturation plateau" clause → stopping-rank sentence ($2\lfloor N/3\rfloor+1$ = the rank budget we set from the grid); last sentence kept exactly |
| `03_related_work.tex` | drafted; D4 full form (R5d binding wording, FLAG-D4); `tab:related` High-Re cell = `target`; Osepko flagged; **W10 applied 2026-09-26**: Koch–Lubich "survey" sentence deleted (no such paper, R139/R140) + `koch2019dlra` removed from the cite list |
| `04_methods.tex` | drafted; governing section: I1–I4 numbering, eq:pin/energy, prop:viscous, eq:step, eq:indicator; **D15 fix 2026-09-26** (`99\%` at :288); **W10 applied 2026-09-26**: `koch2019dlra` → `koch2007`; **batch 2 2026-09-26**: E8 Re clause ($Re = 2U/\nu$, $k = \pi/L = 1/2$ at the fundamental, pointer to Table~\ref{tab:forced-params}) + E9 D128 §4 cost-mechanism sentence verbatim inside the viscous-cost remark; :100 stale $Re = 2\pi F/\nu^2$ left untouched (D18a territory, flagged (n)) |
| `05_experimental_setup.tex` | **batch 2 applied 2026-09-26** (all binding pastes byte-verified): W13 §5 lead paragraph (block_16); W14 TG setup — literal two-sentence replacement (block_17, leading comma → period; preceding clause now a verbless fragment, flagged (m) with 3 options); W12 L2 binding block (block_15) + per-run lead naming the four `kolmogorov_*.json` stems + tab:forced-params (booktabs, `lccccl`, 14 rows, bold 128/2.5e-4/0.05/three ν/85/6.22e-14; every source key verified against the records; same-steps "(200)" sentence); D124 eq:re-set → $Re = 2U/\nu$; L3 rewrite (marker drop, \cite{orszag1971} kept); L4 fixed-rank-16 rewrite (marker drop); hardware closure + CHECKLIST-clause removal (post-fetch: thread count
corrected one→two per the canonical 2-thread artifact — flag (r)).
Remaining PENDING-CODER: TG×2 (:28/:32) + results-layout (:175) — all
intentional holds |
| `06_results.tex` | drafted; all numbers/figures [PENDING-CODER]; `tab:div` placeholders; step-0 per R5m (0.319, not 0.0); **D15 fix 2026-09-26** (`99\%` at :133); **W15 applied 2026-09-26**: L2 expected-outcome sentence → W15.1 saturation block (byte-verified) + standalone slow-decay sentence; `fig:rank` caption → W15.2 ("Retained rank"; budget within fifteen steps; three curves coincide); r*(Re) dropped from the four L2/L4 markers; L4 expected-outcome sentence deleted ("retained rank" in marker); L1 subsection (`fig:tg`, `3 \to 2 \to 1`) and L4 subsection untouched — both to be replaced by D18c in W7 |
| `07_discussion.tex` | drafted 2026-09-25 (rank as diagnostic, invariants/long-time, dimensional regimes, 3D) |
| `08_limitations.tex` | drafted 2026-09-25 (2D/periodic/Re≤5000, TG-only decay, no per-step speedup, no stability analysis, D3 open, no V2 study); **W15 applied 2026-09-26**: L1 bullet body → W15.3 (TG state a single Fourier mode from the outset, numerical rank one; forced rank rises to the budget; decay-events marker deleted — 2000-step run has none); "online rank adaptation" → measured rank-criterion phrasing (W15.4); V2 sentence → "rank already at its ceiling for $99\%$ of the longer run" (W15.6); lines 19–20 "turbulent-validation ladder" still to purge in W9 (banned item 9) |
| `09_conclusion.tex` | drafted 2026-09-25 (summary + [PENDING-CODER] headline + future work); **W15 applied 2026-09-26**: (iii) "online rank adaptation …" → "a rank criterion whose saturation at the grid's alias-free ceiling we measure and report" (W15.4); headline marker shrunk (r*(Re) items dropped); research question → W15.5 (retained rank does not grow with Re; zonal share falls $20\%$→$18\%$; resolved-band-vs-flow question); PENDING-THEORETICAL-RESEARCH marker rewritten to the tolerance-driven-criterion question; line 9 "turbulent dynamics" still to purge in W9 (banned item 9) |
| `main.tex` | venue-agnostic `article` skeleton + swap-in comment; plain `\cite`, no natbib |
| `references.bib` | 38 entries, all web-verified 2026-09-25 (15 [V] arXiv, 14 [J], 9 [C] classics) |
| `README.md` | counts, flags, placeholder legend; D4 flag = GATED on D10 |

## Consistency checks passed (2026-09-25)

- R5d barred phrases: zero in body text (hits only in intentional FLAG-D4 comments in 01/03).
- natbib: zero occurrences (plain `\cite` + `thebibliography`-style `\bibitem`-free bib; no natbib commands anywhere).
- Every cited key ∈ `references.bib` (fixed `orzag1971` → `orszag1971` typo in 01).
- Every `\ref`/`\eqref` target defined; no duplicate labels.
- All 11 `.tex` files brace-balanced (non-comment lines).
- I1–I4 tags consistent with 04's governing numbering (I1 divergence-free, I2 energy, I3 rank economy, I4 turbulent fidelity); fixed 07 (energy I3→I2, comment I3/I4→I2/I4), 09 (I3→I2), 06 (dropped wrong I3 tag from the cost subsection).
- 06 figure-caption bracket bug fixed (six captions had their closing `}` inside a trailing comment).

## Open items

- [ ] coder: scheme confirmations + per-invariant numbers + 6 figure data sets + `tab:div` + computed step-0 error (R5m) — list sent in outbox.
- [ ] writing-research: consolidated venue doc with cited deadlines (D5); reconcile shared `refs.bib` vs `paper/references.bib`; confirm R5d-priority entries; identify "Osepko et al.".
- [ ] reviewer: confirm D4 wording matches R5d intent; sanity-check the P_in sign derivation (eq:pin); venue decision.
- [ ] theoretical-research: forcing-aware invariant (D3) + turbulent rank-growth theory + dimensional-regime boundaries → fill [PENDING-THEORETICAL-RESEARCH] in 04/07/08/09.
- [ ] After V1–V7 close: replace all [PENDING-CODER] with artifacts-traceable numbers (CHECKLIST 1.1), un-gate D4, adapt template to the settled venue.

## Log
- 2026-09-27 **Second pass: the 24-block audit, D18b applied, §9 numbers, README**
  (`b244bab`). `origin/agent/reviewer` == `origin/main` == `8656288`, so there is
  **no new reviewer note**; `bf05073` turns out to be my own first paper commit
  (already merged), not a review of the draft — flagged to the reviewer in case a
  different document was meant.
  **Block audit** (the START_HERE §1.1 criterion, done by whitespace-normalised
  match of all 24 paste-ready `latex` blocks against the rendered draft): **16
  verbatim, 8 not** — 1 blocked (D18a §3 energy block, `04:98–101`, awaiting
  reissue), 1 deliberately skipped (D18c block 2, stale vs W15.1/D105), 6
  differing only by the D138 re-pins. Nothing unaccounted for.
  **D18b applied to §6, §7 and the limitations** (D18b: "use this for §6, §7 and
  the limitations"). Its substance was already in §6/§7 via the newer D18c/D18d
  blocks, but **two of its sentences were in no block** and are now in the paper:
  the *mechanism* of the horizon's refinement behaviour (§6 `sec:res-error`, §7
  `sec:disc-3d`) and "rank therefore helps … up to the point where the
  representation, not the method, runs out"; plus D18b's budget clarification
  inserted *around* W15.4's phrase in §8 rather than replacing it.
  **D18b's mechanism verified, after nearly inverting it**: the artifact's
  `ratio_at_bracket` is `static/dlra`, not the reverse; read the other way the
  reduced advantage looks like it grows. Measured from `crossover_surface.json`
  vs `crossover_N128.json`, column `relative_l2`, `r=16`, `t=1`: reduced
  `0.209 → 0.159`, static `0.127 → 0.153`. Reduced converges, static degrades —
  D18b holds. Printed at 2 s.f. deliberately (no registry rows for the 4-s.f.
  values).
  **D18b's `r=43` at `N=128` value is stale** (`2.683` → artifact now
  `2.989679444793215`); not printed, and it is the second stale registry row in
  that object (`tstar_N128_r32` = its `t_star_legacy`, not its `t_star`).
  **§9's headline-numbers marker filled** now that the runs have landed
  (`≈1e-4` per Re, `4.6e-5` on the finer grid, `2.2–3.5×`, `2.3–4.0 MiB`); the
  half asking for a **POD-baseline cost ratio is unfillable** — `cost_retiming`
  times only the reduced integrator against the full-grid reference — so the
  marker was narrowed and the request sent to `coder`.
  **README.md had three now-false statements, fixed**: figures "not present yet"
  (7/7 resolve, 13 PDFs), "§6 all numbers pending coder", and the marker section
  had no counts (now: 10 `[PENDING-CODER]`: 04×4, 05×3, 06×1, 08×1, 09×1).
  `main.tex` and `references.bib` audited, nothing needed (10 `\input`s present,
  38 entries, 0 phantom citations).
  **Gates on `b244bab`:** `check_paper_builds --ref` 0 defects, 7 graphics, 65
  labels, XREF measures 33 (W7's "34" now wrong — the reviewer's to fix);
  `claims_registry` draft **55 traced / 0 untraced**, 0 uncovered; the 29
  untraced remain in the reviewer's own docs; `check_order_withdrawn` still the
  same 4 read candidates, **no new one from D18b**. Still **not compiled** — no
  TeX engine on this node.

- 2026-09-27 **D18c §6 + D18d §7 applied, numbers re-pinned, markers closed**
  (`5c9f887` + the xref-restore commit, both pushed). Seven D18c blocks
  pasted per subsection with `\subsection`/`\label` lines untouched; block 2
  (`sec:res-rank`) deliberately NOT pasted because it contradicts W15.1/D105
  (rank 1→16 over eight time units vs "budget within fifteen steps"); the
  reviewer is asked to overrule. Four D18d blocks pasted. D128's §6 sentence
  appended verbatim to the cost paragraph.
  **Re-pins from the D138 artifacts** (D138 has no DECISIONS.md section — it
  exists only as `claims_registry.py` comments, flagged): `0.649`→`0.708`,
  `1.482`→`1.598`, `0.667/1.609`→`0.728/1.720`, `2.7%/8.6%`→`2.9%/7.6%`,
  `0.15%/0.63%`→`0.19%/0.60%`, `0.939/2.526`→`0.975/2.694`,
  `1.45/1.71`→`1.38/1.69`, band `2.24–2.74`→`2.21–3.54` (printed `2.2–3.5`),
  spreads `4–26%`/`16–32%`→`0.9–6.8%`/`5.7–19.8%`, memory `2.4–4.2`→
  `2.3–4.0 MiB`. Never-write item 3 still quotes the pre-D138 values — flagged.
  B6's `1.4×` floor kept but its deriving sentence reworded (the old
  arithmetic no longer produces it: `2.24/1.26/1.32≈1.35` → `1.73` on the
  re-pinned spreads, `1.96` for the worst single configuration). B5's "two to
  four" → "down by factors of 1.6 to 2.8" (banned item 4; no registry row).
  B3's `(D120)` internal reference stripped.
  **All six `tab:div` PENDING markers closed** (TG `1.9e-14`; L2 `2.5/2.6/2.7e-14`;
  L3 `7.6e-14`; L4 `1.0e-11`) and its "all entries … by construction" caption
  corrected, since the last row is three orders above the floor. §6 now has one
  marker, deliberately narrowed to the growth-event count the records do not
  contain.
  **Figures:** D18c's mapping is STALE — all thirteen names exist on `main`
  (coder `a2cca7c`) and each of the six slots holds real, caption-matching
  content, so five slots were NOT rewired. Rewired only `fig:error` →
  `fig_crossover` (row 4: `fig_error_vs_ref` covers `t ≤ 0.1` and cannot show a
  horizon of `0.708`/`1.598`). Added `fig_div_free` to `sec:res-div` as the one
  genuine content gap (row 7), labelled `fig:divfree`. Captions rewritten for
  `fig:tg` (rank is one throughout, not `3→2→1`), `fig:error`, `fig:cost` (it
  never showed per-Re wall clock, total time or memory) and `fig:kestats` (its
  right panel is the *reference's* spectrum, full grid only). The `fig:rank` and
  `fig:svd` "generate from the records" markers are closed.
  **§7:** the ref-free blocks dropped 19 cross-references and stranded
  `fig:cost`/`fig:rank`/`fig:svd`/`tab:div`; 11 accurate pointers restored, so
  measured inbound refs into §6's labels = 32 (34 on `main`) — the W7/D18c "34"
  is now wrong and is the reviewer's to fix. Kept the D18d-B2 long-time-stability
  paragraph and the Vinograd paragraph + its marker.
  **My wording, no block supplied:** §6 intro (provenance sentence, marker
  deleted), five figure-pointer sentences, `04:266–268` (rank one from the
  outset), `05:30–32` (`ν = 2×10⁻²` from the record; the old `Re = 2π/ν²` was
  false — the TG driver computes no Re), the two `(V2)` parentheticals deleted.
  **Gates on this branch:** claims_registry PART 3 0 uncovered, PART 4 DRAFT
  53 traced / **0 untraced** (was 1); check_paper_builds `--ref` **0 defects**,
  65 unique labels, 7 graphics all resolving; check_order_withdrawn 4 candidates
  in the draft, all read (2 band false-positives, 1 compliant population caption,
  1 pre-existing `04:283` for the reviewer) and **every D122 `r*(Re)` candidate
  gone**; check_start_here SECTION 0 pass, 6/6 markers, its 2 failures are the
  reviewer's stale START_HERE numbers. **No TeX engine on this node, so the PDF
  was not compiled** — the static gate cannot prove that, and the reviewer is
  asked to compile once. 30 numbered flags in `outbox/to-reviewer.md`, including
  two registry rows now wrong rather than rounded (`tstar_N128_r32` 2.526112 vs
  2.694193556457674; `cost_ratio_min_N64` 2.2377 vs 2.208903) and the missing
  D138/D139 record.


- 2026-09-26 Batch 2 (unit C) applied — nine edits, all binding pastes
  byte-verified (whitespace-normalized substring check against
  `/tmp/opencode/order4_block_{15,16,17}.tex` and order @1323–1326):
  **05** — E1 W13 §5 lead paragraph (block_16 verbatim); E2 W14 TG setup:
  the two sentences replaced literally per order @1107 (block_17, leading
  comma → period) — consequence: the preceding setup clause is now a
  verbless fragment, flagged (m) with three options for the reviewer;
  E3a D124 eq:re-set → $Re = 2U/\nu$; E3b W12 L2 block (block_15 verbatim) +
  per-run lead naming the four `kolmogorov_*.json` stems +
  `tab:forced-params` (booktabs, `lccccl`, 14 rows) + same-steps "(200)"
  sentence; E4 L3 marker drop (reference = same stream-function
  formulation, same grid/dt/dealias policy, `orszag1971`); E5 L4
  fixed-rank-16 rewrite (fit set = IC + every fifth state of the first 100
  steps, truncated at fixed $r_{POD} = 16$; forcing on the full grid;
  re-projection at each stage boundary) + marker drop; E6 hardware closure
  (single x86_64 Linux node, Python 3.12.3, NumPy 2.5.3, thread pools
  pinned); E7 CHECKLIST-clause removal. **04** — E8 Re clause
  ($Re = 2U/\nu$, equivalently $U/(\nu k)$ at the fundamental $k = \pi/L =
  1/2$, pointer to Table~\ref{tab:forced-params}); E9 D128 §4 cost-mechanism
  sentence pasted verbatim ($\textbf{X}$ form) after "…requires no SVD." in
  the viscous-cost remark. Verification: table source keys all exist in the
  four records (N, L=2π, dt, final_time 0.1/0.1/0.1/0.05, F, U, ν, Re,
  cutoff 8, r min/init 2/2, r max 43/43/43/85, check_every 5, amplitude
  cutoff 1e-10, full/max_abs_divergence 2.58/2.66/2.49/6.22e-14, pod_rank
  16); long-run record final_time=1.0, nsteps=2000, dt=5e-4 (caption
  correct). Stale Re remains only at the two intended sites: 05:31 (TG,
  PENDING) and 04:100 (energy subsection — D18a territory, flagged (n)).
  Banned-phrase scan 04/05 clean; no hardcoded table numbers anywhere;
  tabular well-formed (15/15 rows × 5 amps). PENDING-CODER now 38 lines
  (04:4, 05:3, 06:26, 07:3, 08:1, 09:1) — all remaining markers are
  intentional holds (TG×2, results-layout, D18a, W6, rank-rule tolerance,
  W7/W8 rewrites). Flags (a)–(r) appended to outbox. Post-fetch: coder
  moved 310ac6d→f527aed (`bench_cost.py` + `cost_retiming.json` only) — a
  1-thread re-timing, self-flagged non-canonical by the coder's new
  `CANONICAL_THREADS = 2` check (full-step ratios 2.19/2.44, 2.39/2.57,
  2.26/2.26 vs the canonical 2.24/2.56, 3.47/3.64, 3.01/3.05); binding
  band kept as issued, and 05's hardware sentence corrected one→two
  threads (canonical artifact), flagged in (r). Pushed after re-fetch
  (16fa0b4); gates re-run with DRAFT_REF=agent/writer: XREF measured 34
  (as expected; the order's "39" is stale — flag (h)), PENDING-CODER
  measured 38 (04:4, 05:3, 06:26, 07:3, 08:1, 09:1 — all intentional
  holds); draft candidates 8, all known residuals (D52.5×2, D122×4 in
  07, D60×3). Next: W4–W9 (W4 blocked on TG numbers (i)/(g); W5 cost
  wording pending (s)).
- 2026-09-26 (later) Reissued order: batch 1 (units A + W15 + D130) pushed
  Merged `origin/main`@24d7700 and `origin/agent/reviewer`@b46f291 into
  `agent/writer` (de3738e) — brings D128 into the order, R162–R168, the
  re-modified `crossover_N128.json`. Read the full reissued order (1364
  lines): banned list (items 1–13), W15, D124, D128, D130; read the outbox
  in full through R168; extracted all 24 fenced blocks to
  `/tmp/opencode/order4_block_{0..23}.tex`. Applied and byte-verified
  (whitespace-normalized diff against the order's blocks): **W11** (D13
  abstract re-paste: `1.45`/`1.71` grid-convergence sentence, `2.2–2.7×`,
  `1.4×` floor — resolves R168 items 1–2), **W16.1/W16.2** (intro cost band
  + basis-claim sentence), **W2** (D14 contributions re-paste, `2.2`),
  **W10** (zero `koch2019dlra` in `paper/` except the README flag; 01:33 +
  04 repointed to `koch2007`, 03 survey sentence + cite removed, README
  Classics 9→8 + flag #5), **W15** (13 sites in 06/08/09: W15.1 saturation
  block + standalone slow-decay sentence; W15.2 `fig:rank` caption
  "Retained rank … budget within fifteen steps … three curves coincide" —
  contains "forced Kolmogorov flow" as in the binding block, flagged; W15.3
  L1 bullet (TG numerical rank one from the outset; forced rank rises to
  the budget; decay-events marker deleted, answered by the 2000-step run);
  W15.4 both "online rank adaptation" sites; W15.5 conclusion research
  question; W15.6 V2 sentence; five marker edits dropping r*(Re) items and
  "adaptive rank"→"retained rank" in the L4 marker), **D130** (item 3:
  label + stopping-rank sentence, last sentence kept exactly). Verified: no
  "saturat" outside the binding blocks; remaining "quasi-stationary" sites
  are 04:252 (descriptive, kept per site list), 07 (deferred to W8/D18d),
  and 06 L1+L4 subsections (to be replaced by D18c in W7);
  `taylor_green.json` confirms rank 1 throughout (numerical rank 1 from the
  outset) — the `3 \to 2 \to 1` text lives only in W7-replaced subsection
  text, so left untouched. 06:41 "the adaptive rank $r(t)$" left as is
  (descriptive; the gate deliberately does not match it) — flagged for
  confirmation. Next: unit C (W12–W14 in 05 + D124 + D128 §4 sentence),
  then outbox with all open flags, then W4–W9.
- 2026-09-26 Session after the reviewer's overnight restructure
  (DECISIONS now D1–D91; `WRITER_ORDER.md` R104 "supersedes every message";
  `START_HERE.md` R118; compacted outbox). Merged `origin/main` into
  `agent/writer`; the merge left stale D26-era copies of reviewer-owned files
  on my branch — reset all of `state/reviewer/` to `origin/main` (commit
  03a4600) and verified `git diff origin/main HEAD -- state/reviewer/` empty.
  Read `START_HERE.md` + `WRITER_ORDER.md` (all 702 lines) in full. Executed:
  **W1** (D13 abstract pasted verbatim, diff-verified against the order's
  fenced block), **W2** (D14 five-item contributions pasted verbatim; caught
  and fixed my own typo `$10^{278}}` → `$10^{278}$`), **W3** (D11: intro
  summary clauses (ii)–(iii) + validation sentence replaced, clause (i) kept),
  **D15** (`99.9%`→`99%` in `04_methods.tex:288`,
  `05_experimental_setup.tex:86` + its stale PENDING comment `:91`,
  `06_results.tex:133`; zero `99.9` remains in `paper/`). Pre-push checks:
  `claims_registry.py` Part 2's `99.9%` finding reads the *pushed* state
  (`git origin/agent/writer:paper/sections`) and clears on this push; Part 1
  now 14/24 — six memory rows fail because `main`'s `peak_memory.json` is the
  D52.6-era artifact (2.24/4.27/0.066) while the registry encodes D89's
  re-measured values, which I verified exist on `origin/agent/coder`
  (2.37109375/4.2109375/2.17578125/3.6328125/floor 0.09765625; one
  `rank_independence_resolved=False` at N=128 dlra, per D89) — an
  artifact-landing gap, flagged to reviewer, not mine to fix; four N=128 rows
  fail on missing `crossover_N128.json` (C2-1, known). `check_order_withdrawn.py`:
  remaining candidates all sit in sections not yet rewritten (W4–W9). While
  preparing the push, `origin/main` moved twice (dbd1075, 2cbcab2) — merged
  both (83063c2, 456367b), each time resolving conflicts by resetting all of
  `state/reviewer/` to `origin/main` (verified empty diff). Latest state
  absorbed: D89 memory artifact NOW ON MAIN (registry memory rows pass;
  `+2.37`/`+4.21 MiB`, floor `0.098`, overhead variation resolved at N=64,
  NOT resolved at N=128 — so neither "flat in rank" nor "grows with rank" is
  supportable at N=128); cost band `2.24–2.74×` quoted to one sig fig,
  pessimistic floor `1.4×` (D91/R128); D18c §6 supplied (7 blocks) with the
  figure mapping (use the 8 existing figures; no Taylor–Green figure exists;
  `fig_div_free` goes into `sec:res-div`; use PDFs); D18d §7 supplied (4
  blocks); R130 hedges (window/Re-invariance and the r=16 saturation contrast
  are N=64-only — never "at every grid"); R132 three `10^{-14}` sites (W4:
  `04_methods.tex:275`; W7: `06_results.tex:105` + `tab:div` caption); R136
  final energy population `1.3e-4`–`4.9e-4`, worst case = SP-DLRA itself;
  `crossover_N128.json` still not on main (registry 29/33, 4 N=128 rows).
  Re-verified: abstract + contributions still byte-identical to the current
  order's D13/D14 blocks. Pushing W1+W2+W3+D15 as the first reviewable unit;
  next W4 (§3) and W5 (§4).
- 2026-09-25 Worktree + branch created as part of the 5-agent scaffold
  (see `PROTOCOL.md`).
- 2026-09-25 Paper drafted end-to-end. All 10 sections + main.tex +
  references.bib (38 verified entries) + README in `paper/`. D4 claim
  rewritten to the reviewer's binding R5d wording in 01 (short) and 03
  (full), each with a FLAG-D4 comment; barred phrases verified absent from
  body text. Wrote 07_discussion, 08_limitations, 09_conclusion. Consistency
  pass: no natbib, all cited keys verified against the bib, all refs defined,
  no duplicate labels, braces balanced, I1–I4 tags aligned with 04 (fixed
  energy-tag I3→I2 in 07/09 and the cost subsection in 06). Fixed the 06
  figure-caption bracket bug and the `orszag1971` key typo. Sent outbox to
  coder (scheme confirmations, I1–I4 numbers, 6 figure data sets, tab:div,
  step-0 per R5m, R5k/R5l addenda), to writing-research (venue doc with
  cited deadlines, refs reconciliation, Osepko ID), and to reviewer (draft
  review request, P_in sign sanity check, D4 wording confirmation). No merge
  request yet.
