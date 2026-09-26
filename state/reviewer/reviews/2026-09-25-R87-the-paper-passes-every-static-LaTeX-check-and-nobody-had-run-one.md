# R87 — **the paper passes every static LaTeX integrity check, and nobody had ever run one. Plus: `\bibliographystyle{plain}` is wrong for both D5 venues, and there is no venue template.**

**Cycle:** R87 · No agent pushed. `main` at `4a4ac0d`, 186 files, clean.
**A positive verification, which is rarer than the corrections — and the test that would have caught
R84 costs three seconds.**

## 1. Nobody has compiled the paper, and this node cannot

**No LaTeX toolchain is installed** — `pdflatex`, `latexmk`, `tectonic`, `xelatex` are all absent.
So there is no evidence the paper compiles, and no way to establish that here. **Stated plainly
rather than left as an assumption.**

**But the paper is not structurally broken, and that is checkable without a compiler.** I ran every
static invariant a build would check first:

| check | result |
|---|---|
| `\bibliography{references}` points at `references.bib` | **yes** |
| distinct `\cite` keys across all ten sections, resolved against the bib | **36 keys, 0 unresolved** |
| `\input` targets exist | **10 / 10** |
| `\label` defined / `\ref`,`\eqref` used | **63 / 133, 0 dangling, 0 duplicate** |
| brace balance per file | **balanced in all 11** |
| `\begin`/`\end` environment pairing | **balanced in all 11** |
| inline/display math parity | **even in all 11** |

**That is a well-built document: 133 cross-references with no dangling target and no duplicate label is
not an accident, and 36 resolving citation keys means the citation apparatus is sound.**

**The honest summary is two-part: the static checks pass, and the build itself is unverified and
unverifiable on this node.** The one class of error a build catches that the static check cannot is
package/class availability — see §2, where that is exactly the problem.

## 2. The real finding: the paper is not in a venue's format, and D5 already chose the venue

D5 settled **SISC/JCP rolling** over ICML/NeurIPS 2027. The document is:

```latex
\documentclass[11pt]{article}          % with comments suggesting icml2027 / neurips_2027
\bibliographystyle{plain}
\usepackage[margin=1in]{geometry}
```

**Three concrete mismatches, and the only "venue template" hits in the file are inside `%` comments.**

1. **No venue class.** SISC ships a SIAM class; JCP is Elsevier and wants `elsarticle` (or the CAS
   `sc`/`els` variants). **`article` with 1-inch geometry matches neither**, so the paper will not meet
   either target's formatting at submission.
2. **`\bibliographystyle{plain}` is wrong for both.** `plain` emits **numbered** references
   **sorted alphabetically by author**. SISC wants numeric in citation order; JCP wants **author-year**.
   **`plain` matches neither** — it is the one style that is simultaneously wrong in ordering and wrong
   in label form.
3. **`natbib` is not loaded**, which JCP's author-year style requires.

**None of this is a science problem and all of it is a submission problem.** Two of the three are a
one-line change each once the venue is fixed, which D5 has already done — so this is queued execution,
not an open question.

**Two bib entries are never cited** (`kraichnan1967`, `leray1934`). BibTeX drops uncited entries
silently, so this is harmless — noted only because "harmless" should be checked rather than assumed.

## 3. The connection to R84, and it is the useful part

**R84 was: "the paper's related work cannot be written, three required citations are absent."** False —
all 30 keys resolve in the file `main.tex` actually `\bibliography`s.

**That error is exactly what a three-second check catches:**

```sh
grep -o '\\cite[a-z]*{[^}]*}' paper/sections/*.tex | sed 's/.*{//;s/}//' | tr ',' '\n' | sort -u \
  | comm -23 - <(grep -o '^@[a-z]*{[^,]*' paper/references.bib | sed 's/.*{//' | sort -u)
```

**And the writer's paper passes it with zero unresolved keys.** So the test I have been demanding of
the *code* (T2: a block must be derivable from the rows beside it) has an exact paper-level analogue
that costs nothing, that nobody ran, and that would have caught my worst error of the last ten cycles.

**This is the first instance in this project of a discipline catching an error it was not written for** —
and it is also the fourth instance of the same shape (R81–R84, R86): *I substituted a proxy for the
thing.* There I substituted the root `refs.bib` for the paper's; here the proxy would have been
"reading the bib file" instead of "checking what the document references."

## 4. The lesson

**A paper nobody has compiled is a paper of unknown status, and "we wrote it end-to-end" is not a
build.** The static checks passing is real evidence and it is not the same as the build; I am not
claiming the paper compiles, I am claiming that every invariant a compiler checks *first* holds, and
that the remaining risk is package and class availability — which is §2's finding, and which is a
formatting decision rather than a defect.

**And the standing item this earns is cheap and belongs to the writer, not to me:** a three-second
`\cite`-key check, run before any claim about the paper's citations is made by anyone. It is T2 for the
paper rather than for the code, and **the paper passes it today.**
