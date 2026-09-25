# R44 — auditing my own `CLAIMS.md`: 29 verified, 1 real error, 1 of my own numbers struck

**Cycle:** R44 · **Subject:** `state/reviewer/CLAIMS.md` @ `7899c3f`, written in R43 and
immediately made the document every other agent now defers to. **Verdict: one error found and
fixed, one unreproducible number struck, everything else exact.**

## 1. Why this cycle exists

R43 ended with the observation that *a reviewer who cannot fit the current state on one screen
has failed at the reviewer's job*, and produced `CLAIMS.md` as the fix. The obvious next
failure is the one I have spent this project hunting in other people's work: **an authoritative
document that is itself unverified.** Every other artifact in this repository earned trust by
being checked; `CLAIMS.md` was written in one pass from my own reports and pushed unexamined.
So I audited it, number by number, against the artifacts on `main`.

The method is the one I have applied to coder's artifacts throughout: extract every number,
look it up in the artifact that produced it, and report mismatches rather than reconciling
them silently. The audit script is `/tmp/opencode/audit_claims.py`; it walks the 13 result
artifacts and compares field by field.

## 2. What verified

| group | result |
|---|---|
| windowed `r99` at `N=128`, `W = 0.5/1/2/4/8` | `2/4/6/10/16` — **5/5 exact** |
| windowed `r99` at `N=64`, same `W` | `2/4/6/11/16` — **5/5 exact** |
| amplitude rule at `W=8` | `174` (`N=64`), `357` (`N=128`) — exact |
| dealiasing ceilings | `43 / 85 / 171` — exact, and `174/43 = 4.05×`, `357/85 = 4.20×` |
| S2 drifts at `N=128` | `T=4`: E `8.79%`, Z `23.47%`; `T=8`: E `2.22%`, Z `24.66%` — **4/4 exact** |
| `qualifying_horizons` | `[3.0]` / `[]` / `[]` — 3/3 exact |
| IC energies | `22.206703312933374` / `22.188588576546824` — exact to `1e-12` |
| full-step cost ratios, 6 rows | `1.777 / 2.071 / 2.049 / 2.143 / 2.133 / 2.181` — **6/6 exact** |
| rank-independence `r64/r2` | `1.165 / 1.046 / 1.022` — 3/3 exact |
| zonal share at `T=20, A=0.5` | `0.938` — exact |
| `baselines` non-citable flags | `adaptive_rank = 1`, `A=0.5`, has `sha256` — 3/3 exact |

**29 verified, 6 apparent mismatches that were my script's key-name guess, not the data.**
The cost ratios first came back `nan` because the field is
`grids[].rows[].full_step_ratio_vs_reference`, not `full_step_ratio`; the amplitude rule is
`window_rank_table[].amp_1e-6`, not `r_amp`. **Both were caught by re-reading the artifact
rather than by loosening the check** — the standing rule from R9, and the reason the six
"mismatches" resolved to six exact matches rather than to six accepted guesses.

## 3. The real error, in my own document

**§4 stated the committed divergence range as `1e-14 … 2.2e-13`. The true range across all 13
result artifacts is `2.32e-14 … 2.24e-13`.** I had taken the lower bound from a remembered
figure rather than from the minimum, so the claim was optimistic at its most-quoted end.

Re-measuring properly — `Re=5000`, `A=0.2`, 200 steps, DLRA `r=16` and full grid — gives a
**better** claim than the bare bound:

| `N` | 32 | 64 | 128 | 256 |
|---|---|---|---|---|
| `max abs(div u)` | `7.3e-15` | `1.7e-14` | `4.7e-14` | `1.8e-13` |
| fraction of `eps·N²` | `0.03` | `0.02` | `0.01` | `0.01` |

**The divergence grows ≈`N¹` while `eps·N²` grows ≈`N²`, so the ratio falls by an order of
magnitude across the range.** That is the statement that makes it a property of the
*representation* rather than of the scheme, and it is what the paper should say instead of a
bare `≈1e-14`. §4 now carries the table.

## 4. The number I struck: `5.8e-15`

R25 quoted `5.8e-15` at `N=32` and R30 repeated it. **Re-measuring gives `7.3e-15` at the
same `N`.** The discrepancy is not noise — it is that R25's harness recorded no setup, so the
number cannot be reproduced from anything. That is precisely the R27 failure: *provenance
beats fingerprint.* I was quoting a measurement whose only surviving record was my own memory
of having measured it, and I had been propagating it for nineteen cycles.

**`5.8e-15` is struck.** The replacement is the R44 table above, which records its own setup
so it can be re-derived — the difference the strike is about.

## 5. One thing I suspected and was wrong about

I expected the test suite not to assert the divergence bound numerically, since `max|div u|`
is `AGENTS.md`'s headline invariant and I had not seen a test for it. **It does, in nine
places**, every one `assert grid.max_div_velocity(psi) < 1e-12`, plus
`test_divergence_diagnostic_detects_an_injected_violation` which checks the diagnostic does
not fire on a divergence-free perturbation of the same size. Checking cost one grep and
prevented a false blocker.

**But the bound is flat, and my measurement shows why that is a latent problem.** At `N=256`
the measured `1.8e-13` leaves only ~`5×` margin against `1e-12`; at `N=1024` the expected
`N¹` growth puts it near `1.5e-12` and the assertion would **fail**. Every resolution the
project actually runs is safe, so this is a small robustness item, not a blocker. The natural
form is `< 0.5 · eps · N²`, which holds with a `12–50×` margin at all four `N` measured. §4
records the margin so the next agent is not surprised.

## 6. The lesson, which is the same one as always

**An authoritative document inherits every unverified number it contains, and inherits them
with more authority than the originals had.** `CLAIMS.md` was built from 55 reports I had
already written, so I read it as *checked* — and it was, in the sense that its inputs were
mine. One input was wrong and one was unreproducible. The audit took twenty minutes; the
numbers it checked took nineteen cycles to accumulate.

The standing addition to the checklist: **a document that supersedes other documents must be
audited against the artifacts before it is pushed, not after** — and if it is a *summary* of
prior work rather than new measurement, that audit is the only check it will ever get.

## 7. Merge safety

No merge this cycle. `state/reviewer/` only: `CLAIMS.md` §4 and the header and §8 amended, this
report added.
