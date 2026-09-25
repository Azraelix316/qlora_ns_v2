"""Spectral utilities for 2D periodic fields (stream-function formulation).

Conventions
-----------
- Domain: [0, L)^2, periodic, L = 2*pi.  Uniform N x N grid, dx = L/N.
- All operators are defined through numpy's *unnormalized* rfftn/irfftn.
- The stream function psi is real, mean-zero, and
  u = grad_perp(psi) = (d_y psi, -d_x psi),  omega = -Lap psi,
  so div u = 0 holds by construction (up to floating-point roundoff).
"""
from __future__ import annotations

import numpy as np


def zonal_mean(psi: np.ndarray) -> np.ndarray:
    """The streamwise-uniform part of a state, ``x-avg(psi)``.

    Axis 0 is x in this grid's convention, so averaging over it leaves a
    y-profile.  In a forced 2-D problem with an unidirectional shear this mode
    can grow secularly -- the zonal momentum equation has no restoring term on
    it -- which is why every statistic in this project is computed on
    ``psi - zonal_mean(psi)`` with the zonal part reported alongside, rather
    than mixed in.
    """
    psi = np.asarray(psi, dtype=float)
    return np.broadcast_to(psi.mean(axis=0), psi.shape)


def fluctuations(psi: np.ndarray) -> np.ndarray:
    """``psi' = psi - x-avg(psi)``: the state with the zonal mode removed."""
    return np.asarray(psi, dtype=float) - zonal_mean(psi)


class Grid2D:
    """Uniform periodic 2D grid with rfft-based spectral operators."""

    def __init__(self, N: int, L: float = 2.0 * np.pi):
        self.N = N
        self.L = L
        self.dx = L / N
        self.n = N * N
        # numpy's rfftn leaves axis 0 full and halves axis 1.  The physical
        # coordinates use the same convention: x is axis 0, y is axis 1.
        # fftfreq/rfftfreq return cycles per unit length; convert to angular
        # wavenumbers (the default L=2*pi therefore gives integer modes).
        kx = 2.0 * np.pi * np.fft.fftfreq(N, d=L / N)
        ky = 2.0 * np.pi * np.fft.rfftfreq(N, d=L / N)
        self.kx = kx
        self.ky = ky
        self.k2 = kx[:, None] ** 2 + ky[None, :] ** 2
        # NOTE on the Nyquist mode (measured, not assumed).  The x-Nyquist
        # sample of a real field is self-conjugate, so a real-space central
        # difference cannot recover its x-derivative (the stencil aliases it to
        # zero).  The *spectral* derivative is a different matter: numpy's
        # irfftn inverts axis 0 as a complex spectrum, so the 2D Hermitian
        # symmetry of rfft output is preserved and no coefficient is silently
        # dropped.  Keeping the true wavenumber in first derivatives is what
        # makes u = (psi_y, -psi_x) divergence-free mode by mode for *any* psi,
        # including states whose x-Nyquist row is populated -- which SVD
        # projections do, since a truncated SVD fills the whole grid.  Zeroing
        # the Nyquist multiplier instead would delete v's Nyquist row while
        # keeping u's, and the divergence of the resulting real velocity field
        # becomes O(1) (measured 8.0 at N=16 for a Nyquist+smooth field).
        # Exact divergence-freeness by representation is the project's central
        # invariant, so it wins over derivative accuracy on an aliased mode
        # that the 2/3 dealias mask excludes from the dynamics anyway.
        self.x = np.arange(N, dtype=float) * self.dx
        self.y = self.x.copy()
        # Parseval weights on the rfft half-grid.  Since axis 0 is a full
        # x-axis, the only self-conjugate planes in the half spectrum are
        # ky=0 and (for even N) ky=Nyquist.  All other columns contain one
        # member of a conjugate pair and therefore have weight two.
        w = 2.0 * np.ones((N, N // 2 + 1))
        w[:, 0] = 1.0
        if N % 2 == 0:
            w[:, -1] = 1.0
        self.w = w
        # Rectangular 2/3 dealiasing mask for pseudospectral products.
        cutoff = (2.0 / 3.0) * (N // 2)
        self.dealias_mask = (np.abs(kx)[:, None] <= cutoff) & (
            np.abs(ky)[None, :] <= cutoff
        )

    # -- basic transforms -------------------------------------------------
    def fft(self, f: np.ndarray) -> np.ndarray:
        return np.fft.rfftn(f)

    def ifft(self, F: np.ndarray) -> np.ndarray:
        return np.fft.irfftn(F, s=(self.N, self.N), axes=(0, 1))

    # -- differential operators -------------------------------------------
    def lap(self, f: np.ndarray) -> np.ndarray:
        """Laplacian (kills the mean automatically)."""
        return self.ifft(-self.k2 * self.fft(f))

    def inv_lap(self, g: np.ndarray) -> np.ndarray:
        """Solve -Lap phi = g with zero mean."""
        G = self.fft(g)
        F = np.zeros_like(G)
        m = self.k2 != 0
        F[m] = G[m] / self.k2[m]
        return self.ifft(F)

    def _full_spectrum(self, F: np.ndarray) -> np.ndarray:
        """Reconstruct the full last-axis spectrum from the rfft half-spectrum.

        ``rfftn`` keeps axis 0 full and halves axis 1, and for a real field the
        missing columns are ``F_full[k, N-j] = conj(F_half[N-k, j])`` -- note
        the *k-flip*.  ``irfftn`` instead assumes ``F[k, N-j] = conj(F[k, j])``,
        which is a different field.  The two agree for fields whose spectrum is
        symmetric in k, and disagree by O(1) otherwise, so any operator whose
        multiplier depends on k cannot be applied to a half spectrum and then
        inverted with ``irfftn``.
        """
        tail = np.conj(self._flip_x(F[:, 1:-1]))
        return np.concatenate([F, tail], axis=1)

    def _flip_x(self, A: np.ndarray) -> np.ndarray:
        """Reverse axis 0, the full x-axis."""
        return A[::-1, :]

    def _deriv(self, f: np.ndarray, axis: int) -> np.ndarray:
        """Spectral first derivative, correct for any real field.

        The full spectrum is formed first, the real wavenumber multiplier is
        applied to it, and the inverse is a plain complex ``ifft2``.  The cost
        is O(N^2 log N) with a factor ~2 over the half-spectrum route, which is
        negligible beside the Theta(N^3) factorization this project actually
        pays for, and correctness is not optional: the nonlinear term is built
        from these derivatives.

        Both axes use ``kx``, which is already ``2*pi*fftfreq`` over the *full*
        grid; ``ky`` is the rfft half-axis and is not the right multiplier for a
        full-spectrum inversion.
        """
        if axis not in (0, 1):
            raise ValueError("axis must be 0 (x) or 1 (y)")
        arr = np.asarray(f, dtype=float)
        F = np.fft.fft2(arr)
        mult = self.kx[:, None] if axis == 0 else self.kx[None, :]
        return np.fft.ifft2(1j * mult * F).real

    def grad(self, f: np.ndarray):
        """(d/dx f, d/dy f), exact for any real field including full-band ones."""
        return self._deriv(f, 0), self._deriv(f, 1)

    def velocity(self, psi: np.ndarray):
        """Velocity from the stream function: u = (psi_y, -psi_x)."""
        return self._deriv(psi, 1), -self._deriv(psi, 0)

    def vorticity(self, psi: np.ndarray) -> np.ndarray:
        """Vorticity omega = curl(u) = -Lap(psi) for u=(psi_y,-psi_x)."""
        return self.ifft(self.k2 * self.fft(psi))

    def factor_semigroup(
        self, factor: np.ndarray, tau: float, nu: float
    ) -> np.ndarray:
        r"""Exact heat semigroup applied to one low-rank factor.

        Writing the state as ``Y = U S V^T`` with ``U``'s rows indexing ``x``
        and ``V``'s rows indexing ``y``, a field-level diffusion is a
        left-multiplication by ``A_x = nu * Delta_x`` and a right-multiplication
        by ``A_y = nu * Delta_y``, so

            e^{\nu\tau\Delta}Y
                = (e^{\nu\tau\Delta_x}U)\,S\,(e^{\nu\tau\Delta_y}V)^{T},
            \qquad (e^{\nu\tau\Delta_y}V)^{T} = V^{T}e^{\nu\tau\Delta_y T}.

        **Both factors are therefore transformed along axis 0** -- the leading
        axis is the spatial one in each case, with ``U`` carrying ``x`` and ``V``
        carrying ``y``.  Applying the ``y`` semigroup along ``V``'s columns
        would be transforming its ``r`` singular-value directions instead, which
        is a different operator.

        This is what lets a BUG step avoid any full-size factorization: the
        factors keep their rank exactly and the cost is two length-``N`` FFTs per
        factor column, O(N r log N).

        The full-grid wavenumber array ``kx`` is used with a full ``fft``/``ifft``,
        matching :meth:`_deriv`: the rfft half-axis is not a valid multiplier for
        a full-spectrum inversion.
        """
        arr = np.asarray(factor)
        if arr.ndim != 2:
            raise ValueError(f"expected a 2-D factor, got shape {arr.shape}")
        if arr.shape[0] != self.N:
            raise ValueError(
                f"factor's leading axis is {arr.shape[0]}, expected N={self.N}"
            )
        spectrum = np.fft.fft(arr, axis=0)
        mult = np.exp(-nu * self.kx ** 2 * tau)[:, None]
        return np.fft.ifft(spectrum * mult, axis=0).real

    # -- norms / diagnostics ------------------------------------------------
    def l2_sq(self, f: np.ndarray) -> float:
        """L2 norm squared on [0,L)^2 (real-space)."""
        return (self.L ** 2 / self.n) * float(np.sum(f * f))

    def l2_dot(self, f: np.ndarray, g: np.ndarray) -> float:
        """Signed real-space L2 inner product on [0,L)^2."""
        if f.shape != g.shape:
            raise ValueError(f"shape mismatch in L2 dot: {f.shape} versus {g.shape}")
        return (self.L ** 2 / self.n) * float(np.sum(f * g))

    def spec_norm_sq(self, F: np.ndarray, k2: np.ndarray | None = None) -> float:
        """Parseval norm for unnormalized rfft coefficients.

        For the half-spectrum the conjugate-mode weight is ``w`` and the
        real-space integral is ``L^2/N^4`` times the weighted coefficient sum
        (the rfft coefficients are unnormalized).  ``k2`` optionally supplies
        the spectral multiplier (e.g. ``|grad f|^2``).
        """
        A = F.real ** 2 + F.imag ** 2
        if k2 is not None:
            A = k2 * A
        return (self.L ** 2 / self.n ** 2) * float(np.sum(self.w * A))

    def ke(self, psi: np.ndarray) -> float:
        """Kinetic energy E = 1/2 ||grad psi||^2 via Parseval."""
        return 0.5 * self.spec_norm_sq(self.fft(psi), self.k2)

    def enstrophy(self, psi: np.ndarray) -> float:
        """||omega||^2 / 2."""
        return 0.5 * self.spec_norm_sq(self.k2 * self.fft(psi))

    def laplacian_enstrophy(self, psi: np.ndarray) -> float:
        """Integral |grad omega|² (enstrophy-dissipation integrand)."""
        return self.spec_norm_sq(-self.k2 * self.fft(psi), self.k2)

    def isotropic_spectra(self, psi: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Shell-summed isotropic energy and enstrophy spectra of ``psi``.

        Returns ``(k, E, Z)`` with integer shell index ``k`` (unit spacing, which
        is the mode spacing on ``[0,2*pi)^2``) and

            E(k) = 1/2 (L^2/N^4) sum_{shell} w k^2 |F|^2 ,
            Z(k) = 1/2 (L^2/N^4) sum_{shell} w k^4 |F|^2 ,

        so that ``sum(E)`` reproduces ``ke(psi)`` and ``sum(Z)`` reproduces
        ``enstrophy(psi)`` to roundoff.  Modes are assigned to shells by
        rounding ``|k|`` to the nearest integer, which keeps the sum exact and
        avoids the half-shell bookkeeping that would otherwise lose energy at
        the bin edges.

        This is a spectrum of a *state*; it is not a spectrum of a problem, and
        a rank-truncated reduced state has only as many values as its rank.  It
        must be computed on the full-grid reference (and, for agreement checks,
        on the reduced state), never read off a rank-``r`` state's own
        singular values.
        """
        F = self.fft(np.asarray(psi, dtype=float))
        if not np.isfinite(psi).all():
            return np.empty(0), np.empty(0), np.empty(0)
        radius = np.sqrt(self.k2)
        shell = np.rint(radius).astype(int)
        k_max = int(shell.max())
        energy = np.zeros(k_max + 1, dtype=float)
        enstrophy = np.zeros(k_max + 1, dtype=float)
        weight = self.w * (F.real**2 + F.imag**2)
        prefactor = 0.5 * (self.L**2 / self.n**2)
        np.add.at(energy, shell.ravel(), (weight * self.k2).ravel())
        np.add.at(enstrophy, shell.ravel(), (weight * self.k2**2).ravel())
        energy *= prefactor
        enstrophy *= prefactor
        k = np.arange(k_max + 1, dtype=float)
        return k, energy, enstrophy

    def max_divergence(self, u: np.ndarray, v: np.ndarray) -> float:
        """max |div u| of an *explicit* velocity field, measured spectrally.

        This is the diagnostic itself, exposed so that a test can feed it a
        field that is known **not** to be divergence-free and confirm it
        reports O(1).  Without that negative control, an invariant that holds
        by representation would be a vacuous test: it would pass for any
        implementation, including a broken one.

        It differentiates with ``grad``, i.e. the *same* operator ``velocity``
        uses.  Differentiating by a different route would measure the
        disagreement between two spectral conventions rather than the
        divergence of the field.
        """
        if u.shape != v.shape or u.shape != (self.N, self.N):
            raise ValueError(f"velocity shape {u.shape}/{v.shape} does not match grid")
        ux, _ = self.grad(u)
        _, vy = self.grad(v)
        return float(np.max(np.abs(ux + vy)))

    def max_div_velocity(self, psi: np.ndarray) -> float:
        """max |div u| of the velocity *round-tripped* through real space.

        u and v are built as real fields from psi and re-differentiated
        spectrally from those fields; the result measures only floating-point
        roundoff, since div u = 0 holds structurally.
        """
        u, v = self.velocity(psi)
        return self.max_divergence(u, v)
