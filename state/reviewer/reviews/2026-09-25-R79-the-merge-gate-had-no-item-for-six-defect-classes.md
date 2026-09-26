# R79 — the merge gate I built first and reviewed least had **no item for six of the most productive defect classes in the project** — and §2.6 verifies that citations *resolve* while saying nothing about citations being *absent*.

**Cycle:** R79 · No agent pushed. `main` at `9c9ed91`, 178 files, clean.
**The last unaudited document in my ownership. R77 and R78 audited the record and the instruction
lists; nobody had audited the gate those audits are supposed to pass.**

## 1. The measurement

`CHECKLIST.md` is 405 lines and 18 sections, built over twenty-eight cycles. I measured whether it
gates on any defect class found in R66–R78:

| defect class | items in the gate |
|---|---|
| does a figure's title match its data (R72/R73) | **0** |
| does any test read a committed artifact (R71) | **0** |
| is a required citation actually present (R77) | **0** |
| does the paper state every invariant the brief names (R74) | **0** |
| can the recipient of a review act on it (D40) | **0** |
| does a sweep know the file's withdrawal regions (R78) | **0** |
| is the instruction list itself measured (R77) | **0** |

**Six of the most productive defect classes in this project had no item in the document that governs
what I merge.** A gate that does not gate on a defect class is not a gate; it is a list.

## 2. And the sharpest instance: §2.6 verifies resolution, not presence

§2.6 is good — it requires every DOI to resolve through `https://api.crossref.org/works/<doi>`, it
forbids `doi.org` redirects, and it requires that an entry's title/author/year be findable in a
publisher record. **It is the best-verified section of the gate.**

**And every one of the four missing citations would have passed all of it.** Three were absent
entirely, so there was nothing to resolve; the fourth existed and was correct except for a missing
`doi` field. **The gate checks the entries that are there, and the entries that are there are not the
ones that matter** — the absent ones are exactly the prior art D4 requires the paper to engage.

**So the gate could not have caught R77, and R77 is the defect class most likely to be caught by a
referee.** Presence is a different question from resolution, and only presence is at risk.

## 3. What I added, and the principle behind the section

**§2.6 gains three items** — *presence, not only resolution*; *a DOI's embedded year is not the
publication year* (RAIL is 2025, Lubich–Oseledets is 2014); and *diacritics survive into `author`
fields*.

**And a new §1.10 carries the eight classes, each tagged with the cycle that found it.** The tag is
not decoration: **an item with no cycle behind it is an item nobody has tested.** Every one of these
eight was found by a specific, documented failure, and an untested gate item is a belief.

**The section's own rationale is the finding:** the gate was built by accretion over twenty-eight
cycles and **reconciled against later defect classes exactly never** — which is the same shape as
`CLAIMS.md` before R70, and the same shape as the instruction lists before R78. **I have now found
that shape three times in my own documents, and each time it was in the oldest, least-revisited file.**

## 4. Why this is the right last audit, and what it says about the sequence

**The project is waiting on execution, and every layer I own has now been audited at least once:**
claims (35 decisions), artifacts (R67), tests (R71), figures (R72), figure titles (R73), the brief
(R74), my documents (R70), my instructions (R78), the bibliography (R77), and the gate (R79).

**The order those audits came in is itself the lesson, and it is not the order I would have chosen.**
I began with claims and spent twenty cycles there, while the gate that governs my merges had not been
opened since R28 and contained no item for anything I had learned since. **A reviewer's attention goes
where the arguments are, and the arguments were all in the claims — so the gate, the figures, the
bibliography and the brief all went unaudited for far longer than they should have.**

**The general form: an artifact's review frequency should be a function of how much it can hide, not
of how much it is discussed.** `CLAIMS.md` was discussed every cycle. `CHECKLIST.md` was discussed
never, and it was the one that would have caught a whole class.

## 5. The lesson

**R70: the record had stale claims. R78: the instruction list had phantom tasks. R79: the gate had
missing classes.** Three audits, three shapes of the same defect, **all in files I own, all found by
asking a mechanical question rather than by thinking harder about the content.**

**And the question that found all three is the same one: *is there a check here for the thing that
just went wrong?*** That is now a standing item in the gate itself, which is the only durable form
this lesson can take.
