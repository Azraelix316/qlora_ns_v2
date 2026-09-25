"""Static POD-Galerkin projection baseline for stream-function states."""
from __future__ import annotations

from typing import Iterable

import numpy as np

from .spectral import Grid2D


class PODGalerkin:
    """Orthogonal POD basis fitted to an offline snapshot trajectory.

    Snapshots are stream functions, so every projected state remains in the
    divergence-free class.  The nonlinear residual is still evaluated by the
    full spectral operator and then Galerkin-projected, making this a useful
    static-POD comparison rather than an unrelated surrogate model.

    Mean contract: snapshots are centered into the zero-spatial-mean class
    before the SVD, so ``mean`` and every basis column are mean-free and
    ``project`` is the exact L2-orthogonal projection onto
    ``span(mean) + span(basis)`` -- idempotent, with the residual orthogonal to
    both.  No spatial mean is added or removed afterwards.

    Rank contract: the fitted rank always equals ``requested_rank``; a request
    larger than the number of snapshot directions raises instead of clamping.
    """

    def __init__(self, grid: Grid2D, rank: int):
        if rank < 1:
            raise ValueError("rank must be positive")
        self.grid = grid
        self.requested_rank = int(rank)
        self.mean: np.ndarray | None = None
        self.basis: np.ndarray | None = None
        self.singular_values = np.empty(0, dtype=float)

    def fit(self, snapshots) -> "PODGalerkin":
        if isinstance(snapshots, np.ndarray) and snapshots.ndim == 2:
            X = snapshots.astype(float, copy=False)
            if X.shape != (self.grid.N, self.grid.N):
                raise ValueError("a single snapshot has the wrong shape")
            X = X.reshape(self.grid.N * self.grid.N, 1)
        else:
            arr = np.asarray(list(snapshots), dtype=float)
            if arr.ndim != 3 or arr.shape[1:] != (self.grid.N, self.grid.N):
                raise ValueError("snapshots must have shape (n, N, N)")
            # One column per snapshot, one row per grid point.  The order
            # matters: ``reshape(n, N*N)`` keeps each snapshot contiguous and
            # the transpose then stacks snapshots as columns.  Writing
            # ``arr.reshape(N*N, n)`` instead fills the new array in C order
            # and interleaves the snapshots, so the SVD is fitted to shuffled
            # data and the resulting basis is meaningless.
            X = arr.reshape(arr.shape[0], -1).T
        # The stream-function state lives in the zero-spatial-mean class: the
        # initial condition is mean-free and the equations preserve the mean
        # (it is a pure gauge).  Centering every snapshot into that class
        # *before* the SVD makes the stored mean and every basis column
        # mean-free, so ``project`` is the exact L2-orthogonal projection onto
        # span(mean) + span(basis).  This is the same centered matrix as
        # subtracting the snapshot mean, so it changes no fitted direction; it
        # only removes the need to fix up the mean afterwards.
        X = X - X.mean(axis=0, keepdims=True)
        self.mean = np.mean(X, axis=1).reshape(self.grid.N, self.grid.N)
        centered = X - self.mean.reshape(-1, 1)
        U, s, _ = np.linalg.svd(centered, full_matrices=False)
        # A truncated SVD of an (N^2, n) matrix returns exactly n columns, so
        # clamping the request to n would silently run a "rank r" comparison at
        # a lower rank than the artifact reports -- in the direction that
        # flatters the proposed method.  Fail loudly and make the caller supply
        # enough snapshots instead.
        if self.requested_rank > U.shape[1]:
            raise ValueError(
                f"requested rank {self.requested_rank} exceeds the "
                f"{U.shape[1]} snapshot directions available; supply at least "
                f"{self.requested_rank} snapshots so the fitted rank is the "
                "requested one"
            )
        self.basis = U[:, : self.requested_rank]
        self.singular_values = s.copy()
        return self

    def _check_fitted(self) -> None:
        if self.basis is None or self.mean is None:
            raise RuntimeError("PODGalerkin.fit must be called before projection")

    def project(self, field: np.ndarray) -> np.ndarray:
        self._check_fitted()
        f = np.asarray(field, dtype=float)
        if f.shape != (self.grid.N, self.grid.N):
            raise ValueError(f"field shape {f.shape} does not match grid")
        z = f.reshape(-1) - self.mean.reshape(-1)
        coeff = self.basis.T @ z
        out = self.mean.reshape(-1) + self.basis @ coeff
        return out.reshape(self.grid.N, self.grid.N)

    def __call__(self, field: np.ndarray) -> np.ndarray:
        return self.project(field)

    def relative_error(self, field: np.ndarray) -> float:
        f = np.asarray(field, dtype=float)
        p = self.project(f)
        f = f - np.mean(f)
        p = p - np.mean(p)
        denom = max(np.linalg.norm(f), np.finfo(float).eps)
        return float(np.linalg.norm(p - f) / denom)

    def effective_rank(self) -> int:
        self._check_fitted()
        return int(self.basis.shape[1])


def fit_pod(
    grid: Grid2D,
    snapshots: Iterable[np.ndarray],
    rank: int,
) -> PODGalerkin:
    """Convenience function used by benchmark drivers."""
    return PODGalerkin(grid, rank).fit(snapshots)


class PODDMD:
    """POD-DMD baseline: a fitted linear operator on a POD basis.

    This is the dynamic data-driven comparator F5 asks for, not a second copy
    of the static projection.  The basis and snapshot mean come from
    :class:`PODGalerkin`; the dynamics are a single linear operator ``A`` on the
    modal coefficients, fitted by least squares over a training segment:

        A = argmin ||C_{n+1} - A C_n||_F  =>  A = (C_n C_n^T)^-1 C_n C_{n+1}^T .

    The normal equations are accumulated **online**, one step at a time, so the
    memory is O(r^2) rather than O(n_snapshots * r).  That matters here: the
    training segment of a long run is tens of thousands of steps, and holding
    every snapshot would be gigabytes.

    The operator advances exactly one solver time step per application, so the
    baseline is compared on the same time grid as everything else (F5's "same
    dt policy").  A ridge term is available for conditioning and its value is
    recorded by the driver; ``ridge=0`` is plain least squares.
    """

    def __init__(self, pod: PODGalerkin, ridge: float = 0.0):
        if ridge < 0.0:
            raise ValueError("ridge must be non-negative")
        self.pod = pod
        self.ridge = float(ridge)
        self.operator: np.ndarray | None = None
        self._gram: np.ndarray | None = None
        self._cross: np.ndarray | None = None
        self.samples = 0
        self.singular_gram = False
        self._previous: np.ndarray | None = None

    # -- offline phase ----------------------------------------------------
    def accumulate(self, psi: np.ndarray) -> None:
        """Add one training sample; pairs it with the previous accumulated one."""
        pod = self.pod
        pod._check_fitted()
        c = pod.basis.T @ (np.asarray(psi, dtype=float).reshape(-1) - pod.mean.reshape(-1))
        if self._gram is None:
            r = pod.basis.shape[1]
            self._gram = np.zeros((r, r), dtype=float)
            self._cross = np.zeros((r, r), dtype=float)
        if self._previous is not None:
            self._gram += np.outer(self._previous, self._previous)
            # Least squares for A in min ||C_{n+1} - A C_n|| gives
            # A (C_n C_n^T) = C_{n+1} C_n^T, so the *next* coefficient goes on
            # the left of the outer product.  Transposing this silently fits
            # A^T, which a symmetric test operator can hide -- the dedicated
            # non-symmetric linear-system test exists for that reason.
            self._cross += np.outer(c, self._previous)
            self.samples += 1
        self._previous = c

    def fit(self) -> "PODDMD":
        """Solve the accumulated normal equations for ``A``."""
        if self._gram is None or self.samples == 0:
            raise RuntimeError("PODDMD.accumulate must be called before fit")
        gram = self._gram.copy()
        if self.ridge > 0.0:
            gram += self.ridge * np.trace(self._gram) / gram.shape[0] * np.eye(gram.shape[0])
        # A = C_{n+1} C_n^T (C_n C_n^T)^{-1}; the Gram is symmetric, so this is
        # solve(G, cross^T)^T.  A rank-deficient Gram (too few distinct training
        # directions) is reported and solved in the least-squares sense rather
        # than raising, because a baseline that refuses to fit is a harness
        # failure and not a finding.
        try:
            self.operator = np.linalg.solve(gram, self._cross.T).T
            self.singular_gram = False
        except np.linalg.LinAlgError:
            self.operator = np.linalg.lstsq(gram, self._cross.T, rcond=None)[0].T
            self.singular_gram = True
        return self

    # -- online phase -----------------------------------------------------
    def coefficients(self, psi: np.ndarray) -> np.ndarray:
        """Modal coordinates of a state, i.e. its projection in coefficient space."""
        pod = self.pod
        pod._check_fitted()
        f = np.asarray(psi, dtype=float)
        if f.shape != (pod.grid.N, pod.grid.N):
            raise ValueError(f"field shape {f.shape} does not match grid")
        return pod.basis.T @ (f.reshape(-1) - pod.mean.reshape(-1))

    def reconstruct(self, coefficients: np.ndarray) -> np.ndarray:
        """State for a set of modal coordinates: mean + B c, no mean fix-up."""
        pod = self.pod
        pod._check_fitted()
        out = pod.mean.reshape(-1) + pod.basis @ np.asarray(coefficients, dtype=float)
        return out.reshape(pod.grid.N, pod.grid.N)

    def initialize(self, psi: np.ndarray) -> np.ndarray:
        """Project the initial condition, giving the same bit-identical start.

        The online state is the exact L2 projection of the IC, which is the IC
        itself when the basis contains it -- the same P0 requirement the static
        baseline meets.
        """
        if self.operator is None:
            raise RuntimeError("PODDMD.fit must be called before use")
        return self.reconstruct(self.coefficients(psi))

    def step(self, coefficients: np.ndarray) -> np.ndarray:
        """Advance the modal coefficients by one time step."""
        if self.operator is None:
            raise RuntimeError("PODDMD.fit must be called before use")
        return self.operator @ np.asarray(coefficients, dtype=float)
