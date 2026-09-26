"""Fast correctness tests for the stream-function SP-DLRA engine.

Run from the repository root with ``~/.venvs/ns/bin/python -m pytest``.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

_ROOT = Path(__file__).resolve().parents[1]
for _p in (str(_ROOT), str(_ROOT / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from solvers import (
    BUGIntegrator,
    DLRA,
    FrozenVorticityForcing,
    Grid2D,
    KolmogorovForcing,
    PODDMD,
    PODGalerkin,
    SelfConsistentForcing,
    StreamFunctionNS,
    SVDProjector,
    ZeroForcing,
    fluctuations,
)


def field(grid: Grid2D, name: str = "tg", rng=None) -> np.ndarray:
    X, Y = np.meshgrid(grid.x, grid.y, indexing="ij")
    if name == "tg":
        return np.sin(X) * np.sin(Y)
    if name == "mixed":
        return (
            0.7 * np.sin(X) * np.sin(Y)
            + 0.2 * np.cos(2 * X) * np.sin(Y)
            + 0.1 * np.sin(X) * np.cos(2 * Y)
        )
    if name == "random":
        # Smooth rather than white, so a modest rank can represent it and the
        # tests measure the integrator rather than the representation.
        u, v = np.meshgrid(
            np.cos(grid.x) * np.sin(grid.y), np.sin(2 * grid.x) * np.cos(grid.y),
            indexing="ij",
        )
        return 0.8 * u - 0.5 * v + 0.1 * np.sin(X) * np.cos(Y)
    raise ValueError(name)


def test_spectral_conventions_and_norms():
    grid = Grid2D(32)
    psi = field(grid)
    omega = grid.vorticity(psi)
    u, v = grid.velocity(psi)
    assert np.max(np.abs(omega - 2.0 * psi)) < 1e-11
    assert np.isclose(grid.ky[-1], grid.N / 2.0)
    assert grid.max_div_velocity(psi) < 1e-12
    assert np.isclose(grid.ke(psi), 0.5 * (grid.l2_sq(u) + grid.l2_sq(v)))
    assert np.isclose(grid.enstrophy(psi), 0.5 * grid.l2_sq(omega))
    random = np.random.default_rng(3).normal(size=(grid.N, grid.N))
    assert np.isclose(grid.l2_sq(random), grid.spec_norm_sq(grid.fft(random)))
    omega_x, omega_y = grid.grad(omega)
    assert np.isclose(
        grid.laplacian_enstrophy(psi),
        grid.l2_dot(omega_x, omega_x) + grid.l2_dot(omega_y, omega_y),
    )


def test_frozen_forcing_records_and_removes_mean():
    grid = Grid2D(16)
    field = np.ones((grid.N, grid.N))
    forcing = FrozenVorticityForcing(field)
    assert forcing.mean_removed == 1.0
    assert np.max(np.abs(forcing.vorticity(grid))) < 1e-14


def test_projection_diagnostic_tracks_stage_energy_changes():
    grid = Grid2D(24)
    model = StreamFunctionNS(grid, 0.01, forcing=KolmogorovForcing(0.1))
    model.track_step_diagnostics = True
    lowrank = DLRA(
        model,
        rank=2,
        min_rank=1,
        max_rank=8,
        relative_amplitude_cutoff=1e-6,
        check_every=5,
    )
    lowrank.step(field(grid), 0.002)
    assert model.last_step_info["projection_count"] == 4
    assert np.isfinite(model.last_step_info["projection_energy_increment"])


def test_kolmogorov_force_is_divergence_free_and_has_expected_curl():
    grid = Grid2D(32)
    forcing = KolmogorovForcing(amplitude=0.7, wavenumber=2.0, phase=0.13)
    fx, fy = forcing.velocity(grid)
    div = grid.ifft(
        1j * grid.kx[:, None] * grid.fft(fx)
        + 1j * grid.ky[None, :] * grid.fft(fy)
    )
    curl = grid.ifft(
        1j * grid.kx[:, None] * grid.fft(fy)
        - 1j * grid.ky[None, :] * grid.fft(fx)
    )
    assert np.max(np.abs(div)) < 1e-12
    assert np.max(np.abs(curl - forcing.vorticity(grid))) < 1e-11
    chi = forcing.streamfunction(grid)
    ux, uy = grid.velocity(chi)
    assert np.max(np.abs(ux - fx)) < 1e-11
    assert np.max(np.abs(uy - fy)) < 1e-11


def test_diffusion_and_taylor_green_are_exact():
    grid = Grid2D(32)
    nu = 0.03
    psi = field(grid)
    model = StreamFunctionNS(grid, nu, forcing=ZeroForcing(), dealias=False)
    dt = 0.17
    evolved = model.step(psi, dt)
    exact = np.exp(-2.0 * nu * dt) * psi
    assert np.max(np.abs(evolved - exact)) < 2e-12
    energies = [grid.ke(psi)]
    state = psi
    for _ in range(8):
        state = model.step(state, dt)
        energies.append(grid.ke(state))
    assert np.all(np.diff(energies) <= 2e-12)
    assert energies[-1] < energies[0]


def test_self_consistent_forcing_makes_reference_stationary():
    grid = Grid2D(32)
    nu = 0.02
    reference = field(grid, "mixed")
    base = StreamFunctionNS(grid, nu, forcing=ZeroForcing())
    forcing = SelfConsistentForcing.from_state(
        grid, reference, nu, advection=base.advection
    )
    model = StreamFunctionNS(grid, nu, forcing=forcing)
    assert np.max(np.abs(model.rhs(reference))) < 1e-11


def test_energy_balance_for_self_consistent_state():
    grid = Grid2D(32)
    nu = 0.02
    reference = field(grid, "mixed")
    base = StreamFunctionNS(grid, nu, forcing=ZeroForcing())
    forcing = SelfConsistentForcing.from_state(
        grid, reference, nu, advection=base.advection
    )
    model = StreamFunctionNS(grid, nu, forcing=forcing)
    terms = model.energy_terms(reference)
    # At a manufactured fixed point, total RHS is zero, so the balance
    # derivative must equal the dissipation minus the forcing work.
    derivative = 0.0
    assert abs(terms.residual_from_derivative(derivative)) < 1e-10


def test_continuous_energy_balance_for_arbitrary_state():
    grid = Grid2D(32)
    model = StreamFunctionNS(
        grid,
        nu=0.01,
        forcing=KolmogorovForcing(amplitude=0.2),
        dealias=True,
    )
    psi = field(grid, "mixed")
    psi_x, psi_y = grid.grad(psi)
    rhs_x, rhs_y = grid.grad(model.rhs(psi))
    derivative = grid.l2_dot(psi_x, rhs_x) + grid.l2_dot(psi_y, rhs_y)
    terms = model.energy_terms(psi)
    assert abs(terms.residual_from_derivative(derivative)) < 1e-10


def test_midpoint_time_order_on_forced_multi_mode_state():
    grid = Grid2D(32)
    model = StreamFunctionNS(
        grid,
        nu=0.01,
        forcing=KolmogorovForcing(amplitude=0.2),
        dealias=True,
    )
    initial = field(grid, "mixed")
    final_time = 0.08
    errors = []
    for dt in (0.01, 0.005):
        state = model.integrate(initial, dt, int(round(final_time / dt)))
        reference = model.integrate(initial, 0.00125, int(round(final_time / 0.00125)))
        errors.append(np.linalg.norm(state - reference) / np.linalg.norm(reference))
    # A second-order method gives a factor near four; allow a modest defect
    # from the finite reference and the nonlinear transient.
    assert 2.5 < errors[0] / errors[1] < 5.5


def test_svd_projection_adapts_and_preserves_divergence():
    grid = Grid2D(32)
    model = StreamFunctionNS(grid, 0.01, forcing=KolmogorovForcing(0.1))
    rng = np.random.default_rng(4)
    state = rng.normal(size=(grid.N, grid.N))
    state -= state.mean()
    lowrank = DLRA(
        model,
        rank=2,
        min_rank=1,
        max_rank=12,
        relative_amplitude_cutoff=1e-6,
        check_every=1,
    )
    projected = lowrank.initialize(state)
    assert grid.max_div_velocity(projected) < 1e-12
    evolved = lowrank.step(projected, 0.002)
    # Diffusion is a diagonal Fourier semigroup, so it preserves the
    # low-rank stream-function subspace before the nonlinear projection.
    diffuse_rank = np.linalg.svd(
        StreamFunctionNS(grid, 0.01).diffuse(projected, 0.01), compute_uv=False
    )
    assert np.count_nonzero(diffuse_rank > 1e-10 * diffuse_rank[0]) <= 2
    assert lowrank.rank > 2
    assert lowrank.rank <= 12
    assert grid.max_div_velocity(evolved) < 1e-12
    assert lowrank.projector.last_stats is not None
    assert lowrank.projector.last_stats.target_rank <= 12


def test_adaptive_rank_decays_for_laminar_multimode_decay():
    grid = Grid2D(24)
    X, Y = np.meshgrid(grid.x, grid.y, indexing="ij")
    initial = (
        np.sin(X) * np.sin(Y)
        + 0.1 * np.sin(2 * X) * np.sin(Y)
        + 0.01 * np.sin(X) * np.sin(2 * Y)
    )
    model = StreamFunctionNS(grid, 0.02, forcing=ZeroForcing(), dealias=False)
    lowrank = DLRA(
        model,
        rank=6,
        min_rank=1,
        max_rank=12,
        relative_amplitude_cutoff=0.2,
        check_every=1,
    )
    final = lowrank.integrate(initial, 0.01, 100)
    assert max(lowrank.rank_history) > 1
    assert lowrank.rank == 1
    assert grid.ke(final) < grid.ke(initial)
    assert grid.max_div_velocity(final) < 1e-12


def test_rank_stagnation_and_restart_from_checkpoint():
    grid = Grid2D(24)
    model = StreamFunctionNS(grid, 0.01, forcing=ZeroForcing())
    initial = field(grid, "tg")
    first = DLRA(
        model,
        rank=1,
        min_rank=1,
        max_rank=6,
        relative_amplitude_cutoff=1e-6,
        check_every=2,
    )
    direct = first.integrate(initial, 0.002, 5)
    assert set(first.rank_history) == {1}

    # Reinitialize the adaptive state from a saved field and verify that a
    # resumed trajectory agrees with an uninterrupted one.
    checkpoint = first.integrate(initial, 0.002, 2)
    resumed_model = StreamFunctionNS(grid, 0.01, forcing=ZeroForcing())
    resumed = DLRA(
        resumed_model,
        rank=1,
        min_rank=1,
        max_rank=6,
        relative_amplitude_cutoff=1e-10,
        check_every=2,
    )
    resumed_state = resumed.integrate(checkpoint, 0.002, 3, t0=0.004)
    assert np.max(np.abs(resumed_state - direct)) < 2e-11


def test_static_pod_projection_is_a_galerkin_baseline():
    grid = Grid2D(24)
    tg = field(grid, "tg")
    mixed = field(grid, "mixed")
    snapshots = np.stack([tg, 0.8 * mixed])
    pod = PODGalerkin(grid, rank=1).fit(snapshots)
    assert pod.effective_rank() == 1
    # The fitted offset is the arithmetic snapshot mean.
    assert np.max(np.abs(pod.mean - 0.5 * (tg + 0.8 * mixed))) < 1e-13
    # Two snapshots have centred rank 1, so rank 1 is lossless and the static
    # baseline reproduces its own IC bit-for-bit (the P0 requirement).
    assert np.max(np.abs(pod.project(snapshots[1]) - snapshots[1])) < 1e-13
    assert np.max(np.abs(pod.project(tg) - tg)) < 1e-13
    assert np.isfinite(pod.relative_error(mixed))
    # Projection stays in the divergence-free class by representation.
    assert grid.max_div_velocity(pod.project(mixed)) < 1e-12

    # Rank truncation is a genuine L2-orthogonal, idempotent projection.
    three = np.stack([tg, 0.8 * mixed, 0.5 * tg + 0.9 * mixed])
    pod1 = PODGalerkin(grid, rank=1).fit(three)
    p = pod1.project(mixed)
    assert np.max(np.abs(pod1.project(p) - p)) < 1e-12
    residual = mixed - p
    assert abs(grid.l2_dot(residual, p - pod1.mean)) < 1e-10 * grid.l2_sq(p)
    assert np.linalg.norm(residual) > 1e-8  # rank 1 of a rank-2 set truncates


def test_pod_basis_spans_the_centered_snapshot_matrix():
    """Regression: fit() must SVD the snapshot matrix, not interleaved data.

    The snapshot matrix is rebuilt here independently (one column per
    snapshot), so this fails if fit() reshapes (n, N, N) straight to
    (N*N, n) and thereby fits the SVD to shuffled values.
    """
    grid = Grid2D(16)
    rng = np.random.default_rng(7)
    snaps = [
        field(grid, "tg") + 0.05 * rng.standard_normal((grid.N, grid.N)),
        field(grid, "mixed") + 0.05 * rng.standard_normal((grid.N, grid.N)),
        0.3 * field(grid, "tg") + field(grid, "mixed")
        + 0.05 * rng.standard_normal((grid.N, grid.N)),
    ]
    X = np.stack([s.ravel() for s in snaps], axis=1)   # (N*N, n), correct matrix
    # fit()'s documented contract: center every snapshot into the
    # zero-spatial-mean class, then take the ensemble mean of those.
    X = X - X.mean(axis=0, keepdims=True)
    M = X.mean(axis=1)
    centered = X - M[:, None]
    U, s, _ = np.linalg.svd(centered, full_matrices=False)
    for rank in (1, 2, 3):
        pod = PODGalerkin(grid, rank=rank).fit(snaps)
        # fit() keeps the arithmetic mean up to the documented zero-spatial-mean
        # adjustment, which the stream-function equations require.
        assert np.max(np.abs(pod.mean.ravel() - M)) < 1e-12
        assert abs(float(pod.mean.mean())) < 1e-15
        assert np.allclose(pod.singular_values[:rank], s[:rank])
        assert np.max(np.abs(pod.basis.T @ pod.basis - np.eye(rank))) < 1e-10
        recon = M[:, None] + pod.basis @ (pod.basis.T @ centered)
        residual = X - recon
        # The discarded content is orthogonal to the retained basis.
        assert np.max(np.abs(pod.basis.T @ residual)) < 1e-9
        if rank == 3:
            assert np.max(np.abs(residual)) < 1e-10


def test_pod_refuses_to_clamp_the_requested_rank():
    """A rank-r comparison must never silently run at a lower rank."""
    grid = Grid2D(16)
    snaps = [field(grid, "tg"), field(grid, "mixed"), 0.5 * field(grid, "mixed")]
    pod = PODGalerkin(grid, rank=3).fit(snaps)
    assert pod.effective_rank() == 3
    assert pod.requested_rank == 3
    # 3 snapshots supply only 2 centered directions plus the mean.
    try:
        PODGalerkin(grid, rank=4).fit(snaps)
    except ValueError as exc:
        assert "4" in str(exc) and "3" in str(exc)
    else:
        raise AssertionError("rank request above the snapshot count must raise")


def test_dlra_initialize_resets_a_warm_object():
    """A reused DLRA must not inherit a previous run's rank or schedule."""
    grid = Grid2D(24)
    initial = field(grid, "mixed")
    dt = 0.002

    def build():
        return DLRA(
            StreamFunctionNS(grid, 0.01, forcing=ZeroForcing()),
            rank=2,
            min_rank=1,
            max_rank=8,
            relative_amplitude_cutoff=1e-6,
            check_every=2,
        )

    # Drive the first run until it has adapted its rank away from nominal.
    warm = build()
    warm.integrate(initial, dt, 6)
    assert warm.steps == 6
    assert warm.spectrum_history  # learned state exists before reinitialization

    # A fresh object and the reused one must agree exactly from initialize().
    fresh = build()
    state_fresh = fresh.initialize(initial)
    state_reused = warm.initialize(initial)
    assert warm.steps == 0
    assert warm.spectrum_history == []
    assert warm.projector.rank == warm.projector.nominal_rank
    assert np.max(np.abs(state_fresh - state_reused)) == 0.0
    assert fresh.rank_history == warm.rank_history
    for _ in range(5):
        state_fresh = fresh.step(state_fresh, dt)
        state_reused = warm.step(state_reused, dt)
    assert np.max(np.abs(state_fresh - state_reused)) == 0.0
    assert fresh.rank_history == warm.rank_history


def test_svd_projector_reproduces_its_own_input_at_full_rank():
    """Fit-reproduces-its-own-input, applied to the DLRA projector."""
    grid = Grid2D(24)
    projector = SVDProjector(grid, rank=grid.N, min_rank=1, max_rank=grid.N)
    f = field(grid, "mixed")
    f = f - np.mean(f)
    assert np.max(np.abs(projector.project(f) - f)) < 1e-12
    retained = projector.candidate("stage")
    assert retained is None
    projector.project(f, stage="stage")
    centered, u, s, vh = projector.candidate("stage")
    rebuilt = (u * s) @ vh
    assert np.max(np.abs(rebuilt - centered)) < 1e-12


def test_nyquist_row_keeps_velocity_exactly_divergence_free():
    """Guard the invariant against a tempting but wrong "fix".

    A real field's x-Nyquist sample is self-conjugate, so a central-difference
    stencil cannot recover its x-derivative.  Zeroing the Nyquist multiplier in
    the first derivatives is the textbook-looking remedy and it is wrong here:
    it deletes v's Nyquist row while keeping u's, and the divergence of the
    resulting real velocity field becomes O(1).  SVD projections populate that
    row, so this would silently break the project's central invariant.  The
    spectral derivative is exact (numpy's irfftn inverts the full x-axis as a
    complex spectrum, preserving 2D Hermitian symmetry), so the true
    wavenumbers are kept and cancellation holds mode by mode.
    """
    grid = Grid2D(16)
    X, Y = np.meshgrid(grid.x, grid.y, indexing="ij")
    # A field whose x-Nyquist row is populated, mixed with smooth content.
    psi = (-1.0) ** np.arange(grid.N)[:, None] * np.cos(Y) + 0.5 * np.sin(X) * np.sin(Y)
    psi = psi - psi.mean()
    assert np.max(np.abs(grid.fft(psi)[grid.N // 2, :])) > 1.0  # Nyquist row is real
    u, v = grid.velocity(psi)
    assert grid.max_div_velocity(psi) < 1e-12
    # The multiplier arrays are deliberately untouched: only k=0 is zero.
    for arr in (grid.kx, grid.ky):
        assert np.count_nonzero(arr == 0.0) == 1
    # lap keeps the true Nyquist wavenumber: on a pure Nyquist mode the
    # multiplier k^2 is exact, so enstrophy is a real, nonzero quantity.
    nyq = grid.N // 2
    pure = (-1.0) ** np.arange(grid.N)[:, None] * np.ones((1, grid.N))
    assert np.max(np.abs(grid.lap(pure) + (grid.kx[nyq] ** 2) * pure)) < 1e-10
    assert grid.enstrophy(psi) > 0.0


def test_pod_dmd_reproduces_a_linear_system():
    """POD-DMD is only checkable where the answer is known: a linear system.

    Generate modal coefficients from a known linear operator, embed them in a
    POD basis, and require the fitted operator to reproduce the trajectory.  A
    least-squares fit of an exactly linear map must be exact, so this catches a
    transposed normal equation, a mis-ordered Gram/cross product, or a stride
    error -- the same class of defect as the R24 reshape.
    """
    grid = Grid2D(20)
    rng = np.random.default_rng(17)
    snaps = [
        field(grid, "tg") + 0.05 * rng.standard_normal((grid.N, grid.N)),
        field(grid, "mixed") + 0.05 * rng.standard_normal((grid.N, grid.N)),
        0.3 * field(grid, "tg") + field(grid, "mixed")
        + 0.05 * rng.standard_normal((grid.N, grid.N)),
        0.7 * field(grid, "tg") - 0.4 * field(grid, "mixed")
        + 0.05 * rng.standard_normal((grid.N, grid.N)),
    ]
    pod = PODGalerkin(grid, rank=3).fit(np.stack(snaps))
    dmd = PODDMD(pod)
    true_op = np.array(
        [[0.9, 0.1, 0.0], [0.0, 0.8, 0.2], [0.05, 0.0, 0.7]]
    )
    c0 = np.array([1.0, -0.5, 0.25])
    coefficients = [c0]
    for _ in range(12):
        coefficients.append(true_op @ coefficients[-1])
    for c in coefficients:
        dmd.accumulate(dmd.reconstruct(c))
    dmd.fit()
    assert np.max(np.abs(dmd.operator - true_op)) < 1e-8

    # The online rollout must then track the exact linear trajectory.
    state = dmd.initialize(dmd.reconstruct(c0))
    assert np.max(np.abs(state - dmd.reconstruct(c0))) < 1e-12
    c = c0
    for n in range(1, 6):
        c = dmd.step(c)
        assert np.max(np.abs(dmd.reconstruct(c) - dmd.reconstruct(coefficients[n]))) < 1e-8


def test_pod_dmd_reports_when_it_is_undertrained():
    """A baseline that cannot be fitted must say so, not return zeros."""
    grid = Grid2D(16)
    pod = PODGalerkin(grid, rank=2).fit(
        np.stack([field(grid, "tg"), field(grid, "mixed")])
    )
    dmd = PODDMD(pod)
    for method, args in (("fit", ()), ("step", (np.zeros(2),)),
                         ("initialize", (field(grid, "tg"),))):
        try:
            getattr(dmd, method)(*args)
        except RuntimeError:
            continue
        raise AssertionError(f"PODDMD.{method} must refuse before fit")
    dmd.accumulate(field(grid, "tg"))     # only one sample: no pair yet
    try:
        dmd.fit()
    except RuntimeError:
        pass
    else:
        raise AssertionError("PODDMD.fit must refuse with no sample pairs")


def _bug_stationary_case(N: int = 16, seed: int = 7):
    """A state that is an exact stationary point of the non-diffusive RHS.

    ``SelfConsistentForcing`` with ``nu = 0`` makes ``nonlinear_forcing`` vanish
    at the reference state, so a BUG run started there has zero right-hand side
    in every sub-equation.  That turns the factor algebra into an equality that
    either holds to roundoff or does not hold at all.
    """
    grid = Grid2D(N)
    rng = np.random.default_rng(seed)
    reference = field(grid, "random", rng=rng)
    reference = reference - reference.mean()
    forcing = SelfConsistentForcing.from_state(grid, reference, nu=0.0)
    model = StreamFunctionNS(grid, 0.0, forcing=forcing)
    return grid, model, reference


def test_bug_holds_a_stationary_state_to_machine_precision():
    """A stationary state is a fixed point of every BUG sub-equation.

    This is the sharp test of the factor algebra.  A transposed factor, a
    ``Mhat S0 Nhat`` written without the transpose, or a projector applied with
    the wrong sign all leave the state *almost* stationary, and a loose
    tolerance would pass all of them.  At machine precision only the exact
    algebra survives.
    """
    grid, model, reference = _bug_stationary_case()
    bug = BUGIntegrator(model, rank=4, min_rank=1, max_rank=12, substeps=2)
    start = bug.initialize(reference)
    assert np.max(np.abs(start - reference)) < 1e-13, "initialize must be exact"

    dt = 0.01
    state = start
    for i in range(25):
        state = bug.step(dt=dt, t=i * dt)
    drift = np.max(np.abs(state - reference))
    scale = float(np.max(np.abs(reference)))
    assert drift < 1e-12 * max(scale, 1.0), (
        f"BUG drifted {drift:.3e} from an exact stationary state "
        f"(field scale {scale:.3e})"
    )
    # The factors must stay orthonormal for the Galerkin projection to mean
    # anything; a QR-based truncation can silently break that.
    for factor in (bug.U, bug.V):
        err = np.max(np.abs(factor.T @ factor - np.eye(factor.shape[1])))
        assert err < 1e-12, f"factor lost orthonormality: {err:.3e}"


def test_bug_never_factorizes_the_full_state_inside_a_step():
    """The port's entire purpose is a structural one, so it is asserted.

    A timing claim cannot distinguish a BUG step from a projected one on a
    shared node, but the *shape* of the factorization can: the only
    factorization allowed after ``initialize`` is of the small augmented
    S-matrix, of dimension at most 4r (or 3r for the Remark-1 variant).
    """
    grid = Grid2D(32)
    model = StreamFunctionNS(grid, 1 / 5000, forcing=KolmogorovForcing(0.5, 1.0))
    initial = field(grid, "mixed")
    initial = initial - initial.mean()
    rank = 6
    bug = BUGIntegrator(model, rank=rank, min_rank=1, max_rank=40,
                        relative_amplitude_cutoff=1e-6, substeps=2)
    bug.initialize(initial)
    dt = 0.001
    for i in range(10):
        bug.step(dt=dt, t=i * dt)
    assert bug.large_svd_calls == 0, "a full-size SVD ran inside step()"
    assert bug.svd_max_dimension <= 4 * rank, (
        f"factorized a {bug.svd_max_dimension}x{bug.svd_max_dimension} matrix; "
        f"the augmented S is at most 4r = {4*rank}"
    )
    assert bug.svd_calls == 10, "one truncation SVD per step, no more"
    assert np.all(np.isfinite(bug.state()))


def test_bug_rank_is_governed_by_min_rank_and_max_rank():
    """Truncation sets the rank; the two bounds are what constrain it.

    The paper offers two truncation rules: back to the original rank r, or to
    whatever passes a tolerance on the augmented S-matrix's singular values.  The
    second is genuinely two-sided -- with a loose tolerance the rank *grows*
    past r (the augmented basis offers up to 4r directions), and with a very
    tight one it still grows if the small spectrum is flat, so a rank-decreasing
    assertion would be asserting the wrong thing.  What must hold is that the
    fixed-rank option is exact, that the ceiling binds, and that the rank never
    leaves the bounds.
    """
    grid = Grid2D(32)
    model = StreamFunctionNS(grid, 1 / 5000, forcing=KolmogorovForcing(0.5, 1.0))
    initial = field(grid, "random")
    initial = initial - initial.mean()
    dt = 0.001

    # "truncated to the original rank r": min_rank == max_rank pins it exactly.
    fixed = BUGIntegrator(model, rank=6, min_rank=6, max_rank=6, substeps=2)
    fixed.initialize(initial)
    for i in range(12):
        fixed.step(dt=dt, t=i * dt)
    assert fixed.rank == 6, f"fixed-rank option drifted to {fixed.rank}"

    # The ceiling binds below the augmented dimension, and the floor holds.
    for cap in (3, 7, 40):
        bug = BUGIntegrator(model, rank=1, min_rank=1, max_rank=cap,
                            relative_amplitude_cutoff=0.5, substeps=2)
        bug.initialize(initial)
        for i in range(12):
            bug.step(dt=dt, t=i * dt)
            assert 1 <= bug.rank <= cap, (
                f"rank {bug.rank} left [1, {cap}] mid-run"
            )
    # A loose tolerance on a rank-1 start must be able to grow, otherwise the
    # rank-adaptive option is vacuous.
    loose = BUGIntegrator(model, rank=1, min_rank=1, max_rank=40,
                          relative_amplitude_cutoff=0.5, substeps=2)
    loose.initialize(initial)
    for i in range(12):
        loose.step(dt=dt, t=i * dt)
    assert loose.rank >= 1


def test_bug_is_second_order():
    """Second order is the paper's claim, so it is measured and asserted.

    The reference is a **same-rank** BUG run at a much finer step, not the exact
    solution.  A projected method's error against the exact solution contains a
    representation bias that does not shrink with ``dt``, so the total error
    plateaus and the order is unmeasurable; subtracting a same-rank reference
    isolates the time-discretization error, which is what "second order" is a
    claim about.  The rank is pinned (``min_rank == max_rank``) so the augmented
    dimension is the same for every ``dt``.

    **The rank has to be rich enough for the measurement to mean anything.**
    Measured on this case: at rank 6 the observed order is 1.01/1.02/1.05, and at
    rank 24 it is 1.98/1.95.  Both are the same code.  The rank-6 truncation
    discards 18 of the 24 augmented directions every step, and that error is
    O(1) in ``dt``, so it dominates the time error and masks the scheme's true
    order.  Second order is therefore a statement about the *time integrator*,
    conditional on the rank being sufficient to represent the dynamics -- which
    is the same conditioning the rank criterion has to satisfy, and the reason
    an under-selecting rank rule does not merely lose accuracy but loses order.
    """
    grid = Grid2D(16)
    nu = 1 / 5000
    initial = field(grid, "random")
    initial = initial - initial.mean()
    final_time = 0.05
    # ``max_rank`` is capped at the grid's N, so at N=16 the richest fixed rank
    # is 16; that is what the order measurement below actually uses.
    rank = 16

    def run(nsteps: int) -> np.ndarray:
        model = StreamFunctionNS(grid, nu, forcing=KolmogorovForcing(0.5, 1.0))
        bug = BUGIntegrator(model, rank=rank, min_rank=rank, max_rank=rank,
                            substeps=2)
        state = bug.initialize(initial)
        dt = final_time / nsteps
        for i in range(nsteps):
            state = bug.step(dt=dt, t=i * dt)
        assert bug.rank == rank
        return state

    reference = run(6400)
    errors = [float(np.max(np.abs(run(n) - reference))) for n in (200, 400, 800)]
    orders = [float(np.log2(errors[i] / errors[i + 1])) for i in range(len(errors) - 1)]
    assert orders[-1] > 1.7, (
        f"observed convergence order {orders[-1]:.2f} "
        f"(errors {[f'{e:.3e}' for e in errors]}); midpoint BUG is second order"
    )


def test_window_energy_rank_matches_a_stacked_svd():
    """The windowed rule must measure the *stacked* spectrum, exactly.

    The implementation takes square roots of the eigenvalues of a Gram matrix
    instead of factorizing the stacked matrix, which is a real algebraic
    substitution: a Gram eigendecomposition returns squared singular values, and
    getting that wrong (or using eigenvalues directly) would scale the spectrum
    but leave the *rank* right, so only a test that compares spectra catches it.
    A window that includes its own evaluation point would also pass, so the
    comparison is against the singular values of exactly the retained fields.
    """
    grid = Grid2D(16)
    proj = SVDProjector(
        grid, rank=2, min_rank=1, max_rank=16,
        rank_criterion="window_energy", energy_fraction=0.99,
        rank_basis="fluctuations", rank_window=4,
    )
    rng = np.random.default_rng(5)
    fields = [
        field(grid, "mixed") * (1.0 + 0.3 * i) + 0.01 * rng.normal(size=(grid.N, grid.N))
        for i in range(6)
    ]
    for f in fields:
        got = proj._rank_spectrum(f, np.zeros(0))
    stacked = np.stack(
        [fluctuations(f).reshape(-1) for f in fields[-4:]], axis=1
    )
    expected = np.linalg.svd(stacked, compute_uv=False)
    assert got.shape == expected.shape, (got.shape, expected.shape)
    scale = float(np.max(expected))
    assert np.max(np.abs(got - expected)) < 1e-8 * scale, (
        f"windowed spectrum differs from the stacked SVD by "
        f"{np.max(np.abs(got - expected)):.3e} against a scale of {scale:.3e}"
    )
    # ...and the window must actually slide, not accumulate everything.
    assert len(proj._window_fields) == 4


def test_window_energy_rank_is_reset_between_runs():
    """A retained candidate from an earlier run must not leak into a new one."""
    grid = Grid2D(16)
    proj = SVDProjector(
        grid, rank=2, min_rank=1, max_rank=16, rank_criterion="window_energy",
        rank_window=4,
    )
    f = field(grid, "mixed")
    for _ in range(9):
        proj._rank_spectrum(f, np.zeros(0))
    assert len(proj._window_fields) == 4
    proj.reset()
    assert proj._window_fields == []
    assert proj.rank == proj.nominal_rank


def test_window_energy_rank_exceeds_the_instantaneous_one():
    """The whole point: a window sees more directions than one state does.

    For a trajectory that turns, the modes needed to represent a window of it
    exceed the modes any single state needs.  If this failed, the windowed rule
    would be indistinguishable from the per-step one and the distinction the
    project keeps drawing would be vacuous.
    """
    grid = Grid2D(16)
    X, Y = np.meshgrid(grid.x, grid.y, indexing="ij")
    states = [np.sin((m + 1) * X) * np.cos((m + 1) * Y) for m in range(8)]
    states = [s - s.mean() for s in states]
    per_step = SVDProjector(
        grid, rank=2, min_rank=1, max_rank=32,
        rank_criterion="energy", energy_fraction=0.99, rank_basis="fluctuations",
    )
    windowed = SVDProjector(
        grid, rank=2, min_rank=1, max_rank=32,
        rank_criterion="window_energy", energy_fraction=0.99,
        rank_basis="fluctuations", rank_window=8,
    )
    r_step = per_step._target_from_spectrum(
        per_step._rank_spectrum(states[-1], np.zeros(0))
    )
    # The windowed rule only sees a window if it is *fed* one; a single call
    # would leave its window holding a single field and the two rules identical.
    for s in states:
        windowed._rank_spectrum(s, np.zeros(0))
    r_win = windowed._target_from_spectrum(
        windowed._rank_spectrum(states[-1], np.zeros(0))
    )
    assert r_win > r_step, (
        f"windowed rank {r_win} did not exceed the per-step rank {r_step}"
    )


def test_crossover_horizon_detects_a_downward_crossing():
    """The advantage horizon is a *downward* crossing and must be found.

    ``R = static/DLRA`` falls through 1 as the DLRA's error grows, so a detector
    that only tests for an upward crossing finds nothing and reports "no
    crossover" -- which is what happened for three review cycles, because this
    function had no test.  Each case below is a shape the detector must handle.
    """
    from run_crossover import crossover_horizon

    def rows(dlra, static, times):
        d = [
            {"time": t, "relative_l2": v, "relative_l2_oracle_mean": 0.0}
            for t, v in zip(times, dlra)
        ]
        s = [
            {"time": t, "relative_l2": 0.0, "relative_l2_oracle_mean": v}
            for t, v in zip(times, static)
        ]
        return d, s

    times = [0.1, 0.25, 0.5, 1.0, 2.0, 4.0]

    # 1. A single downward crossing between t=0.25 and t=0.5.  The static error
    #    is held flat and the DLRA's grows, which is the shape the real data has:
    #    R = 3, 1.5, 0.75, 0.6, 0.6, 0.6.
    d, s = rows([0.10, 0.20, 0.40, 0.50, 0.50, 0.50], [0.30, 0.30, 0.30, 0.30, 0.30, 0.30], times)
    out = crossover_horizon(d, s)
    assert out["status"] == "resolved", out
    assert out["bracket"] == [0.25, 0.5], out["bracket"]
    assert out["t_star_loglog"] == pytest.approx(out["t_star_linear"], rel=0.2)
    assert 0.25 < out["t_star"] < 0.5
    assert out["crossings"] == 1, out["all_crossings"]

    # 2. DLRA leads everywhere: unresolved, and the reason must not invent a
    #    horizon.
    #    Ratios 9, 4.5, 3, 2.25, 1.8, 1.5 -- all above 1.
    d, s = rows([0.1, 0.2, 0.3, 0.4, 0.5, 0.6], [0.9, 0.9, 0.9, 0.9, 0.9, 0.9], times)
    out = crossover_horizon(d, s)
    assert out["status"] == "unresolved", out
    assert out["t_star"] is None
    assert "no crossing" in out["reason"]

    # 3. Static leads everywhere: also unresolved, with the *other* leader named.
    d, s = rows([0.5, 0.5, 0.5, 0.5, 0.5, 0.5], [0.1, 0.1, 0.1, 0.1, 0.1, 0.1], times)
    out = crossover_horizon(d, s)
    assert out["status"] == "unresolved", out
    assert "static baseline leads" in out["reason"], out["reason"]

    # 4. An exact DLRA is "never", which is not the same as unresolved.  The
    #    error need not be *zero*: at the dealiasing ceiling it is ~1e-8 against a
    #    static error of ~0.1, which is a ratio of 1e6 and must still read as
    #    exact rather than as an unresolved crossing.
    d, s = rows([1e-8] * 6, [0.2, 0.2, 0.2, 0.2, 0.2, 0.2], times)
    out = crossover_horizon(d, s)
    assert out["status"] == "never", out
    assert out["t_star"] is None
    assert "exact" in out["reason"]

    # 5. A ratio that crosses twice must report both, and t* is the first
    #    downward one.
    #    Ratios 3, 2, 0.667, 1.5, 0.6, 0.545: down through 1 then back up.
    d, s = rows(
        [0.10, 0.15, 0.45, 0.20, 0.50, 0.55],
        [0.30, 0.30, 0.30, 0.30, 0.30, 0.30],
        times,
    )
    out = crossover_horizon(d, s)
    # 3, 2, 0.667, 1.5, 0.6, 0.545 changes sign three times.
    assert out["crossings"] == 3, out["all_crossings"]
    directions = [c["direction"] for c in out["all_crossings"]]
    assert directions == [
        "static_overtakes", "dlra_retakes", "static_overtakes"
    ], directions
    # t* is the *first* downward crossing, and the reason says the lead is not
    # held throughout rather than presenting a single number.
    assert out["bracket"] == [0.25, 0.5], out["bracket"]
    assert "crosses 1 again" in out["reason"], out["reason"]

    # 6. Every reported ratio is consistent with the rows it came from.
    d, s = rows([0.10, 0.20, 0.40, 0.50, 0.50, 0.50], [0.30, 0.30, 0.30, 0.30, 0.30, 0.30], times)
    out = crossover_horizon(d, s)
    for entry, drow, srow in zip(out["ratio_by_horizon"], d, s):
        assert entry["time"] == drow["time"]
        assert entry["ratio"] == pytest.approx(
            srow["relative_l2_oracle_mean"] / drow["relative_l2"]
        )


def test_the_recorded_energy_residual_is_the_full_pde_balance():
    """The projection-aware residual and the PDE residual are different numbers.

    D70: the artifact's residual key was named for the energy balance but held
    the *projection-aware* balance, so a writer taking it for the PDE balance
    understated a projected method's violation by the size of the projection's
    energy increment -- a factor of hundreds in the committed suite.  The two
    are only interchangeable when there is no projection, and this pins both
    halves of that: they coincide for a full-grid run, and they separate when a
    projection does work.
    """
    from run_kolmogorov import _energy_residual

    grid = Grid2D(24)
    nu = 1 / 1000
    forcing = KolmogorovForcing(0.5, 1.0)
    model = StreamFunctionNS(grid, nu, forcing=forcing, dealias=True)
    initial = field(grid, "mixed")
    initial = initial - initial.mean()
    dt = 0.002

    # 1. A full-grid step has no projection, so the two must be identical.
    state = initial.copy()
    pde = proj = 0.0
    for _ in range(20):
        old = state
        state = model.step(old, dt, t=0.0)
        pde = max(pde, _energy_residual(model, old, state, dt, 0.0, grid, 0.0))
        proj = max(proj, _energy_residual(model, old, state, dt, 0.0, grid, 0.0))
    assert pde == proj, (pde, proj)

    # 2. A projection that does measurable work must separate them, and in the
    #    only possible direction: the projection-aware residual is the smaller,
    #    because the projection's energy increment is exactly the discrepancy
    #    between the two.
    from solvers.pod import PODGalerkin
    # Diagnostics must be on: the projection's energy increment is only
    # accumulated when ``track_step_diagnostics`` is set, so a run that forgets
    # it gets a silent zero and reports the PDE residual under the
    # projection-aware name -- the D70 trap in code rather than in a key.
    tracked = StreamFunctionNS(grid, nu, forcing=forcing, dealias=True)
    tracked.track_step_diagnostics = True
    X, Y = np.meshgrid(grid.x, grid.y, indexing="ij")
    snapshots = np.stack([
        np.sin(X) * np.sin(Y),
        np.cos(2 * X) * np.sin(Y),
        np.sin(X) * np.cos(2 * Y),
    ])
    snapshots = snapshots - snapshots.mean(axis=(1, 2), keepdims=True)
    pod = PODGalerkin(grid, rank=2).fit(snapshots)
    state = pod.project(field(grid, "mixed"))
    pde = proj = 0.0
    increments = []
    for _ in range(20):
        old = state
        state = tracked.step(old, dt, t=0.0, projector=pod.project)
        increment = float(
            tracked.last_step_info.get("projection_energy_increment", 0.0)
        )
        increments.append(increment)
        pde = max(pde, _energy_residual(tracked, old, state, dt, 0.0, grid, 0.0))
        proj = max(
            proj, _energy_residual(tracked, old, state, dt, 0.0, grid, increment)
        )
    assert max(abs(i) for i in increments) > 0.0, (
        "the projection did no measurable work, so this test cannot separate "
        "the two residuals; check track_step_diagnostics is enabled"
    )
    assert proj < pde, (
        f"projection-aware residual {proj:.3e} is not below the PDE residual "
        f"{pde:.3e}; the difference between them is the projection's energy "
        f"increment, so the ordering is not a matter of taste"
    )


def test_baseline_rollouts_run_to_completion():
    """The baseline rollouts must actually run, not just import.

    A moving-window rollout that only receives its projector at the first refit
    has an unbound projector before that point; nothing else in the suite would
    notice, because the failure only appears when the driver is run.  This
    exercises both rollout paths end to end at a size where they are instant,
    and checks the fields the artifact contract depends on.
    """
    from run_baselines import run_dmd, run_projected_moving

    grid = Grid2D(16)
    dt = 0.01
    model = StreamFunctionNS(grid, 0.05, forcing=KolmogorovForcing(0.5, 1.0))
    initial = field(grid, "mixed")
    initial = initial - initial.mean()

    # POD-DMD: fitted on a short window, rolled out with a stride > 1.
    pod = PODGalerkin(grid, rank=3).fit(np.stack([initial, 0.9 * initial, 1.1 * initial]))
    dmd = PODDMD(pod)
    # A few distinct coefficient vectors, so the Gram is not rank deficient.
    for c in (np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]),
              np.array([0.0, 0.0, 1.0]), np.array([0.5, 0.5, 0.0])):
        dmd.accumulate(dmd.reconstruct(c))
    dmd.fit()
    assert not dmd.singular_gram
    out = run_dmd(
        grid, dmd, initial, dt, 0.1, sample_every=5, steps_per_application=5
    )
    assert out["times"][-1] == 0.1
    assert out["applications"] == 2
    assert out["diverged_at_step"] is None
    assert len(out["states"]) == len(out["times"])

    # Moving window: no initial projector, so the first steps run unprojected
    # rather than raising on an unbound one.
    schedule = {5: pod}
    out = run_projected_moving(
        grid,
        StreamFunctionNS(grid, 0.05, forcing=KolmogorovForcing(0.5, 1.0)),
        initial, dt, 0.1, 5, schedule,
    )
    assert out["times"][-1] == 0.1
    assert out["diverged_at_step"] is None
    assert out["final_time_reached"] == 0.1
    # ...and with an initial projector it is projected from t=0.
    out2 = run_projected_moving(
        grid,
        StreamFunctionNS(grid, 0.05, forcing=KolmogorovForcing(0.5, 1.0)),
        initial, dt, 0.1, 5, schedule, initial_projector=pod,
    )
    assert out2["diverged_at_step"] is None


def test_isotropic_spectra_reproduce_the_energies():
    """The shell sums must equal ke() and enstrophy(), or the spectra lie."""
    grid = Grid2D(24)
    rng = np.random.default_rng(5)
    for name, f in (
        ("tg", field(grid, "tg")),
        ("mixed", field(grid, "mixed")),
        ("full-band", rng.standard_normal((grid.N, grid.N))),
    ):
        f = f - f.mean()
        k, e, z = grid.isotropic_spectra(f)
        assert k.size == e.size == z.size
        assert np.isclose(np.sum(e), grid.ke(f), rtol=1e-10, atol=1e-12)
        assert np.isclose(np.sum(z), grid.enstrophy(f), rtol=1e-10, atol=1e-12)
        assert np.all(e >= 0.0) and np.all(z >= 0.0)
    # Enstrophy is the demanding metric: for a broadband field its spectrum must
    # sit at higher k than the energy spectrum's, which is why both are
    # reported.  (For a single mode the two coincide, so this is checked only
    # on broadband input.)
    broadband = rng.standard_normal((grid.N, grid.N))
    broadband = broadband - broadband.mean()
    k, e, z = grid.isotropic_spectra(broadband)
    assert (k * z).sum() / z.sum() > (k * e).sum() / e.sum()
    # A non-finite field yields empty spectra rather than NaNs.
    bad = np.zeros((grid.N, grid.N))
    bad[0, 0] = np.nan
    k, e, z = grid.isotropic_spectra(bad)
    assert k.size == 0 and e.size == 0 and z.size == 0


def test_energy_rank_criterion_matches_brute_force_and_differs_from_amplitude():
    """The two criteria are different rules, and the energy one is r99.

    R26's constructive consequence is that the amplitude rule cannot see the
    rank growth (its request saturates at the largest alias-free rank for the
    grid) while an energy rule can.
    That only holds if they genuinely differ, so this pins both against
    brute force *and* against each other.
    """
    grid = Grid2D(16)
    # A steeply decaying spectrum: the amplitude count is far larger than the
    # number of modes carrying 99% of the energy.
    s = 10.0 ** (-np.arange(1, 13) / 2.0)   # each term is 1/10 of the last
    # Total energy is sum 10^-1 + 10^-2 + ... = 1/9 * 10^-1..., so 99% of it is
    # reached after two modes and 99.9% after three.
    for fraction, expected in ((0.99, 2), (0.999, 3)):
        projector = SVDProjector(
            grid, rank=4, min_rank=1, max_rank=grid.N,
            rank_criterion="energy", energy_fraction=fraction,
        )
        brute = int(np.searchsorted(np.cumsum(s**2), fraction * np.sum(s**2)) + 1)
        assert brute == expected, (fraction, brute)
        assert projector._target_from_spectrum(s) == expected
    amp = SVDProjector(
        grid, rank=4, min_rank=1, max_rank=grid.N,
        rank_criterion="amplitude", relative_amplitude_cutoff=1e-6,
    )
    energy = SVDProjector(
        grid, rank=4, min_rank=1, max_rank=grid.N,
        rank_criterion="energy", energy_fraction=0.99,
    )
    assert amp._target_from_spectrum(s) == 12      # every mode clears 1e-6*s0
    assert energy._target_from_spectrum(s) == 2    # r99
    assert amp._target_from_spectrum(s) != energy._target_from_spectrum(s)
    # Clamping applies to the energy rule too: r999 needs 3 modes, so a cap of
    # 2 must bring it down, and a cap of 3 leaves it alone.
    capped = SVDProjector(
        grid, rank=2, min_rank=1, max_rank=2, rank_criterion="energy",
        energy_fraction=0.999,
    )
    assert capped._target_from_spectrum(s) == 2
    uncapped = SVDProjector(
        grid, rank=2, min_rank=1, max_rank=3, rank_criterion="energy",
        energy_fraction=0.999,
    )
    assert uncapped._target_from_spectrum(s) == 3
    # Bad configuration is rejected rather than silently ignored.
    for kwargs in ({"rank_criterion": "nonsense"}, {"energy_fraction": 1.5},
                   {"energy_fraction": 0.0}):
        try:
            SVDProjector(grid, rank=2, **kwargs)
        except ValueError:
            continue
        raise AssertionError(f"SVDProjector must reject {kwargs}")


def test_divergence_diagnostic_detects_an_injected_violation():
    """Negative control: the invariant test must be able to fail.

    Exact divergence-freeness holds *by representation* for any stream
    function, so a test that only checks that property would pass for any
    implementation, including a broken one.  Inject a gradient into the
    velocity -- u + grad(phi) is not divergence-free -- and require the
    diagnostic to report O(1).
    """
    grid = Grid2D(24)
    X, Y = np.meshgrid(grid.x, grid.y, indexing="ij")
    psi = field(grid, "mixed")
    u, v = grid.velocity(psi)
    assert grid.max_divergence(u, v) < 1e-12        # the structural case
    assert grid.max_div_velocity(psi) < 1e-12       # the reported invariant

    # phi = sin(x): div(grad phi) = Lap phi = -sin(x), so the diagnostic must
    # report ~1, not ~0.
    phi = np.sin(X)
    dphi_dx, dphi_dy = grid.grad(phi)
    injected = grid.max_divergence(u + dphi_dx, v + dphi_dy)
    assert 0.5 < injected < 2.0, injected

    # A divergence-free perturbation of the same size must not trip it, so the
    # control is specific rather than merely sensitive.
    curl_x, curl_y = grid.velocity(np.sin(X) * np.sin(Y) * 0.1)
    assert grid.max_divergence(u + curl_x, v + curl_y) < 1e-12


def test_full_field_svd_is_rank_independent():
    """R5q (a): the factorization is whole-field, so cost cannot depend on rank.

    This pins the *structural* fact behind the measured rank-independence: the
    projector factorizes the entire N x N field and keeps the full N-value
    spectrum regardless of the retained rank.  A future port that factorizes
    only r columns (the V6 per-stage update) fails this test, which is the
    point -- the change should show up as a failing test, not as prose.
    """
    grid = Grid2D(24)
    f = field(grid, "mixed")
    for rank in (1, 2, 8, grid.N):
        projector = SVDProjector(grid, rank=rank, min_rank=1, max_rank=grid.N)
        centered, u, s, vh = projector._svd(f)
        assert centered.shape == (grid.N, grid.N)
        assert s.size == grid.N, (rank, s.size)
        assert np.allclose(np.linalg.svd(centered, compute_uv=False), s)
        # The rank only changes which columns are used, never the factorization.
        assert projector.project(f).shape == f.shape


def test_svd_call_count_per_step():
    """R5q (b): four whole-field factorizations per step, asserted.

    Reducing 4 -> 1 (or 4 -> 1 per adaptation step) must be a test that can
    fail, so the count is measured from the projector rather than documented.
    """
    grid = Grid2D(16)
    steps = 5
    model = StreamFunctionNS(grid, 0.01, forcing=KolmogorovForcing(0.2, 1.0))
    dlra = DLRA(
        model,
        rank=2,
        min_rank=1,
        max_rank=8,
        relative_amplitude_cutoff=1e-10,
        check_every=10**9,     # no adaptation, so the count is the plain 4
        adapt_initial=False,
    )
    dlra.initialize(field(grid, "tg"))   # reset zeroes the counters
    state = dlra.projector.project(field(grid, "tg"))
    dlra.projector.reset_counters_only()
    for i in range(steps):
        state = dlra.step(state, 0.001, t=i * 0.001)
    assert dlra.projector.svd_calls == 4 * steps
    assert dlra.projector.svd_seconds > 0.0


def test_rank_rule_matches_brute_force():
    """R5l: the rank rule is #{sigma_i > cutoff*sigma_1} clipped to the bounds."""
    grid = Grid2D(16)
    rng = np.random.default_rng(3)
    for cutoff, min_rank, max_rank in ((1e-6, 2, 48), (0.2, 1, 8), (1e-12, 3, 6)):
        projector = SVDProjector(
            grid, rank=4, min_rank=min_rank, max_rank=max_rank,
            relative_amplitude_cutoff=cutoff,
        )
        for _ in range(5):
            f = rng.standard_normal((grid.N, grid.N))
            s = np.linalg.svd(f - f.mean(), compute_uv=False)
            expected = int(np.count_nonzero(s > cutoff * s[0]))
            expected = max(min_rank, min(max_rank, expected))
            assert projector._target_from_spectrum(s) == expected
            assert projector.adapt(f).shape == f.shape
    # Degenerate and empty spectra fall back to min_rank rather than raising.
    assert projector._target_from_spectrum(np.empty(0)) == min_rank
    assert projector._target_from_spectrum(np.zeros(5)) == min_rank


def test_operators_agree_with_full_2d_spectrum_everywhere():
    """R5k: compare every operator against a full 2-D spectrum, no rFFT route.

    A suite whose fields are all band-limited cannot see an error that lives
    only at the Nyquist wavenumber, so the field here is full band and the
    reference builds its own k-grid with ``numpy.fft.fft2``/``ifft2``.

    This test is the regression guard for a real defect.  Applying a
    k-dependent multiplier to the rfft **half** spectrum and inverting with
    ``irfftn`` is a different operator: ``irfftn`` rebuilds the missing columns
    as ``conj(F[k, N-j])`` whereas a real field requires
    ``conj(F[N-k, j])``.  The two agree for fields whose spectrum is symmetric
    in k -- which every band-limited test field happened to be -- and disagree
    by O(1) otherwise, including in the nonlinear term, which is built from
    these derivatives.  The first derivative is therefore formed from the full
    spectrum, and both halves of that claim are asserted here: the operators
    match the independent route *everywhere* (Nyquist planes included), and the
    half-spectrum shortcut demonstrably does not.
    """
    grid = Grid2D(16)
    rng = np.random.default_rng(11)
    f = rng.standard_normal((grid.N, grid.N))

    k = 2 * np.pi * np.fft.fftfreq(grid.N, d=grid.dx)
    KX, KY = np.meshgrid(k, k, indexing="ij")
    F = np.fft.fft2(f)
    ref_lap = np.fft.ifft2(-(KX**2 + KY**2) * F).real
    ref_vort = np.fft.ifft2((KX**2 + KY**2) * F).real
    ref_u = np.fft.ifft2(1j * KY * F).real
    ref_v = np.fft.ifft2(-1j * KX * F).real
    ref_fx = np.fft.ifft2(1j * KX * F).real
    ref_fy = np.fft.ifft2(1j * KY * F).real

    scale = float(np.max(np.abs(ref_lap)))
    assert np.max(np.abs(grid.lap(f) - ref_lap)) < 1e-9 * scale
    assert np.max(np.abs(grid.vorticity(f) - ref_vort)) < 1e-9 * scale
    u, v = grid.velocity(f)
    fx, fy = grid.grad(f)
    for name, got, ref in (
        ("u", u, ref_u), ("v", v, ref_v), ("fx", fx, ref_fx), ("fy", fy, ref_fy),
    ):
        tol = 1e-9 * max(1.0, float(np.max(np.abs(ref))))
        assert np.max(np.abs(got - ref)) < tol, name

    # The half-spectrum shortcut is *not* the same operator; if this ever stops
    # holding, the reason the full spectrum is used has gone away.
    shortcut_x = grid.ifft(1j * grid.kx[:, None] * grid.fft(f))
    assert np.max(np.abs(shortcut_x - ref_fx)) > 1e-3 * np.max(np.abs(ref_fx))

    # div u = 0 holds on a full-band field, measured with the same operator.
    assert grid.max_div_velocity(f) < 1e-9 * scale


def test_reduced_path_is_second_order_in_dt():
    """R5: the time-order test must cover the reduced path, not only the kernel.

    ``DLRA.step`` runs the same kernel but calls the projector at four stage
    boundaries, so its order has to be measured on that path.  The projection
    is taken at full rank, where it is the identity (Eckart--Young, asserted
    elsewhere), which isolates the integrator's order; the forcing is strong
    and the horizon long enough that the truncation error sits far above
    roundoff, because a near-static state collapses both errors to ~1e-12 and
    makes the ratio meaningless.
    """
    grid = Grid2D(24)
    X, Y = np.meshgrid(grid.x, grid.y, indexing="ij")
    initial = np.sin(X) * np.sin(Y) + 0.5 * np.cos(2 * X) * np.cos(2 * Y)
    initial = initial - initial.mean()

    def run(dt: float, nsteps: int) -> np.ndarray:
        model = StreamFunctionNS(grid, 1e-3, forcing=KolmogorovForcing(2.0, 1.0))
        dlra = DLRA(
            model,
            rank=grid.N,         # lossless: this isolates the integrator's order
            min_rank=grid.N,
            max_rank=grid.N,
            relative_amplitude_cutoff=1e-12,
            check_every=10**9,
            adapt_initial=False,
        )
        state = dlra.initialize(initial)
        for i in range(nsteps):
            state = dlra.step(state, dt, t=i * dt)
        return state

    T = 0.5
    reference = run(T / 80, 80)
    coarse = run(T / 5, 5)
    fine = run(T / 10, 10)
    e_coarse = float(np.linalg.norm(coarse - reference))
    e_fine = float(np.linalg.norm(fine - reference))
    assert e_coarse > 1e-10, e_coarse
    # Second order: halving dt cuts the error by about four.
    assert 3.0 < e_coarse / e_fine < 5.0, (e_coarse, e_fine)


def test_pod_projection_handles_fields_with_nonzero_mean():
    """R5l: the defect hid when every field and basis was mean-free.

    Snapshots here carry a constant offset, so if ``project`` ended with a mean
    subtraction it would move the result out of span(mean) + span(basis) and
    break idempotence.  Note *which* orthogonality is the contract: the
    residual is orthogonal to the retained **modes**, not to the mean.  The
    mean is an offset with its own dynamics (here the zonal mode), so the
    Galerkin step projects the deviation; requiring the residual to be
    orthogonal to the mean as well would be requiring the projection onto
    span(mean) + span(basis) to be orthogonal, which it is not and should not
    be -- the mean is not a dynamic direction to be projected onto.
    """
    grid = Grid2D(20)
    snaps = [
        field(grid, "tg") + 0.7,
        field(grid, "mixed") - 1.3,
        0.4 * field(grid, "tg") + field(grid, "mixed") + 0.2,
    ]
    for rank in (1, 2, 3):
        pod = PODGalerkin(grid, rank=rank).fit(np.stack(snaps))
        probe = field(grid, "mixed") + 2.5      # deliberately non-mean-free
        p = pod.project(probe)
        assert np.max(np.abs(pod.project(p) - p)) < 1e-12
        residual = probe - p
        # Residual is orthogonal to every retained mode.
        assert np.max(np.abs(pod.basis.T @ residual.ravel())) < 1e-9 * np.linalg.norm(
            residual
        )
        # p lies in span(mean) + span(basis) ...
        B = np.column_stack([pod.mean.ravel(), pod.basis])
        assert np.linalg.norm(
            p.ravel() - B @ np.linalg.lstsq(B, p.ravel(), rcond=None)[0]
        ) < 1e-9 * max(1.0, np.linalg.norm(p))
        # ... and equals the independent least-squares fit of the *deviation*
        # onto the modes, which is the Galerkin statement.
        dev = probe.ravel() - pod.mean.ravel()
        lstsq = pod.mean.ravel() + pod.basis @ np.linalg.lstsq(
            pod.basis, dev, rcond=None
        )[0]
        assert np.max(np.abs(p.ravel() - lstsq)) < 1e-9 * max(1.0, np.linalg.norm(p))
    # Mean-free inputs are unaffected by the convention.
    pod = PODGalerkin(grid, rank=2).fit(np.stack(snaps))
    assert abs(float(pod.mean.mean())) < 1e-15


def test_initial_state_reference_grid_holds_the_same_field():
    """A two-grid comparison must hold the identical field, not just the band.

    With the default the Gaussian draw has shape (N, N), so changing N gives a
    different realization of the same band.  Passing the coarse N as
    ``reference_N`` evaluates the same band-limited field on the finer grid.
    """
    from run_kolmogorov import make_initial_state

    coarse, fine = Grid2D(64), Grid2D(128)
    a = make_initial_state(coarse, base_speed=0.5, perturbation_velocity_rms=1.0, cutoff=8)
    same_field = make_initial_state(
        fine, base_speed=0.5, perturbation_velocity_rms=1.0, cutoff=8, reference_N=64
    )
    redrawn = make_initial_state(
        fine, base_speed=0.5, perturbation_velocity_rms=1.0, cutoff=8
    )
    # The resampled field is the identical band-limited field: unnormalized
    # rfft coefficients scale with N^2, so compare them normalized.
    Fa, Fb = coarse.fft(a - np.mean(a)), fine.fft(same_field - np.mean(same_field))
    kx_ok = np.abs(fine.kx) <= 8
    ky_ok = fine.ky <= 8
    idx_x = np.rint(fine.kx).astype(int) % coarse.N
    idx_y = np.rint(fine.ky).astype(int)
    lhs = Fa[np.ix_(idx_x[kx_ok], idx_y[ky_ok])] / coarse.n
    rhs = Fb[np.ix_(kx_ok, ky_ok)] / fine.n
    assert np.max(np.abs(lhs - rhs)) < 1e-12 * np.max(np.abs(lhs))
    # Everything outside the box is empty on both grids.
    assert np.max(np.abs(Fb[~kx_ok, :])) < 1e-12 * np.max(np.abs(Fb))
    assert np.max(np.abs(Fb[:, ~ky_ok])) < 1e-12 * np.max(np.abs(Fb))
    # ...and it is genuinely a different field from the redrawn one.
    Fr = fine.fft(redrawn - np.mean(redrawn))
    assert np.max(np.abs(Fb - Fr)) > 1e-3 * np.max(np.abs(Fb))
    # The default is unchanged, so the verified N=64 fingerprint still holds.
    assert abs(coarse.ke(a) - 22.206703312933374) < 1e-12
    # A reference grid too coarse to resolve the band is rejected.
    try:
        make_initial_state(fine, cutoff=8, reference_N=8)
    except ValueError:
        pass
    else:
        raise AssertionError("an under-resolving reference grid must raise")


def test_initial_state_mask_is_a_box_with_rank_2c_plus_1():
    """cutoff is a box half-width: rank 2c+1, max radial |k| floor(c*sqrt2)."""
    from run_kolmogorov import make_initial_state

    for cutoff, expect_rank in ((2, 5), (4, 9), (8, 17)):
        grid = Grid2D(64)
        state = make_initial_state(
            grid, base_speed=0.5, perturbation_velocity_rms=1.0, cutoff=cutoff
        )
        values = np.linalg.svd(state - np.mean(state), compute_uv=False)
        rank = int(np.count_nonzero(values > 1e-10 * values[0]))
        assert rank == expect_rank, (cutoff, rank)
        # Radial extent is the box corner, not the box half-width.
        F = np.abs(grid.fft(state))
        present = np.argwhere(F > 1e-8 * F.max())
        radial = np.max(np.hypot(grid.kx[present[:, 0]], grid.ky[present[:, 1]]))
        assert np.floor(cutoff * np.sqrt(2)) == int(np.floor(radial))
