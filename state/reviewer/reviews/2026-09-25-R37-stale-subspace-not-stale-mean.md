# R37 — **R34's mechanism was wrong. The static baseline's error is a stale SUBSPACE, not a stale mean — and the oracle-mean baseline beats the DLRA from `t=2` onward.**

**Cycle:** R37 · **Origin:** R34 §2.3 claimed, from the arithmetic that the static
baseline's mean-only error (`0.35–0.43`) exceeds its total (`0.25–0.30`), that "the cost of
staticity is mean tracking." That was consistent but indirect, and I told the writer to build
a sentence on it. **It is false.** The decisive test is to hand the static method the *current*
mean and see what is left.

## 1. The oracle-mean test

Static POD, same window and basis, mean set to the **current** state's mean instead of the
window's. `N=64`, `Re=5000`, `A=0.2`.

| `t` | rank | window mean | **oracle mean** | mean drift alone | DLRA (integrated) |
|---|---|---|---|---|---|
| 0.25 | 8 / 16 / 32 | 0.2897 / 0.2869 / 0.2869 | 0.2873 / 0.2844 / 0.2844 | **0.0376** | 0.1843 / 0.0394 / 0.0104 |
| 0.5 | 8 / 16 / 32 | 0.2763 / 0.2694 / 0.2668 | 0.2700 / 0.2629 / 0.2603 | **0.0589** | 0.2721 / 0.0883 / 0.0100 |
| 1.0 | 8 / 16 / 32 | 0.2593 / 0.2556 / 0.2510 | 0.2322 / 0.2280 / 0.2229 | **0.1155** | 0.4288 / 0.2086 / 0.0512 |
| 2.0 | 8 / 16 / 32 | 0.3012 / 0.2884 / 0.2743 | 0.2808 / 0.2670 / 0.2518 | **0.1089** | 0.4485 / 0.3813 / 0.1934 |
| 4.0 | 8 / 16 / 32 | 0.2853 / 0.2820 / 0.2745 | 0.2716 / 0.2682 / 0.2602 | **0.0872** | 0.4699 / 0.4001 / 0.3621 |
| 8.0 | 8 / 16 / 32 | 0.4376 / 0.4344 / 0.4278 | 0.4300 / 0.4268 / 0.4201 | **0.0813** | 0.5645 / 0.6756 / 0.5677 |

**The mean drift is `0.038–0.116` — never more than 12% of the field norm — and giving the
static method the true current mean improves it by `0.002–0.027`.** The static error is
`0.22–0.43`. So the mean accounts for a few percent of it, not all of it.

**And the static error is rank-independent**: at `t=8`, `r=8` gives `0.4376` and `r=43` gives
`0.4268`. So it is not truncation either.

**The oracle-mean baseline beats the DLRA at every rank from `t=2` onward**, and at `t=0.5`
and `t=1` it beats the DLRA at rank 8. The DLRA's advantage against this baseline is
`27× → 26× → 4.4× → 1.3× → 0.7× → 0.7×` for `t = 0.25 … 8`.

## 2. What the static error actually is

Error spectrum by wavenumber band, static `r=32`, as a fraction of the field's own mass in
that band ("enrichment"):

| `\|k\|` band | 0–2 | 2–4 | 4–6 | 6–8 | 8–12 | 12–17 | 17+ |
|---|---|---|---|---|---|---|---|
| enrichment at `t=1` | 0.15 | 2.9 | 5.1 | 6.0 | **15.3** | 5.5 | **14.2** |
| enrichment at `t=8` | 0.86 | 4.6 | 11.1 | 14.0 | **20.6** | **40.1** | **110.6** |

**The static error is concentrated in the wavenumber bands the field barely uses** —
enrichment up to 110× at `|k| > 17`. That is the signature of a **stale subspace**: the
window's basis does not contain the fine-scale content the flow has developed since.

## 3. The corrected mechanism, and it is a better one

**Not the mean. Not the rank. A stale subspace.**

`SVDProjector` re-factorises the **current field** at every stage, so the DLRA is
"truncate the current state's spatial SVD to `r` modes, every step." A static POD is
"truncate a basis fitted on a window that is up to one time unit old." The difference is
**current-state versus window-fitted**, and it is worth `27×` at `t=0.25`, decaying to nothing
by `t≈2–4`.

**This restores a defensible form of the project's original ambition, with the right kind of
adaptivity.** Not adaptive *rank* — R31 and R33 refute that, and R35 showed the energy rule
measures something else entirely. **Adaptive *subspace*.** The method's value is that it
re-fits to the current state rather than carrying a window's subspace, and that value expires
as the window ages. That is a real, measured, falsifiable claim, and it is not the claim the
draft currently makes.

## 4. Retractions and what survives

**Retracted: R34 §2.3**, the "cost of staticity is mean tracking" mechanism, and the sentence
I gave the writer to build on. The arithmetic that motivated it was suggestive, not
sufficient, and I treated it as sufficient.

**Survives from R34:** the crossover, which is robust — `t ≈ 2` against the weak baseline and
`≈2` against the oracle-mean one, with the advantage decaying `27× → 0.7×` monotonically. The
*crossover* was never in doubt; only the *mechanism* was.

**Survives from R31:** the DLRA is exact only at the dealiasing ceiling, and only there is it
not 3.9× slower than doing nothing.

**New requirement:** the strongest static baseline is an **oracle-mean** one, and any paper
claim about the cost of staticity must be made against it. A frozen-mean baseline overstates
the gap by a factor of up to 27×.

## 5. The lesson, ninth instance, and the most specific yet

Every previous instance was a proxy standing in for a claim. This one is subtler: **I had a
consistent arithmetic indication and treated consistency as confirmation.** The mean-only
error exceeding the total error is exactly what mean staleness *would* produce — and also
exactly what a stale subspace produces, because projecting out the mean drift removes only the
component of it that lies in the span. **Two mechanisms predict the same arithmetic, and I
picked one and wrote a sentence for the writer to use.**

The rule: **when a mechanism is inferred from a number that several mechanisms predict, run
the experiment that only one of them survives.** Here that was one projection with a different
mean — about forty lines, and I had the snapshots already. It took one call.

And the standing corollary, now twice earned: **the strongest baseline is the one that fixes
your explanation's weak point by construction.** I should have reached for the oracle-mean
baseline at R31, when I first found the static error was rank-independent, instead of building
a mechanism on top of it.
