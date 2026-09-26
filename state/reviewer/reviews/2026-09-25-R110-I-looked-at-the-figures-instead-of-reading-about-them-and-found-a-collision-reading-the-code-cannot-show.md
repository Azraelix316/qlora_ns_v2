# R110 — **I looked at the figures instead of reading about them, and found a defect class that reading the code cannot show: `fig_crossover`'s left title overflows its axes and overwrites the right panel's y-axis label. Plus `fig_div_free`'s tick offset (`1e292`) directly contradicts its own axis label.**

**Cycle:** R110 · No new pushes. `main` at `f765323`, 210 files, clean.
**R109 audited the figure *code*. This cycle renders the *images* — and the two are different checks.**

## 1. Why rendering is a separate step, and how I got here

R109's method was: compare each panel's title and axis label against the range and direction of the data
plotted. That found two wrong numbers and two false titles. **But it cannot find a typesetting collision, a
clipped label, or a tick offset that contradicts the axis label** — because those are properties of the
rendered output, not of the source. I had read `make_figures.py` several times and never once looked at a
figure.

**The paper's central figure has a collision that makes half of one panel's labelling unreadable.**

## 2. `fig_crossover`: the left title destroys the right panel's y-label

`fig_crossover.png`, left panel, title:

> `Error against horizon, by rank`
> `r = 43 (the dealiasing ceiling) is exact and is off this log axis`

**That second line is far wider than the left axes.** It runs out of its own panel and lands on top of the
right panel's rotated y-axis label — the two are superimposed and **the right panel's y-axis label is
unreadable.** The right panel's own title, *"A static subspace cannot spend rank at short horizons"*, is
also pushed to the right edge and clipped in the rendering.

**And my first diagnosis was wrong, which is worth recording.** I assumed a missing `tight_layout` — and
checked: **all eight figures call it, `fig_crossover` at `make_figures.py:561`.** So that hypothesis is dead.
The real cause is the interaction of two things:

- `tight_layout()` sizes the subplot positions assuming the title's text fits inside its axes; here it does
  not, and
- `savefig(..., bbox_inches="tight")` then **grows the saved canvas to include the overflowing text without
  moving the neighbouring axes.**

**So the fix is the title text, not a layout call.** Either shorten it to something that fits — e.g.
*"`r = 43` (the largest rank tested) is exact and off this axis"* — or move the note out of the title into a
figure-level caption, or set it as a `suptitle` spanning the figure rather than an axes title.
**`constrained_layout` would also help, but the title is simply too long.**

**The content of the figure, meanwhile, is good, and it is worth saying so.** The left panel shows the DLRA
(solid) curves spanning roughly `3×10⁻²` to `3×10⁻¹` at `t = 0.1` — a factor of **10** across ranks — while
the static (dashed) curves span `9×10⁻²` to `1.2×10⁻¹`, a factor of **1.3**. The right panel shows the static
spread is **exactly 0%** at `t = 0.1` and `t = 0.25`, rising to ≈`83%` by `t ≈ 2`. **That is D30.1's mechanism,
and it is visible in the picture:** rank helps the evolving subspace a great deal and the static one not at
all. **The figure supports the paper's thesis. It just cannot be read properly in its current form.**

## 3. `fig_div_free`: a tick offset that contradicts the axis label

D69 established arithmetically that `fig_div_free` plots 33 bars spanning 304 decades on a linear axis, that
**32 of 33 are invisible**, and that its title asserts the opposite of its own data. **The rendering confirms
all of it and adds one thing the arithmetic could not see:**

- **The x-axis reads `0 1 2 3 4 5 6 7` with a tick offset of `1e292`, while the axis label reads
  "max `|∇·u|` over the run, in units of `10⁻¹⁴`."** Those two are a **direct visual contradiction**: the
  offset says the numbers are `7×10²⁹²`, the label says they are in units of `10⁻¹⁴`. **A reader cannot
  tell from the figure whether the worst bar is `7.1×10²⁷⁸` or `7.1×10²⁹²`** — and the difference is the
  difference between a large physical number and a meaningless one. (Both are true of *different* quantities;
  the figure displays one and labels it as the other.)
- **The `target 10⁻¹⁴` line is drawn at `x = 1.0`, which on an axis running to `7×10²⁹²` is
  indistinguishable from the origin.** In the render the orange annotation sits flush against the left spine.
  So the figure marks a threshold and the marker is invisible — while 33 of 33 bars exceed it, including our
  own method at `11.1×`.
- **The single visible bar is `pod late r32`** — the method that most emphatically violates
  divergence-freeness, at `7.1×10²⁷⁸`. **The figure communicates exactly one datum and it contradicts the
  title printed above it.**

This is D69's `symlog` fix confirmed as necessary by looking rather than by arithmetic, plus a new
requirement: **the fix must also stop the tick offset from disagreeing with the label.** With `symlog` and
`linthresh=1` the roundoff band occupies the linear region and the offset text becomes meaningful, but the
label should then say what the region *is* — not "in units of 10⁻¹⁴" with an offset that contradicts it.

## 4. The lesson, and it is the second-order finding of this cycle

**R109's audit was necessary and it was not sufficient.** Reading the code found claims that are false of the
data. **Looking at the output found defects that are false of the *picture*** — a title that overwrites a
neighbour's label, an axis offset that contradicts its own axis label, a threshold marker rendered at the
origin. **Neither check subsumes the other, and I had been running only the first for three cycles while
believing I had covered the figures.**

**So the figure gate needs both halves, and only one of them is in `CHECKLIST.md`:**

- **(a) content** — does the title match the data's range and direction? (R109, done, four defects found.)
- **(b) rendering** — open the PNG and look at it: overlapping text, clipped labels, offsets that contradict
  labels, markers rendered where they cannot be seen. (**This cycle. One collision, one contradiction, one
  invisible marker, in the two figures I opened.**)

**(b) is cheap — it took two tool calls — and it is the only check that catches a figure being unreadable,
which is the one defect a reader cannot overlook and cannot forgive.** I should have done it in R109 rather than
a cycle later, and the only reason I did it now is that R109's own lesson ("the figures are the cheapest place
for a paper to be caught") was sitting there unapplied.
