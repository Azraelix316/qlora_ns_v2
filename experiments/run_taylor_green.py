"""Taylor--Green validation run for the stream-function solver.

The single-mode Taylor--Green stream function has a known exact viscous
solution, making this a cheap end-to-end check of the split kernel and the
low-rank path.  The script writes a compact JSON report and is intentionally
usable both as a command-line experiment and as a library function.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

# Make direct ``python experiments/run_*.py`` execution work from any cwd.
ROOT = Path(__file__).resolve().parents[1]
from provenance import provenance as _provenance
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.run_kolmogorov import initial_state_fingerprint
from solvers import DLRA, Grid2D, StreamFunctionNS, ZeroForcing
from solvers.spectral import fluctuations


def relative_l2(a: np.ndarray, b: np.ndarray) -> float:
    denom = max(float(np.linalg.norm(b)), np.finfo(float).eps)
    return float(np.linalg.norm(a - b) / denom)


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def run_case(
    N: int = 64,
    nu: float = 0.02,
    dt: float = 0.01,
    nsteps: int = 100,
    rank: int = 1,
) -> dict:
    grid = Grid2D(N)
    X, Y = np.meshgrid(grid.x, grid.y, indexing="ij")
    # u=(sin x cos y,-cos x sin y), omega=2 sin x sin y, |k|^2=2.
    initial = np.sin(X) * np.sin(Y)
    model = StreamFunctionNS(grid, nu=nu, forcing=ZeroForcing(), dealias=False)
    lowrank = DLRA(
        model,
        rank=rank,
        min_rank=rank,
        max_rank=max(rank, 8),
        relative_amplitude_cutoff=1e-10,
        check_every=5,
    )
    full = initial.copy()
    reduced = lowrank.initialize(initial)
    max_full_error = 0.0
    max_reduced_error = 0.0
    max_div = 0.0
    max_energy_increase = -np.inf
    max_balance_residual = 0.0
    exact = initial.copy()
    # C11-1: the paper's `fig_tg_ke_rank` plots E(t) and the adaptive r(t), and
    # neither was recorded -- the artifact carried only scalars, so a caption
    # asking for a monotone E(t) and a rank decaying 3 -> 2 -> 1 had nothing to
    # be drawn from.  The zonal share rides along because it is the same
    # diagnostic the forced runs now carry.
    energy_history = [grid.ke(full)]
    dlra_energy_history = [grid.ke(reduced)]
    rank_history = [int(lowrank.rank)]
    zonal_energy_history = [grid.ke(fluctuations(full))]

    for n in range(nsteps):
        t = n * dt
        old = full
        old_energy = grid.ke(old)
        terms = model.energy_terms(old, t)
        full = model.step(old, dt, t=t)
        reduced = lowrank.step(reduced, dt, t=t)
        exact = np.exp(-2.0 * nu * (n + 1) * dt) * initial
        max_full_error = max(max_full_error, relative_l2(full, exact))
        max_reduced_error = max(max_reduced_error, relative_l2(reduced, exact))
        max_div = max(max_div, grid.max_div_velocity(full), grid.max_div_velocity(reduced))
        new_energy = grid.ke(full)
        max_energy_increase = max(max_energy_increase, new_energy - old_energy)
        derivative = (new_energy - old_energy) / dt
        residual = terms.residual_from_derivative(derivative)
        scale = max(1.0, abs(terms.dissipation), abs(terms.forcing_input))
        max_balance_residual = max(max_balance_residual, abs(residual) / scale)
        energy_history.append(grid.ke(full))
        dlra_energy_history.append(grid.ke(reduced))
        rank_history.append(int(lowrank.rank))
        zonal_energy_history.append(grid.ke(fluctuations(full)))
    # Time each method in a separate loop so the reported costs include only
    # the method named by the corresponding field.
    timing_full = initial.copy()
    start_full = time.perf_counter()
    for n in range(nsteps):
        timing_full = model.step(timing_full, dt, t=n * dt)
    full_seconds = time.perf_counter() - start_full

    timing_state = initial.copy()
    timing_lowrank = DLRA(
        model,
        rank=rank,
        min_rank=rank,
        max_rank=max(rank, 8),
        relative_amplitude_cutoff=1e-10,
        check_every=5,
    )
    timing_state = timing_lowrank.initialize(timing_state)
    start_reduced = time.perf_counter()
    for n in range(nsteps):
        timing_state = timing_lowrank.step(timing_state, dt, t=n * dt)
    reduced_seconds = time.perf_counter() - start_reduced

    return {
        "case": "taylor_green",
        "provenance": {
            **_provenance(Path(__file__).resolve()),
            "driver": "experiments/run_taylor_green.py",
        },
        "grid": {"N": N, "L": grid.L},
        "parameters": {"nu": nu, "dt": dt, "nsteps": nsteps, "rank": rank},
        "energy_history": energy_history,
        "dlra_energy_history": dlra_energy_history,
        "rank_history": rank_history,
        "fluctuation_energy_history": zonal_energy_history,
        "series_note": (
            "E(t) for the full grid and for the reduced state, the adaptive rank "
            "at every step, and the fluctuation energy. Recorded so the paper's "
            "fig_tg_ke_rank can be drawn from the artifact rather than "
            "reconstructed. This case is UNFORCED, so E(t) is the laminar decay "
            "and the fluctuation series is the same quantity on a field with no "
            "zonal forcing."
        ),
        "initial_state": initial_state_fingerprint(grid, initial),
        "initial_energy": grid.ke(initial),
        "final_energy": grid.ke(full),
        "max_relative_l2_error_full": max_full_error,
        "max_relative_l2_error_dlra": max_reduced_error,
        "max_abs_divergence": max_div,
        "max_energy_increase": float(max_energy_increase),
        "max_scaled_projected_energy_residual": max_balance_residual,
        "full_seconds": full_seconds,
        "dlra_seconds": reduced_seconds,
        "full_seconds_per_step": full_seconds / max(nsteps, 1),
        "dlra_seconds_per_step": reduced_seconds / max(nsteps, 1),
        "dlra_rank_final": lowrank.rank,
        "dlra_rank_min": min(lowrank.rank_history),
        "dlra_rank_max": max(lowrank.rank_history),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--N", type=int, default=64)
    parser.add_argument("--nu", type=float, default=0.02)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--rank", type=int, default=1)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("state/coder/results/taylor_green.json"),
    )
    args = parser.parse_args()
    result = run_case(args.N, args.nu, args.dt, args.steps, args.rank)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
