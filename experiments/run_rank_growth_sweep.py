"""Measure how the adaptive-rank threshold changes the rank/error tradeoff."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from provenance import provenance as _provenance
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.run_kolmogorov import _git_commit, run_case


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--N", type=int, default=64)
    parser.add_argument("--re", type=int, default=5000)
    parser.add_argument("--dt", type=float, default=0.0005)
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--output", type=Path, default=Path("state/coder/results/rank_growth_sweep.json"))
    args = parser.parse_args()
    rows = []
    for cutoff in (1e-6, 1e-8, 1e-10):
        result = run_case(
            re=args.re,
            N=args.N,
            dt=args.dt,
            nsteps=args.steps,
            force_amplitude=0.5,
            base_speed=0.5,
            perturbation_velocity_rms=1.0,
            cutoff=8,
            train_steps=args.steps // 2,
            snapshot_stride=5,
            compare_stride=20,
            pod_rank=16,
            dlra_rank=2,
            dlra_min_rank=2,
            dlra_max_rank=48,
            dlra_relative_amplitude_cutoff=cutoff,
            dlra_check_every=5,
        )
        dlra = result["dlra"]
        rows.append(
            {
                "relative_amplitude_cutoff": cutoff,
                "stable": dlra["stable"],
                "rank_min": dlra["rank_min"],
                "rank_max": dlra["rank_max"],
                "rank_final": dlra["rank_final"],
                "max_relative_l2_vs_full": dlra["max_relative_l2_vs_full"],
                "max_scaled_invariant_residual": dlra[
                    "max_scaled_energy_balance_residual"
                ],
                "seconds_per_step": dlra["wall_seconds_per_step"],
            }
        )
    output = {
        "case": "rank_growth_sweep",
        "provenance": {
            **_provenance(Path(__file__).resolve()),
            "driver": "experiments/run_rank_growth_sweep.py",
        },
        "parameters": {
            # run_case's own record is the authoritative one (P0 item 5: a
            # default in a signature is not a record of what was run), so take
            # it verbatim and add only what is specific to the sweep.
            **result["parameters"],
            "steps": args.steps,
            "relative_amplitude_cutoffs": [1e-6, 1e-8, 1e-10],
        },
        "initial_state": result["initial_state"],
        "rows": rows,
        "interpretation": "The unprojected candidate is inspected at each check; tighter thresholds retain more slowly decaying singular directions and therefore grow rank.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
