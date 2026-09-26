"""Check that a driver's flags exist before running it — the cheap gate.

Two bad invocations cost real time on 2026-09-26, and both were the same shape:
an argument that the driver's parser does not have, or has differently.

* a shared ``--dt`` plus a per-case ``--dt`` — argparse keeps the last, so one
  case ran at twice its recorded timestep and produced a different case under the
  right filename;
* ``--re 5000 --re 1000`` — argparse keeps the last, so half the parameter space
  ran and overwrote a complete artifact.

Neither failed loudly. Both produced a *complete-looking* artifact from a run
that did not do what its filename said, and each was caught only by a gate
downstream (`test_every_driver_runs` for the first, a registry row for the
second). A driver's own ``--help`` knows its flags exactly, so asking it costs
one subprocess and no compute.

This does not replace reading the driver. It catches the flags that do not exist
-- which is the failure that produces a wrong run rather than an error.

    python experiments/check_driver_flags.py <script.sh> [more scripts ...]

With no arguments it checks every launch script it can find under
``/tmp/opencode`` is not assumed; pass paths explicitly.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = os.path.expanduser("~/.venvs/ns/bin/python")

# `experiments/foo.py` followed by the rest of the logical line, honouring
# backslash continuations.
INVOCATION = re.compile(r"experiments/(\w+\.py)((?:[^\n]*\\\n)*[^\n]*)")


def flags_of(driver: str) -> set[str] | None:
    result = subprocess.run(
        [PY, str(ROOT / "experiments" / driver), "--help"],
        cwd=ROOT, capture_output=True, text=True, timeout=300,
    )
    if result.returncode != 0:
        return None
    return set(re.findall(r"--[A-Za-z0-9-]+", result.stdout))


def check(script: Path) -> list[str]:
    problems: list[str] = []
    text = script.read_text()
    for driver, tail in INVOCATION.findall(text):
        known = flags_of(driver)
        if known is None:
            problems.append(f"{script.name}: {driver} --help failed; cannot validate")
            continue
        for flag in re.findall(r"--[A-Za-z0-9-]+", tail):
            if flag not in known:
                problems.append(
                    f"{script.name}: {driver} has no {flag} "
                    f"(known: {' '.join(sorted(known))})"
                )
    return problems


def main() -> int:
    # `--help` has to be handled explicitly. This script takes a list of paths
    # positionally, so without this it treats `--help` as a filename, reports
    # "no such file" and exits 1 -- a tool for inspecting drivers that cannot be
    # asked for its own help. Found by
    # `test_every_driver_can_print_its_own_help`, which is the check that
    # `check_driver_flags.py` exists to make reliable.
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print(__doc__)
        print("usage: check_driver_flags.py <script.sh> [more scripts ...]")
        return 0
    if len(sys.argv) < 2:
        print(__doc__)
        print("usage: check_driver_flags.py <script.sh> [more scripts ...]")
        return 2
    all_problems: list[str] = []
    for arg in sys.argv[1:]:
        script = Path(arg)
        if not script.exists():
            all_problems.append(f"{arg}: no such file")
            continue
        found = check(script)
        n_inv = len(INVOCATION.findall(script.read_text()))
        print(f"  {script.name}: {n_inv} invocation(s), "
              + ("all flags exist" if not found else f"{len(found)} bad flag(s)"))
        all_problems.extend(found)
    print()
    for problem in all_problems:
        print(f"  - {problem}")
    if all_problems:
        print("\n  A flag the parser does not have fails at parse time, which is")
        print("  good. A flag the parser HAS but means differently runs happily")
        print("  and produces a wrong artifact -- this check cannot see that.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
