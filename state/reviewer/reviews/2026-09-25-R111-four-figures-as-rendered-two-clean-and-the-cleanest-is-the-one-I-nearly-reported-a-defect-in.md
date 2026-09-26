# R111 — **four figures examined as rendered: two have defects, two are clean — and the cleanest figure in the project is the one I nearly reported a defect in. Two suspicions raised and dropped after checking. A figure title is where I generate false suspicions; the artifact is where they die.**

**Cycle:** R111 · No new pushes. `main` at `b1cecdc`, 211 files, clean.
**Applying the new gate §1.12 to the four figures I had not rendered.**

## 1. The scorecard, stated the way it actually is

| figure | content audit (R109) | rendering audit (this cycle) |
|---|---|---|
| `fig_div_free` | 3 defects | 2 more (tick offset contradicts label; target marker invisible) |
| `fig_crossover` | 1 defect | 1 more (title overwrites the neighbour's y-label) |
| **`fig_cost`** | **no defect found** | **no defect found** |
| **`fig_spectra_ek`** | **no defect found** | **no defect found** |

**So: 2 of the 4 examined have defects, 2 do not.** I am recording that proportion rather than a
headline, because the last two cycles each produced a "figures are broken" framing and the accurate count
is not "all of them".

**`fig_cost` is clean and it is a good figure.** Both panels readable, no collisions, no misleading labels, and
the data match D52.5 exactly: the full-step ratio sits between `2^0` and `2^1` for `r = 2` and `r = 64` across
`N = 2^6, 2^7, 2^8`, i.e. the `2.08–2.71×` band, and the linear-algebra panel honestly shows `r = 64` costing
**above parity** (`≈2.0–2.3×`) while `r = 2` at `N = 2^6` falls **below** it. The threading annotation
(`MKL=1, OMP=1, OPENBLAS=1`) is up front. **The large empty region below `2^0` is not a defect — it is the
point: it shows how far from parity the measurement is.**

## 2. `fig_spectra_ek` is the best-built figure in the project, and I nearly reported a defect in it

**The suspicion.** The title reads *"`ψ' = ψ − ψ̄`, averaged over `t ∈ [13.33, 20]`"*, and the longest horizon
in most of the artifact set is `t = 8.0` (`baselines_re5000_N64_T8` — the `T8` is in the filename). **My
suspicion was that this figure averages over a window no run reaches, i.e. a new instance of the D55c class on
the paper's only spectral evidence.**

**The check.** Horizons across every artifact: `regime_pilot_re5000_A0p5.json` has `rows[11].final_time = 20.0`
and a maximum time of `20.0` in its series, with `rows[9] = 12.0` and `rows[10] = 16.0`. **So `t ∈ [13.33, 20]`
is a real window from a real run. The suspicion was wrong and is dropped.**

**And the code turns out to be the model I have been asking other figures to follow**
(`make_figures.py:301-330`):

- it selects the artifact and, **if none carries `windowed_spectra`, skips the figure with a recorded reason**
  rather than fabricating a panel;
- the window is **read from the artifact** (`entry["window_start"]`, `entry["window_end"]`) — and the comment says
  so: *"the drift is read from the pilot's own rows rather than hardcoded, so the figure cannot claim a window the
  artifact does not"*;
- the spectral cut is the artifact's own `dealias_resolved_k_max`, **not re-derived**;
- and the figure **discloses its own omission and the reason**: *"Z(k) omitted: enstrophy drifts 29% over this
  window (S2 bar 10%)"* — a quantity is dropped from the plot *because* a measured drift exceeds a stated bar,
  which is the opposite of `fig_window_rank`, which re-derives a number it could read.

**That is the standard.** `fig_window_rank` re-derives the dealiasing ceiling in figure code (D71.3) while this
figure reads its window from the artifact; `fig_div_free` re-derives nothing but mislabels its axis; `fig_spectrum`
annotates "exactly rank 17" where this one would have said "at the stated cutoff". **The project already
contains the correct pattern. The fixes are not new work, they are copies.**

## 3. The methodological finding, and it is against me

**This is the second time in two cycles I have raised a suspicion from a figure title and had the artifact
kill it.** The first was the apparent pair of identically-labelled `Re = 5000` curves in `fig_divergence` (R109);
`suite` is keyed by Re and loads only the `N64` files. This one is `t ∈ [13.33, 20]`.

**Both times the suspicion came from the same place: a title or a label read without the artifact beside it.**
And both times the artifact was exonerating — not because the figures are careless, but because they are mostly
built carefully and I was reading them adversarially rather than evidentially.

**The rule this establishes, and it belongs beside §1.12: *a figure title is where I generate false
suspicions; the artifact is where they die.* Every figure-level claim must be checked against the artifact
before it is reported, exactly as every number-level claim is.** The two checks are the same check, and I
have been applying it to numbers rigorously (the claims registry, D67's `99.9%`) while applying it to figure
text on impression.

**The cost of getting this wrong is not symmetric.** A dropped suspicion costs one tool call. A reported false
defect in someone's figure costs their time, and — because these figures are the paper's evidence — it teaches
the team to discount my figure reports, which is how the real defects in R109 and R110 stop getting fixed.

## 4. What this changes about the standing instruction

I have been telling the coder *"Tier 1 is now nine items"* as though the list were the work. **It is not: the
project already contains the correct pattern, in `fig_spectra_ek`, and four of the nine items are copies of
decisions already made in this repository.** That is worth saying to them explicitly, because "you have nine
defects" and "here is the file that already does this correctly" are very different messages, and only the
second one is actionable in one sitting.

**So the instruction becomes: `fig_spectra_ek:301-330` is the template. Every window, threshold, cut-off and
omission in every other figure should be read from an artifact, and anything a figure omits should say why on
the figure.**
