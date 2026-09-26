# R114 — **I undid my own R104 fix. The index went stale a second time, and this time it instructed the writer to write a claim I had already withdrawn. A gate that keeps a document fixed is not the same as fixing it once.**

**Cycle:** R114 · No new pushes. `main` at `5a4c254`, 213 files, clean.
**Found by checking my own deliverable against the property I claimed for it, rather than assuming it still held.**

## 1. What regressed

R104 rebuilt `WRITER_ORDER.md` because it was 508 lines with five colliding `## §4` headings, two sections each
claiming to be the highest-priority item, and the one-screen index **buried at line 98**. The rebuild put the
index first, gave the order `W1`–`W9`, and moved the detail to `D1`–`D14` below a `## DETAIL` heading.

**Since then I have appended a section every cycle — D67, the checker note, D68, D70, D74 — and I appended
them to the *end*, without touching the index.** The file is now 646 lines. The index was still at the top, so
the *ordering* property survived. **The *accuracy* property did not.**

**And the failure is worse than the original one, in a specific way. R104's lesson was "the index was itself
stale, which is worse than a long document", because the writer trusts it. This time the staleness was not an
omission — it was an instruction to write something false:**

> `W8 | §7 discussion | Four honest gaps, stated as gaps. | … never-yields rank **bracketed 32–43** …`

**D74 retired exactly that claim nine cycles ago.** The never-yields rank is not bracketed between 32 and 43; it
is the dealiasing ceiling of each grid — `43` at `N=64`, `85` at `N=128`. **So the index was not merely
incomplete, it was directing the writer to print a sentence I have withdrawn, in the section where I had just
delivered its replacement.**

`W7` was stale in the ordinary way: it listed the `N=64` horizons and the saturation mechanism and said nothing
about the grid result, because it predates D68 and D74 entirely.

## 2. Three further defects, found only because I checked rather than assumed

Verifying the rebuild surfaced problems I had not introduced this cycle:

1. **The header lies about its own contents.** It read *"`D1`–`D14` behind it are the detail"* while the IDs ran
   `D1`–`D18b`. A reader who trusts the range would conclude four detail sections do not exist.
2. **The pre-send check line was missing entirely.** I had added a "run `claims_registry.py` before you send me a
   section" instruction in an earlier cycle with `t.replace(anchor, …)` **and no assertion**. The anchor text had
   changed, the replace silently no-op'd, and **I did not notice for eight cycles.** The instruction existed only
   in the D16 detail and in an outbox message, never in the document the writer is told to work from.
3. **A stray `## D` heading with an empty ID**, left by an earlier bulk rename.

**Defect 2 is the one worth generalising: an unasserted string replace is a silent no-op, and in a document
nobody re-reads, a silent no-op is indistinguishable from success.** Every other edit I have made this cycle
carried an `assert anchor in t` first. That one did not, and it cost eight cycles of an instruction that was
supposed to be in the writer's first screen.

## 3. The fix, and the asymmetry that makes it right

- `W3` gains the "never say 43 without saying which 43" rule (D74.4).
- `W4` gains the full-PDE residual instruction (D70).
- `W7` gains the grid result: `t*` = `0.939` / `2.433` at `N=128`, the `1.4456×` / `1.6424×` ratios, and the
  never-yields-rank-is-the-ceiling result.
- `W8` has the withdrawn "bracketed 32–43" claim **replaced**, with an explicit *"Do NOT write 'bracketed between
  32 and 43'; that is withdrawn (D74)."*
- The pre-send check is restored **as an action line in the order**, not as detail.
- The lookup tables — the three load-bearing sentences, the thirteen prohibitions, the file locations — move
  below a `## REFERENCE` heading, because they are lookup, not order.

**The order now occupies the first ~36 lines and is the whole truth. The detail is 650 lines and is reference.**

**That asymmetry is the point and it is the opposite of what I have been doing.** For four cycles the *detail*
grew and the *index* did not, which is precisely how an index goes stale. Now the detail grows freely and the
order is fixed at one screen — **so growth in the evidence can never again silently invalidate the instructions.**

## 4. The gate this cycle adds, because fixing a document once is not the same as keeping it fixed

`CHECKLIST.md` §1.14: **every cycle, grep the order region of each agent's order document for claims that later
decisions withdrew.**

This is mechanical and it is exactly the check that would have caught this. The withdrawn claims are enumerable —
D29's `1.26`/`2.44`, D56's `N=128` multipliers, D60's `1e-14`, D74's "bracketed 32–43", D52.5's `1.78–2.18`, the
four barred novelty claims — and each has a decision that retired it. **A one-line grep per withdrawn claim over
the first screen of the order document is a five-second check, and its absence is why a withdrawn instruction sat
in the writer's first screen for nine cycles.**

**The general form, and it is the same shape as everything else in this project: an instruction document is
itself an artifact with claims in it, and it needs the same treatment as any other — a population, a check, and
a gate. I have been running the registry over the *paper* and applying no check at all to the document that
instructs the writer about the paper.**
