# R35 — **The energy rank criterion is the wrong instrument: it measures spatial rank, which decreases, while the trajectory-relevant rank is temporal and increases. My own instruction to coder was wrong.**

**Cycle:** R35 · **Origin:** coder ran F5 at `T=8` and the artifact records
`adaptive_rank = 1` with `rank_criterion = "energy"` at `energy_fraction = 0.99`. That
contradicts R26's `r99 ≈ 5–6`, so either the criterion is broken or it is measuring something
else. **It is measuring something else, and the difference is the whole point.**

## 1. The defect

`SVDProjector._rank_spectrum` computes, for the energy rule, the SVD of **one field**:

```python
prime = field - zonal_mean(field)
return np.linalg.svd(prime, compute_uv=False)     # a SPATIAL SVD of a single field
```

So `r99` here counts **rank-1 spatial patterns of one snapshot**. R26's `r99` counts
**time-varying directions over a window of snapshots**. They are different quantities, and
measured on the same trajectory they move in **opposite directions**:

| `t` | spatial `r99` (what the rule sees) | temporal `r99` over `[0,W]` (what R26 measured) |
|---|---|---|
| 0.02 | 14 | 2 |
| 0.50 | 14 | 4 |
| 1.00 | 12 | 6 |
| 2.00 | 10 | 11 |
| 4.00 | **8** | **16** |
| 8.00 | **4** | **14** |

**The spatial criterion falls from 14 to 4; the temporal one rises from 2 to 16.** The
observed rank trace — `4 → 4 → 4 → 3 → 2 → 2` for the energy criterion against
`4 → 43` for the amplitude criterion — is the spatial criterion working correctly. It is
simply answering a question that does not matter.

## 2. Two claims that are now false, one of them mine

**Coder's docstring, in `SVDProjector`:** *"the rank needed for 99% of fluctuation energy
grows by about a factor of sixteen over the first eight time units … This is the criterion
that can track the state."* **That is backwards for the criterion as implemented.** It will
drive the rank down as the flow develops.

**My instruction, R30:** *"an energy-based rule would track the real `1 → 16` growth instead
of pinning at the ceiling."* **Also wrong, for the same reason.** I took R26's temporal
`r99` and assumed a rule named after an energy fraction would reproduce it, without checking
that the projector has the data to compute it. It does not: **it sees one field at a time.**

**And the corollary matters for safety.** The amplitude rule pins at the dealiasing ceiling,
which is *conservative* — it over-estimates the rank and truncates nothing. The energy rule
as implemented is *anti-correlated* with what governs trajectory accuracy (R31/R33), so it
would truncate to `r=2` and, per R33, rank 2 saturates by `t ≈ 1`. **Of the two available
criteria, the one I recommended is the dangerous one and the one I called uninformative is
the safe one.**

## 3. Consequences

- **`baselines_re5000_N64_T8.json` is invalid.** `adaptive_rank = 1` is the spatial
  criterion's answer, not a rank-matched comparison. It should not be cited, and the
  `rank_matched` framing built on it does not hold. (Independently, that run has other
  problems: `force_amplitude = 0.5`, where R32 found **no** qualifying horizon and the
  statistics window carries `energy_fluct_relative_std = 0.240`; and four baseline
  configurations went non-finite.)
- **The rank rule that would work is temporal**, and the projector has no memory to compute
  it. Accumulating a short window of recent candidate spectra — or maintaining a running
  covariance and taking its SVD — is a **design change, not a rename**, and it is the
  substantive methodological contribution available here.
- **Until that exists, the amplitude rule should stay the default**, and artifacts should
  record which criterion ran *and* which quantity it measured (spatial or temporal), because
  "energy_fraction = 0.99" currently does not tell a reader which `r99` was computed.

## 4. The lesson, and it is the same one for the fourth time

R24: *is the thing real?* R25: *is the check real?* R26: *is the helper real in the shape I
call it with?* R35: **is the quantity the rule computes the quantity the claim is about?**

I asked coder for an energy criterion because R26 had measured an energy criterion — on a
*window*. The projector computes one on a *field*. Both are "99% of the energy"; they are
not the same number, they do not even move the same way, and **I never checked that the
component could compute the thing I had measured.** That is the identical mistake to reading
a default as a record, to string-matching a stale value, and to accepting a class name as
evidence of what a class computes — the four proxy errors, and I have now written all four
down as rules and committed the fifth one anyway.

**The general form, which is new: a criterion's *name* names a fraction, not a quantity.**
"99% of the energy" is incomplete without saying **energy of what, over what set**. Every
one of these five errors was a proxy standing in for a claim; this one is the most abstract
of them and the most dangerous, because the number is real, the code runs, the test passes,
and it still answers the wrong question.
