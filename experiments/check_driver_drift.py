"""Classify driver drift: did the numbers' provenance go stale, or only the parser?

`provenance.py` records a `driver_sha256` and decides `driver_matches_HEAD` by
comparing the driver on disk with the one in the recorded `git_commit`. That is
the right check, and it is deliberately unforgiving: any edit to a driver makes
every artifact it produced non-reproducible until re-run.

But "non-reproducible" currently conflates two very different situations:

* the driver's **computation** changed, so the recorded numbers may no longer be
  what the code produces -- and the artifact must be re-run; and
* only the **command-line wiring** changed, so the computation is byte-identical
  and the numbers are exactly what the current code produces.

The second case is real and common. On 2026-09-26 every list-valued flag in
every driver gained ``action=ListOnce`` (see ``_cli.py``) so that a repeated flag
fails loudly instead of silently running half the parameter space. That touched
seven drivers and so invalidated the recorded provenance of every artifact they
produced -- including runs costing hours -- while changing no arithmetic
whatsoever.

This does not decide which case applies, and it does not excuse anything: it
reports the diff and labels it, so the decision to re-run is made with the
evidence in front of it rather than from a boolean.

    python experiments/check_driver_drift.py [--results state/coder/results]

A line is treated as *wiring* if it is an ``add_argument`` call, the ``ListOnce``
import, or the action class itself. Everything else counts as *substantive*, and
a single substantive line is enough to make an artifact's numbers suspect.
"""
from __future__ import annotations

import argparse
import ast
import difflib
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

WIRING_MARKERS = (
    "add_argument",
    "ListOnce",
    "from _cli import",
    "argparse.Action",
)


def _strip_wiring(tree: ast.AST) -> ast.AST:
    """Remove exactly the ``ListOnce`` wiring, leaving the computation intact.

    A *line-based* comparison is the obvious implementation and it is wrong:
    adding ``action=ListOnce`` to a call that already spanned two lines pushes its
    ``default=`` onto a continuation line, so a text diff reports
    ``+ default=[64, 128])`` as a changed line and the classifier calls a pure
    wiring change "substantive".  Thirteen of twenty artifacts were mislabelled
    that way before this was replaced.  Comparing parsed structure cannot have
    that failure: the continuation lines are not nodes, and an edit that changed
    a default, a formula or a loop bound shows up as a different tree.

    Two things are removed and nothing else: the ``from _cli import ListOnce``
    statement, and any ``action=ListOnce`` keyword on an ``add_argument`` call.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "add_argument":
            node.keywords = [
                kw for kw in node.keywords
                if not (kw.arg == "action" and isinstance(kw.value, ast.Name)
                        and kw.value.id == "ListOnce")
            ]
    body = getattr(tree, "body", [])
    tree.body = [
        stmt for stmt in body
        if not (isinstance(stmt, ast.ImportFrom) and stmt.module == "_cli"
                and any(a.name == "ListOnce" for a in stmt.names))
    ]
    return tree


def _diff_summary(old: str, new: str) -> str:
    diff = [
        ln for ln in difflib.unified_diff(
            old.splitlines(), new.splitlines(), lineterm="", n=0
        )
        if ln[:1] in "+-" and not ln.startswith(("+++", "---"))
    ]
    return f"{len(diff)} line(s) differ textually"


def driver_at(ref: str, path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True, text=True
    )
    return result.stdout if result.returncode == 0 else None


def classify(rec: dict, path: str) -> tuple[str, str, str]:
    """Return (state, detail, driver_path) for one artifact's provenance."""
    recorded = rec.get("driver_sha256")
    commit = rec.get("git_commit")
    if not recorded or not commit:
        return "unverifiable", "no driver_sha256 or git_commit recorded", path
    if not path or not (ROOT / path).exists():
        return "driver-missing", f"{path} does not exist on disk", path
    current = (ROOT / path).read_text()
    now = hashlib.sha256(current.encode()).hexdigest()
    if now == recorded:
        return "current", "driver on disk matches the recorded sha256", path
    old = driver_at(commit, path)
    if old is None:
        return "unverifiable", (
            f"{path} is not in {commit[:8]}, so the recorded run cannot be compared"
        ), path
    old_sha = hashlib.sha256(old.encode()).hexdigest()
    if old_sha != recorded:
        return "unverifiable", (
            f"{path} at {commit[:8]} hashes to {old_sha[:12]}, not the recorded "
            f"{recorded[:12]}: the recorded commit is not the one that ran"
        ), path

    # Semantic comparison: identical once the ListOnce wiring is removed from the
    # current version means the computation is byte-identical.
    try:
        old_tree = ast.dump(ast.parse(old))
        new_tree = ast.dump(_strip_wiring(ast.parse(current)))
    except SyntaxError as exc:
        return "unverifiable", f"{path} does not parse: {exc}", path
    if old_tree == new_tree:
        return "wiring-only", (
            f"{_diff_summary(old, current)}, and the parsed structure is "
            "IDENTICAL once action=ListOnce and its import are removed: the "
            "computation is unchanged"
        ), path

    # Not identical: name something concrete rather than a line count.
    old_names = {n.name for n in ast.walk(ast.parse(old))
                 if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    new_names = {n.name for n in ast.walk(ast.parse(current))
                 if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    added, removed = sorted(new_names - old_names), sorted(old_names - new_names)
    what = []
    if added:
        what.append(f"added {', '.join(added[:3])}")
    if removed:
        what.append(f"removed {', '.join(removed[:3])}")
    if not what:
        changed = sorted(
            n.name for n in ast.walk(ast.parse(current))
            if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in old_names
            and ast.dump(n) != ast.dump(
                next(m for m in ast.walk(ast.parse(old))
                     if isinstance(m, (ast.FunctionDef, ast.ClassDef))
                     and getattr(m, "name", None) == n.name))
        )
        what.append(f"changed body of {', '.join(changed[:3])}" if changed
                    else "changed module-level code")
    return "substantive", (
        _diff_summary(old, current) + "; the parsed structure differs beyond the "
        "wiring: " + "; ".join(what)
    ), path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path,
                        default=ROOT / "state" / "coder" / "results")
    args = parser.parse_args()

    rows = []
    for artifact in sorted(args.results.glob("*.json")):
        try:
            data = json.loads(artifact.read_text())
        except json.JSONDecodeError as exc:
            print(f"  {artifact.name}: unreadable ({exc})")
            continue
        rec = data.get("provenance")
        if not isinstance(rec, dict):
            continue
        state, detail, path = classify(rec, rec.get("driver", ""))
        rows.append((state, artifact.name, path, detail))

    order = {"substantive": 0, "wiring-only": 1, "unverifiable": 2,
             "driver-missing": 3, "current": 4}
    rows.sort(key=lambda r: (order[r[0]], r[1]))

    print("DRIVER DRIFT — whether a recorded artifact's numbers are in question\n")
    print(f"  artifacts with provenance: {len(rows)}")
    print()
    width = max((len(n) for _, n, _, _ in rows), default=10)
    for state, name, path, detail in rows:
        print(f"  {state:<15} {name:<{width}}  {path}")
        print(f"  {'':<15} {'':.<{width}}  {detail}")
    print()
    counts: dict[str, int] = {}
    for state, *_ in rows:
        counts[state] = counts.get(state, 0) + 1
    for state in ("substantive", "wiring-only", "unverifiable", "driver-missing",
                  "current"):
        if counts.get(state):
            print(f"  {counts[state]:>3}  {state}")
    print()
    if counts.get("substantive"):
        print("  SUBSTANTIVE drift: the recorded numbers may no longer be what the")
        print("  code produces. Those artifacts need re-running before their")
        print("  provenance can be called reproducible.")
    if counts.get("wiring-only"):
        print("  WIRING-ONLY drift: the computation is unchanged, so the numbers")
        print("  still are what the current code produces. Whether that is")
        print("  acceptable without a re-run is a decision, not a measurement --")
        print("  this reports the evidence and does not make the call.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
