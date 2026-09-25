"""Fast correctness tests for the stream-function SP-DLRA engine.

Run from the repository root with ``~/.venvs/ns/bin/python -m pytest``.
"""
from __future__ import annotations

import numpy as np

from solvers import (
    DLRA,
    Grid2D,
    KolmogorovForcing,
    PODGalerkin,
    SelfConsistentForcing,
    StreamFunctionNS,
    ZeroForcing,
)


def field(grid: Grid2D, name: str = "tg") -> np.ndarray:
    X, Y = np.meshgrid(grid.x, grid.y, indexing="ij")
    if name == "tg":
        return np.sin(X) * np.sin(Y)
    if name == "mixed":
        return (
            0.7 * np.sin(X) * np.sin(Y)
            + 0.2 * np.cos(2 * X) * np.sin(Y)
            + 0.1 * np.sin(X) * np.cos(2 * Y)
        )
    raise ValueError(name)


def test_spectral_conventions_and_norms():
    grid = Grid2D(32)
    psi = field(grid)
    omega = grid.vorticity(psi)
    u, v = grid.velocity(psi)
    assert np.max(np.abs(omega - 2.0 * psi)) < 1e-11
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
        tolerance=1e-6,
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
    assert lowrank.projector.last_stats.numerical_rank <= 12


def test_rank_stagnation_and_restart_from_checkpoint():
    grid = Grid2D(24)
    model = StreamFunctionNS(grid, 0.01, forcing=KolmogorovForcing(0.1))
    initial = field(grid, "tg")
    first = DLRA(
        model,
        rank=1,
        min_rank=1,
        max_rank=6,
        tolerance=1e-10,
        check_every=2,
    )
    direct = first.integrate(initial, 0.002, 5)
    assert set(first.rank_history) == {1}

    # Reinitialize the adaptive state from a saved field and verify that a
    # resumed trajectory agrees with an uninterrupted one.
    checkpoint = first.integrate(initial, 0.002, 2)
    resumed_model = StreamFunctionNS(grid, 0.01, forcing=KolmogorovForcing(0.1))
    resumed = DLRA(
        resumed_model,
        rank=1,
        min_rank=1,
        max_rank=6,
        tolerance=1e-10,
        check_every=2,
    )
    resumed_state = resumed.integrate(checkpoint, 0.002, 3, t0=0.004)
    assert np.max(np.abs(resumed_state - direct)) < 2e-11


def test_static_pod_projection_is_a_galerkin_baseline():
    grid = Grid2D(24)
    snapshots = np.stack([field(grid, "tg"), 0.8 * field(grid, "mixed")])
    pod = PODGalerkin(grid, rank=1).fit(snapshots)
    projected = pod.project(snapshots[1])
    assert grid.max_div_velocity(projected) < 1e-12
    assert pod.effective_rank() == 1
    assert np.isfinite(pod.relative_error(field(grid, "mixed")))
    assert np.linalg.norm(projected - snapshots[1]) > 1e-8
