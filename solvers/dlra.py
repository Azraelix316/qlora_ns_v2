"""Dynamical low-rank projection and adaptive-rank driver.

This module implements a *projected stream-function DLRA* discretization:
the nonlinear residual is evaluated on the current full field, then an
explicit SVD projector is applied at split-stage boundaries.  It is not a
claim that the factor ODEs of a factorized Fourier DLRA have been eliminated;
the experiment driver reports the resulting SVD cost honestly.

The stream-function constant is an irrelevant gauge.  SVD inputs are centered,
but the truncated reconstruction is not mean-subtracted a second time (that
would add a rank-one constant).  The integrator centers before physical
operators, so divergence-freeness is unaffected.
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
    """Rank-r projector with candidate-stage tracking and rank adaptation.

    Rank selection is an **amplitude** test, not an accuracy criterion: the
    retained rank counts the singular values above
    ``relative_amplitude_cutoff * s[0]``.  Because singular values are
    amplitudes, a cutoff of 1e-6 keeps modes down to an *energy* ratio of
    1e-12, so the parameter is deliberately not called a tolerance and must not
    be described as one.
    """

    def __init__(
        self,
        grid: Grid2D,
        rank: int = 4,
        min_rank: int = 2,
        max_rank: int = 64,
        relative_amplitude_cutoff: float = 1e-6,
    ):
        integer_values = (rank, min_rank, max_rank)
        if any(int(value) != value for value in integer_values):
            raise ValueError("rank, min_rank, and max_rank must be integers")
        if not 0 < int(min_rank) <= int(max_rank):
            raise ValueError("require 0 < min_rank <= max_rank")
        if not int(min_rank) <= int(rank) <= int(max_rank):
            raise ValueError("rank must lie between min_rank and max_rank")
        if not 0.0 < float(relative_amplitude_cutoff) < 1.0:
            raise ValueError("relative_amplitude_cutoff must lie in (0,1)")
        if int(min_rank) > grid.N:
            raise ValueError("min_rank cannot exceed the physical matrix rank")
        self.grid = grid
        self.min_rank = int(min_rank)
        # A square N x N physical field cannot have rank above N.
        self.max_rank = min(int(max_rank), grid.N)
        self.rank = min(int(rank), self.max_rank)
        self.relative_amplitude_cutoff = float(relative_amplitude_cutoff)
        self.last_stats: Optional[RankStats] = None
        self.last_singular_values = np.empty(0, dtype=float)
        self._last_u: Optional[np.ndarray] = None
        self._last_s: Optional[np.ndarray] = None
        self._last_vh: Optional[np.ndarray] = None
        self._last_centered: Optional[np.ndarray] = None
        self._stage_candidates: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
        # The configured rank, restored by ``reset()`` so a reused projector
        # cannot start a new run at the rank a previous run adapted to.
        self.nominal_rank = self.rank
        self.reset()

    def reset(self) -> None:
        """Clear every piece of learned state and restore the configured rank.

        A projector carries state across steps: the last SVD, the retained
        per-stage candidates, the statistics, and an adapted rank.  Reusing one
        object across runs would let a later run inherit the earlier run's
        rank, its adaptation schedule, and even a stale stage candidate, so
        every fresh run must begin from the configured rank with nothing
        retained.
        """
        self.rank = self.nominal_rank
        self.last_stats = None
        self.last_singular_values = np.empty(0, dtype=float)
        self._last_u = None
        self._last_s = None
        self._last_vh = None
        self._last_centered = None
        self._stage_candidates = {}

    def _svd(self, field: np.ndarray):
        centered = np.asarray(field, dtype=float)
        if centered.shape != (self.grid.N, self.grid.N):
            raise ValueError(
                f"field shape {centered.shape} does not match grid {(self.grid.N, self.grid.N)}"
            )
        if not np.isfinite(centered).all():
            raise FloatingPointError("cannot SVD-project a non-finite state")
        centered = centered - np.mean(centered)
        u, s, vh = np.linalg.svd(centered, full_matrices=False)
        return centered, u, s, vh

    def _target_from_spectrum(self, s: np.ndarray) -> int:
        if s.size == 0 or s[0] <= np.finfo(float).eps:
            return self.min_rank
        numerical = int(np.count_nonzero(s > self.relative_amplitude_cutoff * s[0]))
        return max(self.min_rank, min(self.max_rank, numerical))

    def _record_svd(
        self,
        centered: np.ndarray,
        u: np.ndarray,
        s: np.ndarray,
        vh: np.ndarray,
        stage: Optional[str] = None,
    ) -> None:
        self._last_centered = centered
        self._last_u = u
        self._last_s = s
        self._last_vh = vh
        if stage is not None:
            self._stage_candidates[stage] = (centered, u, s, vh)
        numerical = (
            int(np.count_nonzero(s > self.relative_amplitude_cutoff * s[0]))
            if s.size and s[0] > 0
            else 0
        )
        self.last_stats = RankStats(
            target_rank=self.rank,
            numerical_rank=numerical,
            singular_values=s.copy(),
        )
        self.last_singular_values = s.copy()

    def _reconstruct(
        self,
        centered: np.ndarray,
        u: np.ndarray,
        s: np.ndarray,
        vh: np.ndarray,
    ) -> np.ndarray:
        r = min(self.rank, s.size)
        if r:
            out = (u[:, :r] * s[:r]) @ vh[:r, :]
        else:
            out = np.zeros_like(centered)
        # Do not subtract the reconstruction's mean here; see module docstring.
        return out

    def project(
        self,
        field: np.ndarray,
        adapt: bool = False,
        stage: Optional[str] = None,
    ) -> np.ndarray:
        """Project ``field`` and optionally record the untruncated candidate."""
        centered, u, s, vh = self._svd(field)
        self._record_svd(centered, u, s, vh, stage=stage)
        if adapt:
            self.rank = self._target_from_spectrum(s)
        return self._reconstruct(centered, u, s, vh)

    def project_stage(self, field: np.ndarray, stage: str) -> np.ndarray:
        return self.project(field, adapt=False, stage=stage)

    def __call__(self, field: np.ndarray) -> np.ndarray:
        return self.project(field, adapt=False)

    def candidate(self, stage: str):
        """Return the retained untruncated SVD candidate for a named stage."""
        return self._stage_candidates.get(stage)

    def _set_rank_from_candidate(self, candidate) -> None:
        centered, u, s, vh = candidate
        self.rank = self._target_from_spectrum(s)
        self._last_centered, self._last_u, self._last_s, self._last_vh = candidate
        numerical = (
            int(np.count_nonzero(s > self.relative_amplitude_cutoff * s[0]))
            if s.size and s[0] > 0
            else 0
        )
        self.last_stats = RankStats(
            target_rank=self.rank,
            numerical_rank=numerical,
            singular_values=s.copy(),
        )
        self.last_singular_values = s.copy()

    def adapt(self, field: np.ndarray) -> np.ndarray:
        """Select rank from a supplied field and return its projection."""
        return self.project(field, adapt=True)

    def adapt_candidate(self, candidate) -> np.ndarray:
        """Select rank from a retained untruncated stage candidate."""
        if candidate is None:
            raise RuntimeError("no retained stage candidate is available")
        self._set_rank_from_candidate(candidate)
        return self._reconstruct(*candidate)

    def adapt_last(self) -> np.ndarray:
        """Adapt using the most recently recorded SVD candidate."""
        if self._last_u is None or self._last_s is None or self._last_vh is None:
            raise RuntimeError("no projector candidate is available")
        return self.adapt_candidate(
            (self._last_centered, self._last_u, self._last_s, self._last_vh)
        )


class DLRA:
    """Adaptive-rank wrapper around the shared stream-function stepper."""

    def __init__(
        self,
        model: StreamFunctionNS,
        rank: int = 4,
        min_rank: int = 2,
        max_rank: int = 64,
        relative_amplitude_cutoff: float = 1e-6,
        check_every: int = 5,
        adapt_initial: bool = False,
    ):
        if int(check_every) != check_every or check_every < 1:
            raise ValueError("check_every must be a positive integer")
        self.model = model
        self.projector = SVDProjector(
            model.grid,
            rank=rank,
            min_rank=min_rank,
            max_rank=max_rank,
            relative_amplitude_cutoff=relative_amplitude_cutoff,
        )
        self.check_every = int(check_every)
        self.adapt_initial = bool(adapt_initial)
        self.steps = 0
        self.rank_history: list[int] = [self.projector.rank]
        self.spectrum_history: list[np.ndarray] = []
        self.last_step_info: dict = {}

    @property
    def rank(self) -> int:
        return self.projector.rank

    def initialize(self, psi: np.ndarray) -> np.ndarray:
        """Reset all learned state, then project the initial condition.

        ``DLRA`` is reusable: the projector's rank, retained SVD candidates and
        statistics, the step counter, and the rank/spectrum histories are all
        cleared here.  Without this a second run would inherit the first run's
        adapted rank and its adaptation schedule, and could even adapt on a
        stage candidate left over from the previous run -- a plausible-looking
        trajectory that is not the one the configuration describes.
        """
        self.projector.reset()
        self.steps = 0
        self.rank_history = []
        self.spectrum_history = []
        self.last_step_info = {}
        field = np.asarray(psi, dtype=float)
        if self.adapt_initial:
            projected = self.projector.adapt(field)
        else:
            projected = self.projector.project(field)
        # With an adaptive initialisation the projector's rank may have moved
        # away from the nominal rank recorded in ``__init__``; keep
        # ``rank_history`` aligned with the state that was actually returned.
        self.rank_history = [self.projector.rank]
        return projected

    def _record(self, state: np.ndarray) -> None:
        self.rank_history.append(self.projector.rank)
        self.spectrum_history.append(self.projector.last_singular_values.copy())

    def step(self, psi: np.ndarray, dt: float, t: float = 0.0) -> np.ndarray:
        # The model records ``after_nonlinear`` before its projection.  At an
        # adaptation checkpoint, use that untruncated candidate rather than
        # the already-projected final state; otherwise nonlinear modes lost at
        # the stage projection could never trigger rank growth.
        state = self.model.step(psi, dt, projector=self.projector, t=t)
        step_info = dict(self.model.last_step_info)
        self.steps += 1
        if self.steps % self.check_every == 0:
            candidate = self.projector.candidate("after_nonlinear")
            if candidate is not None:
                centered, u, s, vh = candidate
                candidate_field = (u * s) @ vh
                before_adapt = self.model.grid.ke(candidate_field)
                state = self.projector.adapt_candidate(candidate)
                after_adapt = self.model.grid.ke(state)
                extra_projection_work = after_adapt - before_adapt
                state = self.model.diffuse(state, 0.5 * dt)
                before_final = self.model.grid.ke(state)
                state = self.projector(state)
                extra_projection_work += self.model.grid.ke(state) - before_final
                step_info["projection_energy_increment"] = float(
                    step_info.get("projection_energy_increment", 0.0)
                    + extra_projection_work
                )
                step_info["projection_count"] = int(step_info.get("projection_count", 0)) + 2
            else:
                state = self.projector.adapt_last()
        self.last_step_info = step_info
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
