"""Forcing primitives for the two-dimensional stream-function solver.

The solver evolves the scalar vorticity source ``zeta`` rather than a
momentum pressure decomposition.  ``KolmogorovForcing`` represents the
periodic pump

    f = (A sin(k y), 0),

whose curl under our convention ``omega = d_x v - d_y u`` is
``zeta = -A k cos(k y)``.  Since ``d_x f_x = 0`` this force is itself
divergence-free, while its curl is a single resolved Fourier mode.  This is
the periodic analogue of the usual Kolmogorov body-force driver.

A frozen source returned by :class:`SelfConsistentForcing` is also provided;
it is useful for manufactured fixed-point tests and for reproducible
validation runs.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from .spectral import Grid2D


class ZeroForcing:
    """Unforced dynamics."""

    def vorticity(self, grid: Grid2D, t: float = 0.0) -> np.ndarray:
        return np.zeros((grid.N, grid.N), dtype=float)

    def velocity(self, grid: Grid2D, t: float = 0.0):
        return (
            np.zeros((grid.N, grid.N), dtype=float),
            np.zeros((grid.N, grid.N), dtype=float),
        )

    def energy_input(self, psi: np.ndarray, grid: Grid2D, t: float = 0.0) -> float:
        return 0.0


class KolmogorovForcing:
    """A time-independent periodic Kolmogorov pump.

    Parameters
    ----------
    amplitude:
        Strength ``A`` of the x-momentum body force.
    wavenumber:
        Angular wavenumber ``k`` of the y dependence.
    phase:
        Phase shift in radians.
    """

    def __init__(self, amplitude: float = 1.0, wavenumber: float = 1.0, phase: float = 0.0):
        if amplitude == 0.0:
            raise ValueError("amplitude must be nonzero for a Kolmogorov driver")
        if wavenumber <= 0.0:
            raise ValueError("wavenumber must be positive")
        self.amplitude = float(amplitude)
        self.wavenumber = float(wavenumber)
        self.phase = float(phase)
        self._last_t: Optional[float] = None
        self._last_zeta: Optional[np.ndarray] = None

    def _y(self, grid: Grid2D) -> np.ndarray:
        # Broadcast along x (axis 0), y is axis 1.
        return grid.y[None, :] + self.phase

    def velocity(self, grid: Grid2D, t: float = 0.0):
        fx = self.amplitude * np.sin(self.wavenumber * self._y(grid))
        fx = np.broadcast_to(fx, (grid.N, grid.N)).copy()
        fy = np.zeros((grid.N, grid.N), dtype=float)
        return fx, fy

    def vorticity(self, grid: Grid2D, t: float = 0.0) -> np.ndarray:
        # A harmless cache matters for long runs, while returning a copy keeps
        # callers from accidentally mutating the cached source.
        if self._last_t == t and self._last_zeta is not None:
            return self._last_zeta.copy()
        z = -self.amplitude * self.wavenumber * np.cos(
            self.wavenumber * self._y(grid)
        )
        z = np.broadcast_to(z, (grid.N, grid.N)).copy()
        self._last_t = float(t)
        self._last_zeta = z
        return z.copy()

    def streamfunction(self, grid: Grid2D, t: float = 0.0) -> np.ndarray:
        """Stream function whose rotated gradient is the body force."""
        # If chi = -A/k cos(k y), then (chi_y, -chi_x) = (A sin(k y), 0).
        chi = -(self.amplitude / self.wavenumber) * np.cos(
            self.wavenumber * self._y(grid)
        )
        return np.broadcast_to(chi, (grid.N, grid.N)).copy()

    def energy_input(self, psi: np.ndarray, grid: Grid2D, t: float = 0.0) -> float:
        return grid.l2_dot(psi, self.vorticity(grid, t))


class FrozenVorticityForcing:
    """Wrap a fixed scalar vorticity source array."""

    def __init__(self, zeta: np.ndarray):
        self.zeta = np.asarray(zeta, dtype=float).copy()

    def vorticity(self, grid: Grid2D, t: float = 0.0) -> np.ndarray:
        if self.zeta.shape != (grid.N, grid.N):
            raise ValueError(
                f"forcing shape {self.zeta.shape} does not match grid {(grid.N, grid.N)}"
            )
        return self.zeta.copy()

    def velocity(self, grid: Grid2D, t: float = 0.0):
        # The source need not be divergence-free; this method is only a
        # diagnostic convenience and is intentionally not used by the solver.
        return np.zeros_like(self.zeta), np.zeros_like(self.zeta)

    def energy_input(self, psi: np.ndarray, grid: Grid2D, t: float = 0.0) -> float:
        return grid.l2_dot(psi, self.vorticity(grid, t))


class SelfConsistentForcing(FrozenVorticityForcing):
    """Construct a source making a reference state stationary.

    For a reference state ``psi_ref`` and the same nonlinear operator used by
    the solver, set ``zeta = adv(psi_ref) - nu * Delta omega_ref``.  The full
    stream-function right-hand side then vanishes at ``psi_ref``.  This is a
    manufactured forcing, not the Kolmogorov driver; it is intended for
    validation and unit tests.
    """

    @classmethod
    def from_state(
        cls,
        grid: Grid2D,
        reference: np.ndarray,
        nu: float,
        advection=None,
        dealias: bool = True,
    ) -> "SelfConsistentForcing":
        if advection is None:
            # Local import avoids a module cycle at package import time.
            from .ns_psi import StreamFunctionNS

            advection = StreamFunctionNS(grid, nu=nu, forcing=ZeroForcing(), dealias=dealias).advection
        omega = grid.vorticity(reference)
        zeta = advection(reference) - nu * grid.lap(omega)
        return cls(zeta)
