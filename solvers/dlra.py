"""Dynamical low-rank projection and adaptive-rank driver.

The implementation uses a stream-function field as the state and applies a
rank-r real SVD projector at every split-stage boundary.  This is a direct
Riemannian-projection form of a structure-preserving DLRA discretisation: any
linear combination of stream functions remains exactly divergence-free, while
the nonlinear term is evaluated on the current reduced state before projection.
The SVD is intentionally kept explicit (rather than hidden in a factorized
implementation) so singular-value diagnostics and honest wall-clock costs are
reproducible.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .ns_psi import StreamFunctionNS
from .spectral import Grid2D


@dataclass
class RankStats:
    target_rank: int
    numerical_rank: int
    singular_values: np.ndarray

    @property
    def leading(self) -> float:
        return float(self.singular_values[0]) if self.singular_values.size else 0.0


class SVDProjector:
    """Rank-r projector with an optional adaptive target rank.

    Inputs are centered before the SVD because the stream-function constant is
    an irrelevant gauge.  The truncated reconstruction is returned without a
    second mean subtraction: that subtraction would add a rank-one constant
    matrix.  The integrator discards the constant before applying physical
    operators, and error diagnostics compare centered states.
    """

    def __init__(
        self,
        grid: Grid2D,
        rank: int = 4,
        min_rank: int = 2,
        max_rank: int = 64,
        tolerance: float = 1e-6,
    ):
        if not 0 < min_rank <= max_rank:
            raise ValueError("require 0 < min_rank <= max_rank")
        if not min_rank <= rank <= max_rank:
            raise ValueError("rank must lie between min_rank and max_rank")
        if not 0.0 < tolerance < 1.0:
            raise ValueError("tolerance must lie in (0,1)")
        self.grid = grid
        self.min_rank = int(min_rank)
        self.max_rank = int(max_rank)
        self.rank = int(rank)
        self.tolerance = float(tolerance)
        self.last_stats: Optional[RankStats] = None
        self.last_singular_values = np.empty(0, dtype=float)
        # The final projector call in a split step sees the untruncated
        # candidate.  Retaining its factors lets rank adaptation see modes
        # that the current low-rank projection discarded, so growth is real
        # rather than an artifact of re-inspecting an already projected state.
        self._last_u: Optional[np.ndarray] = None
        self._last_s: Optional[np.ndarray] = None
        self._last_vh: Optional[np.ndarray] = None

    def _svd(self, field: np.ndarray):
        centered = np.asarray(field, dtype=float)
        if centered.shape != (self.grid.N, self.grid.N):
            raise ValueError(
                f"field shape {centered.shape} does not match grid {(self.grid.N, self.grid.N)}"
            )
        centered = centered - np.mean(centered)
        u, s, vh = np.linalg.svd(centered, full_matrices=False)
        return centered, u, s, vh

    def _target_from_spectrum(self, s: np.ndarray) -> int:
        if s.size == 0 or s[0] <= np.finfo(float).eps:
            return self.min_rank
        numerical = int(np.count_nonzero(s > self.tolerance * s[0]))
        return max(self.min_rank, min(self.max_rank, numerical))

    def _record_svd(self, centered: np.ndarray, u: np.ndarray, s: np.ndarray, vh: np.ndarray) -> None:
        self._last_u = u
        self._last_s = s
        self._last_vh = vh
        numerical = int(np.count_nonzero(s > self.tolerance * s[0])) if s.size and s[0] > 0 else 0
        self.last_stats = RankStats(
            target_rank=self.rank,
            numerical_rank=numerical,
            singular_values=s.copy(),
        )
        self.last_singular_values = s.copy()

    def _reconstruct(self, centered: np.ndarray, u: np.ndarray, s: np.ndarray, vh: np.ndarray) -> np.ndarray:
        r = min(self.rank, s.size)
        if r:
            out = (u[:, :r] * s[:r]) @ vh[:r, :]
        else:
            out = np.zeros_like(centered)
        # Do not subtract the reconstruction's mean here.  The stream
        # function has an irrelevant constant gauge; subtracting it after a
        # truncated SVD would add a rank-one constant and destroy exact rank
        # preservation.  The integrator centers the state before each physical
        # operator, and diagnostics use the centered field.
        return out

    def project(self, field: np.ndarray, adapt: bool = False) -> np.ndarray:
        """Project ``field`` onto the current (or newly selected) rank-r space."""
        centered, u, s, vh = self._svd(field)
        self._record_svd(centered, u, s, vh)
        if adapt:
            self.rank = self._target_from_spectrum(s)
        out = self._reconstruct(centered, u, s, vh)
        return out

    def __call__(self, field: np.ndarray) -> np.ndarray:
        return self.project(field, adapt=False)

    def adapt(self, field: np.ndarray) -> np.ndarray:
        """Select rank from the spectrum and return the projected state."""
        return self.project(field, adapt=True)

    def adapt_last(self) -> np.ndarray:
        """Adapt using the unprojected candidate from the latest projector call."""
        if self._last_u is None or self._last_s is None or self._last_vh is None:
            raise RuntimeError("no projector candidate is available")
        self.rank = self._target_from_spectrum(self._last_s)
        if self.last_stats is not None:
            self.last_stats = RankStats(
                target_rank=self.rank,
                numerical_rank=self.last_stats.numerical_rank,
                singular_values=self.last_stats.singular_values,
            )
        return self._reconstruct(
            (self._last_u * self._last_s) @ self._last_vh,
            self._last_u,
            self._last_s,
            self._last_vh,
        )


class DLRA:
    """Adaptive-rank wrapper around the shared stream-function stepper."""

    def __init__(
        self,
        model: StreamFunctionNS,
        rank: int = 4,
        min_rank: int = 2,
        max_rank: int = 64,
        tolerance: float = 1e-6,
        check_every: int = 5,
    ):
        if check_every < 1:
            raise ValueError("check_every must be positive")
        self.model = model
        self.projector = SVDProjector(
            model.grid,
            rank=rank,
            min_rank=min_rank,
            max_rank=max_rank,
            tolerance=tolerance,
        )
        self.check_every = int(check_every)
        self.steps = 0
        self.rank_history: list[int] = [self.projector.rank]
        self.spectrum_history: list[np.ndarray] = []

    @property
    def rank(self) -> int:
        return self.projector.rank

    def initialize(self, psi: np.ndarray) -> np.ndarray:
        return self.projector.project(np.asarray(psi, dtype=float))

    def _record(self, state: np.ndarray) -> None:
        self.rank_history.append(self.projector.rank)
        self.spectrum_history.append(self.projector.last_singular_values.copy())

    def step(self, psi: np.ndarray, dt: float, t: float = 0.0) -> np.ndarray:
        state = self.model.step(psi, dt, projector=self.projector, t=t)
        self.steps += 1
        if self.steps % self.check_every == 0:
            # The final projector call retained the untruncated candidate;
            # adapt from that candidate so discarded modes can cause growth.
            state = self.projector.adapt_last()
        self._record(state)
        return state

    def integrate(
        self,
        psi: np.ndarray,
        dt: float,
        nsteps: int,
        t0: float = 0.0,
        callback=None,
    ) -> np.ndarray:
        state = self.initialize(psi)
        for n in range(nsteps):
            state = self.step(state, dt, t=t0 + n * dt)
            if callback is not None:
                callback(n + 1, t0 + (n + 1) * dt, state)
        return state
