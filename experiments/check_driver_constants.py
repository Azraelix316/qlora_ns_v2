"""Are the parameters a driver does NOT take as flags still the ones it used?

`run_long_time.py` and `run_rank_growth_sweep.py` expose a handful of options and
hold the rest as constants, so their artifacts record a `parameters` block with
more entries than the parser has options. That is a real hazard: re-running such
a driver with only the flags can silently change a parameter that has no flag,
and the artifact will look perfectly reproducible.

So the constants are read *out of the source* and compared with what the last run
recorded. This is a textual/AST check rather than an execution of the driver --
it is meant to be cheap enough to run before a multi-hour launch, not to be a
substitute for one.

    python experiments/check_driver_constants.py
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "state" / "coder" / "results"

#: driver -> (artifact, [(name, source-variable, recorded-parameter-name)])
#:
#: Only parameters the driver holds as a *constant* appear here. Everything with a
#: flag is covered by ``check_driver_flags.py`` instead, and the division matters:
#: a flag can be validated against the parser, a constant cannot.
DRIVERS = {
    "run_long_time.py": (
        "kolmogorov_re5000_N64_long.json",
        [
            # (constant name in the source, key in the artifact's parameters)
            ("force_amplitude", "force_amplitude"),
            ("base_speed", "base_speed"),
            ("perturbation_velocity_rms", "perturbation_velocity_rms"),
            ("cutoff", "cutoff"),
            ("seed", "seed"),
            ("wavenumber", "forcing_wavenumber"),
        ],
    ),
}


def constants_in(tree: ast.AST) -> dict[str, object]:
    """Every ``name = <literal>`` binding in the module, and tuple-unpacked ones.

    The drivers assign several constants on one line
    (``force_amplitude, base_speed, perturbation_velocity_rms = 0.5, 0.5, 1.0``),
    so a plain walk of ``Assign`` nodes would miss all three. Both forms are
    handled, because the form that actually occurs is the one that has to work.
    """
    out: dict[str, object] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, SyntaxError):
            continue
        if isinstance(node.targets[0], ast.Name):
            out[node.targets[0].id] = value
        elif isinstance(node.targets[0], (ast.Tuple, ast.List)) and isinstance(
            value, (tuple, list)
        ):
            for name, item in zip(node.targets[0].elts, value):
                if isinstance(name, ast.Name):
                    out[name.id] = item
    return out


def main() -> int:
    problems: list[str] = []
    checked = 0
    for driver, (artifact_name, pairs) in DRIVERS.items():
        path = ROOT / "experiments" / driver
        constants = constants_in(ast.parse(path.read_text()))
        data = json.loads((RESULTS / artifact_name).read_text())
        recorded = data.get("parameters", {})
        print(f"  {driver}  vs  {artifact_name}")
        for source_name, recorded_name in pairs:
            if source_name not in constants:
                problems.append(
                    f"{driver}: {source_name} is not a module-level constant any "
                    "more; this check needs updating before it can vouch for it"
                )
                print(f"    {recorded_name:28s} NOT FOUND as a constant")
                continue
            want, got = constants[source_name], recorded.get(recorded_name)
            ok = want == got
            checked += 1
            print(f"    {recorded_name:28s} source {want!r:12} recorded {got!r:12} "
                  + ("ok" if ok else "<== DIFFERS"))
            if not ok:
                problems.append(
                    f"{driver}: {recorded_name} is {want!r} in the source but "
                    f"{got!r} in {artifact_name}; re-running with the flags alone "
                    "would change it silently"
                )
    print()
    print(f"  {checked} constant(s) compared")
    for problem in problems:
        print(f"  - {problem}")
    if not problems:
        print("  every constant matches what the last run recorded")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
