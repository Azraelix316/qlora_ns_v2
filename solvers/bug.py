"""Midpoint BUG integrator (Ceruti, Einkemmer, Kusch & Lubich 2024).

Implemented from the primary text, arXiv:2402.08607, Sections 2 and 3 -- not
from a summary.  The scheme is the one the paper calls *Midpoint BUG (4r)*:

    1. **Midpoint approximation.**  One augmented-BUG step of size h/2
       (Section 2) gives a rank-``rhat <= 2r`` approximation
       ``Yhat_1/2 = Uhat S_1/2 Vhat^T`` at ``t_1/2 = t0 + h/2``:

         K-step   Kdot = F(t, K V0^T) V0,          K(t0) = U0 S0
         Uhat     = orth(U0, K(t1))               Mhat = Uhat^T U0
         L-step   Ldot = F(t, U0 L^T)^T U0,       L(t0) = V0 S0^T
         Vhat     = orth(V0, L(t1))               Nhat = Vhat^T V0
         S-step   Shatdot = Uhat^T F(t, Uhat Shat Vhat^T) Vhat,
                  Shat(t0) = Mhat S0 Nhat^T

    2. **Galerkin step** in bases augmented by one midpoint correction,
       so the intermediate rank is at most 4r (equation (10)):

         Ubar = orth(Uhat_1/2, h F(t_1/2, Yhat_1/2) Vhat_1/2)
         Vbar = orth(Vhat_1/2, h F(t_1/2, Yhat_1/2)^T Uhat_1/2)
         Mbar = Ubar^T U0,  Nbar = Vbar^T V0
         Sbardot = Ubar^T F(t, Ubar Sbar Vbar^T) Vbar,
                  Sbar(t0) = Mbar S0 Nbar^T,  integrated t0 -> t1

    3. **Truncation.**  An SVD of the small ``Sbar(t1)`` (rbar x rbar) reduces
       the result to rank r, or to whatever rank a tolerance on its singular
       values selects.

The ``variant="3r"`` option of Remark 1 is also available: augmenting with
``U0``/``V0`` as well keeps the intermediate rank at 3r, which is cheaper and
less accurate.

**Why this is the port that matters.**  The only factorization in the whole
step is of the ``rbar x rbar`` matrix ``Sbar(t1)``; everything else is
O(N r^2) or smaller.  The scheme implemented in ``dlra.py`` instead factorizes
the entire N x N field four times per step, which is Theta(N^3) and
rank-independent.  So the cost difference is structural, not a tuning matter.

**What is *not* claimed.**  BUG's usual selling point is robustness against
small singular values, because the classical factor ODEs contain ``S^-1``.
This engine never had that problem -- it recomputed a full SVD each stage -- so
a robustness improvement over our own code is not available and is not claimed.
The honest claims are the cost, the Galerkin step in the augmented basis (the
mathematically meaningful change, and per Remark 3 the route to norm/energy/
dissipation preservation in the same situations as the plain augmented BUG),
and second order with rank adaptivity.
"""
from __future__ import annotations

import time
from typing import Optional

import numpy as np

from .ns_psi import StreamFunctionNS


def _orth(A: np.ndarray, B: Optional[np.ndarray] = None) -> np.ndarray:
    """Orthonormal basis of the range of ``[A, B]`` (thin QR of the columns).

    Rank-deficient directions are kept as orthonormal columns rather than
    dropped: the augmented ``S``-matrix then has a zero row/column for the
    spurious direction and the truncation SVD removes it.  This is
    mathematically the same subspace and avoids a rank decision here that the
    truncation step is there to make.
    """
    M = A if B is None else np.hstack([A, B])
    Q, _ = np.linalg.qr(M, mode="reduced")
    return Q


class BUGIntegrator:
    """Midpoint BUG for the stream-function RHS, with rank truncation.

    The state is the stream function as an N x N matrix, so ``m = n = N`` and
    the factors are ``N x r``.  The right-hand side supplied by the model is
    applied to *fields*; the augmentation directions need it applied to one
    field and then multiplied by a factor, which is all this class needs.
    """

    def __init__(
        self,
        model: StreamFunctionNS,
        rank: int = 4,
        min_rank: int = 1,
        max_rank: int = 64,
        relative_amplitude_cutoff: float = 1e-6,
        substeps: int = 2,
        variant: str = "4r",
    ):
        if substeps < 1:
            raise ValueError("substeps must be at least 1")
        if variant not in ("3r", "4r"):
            raise ValueError("variant must be '3r' or '4r'")
        if int(min_rank) < 1 or int(max_rank) < int(min_rank):
            raise ValueError("require 1 <= min_rank <= max_rank")
        self.model = model
        self.grid = model.grid
        self.min_rank = int(min_rank)
        self.max_rank = min(int(max_rank), self.grid.N)
        self.nominal_rank = min(int(rank), self.max_rank)
        self.relative_amplitude_cutoff = float(relative_amplitude_cutoff)
        self.substeps = int(substeps)
        self.variant = variant
        self.rank = self.nominal_rank
        # Cost accounting: the point of the port is that these are *small*
        # factorizations, so their dimension is recorded as well as their count.
        self.svd_seconds = 0.0
        self.svd_calls = 0
        self.svd_max_dimension = 0
        self.large_svd_calls = 0
        self.steps = 0
        self.rank_history: list[int] = []
        self.U: Optional[np.ndarray] = None
        self.S: Optional[np.ndarray] = None
        self.V: Optional[np.ndarray] = None

    # -- state -----------------------------------------------------------
    def _as_matrix(self, psi: np.ndarray) -> np.ndarray:
        arr = np.asarray(psi, dtype=float)
        if arr.shape != (self.grid.N, self.grid.N):
            raise ValueError(f"state shape {arr.shape} does not match the grid")
        return arr

    def _F(self, t: float, Y: np.ndarray) -> np.ndarray:
        """The right-hand side, applied to a field."""
        return self.model.nonlinear_forcing(Y, t)

    def initialize(self, psi: np.ndarray) -> np.ndarray:
        """Factorize the initial state; the only full-size SVD in the method."""
        Y = self._as_matrix(psi)
        centered = Y - np.mean(Y)
        U, s, Vt = np.linalg.svd(centered, full_matrices=False)
        r = self.nominal_rank
        self.U = U[:, :r].copy()
        self.S = np.diag(s[:r]).copy()
        self.V = Vt[:r, :].T.copy()
        self.rank = r
        self.svd_seconds = 0.0
        self.svd_calls = 0
        self.svd_max_dimension = 0
        self.large_svd_calls = 0
        self.steps = 0
        self.rank_history = [r]
        return self.state()

    def state(self) -> np.ndarray:
        """The approximated field ``U S V^T`` (no mean re-adding)."""
        if self.U is None:
            raise RuntimeError("BUGIntegrator.initialize must be called first")
        return self.U @ self.S @ self.V.T

    # -- the substeps ----------------------------------------------------
    def _rk2(self, dY, t0: float, h: float, rhs) -> np.ndarray:
        """Midpoint integration of ``dY = rhs(t, Y)`` over one substep."""
        k1 = rhs(t0, dY)
        k2 = rhs(t0 + 0.5 * h, dY + 0.5 * h * k1)
        return dY + h * k2

    def _integrate(self, dY, t0: float, h: float, rhs) -> np.ndarray:
        """Advance ``dY`` from t0 over h with ``substeps`` midpoint substeps."""
        if self.substeps == 1:
            return self._rk2(dY, t0, h, rhs)
        # Compose midpoint substeps: each is second order, so the composition
        # is too, and the extra substeps buy accuracy for the stiff stages.
        n = self.substeps
        for i in range(n):
            dY = self._rk2(dY, t0 + i * h / n, h / n, rhs)
        return dY

    def _diffuse_factors(self, tau: float) -> None:
        r"""Apply the exact heat semigroup to the factors, in place.

        ``e^{\nu\tau\Delta}Y = (e^{\nu\tau\Delta_x}U)\,S\,(e^{\nu\tau\Delta_y}V)^T``
        holds exactly, so the diffusion needs no factorization of the state at
        all.  Orthonormality is then restored by QR of the ``N x r`` factors --
        O(N r^2), not a factorization -- with ``R_u S R_v^T`` folded into the
        small matrix.  Reusing :meth:`initialize`'s full SVD here instead would
        have put a Theta(N^3) factorization back in every step and defeated the
        entire point of the port.
        """
        U = self.grid.factor_semigroup(self.U, tau, self.model.nu)
        V = self.grid.factor_semigroup(self.V, tau, self.model.nu)
        Uq, Ru = np.linalg.qr(U, mode="reduced")
        Vq, Rv = np.linalg.qr(V, mode="reduced")
        self.U, self.V = Uq, Vq
        self.S = Ru @ self.S @ Rv.T

    def _truncate(self, U: np.ndarray, S: np.ndarray, V: np.ndarray):
        """Truncate by an SVD of the small ``S`` (the only SVD in the step)."""
        start = time.perf_counter()
        Uc, s, Vt = np.linalg.svd(S, full_matrices=False)
        self.svd_seconds += time.perf_counter() - start
        self.svd_calls += 1
        self.svd_max_dimension = max(self.svd_max_dimension, int(S.shape[0]))
        if s.size == 0 or s[0] <= np.finfo(float).eps:
            keep = self.min_rank
        else:
            keep = int(np.count_nonzero(s > self.relative_amplitude_cutoff * s[0]))
            keep = max(self.min_rank, min(self.max_rank, keep))
        # Fold the rotation of S into the bases: U <- U Uc, V <- V Vc.
        U_new = U @ Uc[:, :keep]
        V_new = V @ Vt[:keep, :].T
        S_new = np.diag(s[:keep])
        return U_new, S_new, V_new

    def _augmented_bug(self, t0: float, h: float):
        """One augmented-BUG step (Section 2); returns the rank-rhat factors."""
        U0, S0, V0 = self.U, self.S, self.V
        # K-step (m x r): Kdot = F(t, K V0^T) V0, K(t0) = U0 S0.
        K = U0 @ S0
        K = self._integrate(
            K, t0, h, lambda t, k: self._F(t, k @ V0.T) @ V0
        )
        Uhat = _orth(U0, K)
        Mhat = Uhat.T @ U0
        # L-step (n x r): Ldot = F(t, U0 L^T)^T U0, L(t0) = V0 S0^T.
        L = V0 @ S0.T
        L = self._integrate(
            L, t0, h, lambda t, l: self._F(t, U0 @ l.T).T @ U0
        )
        Vhat = _orth(V0, L)
        Nhat = Vhat.T @ V0
        # S-step (rhat x rhat): Shatdot = Uhat^T F(t, Uhat Shat Vhat^T) Vhat.
        Shat = Mhat @ S0 @ Nhat.T
        Shat = self._integrate(
            Shat, t0, h,
            lambda t, s: Uhat.T @ self._F(t, Uhat @ s @ Vhat.T) @ Vhat,
        )
        return Uhat, Shat, Vhat

    def step(self, psi: Optional[np.ndarray] = None, dt: float = 0.0, t: float = 0.0) -> np.ndarray:
        """One midpoint-BUG step of size dt, then truncation back to rank r.

        The exact diffusion semigroup brackets the BUG step as a Strang split,
        matching how the projected integrator in ``dlra.py`` separates the stiff
        linear part; the BUG step itself advances the advective and forced part,
        which is what the paper's ``F`` reduces to once the linear part is
        integrated exactly.  ``psi`` is accepted for interface symmetry with
        ``DLRA.step`` and is **not** read: the factors are the state, and
        silently reinitializing from a field would discard the basis.
        """
        if self.U is None:
            raise RuntimeError("BUGIntegrator.initialize must be called first")
        if dt <= 0.0:
            raise ValueError("dt must be positive")
        self._diffuse_factors(0.5 * dt)

        t_half = t + 0.5 * dt
        # 1. midpoint approximation: augmented BUG over h/2
        Uhat, Shat, Vhat = self._augmented_bug(t, 0.5 * dt)
        # 2. Galerkin step in the augmented bases (equation (10))
        Y_half = Uhat @ Shat @ Vhat.T
        F_half = self._F(t_half, Y_half)
        if self.variant == "3r":
            Ubar = _orth_many(self.U, Uhat, dt * F_half @ Vhat)
            Vbar = _orth_many(self.V, Vhat, dt * F_half.T @ Uhat)
        else:
            Ubar = _orth(Uhat, dt * F_half @ Vhat)
            Vbar = _orth(Vhat, dt * F_half.T @ Uhat)
        Mbar = Ubar.T @ self.U
        Nbar = Vbar.T @ self.V
        Sbar = Mbar @ self.S @ Nbar.T
        Sbar = self._integrate(
            Sbar, t, dt,
            lambda t_, s_: Ubar.T @ self._F(t_, Ubar @ s_ @ Vbar.T) @ Vbar,
        )
        # 3. truncate back to a lower rank
        self.U, self.S, self.V = self._truncate(Ubar, Sbar, Vbar)
        self.rank = self.S.shape[0]
        self.steps += 1
        self.rank_history.append(self.rank)

        self._diffuse_factors(0.5 * dt)
        return self.state()

    def integrate(self, psi: np.ndarray, dt: float, nsteps: int, t0: float = 0.0) -> np.ndarray:
        self.initialize(psi)
        for i in range(nsteps):
            self.step(dt=dt, t=t0 + i * dt)
        return self.state()


def _orth_many(*blocks: np.ndarray) -> np.ndarray:
    """Orthonormal basis of the range of several blocks stacked column-wise."""
    A = None
    for b in blocks:
        if b is None:
            continue
        A = b if A is None else np.hstack([A, b])
    if A is None:
        raise ValueError("no blocks given")
    Q, _ = np.linalg.qr(A, mode="reduced")
    return Q
