#!/usr/bin/env python3
"""Every shipped run artifact must be able to say whether it is reproducible.

WHY THIS EXISTS. `state/coder/results/` is the project's evidence. A result
whose provenance is unknown is indistinguishable from a result whose provenance
is clean -- which is the failure this project has paid for repeatedly (D66, D77,
D85, D94, D96, D103, D105). And the provenance block was, until this check,
read by NOTHING: no gate, and no test. It was written by the driver and then
never looked at again by anyone.

It was not decorative. `kolmogorov_re5000_N128.json` sat on `main` recording

    "driver_dirty": true, "driver_matches_HEAD": false, "reproducible": false

i.e. produced by a driver that matched no commit, from a dirty working tree --
and it was being cited, including by my own D106. The coder re-ran it, and the
re-run reproduced every recorded series BYTE-IDENTICALLY (rank history,
fluctuation histories, comparison series) with only the timings changed. That is
a strong result, and it was invisible until something read the flag.

THE THREE CATEGORIES, because they are different faults and must not be
collapsed:

  clean    -- `driver_matches_HEAD is True`. The driver that produced the file
              is byte-identical to the driver at the recorded commit.
  DIRTY    -- `driver_matches_HEAD is False`. The file was produced by code that
              is in no commit. A hard FAILURE: the run is not reproducible from
              the repository.
  LEGACY   -- the field is absent. The run predates the fingerprint mechanism:
              it records which commit was HEAD at launch but not whether the
              driver on disk matched it. NOT a defect, and not silently passed
              either -- it is reported by name every run, because it bounds what
              may be claimed from those artifacts.

An artifact with no `parameters` is a SUMMARY of other runs and cannot carry
provenance of its own; it must still carry a `provenance` block, and it is
exempt from the run rules.

Usage:  check_provenance.py [--ref main] [--self-test]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
RESULTS = "state/coder/results"


def _git(*a: str) -> str:
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout


def classify(doc: dict) -> str:
    """clean | dirty | legacy | summary-noprovenance | summary | no-provenance"""
    prov = doc.get("provenance")
    is_run = "parameters" in doc
    if not prov:
        return "no-provenance"
    if not is_run:
        return "summary"
    m = prov.get("driver_matches_HEAD")
    if m is True:
        return "clean"
    if m is False:
        return "dirty"
    return "legacy"


def load_from_ref(ref: str) -> list[tuple[str, dict]]:
    out = []
    for path in _git("ls-tree", "-r", "--name-only", ref, "--", RESULTS).split():
        if not path.endswith(".json"):
            continue
        raw = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=REPO,
                             capture_output=True, text=True).stdout
        try:
            out.append((path.split("/")[-1], json.loads(raw)))
        except json.JSONDecodeError:
            out.append((path.split("/")[-1], {}))
    return out


def check(ref: str = "main") -> int:
    rows = load_from_ref(ref)
    print(f"POPULATION: {len(rows)} artifact file(s) in {RESULTS} at git ref {ref}.")
    print("            Read out of git, not off disk, so this measures the merged state.")
    print("            A run is an artifact recording `parameters`; a summary aggregates other runs.")
    print()
    buckets: dict[str, list[str]] = {}
    for name, doc in rows:
        buckets.setdefault(classify(doc), []).append(name)
    order = ["clean", "summary", "legacy", "dirty", "no-provenance"]
    label = {
        "clean": "clean      driver matches HEAD, reproducible=true",
        "summary": "summary    aggregates other runs; provenance not applicable",
        "legacy": "LEGACY     no driver_matches_HEAD field: predates the fingerprint",
        "dirty": "DIRTY      driver_matches_HEAD=false: not reproducible from the repo",
        "no-provenance": "NO PROVENANCE BLOCK AT ALL",
    }
    for k in order:
        names = buckets.get(k, [])
        print(f"  {len(names):>3}  {label[k]}")
        for n in names:
            print(f"        {n}")
    runs = sum(len(buckets.get(k, [])) for k in ("clean", "legacy", "dirty", "no-provenance"))
    unverifiable = len(buckets.get("legacy", []))
    print()
    print(f"TOTAL: {len(rows)} artifacts = {runs} run(s) + "
          f"{len(buckets.get('summary', []))} summary/summaries.")
    print(f"  runs whose driver is fingerprinted and matches a commit : {len(buckets.get('clean', []))}")
    print(f"  runs that are NOT reproducible from the repository      : {len(buckets.get('dirty', []))}")
    print(f"  runs whose reproducibility cannot be checked            : {unverifiable}")
    if buckets.get("no-provenance"):
        print()
        print("FAIL: an artifact has no provenance block at all.")
        return 1
    if buckets.get("dirty"):
        print()
        print("FAIL: a shipped run was produced by a driver that matches no commit.")
        print("      Re-run it from a clean tree, or delete it. A DIRTY artifact is not evidence.")
        return 1
    if unverifiable:
        print()
        print(f"NOTE (not a failure): {unverifiable} run(s) predate the driver fingerprint, so their")
        print("      reproducibility cannot be checked either way. They are named above on purpose:")
        print("      any claim resting on one of them should say so. `reproducible` is computed as")
        print("      `driver_matches_HEAD is True` (experiments/provenance.py), so an absent field")
        print("      means the mechanism did not exist yet, not that the run was dirty.")
    print()
    print("PASS: every shipped run is either fingerprinted-and-clean or named as unverifiable.")
    return 0


def self_test() -> int:
    prov_ok = {"driver_matches_HEAD": True, "driver_dirty": False, "reproducible": True}
    cases = [
        ("a clean run", {"parameters": {}, "provenance": prov_ok}, "clean"),
        ("a summary that aggregates runs", {"provenance": prov_ok}, "summary"),
        ("a legacy run: field absent", {"parameters": {}, "provenance": {"git_commit": "abc"}}, "legacy"),
        ("a dirty run: the real defect", {"parameters": {}, "provenance": {"driver_matches_HEAD": False, "driver_dirty": True, "reproducible": False}}, "dirty"),
        ("no provenance block", {"parameters": {}}, "no-provenance"),
    ]
    print(f"POPULATION: {len(cases)} hand-built artifacts, each with its expected category.")
    print("  These are the FIVE distinct states the classifier must tell apart; collapsing any two of")
    print("  them is the bug this check exists to prevent (a DIRTY run read as LEGACY would pass).")
    fails = 0
    for name, doc, want in cases:
        got = classify(doc)
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {name:<38} -> {got:<15} (expected {want})")
        if not ok:
            fails += 1
    print()
    if fails:
        print(f"FAIL: {fails} case(s) misclassified")
        return 1
    print("PASS: all five categories distinguished, including DIRTY vs LEGACY")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    a = sys.argv[1:]
    ref = a[a.index("--ref") + 1] if "--ref" in a else "main"
    sys.exit(check(ref))
