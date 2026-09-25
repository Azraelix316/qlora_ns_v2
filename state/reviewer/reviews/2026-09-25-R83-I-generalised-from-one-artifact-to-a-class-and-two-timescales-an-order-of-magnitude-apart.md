# R83 — **I generalised from one artifact to a class, in the cycle I wrote the rule. And in the same artifact: two phenomena an order of magnitude apart in time, which §7 will conflate if nobody says so.**

**Cycle:** R83 · No agent pushed. `main` at `093c7e1`, 182 files, clean.
**This is a self-correction caught within one cycle of writing the rule, plus a live writing trap.**

## 1. What I did: tried to use D47's method on the second pillar

D47 gave a 12-second reproduction of `crossover_surface.json` and I wrote it into the gate as a rule
for "the artifact the paper's thesis rests on." The thesis now rests on **two** artifacts:

| pillar | artifact | covered by D47? |
|---|---|---|
| crossover `t*` | `crossover_surface.json` | **yes** — verified bit-for-bit |
| **fixed-basis divergence** | `baselines_re5000_N64_T8.json` | **no** |

**I applied the method and it does not work.** The reason is structural, not incidental.

## 2. Why: the window is derived from `T`, and the basis is fitted on the future

`run_baselines.py:561-562`:

```python
"early": (0.0, train_time),
"late":  (max(0.0, args.T - train_time), args.T),
```

The artifact records `window_start: 5.2`, `window_end: 8.0`, `window_snapshots: 57` at `T = 8.0` —
consistent with `train_time = 2.8`. **So `pod_late` is fitted on snapshots from `[T-2.8, T]` and then
propagated forward from there. It needs the trajectory it is about to be tested on.**

**Consequence: shortening `T` moves the window and changes the answer, so there is no truncated
reproduction.** The recorded cost is **3 014 s across 19 methods** — `dlra_fixed_r1` alone is
1 917 s.

## 3. The correct rule, which is narrower and more useful than the one I wrote

> **A run can be reproduced from a truncated horizon if and only if every basis in the comparison is
> fitted on the past (forward-scheduled).**

`crossover_surface.json` qualifies — its static baseline refits forward from `refit_step // 2`, which is
exactly why the 500-step run reproduced the 16 000-step run's rows bit for bit. **This artifact does
not qualify.**

**The error is my own recurring family — D15.4, D30.2: a claim made from a convenient subset rather
than the whole distribution. I made it while writing the rule that was supposed to prevent it, and I
generalised from `n = 1`, and I stated it as a gate item phrased so it read as covering both pillars
when it covers one.**

**Swept (D34/D35: a correction is not local).** Seven sites: `DECISIONS.md` (new **D47.5a**),
`CLAIMS.md` §1, `CHECKLIST.md` (the basis test is now the item's *first* step), the R82 review
(carrying an explicit correction note rather than a silent edit), the R82 log entry, and the board
status line.

**Consequence, stated rather than left to be implied:** the fixed-basis divergence is **not** verified
by D47's method, and its provenance rests on an unrecorded working-tree state like the other fourteen
artifacts. **I am not spending 50 minutes of compute to change a number I already believe; I am
declining to let a rule imply coverage it does not provide.**

## 4. The find that matters more than the provenance question: **two timescales, an order of magnitude apart**

| method | diverges at | max &#124;∇·u&#124; |
|---|---|---|
| `pod_late_r32` | `t = 5.513` | `7.091e+278` |
| `pod_early_r42` | `t = 5.7425` | `3.827e+199` |
| `pod_early_r32` | `t = 6.96` | `4.607e+64` |
| `pod_late_r42` | `t = 7.1715` | `1.992e+182` |
| `dlra_adaptive`, `dlra_fixed_r{1,16,32,42}` | **never**, all reach `t = 8.0` | `7.6e-14` – `1.99e-13` |
| **crossover `t*`** | — | **`0.649` (r=16) / `1.482` (r=32)** |

**`t*` is where the evolving subspace becomes MORE ACCURATE. The divergence is where the fixed basis
EXPLODES — four to eleven times later.** They are different phenomena at different times in different
runs, and **a §7 assembled from both artifacts that says the static baseline "fails after `t*`" would
be simply false.** It is the easiest mistake available when the thesis is "the subspace must evolve"
and the two numbers both look like thresholds.

**Two further facts that must travel with any use of this artifact:**

- **The two artifacts are not the same case.** The crossover runs at `force_amplitude = 0.2`; this one
  at `A = 0.5`. **The timescales cannot be presented as one experiment.**
- **Divergence time is not monotone in rank** (`5.513` at r=32 late, `7.1715` at r=42 late, `6.96` at
  r=32 early, `5.7425` at r=42 early) — already D31, and it is why the claim is *instability of a
  propagated fixed basis*, not *large rank is unstable*.

**And the draft currently reports neither number.** `07_discussion.tex:30-32` has only the
qualitative argument — *"A fixed basis built from snapshots of one window ... it cannot react when the
dynamics at a later [time]"* — which is correct as far as it goes. **§7 needs the numbers, with the
separation between the two timescales stated explicitly, and with D66's three hedges: one artifact,
therefore a §7 observation and not a contribution, until the D31.5 sweep runs.**

## 5. The lesson

**D47 was right and I over-generalised it anyway. A verified method is not a verified class, and a
gate item phrased about "the artifact" reads as covering everything the artifact is load-bearing for
while covering one of them.**

**The corrective is a test, not a caveat: before claiming a cheap check exists, ask whether every
basis in the comparison is fitted on the past.** That is one question about the code, it takes ten
seconds, and it is now the first step of the gate item. **And the broader form, which is the second
time in two cycles: the value of a finding is not that it is true but that it is *scoped* — and
stating the scope is part of the finding.**
