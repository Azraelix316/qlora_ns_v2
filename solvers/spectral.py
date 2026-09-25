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


class Grid2D:
    """Uniform periodic 2D grid with rfft-based spectral operators."""

    def __init__(self, N: int, L: float = 2.0 * np.pi):
        self.N = N
        self.L = L
        self.dx = L / N
        self.n = N * N
        # numpy's rfftn leaves axis 0 full and halves axis 1.  The physical
        # coordinates use the same convention: x is axis 0, y is axis 1.
        # fftfreq returns cycles per unit length; convert to angular
        # wavenumbers (the default L=2*pi therefore gives integer modes).
        kx = 2.0 * np.pi * np.fft.fftfreq(N, d=L / N)
        ky = 2.0 * np.pi * np.fft.fftfreq(N, d=L / N)[: N // 2 + 1]
        self.kx = kx
        self.ky = ky
        self.k2 = kx[:, None] ** 2 + ky[None, :] ** 2
        self.x = np.arange(N, dtype=float) * self.dx
        self.y = self.x.copy()
        # Parseval weights on the rfft half-grid: a mode counts once on each
        # Nyquist/zero mirror plane, otherwise it pairs with its conjugate.
        w = 2.0 * np.ones((N, N // 2 + 1))
        w[0, :] = 1.0
        w[:, 0] = 1.0
        if N % 2 == 0:
            # kx=Nyquist is row N/2; in the rfft half-spectrum ky=Nyquist is
            # the final column.  The last kx row is -1, not a self-conjugate
            # mode (except in the accidental N=2 case, handled below).
            if N == 2:
                w[-1, :] = 1.0
            else:
                w[N // 2, :] = 1.0
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
        return np.fft.irfftn(F, s=(self.N, self.N))

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

    def grad(self, f: np.ndarray):
        F = self.fft(f)
        fx = self.ifft(1j * self.kx[:, None] * F)
        fy = self.ifft(1j * self.ky[None, :] * F)
        return fx, fy

    def velocity(self, psi: np.ndarray):
        """Velocity from the stream function: u = (psi_y, -psi_x)."""
        F = self.fft(psi)
        u = self.ifft(1j * self.ky[None, :] * F)
        v = self.ifft(-1j * self.kx[:, None] * F)
        return u, v

    def vorticity(self, psi: np.ndarray) -> np.ndarray:
        """Vorticity omega = curl(u) = -Lap(psi) for u=(psi_y,-psi_x)."""
        return self.ifft(self.k2 * self.fft(psi))

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
        """||Lap psi||^2 = integral |grad omega|^2 (dissipation integrand)."""
        return self.spec_norm_sq(-self.k2 * self.fft(psi), self.k2)

    def max_div_velocity(self, psi: np.ndarray) -> float:
        """max |div u| of the velocity *round-tripped* through real space.

        u and v are built as real fields from psi and re-differentiated
        spectrally from those fields; the result measures only floating-point
        roundoff, since div u = 0 holds structurally.
        """
        u, v = self.velocity(psi)
        div = self.ifft(
            1j * self.kx[:, None] * self.fft(u)
            + 1j * self.ky[None, :] * self.fft(v)
        )
        return float(np.max(np.abs(div)))
