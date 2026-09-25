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
            X = arr.reshape(self.grid.N * self.grid.N, arr.shape[0])
        self.mean = np.mean(X, axis=1).reshape(self.grid.N, self.grid.N)
        centered = X - self.mean.reshape(-1, 1)
        U, s, _ = np.linalg.svd(centered, full_matrices=False)
        r = min(self.requested_rank, U.shape[1])
        self.basis = U[:, :r]
        self.singular_values = s.copy()
        # The stream-function equations preserve the zero spatial mean.  Keep
        # the fitted mean for diagnostics/general use, but remove roundoff mean
        # from the actual basis states.
        self.mean -= np.mean(self.mean)
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
        out = out.reshape(self.grid.N, self.grid.N)
        return out - np.mean(out)

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
