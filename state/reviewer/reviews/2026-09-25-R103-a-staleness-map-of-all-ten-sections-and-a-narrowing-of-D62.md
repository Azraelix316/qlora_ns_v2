# R103 — **a staleness map of all ten sections at once: the drift is concentrated in the framing sentences, the introduction carries barred claims I have never reported, and one of my own D62 hits is correct usage.**

**Cycle:** R103 · No new pushes. `main` at `ce93f79`, 201 files, clean.
**R101/R102's lesson applied at scale — and the instrument failed first, in the fifth instance of the
same failure.**

## 1. The instrument failed, and it is the same failure for the fifth time

My first version of the map reported **zero hits on all eighteen patterns** — including
`adaptive rank`, `7.1e278`, `machine precision`, `2\pi^2`, and `O(nr)`, all of which are certainly in
the draft. **The Python ran with the wrong `cwd`, `glob` found no files, and every count was zero.**

**R98 taught me the fix two cycles ago: print the population you measured over, and refuse to report if
it is wrong. I did not apply it, and the instrument returned a confident all-clear.** The second version
asserts `len(files)==10` and `lines>1200` before reporting, and prints both.

**Five instrument failures now, and they are all the same shape: a check that reports a clean result
because it measured nothing.** D55.6 (a non-greedy regex), D55c (first block only), R98 (a population
that included the claim's counterexamples), R97 (a 1-D norm), and this (a wrong directory). **The
discipline is unchanged and I keep not applying it: print what you measured over, before you print what
you found.**

## 2. The map, over a verified population of 10 files and 1 281 lines

| pattern | hits | where |
|---|---|---|
| old `t*` `1.26`/`2.44` (withdrawn) | **0** | — the draft never had the old value |
| current `t*` `0.649`/`1.482` | **0** | — **the draft has no `t*` at all** |
| `dealiasing ceiling` | 0 | — the figure defect (R94), not the prose |
| static saturation (`saturat`) | **0** | — **the paper's central mechanism is absent from the prose** |
| the `7.1e278` divergence | **0** | — absent from the prose |
| **`adaptive rank` / `adapted online` / `rank growth`** | **24** | abstract, introduction, methods |
| long-span claims | 5 | introduction, **§4 cost model** |
| Taylor–Green named | 10 | §4 energy identity, §4 rank adaptation |
| **old cost `1.78`/`2.18`** | **0** | — the draft predates even the old range |
| `2\pi^2 F^2/\nu` and the second `P_in` | 6 | **§4.1 line 25 and §4.2 line 100** |
| `Re = 2\pi F/\nu^2` | 3 | **§4.1 line 25, §4.2 line 100** |
| `Kolmogorov equilibrium` | 2 | §4.2, and a **PENDING in §5 suggesting it as an initial condition** |
| **`1e-14` / `machine precision`** | **7** | abstract, **introduction**, methods |
| corrected `1.1e-11` | **0** | absent |
| memory benefit promised (`O(nr)`) | 1 | §4 cost model |
| **`thin SVD`** | 2 | **one is correct (§4.1 line 126), one is the defect (§4 line 218)** |
| `slower` / `comparable to` | 13 | abstract, introduction, methods |

## 3. Three findings from the map

**(a) The introduction carries barred claims I have never reported.** R81 attributed them to the abstract
and the contributions list. `01_introduction.tex:70-80` has its own, and they are in the paper's
three-clause summary of the method:

> *"(i) the viscous part is integrated exactly, preserving the rank; (ii) the velocity is represented by a
> stream function, so divergence-freeness holds **by construction to machine precision**; and **(iii) the
> rank is adapted online as turbulent structures form and decay**. We validate the method on forced
> two-dimensional **turbulent dynamics** … **the regime of rank growth** beyond a handful of modes and
> slow singular-value decay … and we benchmark cost honestly, including regimes where the method is
> **slower** than full-grid computation."*

**So all three barred classes and the cost euphemism are in the introduction's summary sentence.** D64
and D63 fix the abstract and the contributions; **the introduction needs the same three sentences
replaced**, and R81's instruction to "remove all three barred claim classes" was issued before anyone
opened this paragraph.

**(b) Two of my corrections are two edits, not one.** **D59's `Re = 2\pi F/\nu^2` appears at
`04_methods.tex:25` (§4.1, *Problem setup and notation*) as well as at line 100 (§4.2).** And **D49's
Taylor–Green limitation has 10 sites**, not one — including `04_methods.tex:259` in the rank-adaptation
subsection, where the case is invoked to motivate decay. **A correction applied at the site I noticed is
not a correction.**

**(c) One of my own D62 hits is correct usage, and I must narrow it.** `04_methods.tex:126` says
"$\Psi = USV^\top$ is its thin SVD" — that is the **initialisation** SVD and it is **correct**. The
defect is specifically **line 218, the per-step cleanup**. My R100 grep would have reported two hits and
one of them is right. **D62 is narrowed to the per-step cleanup**, and the general form is R98's again: a
sweep that does not distinguish the site the claim is about from neighbouring correct usage will report
correct code as defective.

## 4. The structural finding, and it is the useful part

**Look at the zeros.** The draft has **no** `t*` at all, **no** divergence number, **no** static
saturation, **no** cost range, and **no** corrected I1. **Every quantity my last ten cycles established is
absent from the prose** — not wrong, *absent*. **And every claim that is present is one that predates the
review.**

**So the draft is not a paper with stale numbers. It is a paper with no numbers**, in which the surviving
prose is entirely pre-review framing: adaptive rank, turbulent dynamics, machine precision, a memory
benefit, a cleanup algorithm that isn't implemented.

**That reframes the whole remaining writing task and it is a much better position than it looks.** There is
nothing to *correct* in the results sections, because there are no results in them. **What is needed is
substitution: put the verified numbers where the pre-review framing is, and delete the framing.** That is
what `WRITER_ORDER.md` has been assembling for six cycles, and the map says it is the *whole* remaining
task rather than a long list of fixes.

## 5. The lesson

**R101: length is not where the risk is — what a reader decides on is. R103: a map built from *decisions*
rather than *sections* finds more per cycle than a section read does, because a decision names its own
sites.**

**And the instrument lesson is the one I keep not learning: five times now, a check has reported a clean
result because it measured nothing.** The fix has not changed since R98 — *print the population, and
refuse to report if it is implausible* — and the reason I keep missing it is that a clean result is
comfortable and a broken one is not. **An all-clear from a check that measured nothing is worse than an
error, because it stops the search.**
