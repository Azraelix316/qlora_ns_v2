"""Figures for the paper, generated only from committed artifacts.

Three things this script deliberately does **not** do, each because a binding
rule forbids it:

* It does not title a rank trace "adaptive rank growth".  The committed runs
  sit at the dealiasing ceiling, so a trace of 17 -> 43 is the grid, not the
  dynamics (D11.3).  The rank figure is the *windowed* rank, which is the
  quantity that is grid-independent.
* It does not label pointwise L2 as "error".  Once solutions decorrelate it
  measures phase, not accuracy, so every such axis is labelled trajectory
  divergence and the accuracy quantities (time-averaged KE/enstrophy, spectra)
  are shown next to them.
* It does not plot the singular values of a rank-truncated reduced state as a
  spectrum.  Such a state has exactly as many values as its rank and decays
  smoothly by construction; spectra are taken from the full-grid reference
  (F2, R5).

Every figure records the artifact and commit it came from, so a figure cannot
outlive the numbers it was drawn from.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict | None:
    if not path.exists():
        print(f"  (missing, skipped: {path.name})")
        return None
    return json.loads(path.read_text())


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()[:8]
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def provenance(
    results: Path, out: Path, names: list[str], skipped: list[tuple[str, str]]
) -> None:
    """Record which artifact backs each figure -- *and* which figure is missing.

    A figure that silently failed to generate is indistinguishable from one that
    was never asked for, so an expected-but-skipped figure is stated with the
    reason.  That is the whole point of recording provenance: a figure must not
    be able to disappear between one commit and the next without a line here
    saying so.
    """
    lines = ["# Figure provenance", ""]
    for name in names:
        path = results / name
        if path.exists():
            data = json.loads(path.read_text())
            lines.append(
                f"- `{name}` -- commit "
                f"`{data.get('provenance', {}).get('git_commit', '?')[:8]}`"
            )
    if skipped:
        lines += ["", "## Expected but not generated", ""]
        for figure, reason in skipped:
            lines.append(f"- **{figure}** -- {reason}")
    lines += ["", f"figures generated at commit `{git_commit()}`", ""]
    (out / "PROVENANCE.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results", type=Path, default=ROOT / "state" / "coder" / "results"
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "experiments" / "figures"
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    R = args.results
    colors = {"full": "#264653", "pod": "#8C8C8C", "dlra": "#E76F51",
              "ref": "#0072B2", "a": "#2A9D8F", "b": "#E9C46A"}
    used: list[str] = []
    skipped: list[tuple[str, str]] = []

    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 9,
        "axes.labelsize": 9, "axes.titlesize": 10, "legend.fontsize": 8,
        "legend.frameon": False, "figure.dpi": 150, "savefig.dpi": 300,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.18, "lines.linewidth": 1.6,
    })

    # ---------------------------------------------------------------- figure 1
    # The premise: windowed rank vs horizon, on the fluctuations, at two grids.
    # This replaces the old "adaptive rank growth" panel.
    pilots = {
        "N=64": load(R / "regime_pilot_re5000_A0p2.json"),
        "N=128": load(R / "regime_pilot_re5000_N128_A0p2.json"),
    }
    pilots = {k: v for k, v in pilots.items() if v and v.get("window_rank_table")}
    if pilots:
        used += ["regime_pilot_re5000_A0p2.json", "regime_pilot_re5000_N128_A0p2.json"]
        fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.8))
        ax = axes[0]
        for (label, data), style in zip(pilots.items(), (("-", "o"), ("--", "s"))):
            table = {r["window_end"]: r for r in data["window_rank_table"]}
            W = sorted(table)
            ax.plot(W, [table[w]["r99"] for w in W], style[0], marker=style[1],
                    markersize=3.5, color=colors["a"] if "64" == label[-2:] else colors["b"],
                    label=f"r99, {label}")
            ax.plot(W, [table[w]["r999"] for w in W], style[0], marker=style[1],
                    markersize=3.5, alpha=0.45,
                    color=colors["a"] if "64" == label[-2:] else colors["b"],
                    label=f"r999, {label}")
        ax.set_xlabel("window end $W$")
        ax.set_ylabel("modes to represent the window")
        ax.set_title("Rank of the windowed fluctuations")
        ax.legend(fontsize=7)
        ax = axes[1]
        for (label, data), style in zip(pilots.items(), (("-", "o"), ("--", "s"))):
            table = {r["window_end"]: r for r in data["window_rank_table"]}
            W = sorted(table)
            ceiling = 2 * (int(label.split("=")[1]) // 3) + 1
            ax.plot(W, [table[w]["amp_1e-6"] for w in W], style[0], marker=style[1],
                    markersize=3.5, label=f"amplitude rule, {label}")
            ax.axhline(ceiling, color=colors["ref"], linestyle=":", linewidth=1.0)
            ax.annotate(f"dealias ceiling {ceiling}", (W[0], ceiling),
                        textcoords="offset points", xytext=(2, 3),
                        fontsize=6.5, color=colors["ref"])
        ax.set_yscale("log")
        ax.set_xlabel("window end $W$")
        ax.set_ylabel("modes requested (log)")
        ax.set_title("The amplitude rule asks for the grid")
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(args.output_dir / "fig_window_rank.pdf", bbox_inches="tight")
        fig.savefig(args.output_dir / "fig_window_rank.png", bbox_inches="tight")
        plt.close(fig)

    # ---------------------------------------------------------------- figure 2
    # Full-grid state spectrum: the IC cliff against the developed state.
    # Never the reduced state's spectrum.
    suite = {re: load(R / f"kolmogorov_re{re}_N64.json") for re in (100, 1000, 5000)}
    suite = {k: v for k, v in suite.items() if v}
    if suite:
        used += [f"kolmogorov_re{re}_N64.json" for re in suite]
        data = suite[5000]
        full = data["full"]
        s_ic = np.asarray(full["singular_values"][0])
        s_end = np.asarray(full["singular_values"][-1])
        fig, ax = plt.subplots(figsize=(3.5, 2.7))
        idx = np.arange(1, s_ic.size + 1)
        ax.semilogy(idx, s_ic / s_ic[0], color=colors["ref"], label="initial condition ($t=0$)")
        ax.semilogy(idx, s_end / s_end[0], color=colors["dlra"],
                    label=f"developed ($t={data['parameters']['final_time']}$)")
        ax.axvline(17, color=colors["full"], linestyle=":", linewidth=1.0)
        ax.annotate("IC is exactly rank 17", (17, 1e-2), textcoords="offset points",
                    xytext=(4, 0), fontsize=7, color=colors["full"])
        ax.set_xlabel("mode index $r$")
        ax.set_ylabel(r"$\sigma_r/\sigma_1$")
        ax.set_title("Full-grid state spectrum (all resolved modes)")
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(args.output_dir / "fig_spectrum.pdf", bbox_inches="tight")
        fig.savefig(args.output_dir / "fig_spectrum.png", bbox_inches="tight")
        plt.close(fig)

    # ---------------------------------------------------------------- figure 3
    # Trajectory divergence, labelled as such, with the accuracy quantity
    # (time-averaged fluctuation KE) beside it.
    if suite:
        fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.8))
        ax = axes[0]
        for re, result in suite.items():
            rows = result["dlra"]["comparison"]
            ax.plot([r["time"] for r in rows], [r["relative_l2"] for r in rows],
                    color=colors["dlra"], alpha=0.9 if re == 5000 else 0.4,
                    label=f"DLRA Re={re}")
            rows = result["pod"]["comparison"]
            ax.plot([r["time"] for r in rows], [r["relative_l2"] for r in rows],
                    color=colors["pod"], linestyle="--",
                    alpha=0.9 if re == 5000 else 0.4, label=f"static POD Re={re}")
        ax.set_xlabel("time")
        ax.set_ylabel(r"relative $L^2$")
        ax.set_title("Trajectory divergence, not error")
        ax.legend(fontsize=6.5, ncol=2)
        ax = axes[1]
        for re, result in suite.items():
            t = np.arange(len(result["full"]["energy_history"])) * result["parameters"]["dt"]
            ax.plot(t, result["full"]["energy_history"], color=colors["full"],
                    alpha=0.9 if re == 5000 else 0.4, label=f"full Re={re}")
        ax.set_xlabel("time")
        ax.set_ylabel(r"$E$")
        ax.set_title(r"Total KE: the zonal mean grows")
        ax.legend(fontsize=6.5)
        fig.tight_layout()
        fig.savefig(args.output_dir / "fig_divergence.pdf", bbox_inches="tight")
        fig.savefig(args.output_dir / "fig_divergence.png", bbox_inches="tight")
        plt.close(fig)

    # ---------------------------------------------------------------- figure 4
    # Exact divergence-freeness per run, including every baseline.
    rows = []
    for re, result in suite.items():
        for method in ("full", "pod", "dlra"):
            rows.append((f"{method} Re={re}", result[method]["max_abs_divergence"]))
    b128 = load(R / "kolmogorov_re5000_N128.json")
    if b128:
        used.append("kolmogorov_re5000_N128.json")
        for method in ("full", "pod", "dlra"):
            rows.append((f"{method} Re=5000 N=128", b128[method]["max_abs_divergence"]))
    baselines = load(R / "baselines_re5000_N64_T8.json")
    if baselines:
        used.append("baselines_re5000_N64_T8.json")
        for name, m in baselines["methods"].items():
            rows.append((name.replace("_", " "), m["max_abs_divergence"]))
    if rows:
        fig, ax = plt.subplots(figsize=(6.9, 0.22 * len(rows) + 1.1))
        names = [r[0] for r in rows]
        # Linear axis in units of the 1e-14 target: a log axis over four decades
        # of roundoff is hard to read and its tick locator overflows.
        values = [float(r[1]) / 1e-14 for r in rows]
        ax.barh(names, values, color=colors["full"])
        ax.axvline(1.0, color=colors["dlra"], linestyle="--", linewidth=1.0)
        ax.annotate("target $10^{-14}$", (1.0, len(rows) - 0.4),
                    textcoords="offset points", xytext=(4, 0), fontsize=7,
                    color=colors["dlra"])
        ax.set_xlabel(r"max $|\nabla\!\cdot u|$ over the run, in units of $10^{-14}$")
        ax.set_title("Exact divergence-freeness holds for every method")
        ax.invert_yaxis()
        fig.tight_layout()
        fig.savefig(args.output_dir / "fig_div_free.pdf", bbox_inches="tight")
        fig.savefig(args.output_dir / "fig_div_free.png", bbox_inches="tight")
        plt.close(fig)

    # ---------------------------------------------------------------- figure 5
    # Cost, two accountings, median with spread, annotated with the threading.
    cost = load(R / "cost_retiming.json")
    if cost is None:
        skipped.append((
            "fig_cost",
            "`cost_retiming.json` is absent, so the per-step cost axis is "
            "missing. The crossover law is uninterpretable without it: a "
            "reader cannot tell what a rank costs.",
        ))
    if cost:
        used.append("cost_retiming.json")
        grids = [g for g in cost["grids"] if g["N"] in (64, 128, 256)]
        fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.8))
        for ax, key, title in (
            (axes[0], "full_step_ratio_vs_reference", "Full step vs the reference"),
            (axes[1], "linear_algebra_ratio_vs_reference", "Linear algebra alone"),
        ):
            for rank, style in zip(sorted({r["rank"] for g in grids for r in g["rows"]}),
                                   (("o", "-"), ("s", "--"))):
                xs = [g["N"] for g in grids
                      for r in g["rows"] if r["rank"] == rank]
                ys = [r[key] for g in grids for r in g["rows"] if r["rank"] == rank]
                if xs:
                    ax.plot(xs, ys, style[1], marker=style[0], markersize=4,
                            color=colors["a"] if rank == 2 else colors["b"],
                            label=f"r={rank}")
            ax.axhline(1.0, color=colors["ref"], linestyle=":", linewidth=1.0)
            ax.set_xscale("log", base=2)
            ax.set_yscale("log", base=2)
            ax.set_xlabel("$N$")
            ax.set_ylabel("ratio to full grid")
            ax.set_title(title)
            ax.legend(fontsize=7)
        threads = cost["environment"]["thread_settings"]
        fig.suptitle(
            "median of "
            f"{grids[0]['repeats']} repeats over {grids[0]['steps_per_repeat']} steps; "
            + ", ".join(f"{k.split('_')[0]}={v}" for k, v in threads.items() if v),
            fontsize=6.5, y=1.02,
        )
        fig.tight_layout()
        fig.savefig(args.output_dir / "fig_cost.pdf", bbox_inches="tight")
        fig.savefig(args.output_dir / "fig_cost.png", bbox_inches="tight")
        plt.close(fig)

    # ---------------------------------------------------------------- figure 6
    # Isotropic spectra of the fluctuations, time-averaged over a window.
    spec_source = None
    for name in ("regime_pilot_re5000_A0p5.json", "regime_pilot_re5000_A0p2.json"):
        data = load(R / name)
        if data and data.get("windowed_spectra"):
            spec_source = (name, data)
            used.append(name)
            break
    if spec_source is None:
        skipped.append((
            "fig_spectra_ek",
            "no pilot artifact carried time-averaged fluctuation spectra",
        ))
    if spec_source:
        name, data = spec_source
        entry = next(iter(data["windowed_spectra"].values()))
        k = np.asarray(entry["k"], dtype=float)
        e = np.asarray(entry["E_fluct"], dtype=float)
        z = np.asarray(entry["Z_fluct"], dtype=float)
        ok = k <= entry["dealias_resolved_k_max"]
        w0, w1 = entry["window_start"], entry["window_end"]

        # Whether a time-averaged spectrum is legitimate is a *measurement*, not
        # a matter of taste, and the measurement is already in the artifact: the
        # S2 drift of each quantity over exactly this window.  A quantity that
        # drifts by more than the S2 bar over the averaging interval is not
        # stationary there, so averaging it reports the average of a moving
        # thing.  The drift is read from the pilot's own rows rather than
        # hardcoded, so the figure cannot claim a window the artifact does not
        # support.
        def drift_of(key: str) -> float | None:
            for row in data.get("rows", []):
                if abs(row["final_time"] - w1) < 1e-9:
                    return row.get(key)
            return None

        d_e = drift_of("S2_energy_fluct_drift")
        d_z = drift_of("S2_enstrophy_fluct_drift")
        bar = 0.10
        # The window may start after the run began, in which case the S2 row at
        # its end measures drift over the final third, not this window; the
        # conservative reading is that this window is at least that non-stationary.
        note_e = "drift n/a" if d_e is None else f"drift {100*d_e:.0f}%"
        z_defensible = d_z is not None and d_z <= bar

        fig, ax = plt.subplots(figsize=(3.6, 2.8))
        ax.semilogy(k[ok], e[ok] / max(e.max(), 1e-300), color=colors["a"],
                    label=rf"$E(k)$  ({note_e})")
        if z_defensible:
            ax.semilogy(k[ok], z[ok] / max(z.max(), 1e-300), color=colors["b"],
                        label=rf"$Z(k)$  (drift {100*d_z:.0f}%)")
        ax.axvline(entry["dealias_resolved_k_max"], color=colors["full"],
                   linestyle=":", linewidth=1.0)
        ax.annotate("dealiased\nrange", (entry["dealias_resolved_k_max"], 3e-3),
                    textcoords="offset points", xytext=(-30, 0), fontsize=6.5,
                    color=colors["full"], ha="right")
        ax.set_xlabel("isotropic wavenumber $k$")
        ax.set_ylabel("normalised, time-averaged")
        ax.set_title(
            rf"$\psi'=\psi-\overline{{\psi}}$, averaged over "
            rf"$t\in[{w0:.4g},{w1:.4g}]$",
            fontsize=9,
        )
        if not z_defensible:
            # Dropping the panel is the honest option, and saying so on the
            # figure is better than leaving a legend entry a reader trusts.
            # Two short lines, placed where the curve leaves room, so the note
            # cannot overrun the axes or collide with the other annotation.
            drift_pct = "not measurable" if d_z is None else f"{100*d_z:.0f}%"
            ax.annotate(
                f"$Z(k)$ omitted: enstrophy drifts\n{drift_pct} over this window "
                f"(S2 bar {100*bar:.0f}%)",
                (0.03, 0.30), xycoords="axes fraction", fontsize=6.2,
                color=colors["dlra"], va="top",
            )
        ax.legend(fontsize=7, loc="upper right")
        fig.tight_layout()
        fig.savefig(args.output_dir / "fig_spectra_ek.pdf", bbox_inches="tight")
        fig.savefig(args.output_dir / "fig_spectra_ek.png", bbox_inches="tight")
        plt.close(fig)
        if not z_defensible:
            skipped.append((
                "fig_spectra_ek: $Z(k)$ panel",
                f"fluctuation enstrophy drifts {100*d_z:.0f}% over the averaging "
                f"window [{w0:g}, {w1:g}], outside the 10% S2 bar, so a "
                "time-averaged $Z(k)$ there would average a moving quantity",
            ))

    provenance(R, args.output_dir, sorted(set(used)), skipped)
    print(f"figures written to {args.output_dir}")


if __name__ == "__main__":
    main()
