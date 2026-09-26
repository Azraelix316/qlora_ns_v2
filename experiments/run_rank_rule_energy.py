"""How much fluctuation energy each rank rule leaves outside the subspace.

D18.6 makes the numbers in ``state/coder/results/README.md`` inadmissible until
they are committed: the instantaneous rule keeping ``1.5%`` outside, the windowed
rule ``27.5%``, and the windowed rule with a hindsight-chosen window ``1.3%``
were measured in a message and never landed.  This driver measures them again and
writes them where a reader can check them, so the D12 note can cite an artifact
instead of asserting.

The quantity is the fraction of fluctuation energy that the retained subspace
does **not** span, so it is directly comparable across rules and lower is
better.  It is computed from the *same* candidate fields for every rule, so the
comparison isolates the rule and not the trajectory or the window contents.

Three rules are measured, and the third is the control that decides whether the
second one's result is about windows or about the rule:

``instantaneous``
    one candidate field at a time -- what the per-step criterion actually reads.
``windowed``
    the singular values of the *stacked* recent candidates, via the same Gram
    construction as ``DLRA._window_spectrum``.  This is the rule D18.1 proposed.
``windowed_oracle``
    the same, but over the window placement that minimises the retained fraction
    when chosen with hindsight.  If this is close to the instantaneous rule, the
    windowed rule's loss is the *rule*; if it is close to the windowed rule, the
    loss is the *window placement*.  D18.3 refuted the placement explanation.

Run from the repository root::

    python experiments/run_rank_rule_energy.py --output state/coder/results/rank_rule_energy.json
"""
from __future__ import annotations

import argparse
import json

from _cli import ListOnce
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "experiments") not in sys.path:
    sys.path.insert(0, str(ROOT / "experiments"))

from provenance import provenance as _provenance  # noqa: E402
from run_kolmogorov import make_initial_state  # noqa: E402
from solvers import Grid2D, KolmogorovForcing, StreamFunctionNS  # noqa: E402
from solvers.spectral import fluctuations  # noqa: E402


def _spectrum_and_basis(
    columns: list[np.ndarray], centre: bool
) -> tuple[np.ndarray, np.ndarray]:
    """Singular values and a basis for the retained subspace.

    ``centre`` is not a detail, it is the whole difference between the two rules,
    and getting it wrong is what made the first version of this driver score
    every rule identically:

    * ``centre=True`` reproduces ``run_regime_pilot.window_rank_table``: the
      stack has its across-window mean removed before the SVD, so the spectrum
      ranks the *variation* across the window.  This is what the windowed rule
      does, and it is why the windowed rule's subspace is a variation subspace.
    * ``centre=False`` is the instantaneous rule: one field, no window, so there
      is nothing to centre.  (Centring a single column would return the zero
      vector and rank 0 for every input.)

    Via the Gram matrix, as ``DLRA._window_spectrum`` does: the singular values
    of an ``N^2 x k`` stack are the square roots of the eigenvalues of its ``k x
    k`` Gram matrix, so no large factorization is needed.
    """
    k = len(columns)
    if k == 0:
        return np.zeros(0), np.zeros((k, 0))
    stack = np.stack(columns, axis=1)                  # N^2 x k
    if centre:
        stack = stack - stack.mean(axis=1)[:, None]
    values, vectors = np.linalg.eigh(stack.T @ stack)
    order = np.argsort(values)[::-1]
    return (
        np.sqrt(np.clip(values[order], 0.0, None)),
        vectors[:, order],
    )


def _retained_rank(singular_values: np.ndarray, energy_fraction: float) -> int:
    """Smallest r whose leading energy fraction reaches the target."""
    if singular_values.size == 0 or singular_values[0] <= np.finfo(float).eps:
        return 0
    energy = np.cumsum(singular_values.astype(float) ** 2)
    total = energy[-1]
    if total <= 0.0:
        return 0
    return int(np.searchsorted(energy / total, energy_fraction) + 1)


def _retained_rank_amplitude(
    singular_values: np.ndarray, relative_cutoff: float
) -> int:
    """Number of leading singular values above ``cutoff * s_1``.

    This is the rule the DLRA actually applies (``relative_amplitude_cutoff``)
    and the one the D12 note's numbers were measured at, so it is the default
    here.  An amplitude test is a test on singular *values*: a cutoff of 1e-6 is
    an energy ratio of 1e-12, which is why the two criteria give very different
    ranks on the same spectrum, and why neither may be called an accuracy
    tolerance.
    """
    if singular_values.size == 0 or singular_values[0] <= 0.0:
        return 0
    return int(np.count_nonzero(
        singular_values >= relative_cutoff * singular_values[0]
    ))


def _fraction_left_out(
    columns: list[np.ndarray], target: np.ndarray, energy_fraction: float,
    centre: bool, relative_cutoff: float | None = None,
) -> dict:
    """Fraction of ``target``'s energy that the rule's subspace does not span.

    The target is the *last* candidate -- the field the dynamics has actually
    reached -- and the subspace is the one the rule would retain from its own
    columns.  That is the quantity that says whether a rule has thrown away
    something the dynamics still needs.

    The target is **not** centred, for either rule.  Centring it would subtract
    from the denominator the very component whose retention is in question, and
    the windowed rule's subspace is a variation subspace by construction, so an
    uncentred target is exactly what exposes the cost.

    An earlier version of this measured the fraction of the **stack's** own
    energy left outside the stack's leading directions, and every rule scored
    ~0%: consecutive candidates are nearly parallel, so one direction holds 99%
    of the stack whatever the rule does.  That measures the stack, not the rule,
    and it is the kind of metric that makes every alternative look equivalent.
    """
    spectrum, vectors = _spectrum_and_basis(columns, centre)
    rank = (
        _retained_rank_amplitude(spectrum, relative_cutoff)
        if relative_cutoff is not None
        else _retained_rank(spectrum, energy_fraction)
    )
    target_energy = float(target @ target)
    stack = np.stack(columns, axis=1)
    if centre:
        stack = stack - stack.mean(axis=1)[:, None]
    if rank == 0 or target_energy <= 0.0:
        return {
            "rank": rank,
            "fraction_left_out": None,
            "target_energy": target_energy,
            "singular_values": [float(x) for x in spectrum],
        }
    basis = stack @ vectors[:, :rank]                          # N^2 x r
    coefficients, *_ = np.linalg.lstsq(basis, target, rcond=None)
    residual = target - basis @ coefficients
    return {
        "rank": rank,
        "fraction_left_out": float(residual @ residual) / target_energy,
        "target_energy": target_energy,
        "singular_values": [float(x) for x in spectrum],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--N", type=int, default=64)
    parser.add_argument("--re", type=int, default=5000)
    parser.add_argument("--dt", type=float, default=0.0005)
    parser.add_argument("--steps", type=int, default=2000,
                        help="trajectory length; the rules are compared on the "
                             "same candidates, so this only sets how much of the "
                             "trajectory they have seen")
    parser.add_argument("--energy-fraction", type=float, default=0.99,
                        help="used only when --relative-amplitude-cutoff is None")
    parser.add_argument("--relative-amplitude-cutoff", type=float, default=1e-10,
                        help="the rule the DLRA applies; set to an empty value to "
                             "use the energy criterion instead")
    parser.add_argument("--window", type=int, default=16,
                        help="candidates in the windowed rule's stack")
    parser.add_argument("--force-amplitude", type=float, default=0.5)
    parser.add_argument("--base-speed", type=float, default=0.5)
    parser.add_argument("--perturbation-velocity-rms", type=float, default=1.0)
    parser.add_argument("--cutoff", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260925)
    parser.add_argument("--check-every", type=int, default=5)
    parser.add_argument("--gaps", type=int, nargs="+", action=ListOnce,
                        default=[1, 20, 100, 400],
                        help="how many checks ahead of the rule's columns the "
                             "target field lies; each is a separate row, because "
                             "the answer depends on how far the rank has to hold")
    parser.add_argument("--output", type=Path,
                        default=Path("state/coder/results/rank_rule_energy.json"))
    args = parser.parse_args()

    grid = Grid2D(args.N)
    model = StreamFunctionNS(
        grid, nu=1.0 / args.re,
        forcing=KolmogorovForcing(amplitude=args.force_amplitude, wavenumber=1.0),
        dealias=True,
    )
    state = make_initial_state(
        grid, base_speed=args.base_speed,
        perturbation_velocity_rms=args.perturbation_velocity_rms,
        cutoff=args.cutoff, seed=args.seed,
    )
    # Candidates are fluctuation fields, so the secularly growing zonal mean
    # cannot dominate the energy fraction -- the same basis the DLRA uses.
    candidates: list[np.ndarray] = []
    for step in range(1, args.steps + 1):
        state = model.step(state, args.dt, t=(step - 1) * args.dt)
        if not np.isfinite(state).all():
            raise SystemExit(f"reference run went non-finite at step {step}")
        if step % args.check_every == 0:
            psi = fluctuations(state)
            candidates.append(psi.reshape(-1).copy())

    # Every rule is evaluated on columns that *exclude* the target, and the target
    # is held a configurable number of checks ahead of them.  Both details are
    # load-bearing and both were found by getting them wrong first.
    #
    # Scoring the instantaneous rule on the target itself is tautological: it
    # retains the field it is shown and leaves 0% out for a reason that has
    # nothing to do with the rule.  With a gap of one check the comparison is
    # *also* uninformative, because consecutive candidates 0.0025 apart are
    # nearly parallel and rank 1 spans the next one to within 1e-10 -- the rule
    # looks perfect because the flow is slow at that sampling interval, not
    # because the rule is good.  The gap is what makes the question real: a rank
    # is chosen at some step and has to hold at a later one, so the reported
    # fraction is measured against how far ahead it has to hold.
    rows = []
    for gap in args.gaps:
        stop = len(candidates) - gap
        if stop < 2:
            continue
        target = candidates[stop - 1 + gap]
        history = candidates[:stop - 1]
        for label, columns, centre in (
            # The instantaneous rule reads one field, so there is no window to
            # centre.
            ("instantaneous", history[-1:], False),
            # The windowed rule reads a window, and the project's windowed
            # spectrum (run_regime_pilot.window_rank_table) centres it.  That
            # centring is the mechanism, not an incidental choice: it is what
            # makes the retained subspace a *variation* subspace.
            ("windowed", history[-args.window:], True),
        ):
            rows.append({
                "rule": label,
                "gap_checks": gap,
                "gap_time": gap * args.check_every * args.dt,
                "window_centred": centre,
                **_fraction_left_out(
                    columns, target, args.energy_fraction, centre,
                    args.relative_amplitude_cutoff,
                ),
            })

        # The control: the same rule over the best window available, chosen with
        # hindsight.  It is what decides whether the windowed rule's loss is the
        # rule or the window placement, and it is why the note in
        # results/README.md can say the placement explanation is refuted rather
        # than merely unexamined.
        best = None
        for start in range(0, max(len(history) - args.window + 1, 1)):
            window = history[start:start + args.window]
            if len(window) < 2:
                continue
            trial = _fraction_left_out(
                window, target, args.energy_fraction, True,
                args.relative_amplitude_cutoff,
            )
            if trial["fraction_left_out"] is None:
                continue
            if best is None or trial["fraction_left_out"] < best["fraction_left_out"]:
                best = {**trial, "window_start_index": start,
                        "window_start_time": (start + 1) * args.check_every * args.dt}
        if best is not None:
            rows.append({
                "rule": "windowed_oracle", "gap_checks": gap,
                "gap_time": gap * args.check_every * args.dt,
                "window_centred": True, **best,
            })

    artifact = {
        "case": "rank_rule_energy",
        "case_family": "rank",
        "provenance": {
            **_provenance(Path(__file__).resolve()),
            "driver": "experiments/run_rank_rule_energy.py",
        },
        "parameters": {
            "N": args.N, "re": args.re, "dt": args.dt, "steps": args.steps,
            "energy_fraction": args.energy_fraction,
            "relative_amplitude_cutoff": args.relative_amplitude_cutoff,
            "criterion": ("relative amplitude" if args.relative_amplitude_cutoff
                          is not None else "energy fraction"),
            "window": args.window,
            "check_every": args.check_every, "seed": args.seed,
            "cutoff": args.cutoff, "force_amplitude": args.force_amplitude,
            "base_speed": args.base_speed,
            "perturbation_velocity_rms": args.perturbation_velocity_rms,
            "candidates_collected": len(candidates),
            "gaps": args.gaps,
            "final_time": args.steps * args.dt,
        },
        "rows": rows,
        "interpretation": (
            "The fraction of FLUCTUATION energy left outside the subspace each "
            "rule retains, at the same energy fraction, on the same candidate "
            "fields. Lower is better. This exists because D18.6 makes the "
            "equivalent numbers inadmissible until they are committed: they were "
            "previously message-only. The windowed_oracle row is the control -- "
            "it is the windowed rule given the best window chosen with "
            "hindsight, so a windowed_oracle value close to `instantaneous` means "
            "the windowed rule's loss is the RULE and not the window placement."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
