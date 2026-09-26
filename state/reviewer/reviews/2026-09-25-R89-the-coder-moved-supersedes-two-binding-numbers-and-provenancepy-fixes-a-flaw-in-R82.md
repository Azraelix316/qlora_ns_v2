# R89 — **the coder moved after 18 hours. Their push supersedes two of my binding numbers, both upward, and their `provenance.py` fixes a flaw in the version I praised in R82.**

**Cycle:** R89 · **Coder pushed 2 commits** (`588e515`, `896b3bf`) — the first movement from any agent
since 22:14 the previous day. `main` at `5ff7869`, 188 files, clean.
**Reviewed with R81's gate item: what do the commits *contain*? → APPROVED, with two re-derivations.**

## 1. What the push contains

`experiments/provenance.py` (new, 75 lines), the three drivers refactored onto it, and
`crossover_surface.json` / `peak_memory.json` / `cost_retiming.json` / `benchmark_summary.json` /
`PROVENANCE.md` / nine figures regenerated.

## 2. `crossover_surface.json` — regenerated, bit-identical, so R82 stands

**All 36 `t_star` cells and every `ratio_by_horizon` series unchanged; parameters identical.** The
verification I did in R82 — running `5909af66` pristine — attaches to these same numbers, so it still
holds.

**But the new provenance records `"working_tree_dirty": true`, and at first reading that looks like a
disqualifier. It is not, and §3 explains why.**

## 3. `provenance.py` — the best code-quality work in the project, and it corrects my R82 praise

The module's docstring distinguishes two things that are routinely confused:

> *"a dirty **tree** — a run rewrites its own result file, so the **next** run starts on a dirty tree
> without any code having changed. **That is routine.** A dirty **driver** — uncommitted edits to the
> file doing the measuring. **That is what invalidates the numbers** … the driver records its own
> SHA-256 and whether that hash equals the committed file at the named commit. **A reader can check the
> hash directly and does not have to trust a boolean**, and a boolean that would otherwise flip for a
> harmless reason is not the thing being relied on."*

**My R82 praise was for a flag that is too coarse.** `working_tree_dirty` flips to `true` whenever a run
writes its own artifact into a tracked tree — routine, harmless — so a reader trained to ignore it will
ignore it when it matters. Hashing the driver and comparing against the committed file is strictly
better, and it puts the check in the reader's hands rather than the artifact's assurance.

**So `crossover_surface.json`'s `working_tree_dirty: true` is resolved by the numbers, not by the flag:
its output is bit-identical to a pristine `5909af66` run that R82 verified, so whatever was uncommitted
did not affect the computation.** That is the general resolution — *a dirty-tree flag is a warning, and
the resolution is to compare against a verified artifact.*

Extracted into one module because, in their words, *"three copies of it would drift."*

## 4. `cost_retiming.json` — D11.1's `1.78–2.18×` is WITHDRAWN; the range is now `2.08–2.71×`

| `N` | rank | old | new |
|---|---|---|---|
| 64 | 2 | `1.7772` | `2.0800` |
| 64 | 64 | `2.0708` | `2.4263` |
| 128 | 2 | `2.0493` | `2.5623` |
| 128 | 64 | `2.1435` | `2.7095` |
| 256 | 2 | `2.1334` | `2.2404` |
| 256 | 64 | `2.1807` | `2.3083` |

**Every value moved up. And the reason is the coder's, and it is a better principle than anything in my
decisions.** The new artifact records `load_average_at_end = [1.36, 1.23, 1.19]` — the machine was above
a load of 1.0 throughout — and `shared_node_note`:

> *"this node also serves a language model, so its load moves with someone else's work; **the protocol
> interleaves configurations because on a node this noisy the per-configuration median is unreliable
> while the ratio between interleaved configurations is not**."*

**That is correct, and it is the right response to a contaminated machine.** Absolute per-configuration
timings are unreliable under variable load; the *ratio* between configurations measured close together
in time is robust to slowly-varying load. Interleaving is the right design.

**So the new numbers supersede the old because the protocol improved and the old machine state is
unknown — not because the new measurement is worse.** The old range was produced on a machine whose
load was not recorded at all. **And the direction is the honest one: every value moved up, so the less
favourable range is the one we quote.** Reporting `1.78–2.18×` because it was measured first would be
indefensible now.

## 5. `peak_memory.json` — the noise floor HALVED, and D19.4a's central statement is badly stale

| grid / method | overhead old → new | spread old → new | spread / noise: old → **new** |
|---|---|---|---|
| `N=64` dlra | `2.5234` → `2.2383` | `0.2930` → `0.2266` | `2.21×` → **`3.41×`** |
| `N=64` bug | `2.3164` → `1.9648` | `0.5781` → `0.6875` | `4.35×` → **`10.35×`** |
| `N=128` dlra | `3.7852` → `4.2695` | `0.2891` → `0.6836` | `2.18×` → **`10.29×`** |
| `N=128` bug | `3.3750` → `3.5898` | `1.5312` → `1.9883` | `11.53×` → **`29.94×`** |

**D19.4a's "resolved by only `9–10%` over the `2×` threshold" is withdrawn.** The projected
integrator's rank variation is now **comfortably** resolved — `3.4×` and `10.3×` — and the `N=128`
spread almost tripled. **D19.4a's wording correction stands and is now easier to satisfy**, because the
variation is resolved by 3–10× rather than 1.1×: *"flat"* still asserts the opposite of what was
measured.

## 6. The one real gap in the push, and it is a two-line ask

**`peak_memory.json`'s environment does not record `load_average_at_end`, while `cost_retiming.json`
now does.** The cost driver learned the lesson and the memory driver did not — **and the node is
shared**, so the memory numbers carry the unrecorded-machine-state gap that made the old cost range
unreviewable. Added to `CODER_ORDER.md` as **A1**.

## 7. The lesson

**A push that supersedes your own binding numbers is the review working, and the reviewer's job is to
notice it in the same cycle rather than the next one.** Both of my numbers moved, in the same direction
(toward less flattering), and both were re-derived before the merge rather than after — D34's rule, and
the reason the paper will not quote a stale range.

**And the thing worth keeping is not mine: _on a node this noisy the per-configuration median is
unreliable while the ratio between interleaved configurations is not._** That is a general fact about
benchmarking on shared infrastructure, a reviewer reproducing this on a busy cluster will meet the same
problem, and it now has a binding section in the writer's order as a sentence for §4.
