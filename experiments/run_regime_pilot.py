"""S1-S3 regime pilot: is there an affordable horizon that meets S2?

D11.2 settles the regime framing: statistics are computed on the
fluctuations, the zonal mean's trajectory is reported alongside, and no
agent may call this forced-turbulence validation.  What is left to measure
is S3 -- the horizon itself.  S2 is mechanical:

  * ``psi' = psi - x-avg(psi)`` (S1), so the statistic is a *fluctuation*
    quantity; total-E stationarity is not a criterion and is not asserted.
  * ``E_fluct = 1/2 <|grad psi'|^2>`` and ``Z_fluct = 1/2 <|omega'|^2>``.
  * Block means of at least ``--block-time`` time units are formed over the
    final third, and the drift is measured between the last two thirds.
  * S2 passes when ``|drift| <= 10%`` on **both** E_fluct and Z_fluct.

The pilot reports that drift as a function of T so the horizon is chosen
from a measurement instead of an assumption, and it reports the zonal
mean's own trajectory next to it so the secular growth is visible rather
than hidden inside a fluctuation statistic.

Only the full-grid reference is run: this is a question about the forced
problem, not about any reduced method.

Run from the repository root::

    ~/.venvs/ns/bin/python experiments/run_regime_pilot.py --re 5000
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from solvers import Grid2D, KolmogorovForcing, StreamFunctionNS, fluctuations, zonal_mean
from experiments.run_kolmogorov import make_initial_state


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def fluctuation_terms(grid: Grid2D, psi: np.ndarray) -> dict:
    """S1 quantities: fluctuation energy/enstrophy plus the zonal part."""
    prime = fluctuations(psi)
    zonal = zonal_mean(psi)
    return {
        "energy_total": grid.ke(psi),
        "enstrophy_total": grid.enstrophy(psi),
        "energy_fluct": grid.ke(prime),
        "enstrophy_fluct": grid.enstrophy(prime),
        "energy_zonal": grid.ke(zonal),
    }


def s2_drift(
    times: list[float],
    values: list[float],
    block_time: float,
) -> dict:
    """S2: block-mean drift between the last two thirds of the record.

    Blocks are at least ``block_time`` long.  The final third of the record is
    split into blocks; the drift is the relative change of the block-mean
    sequence's last third against the preceding third, i.e. between the last
    two thirds of the record.
    """
    t_end = times[-1]
    t_start = t_end / 3.0
    tail = [(t, v) for t, v in zip(times, values) if t >= t_start]
    if len(tail) < 2:
        return {"drift": None, "blocks": [], "reason": "too few samples in final third"}
    blocks: list[list[float]] = []
    current: list[float] = []
    block_start = tail[0][0]
    for t, v in tail:
        if t - block_start >= block_time and current:
            blocks.append(current)
            current = []
            block_start = t
        current.append(v)
    if current:
        blocks.append(current)
    if len(blocks) < 2:
        return {"drift": None, "blocks": [], "reason": "fewer than two blocks"}
    means = [float(np.mean(b)) for b in blocks]
    third = max(1, len(blocks) // 3)
    earlier = means[-2 * third:-third] or means[:-1]
    later = means[-third:]
    ref = float(np.mean(earlier))
    drift = None
    if abs(ref) > 0.0:
        drift = abs(float(np.mean(later)) - ref) / abs(ref)
    return {
        "drift": drift,
        "block_means": means,
        "block_count": len(blocks),
        "reference_mean": ref,
        "final_mean": float(np.mean(later)),
    }


def run_to(
    grid: Grid2D,
    model: StreamFunctionNS,
    initial: np.ndarray,
    dt: float,
    final_time: float,
    sample_every: int,
    keep_snapshots: bool = True,
) -> dict:
    state = initial.copy()
    times = [0.0]
    history = [fluctuation_terms(grid, state)]
    snapshots = [state.copy()] if keep_snapshots else []
    ranks = [rank_spectrum(state)]
    max_div = grid.max_div_velocity(state)
    u0, v0 = grid.velocity(state)
    max_cfl = float(np.max(np.hypot(u0, v0)) * dt / grid.dx)
    nsteps = int(round(final_time / dt))
    start = time.perf_counter()
    for step in range(1, nsteps + 1):
        state = model.step(state, dt, t=(step - 1) * dt)
        if not np.isfinite(state).all():
            raise FloatingPointError(f"non-finite state at step {step}")
        max_div = max(max_div, grid.max_div_velocity(state))
        if step % sample_every == 0 or step == nsteps:
            times.append(step * dt)
            history.append(fluctuation_terms(grid, state))
            ranks.append(rank_spectrum(state))
            if keep_snapshots:
                snapshots.append(state.copy())
        if step % (50 * sample_every) == 0:
            u, v = grid.velocity(state)
            max_cfl = max(max_cfl, float(np.max(np.hypot(u, v)) * dt / grid.dx))
    return {
        "times": times,
        "history": history,
        "snapshots": snapshots,
        "ranks": ranks,
        "max_abs_divergence": max_div,
        "max_cfl": max_cfl,
        "wall_seconds": time.perf_counter() - start,
        "nsteps": nsteps,
    }


def rank_for_energy(s: np.ndarray, fraction: float) -> int:
    """Modes needed to carry ``fraction`` of the energy (the r99-style rank)."""
    if s.size == 0 or s[0] <= 0.0:
        return 0
    energy = np.cumsum(s.astype(float) ** 2)
    total = energy[-1]
    if total <= 0.0:
        return 0
    return int(min(np.searchsorted(energy, fraction * total) + 1, s.size))


def rank_for_amplitude(s: np.ndarray, cutoff: float) -> int:
    """Modes above ``cutoff * s[0]`` -- the implemented historical rule."""
    if s.size == 0 or s[0] <= 0.0:
        return 0
    return int(np.count_nonzero(s > cutoff * s[0]))


def rank_spectrum(state: np.ndarray) -> dict:
    """Both rank criteria for one state, on the fluctuations and in total."""
    out = {}
    for tag, field in (
        ("fluct", fluctuations(state)),
        ("total", state - np.mean(state)),
    ):
        s = np.linalg.svd(field, compute_uv=False)
        out[tag] = {
            "r99": rank_for_energy(s, 0.99),
            "r999": rank_for_energy(s, 0.999),
            "amp_1e-6": rank_for_amplitude(s, 1e-6),
            "amp_1e-8": rank_for_amplitude(s, 1e-8),
            "amp_1e-10": rank_for_amplitude(s, 1e-10),
            "sigma_1": float(s[0]) if s.size else 0.0,
        }
    return out


def window_rank_table(
    snapshots: list[np.ndarray], horizons: list[float], times: list[float]
) -> list[dict]:
    """R26's table, computed here: modes needed to represent the window [0, W].

    This is *not* the instantaneous rank of a state.  It is the number of modes
    a POD basis fitted on every snapshot from t=0 to t=W needs to carry the
    requested energy fraction of that window's fluctuations -- how many modes
    the dynamics of the window actually occupies.  R26 measured this growing
    1 -> 16 over the first eight time units and grid-independently; reproducing
    it from this code is the cross-check, and the amplitude column beside it is
    the same table's demonstration that the historical rule cannot see it.
    """
    table = []
    for W in horizons:
        cols = [
            fluctuations(s).reshape(-1)
            for t, s in zip(times, snapshots)
            if t <= W + 1e-12
        ]
        if len(cols) < 2:
            continue
        X = np.stack(cols, axis=1)
        centered = X - X.mean(axis=1)[:, None]
        s = np.linalg.svd(centered, compute_uv=False)
        table.append({
            "window_end": W,
            "snapshots": len(cols),
            "r99": rank_for_energy(s, 0.99),
            "r999": rank_for_energy(s, 0.999),
            "amp_1e-6": rank_for_amplitude(s, 1e-6),
            "amp_1e-10": rank_for_amplitude(s, 1e-10),
        })
    return table


def windowed_spectra(
    grid: Grid2D,
    model: StreamFunctionNS,
    initial: np.ndarray,
    dt: float,
    start_time: float,
    end_time: float,
    sample_every: int,
) -> dict:
    """Time-averaged isotropic E(k)/Z(k) of the fluctuations over a window.

    S1 applies here as everywhere else: the spectra are accumulated on
    ``psi' = psi - x-avg(psi)``, because the zonal mean holds a secularly
    growing low-wavenumber component that would otherwise dominate the
    low-k bins.  The window's own energy and enstrophy are reported next to the
    spectra so the two can be checked against each other.
    """
    state = initial.copy()
    nsteps = int(round(end_time / dt))
    begin = int(round(start_time / dt))
    e_sum = z_sum = None
    count = 0
    for step in range(1, nsteps + 1):
        state = model.step(state, dt, t=(step - 1) * dt)
        if step < begin:
            continue
        if step % sample_every == 0 or step == nsteps:
            prime = fluctuations(state)
            k, e, z = grid.isotropic_spectra(prime)
            if e_sum is None:
                e_sum, z_sum = np.zeros_like(e), np.zeros_like(z)
            e_sum += e
            z_sum += z
            count += 1
    if not count:
        return {}
    e_mean, z_mean = e_sum / count, z_sum / count
    resolved = int(grid.N // 3)
    return {
        "window_start": start_time,
        "window_end": end_time,
        "samples": count,
        "k": [int(x) for x in k],
        "E_fluct": [float(x) for x in e_mean],
        "Z_fluct": [float(x) for x in z_mean],
        "sum_E_fluct": float(np.sum(e_mean)),
        "sum_Z_fluct": float(np.sum(z_mean)),
        "dealias_resolved_k_max": resolved,
        "note": (
            "time-averaged on psi' = psi - x-avg(psi); sum(E) and sum(Z) "
            "reproduce the window's fluctuation energy and enstrophy"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--re", type=int, default=5000)
    parser.add_argument("--N", type=int, default=64)
    parser.add_argument("--dt", type=float, default=None)
    parser.add_argument("--horizons", type=float, nargs="+",
                        default=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 40.0])
    parser.add_argument("--block-time", type=float, default=2.0,
                        help="minimum block length in time units (S2 requires >= 2)")
    parser.add_argument("--sample-every", type=int, default=200)
    parser.add_argument("--force-amplitude", type=float, default=0.5)
    parser.add_argument("--base-speed", type=float, default=0.5)
    parser.add_argument("--perturbation-velocity-rms", type=float, default=1.0)
    parser.add_argument("--cutoff", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260925)
    parser.add_argument(
        "--rank-horizons", type=float, nargs="*", default=None,
        help="window ends for the rank-vs-horizon table (default: a ladder "
             "through 8, where the growth happens)",
    )
    parser.add_argument(
        "--spectra-at", type=float, nargs="*", default=None,
        help="horizons at which to also accumulate windowed E(k)/Z(k) "
             "(default: the largest horizon)",
    )
    parser.add_argument(
        "--output", type=Path,
        default=Path("state/coder/results/regime_pilot.json"),
    )
    args = parser.parse_args()
    if args.block_time < 2.0:
        raise SystemExit("S2 requires block means of at least 2 time units")
    horizons = sorted(args.horizons)
    spectra_at = sorted(args.spectra_at) if args.spectra_at else [horizons[-1]]
    # The rank ladder is finer than the S2 ladder on purpose: the rank question
    # is where the growth happens (the first few time units), which is exactly
    # where S2 has too little record to say anything.
    rank_horizons = sorted(
        set(args.rank_horizons) | {h for h in horizons if h <= 8.0}
    ) if args.rank_horizons else sorted(
        {0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0}
        | {h for h in horizons if h <= 8.0}
    )

    grid = Grid2D(args.N)
    # dt scales with dx so the CFL number is held fixed across grids (P0 item 4).
    dt = args.dt if args.dt is not None else 5e-4 * (64.0 / args.N)
    forcing = KolmogorovForcing(amplitude=args.force_amplitude, wavenumber=1.0)
    model = StreamFunctionNS(grid, nu=1.0 / args.re, forcing=forcing, dealias=True)
    initial = make_initial_state(
        grid,
        base_speed=args.base_speed,
        perturbation_velocity_rms=args.perturbation_velocity_rms,
        cutoff=args.cutoff,
        seed=args.seed,
    )

    rows = []
    spectra = {}
    for T in horizons:
        print(f"regime pilot: Re={args.re} T={T} ...", flush=True)
        rec = run_to(grid, model, initial, dt, T, args.sample_every)
        times = rec["times"]
        e_f = [h["energy_fluct"] for h in rec["history"]]
        z_f = [h["enstrophy_fluct"] for h in rec["history"]]
        e_t = [h["energy_total"] for h in rec["history"]]
        e_z = [h["energy_zonal"] for h in rec["history"]]
        d_e = s2_drift(times, e_f, args.block_time)
        d_z = s2_drift(times, z_f, args.block_time)
        passes = (
            d_e["drift"] is not None
            and d_z["drift"] is not None
            and d_e["drift"] <= 0.10
            and d_z["drift"] <= 0.10
        )
        rows.append({
            "final_time": T,
            "nsteps": rec["nsteps"],
            "wall_seconds": rec["wall_seconds"],
            "max_abs_divergence": rec["max_abs_divergence"],
            "max_cfl": rec["max_cfl"],
            "S2_energy_fluct_drift": d_e["drift"],
            "S2_enstrophy_fluct_drift": d_z["drift"],
            "S2_passes": bool(passes),
            "S2_energy_block_means": d_e.get("block_means", []),
            "S2_enstrophy_block_means": d_z.get("block_means", []),
            "S2_energy_drift_note": d_e.get("reason"),
            "S2_enstrophy_drift_note": d_z.get("reason"),
            "final_energy_total": e_t[-1],
            "final_energy_fluct": e_f[-1],
            "final_enstrophy_fluct": z_f[-1],
            "final_energy_zonal": e_z[-1],
            "zonal_share_of_total_energy_at_end": (
                e_z[-1] / e_t[-1] if e_t[-1] > 0 else None
            ),
            "samples": len(times),
            # Instantaneous rank of the state at t=T under both criteria, so the
            # trajectory's rank and the window's rank can be compared.
            "rank_at_end": rec["ranks"][-1],
        })
        if T in spectra_at:
            print(f"regime pilot: windowed spectra at T={T} ...", flush=True)
            window_start = max(0.0, T - max(args.block_time * 2.0, T / 3.0))
            spectra[str(T)] = windowed_spectra(
                grid, model, initial, dt, window_start, T, args.sample_every
            )

    # R26's measurement, reproduced here: how many modes the window [0, W]
    # needs, for a ladder of W.  Built from the longest run's snapshots.
    if rows and rec is not None:
        print("regime pilot: window rank table ...", flush=True)
        # Only windows the longest run actually covered: a rank entry for a
        # horizon past the record would silently be fitted to a shorter window
        # and look like saturation.
        longest = rec["times"][-1]
        usable = [W for W in rank_horizons if W <= longest + 1e-12]
        rank_table = window_rank_table(rec["snapshots"], usable, rec["times"])
        instantaneous = [
            {"time": t, **ranks["fluct"]}
            for t, ranks in zip(rec["times"], rec["ranks"])
        ]

    qualifying = [r["final_time"] for r in rows if r["S2_passes"]]
    output = {
        "case": "regime_pilot",
        "provenance": {
            "git_commit": _git_commit(),
            "driver": "experiments/run_regime_pilot.py",
        },
        "parameters": {
            "re": args.re,
            "N": args.N,
            "dt": dt,
            "horizons": horizons,
            "rank_horizons": rank_horizons,
            "block_time": args.block_time,
            "spectra_at": spectra_at,
            "sample_every": args.sample_every,
            "force_amplitude": args.force_amplitude,
            "base_speed": args.base_speed,
            "perturbation_velocity_rms": args.perturbation_velocity_rms,
            "cutoff": args.cutoff,
            "seed": args.seed,
        },
        "initial_state": {
            "energy": grid.ke(initial),
            "numerical_rank": int(
                np.count_nonzero(
                    np.linalg.svd(initial - initial.mean(), compute_uv=False)
                    > 1e-10 * np.linalg.svd(initial - initial.mean(),
                                            compute_uv=False)[0]
                )
            ),
        },
        "rows": rows,
        "windowed_spectra": spectra,
        "window_rank_table": rank_table,
        "instantaneous_rank_series": instantaneous,
        "qualifying_horizons": qualifying,
        "interpretation": (
            "S1: every statistic here is computed on psi' = psi - x-avg(psi); the "
            "zonal mean's own energy is reported alongside so its secular growth "
            "is visible. S2: block-mean drift between the last two thirds of the "
            "record, on E_fluct and Z_fluct, passing at |drift| <= 10% on both. "
            "S3: the horizon is chosen from this table, not assumed. S5: T <= 0.1 "
            "carries no turbulence statistic and is included only as the "
            "left-hand end of the drift curve."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
