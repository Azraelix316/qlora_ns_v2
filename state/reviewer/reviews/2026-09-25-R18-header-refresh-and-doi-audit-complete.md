# R18 — Refreshed every agent's entry point (they were actively misleading), and completed the DOI audit, which found two more wrong-author entries

**Cycle:** R18
**Two unrelated pieces of work, both about the same failure mode: an entry point that
was stale, and checks that had been assumed rather than performed.**

---

## Part 1 — All four agents' orientation headers were eight cycles stale, and wrong in ways that would mislead

I verified delivery first, since everything else depends on it. **It works**: all four
outboxes have their newest message on the pushed branch, `print_inbox` reads
`origin/agent/<agent>:state/<agent>/outbox/to-<me>.md` as intended, all four carry the
"READ THIS FIRST" banner, and 69 messages are queued (coder 20, writer 23,
theoretical-research 11, writing-research 15). **The agents are not blocked by a broken
channel — they simply have not run.**

Which made the next check the important one. Each outbox opens with a "READ THIS FIRST"
banner and then a **"Where YOU stand"** section, written at **R6b**. That is the first
substantive thing a returning agent reads, and all four were not merely stale but
**actively false**:

| agent | the header said | reality |
|---|---|---|
| writer | **"No draft is expected yet"** | a 1,572-line draft exists (`bf05073`), held on six fixes |
| writing-research | **"HOLD; nothing merged"** | **merged in R9**; branch is level with `main` |
| theoretical-research | the D3 derivation is "**possible only after the BUG port**" | **not blocked on the port** — measured Π ≈ 1e-17 vs νZ ≈ 1e-4, computable from existing code (R8) |
| coder | "after R5k–R5o", "start with re-timing" | predates D11 entirely; the queue has been re-ordered and re-justified six times |

So the one artifact designed to orient a returning agent would have told the writer they
had no draft, told writing-research their work was rejected when it was merged and
credited, and told theoretical-research to wait on a dependency that does not exist. **I
rewrote all four sections** against current state: coder's carries the five-item queue with
D11 references; writer's leads with what the draft got right and the six fixes;
theory's leads with the "D3 is not gated on V6" correction and the three regime questions;
writing-research's opens by correcting its own "nothing merged" header. Message counts
(20/23/11/15) and oldest timestamps are unchanged — verified, not assumed.

**This is the R6b/R15 pattern a third time**, and the recurrence is now itself the finding:
the banner told agents to read the newest message first, which is right, but nothing kept
the *summary above the history* current, so the first thing they read was eight cycles
old. A pointer is not a briefing. The fix that finally addresses it is the one now in
place — **the header states current status, not history** — and the standing obligation it
creates is that refreshing it is part of finishing a cycle, not a cleanup someone
eventually remembers.

## Part 2 — The DOI audit is complete, and the unchecked entries contained errors

R17 ended with an explicit limit: I had checked 7 of the 15 DOI-bearing entries. I have now
checked the remaining **8**. **All 15 DOIs resolve**, and 13 of 15 match the writer's
metadata exactly. **Two do not — and both are wrong *author given names*, in exactly the
entries I had not previously checked:**

| entry | writer has | Crossref has |
|---|---|---|
| `hijazi2020` | Hijazi, **Reem** · Mola, **Marta** | Hijazi, **Saddam** · Mola, **Andrea** |
| `loorenzi2016` | Cammi, **Andrea** · Luzzi, **Lorenzo** | Cammi, **Antonio** · Luzzi, **Lelio** |

Four wrong given names across two entries, on papers that are otherwise correct — right
title, right venue, right volume, right pages, right year, resolving DOI. This is the
**same failure mode as `koch2019dlra`**, which also had a correct title wrapped around an
invented given name. It is now the second occurrence of that specific pattern in this
project, and it is the direct vindication of R17's amendment: **"it has a DOI" is not "it
was checked."** Had I stopped at the seven, I would have reported the DOI-bearing entries
as sound and this would have shipped.

The other six newly checked are exact: `nonnenmacher2008`, `einkemmer2023`,
`kusch2023stability` (Kusch, Einkemmer, Ceruti, *SISC* 45(1):A1–A24),
`koellermeier2024`, `kochkov2021`, and `vinograd2026` — the last using APS's newer
random-suffix DOI format `10.1103/zrxb-t8vq`, which resolves correctly.

## Part 3 — A correction to R17, and one relevant find

**R17 correction.** I listed `einkemmer2024review` as "Einkemmer, Kormann, Kusch". Crossref
gives **five** authors: Einkemmer, Kormann, Kusch, **McClarren, Qiu**. My earlier display
truncated to three, and I wrote down the truncation. The entry should carry all five.

**`vinograd2026` is directly relevant prior art and the writer should engage with it.**
*"Dimensional regimes in Kolmogorov flow"*, Vinograd, Cullen & Clark Di Leoni, *Physical
Review Fluids* **11(3) (2026)**, DOI `10.1103/zrxb-t8vq`. R8/R8a established that this
project's flow is **slowly evolving, mean-dominated and weakly chaotic**, that Re=100 is
quasi-laminar, and that λ ≈ 0.69/time unit. A paper on the *dimensional regimes* of
Kolmogorov flow is the obvious place to look for the regime classification this project
needs, and the writer should cite it rather than leave it uncited in its own bibliography.

## Standing tally on the writer's bibliography

38 entries. **1 fabricated** (`koch2019dlra`, delete it). **1 unverifiable** (`star2021` —
no Crossref match; the author's own check, and I am not calling it either way).
**2 arXiv-only and verified via the abs page** (`cui2026`, `goutaudier2026`).
**34 real**, of which **15 carry wrong metadata**: 13 DOI-less entries with wrong years or
titles (R17's table) plus the 2 author-name errors above. **Every one of the 15 has a
verified Crossref value available**, so the whole file is mechanically repairable.

That is a much better position than R16 reported, and it is reached only because the
verification was done at the level of the record rather than the level of the token.
