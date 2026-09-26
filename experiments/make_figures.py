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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_crossover import t_star_from_rows  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "experiments") not in sys.path:
    sys.path.insert(0, str(ROOT / "experiments"))
# The spread definition is shared with make_summary.py so the figure and
# the persisted summary cannot drift apart.
from make_summary import static_error_spread  # noqa: E402


def load(path: Path) -> dict | None:
    if not path.exists():
        print(f"  (missing, skipped: {path.name})")
        return None
    return json.loads(path.read_text())


# Caption text, recorded as each figure is drawn and written to CAPTIONS.md
# beside PROVENANCE.md.  A panel omitted for a stated reason is exactly right, but
# the reason has to reach the caption or the writer will not know to state it --
# and PROVENANCE.md is a provenance file, not something anyone reads while
# drafting.
CAPTIONS: dict[str, str] = {}
FIGURES_WRITTEN: set[str] = set()


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def tree_is_dirty() -> bool:
    """Whether the working tree was dirty when the figures were generated.

    Recorded because a dirty tree means the figures were built from code that
    the generation commit does not contain -- which is precisely the condition
    that let a stale commit reach this file before.
    """
    try:
        diff = subprocess.check_output(
            ["git", "diff", "HEAD"], cwd=ROOT, text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return False
    return bool(diff.strip())


def _crossover_schema_ok(xover: dict) -> bool:
    """Whether the surface carries the error column this driver reads.

    A cheap structural check rather than a try/except around the whole figure:
    it names the missing column in the skip reason, so a reader is told what to
    regenerate instead of only that something went wrong.
    """
    case = next(iter(xover.get("by_reynolds", {}).values()), None)
    if not case:
        return False
    if "relative_l2_fluct_over_full" not in (case.get("error_columns")
                                            or xover.get("error_columns") or {}):
        return False
    for rows in case.get("static_moving_window", {}).values():
        if rows and "relative_l2_fluct_over_full" not in rows[0]:
            return False
    return True


def make_paper_figures(results, out, paper_dir, used, skipped, colors) -> None:
    """The five figures the paper includes that no code wrote (C11-1).

    Names and content are the draft's: ``fig_tg_ke_rank`` (fig:tg),
    ``fig_rank_vs_time`` (fig:rank), ``fig_sv_decay`` (fig:svd),
    ``fig_error_vs_ref`` (fig:error), ``fig_ke_spectrum`` (fig:kestats).  Each is
    written as both .pdf and .png, and to both output roots.

    Two rules the rest of this script also follows:

    * every number on an axis or in a title is read out of the artifact, so a
      re-run cannot leave a stale claim in the paper's rendering path;
    * a figure whose data is absent is *skipped with a reason*, never drawn from
      whatever else is in the directory -- which is the failure the stale-file
      guard below exists to prevent.
    """
    suite = {
        re: load(results / f"kolmogorov_re{re}_N64.json")
        for re in (100, 1000, 5000)
    }
    suite = {k: v for k, v in suite.items() if v}

    def emit(fig, name, caption) -> None:
        # Mirroring is done once, for every figure the run wrote, after the fact
        # -- doing it per figure here would only ever reach the five new ones, and
        # the blocker was that `fig_cost` existed, was generated, and still did
        # not resolve because the paper looks in a different directory.
        CAPTIONS[name] = caption
        FIGURES_WRITTEN.add(name)

    # --- fig_tg_ke_rank (fig:tg) -------------------------------------------
    tg = load(results / "taylor_green.json")
    if tg and tg.get("energy_history") and tg.get("rank_history"):
        used.append("taylor_green.json")
        dt = tg["parameters"]["dt"]
        steps = np.arange(len(tg["energy_history"]))
        fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.6), layout="constrained")
        ax = axes[0]
        ax.plot(steps * dt, tg["energy_history"], color=colors["full"],
                label="full grid")
        if tg.get("dlra_energy_history"):
            ax.plot(steps * dt, tg["dlra_energy_history"], color=colors["dlra"],
                    linestyle="--", label="reduced (rank 1)")
        # I2 is a *monotonicity* claim, so it is shown as one rather than
        # asserted in prose: the increments are non-positive throughout.
        increments = np.diff(tg["energy_history"])
        ax.set_title(
            r"$E(t)$: monotone non-increasing"
            f"\n({int(np.count_nonzero(increments > 0))} increases in "
            f"{len(increments)} steps)", fontsize=9,
        )
        ax.set_xlabel("time $t$")
        ax.set_ylabel(r"$E$")
        ax.legend(fontsize=7)
        ax = axes[1]
        ranks = np.asarray(tg["rank_history"], dtype=float)
        ax.plot(steps * dt, ranks, color=colors["dlra"], drawstyle="steps-post")
        ax.set_ylim(0, max(2.0, ranks.max() + 0.5))
        ax.set_xlabel("time $t$")
        ax.set_ylabel(r"adaptive rank $r(t)$")
        # The caption says 3 -> 2 -> 1; the run gives a constant.  The figure
        # says what the run gives, and CAPTIONS.md carries the discrepancy.
        distinct = sorted(set(int(r) for r in tg["rank_history"]))
        ax.set_title(
            r"adaptive $r(t)$: constant at " + str(distinct[0]) + "\n"
            "(single Fourier mode: numerical rank 1)", fontsize=9,
        )
        fig.savefig(out / "fig_tg_ke_rank.pdf", bbox_inches="tight")
        fig.savefig(out / "fig_tg_ke_rank.png", bbox_inches="tight")
        plt.close(fig)
        emit(fig, "fig_tg_ke_rank",
             "Taylor--Green laminar decay. Left: kinetic energy of the full grid "
             "and of the reduced state; the increments are non-positive at every "
             "step, which is the monotonicity invariant I2 stated as a property "
             "of the figure rather than of the prose. Right: the adaptive rank, "
             "which is **constant at 1** because the initial condition is a "
             "single Fourier mode, so the numerical rank is 1 and there is "
             "nothing further to request. **The draft's caption says the rank "
             "decays 3 -> 2 -> 1; that is not what this run produces and it "
             "cannot, since a rank-3 start would need a 3-mode initial "
             "condition.**")
    else:
        skipped.append((
            "fig_tg_ke_rank",
            "`taylor_green.json` has no energy/rank history, so E(t) and r(t) "
            "cannot be drawn from it",
        ))

    # --- fig_rank_vs_time (fig:rank) ----------------------------------------
    if suite:
        used += [f"kolmogorov_re{re}_N64.json" for re in suite]
        fig, ax = plt.subplots(figsize=(3.6, 2.7), layout="constrained")
        cmap = plt.get_cmap("viridis")
        final_ranks = {}
        for i, (re, data) in enumerate(sorted(suite.items())):
            history = data["dlra"].get("rank_history")
            if not history:
                continue
            dt = data["parameters"]["dt"]
            t = np.arange(len(history)) * dt
            ax.plot(t, history, color=cmap(i / 2.0), linewidth=1.3,
                    label=f"Re={re}")
            final_ranks[re] = int(history[-1])
        ax.set_xlabel("time $t$")
        ax.set_ylabel(r"adaptive rank $r(t)$")
        ax.set_title(
            # The measured behaviour, not the draft's caption.  There is no
            # spin-up growth phase -- the rank reaches its final value at the
            # FIRST check and stays there -- and r* is the same number at every
            # Reynolds number, so there is no r*(Re) to quote.  The value it
            # takes is the top of the band the grid resolves, which makes it a
            # property of the discretisation rather than of the dynamics.
            r"$r(t)$: one jump at the first check, then flat"
            + (f"\n$r^*$ = {sorted(set(final_ranks.values()))[0]} at every Re "
               f"(the top of the band $N$ resolves)"
               if final_ranks and len(set(final_ranks.values())) == 1
               else "\nfinal: " + ", ".join(
                   f"Re={k}: {v}" for k, v in sorted(final_ranks.items()))),
            fontsize=8.5,
        )
        ax.legend(fontsize=7)
        fig.savefig(out / "fig_rank_vs_time.pdf", bbox_inches="tight")
        fig.savefig(out / "fig_rank_vs_time.png", bbox_inches="tight")
        plt.close(fig)
        emit(fig, "fig_rank_vs_time",
             r"Adaptive rank $r(t)$ for the forced flow at each Reynolds number, "
             r"from the suite runs. **Two things the draft's caption asserts that "
             r"this figure does not show.** There is no spin-up growth phase: the "
             r"rank reaches its final value at the *first* check and is flat "
             r"thereafter. And $r^*(\mathrm{Re})$ does not depend on "
             r"$\mathrm{Re}$ -- it is the same number at all three -- so there is "
             r"no $r^*(\mathrm{Re})$ to quote. The value it takes is the top of "
             r"the band the grid resolves without aliasing, which makes it a "
             r"property of the discretisation rather than of the dynamics; the "
             r"**window** rank, which does measure the dynamics, is a different "
             r"quantity and is 16 at both grids. Read it with the horizon too: "
             r"these runs reach $t=0.1$, and the same rule at $T=8$ still sits at "
             r"the top of the band at every cutoff while the error grows to "
             r"$0.1$--$0.5$.")

    # --- fig_sv_decay (fig:svd) ---------------------------------------------
    if suite:
        fig, axes = plt.subplots(1, len(suite), figsize=(2.3 * len(suite) + 0.4, 2.5),
                                 layout="constrained", squeeze=False)
        slowest = {}
        slope = {}
        for j, (re, data) in enumerate(sorted(suite.items())):
            block = data["dlra"]
            steps_at = block.get("singular_value_steps") or []
            spectra = block.get("singular_values") or []
            ax = axes[0][j]
            if not steps_at or not spectra:
                ax.set_visible(False)
                continue
            dt = data["parameters"]["dt"]
            for i, step in enumerate(steps_at):
                if i >= len(spectra):
                    break
                s = np.asarray(spectra[i], dtype=float)
                if s.size == 0 or s[0] <= 0:
                    continue
                shade = 0.25 + 0.75 * i / max(len(steps_at) - 1, 1)
                ax.semilogy(np.arange(1, s.size + 1), s / s[0],
                            color=colors["dlra"], alpha=shade, linewidth=1.0)
            final = np.asarray(spectra[-1], dtype=float)
            if final.size:
                kept = int(np.count_nonzero(
                    final >= 1e-10 * final[0])) if final[0] > 0 else 0
                slowest[re] = kept
                # The draft's caption says "slower decay at higher Re".  Measured,
                # that is true and small: sigma_20/sigma_1 rises monotonically
                # with Re by about 19% across a 50x range, which is invisible on
                # a log axis spanning fifteen decades.  The number is printed so
                # the claim is quantified instead of asserted, and so a reader
                # can see how weak it is.
                slope[re] = float(final[19] / final[0]) if final.size > 19 else None
            ax.set_xlabel("mode index $r$")
            if j == 0:
                ax.set_ylabel(r"$\sigma_r/\sigma_1$")
            ax.set_title(
                f"Re={re}\n"
                + (f"{slowest.get(re, 0)} modes at $10^{{-10}}$"
                   f"   $\\sigma_{{20}}/\\sigma_1$ = {slope[re]:.2e}"
                   if re in slowest and slope.get(re) is not None
                   else (f"{slowest.get(re, 0)} modes at $10^{{-10}}$"
                         if re in slowest else "")),
                fontsize=8.5,
            )
        fig.suptitle(
            r"Singular-value decay of $\psi$ at increasing times"
            r" (darker = later)", fontsize=9,
        )
        fig.savefig(out / "fig_sv_decay.pdf", bbox_inches="tight")
        fig.savefig(out / "fig_sv_decay.png", bbox_inches="tight")
        plt.close(fig)
        emit(fig, "fig_sv_decay",
             r"Singular-value decay of the full-grid state at every recorded "
             r"time, one panel per Reynolds number, darker for later. Both "
             r"numbers per panel are read from the artifact. **On the draft's "
             r"claim that the decay is slower at higher $\mathrm{Re}$: it is "
             r"true and small.** $\sigma_{20}/\sigma_1$ rises monotonically "
             r"with $\mathrm{Re}$ (1.97e-3, 2.31e-3, 2.34e-3 at Re = 100, 1000, "
             r"5000), which is +19% across a 50-fold range of Reynolds numbers "
             r"and invisible on a log axis spanning the fifteen decades these "
             r"panels cover. The mode count above the $10^{-10}$ cutoff is 43 at "
             r"all three. The two cliffs are the initial condition's numerical "
             r"rank (17) and the top of the band the grid resolves (43).")

    # --- fig_error_vs_ref (fig:error) ---------------------------------------
    if suite:
        fig, ax = plt.subplots(figsize=(3.6, 2.7), layout="constrained")
        cmap = plt.get_cmap("viridis")
        for i, (re, data) in enumerate(sorted(suite.items())):
            for key, colour, style, label in (
                ("dlra", colors["dlra"], "-", "SP-DLRA (adaptive)"),
                ("pod", colors["pod"], "--", "static POD"),
            ):
                rows = (data.get(key) or {}).get("comparison") or []
                if not rows:
                    continue
                ax.plot([r["time"] for r in rows], [r["relative_l2"] for r in rows],
                        style, color=cmap(i / 2.0), linewidth=1.2,
                        label=f"{label}, Re={re}")
        ax.set_yscale("log")
        ax.set_xlabel("time $t$")
        ax.set_ylabel(r"relative $L^2$ against the full grid")
        ax.set_title(
            r"Error against the full-grid reference"
            "\n(over the suite window $t\\leq0.1$ only)", fontsize=9,
        )
        ax.legend(fontsize=5.8, ncol=2)
        fig.savefig(out / "fig_error_vs_ref.pdf", bbox_inches="tight")
        fig.savefig(out / "fig_error_vs_ref.png", bbox_inches="tight")
        plt.close(fig)
        # By how much static POD wins inside this window, computed here rather
        # than written into the caption by hand: a magnitude in prose that is
        # not read off the artifact is a magnitude that rots on the next re-run,
        # and this figure's whole point is that the ordering is counter-intuitive
        # and therefore needs the number attached.
        pod_advantage = {}
        for re, block in sorted(suite.items()):
            dlra_err = block["dlra"].get("max_relative_l2_vs_full")
            pod_err = block["pod"].get("max_relative_l2_vs_full")
            if dlra_err and pod_err and pod_err > 0:
                pod_advantage[re] = dlra_err / pod_err

        emit(fig, "fig_error_vs_ref",
             r"**The three SP-DLRA curves coincide**, so two of them are hidden "
             r"behind the third: over this window the reduced method's error is "
             r"the same at all three Reynolds numbers, and the legend's six "
             r"entries are three distinct curves rather than six. "
             r"Relative $L^2$ against the full-grid spectral reference, the "
             r"adaptive method against the static POD baseline at each Reynolds "
             r"number. **The window is $t\leq0.1$ and the figure says so, because "
             r"inside it the static baseline is the more accurate method: its "
             r"offline fitting window is a prefix of the evaluated trajectory. "
             r"The ordering reverses at longer horizons, and the crossover is "
             r"measured separately.** The size of the gap inside the window is "
             r"not small and should not be read off the log axis without it: by "
             r"max relative $L^2$, static POD beats SP-DLRA by "
             + (
                 ", ".join(
                     f"{r:.0f}$\\times$ at Re={k}"
                     for k, r in sorted(pod_advantage.items())
                 )
                 if pod_advantage
                 else "(see the artifact; POD is the more accurate method at "
                      "every Re measured)"
             )
             + r", because a basis fitted offline on a prefix of the evaluated "
             r"trajectory is a very good representation of a short, smooth "
             r"window. **The two methods' Reynolds-sensitivities differ by two "
             r"orders of magnitude** -- SP-DLRA's error is flat in Re to within a "
             r"factor of 1.03, static POD's moves by a factor of 105 -- so a "
             r"single $\\mathrm{Re}$ axis spanning both shows one method's "
             r"sensitivity and hides the other's.")

    # --- fig_ke_spectrum (fig:kestats) --------------------------------------
    pilot = None
    for name in ("regime_pilot_re5000_A0p2.json", "regime_pilot_re5000_N128_A0p2.json"):
        candidate = load(results / name)
        if candidate and candidate.get("windowed_spectra"):
            pilot = (name, candidate)
            break
    if pilot is None:
        skipped.append((
            "fig_ke_spectrum",
            "no regime pilot carries time-averaged fluctuation spectra",
        ))
    else:
        name, data = pilot
        used.append(name)
        entry = next(iter(data["windowed_spectra"].values()))
        k = np.asarray(entry["k"], dtype=float)
        e = np.asarray(entry["E_fluct"], dtype=float)
        w0, w1 = entry["window_start"], entry["window_end"]
        fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.6), layout="constrained")
        ax = axes[0]
        # The draft's caption for this figure promises "SP-DLRA against the
        # full-grid reference".  Plotting one E(t) per Reynolds number -- which is
        # what this panel did -- cannot deliver that: there is no second curve to
        # compare against.  So plot the comparison itself, one Re per colour, the
        # full grid solid and SP-DLRA dashed on top of it.
        #
        # The answer is that they coincide, and that is a result rather than a
        # defect -- but "coincide" is not a caption, so the maximum relative
        # difference is annotated per Re.  It is also the reason static POD looks
        # no worse here: on the *total* energy all three methods agree to ~1e-7,
        # and the methods separate on the fluctuation field (fig:error), not here.
        max_rel: dict[int, float] = {}
        # Colour encodes the Reynolds number and the line style encodes the
        # method.  The first attempt did it the other way round -- one colour for
        # "the full grid" at every Re -- so the three Re were indistinguishable and
        # only the two line styles separated, which defeats the point of a
        # per-Re panel.
        re_list = sorted(suite)
        palette = ["#264653", "#0072B2", "#E76F51"]
        colour = dict(zip(re_list, palette))
        for re, block in sorted(suite.items()):
            ref = block["full"].get("energy_history") or []
            dlra = block["dlra"].get("energy_history") or []
            if not ref or len(ref) != len(dlra):
                continue
            dt = block["parameters"]["dt"]
            t = np.arange(len(ref)) * dt
            ax.plot(t, ref, color=colour[re], linewidth=1.5,
                    label=f"Re={re}")
            rel = np.abs(np.asarray(dlra) - np.asarray(ref)) / np.asarray(ref)
            max_rel[re] = float(rel.max())
            ax.plot(t, dlra, color=colour[re], linewidth=1.1, linestyle="--")
        ax.set_xlabel("time $t$")
        ax.set_ylabel(r"$E$")
        ax.set_title(
            r"$E(t)$, SP-DLRA against the full grid" "\n"
            r"(curves coincide; $\max|\Delta E|/E$ below)", fontsize=9,
        )
        # One box, not one annotation per curve: three annotations at the curve
        # ends overlapped each other and the legend, which is worse than no
        # annotation at all.
        if max_rel:
            ax.text(
                0.02, 0.03,
                r"$\max_t|\Delta E|/E$:" + "\n" + "\n".join(
                    rf"  Re={re}: {rel:.1e}" for re, rel in sorted(max_rel.items())
                ),
                transform=ax.transAxes, fontsize=6, va="bottom", ha="left",
                bbox={"facecolor": "white", "edgecolor": "0.8", "pad": 2},
            )
        # Below the axes, and one entry per Reynolds number rather than two: the
        # six-entry version put the legend on top of the Re=1000 and Re=5000
        # curves, and duplicated every Re just to restate the line style.
        ax.legend(
            fontsize=6, ncol=3, loc="upper center", frameon=False,
            bbox_to_anchor=(0.5, -0.28),
            title="solid: full grid    dashed: SP-DLRA", title_fontsize=6,
        )
        ax = axes[1]
        ref = block["full"].get("energy_history") or []
        total = ref[-1] if ref else None
        # Labelled "full grid" on purpose.  The draft's caption promises this
        # panel is a method comparison, and it cannot be: the pilot is the only
        # artifact carrying a time-averaged spectrum and it carries ONE, from the
        # full-grid arm.  The suite runs with --spectrum-count unset and so carry
        # no spectrum at all, which is why a per-method version would have to be a
        # new run rather than a redraw.  Saying whose it is beats implying it is
        # a comparison.
        ax.semilogy(k, e, color=colors["full"], linewidth=1.2,
                    label=rf"full grid, time-averaged $\psi'$")
        if total:
            ax.axvline(k.max(), color=colors["ref"], linestyle=":", linewidth=1.0)
            ax.annotate("dealiased range", (k.max(), e.max()), fontsize=6,
                        color=colors["ref"], ha="right", va="top")
        ax.set_xlabel("wavenumber $k$")
        ax.set_ylabel(r"$E_{\mathrm{fluct}}(k)$")
        ax.set_title(
            rf"$\psi'$ spectrum, full grid only, $t\in[{w0:.4g},{w1:.4g}]$"
            "\n$Z(k)$ omitted: enstrophy drifts, so it would\n"
            "average a moving quantity", fontsize=8,
        )
        ax.legend(fontsize=6.5)
        fig.savefig(out / "fig_ke_spectrum.pdf", bbox_inches="tight")
        fig.savefig(out / "fig_ke_spectrum.png", bbox_inches="tight")
        plt.close(fig)
        emit(fig, "fig_ke_spectrum",
             r"Kinetic-energy statistics. Left: $E(t)$, **SP-DLRA against the "
             r"full-grid reference at each Reynolds number** -- the comparison the "
             r"draft's caption promised, which the previous version of this panel "
             r"could not deliver because it plotted one curve per Re and so had "
             r"nothing to compare against. The answer is that they coincide, and "
             r"the figure annotates the gap rather than asserting it: the maximum "
             r"relative difference is "
             + ", ".join(
                 f"{rel:.1e} at Re={re}"
                 for re, rel in sorted(max_rel.items())
             )
             + ". **So the total energy does not discriminate between the methods "
             r"here** -- static POD is within 1.1e-07 of the full grid on this "
             r"quantity too, which is why the methods separate on the *fluctuation* "
             r"field in fig:error and not on the total. Right: the time-averaged "
             r"fluctuation spectrum against wavenumber, over the window named in "
             r"the title. **This panel is the full grid only, and cannot be a "
             r"method comparison: the regime pilot is the only artifact carrying a "
             r"time-averaged spectrum and it carries one, from the full-grid arm. "
             r"The suite runs with `--spectrum-count` unset and so carries no "
             r"spectrum at all, so a per-method version is a new run rather than a "
             r"redraw.** The $Z(k)$ half of the enstrophy spectrum is omitted and "
             r"the reason is on the figure: the fluctuation enstrophy drifts across "
             r"this averaging window, outside the 10% stationary bar, so a "
             r"time-averaged $Z(k)$ would be averaging a moving quantity.")


def provenance(
    results: Path, out: Path, names: list[str], skipped: list[tuple[str, str]]
) -> None:
    """Write PROVENANCE.md from the artifacts this run actually loaded.

    This used to be a hand-maintained parallel list, and it drifted in three
    independent ways: an artifact was attributed to a commit it did not record,
    the "figures generated at commit" line lagged the generation, and a commit
    that D55c had proved did not produce an artifact was still quoted -- in a
    human-facing document.  The fix is structural rather than careful: there is
    no second copy to keep correct, because the only inputs are the artifacts
    just read and ``HEAD`` at the moment of generation.

    Each artifact's *own* provenance block is emitted verbatim, including
    ``reproducible``, so the file cannot assert a commit the artifact
    contradicts.
    """
    lines = [
        "# Figure provenance",
        "",
        "Generated by `experiments/make_figures.py` from the artifacts it loaded "
        "in this run. Every entry below is that artifact's own `provenance` "
        "block, so this file cannot disagree with the data it describes.",
        "",
        "## Source artifacts",
        "",
    ]
    for name in names:
        path = results / name
        if not path.exists():
            continue
        prov = json.loads(path.read_text()).get("provenance", {})
        commit = str(prov.get("git_commit", "?"))[:12]
        bits = [f"commit `{commit}`"]
        if "reproducible" in prov:
            bits.append(
                f"driver matches that commit: **{prov['reproducible']}**"
            )
        if prov.get("working_tree_dirty"):
            bits.append("tree was dirty at generation")
        if prov.get("driver"):
            bits.append(f"driver `{prov['driver']}`")
        lines.append(f"- `{name}` -- " + "; ".join(bits))
    if skipped:
        lines += ["", "## Expected but not generated", ""]
        for figure, reason in skipped:
            lines.append(f"- **{figure}** -- {reason}")
    lines += [
        "",
        f"Figures generated at commit `{git_commit()[:12]}`, "
        f"on a {'clean' if not tree_is_dirty() else 'dirty'} working tree.",
        "",
    ]
    (out / "PROVENANCE.md").write_text("\n".join(lines) + "\n")

    # CAPTIONS.md: liftable caption text, generated from the same run.  A figure
    # that dropped a panel for a stated reason has to be able to hand that reason
    # to whoever writes the caption, or the omission looks like an oversight.
    cap_lines = [
        "# Figure captions",
        "",
        "Generated by `experiments/make_figures.py` at the same time as the figures "
        "themselves, so a caption cannot describe a panel the current run did not "
        "draw. Liftable text, not final wording.",
        "",
    ]
    for name in sorted(CAPTIONS):
        cap_lines += [f"## `{name}`", "", CAPTIONS[name], ""]
    if skipped:
        cap_lines += ["## Panels deliberately omitted", ""]
        for figure, reason in skipped:
            cap_lines += [f"- **{figure}** -- {reason}", ""]
    (out / "CAPTIONS.md").write_text("\n".join(cap_lines) + "\n")

    # Delete any figure file this run did not write.  A figure block that is
    # skipped -- because its artifact is missing -- used to leave the *previous*
    # run's file on disk with nothing to say so, and a stale PNG is worse than an
    # absent one: it looks current, renders fine, and carries whatever claim the
    # code used to make.  That is not hypothetical.  It is how a withdrawn title
    # stayed in a rendered image after it was gone from the source, and how I
    # reviewed a figure whose bytes had not changed.
    expected = {f"{name}{ext}" for name in FIGURES_WRITTEN
                for ext in (".png", ".pdf")}
    stale = sorted(
        path.name for path in out.glob("fig_*")
        if path.suffix in {".png", ".pdf"} and path.name not in expected
    )
    for path in sorted(out.glob("fig_*")):
        if path.suffix in {".png", ".pdf"} and path.name not in expected:
            path.unlink()
    if stale:
        print(
            f"removed {len(stale)} stale figure file(s) this run did not write: "
            + ", ".join(stale)
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results", type=Path, default=ROOT / "state" / "coder" / "results"
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "experiments" / "figures"
    )
    parser.add_argument(
        # C11-1: the draft's `\includegraphics{figures/...}` resolves against the
        # paper's own directory, which was empty on every branch -- so even
        # `fig_cost`, which existed and was generated, did not resolve.  The
        # paper's figures are GENERATED here and copied there; no prose and no
        # .tex is written into the writer's tree.  `--paper-figures-dir ''`
        # disables it.
        "--paper-figures-dir", type=Path, default=ROOT / "paper" / "figures",
        help="second output root for the figures the paper includes; pass an "
             "empty string to write only to --output-dir",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if not str(args.paper_figures_dir or "").strip():
        args.paper_figures_dir = None
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
        CAPTIONS["fig_window_rank"] = (
            r"Two different rank quantities against window length. Left: the modes "
            r"needed to represent a whole window of the trajectory, which grows and "
            r"is grid-independent. Right: what the per-step amplitude rule requests, "
            r"which tracks the grid and saturates at the top of the band the grid "
            r"resolves without aliasing, $2\lfloor N/3\rfloor+1$ modes. Conflating "
            r"these is what made adaptive rank "
            r"look like a grid artifact."
        )
        FIGURES_WRITTEN.add("fig_window_rank")
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
        CAPTIONS["fig_spectrum"] = (
            'Singular-value spectrum of the **full-grid** state, at $t=0$ and at the end of the run, for every resolved mode. The initial condition is exactly rank 17; the developed state is not low rank at all, which is the regime the reduced methods are being asked to approximate.'
        )
        FIGURES_WRITTEN.add("fig_spectrum")
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
        # The window this figure covers, and what it therefore cannot show, has
        # to be on the figure.  The suite runs to t = 0.1 while the crossover --
        # the measurement the paper's argument actually turns on -- sits at
        # t* ~ 0.65 and 1.48.  Inside t <= 0.1 the static baseline's offline
        # window is a *prefix* of the evaluated trajectory and its divergence
        # stays near zero while the DLRA's rises, so an unlabelled reader sees the
        # static baseline winning: the opposite of the paper's conclusion, with
        # nothing on the figure to say the window is the reason.
        window = max(
            (r["parameters"].get("final_time")
             or r["parameters"]["dt"] * (len(r["full"]["energy_history"]) - 1))
            for r in suite.values()
        )
        t_star = None
        crossover = load(R / "crossover_surface.json")
        if crossover:
            # From the ROWS, never from the artifact's `crossovers` block (D22.5,
            # D23): measured on the committed surface that block sits 7-16% below
            # every rows-based value, and quoting it here would put an unverifiable
            # number into a figure label.  Both the brackets and the point
            # estimates are reported, because the bracket is the convention-free
            # statement and the point estimate is not.
            brackets, points = [], []
            for case in crossover["by_reynolds"].values():
                windows = crossover["parameters"].get("moving_window_lengths") or [0.25]
                for rank in crossover["parameters"]["ranks"]:
                    rows_dlra = case["dlra"].get(str(rank))
                    rows_static = case["static_moving_window"].get(
                        f"W{windows[0]:g}_r{rank}"
                    )
                    if not rows_dlra or not rows_static:
                        continue
                    got = t_star_from_rows(
                        rows_dlra, rows_static, "relative_l2", log_interp=True
                    )
                    if got["t_star"] is not None:
                        brackets.append(tuple(got["bracket"]))
                        points.append(got["t_star"])
            if points:
                t_star = (min(points), max(points), brackets)
        caveat = (
            f"window $t\\leq{window:g}$ only"
            + (f"; the crossover is bracketed in $t\\in"
               f"[{min(b[0] for b in t_star[2]):g},{max(b[1] for b in t_star[2]):g}]$"
               if t_star else "")
        )
        ax.set_xlabel("time")
        ax.set_ylabel(r"relative $L^2$")
        ax.set_title("Trajectory divergence over the suite window,\n" + caveat,
                     fontsize=9)
        ax.legend(fontsize=6.5, ncol=2)
        ax = axes[1]
        # Two series, and the second one was previously missing.  The paper's
        # statistics are on psi' = psi - x-average(psi) (D11/S1).  The comment
        # that used to sit here had this backwards: it said the fluctuation was
        # "only 32%" of the total, which is the N=32 figure, on a panel built
        # from N=64, where the fluctuation is **83.8%** of the initial energy
        # (18.6076 of 22.2067) and the zonal mean 16.2% rising to 18.4% at
        # t=0.1.  So the total is fluctuation-DOMINATED here, and the reason to
        # plot the split is not that the total hides the fluctuation -- it is
        # that the two curves are then nearly the same curve, so a reader cannot
        # see the zonal part at all, and a claim about the zonal mean has to be
        # visible to be checked.
        plotted = False
        for re, result in suite.items():
            dt = result["parameters"]["dt"]
            block = result["full"]
            total = np.asarray(block["energy_history"], dtype=float)
            fluct = np.asarray(
                block.get("fluctuation_energy_history") or [], dtype=float
            )
            if fluct.size != total.size:
                continue
            t = np.arange(total.size) * dt
            alpha = 0.9 if re == 5000 else 0.4
            ax.plot(t, total - fluct, color=colors["full"], alpha=alpha,
                    label=f"zonal mean Re={re}")
            ax.plot(t, fluct, color=colors["dlra"], alpha=alpha,
                    label=r"fluctuation $\psi'$ Re=" + str(re))
            plotted = True
        if not plotted:
            for re, result in suite.items():
                t = (np.arange(len(result["full"]["energy_history"]))
                     * result["parameters"]["dt"])
                ax.plot(t, result["full"]["energy_history"],
                        color=colors["full"],
                        alpha=0.9 if re == 5000 else 0.4,
                        label=f"total KE Re={re} "
                              r"($\psi'$ series not recorded)")
        ax.set_xlabel("time")
        ax.set_ylabel(r"$E$")
        ax.set_title(
            r"KE split: fluctuation $\psi'$ (the reported statistic)"
            "\nand zonal mean, which carries no method difference",
            fontsize=9,
        )
        ax.legend(fontsize=6.5)
        fig.tight_layout()
        CAPTIONS["fig_divergence"] = (
            rf"**Left: relative $L^2$ against the full grid, over the suite window "
            rf"$t\leq{window:g}$ only.** Once two trajectories decorrelate this "
            rf"measures phase, not accuracy. **This window does not show the "
            rf"paper's conclusion and must not be read as if it did**: inside "
            rf"$t\leq{window:g}$ the static baseline's offline fitting window is a "
            rf"*prefix* of the evaluated trajectory, so it is the more accurate "
            rf"method here"
            + (rf", and the ordering reverses at the crossover, bracketed in "
               rf"$t\in[{min(b[0] for b in t_star[2]):g},"
               rf"{max(b[1] for b in t_star[2]):g}]$ from the rows (point "
               rf"estimates {t_star[0]:.2f}-{t_star[1]:.2f} on "
               rf"$t^*=\\mathrm{{static}}/\\mathrm{{DLRA}}$ with log "
               rf"interpolation, Fig. \\ref{{fig:crossover}})"
               if t_star else ", and the ordering reverses only at longer "
               "horizons")
            + rf". Right: kinetic energy split as the fluctuation "
            rf"$\psi'=\psi-\overline{{\psi}}_x$ and the zonal mean; the "
            rf"fluctuation is the series the paper's statistics are computed on, "
            rf"and it is the one that carries the method-to-method difference."
        )
        FIGURES_WRITTEN.add("fig_divergence")
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
        # Diverged runs are kept *out* of the stable panel and given their own.
        # Plotting them on the same linear axis is not a cosmetic problem: the
        # worst is 7.1e+278 against stable values of ~1e-14, so the axis must span
        # 292 decades and every finite bar becomes about 1e-290 of the width --
        # a figure that renders cleanly and shows nothing.  The guard below makes
        # that failure loud instead of silent.
        diverged = [
            (n.replace("_", " "), m) for n, m in baselines["methods"].items()
            if m.get("diverged")
        ]
        # One list for the stable panel: the suite rows and the finite baseline
        # rows are different namespaces, and indexing one by a label from the
        # other is how a label silently goes missing.
        stable = [(r[0], float(r[1]), None) for r in rows if r[1] < 1e6 * 1e-14]
        stable += [
            (n.replace("_", " "), float(m["max_abs_divergence"]), m)
            for n, m in baselines["methods"].items() if not m.get("diverged")
        ]
        n_panels = 2 if diverged else 1
        fig, axes = plt.subplots(
            n_panels, 1, figsize=(6.9, 0.24 * len(stable) + 1.6),
            squeeze=False,
        )
        ax = axes[0][0]
        names = [s[0] for s in stable]
        values = [s[1] / 1e-14 for s in stable]
        # A guard, not a hope: if anything here were large enough to compress the
        # rest, the figure says so instead of drawing an unreadable one.
        largest = max(values) if values else 0.0
        if largest > 1e4:
            raise SystemExit(
                f"fig_div_free: a value of {largest:.3e} (in units of 1e-14) "
                f"would compress every other bar below 1e-4 of the axis. Plot it "
                f"in its own panel; see the diverged-run panel for the pattern."
            )
        # A log axis, against the reviewer's suggestion of linear, and the
        # deviation is deliberate: one finite method sits at 1046x the target, so
        # a linear axis would render the other fifteen as sub-pixel slivers --
        # reproducing exactly the defect this figure is being split to fix.  Over
        # the three decades the finite methods actually span, a log axis shows
        # every one of them and keeps the target line meaningful.
        ax.barh(names, values, color=colors["full"])
        ax.set_xscale("log")
        finite_max = max(values) if values else 1.0
        ax.set_xlim(0.5, finite_max * 4.0)
        for i, (label, value, m) in enumerate(stable):
            v = value / 1e-14
            # The one method that degraded a thousandfold without diverging is
            # named, because it is the only finite bar far from the others and
            # an unexplained outlier is the thing a reader should notice.  The
            # label goes to the right of its own bar so it cannot collide with
            # the axis labels.
            if v > 100.0:
                ax.annotate(f"{v:.0f}$\\times$ the floor, finite",
                            (v, i), textcoords="offset points", xytext=(4, 0),
                            ha="left", va="center", fontsize=6.2,
                            color=colors["dlra"])
        ax.axvline(1.0, color=colors["dlra"], linestyle="--", linewidth=1.0)
        # Not a "target": every surviving method sits one to two orders *above*
        # 1e-14, which is the roundoff floor for an 8-unit rollout at N=64 rather
        # than a level the methods meet.  Labelling it a target would have every
        # bar on the wrong side of the line.
        ax.annotate("$10^{-14}$ roundoff floor\n(N=64, T=8)", (1.0, -1.4),
                    textcoords="offset points", xytext=(4, 0), fontsize=6.4,
                    color=colors["dlra"], va="top")
        ax.set_xlabel(
            r"max $|\nabla\!\cdot u|$ over the run, in units of $10^{-14}$ "
            r"(log; survivors sit 2–20x the floor, one is $10^3\times$)"
        )
        ax.set_title(
            "Exact divergence-freeness for every method that survives —\n"
            "and four fixed-subspace methods that do not",
            fontsize=9.5,
        )
        # No explicit left limit: this is a log axis, and `set_xlim(left=0.0)` on
        # one is not a no-op warning -- matplotlib refuses it and the axis keeps
        # whatever lower bound the data implies. Which is what we want, but the
        # call was doing nothing except emitting a warning on every figure run.
        ax.invert_yaxis()
        if diverged:
            ax2 = axes[1][0]
            # No shared axis: these four failed at four different times, with four
            # different magnitudes, and a common scale would say nothing.
            dnames = [d[0] for d in diverged]
            dvals = [float(d[1]["max_abs_divergence"]) for d in diverged]
            # Barred as log10 on a *linear* axis.  A log axis here would have to
            # place ticks across 214 decades, and matplotlib's decade locator
            # overflows on that; barring the exponent says the same thing and
            # cannot.
            dexps = [np.log10(v) if v > 0 else 0.0 for v in dvals]
            ax2.barh(dnames, dexps, color=colors["dlra"])
            for i, ((label, m), v, e) in enumerate(zip(diverged, dvals, dexps)):
                ax2.annotate(
                    f"diverged at $t={m['diverged_at_time']:.2f}$",
                    (e, i), textcoords="offset points", xytext=(4, 0),
                    ha="left", va="center", fontsize=6.4, color=colors["full"],
                )
            ax2.set_xlabel(
                r"$\log_{10}$ of max $|\nabla\!\cdot u|$ before the run "
                r"went non-finite"
            )
            ax2.set_title(
                "The four fixed-subspace runs that overflowed "
                "(one parameter set)", fontsize=8.5,
            )
            ax2.invert_yaxis()
        fig.tight_layout()
        CAPTIONS["fig_div_free"] = (
            r"Maximum $|\nabla\!\cdot u|$ over each run. Every method that survives "
            r"stays within two orders of the $10^{-14}$ roundoff floor for this grid "
            r"and horizon, with one named exception annotated; the four "
            r"fixed-subspace runs that overflowed are shown separately with their "
            r"divergence times, because their final recorded value is meaningless."
        )
        FIGURES_WRITTEN.add("fig_div_free")
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
        CAPTIONS["fig_cost"] = (
            "Cost against the full-grid spectral reference: full-step time, "
            "median of "
            f"{grids[0]['repeats']} repeats over {grids[0]['steps_per_repeat']} "
            "steps under one interleaved protocol, with the thread settings "
            "named above the panel. **These ratios are only good to about 15%, "
            "and the figure should be read as a range rather than a value.** "
            "Five committed versions of this same configuration give an N=128 "
            "ratio spanning 2.14-2.74 at ONE thread (28%), against a within-run "
            "spread over "
            f"{grids[0]['repeats']} interleaved repeats of 0.17-0.35 (7-10%), "
            "and the thread count alone moves the N=128 ratio by 43% (2.57 at "
            "one thread, 3.54 at two). The interleaving is what makes the ratio "
            "usable on a shared node -- it cannot control for machine state "
            "between runs, and the thread count has to be stated beside any cost "
            "number. **Three things this figure does NOT contain, which the "
            "draft's caption currently claims it does.** (1) *Peak memory* is in "
            "a different artifact from a different driver (`peak_memory.json`, "
            "`bench_memory.py`), measured for the full-grid, projected and BUG "
            "integrators at N=64 and N=128 only. (2) *The static POD baseline has "
            "no cost row here at all*: this driver times `full_grid_reference` "
            "and `projected_dlra`, and POD's memory was never measured, so the "
            "third method in the caption's list does not appear in this figure. "
            "(3) *It is not per Reynolds number* -- this protocol varies N, and "
            "Re is not one of its parameters. Per-Re wall times do exist in the "
            "suite artifacts, but they are single un-interleaved runs and are "
            "**not comparable with these**: the suite's dlra/full ratio is 33.6x "
            "at Re=100, 5.03x at Re=1000 and 1.90x at Re=5000, against 2.2-3.6x "
            "here. Quoting the two families side by side would be comparing "
            "measurement protocols, not methods."
        )
        FIGURES_WRITTEN.add("fig_cost")
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
        # The caption carries the omission reason, not only PROVENANCE.md: a
        # panel dropped for a stated reason is the right call, but the reason has
        # to be visible to whoever writes the caption or they will not state it.
        CAPTIONS["fig_spectra_ek"] = (
            r"Time-averaged fluctuation spectra over the window "
            f"$t\\in[{w0:.4g},{w1:.4g}]$, for the full-grid state. "
            + (
                f"The $Z(k)$ panel is **omitted**: the fluctuation enstrophy drifts "
                f"{100*d_z:.0f}% across this window, outside the 10% S2 bar, so a "
                f"time-averaged $Z(k)$ would be averaging a moving quantity rather "
                f"than a stationary one."
                if not z_defensible and d_z is not None else
                "The $Z(k)$ panel is omitted because the fluctuation enstrophy is not "
                "measurable as a stationary mean over this window."
                if not z_defensible else
                f"$E(k)$ and $Z(k)$ are both shown; the enstrophy drift over the "
                f"averaging window is {100*d_z:.0f}%."
            )
        )
        FIGURES_WRITTEN.add("fig_spectra_ek")
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

    # ---------------------------------------------------------------- figure 7
    # The BUG port's cost, on the same protocol, beside the projected one.  It is
    # the port's whole motivation, so it belongs in the same figure rather than
    # in prose: the port removes every full-size factorization and is still
    # slower, because the K/L/S right-hand sides are full-grid field evaluations.
    bug_cost = load(R / "cost_bug_port.json")
    if bug_cost is None:
        skipped.append((
            "fig_bug_cost",
            "`cost_bug_port.json` is absent, so the BUG port's cost against the "
            "projected integrator is unmeasured",
        ))
    else:
        used.append("cost_bug_port.json")
        # Grouped bars, one group per (N, rank).  A line per point would give
        # every (N, rank) pair its own legend entry and read as four methods.
        groups, proj_vals, bug_vals = [], [], []
        for g in bug_cost["grids"]:
            for r in sorted(g["rows"], key=lambda r: r["rank"]):
                if "bug" not in r:
                    continue
                groups.append(f"N={g['N']}\nr={r['rank']}")
                proj_vals.append(r["full_step_ratio_vs_reference"])
                bug_vals.append(r["bug"]["full_step_ratio_vs_reference"])
        if groups:
            x = np.arange(len(groups), dtype=float)
            width = 0.36
            ratios = [bv / pv for pv, bv in zip(proj_vals, bug_vals)]
            fig, ax = plt.subplots(figsize=(1.45 * len(groups) + 1.3, 3.0))
            ax.bar(x - width / 2, proj_vals, width, color=colors["full"],
                   label="projected (full-field SVD)")
            ax.bar(x + width / 2, bug_vals, width, color=colors["dlra"],
                   label="midpoint BUG (no full-field SVD)")
            for xi, pv, bv, ratio in zip(x, proj_vals, bug_vals, ratios):
                ax.annotate(f"{ratio:.1f}x", (xi + width / 2, bv),
                            textcoords="offset points", xytext=(0, 2),
                            ha="center", fontsize=6.5, color=colors["dlra"])
            ax.axhline(1.0, color=colors["ref"], linestyle=":", linewidth=1.0)
            ax.annotate("full grid", (-0.45, 1.0), textcoords="offset points",
                        xytext=(0, 2), fontsize=7, color=colors["ref"])
            ax.set_yscale("log", base=2)
            ax.set_xticks(x)
            ax.set_xticklabels(groups, fontsize=7)
            ax.set_ylabel("full-step time / full grid")
            # The factor is computed from the bars above, not typed in, and the
            # denominator is named because there are two and they differ by
            # roughly a factor of two: BUG is ~2x the full grid but ~3.4-5.1x the
            # *projected integrator*, whose linear-algebra share is small.  A
            # reader who does not know which is which cannot use the number.
            ax.set_title(
                "BUG removes every full-size factorization\n"
                f"and is still {min(ratios):.1f}-{max(ratios):.1f}x slower than "
                f"the projected\nintegrator "
                f"({min(bug_vals):.2f}-{max(bug_vals):.2f}x the full grid)",
                fontsize=9,
            )
            ax.legend(fontsize=7, loc="upper left")
            fig.tight_layout()
            CAPTIONS["fig_bug_cost"] = (
                r"Full-step time against the full grid, under one interleaved timing "
                "protocol, on the unforced multi-mode decay. The projected integrator "
                "pays a whole-field SVD that is Theta(N^3) and rank-independent; the "
                "midpoint BUG port removes every full-size factorization and is still "
                "slower, because its K/L/S right-hand sides are full-grid field "
                "evaluations."
            )
            FIGURES_WRITTEN.add("fig_bug_cost")
            fig.savefig(args.output_dir / "fig_bug_cost.pdf", bbox_inches="tight")
            fig.savefig(args.output_dir / "fig_bug_cost.png", bbox_inches="tight")
            plt.close(fig)

    # ---------------------------------------------------------------- figure 8
    # The crossover surface.  Two panels, because the *crossing* is the result:
    # the DLRA's error falls with rank while the static baseline's barely moves,
    # so where they cross is set by rank alone.  A surface without the crossing
    # marked would be a table.
    xover = load(R / "crossover_surface.json")
    if xover is None:
        skipped.append((
            "fig_crossover",
            "`crossover_surface.json` is absent, so the advantage horizon is "
            "unmeasured",
        ))
    elif "by_reynolds" not in xover:
        skipped.append((
            "fig_crossover",
            "`crossover_surface.json` predates the `by_reynolds` layout, so it "
            "cannot be read by this driver; regenerate it with run_crossover.py",
        ))
    elif not _crossover_schema_ok(xover):
        # A renamed column is a *skip*, not a crash.  The alternative -- letting
        # a KeyError abort the run -- makes one stale central artifact the
        # hostage of every other figure, which is how a paper ends up unable to
        # build because of a figure it does not even include.  The reason names
        # the column and says what to do.
        skipped.append((
            "fig_crossover",
            "`crossover_surface.json` predates the error-column rename "
            "(`relative_l2_fluct_over_full`); regenerate it with run_crossover.py. "
            "Every other figure is unaffected, which is why this is a skip rather "
            "than a failure.",
        ))
        xover = None
    else:
        by_re = xover["by_reynolds"]
        used.append("crossover_surface.json")
        primary = list(by_re)[0]
        case = by_re[primary]
        ranks = sorted(int(r) for r in case["dlra"])
        windows = xover["parameters"].get("moving_window_lengths") or [1.0]
        # constrained layout, and a taller box: the left title runs to three
        # lines and the right y-label to two, and tight_layout alone let the
        # title overwrite the neighbour's axis label -- an unreadable figure
        # that rendered without complaint.  constrained_layout reserves the
        # space instead of trying to fit it afterwards.
        fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.4),
                                 layout="constrained")
        ax = axes[0]
        cmap = plt.get_cmap("viridis")
        all_errors = [
            row["relative_l2"]
            for r in ranks
            for row in case["dlra"][str(r)] if row["time"] > 0
        ]
        scale = max(all_errors) if all_errors else 1.0
        # "Exact" is judged against the scale of the other curves, not against
        # an absolute constant: the ceiling rank's error is ~1e-8 while the
        # others are O(0.1), so a fixed 1e-10 cut would call it inexact and put it
        # back on the log axis.
        exact = [
            r for r in ranks
            if max(row["relative_l2"] for row in case["dlra"][str(r)]
                   if row["time"] > 0) < 1e-6 * scale
        ]
        plotted = [r for r in ranks if r not in exact]
        for i, rank in enumerate(ranks):
            if rank in exact:
                continue
            shade = cmap(i / max(len(ranks) - 1, 1))
            dl = [r for r in case["dlra"][str(rank)] if r["time"] > 0]
            st = case["static_moving_window"].get(f"W{windows[0]:g}_r{rank}")
            if st is None:
                continue
            ax.plot([r["time"] for r in dl], [r["relative_l2"] for r in dl],
                    color=shade, linewidth=1.3)
            ax.plot([r["time"] for r in st],
                    [r["relative_l2_fluct_over_full"] for r in st],
                    color=shade, linewidth=1.3, linestyle="--")
        ax.plot([], [], color=colors["full"], linewidth=1.3,
                label="DLRA, fixed rank (solid)")
        ax.plot([], [], color=colors["full"], linewidth=1.3, linestyle="--",
                label=f"static, trailing window $W={windows[0]:g}$ (dashed)")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ys = [
            row["relative_l2"]
            for rank in plotted
            for row in case["dlra"][str(rank)] if row["time"] > 0
        ]
        ys += [
            row["relative_l2_fluct_over_full"]
            for rank in plotted
            for row in case["static_moving_window"][f"W{windows[0]:g}_r{rank}"]
        ]
        if ys:
            ax.set_ylim(min(ys) / 2.0, max(ys) * 2.0)
        title = "Error against horizon, by rank"
        if exact:
            # The margin is measured, not asserted.  For each off-axis rank, the
            # decades between its worst error and the *lowest* static baseline
            # anywhere on the panel; the range over those ranks is what the title
            # reports.  A literal here would be a number no re-run could correct.
            static_floor = min(
                (row["relative_l2_fluct_over_full"]
                 for rank in plotted
                 for row in case["static_moving_window"][f"W{windows[0]:g}_r{rank}"]
                 if row["relative_l2_fluct_over_full"] > 0.0),
                default=None,
            )
            decades = sorted(
                (np.log10(static_floor)
                 - np.log10(max(row["relative_l2"] for row in case["dlra"][str(r)]
                                if row["time"] > 0))
                 for r in exact)
                if static_floor else []
            )
            # "below *every* static baseline" is bounded by the *closest* one, so
            # the reference is the minimum over the static curves, not the mean.
            # With a single off-axis rank the span is one number, and printing it
            # as "7-7" would read as a range that does not exist.
            span = (f"{decades[0]:.0f}" if len(decades) == 1
                    else f"{decades[0]:.0f}-{decades[-1]:.0f}" if decades
                    else "several")
            plural = "order" if span in ("1", "several") else "orders"
            title += (
                f"\n$r={'$, $r='.join(str(r) for r in exact)}$ (the largest rank"
                f" tested) stays {span} {plural}\nof magnitude below the closest"
                f" static baseline,\nand is off this log axis"
            )
        ax.set_xlabel("time $t$")
        ax.set_ylabel("relative $L^2$ against the full grid")
        ax.set_title(title, fontsize=8.5)
        ax.legend(fontsize=6.5, loc="lower right")

        # The right panel is the corrected claim, not the endpoint comparison.
        # How much the static error can be improved by rank, *as a function of
        # the horizon*, for every Reynolds number measured.  A single endpoint
        # pair understates this by a factor of several and hides that the spread
        # is essentially zero at short horizons and largest from t ~ 1.
        ax = axes[1]
        # BOTH series, because the title has to describe the axis (C7-1) and the
        # two series say different things.  Over all ranks the spread is large
        # from t ~ 1 -- rank buys a static baseline *something* below r=16.  Over
        # r >= 16 alone it is 0.0% at every horizon: the extra modes are not
        # merely unhelpful, they buy nothing measurable at all.  Plotting only
        # the subset would hide the first fact; plotting only all-ranks would make
        # the title a claim the panel does not show.  A referee checks the axis,
        # so the axis and the title have to agree.
        high = [r for r in ranks if r >= 16]
        for j, (re_key, re_case) in enumerate(sorted(by_re.items())):
            base = colors["dlra"] if j == 0 else colors["ref"]
            series = static_error_spread(
                re_case["static_moving_window"], ranks, windows[0]
            )
            if series:
                ax.semilogx(
                    [s["time"] for s in series],
                    [100.0 * s["spread_over_min"] for s in series],
                    "o-", markersize=3.5, linewidth=1.3, color=base,
                    label=f"all ranks {ranks}, Re={re_key}",
                )
            subset = static_error_spread(
                re_case["static_moving_window"], high, windows[0]
            ) if high else []
            if subset:
                ax.semilogx(
                    [s["time"] for s in subset],
                    [100.0 * s["spread_over_min"] for s in subset],
                    "s--", markersize=3.0, linewidth=1.1, color=base, alpha=0.55,
                    label=rf"$r\geq16$ only ({high}), Re={re_key}",
                )
        ax.axhline(10.0, color=colors["full"], linestyle=":", linewidth=1.0)
        ax.annotate("10%", (ax.get_xlim()[0], 10.0), textcoords="offset points",
                    xytext=(2, 2), fontsize=6.5, color=colors["full"])
        ax.set_xlabel("time $t$")
        # The normalizer is stated because the two conventions differ by a factor
        # of nearly two, and a reader comparing against a number quoted the other
        # way would be comparing conventions rather than results.
        ax.set_ylabel("spread of the static error across ranks\n"
                      r"($\max-\min)/\min$, %)", fontsize=8)
        # C7-2: scoped to the grid, because the r=16 saturation contrast is an
        # N=64 result and cannot exist at N=128 -- where r=16 is half the band.
        ax.set_title(
            f"A static subspace saturates in rank, at $N={xover['parameters'].get('N', 64)}$:\n"
            r"$r\geq16$ buys it nothing, while $r<16$ buys plenty", fontsize=9
        )
        ax.legend(fontsize=5.6, loc="upper left")
        CAPTIONS["fig_crossover"] = (
            rf"Left: error against horizon by rank, for the evolving basis (solid) "
            rf"and an oracle trailing-window static baseline (dashed). Right: the "
            rf"spread of the static error across ranks as a function of horizon, "
            rf"at $N={xover['parameters'].get('N', 64)}$, for every Reynolds number "
            rf"measured, with the 10% level marked. **Both rank sets are plotted "
            rf"and the distinction is the result**: over all ranks {ranks} the "
            rf"spread is large from $t\approx1$ -- rank buys a static baseline "
            rf"something below $r=16$ -- while over $r\geq16$ alone it is 0.0% at "
            rf"every horizon, so the extra modes buy nothing measurable at all. The "
            rf"saturation contrast is an $N=64$ result and does not exist at "
            rf"$N=128$, where $r=16$ is half the resolved band."
        )
        FIGURES_WRITTEN.add("fig_crossover")
        fig.savefig(args.output_dir / "fig_crossover.pdf", bbox_inches="tight")
        fig.savefig(args.output_dir / "fig_crossover.png", bbox_inches="tight")
        plt.close(fig)

    # ---------------------------------------------------------------- C11-1
    # The paper includes six figures and only `fig_cost` existed, and
    # `paper/figures/` was empty on every branch, so even that one did not
    # resolve.  These five are the paper's own names, bound by the draft's
    # `\label`s, and their content is transcribed from the captions the draft
    # already carries -- this is transcription, not design.
    #
    # They are written to BOTH output roots.  `experiments/figures/` is where the
    # project's figures live and where PROVENANCE.md and CAPTIONS.md point;
    # `paper/figures/` is where the draft's `\includegraphics{figures/...}` looks.
    # Only generated images are written into the paper's tree -- no prose, no
    # .tex -- and the generating code stays on this side of the ownership line.
    if args.paper_figures_dir is not None:
        args.paper_figures_dir.mkdir(parents=True, exist_ok=True)
    make_paper_figures(
        R, args.output_dir, args.paper_figures_dir, used, skipped, colors
    )

    provenance(R, args.output_dir, sorted(set(used)), skipped)

    if args.paper_figures_dir is not None:
        # Every figure this run wrote, mirrored into the paper's directory, and
        # any figure file already there that this run did NOT write removed --
        # the same stale-file rule as the primary root, because a stale image in
        # the paper is the one a referee actually looks at.
        mirrored, removed = [], []
        for ext in ("pdf", "png"):
            for name in sorted(FIGURES_WRITTEN):
                src = args.output_dir / f"{name}.{ext}"
                if not src.exists():
                    continue
                (args.paper_figures_dir / f"{name}.{ext}").write_bytes(
                    src.read_bytes()
                )
                mirrored.append(f"{name}.{ext}")
            for existing in sorted(args.paper_figures_dir.glob(f"fig_*.{ext}")):
                if existing.name not in mirrored:
                    existing.unlink()
                    removed.append(existing.name)
        print(
            f"mirrored {len(mirrored)} file(s) to {args.paper_figures_dir}"
            + (f"; removed {len(removed)} stale: {', '.join(removed)}"
               if removed else "")
        )
    print(f"figures written to {args.output_dir}")


if __name__ == "__main__":
    main()
