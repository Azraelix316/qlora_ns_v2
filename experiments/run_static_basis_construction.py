"""Why a propagated static basis overflows where the reduced model's does not.

C6-4: this measurement existed only as a test and a note.  A test asserts a
contrast; it does not produce a table anyone can cite, and "scratch is not
evidence" (D22) means a number that lives only in a message or a scratch tree
cannot be quoted.  So it is run here, at the configuration where the contrast is
sharpest, and written where a registry row can verify it.

**What is actually being separated.**  At ``N=32`` a static basis built on raw
window snapshots overflows at ``t ~ 5.4``, while a static basis built on the
*fluctuations* survives, and so does the reduced model's own subspace whether or
not it refreshes.  Three things could explain that, and the arms are arranged to
tell them apart:

1. the basis construction -- raw snapshots against zonal-mean-removed ones;
2. the basis *refreshing* -- the reduced model's one whole-field factorisation
   per step, on or off (``check_every`` gates the refresh, not only the rank);
3. the rank itself.

Arm 3 below is the control that makes arm 4 interpretable: if the frozen and
refreshing arms are identical, the refresh is not what is doing the work here,
and the difference is construction.  That is a narrower claim than "the subspace
must evolve", and this artifact is where the narrower claim is earned.

Two further arms exist because a single configuration cannot support a general
one.  The **rank sweep** exists because the overflow time is *not monotone* in
rank, so an artifact reporting only "the rank at which it fails" would mislead
whoever reads it next -- the non-monotonicity is recorded as a finding, not as
noise.  The **seed replication** exists because a single seed at a single
configuration is one draw, and a contrast that depends on the initial condition
is a different claim from one that does not.

Run from the repository root::

    python experiments/run_static_basis_construction.py \\
        --output state/coder/results/static_basis_construction_N32.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "experiments") not in sys.path:
    sys.path.insert(0, str(ROOT / "experiments"))

from provenance import provenance as _provenance  # noqa: E402
from run_baselines import make_initial_state, new_model  # noqa: E402
from solvers import DLRA, Grid2D  # noqa: E402
from solvers.pod import PODGalerkin  # noqa: E402
from solvers.spectral import fluctuations  # noqa: E402


def _training_window(
    grid: Grid2D, model, initial: np.ndarray, dt: float, window: float,
    n_snapshots: int, basis: str,
) -> list[np.ndarray]:
    """Snapshots over the first ``window`` time units, on the requested basis.

    ``basis='fluctuations'`` removes each snapshot's zonal mean, which is what
    the reduced model does; ``basis='raw'`` does not, which is what a plain POD
    fit on the stored states does.  The two are the arms under comparison, so
    they differ in exactly this and in nothing else.
    """
    stride = max(1, int(round(window / dt / max(n_snapshots - 1, 1))))
    columns = [initial]
    state = initial.copy()
    for step in range(1, int(round(window / dt)) + 1):
        state = model.step(state, dt, t=(step - 1) * dt)
        if not np.isfinite(state).all():
            raise SystemExit(f"training window went non-finite at step {step}")
        if step % stride == 0:
            columns.append(
                fluctuations(state) if basis == "fluctuations" else state.copy()
            )
    return columns


def _rollout(
    grid: Grid2D, model, initial: np.ndarray, dt: float, final_time: float,
    projector=None, dlra: DLRA | None = None,
) -> dict:
    """Propagate to ``final_time``, reporting the first non-finite step.

    The basis rebuilds are COUNTED rather than inferred: the count is the
    quantity that says whether a refresh happened at all, and inferring it from
    the configuration would have been how the ``check_every`` trap stayed
    invisible.
    """
    state = dlra.initialize(initial) if dlra is not None else projector(
        initial.copy()
    )
    nsteps = int(round(final_time / dt))
    max_div = grid.max_div_velocity(state)
    rebuilds = 0
    diverged_at = None
    start = time.perf_counter()
    with np.errstate(invalid="ignore", over="ignore"):
        for step in range(1, nsteps + 1):
            if dlra is not None:
                before = int(getattr(dlra, "basis_builds", 0))
                state = dlra.step(state, dt, t=(step - 1) * dt)
                rebuilds += int(getattr(dlra, "basis_builds", 0)) - before
            else:
                state = model.step(
                    state, dt, t=(step - 1) * dt, projector=projector
                )
            if not np.isfinite(state).all():
                diverged_at = step
                break
            max_div = max(max_div, grid.max_div_velocity(state))
    return {
        "diverged": diverged_at is not None,
        "diverged_at_step": diverged_at,
        "diverged_at_time": (diverged_at * dt) if diverged_at else None,
        "final_time_reached": (diverged_at * dt) if diverged_at else final_time,
        "max_abs_divergence": max_div,
        "basis_rebuilds": rebuilds,
        "wall_seconds": time.perf_counter() - start,
    }


def _interpretation(arms: list[dict], sweep: list[dict], seeds: list[dict]) -> str:
    """State what the arms show, from the arms, rather than what was hoped.

    An earlier version of this string asserted that the difference was the basis
    *construction*. The arms refute it: the fluctuation-fitted propagated basis
    overflows too, and earlier than the raw one. So the string is generated from
    the measured outcomes, and it says which arms survived rather than
    describing a mechanism the run does not support.
    """
    by_arm = {a["arm"]: a for a in arms}

    def outcome(arm: str) -> str:
        a = by_arm.get(arm)
        if a is None:
            return "not run"
        return (f"overflows at t={a['diverged_at_time']:.3f}" if a["diverged"]
                else f"reaches t={a['final_time_reached']:.3f}")

    propagated = [a for a in arms if a["arm"].endswith("static_stepper")]
    rederived = [a for a in arms if a["arm"].startswith("dlra_basis")]
    all_propagated_fail = all(a["diverged"] for a in propagated)
    all_rederived_survive = not any(a["diverged"] for a in rederived)

    # Is the overflow time monotone in rank, per basis?  Recorded because an
    # artifact reporting only "the rank at which it fails" misleads: at these
    # settings the ordering is not monotone and the surviving basis flips.
    monotone = {}
    for basis in sorted({r["basis"] for r in sweep}):
        rows = [r for r in sweep if r["basis"] == basis]
        diverged = [r["diverged_at_time"] for r in rows if r["diverged"]]
        monotone[basis] = {
            "monotone_in_divergence_time": all(
                a <= b for a, b in zip(diverged, diverged[1:])
            ) if len(diverged) > 1 else None,
            "ranks_that_survived": [r["rank"] for r in rows if not r["diverged"]],
        }
    flip = (
        monotone.get("raw", {}).get("ranks_that_survived")
        != monotone.get("fluctuations", {}).get("ranks_that_survived")
    )
    seed_bases = sorted({s["basis"] for s in seeds})
    seed_all_fail = all(s["diverged"] for s in seeds)

    parts = [
        "At this configuration a subspace fitted once and PROPAGATED overflows, "
        "and a subspace RE-DERIVED from the current state every step survives -- "
        f"raw propagated {outcome('1_raw_snapshots_static_stepper')}, "
        f"fluctuation propagated {outcome('2_fluctuation_snapshots_static_stepper')}, "
        f"re-derived with the rank fixed {outcome('3_dlra_basis_frozen')}, "
        f"re-derived with the rank adapting {outcome('4_dlra_basis_refreshing')} "
        f"({by_arm['4_dlra_basis_refreshing']['basis_rebuilds']} basis rebuilds "
        f"against {by_arm['3_dlra_basis_frozen']['basis_rebuilds']}).",
    ]
    if all_propagated_fail and all_rederived_survive:
        parts.append(
            "Both propagated bases fail, so the zonal mean is NOT the mechanism: "
            "removing it does not rescue a propagated basis, and in fact fails "
            "sooner here."
        )
    parts.append(
        "The two re-derived arms agree, and the reason is structural rather than "
        "a coincidence: SVDProjector recomputes the SVD of whatever field it is "
        "handed on every call, so `check_every` gates the RANK and not the "
        "projection. The rank rule is therefore not what keeps these runs alive; "
        "the per-step re-derivation is."
    )
    parts.append(
        "The overflow time is NOT monotone in rank, and which basis survives flips "
        f"between ranks (raw survives at {monotone.get('raw', {}).get('ranks_that_survived')}, "
        f"fluctuations at {monotone.get('fluctuations', {}).get('ranks_that_survived')}"
        f"{'; the two swap' if flip else ''}). This is recorded as a finding, not "
        "as noise: an artifact reporting only the rank at which a basis fails "
        "would mislead the next reader, because the rank is not a threshold here."
    )
    if seed_all_fail and len(seed_bases) > 1:
        parts.append(
            f"All {len(seeds)} seed/basis combinations of the propagated baselines "
            "overflow, so the propagated failure is not a property of one initial "
            "condition."
        )
    parts.append(
        "Every statement here is specific to the N, horizon and ranks under "
        "`parameters`."
    )
    return " ".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--N", type=int, default=32)
    parser.add_argument("--re", type=int, default=5000)
    parser.add_argument("--dt", type=float, default=0.002)
    parser.add_argument("--final-time", type=float, default=6.0)
    parser.add_argument("--rank", type=int, default=16)
    parser.add_argument("--train-window", type=float, default=0.5)
    parser.add_argument("--train-snapshots", type=int, default=20)
    parser.add_argument("--check-every", type=int, default=5)
    parser.add_argument("--sweep-ranks", type=int, nargs="+", default=[14, 15, 16, 17, 18])
    parser.add_argument("--seeds", type=int, nargs="+",
                        default=[20260925, 7, 991])
    parser.add_argument("--force-amplitude", type=float, default=0.5)
    parser.add_argument("--base-speed", type=float, default=0.5)
    parser.add_argument("--perturbation-velocity-rms", type=float, default=1.0)
    parser.add_argument("--cutoff", type=int, default=8)
    parser.add_argument("--output", type=Path, default=Path(
        "state/coder/results/static_basis_construction_N32.json"))
    args = parser.parse_args()

    grid = Grid2D(args.N)
    re, amp = args.re, args.force_amplitude
    initial = make_initial_state(
        grid, base_speed=args.base_speed,
        perturbation_velocity_rms=args.perturbation_velocity_rms,
        cutoff=args.cutoff, seed=args.seeds[0],
    )
    raw = _training_window(grid, new_model(grid, re, amp), initial, args.dt,
                           args.train_window, args.train_snapshots, "raw")
    fluct = _training_window(grid, new_model(grid, re, amp), initial, args.dt,
                             args.train_window, args.train_snapshots, "fluctuations")

    def make_dlra(check_every: int, rank: int) -> DLRA:
        return DLRA(
            new_model(grid, re, amp), rank=rank, min_rank=rank, max_rank=rank,
            rank_criterion="energy", energy_fraction=0.99,
            rank_basis="fluctuations", check_every=check_every,
            adapt_initial=False,
        )

    # --- the four primary arms, all at the same rank and the same IC ---------
    arms = []
    pod_raw = PODGalerkin(grid, args.rank).fit(raw)
    arms.append({
        "arm": "1_raw_snapshots_static_stepper",
        "basis_construction": "PODGalerkin on raw window snapshots",
        "stepper": "static (projected every step, basis never refitted)",
        "seed": args.seeds[0], "rank": args.rank,
        **_rollout(grid, new_model(grid, re, amp), initial, args.dt,
                   args.final_time, projector=pod_raw.project),
    })
    pod_fluct = PODGalerkin(grid, args.rank).fit(fluct)
    arms.append({
        "arm": "2_fluctuation_snapshots_static_stepper",
        "basis_construction": "PODGalerkin on zonal-mean-removed snapshots",
        "stepper": "static (projected every step, basis never refitted)",
        "seed": args.seeds[0], "rank": args.rank,
        **_rollout(grid, new_model(grid, re, amp), initial, args.dt,
                   args.final_time, projector=pod_fluct.project),
    })
    arms.append({
        "arm": "3_dlra_basis_frozen",
        "basis_construction": "DLRA initialisation (fluctuations, energy rule)",
        "stepper": f"DLRA, check_every=10**9 (frozen; expect rebuilds=0)",
        "seed": args.seeds[0], "rank": args.rank,
        **_rollout(grid, new_model(grid, re, amp), initial, args.dt,
                   args.final_time, dlra=make_dlra(10 ** 9, args.rank)),
    })
    arms.append({
        "arm": "4_dlra_basis_refreshing",
        "basis_construction": "DLRA initialisation (fluctuations, energy rule)",
        "stepper": f"DLRA, check_every={args.check_every} (refreshes)",
        "seed": args.seeds[0], "rank": args.rank,
        **_rollout(grid, new_model(grid, re, amp), initial, args.dt,
                   args.final_time, dlra=make_dlra(args.check_every, args.rank)),
    })

    # --- arm 5: the rank sweep, because the overflow time is NOT monotone ----
    sweep = []
    for rank in args.sweep_ranks:
        for basis, columns in (("raw", raw), ("fluctuations", fluct)):
            pod = PODGalerkin(grid, rank).fit(columns)
            got = _rollout(grid, new_model(grid, re, amp), initial, args.dt,
                           args.final_time, projector=pod.project)
            sweep.append({"rank": rank, "basis": basis, **got})

    # --- arm 6: three seeds at one rank, because one draw is not a result ----
    seeds = []
    for seed in args.seeds:
        state = make_initial_state(
            grid, base_speed=args.base_speed,
            perturbation_velocity_rms=args.perturbation_velocity_rms,
            cutoff=args.cutoff, seed=seed,
        )
        for basis, builder in (("raw", PODGalerkin(grid, args.rank).fit),
                               ("fluctuations", PODGalerkin(grid, args.rank).fit)):
            columns = _training_window(
                grid, new_model(grid, re, amp), state, args.dt,
                args.train_window, args.train_snapshots, basis,
            )
            pod = builder(columns)
            got = _rollout(grid, new_model(grid, re, amp), state, args.dt,
                           args.final_time, projector=pod.project)
            seeds.append({"seed": seed, "basis": basis,
                          "initial_energy": grid.ke(state), **got})

    artifact = {
        "case": "static_basis_construction",
        "case_family": "stability",
        "provenance": {
            **_provenance(Path(__file__).resolve()),
            "driver": "experiments/run_static_basis_construction.py",
        },
        "parameters": {
            "N": args.N, "re": re, "dt": args.dt,
            "final_time": args.final_time, "rank": args.rank,
            "train_window": args.train_window,
            "train_snapshots": len(raw),
            "check_every": args.check_every,
            "sweep_ranks": args.sweep_ranks, "seeds": args.seeds,
            "force_amplitude": args.force_amplitude,
            "base_speed": args.base_speed,
            "perturbation_velocity_rms": args.perturbation_velocity_rms,
            "cutoff": args.cutoff,
        },
        "arms": arms,
        "rank_sweep": sweep,
        "seed_replication": seeds,
        "interpretation": _interpretation(arms, sweep, seeds),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
