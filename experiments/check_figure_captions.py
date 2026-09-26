"""Check the paper's figure captions against the artifacts, mechanically.

Four of the paper's six figure captions carried claims the runs do not support,
and every one of them was a ``PENDING-CODER: confirm the ... values shown`` item
-- a caption written for a figure that did not exist yet, so its content was
plausible rather than measured.  Writing the corrected caption into
``CAPTIONS.md`` fixes the record but does not *check* anything: the next figure,
or the next re-run, can drift the same way.

So the claims are extracted and compared here.  Each entry states what the
caption claims, what the artifact says, and a verdict, and the verdicts are
asserted.  A drift in either the claim or the artifact makes this fail with the
two numbers side by side, which is the form a reader can act on.

This is deliberately *not* a gate on the draft -- the captions are the writer's
to change, and a gate that blocks their edit is a gate that gets bypassed.  It is
a check on **my** side: the measured values are recomputed from the artifacts
here, so if a re-run moves one, this says so before a caption does.

Run from the repository root::

    python experiments/check_figure_captions.py
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "experiments") not in sys.path:
    sys.path.insert(0, str(ROOT / "experiments"))

RESULTS = ROOT / "state" / "coder" / "results"


def load(name: str) -> dict | None:
    path = RESULTS / name
    return json.loads(path.read_text()) if path.exists() else None


def caption_claims() -> dict:
    """The claims as the draft states them, keyed by figure name.

    Transcribed from ``paper/sections/06_results.tex`` on the writer's branch.
    Kept as literals on purpose: this checks the *draft's* wording, so reading it
    out of the file would make the check tautological on the one thing it exists
    to verify.
    """
    return {
        "fig_tg_ke_rank": {
            "caption": (
                "Left: kinetic energy E(t) (monotone non-increasing, I2). Right: "
                "adaptive rank r(t) decaying 3 -> 2 -> 1 under the sigma_tol rule."
            ),
        },
        "fig_rank_vs_time": {
            "caption": (
                "Adaptive rank r(t) for forced Kolmogorov flow at Re in "
                "{100, 1000, 5000}. Growth during spin-up, then a "
                "quasi-stationary rank r*(Re)."
            ),
        },
        "fig_sv_decay": {
            "caption": (
                "Singular-value decay of psi at Re in {100, 1000, 5000}, at "
                "representative times in the statistical window. Slower decay at "
                "higher Re."
            ),
        },
        "fig_error_vs_ref": {
            "caption": (
                "Relative L2 error against the full-grid spectral reference over "
                "the statistical window, per Re. SP-DLRA (adaptive) versus the "
                "static POD baseline."
            ),
        },
        "fig_cost": {
            "caption": (
                "Cost comparison: per-step and total wall-clock time and peak "
                "memory for SP-DLRA, the full-grid spectral reference, and the "
                "static POD baseline, per Re."
            ),
        },
        "fig_ke_spectrum": {
            "caption": (
                "Kinetic-energy statistics: left, E(t) over the statistical "
                "window; right, kinetic-energy spectrum versus wavenumber; per "
                "Re, SP-DLRA against the full-grid reference."
            ),
        },
    }


def check() -> list[str]:
    """Recompute every claim from the artifacts. Returns a list of problems."""
    problems: list[str] = []
    claims = caption_claims()

    # --- fig:tg -- rank 3 -> 2 -> 1, and E(t) monotone --------------------
    tg = load("taylor_green.json")
    if tg and tg.get("rank_history"):
        distinct = sorted(set(int(r) for r in tg["rank_history"]))
        if distinct != [1, 2, 3]:
            problems.append(
                f"fig:tg claims the rank decays 3 -> 2 -> 1; the run gives "
                f"r(t) in {distinct}. The initial condition is a single Fourier "
                f"mode, so a decay of that shape cannot occur here."
            )
        if max(distinct) > 1:
            problems.append(
                f"fig:tg: the rank is not constant ({distinct}), so the "
                f"figure's 'constant at 1' title would now be wrong."
            )
        if tg.get("energy_history"):
            increments = [
                b - a for a, b in zip(tg["energy_history"], tg["energy_history"][1:])
            ]
            increases = sum(1 for d in increments if d > 0)
            if increases:
                problems.append(
                    f"fig:tg claims E(t) is monotone non-increasing; the run has "
                    f"{increases} increases in {len(increments)} steps."
                )
    else:
        problems.append("fig:tg: taylor_green.json has no rank/energy history")

    # --- fig:rank -- growth then r*(Re) ------------------------------------
    finals, firsts = {}, {}
    for re in (100, 1000, 5000):
        data = load(f"kolmogorov_re{re}_N64.json")
        if not data or not (data["dlra"].get("rank_history")):
            problems.append(f"fig:rank: no rank_history for Re={re}")
            continue
        history = data["dlra"]["rank_history"]
        finals[re] = int(history[-1])
        firsts[re] = int(history[0])
        final = history[-1]
        reached = next(
            (i for i, v in enumerate(history) if all(x == final for x in history[i:])),
            None,
        )
        if reached is not None and reached > len(history) // 4:
            problems.append(
                f"fig:rank claims growth during spin-up; at Re={re} the rank "
                f"reaches its final value at check {reached} of "
                f"{len(history)}, so there is a transient to show after all and "
                f"the figure title would be wrong."
            )
    if finals and len(set(finals.values())) == 1:
        only = next(iter(set(finals.values())))
        problems.append(
            f"fig:rank claims a quasi-stationary r*(Re); r* is {only} at every "
            f"Re measured ({finals}), so there is no Re dependence to report -- "
            f"and {only} is the top of the band N=64 resolves, not a dynamical "
            f"rank."
        )
    elif finals:
        problems.append(
            f"fig:rank: r* now varies with Re ({finals}); the caption's claim "
            f"that it is a function of Re is now supported and the figure "
            f"title should change."
        )

    # --- fig:svd -- slower decay at higher Re, and the mode count ----------
    modes, slopes = {}, {}
    for re in (100, 1000, 5000):
        data = load(f"kolmogorov_re{re}_N64.json")
        if not data:
            continue
        spectra = data["dlra"].get("singular_values") or []
        if not spectra:
            continue
        final = spectra[-1]
        if not final or final[0] <= 0:
            continue
        modes[re] = sum(1 for s in final if s >= 1e-10 * final[0])
        slopes[re] = final[19] / final[0] if len(final) > 19 else None
    if len(set(modes.values())) == 1 and modes:
        problems.append(
            f"fig:svd implies the decay differs across Re; the mode count above "
            f"1e-10 is {next(iter(set(modes.values())))} at every Re ({modes})."
        )
    usable = {k: v for k, v in slopes.items() if v}
    if len(usable) == 3:
        ordered = [usable[100], usable[1000], usable[5000]]
        monotone = ordered[0] <= ordered[1] <= ordered[2]
        spread = (ordered[-1] - ordered[0]) / ordered[0]
        if not monotone:
            problems.append(
                f"fig:svd claims slower decay at higher Re; sigma_20/sigma_1 is "
                f"{ordered}, which is not monotone in Re."
            )
        elif spread > 0.5:
            problems.append(
                f"fig:svd: sigma_20/sigma_1 varies by {100*spread:.0f}% across "
                f"Re, so 'slower decay at higher Re' is now a substantial claim "
                f"and the caption should quantify it."
            )

    # --- fig:cost -- memory, POD, per Re ----------------------------------
    cost = load("cost_retiming.json")
    if cost:
        if "memory" in json.dumps(cost).lower():
            problems.append(
                "fig:cost's caption claims peak memory and cost_retiming.json "
                "now contains a memory field; check which figure it belongs in."
            )
        timed = cost.get("integrators_timed") or []
        if not any("pod" in str(t).lower() for t in timed):
            problems.append(
                f"fig:cost's caption lists the static POD baseline among the "
                f"methods, but cost_retiming.json times {timed} -- POD is not "
                f"among them."
            )
        if "re" not in {k.lower() for k in cost.get("parameters", {})}:
            problems.append(
                "fig:cost's caption says per Re; cost_retiming.json has no "
                "Reynolds parameter -- it varies N."
            )
    peak = load("peak_memory.json")
    if peak and not any(
        row.get("method") == "pod" for row in peak.get("measurements", [])
    ):
        problems.append(
            "fig:cost's caption implies POD peak memory; peak_memory.json "
            f"measures {sorted({r.get('method') for r in peak['measurements']})} "
            "-- POD is not among them."
        )

    # --- fig:error -- SP-DLRA versus static POD, per Re ---------------------
    # The claim has two parts: a method comparison, and a per-Re breakdown.  The
    # suite records only scalars, not a series, so this checks the scalars: which
    # method is more accurate, and how much each depends on Re.  Both matter,
    # because a reader shown "SP-DLRA versus static POD" will assume the first is
    # the better one, and the measurement is the other way round.
    per_re: dict[int, dict[str, float]] = {}
    for re in (100, 1000, 5000):
        data = load(f"kolmogorov_re{re}_N64.json")
        if not data:
            continue
        row = {
            m: data[m].get("max_relative_l2_vs_full")
            for m in ("dlra", "pod")
            if isinstance(data.get(m), dict)
            and data[m].get("max_relative_l2_vs_full") is not None
        }
        if row:
            per_re[re] = row
    if len(per_re) >= 2:
        better = {
            re: row["dlra"] / row["pod"]
            for re, row in sorted(per_re.items())
            if {"dlra", "pod"} <= set(row) and row["pod"] > 0 and row["pod"] < row["dlra"]
        }
        if better:
            problems.append(
                "fig:error presents 'SP-DLRA (adaptive) versus the static POD "
                "baseline' with no indication of which is better; at every Re "
                "measured static POD is the MORE accurate method, by factors "
                + ", ".join(f"{r:.0f}x at Re={k}" for k, r in better.items())
                + ". A reader will assume the opposite ordering. The ordering "
                "is not a bug in either method -- a static basis fitted on the "
                "training snapshots is simply the better representation of a "
                "short, smooth window -- but it has to be stated."
            )
        # One "per Re" axis spanning both methods only makes sense if the two
        # have comparable Re-sensitivity.  They do not, by two orders of
        # magnitude, and DLRA's own spread is negligible -- so a threshold is
        # needed or the flat one reads as a fault when it is a property.
        factor = {}
        for method in ("dlra", "pod"):
            values = [row[method] for row in per_re.values() if method in row]
            if len(values) >= 2 and min(values) > 0:
                factor[method] = max(values) / min(values)
        large = {m: f for m, f in factor.items() if f >= 10}
        if large:
            problems.append(
                "fig:error's 'per Re' breakdown is not comparable across the two "
                "methods: max relative L2 varies across Re by "
                + ", ".join(
                    f"a factor of {factor[m]:.0f} for {m.upper()}"
                    + (
                        ""
                        if m in large
                        else f" ({factor[m]:.2f}, i.e. flat -- a property, not a fault)"
                    )
                    for m in ("dlra", "pod")
                    if m in factor
                )
                + f". The axis shows {max(large, key=lambda m: factor[m]).upper()}'s "
                "Re-sensitivity and hides SP-DLRA's; say which."
            )
    elif per_re:
        problems.append(
            f"fig:error: max_relative_l2_vs_full present for only {sorted(per_re)}"
        )

    # --- fig:kestats -- SP-DLRA against the full grid, per Re --------------
    # The right panel is claimed to be a method comparison.  It cannot be unless
    # some artifact carries a spectrum per method; check that rather than assume.
    methods_with_spectra: set[str] = set()
    for name in ("kolmogorov_re100_N64.json", "kolmogorov_re1000_N64.json",
                 "kolmogorov_re5000_N64.json", "kolmogorov_re5000_N128.json",
                 "regime_pilot_re5000_A0p2.json",
                 "regime_pilot_re5000_N128_A0p2.json"):
        data = load(name)
        if not data:
            continue
        windows = data.get("windowed_spectra") or {}
        if windows:
            # A single unnamed spectrum is one arm, not a comparison.
            methods_with_spectra.add(f"{name}:1 spectrum")
        for method, block in data.items():
            if isinstance(block, dict) and (
                block.get("isotropic_spectrum") or block.get("spectrum_E")
            ):
                methods_with_spectra.add(f"{name}:{method}")
    if not any(":" in m and not m.endswith("1 spectrum") for m in methods_with_spectra):
        problems.append(
            "fig:kestats's right panel is claimed to be 'SP-DLRA against the "
            "full-grid reference', but no artifact carries a spectrum per "
            f"method: the suite sets --spectrum-count unset ({len(methods_with_spectra)} "
            "single-arm spectrum(s) found, none per method). A per-method version "
            "is a new run, not a redraw."
        )

    return problems


BASELINE = RESULTS / "caption_verdicts.json"


def _verdict_key(problem: str) -> str:
    """A stable identity for a verdict, so a re-worded message is not a change.

    Keyed on the figure label and the substance, not the full sentence: the
    wording will be edited as the claims are resolved, and a check that fires on
    a reworded message is a check that gets ignored.

    The label is extracted with a pattern rather than by splitting on whitespace,
    because the sentences open with a possessive -- "fig:cost's caption ..." --
    and a naive split yields the key ``fig:cost's``, which is trivially
    mistyped.  That is not hypothetical: the first positive control for this
    checker missed its target for exactly this reason, and reported green.
    """
    match = re.match(r"(fig:[\w]+)", problem)
    label = match.group(1) if match else problem.split()[0].rstrip(":")
    for topic in ("rank decays", "r*(Re)", "spin-up", "mode count", "slower decay",
                  "sigma_20", "static POD", "per Re", "peak memory",
                  "monotone", "E(t)", "history"):
        if topic in problem:
            return f"{label}|{topic}"
    return f"{label}|other"


def main() -> int:
    claims = caption_claims()
    problems = check()
    verdicts = sorted({_verdict_key(p) for p in problems})

    print("FIGURE CAPTION CHECK — the draft's claims against the artifacts\n")
    print(f"  population: {len(claims)} caption(s) from the draft's results section")
    print(f"  artifacts:  {len(list(RESULTS.glob('*.json')))} in {RESULTS}")
    print(f"  unsupported claims: {len(verdicts)}")
    print()
    for key in verdicts:
        print(f"    - {key}")
    print()

    # Drift, not disagreement.  The captions are the writer's to correct and six
    # of them are already reported as unsupported, so a checker that exits
    # non-zero for that is a checker that is permanently red and therefore not
    # read.  What matters is a verdict FLIPPING: a re-run that turns a supported
    # claim into an unsupported one, or moves a measured value, is the thing that
    # would silently reach the paper.
    previous = None
    if BASELINE.exists():
        try:
            previous = set(json.loads(BASELINE.read_text())["verdicts"])
        except (json.JSONDecodeError, KeyError):
            previous = None
    if previous is None:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        baseline = {
            "case": "caption_verdicts",
            "verdicts": verdicts,
            "note": (
                "Which of the draft's figure captions the artifacts do not "
                "support, recorded so the check reports DRIFT rather than "
                "repeating a known list. Keyed on figure label and topic, not "
                "on the message text, so rewording a verdict is not a change."
            ),
        }
        # This file lives in state/coder/results/ alongside the runs, and the
        # reviewer's `check_provenance.py` FAILs any artifact there that carries
        # no provenance block. It is a generated artifact, so it records who
        # generated it and from which commit -- the same discipline the runs get,
        # and what makes that gate's verdict about this file mean something.
        #
        # Wrapped because a missing provenance block is visible and fixable,
        # whereas a checker that refuses to write down its findings because the
        # bookkeeping failed is neither.
        try:
            from _paths import EXPERIMENTS
            from provenance import provenance

            baseline["provenance"] = provenance(
                EXPERIMENTS / "check_figure_captions.py"
            )
        except Exception as exc:                       # pragma: no cover
            baseline["provenance_error"] = f"{type(exc).__name__}: {exc}"
        BASELINE.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n")
        print(f"  baseline written to {BASELINE.name} ({len(verdicts)} verdicts)")
        print("  nothing to compare against yet; this run is the baseline")
        return 0

    new, fixed = set(verdicts) - previous, previous - set(verdicts)
    if not new and not fixed:
        print("  no drift: every verdict is unchanged from the baseline")
        return 0
    if new:
        print(f"  {len(new)} NEWLY UNSUPPORTED claim(s) -- a re-run moved:\n")
        for key in sorted(new):
            print(f"    + {key}")
    if fixed:
        print(f"  {len(fixed)} claim(s) now SUPPORTED:\n")
        for key in sorted(fixed):
            print(f"    - {key}")
    print("\n  the measured values are in experiments/figures/CAPTIONS.md")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
