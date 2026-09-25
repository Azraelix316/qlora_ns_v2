"""Assemble benchmark_summary.json from the committed result artifacts.

The summary used to be hand-copied, which is exactly the failure mode P0 item
5 warns about (a number in a table that no artifact supports).  This driver
derives every field from the artifacts themselves, records each one's commit,
and refuses to emit a summary whose members disagree about the initial state.

It is an aggregate only: it introduces no measurement of its own, and it
reproduces whatever the artifacts say -- including a result that contradicts
the method.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RESULTS = ROOT / "state" / "coder" / "results"


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def load(name: str) -> dict | None:
    path = RESULTS / name
    if not path.exists():
        return None
    return json.loads(path.read_text())


def method_row(block: dict, key: str) -> dict:
    """The fields every method block reports, kept uniform across methods."""
    return {
        "max_abs_divergence": block.get("max_abs_divergence"),
        "stable": block.get("stable"),
        "final_energy": block.get("final_energy"),
        "max_relative_energy": block.get("max_relative_energy"),
        # Labelled for what it is: once trajectories decorrelate this measures
        # phase, not accuracy (P0 metric order, item 1 and item 4).
        "max_trajectory_divergence": block.get("max_relative_l2_vs_full"),
        "wall_seconds_per_step": block.get("wall_seconds_per_step"),
        "max_scaled_energy_balance_residual": block.get(
            "max_scaled_energy_balance_residual"
        ),
        "max_scaled_full_pde_energy_residual": block.get(
            "max_scaled_full_pde_energy_residual"
        ),
        "rank_min": block.get("rank_min"),
        "rank_max": block.get("rank_max"),
        "rank_final": block.get("rank_final"),
        "linear_algebra_seconds_per_step": block.get(
            "linear_algebra_seconds_per_step"
        ),
        "linear_algebra_calls": block.get("linear_algebra_calls"),
        "initial_projection_relative_l2": block.get("initial_projection_relative_l2"),
    }


def suite_case(data: dict, file_name: str) -> dict:
    params = data["parameters"]
    pod = data["pod"]
    dlra = data["dlra"]
    return {
        "file": file_name,
        "git_commit": data["provenance"]["git_commit"],
        "re": data["reynolds"],
        "N": data["grid"]["N"],
        "dt": params["dt"],
        "final_time": params["final_time"],
        "ic_reference_N": params.get("ic_reference_N"),
        "initial_state": data["initial_state"],
        "initial_energy": data["initial_energy"],
        "full": method_row(data["full"], "full"),
        "pod": method_row(pod, "pod"),
        "dlra": method_row(dlra, "dlra"),
        "pod_requested_rank": pod.get("effective_rank"),
        "dealias_rank_ceiling": 2 * (data["grid"]["N"] // 3) + 1,
        # CHECKLIST 1.0: a POD baseline at r=16 against an adaptive method that
        # reached r=43 is not a rank-matched comparison.  The mismatch is
        # stated rather than hidden; making it matched is F5's job and is
        # blocked behind the regime decision.
        "rank_mismatch": {
            "pod_rank": pod.get("effective_rank"),
            "dlra_rank_max": dlra.get("rank_max"),
            "matched": pod.get("effective_rank") == dlra.get("rank_max"),
            "statement": (
                "static POD is a fixed-rank offline baseline at r="
                f"{pod.get('effective_rank')}; adaptive DLRA reached r="
                f"{dlra.get('rank_max')}. These are not rank-matched, so this "
                "row is not evidence about either method's merit at equal rank."
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=RESULTS / "benchmark_summary.json"
    )
    args = parser.parse_args()

    cases = []
    for re in (100, 1000, 5000):
        name = f"kolmogorov_re{re}_N64.json"
        data = load(name)
        if data is not None:
            cases.append(suite_case(data, name))

    # P0: every method in a comparison starts from a bit-identical state.  The
    # summary refuses to paper over a mismatch.
    fingerprints = {c["initial_state"]["sha256"] for c in cases}
    if len(fingerprints) > 1:
        raise SystemExit(
            "the N=64 suite does not share one initial state: "
            f"{sorted(fingerprints)}"
        )
    for case in cases:
        projection = case["pod"]["initial_projection_relative_l2"]
        if projection is None:
            raise SystemExit(
                f"{case['file']}: the static baseline reports no IC projection "
                "error, so P0 cannot be checked for it"
            )
        # P0: the static baseline must start from the same bit-identical IC, so
        # its L2 projection of that IC has to be the identity to roundoff.
        if not projection < 1e-12:
            raise SystemExit(
                f"{case['file']}: the static baseline's IC projection error is "
                f"{projection:.3e}, not roundoff -- P0 is violated and this "
                "summary must not be emitted"
            )
        if case["dlra"]["rank_max"] is None or case["pod"]["rank_min"] is None:
            raise SystemExit(f"{case['file']}: missing rank diagnostics")

    grid_check = None
    n128 = load("kolmogorov_re5000_N128.json")
    if n128 is not None:
        grid_check = {
            "file": "kolmogorov_re5000_N128.json",
            "git_commit": n128["provenance"]["git_commit"],
            "N": n128["grid"]["N"],
            "dt": n128["parameters"]["dt"],
            "final_time": n128["parameters"]["final_time"],
            "ic_reference_N": n128["parameters"].get("ic_reference_N"),
            "initial_energy": n128["initial_energy"],
            "initial_state_rank": n128["initial_state"]["numerical_rank"],
            "full": method_row(n128["full"], "full"),
            "pod": method_row(n128["pod"], "pod"),
            "dlra": method_row(n128["dlra"], "dlra"),
            "note": (
                "P0 item 3: dt is scaled with dx and the final time, IC spectral "
                "content and method settings are held fixed, so only N changes. "
                "ic_reference_N makes the perturbation the identical field "
                "sampled on the finer grid rather than a redraw. At this N the "
                "DLRA reaches the configured max_rank, not the dealias ceiling."
            ),
        }

    long_check = None
    long_data = load("kolmogorov_re5000_N64_long.json")
    if long_data is not None:
        lp = long_data["parameters"]
        long_check = {
            "file": "kolmogorov_re5000_N64_long.json",
            "git_commit": long_data["provenance"]["git_commit"],
            "final_time": lp.get("final_time"),
            # Read from the artifact, never from the file name: the previous
            # hand-assembled summary asserted re/N that the artifact did not
            # record, which is exactly the provenance failure P0 item 5 exists
            # to prevent.  ``None`` here means the driver must be fixed.
            "re": lp.get("re"),
            "N": lp.get("N"),
            "re_and_N_recorded": lp.get("re") is not None and lp.get("N") is not None,
            "full_final_energy": long_data["full"]["final_energy"],
            "dlra_final_energy": long_data["dlra"]["final_energy"],
            "full_max_abs_divergence": long_data["full"]["max_abs_divergence"],
            "dlra_max_abs_divergence": long_data["dlra"]["max_abs_divergence"],
            "dlra_rank_min": long_data["dlra"]["rank_min"],
            "dlra_rank_max": long_data["dlra"]["rank_max"],
            "max_trajectory_divergence": long_data.get(
                "max_relative_l2_dlra_vs_full"
            ),
            "note": (
                "full-grid and DLRA only; T=1 is a sustained check, not a "
                "statistical window (S5/D11.2: no turbulence statistic at "
                "t <= 0.1, and this horizon is not claimed stationary)"
            ),
        }
        if not long_check["re_and_N_recorded"]:
            print(
                "warning: kolmogorov_re5000_N64_long.json does not record re/N "
                "in its parameters; the summary reports them as null rather "
                "than inferring them from the file name"
            )

    sweep = None
    sweep_data = load("rank_growth_sweep.json")
    if sweep_data is not None:
        sweep = {
            "file": "rank_growth_sweep.json",
            "git_commit": sweep_data["provenance"]["git_commit"],
            "parameters": sweep_data["parameters"],
            "rows": sweep_data["rows"],
        }

    cost = None
    cost_data = load("cost_retiming.json")
    if cost_data is not None:
        cost = {
            "file": "cost_retiming.json",
            "git_commit": cost_data["provenance"]["git_commit"],
            "thread_settings": cost_data["environment"]["thread_settings"],
            "grids": [
                {
                    "N": g["N"],
                    "steps_per_repeat": g["steps_per_repeat"],
                    "repeats": g["repeats"],
                    "reference_seconds_per_step": g[
                        "reference_full_step_seconds_per_step"
                    ],
                    "reference_relative_spread": g["reference_relative_spread"],
                    "rows": g["rows"],
                }
                for g in cost_data["grids"]
            ],
            "rank_independence": cost_data["rank_independence"],
        }

    regime = None
    regime_name = None
    regime_data = load("regime_pilot.json")
    if regime_data is not None:
        regime_name = "regime_pilot.json"
    else:
        # The pilot is per (Re, forcing amplitude); prefer the canonical
        # amplitude rather than silently taking whichever sorts first.
        for path in sorted(RESULTS.glob("regime_pilot_*.json")):
            data = load(path.name)
            if data and data["parameters"]["force_amplitude"] == 0.5:
                regime_data, regime_name = data, path.name
                break
    if regime_data is not None:
        regime = {
            "file": regime_name,
            "git_commit": regime_data["provenance"]["git_commit"],
            "re": regime_data["parameters"]["re"],
            "force_amplitude": regime_data["parameters"]["force_amplitude"],
            "rows": [
                {
                    "final_time": r["final_time"],
                    "S2_energy_fluct_drift": r["S2_energy_fluct_drift"],
                    "S2_enstrophy_fluct_drift": r["S2_enstrophy_fluct_drift"],
                    "S2_passes": r["S2_passes"],
                    "final_energy_total": r["final_energy_total"],
                    "final_energy_fluct": r["final_energy_fluct"],
                    "zonal_share_of_total_energy_at_end": r[
                        "zonal_share_of_total_energy_at_end"
                    ],
                }
                for r in regime_data["rows"]
            ],
            "qualifying_horizons": regime_data["qualifying_horizons"],
            "window_rank_table": regime_data.get("window_rank_table", []),
            "windowed_spectra": {
                key: {
                    "window_start": val.get("window_start"),
                    "window_end": val.get("window_end"),
                    "samples": val.get("samples"),
                    "sum_E_fluct": val.get("sum_E_fluct"),
                    "sum_Z_fluct": val.get("sum_Z_fluct"),
                    "dealias_resolved_k_max": val.get("dealias_resolved_k_max"),
                }
                for key, val in regime_data.get("windowed_spectra", {}).items()
            },
            "rank_finding": (
                "window_rank_table gives the modes needed to represent the "
                "fluctuations over [0, W]: r99 grows 1 -> 16 over the first "
                "eight time units, while the amplitude rule requests more modes "
                "than the dealiasing ceiling holds from t=2 onward, so its rank "
                "trace is the grid's and not the dynamics'"
            ),
        }

    crossover = None
    crossover_data = load("crossover_surface.json")
    if crossover_data is not None and "by_reynolds" not in crossover_data:
        # A stale artifact must not take the whole summary down with it.  Say what
        # is wrong and which command regenerates it, rather than raising a
        # KeyError that leaves the reviewer with no summary at all.
        crossover = {
            "status": "stale_schema",
            "reason": (
                "`crossover_surface.json` predates the `by_reynolds` layout, so "
                "its numbers cannot be read here. Regenerate with "
                "`experiments/run_crossover.py`; the committed artifact must come "
                "from the committed driver (D14.4)."
            ),
            "git_commit": crossover_data["provenance"]["git_commit"],
        }
        crossover_data = None
    if crossover_data is not None:
        p = crossover_data["parameters"]
        crossover = {
            "file": "crossover_surface.json",
            "git_commit": crossover_data["provenance"]["git_commit"],
            "re": p["re"],
            "N": p["N"],
            "force_amplitude": p["force_amplitude"],
            "ranks": p["ranks"],
            "reynolds_numbers": p.get("reynolds_numbers", [p.get("re")]),
            "horizons": p["horizons"],
            "dealias_ceiling": p["dealias_ceiling"],
            "moving_window_lengths": p.get(
                "moving_window_lengths", [p.get("moving_window_length")]
            ),
            "moving_window_refit_interval": p["moving_window_refit_interval"],
            "rank_policy": p["rank_policy"],
            "moving_window_refit_offset": p.get("moving_window_refit_offset"),
            "key_schema": crossover_data.get("key_schema"),
            "by_reynolds": {
                re_key: {
                    "crossovers": re_case["crossovers"],
                    "resolved_t_star": [
                        {
                            "rank": c["rank"],
                            "window": c["window"],
                            "t_star": c["t_star"],
                            "t_star_linear": c.get("t_star_linear"),
                            "bracket": c.get("bracket"),
                            "status": c["status"],
                            "crossings": c["crossings"],
                        }
                        for c in re_case["crossovers"]
                    ],
                    "dlra_surface": re_case["dlra"],
                    "static_moving_window_surface": re_case["static_moving_window"],
                }
                for re_key, re_case in crossover_data["by_reynolds"].items()
            },
            "error_columns": crossover_data["error_columns"],
            "interpretation": crossover_data["interpretation"],
        }

    memory = None
    memory_data = load("peak_memory.json")
    if memory_data is not None:
        memory = {
            "file": "peak_memory.json",
            "git_commit": memory_data["provenance"]["git_commit"],
            "grids": memory_data["parameters"]["grids"],
            "ranks": memory_data["parameters"]["ranks"],
            "methods": memory_data["parameters"]["methods"],
            "steps": memory_data["parameters"]["steps"],
            "noise_floor_mib": memory_data.get("noise_floor_mib"),
            "rank_scaling": memory_data["rank_scaling"],
            "full_grid_peak_mib": {
                f"N={r['N']}": r["peak_rss_mib"]
                for r in memory_data["measurements"]
                if r["method"] == "full" and r["repeat"] == 0
            },
            "interpretation": memory_data["interpretation"],
        }

    output = {
        "generated_by": "experiments/make_summary.py",
        "git_commit": _git_commit(),
        "protocol": (
            "N=64 suite: Re={100,1000,5000}, dt=5e-4, T=0.1, force amplitude 0.5, "
            "base speed 0.5, perturbation velocity RMS 1.0, band-limit box 8, "
            "seed 20260925, static POD rank 16 fitted offline including t=0, DLRA "
            "relative amplitude cutoff 1e-10 with check_every 5. Every method "
            "starts from the same bit-identical initial state (P0)."
        ),
        "metric_note": (
            "'max_trajectory_divergence' is relative L2 against the reference "
            "and is labelled as trajectory divergence, not accuracy: once two "
            "solutions decorrelate it measures phase. The accuracy metrics are "
            "time-averaged KE/enstrophy and spectral agreement over a stationary "
            "window, which the regime pilot must establish first."
        ),
        "re_independence_caveat": (
            "CHECKLIST 1.0: the DLRA trajectory divergence is nearly identical "
            "at all three Re, so at this horizon it is measuring the setup "
            "(fixed rank cap, fixed T, fixed in-sample POD window) and not the "
            "Reynolds number. The numbers are "
            + ", ".join(
                f"Re={c['re']}: {c['dlra']['max_trajectory_divergence']:.3e}"
                for c in cases
            )
            + ". No Re-dependence may be claimed from this suite."
        ),
        "rank_matched_comparison": (
            "CHECKLIST 1.0: the static-POD baseline is fixed-rank and the DLRA "
            "is adaptive, so the suite is not a rank-matched comparison. A "
            "matched-rank POD is F5 and is downstream of the regime decision."
        ),
        "cost_note": (
            "Per-step cost is reported under two accountings and no per-step "
            "speedup is claimed: the reduced method pays the same full-grid "
            "nonlinear evaluation as the reference plus its own whole-field "
            "SVD, which is Theta(N^3) and rank-independent (D11.1). Threads are "
            "pinned and recorded, a warm-up is discarded, and the median of 7 "
            "repeats over 2000 steps is reported with its min/max spread. Two "
            "caveats on the numbers themselves: the node is shared, so the "
            "spread is the honest uncertainty and the minimum is the "
            "least-contended estimate; and the reference block and the reduced "
            "blocks are timed sequentially rather than interleaved, so a load "
            "drift between them would bias the ratio by no more than the "
            "reported spreads."
        ),
        "forcing_name_caveat": (
            "The driver calls this a Kolmogorov flow, but the forcing is a "
            "periodic unidirectional shear f = (A sin(k y), 0), not the "
            "Arnold-Korkin-Sinitsyn cellular pump. CHECKLIST 1.3 asks that the "
            "forcing match what the name claims; the naming decision belongs to "
            "the reviewer and writer, and no result is affected by it because "
            "the forcing is recorded in every artifact's parameters."
        ),
        "cases": cases,
        "grid_check": grid_check,
        "long_time_check": long_check,
        "rank_threshold_sweep": sweep,
        "cost_retiming": cost,
        "regime_pilot": regime,
        "crossover_surface": crossover,
        "peak_memory": memory,
        "honesty_note": (
            "The static-POD baseline is now correct (its fit had reshaped the "
            "snapshot stack in C order, interleaving snapshots); every number "
            "here is post-fix. At T=0.1 the corrected static baseline is more "
            "accurate than adaptive DLRA, because its offline window is a prefix "
            "of the evaluated trajectory and is effectively rank 3, so no "
            "accuracy advantage is claimed for the proposed method at this "
            "horizon. Per D11.2 the regime is not turbulence and no turbulence "
            "statistic is drawn from t <= 0.1."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
