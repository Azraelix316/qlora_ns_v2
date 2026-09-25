# R78 — I verified every standing instruction I issued from memory, and the two phantoms were the only ones. But my *audit method* had a gap, and I found it by being wrong.

**Cycle:** R78 · No agent pushed. `main` at `5ea49c6`, 177 files, clean.
**R77's lesson was "measure the files, don't trust my own list." R77's own two order documents were
written from memory. So I measured them.**

## 1. The result: all twelve coder items and all twelve writer prohibitions are still needed

Every item in `CODER_ORDER.md`'s Tier 3, checked against `origin/main`:

| item | verified state |
|---|---|
| `peak_memory.json` still asserts a `1.531 MiB` BUG spread with `rank_independence_resolved: true` | **still true** — spreads `[0.578, 1.531]`, flags `[True, True]` |
| the `crossovers` block is correct (`t* = 0.649`) | **still true** — and it is not a defect |
| `max_scaled_energy_balance_residual` absent per method from the baselines artifact | **still true** |
| `error_columns` still documents `relative_l2_oracle_mean` as the oracle mean | **still true** |
| the crossing test's fixture still splits the two columns | **still true** |
| the corrected surface is still board-only | **still true** |
| the never-yields rank is still bracketed 32–43 | **still true** — ranks tested `[2, 4, 8, 16, 32, 43]` |

And the writer's prohibitions: the static-POD qualification is still required (**four** `pod` runs
diverge and others do not), the forcing is still the single-mode shear, the fitted-law bar is still
needed. **So the only phantom instructions in this project are the two I found and withdrew in R77
— `koch2019` and `temam1977navier` — and there are no others.**

**That is worth stating plainly, because it means the instruction lists can now be trusted, and
future cycles do not need to re-verify them.**

## 2. And my *check* was wrong first, which is the part that matters

My first pass reported **P1 "FALSE — no fitted `c·r^p`"** as though the prohibition were
unnecessary. **It was my boundary condition, not the file.** I delimited the "operative" region as
everything before `## 6`, and found the two R39/R50 fitted laws at lines 211 and 214.

**Those lines are §1.1a, whose heading is "Every fitted form is void — and why, which is the useful
part."** They are the *void-list* — a table of withdrawn laws each with the reason it is void. That is
exactly where they belong, and `PAPER_BLUEPRINT.md`'s prohibition list is the third such region.

**So `CLAIMS.md` has two legitimate "withdrawn" regions, §1.1a and §6, and my R70 sweep knew about
only one.**

## 3. Why that matters for the method, not just for this cycle

**R70's sweep — "flag any line containing a withdrawn token that does not also contain a withdrawal
marker" — would flag both void-lists if it ran on the fitted-law tokens**, because the §1.1a table's
justification column reads *"later found in-sample and starvation-affected"* and *"measured on
`bc35666`, whose baseline window ends at the evaluation time"* — **neither contains any of my
markers.** The reason no false positive actually occurred is luck: **the fitted-law tokens were never
in R70's list**, because they were correctly void-list entries rather than operative claims.

**The refined rule: a sweep needs to know where the file's legitimate withdrawal regions ARE, not
just what a withdrawal marker looks like.** A file that catalogues what it has rejected is a *good*
practice — `CLAIMS.md` §1.1a and §6 and the blueprint's §7 are three of them — and **a reviewer
auditing such a file has to distinguish "this number is void, here is why" from "this number is my
claim" by structure, not by keyword.** A file with one withdrawal region needs a different check from
a file with three.

**And the honest note: my check was wrong in the direction that would have produced a *false
retraction* of a standing bar.** That is the more dangerous direction, because it looks like
housekeeping. **I have caught six real errors this project and one false one, and the false one was
mine, in the method rather than the content.**

## 4. What I am doing about it

**I am not changing the files** — §1.1a is correct and should stay. **I am recording the structural
fact so the next sweep is not built on a keyword list:** `CLAIMS.md`'s withdrawal regions are **§1.1a
(void-list, with per-entry reasons)** and **§6 (prohibition list, with the barring decision)**;
`PAPER_BLUEPRINT.md`'s is **§7**; `WRITER_ORDER.md`'s is **§3**; `CODER_ORDER.md` states prohibitions
inline. **A sweep over any of these must treat a hit inside those regions as legitimate by
construction, and a hit outside them as operative.**

## 5. The lesson, and it is the second-order version of R77's

R77: *measure the files, don't trust your own list.* **R78: when you build a mechanical check over
your own prose, the check's boundary conditions are as much a part of the finding as the tokens are** —
and **the first time you run a new check, expect it to be wrong in the direction that looks like
housekeeping.** A check that returns "FALSE" on a bar you know is load-bearing is not a discovery; it
is a bug in the check, and the cheapest way to tell the difference is to read the region the hit came
from before believing it.
