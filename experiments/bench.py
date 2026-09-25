"""Run the planned Re=100/1000/5000 benchmark suite and persist compact results."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.run_kolmogorov import run_case


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--N", type=int, default=64)
    parser.add_argument("--dt", type=float, default=0.002)
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--train-steps", type=int, default=100)
    parser.add_argument("--pod-rank", type=int, default=12)
    parser.add_argument("--dlra-rank", type=int, default=4)
    parser.add_argument("--dlra-min-rank", type=int, default=2)
    parser.add_argument("--dlra-max-rank", type=int, default=48)
    parser.add_argument("--dlra-relative-amplitude-cutoff", type=float, default=1e-6)
    parser.add_argument(
        "--dlra-adapt-initial",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--compare-stride", type=int, default=10)
    parser.add_argument("--force-amplitude", type=float, default=0.2)
    parser.add_argument("--base-speed", type=float, default=0.5)
    parser.add_argument("--perturbation-velocity-rms", type=float, default=0.25)
    parser.add_argument("--cutoff", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260925)
    parser.add_argument("--snapshot-stride", type=int, default=5)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("state/coder/results"),
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary = []
    for re in (100, 1000, 5000):
        result = run_case(
            re=re,
            N=args.N,
            dt=args.dt,
            nsteps=args.steps,
            force_amplitude=args.force_amplitude,
            base_speed=args.base_speed,
            perturbation_velocity_rms=args.perturbation_velocity_rms,
            cutoff=args.cutoff,
            seed=args.seed,
            train_steps=args.train_steps,
            snapshot_stride=args.snapshot_stride,
            compare_stride=args.compare_stride,
            pod_rank=args.pod_rank,
            dlra_rank=args.dlra_rank,
            dlra_min_rank=args.dlra_min_rank,
            dlra_max_rank=args.dlra_max_rank,
            dlra_relative_amplitude_cutoff=args.dlra_relative_amplitude_cutoff,
            dlra_adapt_initial=args.dlra_adapt_initial,
        )
        case_path = args.output_dir / f"kolmogorov_re{re}_N{args.N}.json"
        case_path.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
        summary.append(
            {
                "re": re,
                "file": str(case_path),
                "git_commit": result["provenance"]["git_commit"],
                "full_stable": result["full"]["stable"],
                "full_div": result["full"]["max_abs_divergence"],
                "full_pde_residual": result["full"]["max_scaled_full_pde_energy_residual"],
                "pod_stable": result["pod"]["stable"],
                "pod_error": result["pod"]["max_relative_l2_vs_full"],
                "pod_discrete_residual": result["pod"]["max_scaled_energy_balance_residual"],
                "pod_rank": result["pod"]["rank_final"],
                "dlra_stable": result["dlra"]["stable"],
                "dlra_error": result["dlra"]["max_relative_l2_vs_full"],
                "dlra_discrete_residual": result["dlra"]["max_scaled_energy_balance_residual"],
                "dlra_rank_min": result["dlra"]["rank_min"],
                "dlra_rank_max": result["dlra"]["rank_max"],
                "full_s_per_step": result["full"]["wall_seconds_per_step"],
                "pod_s_per_step": result["pod"]["wall_seconds_per_step"],
                "dlra_s_per_step": result["dlra"]["wall_seconds_per_step"],
            }
        )
        print(json.dumps(summary[-1], sort_keys=True, allow_nan=False))
    aggregate = args.output_dir / f"benchmark_summary_N{args.N}.json"
    aggregate.write_text(
        json.dumps(
            {
                "provenance": {
                    "git_commit": result["provenance"]["git_commit"],
                    "driver": "experiments/bench.py",
                },
                "grid_N": args.N,
                "dt": args.dt,
                "steps": args.steps,
                "initial_state": result["initial_state"],
                "cases": summary,
            },
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    )
    print(f"wrote {aggregate}")


if __name__ == "__main__":
    main()
