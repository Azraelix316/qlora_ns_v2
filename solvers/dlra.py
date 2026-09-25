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
import time
from typing import Optional

import numpy as np

from .ns_psi import StreamFunctionNS
from .spectral import Grid2D, zonal_mean


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

    Rank selection offers two criteria, and which one is used is recorded in
    every artifact because the choice decides what the rank trace can see:

    ``rank_criterion="amplitude"`` (the historical default) counts modes above
    ``relative_amplitude_cutoff * s[0]``.  It is an amplitude test, so 1e-6 is
    an energy ratio of 1e-12, and in practice it selects the grid's dealiasing
    ceiling: the dealiased candidate has a nine-order cliff at the band edge and
    no further significant modes, so the retained rank is the grid's, not the
    dynamics'.

    ``rank_criterion="energy"`` keeps the smallest r with
    ``sum(s[:r]**2)/sum(s**2) >= energy_fraction`` -- an r99-style rule.  It is
    a far better-behaved criterion than the amplitude test: it leaves the
    dealiasing ceiling behind and selects a physically meaningful number.  It
    is **not**, however, the criterion that tracks the sixteenfold rank growth
    measured on forced 2-D NS, and the earlier version of this docstring said
    so.  The reason is the distinction spelled out below: the growth is a
    *windowed* quantity and this rule reads an *instantaneous* one.

    **Which quantity a criterion measures is part of its meaning, so artifacts
    record it.**  Both rules above act on a single stage candidate, and the
    rank they return is therefore a *spatial* rank -- the dimension of the
    subspace one field needs -- not the dimension of the subspace a trajectory
    sweeps through.  A rank trace labelled only "rank" is ambiguous between the
    two, which is how the ceiling and the windowed growth got conflated.

    Both are clamped to ``[min_rank, max_rank]``.  Neither is an accuracy
    criterion: they say how many modes to keep, not how close the result is.

    **``rank_basis`` decides whose energy is counted.**  This is not cosmetic
    at late times: the zonal mean grows secularly and holds 94% of the total
    energy by t=20 (measured), so an energy fraction of the *whole state* is
    eventually reached by the mean alone, while the fluctuation fraction -- the
    one R26 measured and the one S1 requires of every statistic here -- does
    not.  ``rank_basis="fluctuations"`` ranks on the zonal-mean-removed field,
    costing one extra spectrum computation (``compute_uv=False``, so no
    singular vectors are formed) per projection; the projection itself is
    unchanged and still acts on the whole state.

    **What no choice of criterion or basis can do, measured.**  A per-step rule
    reads one state at a time, so it can only ever select the *instantaneous*
    rank.  On the canonical case at t=8 the final state's own r99 is **2** (on
    the fluctuations as well as on the whole state), while the r99 of the
    *window* [0, 8] -- the modes needed to represent the 401 snapshots the
    trajectory passes through -- is **14**.  The growth R26 measures is
    therefore a property of the subspace the trajectory *visits*, not of any
    single state, and a per-step instantaneous rule does not approach it: the
    energy criterion moves the selection off the dealiasing ceiling and onto a
    physically meaningful ~2, but 2 is not 16 and no threshold on one snapshot
    will make it so.  Tracking the windowed rank needs a method that
    accumulates the visited subspace over a window, which this per-step
    truncation is not.

    **Cost model, as implemented (this is today's behaviour, not a design
    goal).** ``_svd`` factorizes the **whole N x N field** at four stage
    boundaries per step, so per-step cost is Theta(N^3) and
    **rank-independent**: r=2 and r=64 cost the same, because the truncated
    reconstruction only changes which *columns* of an already-computed
    factorization are used.  The V6 port (per-stage rank update) is expected to
    **invert** this property, and two tests pin it so the change is visible as
    a test failing rather than as a claim in prose: ``test_full_field_svd_is_rank_independent``
    (the factorization must return the full N-value spectrum for any rank) and
    ``test_svd_call_count_per_step`` (four whole-field factorizations per step).
    """

    def __init__(
        self,
        grid: Grid2D,
        rank: int = 4,
        min_rank: int = 2,
        max_rank: int = 64,
        relative_amplitude_cutoff: float = 1e-6,
        rank_criterion: str = "amplitude",
        energy_fraction: float = 0.99,
        rank_basis: str = "state",
        rank_window: int = 20,
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
        if rank_criterion not in ("amplitude", "energy", "window_energy"):
            raise ValueError(
                "rank_criterion must be 'amplitude', 'energy' or 'window_energy'"
            )
        if not 0.0 < float(energy_fraction) < 1.0:
            raise ValueError("energy_fraction must lie in (0,1)")
        if rank_basis not in ("state", "fluctuations"):
            raise ValueError("rank_basis must be 'state' or 'fluctuations'")
        if int(rank_window) < 1:
            raise ValueError("rank_window must be at least 1")
        if int(min_rank) > grid.N:
            raise ValueError("min_rank cannot exceed the physical matrix rank")
        self.grid = grid
        self.min_rank = int(min_rank)
        # A square N x N physical field cannot have rank above N.
        self.max_rank = min(int(max_rank), grid.N)
        self.rank = min(int(rank), self.max_rank)
        self.relative_amplitude_cutoff = float(relative_amplitude_cutoff)
        self.rank_criterion = rank_criterion
        self.energy_fraction = float(energy_fraction)
        self.rank_basis = rank_basis
        self.rank_window = int(rank_window)
        self._window_fields: list[np.ndarray] = []
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
        # Measured factorization time, for the two cost accountings R5q
        # requires: linear algebra alone, and the full step.
        self.svd_seconds = 0.0
        self.svd_calls = 0
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
        # The windowed rank rule's own memory.  A retained candidate from an
        # earlier run would make the new run's rank depend on where it started,
        # which is exactly the state leakage `reset` exists to prevent.
        self._window_fields = []
        self.svd_seconds = 0.0
        self.svd_calls = 0

    def reset_counters_only(self) -> None:
        """Zero the measured factorization time without touching the rank.

        Used when a caller projects once to obtain a starting state and then
        wants the per-step cost of the steps alone.
        """
        self.svd_seconds = 0.0
        self.svd_calls = 0

    def _svd(self, field: np.ndarray):
        centered = np.asarray(field, dtype=float)
        if centered.shape != (self.grid.N, self.grid.N):
            raise ValueError(
                f"field shape {centered.shape} does not match grid {(self.grid.N, self.grid.N)}"
            )
        if not np.isfinite(centered).all():
            raise FloatingPointError("cannot SVD-project a non-finite state")
        centered = centered - np.mean(centered)
        start = time.perf_counter()
        u, s, vh = np.linalg.svd(centered, full_matrices=False)
        self.svd_seconds += time.perf_counter() - start
        self.svd_calls += 1
        return centered, u, s, vh

    def _rank_spectrum(self, field: np.ndarray, s: np.ndarray) -> np.ndarray:
        """The singular values the *rank rule* reads.

        Equal to the projection's own spectrum unless ``rank_basis`` asks for
        the fluctuations, in which case the zonal mode is removed first.  The
        extra spectrum is computed without singular vectors, and it is only
        computed when the rule actually needs it.
        """
        if self.rank_criterion == "window_energy":
            return self._window_spectrum(field)
        if self.rank_basis == "state" or self.rank_criterion != "energy":
            return s
        prime = np.asarray(field, dtype=float) - zonal_mean(field)
        if not np.isfinite(prime).all():
            return s
        try:
            return np.linalg.svd(prime, compute_uv=False)
        except np.linalg.LinAlgError:
            return s

    def _window_spectrum(self, field: np.ndarray) -> np.ndarray:
        r"""Spectrum of the **stacked** recent candidates, not of one field.

        This is the quantity R26 measures: how many modes are needed to
        represent a *window* of the trajectory.  A per-step rule reading one
        state at a time cannot approach it -- measured, the instantaneous r99 at
        t=8 is 2 against a windowed 14 -- so this rule keeps the last
        ``rank_window`` candidates and takes the singular values of the matrix
        they form as columns.

        The spectrum of an ``N^2 x n`` stacked matrix is the square root of the
        eigenvalues of its ``n x n`` Gram matrix, so no large factorization is
        needed: the cost is ``n`` inner products of length ``N^2`` per candidate,
        i.e. O(n N^2), which is negligible beside the four whole-field
        factorizations the step already pays.  The Gram is formed from the
        fluctuations when ``rank_basis="fluctuations"``, so the secularly growing
        zonal mean cannot dominate the energy fraction.

        The window is a *sliding* one over the candidates this projector has
        seen, oldest dropped first.
        """
        n = int(self.rank_window)
        if n < 1:
            return np.zeros(0)
        candidate = np.asarray(field, dtype=float)
        if self.rank_basis == "fluctuations":
            candidate = candidate - zonal_mean(candidate)
        flat = candidate.reshape(-1)
        if not np.isfinite(flat).all():
            return np.zeros(0)
        self._window_fields.append(flat)
        if len(self._window_fields) > n:
            self._window_fields = self._window_fields[-n:]
        # Gram of the retained candidates, built column by column so the cost is
        # one inner product per stored field rather than an N^2 x N^2 matrix.
        k = len(self._window_fields)
        gram = np.empty((k, k))
        for i in range(k):
            for j in range(i, k):
                value = float(self._window_fields[i] @ self._window_fields[j])
                gram[i, j] = value
                gram[j, i] = value
        try:
            eigenvalues = np.linalg.eigvalsh(gram)
        except np.linalg.LinAlgError:
            return np.zeros(0)
        return np.sqrt(np.clip(eigenvalues, 0.0, None))[::-1]

    def _target_from_spectrum(self, s: np.ndarray) -> int:
        """Retained rank for the configured criterion, clipped to the bounds."""
        if s.size == 0 or s[0] <= np.finfo(float).eps:
            return self.min_rank
        if self.rank_criterion in ("energy", "window_energy"):
            # Smallest r whose leading energy fraction reaches the target.  The
            # cumulative sum is taken in descending order, so this is the
            # Eckart--Young rank for the requested energy fraction.
            energy = np.cumsum(s.astype(float) ** 2)
            total = energy[-1]
            if total <= 0.0:
                return self.min_rank
            reached = int(np.searchsorted(energy, self.energy_fraction * total) + 1)
            numerical = min(reached, s.size)
        else:
            numerical = int(
                np.count_nonzero(s > self.relative_amplitude_cutoff * s[0])
            )
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
            self.rank = self._target_from_spectrum(self._rank_spectrum(field, s))
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
        # ``centered`` is spatially mean-free but still carries the zonal mode,
        # so it is the right input for the fluctuation spectrum.
        self.rank = self._target_from_spectrum(self._rank_spectrum(centered, s))
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
        rank_criterion: str = "amplitude",
        energy_fraction: float = 0.99,
        rank_basis: str = "state",
        rank_window: int = 20,
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
            rank_criterion=rank_criterion,
            energy_fraction=energy_fraction,
            rank_basis=rank_basis,
            rank_window=rank_window,
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
