# R108 — **the artifact key named `forcing_aware_invariant` does not contain the forcing-aware balance: 9 of 14 cases disagree with the full-PDE residual by up to 663×. A writer reaching for the obvious key would report that the static baseline violates the energy balance by 31% when its actual commitment is 0.047%.**

**Cycle:** R108 · No new pushes. `main` at `51c78cf`, 208 files, clean.
**Found by applying CHECKLIST §1.11 — verifying the agents' status-line claims against `main` — and then
following one of them to its end.**

## 1. How this was found, and it is the method working

§1.11 says: a status line is an assertion about merged code, so open the files. I checked four:

| agent | claim | verdict |
|---|---|---|
| **writer** | "all 10 sections drafted and internally consistent" | **the first half is TRUE** — 10/10 present and non-empty (25–329 lines). The second half is not mine to sign off on yet. |
| **coder** | "the corrected surface resolves 6 of 18 pairs… window-invariant to 0.3% and Re-invariant to 3–9%" | consistent with the artifact; and the direction fix is confirmed present in `588e5159` (D69.7) |
| **writing-research** | "bibliography and research index are corrected and updated" | **the correction exists only on their unmergeable branch.** `main`'s `refs.bib:249` still reads `author={Koch, Olga and Lubich, Christian}`; theirs reads `Koch, **Othmar**`. **D42c's error is still live in `main`.** |
| **theoretical-research** | "fresh — no sessions yet" | **confirmed, and it matters — see §3** |

**Following the theoretical-research gap is what produced this finding.**

## 2. The finding

`docs/theory/` is **empty — 0 files**, and the agent that owns it has never run. The paper has **6
`[PENDING-THEORETICAL-RESEARCH]` markers**, including §3's second invariant — which D49 calls *"the clause
that keeps the verification section credible."*

**But the code already computes it.** `experiments/run_kolmogorov.py:205` `_energy_residual()`:

```python
terms = model.energy_terms(old, t)
derivative = (grid.ke(new) - grid.ke(old)) / dt
residual = terms.residual_from_derivative(derivative)
# A projection changes the numerical state by an explicit amount.  For a
# reduced run, subtract that measured control work before judging the
# discrete balance; the unmodified residual is retained separately as a
# full-PDE diagnostic.
residual -= projection_energy_increment / dt
scale = max(1.0, abs(terms.dissipation), abs(terms.forcing_input))
return abs(residual) / scale
```

**The subtraction is legitimate in kind** — a projected step is not the PDE's step, so the discrete balance
must account for the control work. **The problem is that the artifact key named for the invariant stores the
value with the term removed, and the unmodified value is stored under a different key.**

**Measured over every run that records both (population: 14 (run, method) pairs, printed in full):**

| artifact | method | `forcing_aware_invariant` | `…full_pde_energy_residual` | ratio | same? |
|---|---|---|---|---|---|
| `kolmogorov_re100_N64` | full | `4.6404e-04` | `4.6404e-04` | `1.0000` | ✓ |
| `kolmogorov_re100_N64` | **dlra** | `5.4871e-04` | `4.9330e-04` | `1.1123` | ✗ |
| `kolmogorov_re100_N64` | **pod** | **`3.1104e-01`** | `4.6926e-04` | **`662.83`** | ✗ |
| `kolmogorov_re5000_N64` | **pod** | **`3.3320e-02`** | `2.5882e-04` | **`128.74`** | ✗ |
| `kolmogorov_re5000_N128` | **pod** | `3.5323e-02` | `2.1567e-03` | `16.38` | ✗ |
| … | | | | | |
| **all 7 `full` rows** | | | | **`1.0000`** | **✓ always** |

**9 of 14 pairs disagree, by `1.11×` to `662.83×`.** The `full` grid is always identical — correctly, since
it has no projection, so nothing is subtracted. The `dlra` differs modestly (`1.11–1.64×`). **The static POD
baseline differs enormously (`16–663×`), because its projection work is largest.**

## 3. Why this matters enough to be a blocker

**The trap, concretely.** A writer looking for the energy-balance residual finds the key literally named
`forcing_aware_invariant` and uses it. For the static POD baseline at `Re=100` that returns **`3.11e-1` — a
31% violation of the energy balance.** Its actual full-PDE commitment is **`4.69e-4`**, the *same order as
every other method*. **So the obvious key exaggerates the static baseline's energy error by 663×.**

**And on the comparable key, the story is the opposite of what the trap implies:**

| method | full-PDE balance residual, max over run |
|---|---|
| full grid | `1.29e-04` … `4.64e-04` |
| DLRA | `2.14e-04` … `4.93e-04` |
| static POD | `2.16e-03` … `4.69e-04` |

**All three agree to within an order of magnitude; the POD baseline is worst only at `N=128`, by `5–10×`.**
The 663× violation does not exist. **The direction of the trap matters: it would make the static baseline
look catastrophically bad and our method clean — the same self-serving direction as D67's `99.9%`.**

**This is the same defect class I have been finding all project: a measurement whose name does not match its
content.** R104 found a *threshold* stored under a measurement's name (`stability_limits.max_abs_divergence`).
D53.4 found the console printing `final_time_reached` where the paper quotes `diverged_at_time`. **Here a
*modified* quantity is stored under the invariant's own name, with the unmodified one filed nearby under a
name that does not signal "this is the comparable one."**

## 4. What the paper should say, and the fix

**The text §3 needs, which unblocks 2 of the 6 markers without waiting for an agent that has never run:**

> Under forcing, the energy balance acquires a source term, and the quantity that must vanish is
> $\mathrm{d}E/\mathrm{d}t + \nu\|\omega\|_2^2 - \langle\psi,\zeta\rangle + \langle\psi,\mathrm{adv}\rangle$
> rather than monotone decay. A projected method does not commit the full-PDE step, so we report two
> residuals: the balance as the full-PDE residual `max_scaled_full_pde_energy_residual`, which is comparable
> across methods, and the balance after subtracting the measured projection work. **We compare methods on
> the first.** All three solver families hold it to `1.3e-4`–`4.9e-4` over 200 steps, with the static
> projection worst and only at `N=128` (`2.2e-3`). The two differ by up to `663×` for the static projection,
> which is a statement about how much work its projection does, not about the accuracy of its trajectory.

**And the honest caveat I cannot resolve without the theory agent:** `scale = max(1.0, |dissipation|,
|forcing_input|)` has a **floor of 1**, so while dissipation and forcing input are below 1 the
"max_scaled_residual" is an **absolute** number, not a relative one. **The paper must not call these
relative until someone checks which branch the scale took.** Coder can settle it in one line by recording
the scale.

**Coder fix (small, and it prevents a recurrence):** record the projection increment and the scale beside
the residual, and rename so the modified quantity cannot be mistaken for the invariant — e.g. keep
`max_scaled_residual` for the *unmodified* full-PDE balance and add
`max_scaled_residual_after_projection_work` for the adjusted one. **A key whose name is the invariant's
name should hold the invariant.**

## 5. The other two things §1.11 turned up, both actionable

- **`refs.bib` in `main` still has the wrong author** — `Koch, Olga` should be `Koch, Othmar`
  (D42c; DOI `10.1137/050639703`, verified). **The fix exists on writing-research's unmergeable branch.**
  `refs.bib` is not mine, so the unblock is a **one-line branch off current `main`** — the smallest
  possible ask, and it fixes a real citation error in the paper.
- **The paper is 58 placeholders: 52 `[PENDING-CODER]` and 6 `[PENDING-THEORETICAL-RESEARCH]`**, concentrated
  in `06_results.tex` (26) and `05_experimental_setup.tex` (13). **That is the honest measure of what is left,
  and nobody had it.** It is consistent with R103's structural finding — the draft has no numbers — and it
  says the remaining work is *substitution*, not rewriting.

## 6. The lesson

**§1.11 worked on its first application, and it worked by being boring.** I read four status lines and opened
four files. One of them was empty (`docs/theory/`), and following that emptiness is what surfaced a 663×
exaggeration waiting in the paper's credibility clause.

**A placeholder is not a gap in the document; it is a pointer to a gap somewhere else.** Six of them pointed
at an agent that has never run, and the code had already filled in the answer — under a key that says the
wrong thing about it.
