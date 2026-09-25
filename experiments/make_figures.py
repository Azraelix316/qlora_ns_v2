"""Generate compact paper figures from the committed coder result JSONs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "state/coder/results")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "experiments/figures")
    args = parser.parse_args()
    import matplotlib.pyplot as plt

    args.output_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["DejaVu Serif"],
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "legend.fontsize": 8,
            "legend.frameon": False,
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.18,
            "grid.linestyle": "-",
            "lines.linewidth": 1.6,
        }
    )
    colors = {"full": "#264653", "pod": "#8C8C8C", "dlra": "#E76F51", "ref": "#0072B2"}
    re_files = {
        re: args.results / f"kolmogorov_re{re}_N64.json" for re in (100, 1000, 5000)
    }
    data = {re: load(path) for re, path in re_files.items()}

    # Rank and error over the short common horizon.
    fig, axes = plt.subplots(1, 2, figsize=(6.75, 2.7))
    ax = axes[0]
    rank = data[5000]["dlra"]["rank_history"]
    ax.plot(np.arange(len(rank)) * data[5000]["parameters"]["dt"], rank, color=colors["dlra"], label="adaptive DLRA")
    ax.set_xlabel("time")
    ax.set_ylabel("retained rank")
    ax.set_title("Adaptive rank growth")
    ax.legend(loc="best")
    ax = axes[1]
    for re, result in data.items():
        for method in ("pod", "dlra"):
            rows = result[method]["comparison"]
            ax.plot(
                [row["time"] for row in rows],
                [row["relative_l2"] for row in rows],
                color=colors[method],
                linestyle="-" if method == "dlra" else "--",
                alpha=0.9 if re == 5000 else 0.45,
                label=f"{method.upper()} Re={re}",
            )
    ax.set_xlabel("time")
    ax.set_ylabel("relative $L^2$ error")
    ax.set_title("Error against full grid")
    ax.legend(ncol=2, fontsize=6.5)
    fig.tight_layout()
    fig.savefig(args.output_dir / "fig_rank_error.pdf", bbox_inches="tight")
    fig.savefig(args.output_dir / "fig_rank_error.png", bbox_inches="tight")
    plt.close(fig)

    # Singular-value decay at selected times, normalized by the leading value.
    fig, ax = plt.subplots(figsize=(3.25, 2.6))
    result = data[5000]
    steps = result["dlra"]["singular_value_steps"]
    for step, color in zip(steps[:: max(1, len(steps) // 4)], ["#264653", "#2A9D8F", "#E9C46A", "#E76F51"]):
        idx = steps.index(step)
        values = np.asarray(result["dlra"]["singular_values"][idx])
        values = values[values > 0]
        ax.semilogy(np.arange(1, len(values) + 1), values, "o-", ms=2.5, color=color, label=f"t={step * result['parameters']['dt']:.2f}")
    ax.set_xlabel("singular-value index")
    ax.set_ylabel(r"$\sigma_i/\sigma_1$")
    ax.set_title("Slow singular-value decay")
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.output_dir / "fig_singular_values.pdf", bbox_inches="tight")
    fig.savefig(args.output_dir / "fig_singular_values.png", bbox_inches="tight")
    plt.close(fig)

    # Cost comparison; include the honest SVD overhead.
    fig, ax = plt.subplots(figsize=(3.25, 2.6))
    methods = ["full", "pod", "dlra"]
    x = np.arange(3)
    width = 0.24
    for j, re in enumerate((100, 1000, 5000)):
        vals = [data[re][m]["wall_seconds_per_step"] * 1e3 for m in methods]
        bars = ax.bar(x + (j - 1) * width, vals, width, label=f"Re={re}", color=["#264653", "#56B4E9", "#E76F51"][j])
        for bar, value in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.1f}", ha="center", va="bottom", fontsize=6)
    ax.set_xticks(x, ["full", "POD", "DLRA"])
    ax.set_ylabel("ms / step")
    ax.set_title("Measured cost")
    ax.legend(ncol=3, fontsize=7)
    fig.tight_layout()
    fig.savefig(args.output_dir / "fig_cost.pdf", bbox_inches="tight")
    fig.savefig(args.output_dir / "fig_cost.png", bbox_inches="tight")
    plt.close(fig)

    print(f"wrote figures to {args.output_dir}")


if __name__ == "__main__":
    main()
