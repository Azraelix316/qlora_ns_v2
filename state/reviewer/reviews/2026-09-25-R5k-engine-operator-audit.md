# R5k — independent operator audit of the engine: one latent bug found, inert in production

**Date:** 2026-09-25 · **Reviewer cycle:** R5 (addendum 5) · **Target:** the
merged engine on `main` (`solvers/` at `b2f78fd`) · **Method:** independent
operator verification, references constructed by the reviewer rather than reused
from the implementation.

## Why this audit exists

R5 verified the engine by re-running the author's 13 tests and hand-checking the
algebra. That has a blind spot by construction: a test suite shares any
misconception with the code it tests, and every field in the suite is smooth or
band-limited. This audit checks the *operators* against references built
independently — a full 2-D spectrum (no rFFT half-spectrum machinery), integer
arithmetic for the 2/3-rule mask, and an independently manufactured forcing.

## Result: 18 checks pass, 3 fail — and the 3 share one root cause

Passing, against references the engine does not use:

| Check | Error |
|---|---|
| `lap == -k² ψ` (full spectrum) | 2.3e-13 |
| `vorticity == -Δψ` (full spectrum) | 2.3e-13 |
| `u == ∂_y ψ` (full spectrum) | 1.1e-14 |
| `div u == 0` (full-spectrum divergence) | see below |
| `inv_lap(lap f) == -(f-mean)` and `inv_lap(-lap f) == f-mean` | 7.8e-15 |
| `lap` kills the mean | 8.0e-16 |
| `⟨u, ∇ψ⟩ == 0` (identity behind the energy balance) | 0.0 |
| Parseval `spec_norm(fft f) == l2_sq(f)` | 0.0 |
| 2/3 mask keeps exactly `|k| ≤ floor(N/3)` per direction, Nyquist excluded | exact |
| dealiasing is a no-op for a resolved product | 6.8e-15 |
| dealiasing suppresses aliased content (with a working positive control) | ratio 9.3e-18 |
| manufactured steady state: `rhs == 0` | 2.9e-16 |
| **energy identity with an independently built `ζ`** | **6.0e-17** |
| exact heat semigroup on a (1,1) mode | 5.6e-16 |
| Taylor–Green `ω == 2ψ` | 5.8e-14 |

The aliased-content control is worth stating explicitly, because it is the check
that proves the dealiasing does something: on a full-band input the
out-of-band amplitude is **1.09e+06 undealiased** and **1.02e-11 dealiased**.

## The finding: the x-Nyquist wavenumber is used in derivative multipliers

`Grid2D` builds `kx = 2π·fftfreq(N)`, which for even `N` contains `kx[N//2] =
−N/2`, and then multiplies by it in `velocity()` and `grad()`. For a **real**
field the x-Nyquist mode is self-conjugate: its derivative cannot be
represented by simply multiplying by `i·kx` and inverse-transforming, because
the result is no longer the spectrum of a real field. The standard convention
is to set that wavenumber to zero in derivative multipliers.

Evidence (N=32, `f` a full-band random field):

- `max |v_engine − (−∂_x ψ)_full-spectrum| = 7.48`
- setting `kx[N//2] = 0` in the multiplier: the same error drops to **1.07e-14**
- for a field with no Nyquist content (`|k| ≤ 5`): `u`, `v` and `div u` all agree
  with the full-spectrum reference to **~1e-15**

**Scope — why this is non-blocking, stated precisely.** It is inert in every
committed run: dealiasing zeroes `|k| > floor(N/3)`, and the initial condition
is band-limited to `|k_x|,|k_y| ≤ 8` (N=64) or `≤ 12` (N=128), so `kx = ±N/2`
never carries energy. It cannot affect the 13 passing tests, all of which use
smooth or band-limited fields. It is a **latent** correctness issue that would
bite a user who calls `velocity()` or `grad()` on a full-band field — for
instance on the unfiltered diagnostic fields, or on any future input that is not
pre-filtered.

**Recommended fix** (coder's call, one line plus a test): introduce a separate
derivative wavenumber array, e.g. `self.kx_diff = self.kx.copy()` with
`self.kx_diff[N//2] = 0.0` for even `N`, and use it in `grad()` and
`velocity()`. Do **not** zero it inside `k2` — the Laplacian eigenvalue at the
Nyquist mode is legitimate, and overwriting `kx` would silently change `lap`.
Add a test on a full-band field asserting `v == −∂_x ψ` and `u == ∂_y ψ` against
a full 2-D spectrum; that test fails on the current code and is the one the
suite is missing.

## A note on my own process, since it nearly produced a false report

My first three audit runs reported failures that were **my** errors, not the
engine's: I asserted `inv_lap(lap f) == f` (it solves `−Δφ = g`, so it is `−f`);
I expected a circular 2/3 cutoff when the mask is correctly rectangular per
direction; and my "independent curl" reference was itself built through the
ambiguous rFFT route, which is how the Nyquist issue surfaced at all. Each time
the correct move was to construct the reference more carefully rather than to
accept the first discrepancy — and the fourth run, using a full 2-D spectrum,
showed the engine matching to 2e-13 on everything except the one real issue.
An independent check is only as good as the reference it compares against; the
three "failures" I could not immediately explain were the signal to stop and
re-derive, not evidence against the code.

## Consequence for the review record

D9 (engine approved) **stands** — this is a latent issue outside the operating
regime, it does not affect any committed result, and the fix is small. It is
recorded here and sent to `coder` as a non-blocking item, and the missing test
is added to the standing checklist.
