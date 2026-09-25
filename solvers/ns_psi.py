"""Structure-preserving stream-function time integration for 2-D NS.

The state is the real stream function ``psi`` with

    u = (d_y psi, -d_x psi),       omega = -Delta psi.

Consequently every state produced by the solver, including a truncated
low-rank state, has zero divergence by construction.  The split integrator
uses an exact diffusion semigroup and a midpoint treatment of the
advection-plus-vorticity-forcing term.  Full-grid, static-POD, and DLRA runs
all call the same :meth:`StreamFunctionNS.step` kernel.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

from .forcing import ZeroForcing
from .spectral import Grid2D

Projector = Callable[[np.ndarray], np.ndarray]


@dataclass(frozen=True)
class EnergyTerms:
    """Instantaneous terms in the kinetic-energy balance."""

    energy: float
    dissipation: float
    forcing_input: float
    advection_input: float

    def residual_from_derivative(self, denergy_dt: float) -> float:
        """Return the kinetic-energy balance residual (ideal zero)."""
        # E = 1/2 ||grad psi||^2, so the viscous term is nu||omega||^2.
        # The advection contribution is retained as a signed diagnostic;
        # for an exactly divergence-free 2-D velocity it vanishes.
        return float(
            denergy_dt
            + self.dissipation
            - self.forcing_input
            + self.advection_input
        )


class StreamFunctionNS:
    """Split integrator for the 2-D incompressible Navier--Stokes equations.

    Parameters
    ----------
    grid:
        Fourier grid.
    nu:
        Kinematic viscosity.
    forcing:
        Object exposing ``vorticity(grid, t)``.  The default is unforced.
    dealias:
        Apply the rectangular 2/3-rule to the nonlinear product.  The forcing
        is resolved independently and is not filtered.
    """

    def __init__(
        self,
        grid: Grid2D,
        nu: float,
        forcing=None,
        dealias: bool = True,
    ):
        if nu < 0.0:
            raise ValueError("nu must be non-negative")
        self.grid = grid
        self.nu = float(nu)
        self.forcing = ZeroForcing() if forcing is None else forcing
        self.dealias = bool(dealias)
        self.step_count = 0
        self.track_step_diagnostics = False
        self.last_step_info: dict = {}

    # -- operators ---------------------------------------------------------
    def _dealias_field(self, field: np.ndarray) -> np.ndarray:
        if not self.dealias:
            return field
        return self.grid.ifft(self.grid.fft(field) * self.grid.dealias_mask)

    def advection(self, psi: np.ndarray) -> np.ndarray:
        """Return ``(u.grad) omega`` with optional 2/3 dealiasing."""
        grid = self.grid
        psi = self._dealias_field(psi)
        u, v = grid.velocity(psi)
        omega = grid.vorticity(psi)
        omega_x, omega_y = grid.grad(omega)
        q_hat = grid.fft(u * omega_x + v * omega_y)
        if self.dealias:
            q_hat *= grid.dealias_mask
        return grid.ifft(q_hat)

    def nonlinear_forcing(self, psi: np.ndarray, t: float = 0.0) -> np.ndarray:
        """RHS of the non-diffusive split, ``Delta^{-1}(zeta-adv)``."""
        grid = self.grid
        adv = self.advection(psi)
        zeta = self.forcing.vorticity(grid, t)
        if np.shape(zeta) != psi.shape:
            raise ValueError(f"forcing shape {np.shape(zeta)} does not match state {psi.shape}")
        # inv_lap solves -Delta phi=g.  Thus Delta^{-1}g=-inv_lap(g).
        return -grid.inv_lap(adv - zeta)

    def rhs(self, psi: np.ndarray, t: float = 0.0) -> np.ndarray:
        """Full unsplit PDE right-hand side, useful for manufactured tests."""
        return self.nu * self.grid.lap(psi) + self.nonlinear_forcing(psi, t)

    def diffuse(self, psi: np.ndarray, dt: float) -> np.ndarray:
        """Exact heat semigroup applied to psi."""
        F = self.grid.fft(psi)
        return self.grid.ifft(np.exp(-self.nu * self.grid.k2 * dt) * F)

    # -- integration --------------------------------------------------------
    @staticmethod
    def _apply_projector(projector: Projector, field: np.ndarray, stage: str) -> np.ndarray:
        if hasattr(projector, "project_stage"):
            return projector.project_stage(field, stage)
        return projector(field)

    def step(
        self,
        psi: np.ndarray,
        dt: float,
        projector: Optional[Projector] = None,
        t: float = 0.0,
    ) -> np.ndarray:
        """Advance one Strang/midpoint split step.

        The diffusion semigroup is exact.  The remaining advection and
        forcing term is advanced by an explicit midpoint method.  Supplying a
        projector gives the same discrete evolution on a reduced manifold;
        the full-grid reference uses ``projector=None``.
        """
        if dt <= 0.0:
            raise ValueError("dt must be positive")
        state = np.asarray(psi, dtype=float)
        state = state - np.mean(state)
        state = self.diffuse(state, 0.5 * dt)
        projection_energy = 0.0
        if projector is not None:
            before = self.grid.ke(state) if self.track_step_diagnostics else 0.0
            state = np.asarray(
                self._apply_projector(projector, state, "after_diffusion_half"),
                dtype=float,
            )
            if self.track_step_diagnostics:
                projection_energy += self.grid.ke(state) - before

        y0 = self.nonlinear_forcing(state, t)
        midpoint = state + 0.5 * dt * y0
        if projector is not None:
            before = self.grid.ke(midpoint) if self.track_step_diagnostics else 0.0
            midpoint = np.asarray(
                self._apply_projector(projector, midpoint, "after_midpoint"),
                dtype=float,
            )
            if self.track_step_diagnostics:
                projection_energy += self.grid.ke(midpoint) - before
        ymid = self.nonlinear_forcing(midpoint, t + 0.5 * dt)
        state = state + dt * ymid
        if projector is not None:
            before = self.grid.ke(state) if self.track_step_diagnostics else 0.0
            state = np.asarray(
                self._apply_projector(projector, state, "after_nonlinear"),
                dtype=float,
            )
            if self.track_step_diagnostics:
                projection_energy += self.grid.ke(state) - before

        state = self.diffuse(state, 0.5 * dt)
        if projector is not None:
            before = self.grid.ke(state) if self.track_step_diagnostics else 0.0
            state = np.asarray(
                self._apply_projector(projector, state, "after_diffusion_half_final"),
                dtype=float,
            )
            if self.track_step_diagnostics:
                projection_energy += self.grid.ke(state) - before
        self.step_count += 1
        self.last_step_info = {
            "projection_energy_increment": float(projection_energy),
            "projection_count": 0 if projector is None else 4,
        }
        return state

    def integrate(
        self,
        psi: np.ndarray,
        dt: float,
        nsteps: int,
        projector: Optional[Projector] = None,
        t0: float = 0.0,
        callback: Optional[Callable[[int, float, np.ndarray], None]] = None,
    ) -> np.ndarray:
        """Integrate ``nsteps`` times and optionally report each state."""
        if nsteps < 0:
            raise ValueError("nsteps must be non-negative")
        state = np.asarray(psi, dtype=float).copy()
        for n in range(nsteps):
            state = self.step(state, dt, projector=projector, t=t0 + n * dt)
            if callback is not None:
                callback(n + 1, t0 + (n + 1) * dt, state)
        return state

    # -- diagnostics --------------------------------------------------------
    def energy_terms(self, psi: np.ndarray, t: float = 0.0) -> EnergyTerms:
        """Compute energy and all work/dissipation terms at a state.

        ``advection_input`` is retained explicitly rather than assumed to be
        zero.  For the exact incompressible velocity equation it vanishes up
        to roundoff, and exposing it makes the diagnostic useful for reduced
        models and for diagnosing a bad time step.
        """
        grid = self.grid
        omega = grid.vorticity(psi)
        adv = self.advection(psi)
        zeta = self.forcing.vorticity(grid, t)
        if np.shape(zeta) != psi.shape:
            raise ValueError(f"forcing shape {np.shape(zeta)} does not match state {psi.shape}")
        return EnergyTerms(
            energy=grid.ke(psi),
            dissipation=self.nu * grid.l2_sq(omega),
            forcing_input=grid.l2_dot(psi, zeta),
            advection_input=grid.l2_dot(psi, adv),
        )
