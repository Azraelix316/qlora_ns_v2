# R109 — **auditing the six figures nobody had reviewed finds two more wrong numbers and two more false titles. A figure title says the BUG is "3-5x slower" when the artifact says 2.14-2.58x, and another says "the zonal mean grows" about a panel that plots total KE and whose Re=100 curve decays.**

**Cycle:** R109 · No new pushes. `main` at `14e1c2b`, 209 files, clean.
**Method: D69 found one unreadable figure and one false title. A figure defect is what a reviewer sees in
seconds, so I applied the same check to the six I had never opened.**

## 1. `fig_bug_cost`: the title's number is wrong (same class as D67's `99.9%`)

`experiments/make_figures.py:433`:

```
"BUG removes every full-size factorization\nand is still 3-5x slower"
```

**Measured, from `cost_bug_port.json`, population = all 12 ratio fields in the artifact:**

| quantity | N=64 | N=128 |
|---|---|---|
| `full_step_ratio_vs_reference` | **`2.1421`, `2.1702`** | **`2.5545`, `2.5842`** |
| `linear_algebra_ratio_vs_reference` | `0.7057`, `0.7921` | `1.2133`, `1.2247` |
| `amplitude_cost_ratio` | `1.0180`, `0.9744` | `0.9686`, `0.9816` |

**The slowdown is `2.14–2.58×`. Values inside `[3, 5]`: `0` of `12`.** The title is wrong at both ends —
the low end by `0.86×` and the high end by `2.42×`.

**And it is inconsistent with the paper's own figure.** D52.5's range is `2.08–2.71×` from
`cost_retiming.json`, and the BUG port's `2.14–2.58×` is a *subset* of it — so the two measurements agree.
**A reader comparing the BUG panel with the cost panel sees two different slowdown ranges for the same solver
at overlapping grids and has no way to reconcile them.** The title should read **`2.1–2.6×`**.

**The other half of that title is supported and worth keeping:** `linear_algebra_ratio_vs_reference` is
`0.71–0.79` at `N=64` and `1.21–1.22` at `N=128`, so the linear-algebra share is at or near parity while the
full step is `2.1–2.6×`. **"Removes every full-size factorization" is the interesting half; it is also the true
half.** (Note the nuance: at `N=128` the linear-algebra share is `21%` *above* parity, so "removes" should not
be read as "is free at every grid.")

## 2. `fig_divergence`: the title names a quantity that is not plotted, and a direction that is false

`make_figures.py:207-213`. The right panel plots, for every `Re` in the suite:

```python
ax.plot(t, result["full"]["energy_history"], ...)
ax.set_ylabel(r"$E$")
ax.set_title(r"Total KE: the zonal mean grows")
```

**Two separate defects:**

**(a) There is no zonal mean in this figure, or anywhere in `make_figures.py`.** Grepping `zonal` returns
only the title at `:213` and an unrelated `relative_l2_oracle_mean` at `:498`/`:512`, which belongs to a
different figure. **The panel plots total kinetic energy; the title asserts a property of the zonal mean.**

**(b) One of the three curves it plots goes down.** The suite is `{100, 1000, 5000}` from
`kolmogorov_re{re}_N64.json` (`:162`):

| Re | `E(0)` | `E(T)` | change | direction |
|---|---|---|---|---|
| 100 | `22.2067` | `20.2560` | **`−1.9507`** | **DECAYS** |
| 1000 | `22.2067` | `22.4596` | `+0.2529` | grows |
| 5000 | `22.2067` | `22.6716` | `+0.4648` | grows |

**So the title states one direction over a panel containing a curve with the other direction — and that curve
is the one that carries the physics.** D59 established that these runs start `3.6×10⁻⁷` of the Kolmogorov
equilibrium's energy below it, and at `A = 0.5, Re = 100` the forcing cannot sustain the state, so the energy
decays. **The figure's title erases the single feature that distinguishes the low-Reynolds case, which is
exactly the observation §5's account rests on.** Either the title becomes *"Total KE: it grows at Re ≥ 1000 and
decays at Re = 100"*, or the panel plots the zonal mean and earns the old title.

## 3. Two more, lesser but the same class

- **`fig_window_rank`, `:146`** — `ax.annotate(f"dealias ceiling {ceiling}")`, where `ceiling` is **recomputed
  in figure code** as `2 * (N // 3) + 1`. **This is D30's barred phrase, and it is the *fourth* instance**
  (`:7` docstring, `:522`, and now here). Worse, the number is *derived rather than read*: the artifact already
  carries `dealias_rank_ceiling` (`43 / 85 / 171`), so the figure should read it rather than re-derive it, or it
  will silently disagree the day the two formulas diverge. **Read it from the artifact; label it "the largest
  rank the grid resolves".**
- **`fig_spectrum`, `:176`** — `ax.annotate("IC is exactly rank 17")`. **"Exactly" is a tolerance claim, and
  this is the word D-record bars elsewhere.** The initial state is *constructed* by filtering at `cutoff = 8`,
  so it is rank 17 **of the filtered state**; and D60.3 established that the *rank rule* counts
  `rank_basis: "fluctuations"`, a different basis from the state itself. **"IC is exactly rank 17" conflates
  the state's numerical rank with the rank criterion's basis.** The companion title, *"Full-grid state spectrum
  (all resolved modes)"*, has the same problem: the spectrum is of the filtered state. Say **"at the stated
  spectral cutoff"** and drop "exactly".

## 4. A suspicion I checked and dropped

The artifact set contains **two `Re=5000` runs with different final energies** (`22.6716` at `N=64` and
`28.7223` at `N=128`), which would have meant two identically-labelled, identically-coloured curves in one
panel. **`suite` is keyed by Reynolds number and loads only `kolmogorov_re{re}_N64.json` (`:162`); the `N=128`
artifact is loaded separately at `:226` for `fig_div_free` alone.** So there is one `Re=5000` curve and **no
such defect. Dropped before reporting.**

## 5. The tally, and the lesson

**Of eight figures, six had never been opened. In those six: two wrong numbers (`3-5x` where the artifact says
`2.14–2.58×`; `exactly rank 17` where the state is rank 17 *at a stated cutoff*), two false titles (a zonal
mean that is not plotted, a direction that is false for one of three curves), and one barred phrase in its
fourth instance — plus one ceiling that is re-derived in figure code instead of read from the artifact.**

**Every one of these is a defect a reviewer sees by looking at one figure, and none of them requires reading a
sentence.** That is the argument for auditing figures as carefully as prose: **the figures are the cheapest
place for a paper to be caught, and the most expensive place to be caught in.**

**And the method that found them is D69's, generalised: for each panel, compare the title and the axis label
against the range and the direction of the data actually plotted.** Nothing here needed a new tool — it needed
opening six files I had no reason to open except that five others were already wrong.
