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
