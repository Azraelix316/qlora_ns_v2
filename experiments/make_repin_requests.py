"""Generate the registry re-pin requests from the gate's own output.

**Why.** Twelve `claims_registry.py` rows fail for reasons that are settled and
documented, and every one of them needs a number changed in a file I do not own.
As prose in an outbox message those twelve numbers have to be transcribed by hand
into `state/reviewer/claims_registry.py`, and a transcription of twelve
sixteen-significant-figure values is exactly the step where a digit is lost
quietly.

So the list is generated, and — the part that makes it worth having — it is
generated **by running the gate**, not from memory. A row that stops failing
disappears from the list, and a row that starts failing appears in it. A
hand-maintained list of things to re-pin would be stale the moment the gate moved,
and a stale list that claims to be complete is worse than no list.

What this deliberately does NOT do: decide any re-pin. Each entry carries the
measured value, the value the row currently holds, the relative change, and why
they differ. Whether a row should be re-pinned, given a tolerance, or replaced by
a claim about a distribution is the reviewer's decision — D55c.6 puts the verdict
with the reviewer, and this only removes the transcription.

    python experiments/make_repin_requests.py [--registry path] [--reg-ref ref]

Output: ``state/coder/results/repin_requests.json``.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "state" / "coder" / "results"
OUT = RESULTS / "repin_requests.json"

DEFAULT_REGISTRY = "state/reviewer/claims_registry.py"
DEFAULT_REF = "origin/agent/reviewer"
DEFAULT_DRAFT = "origin/agent/writer"

#: Why each failing group differs, keyed by the row-id prefix. A row with no entry
#: here is reported with `reason: null` rather than being dropped -- an
#: unexplained failure is still a failure, and hiding it would make this file look
#: like a closed list when it is not.
REASONS = {
    "tstar_": (
        "the recorded value came from the crossover BLOCK, which computed its own "
        "crossing; the block sat 3.9-9.3% BELOW the rows in all 18 resolved cases "
        "across both Reynolds numbers, so the rows-derived value is the one to pin. "
        "t_star_from_rows() now reads the crossing off the rows and "
        "t_star_legacy is kept beside it so the gap stays measurable."
    ),
    "zonal_share_energy_": (
        "NOT A VALUE PROBLEM: the row passes a dotted path as `field`, and "
        "resolve() looks a plain `field` up as a LITERAL key, descending only "
        "inside the @min:/@max: form. The artifacts have always been nested, so "
        "these rows have never resolved against any version of the data. Confirmed "
        "against the pre-change artifacts. Either descend on '.' generally, or "
        "point the rows at zonal_energy_fraction_fluctuation / "
        "zonal_energy_fraction_components, which would also let a row check the "
        "value AND its definition."
    ),
    "mem_noise_floor_mib": (
        "the row is pinned at 0.09765625 MiB, one of FOUR single-sample values this "
        "quantity has taken (0.1328 / 0.0664 / 0.0977 / 0.0039 -- a factor of 34). "
        "bench_memory.py now measures every configuration five times and the floor "
        "is the MAXIMUM of 92 same-configuration differences by construction, so no "
        "correct measurement can equal 0.0977. The row needs a tolerance, or "
        "replacing by a claim about the distribution."
    ),
    "mem_overhead_": (
        "the row is pinned at eight significant figures on a quantity that is now "
        "recorded as a distribution with min/median/max and a spread. Across three "
        "independent measurements the projected integrator's N=64 overhead moved by "
        "+136%, so a point at sf=8 cannot be satisfied. The artifact carries the "
        "median and the spread to pin against instead."
    ),
    "mem_rank_resolved_": (
        "a boolean claim under D89: the row asserts the flag is False, and the "
        "current measurement is consistent with that. Listed here only if it fails; "
        "if it does, the rank-variation guidance is what needs revisiting, not the "
        "number."
    ),
    "cost_ratio_": (
        "a cost ratio on this node is not reproducible to better than about 15%: at "
        "a FIXED thread count the N=128 max ratio has ranged 2.14-2.74 (28%) across "
        "five committed versions of the same configuration, and the thread count "
        "alone moves it 43% (2.57 at one thread, 3.54 at two). The within-run spread "
        "over 7 interleaved repeats is only 0.17-0.35. The row needs a stated "
        "tolerance and a thread count, not a point."
    ),
}


def reason_for(row_id: str) -> str | None:
    for prefix, text in REASONS.items():
        if row_id.startswith(prefix.rstrip("_")) or row_id.startswith(prefix):
            return text
    return None


def run_gate(registry: Path, draft_ref: str) -> tuple[str, str | None]:
    """Run the reviewer's registry against a scratch tree. Returns (stdout, root)."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "root"
        (root / "state" / "coder" / "results").mkdir(parents=True)
        (root / "state" / "reviewer").mkdir(parents=True)
        for artifact in RESULTS.glob("*.json"):
            (root / "state" / "coder" / "results" / artifact.name).symlink_to(artifact)
        (root / "state" / "reviewer" / registry.name).write_text(registry.read_text())
        subprocess.run(["git", "init", "-q", "."], cwd=root, capture_output=True)

        draft = Path(tmp) / "draft"
        draft.mkdir()
        names = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", draft_ref, "--", "paper/sections"],
            cwd=ROOT, capture_output=True, text=True,
        ).stdout.split()
        for name in names:
            if not name.endswith(".tex"):
                continue
            blob = subprocess.run(
                ["git", "show", f"{draft_ref}:{name}"], cwd=ROOT,
                capture_output=True, text=True,
            ).stdout
            (draft / Path(name).name).write_text(blob)

        result = subprocess.run(
            [sys.executable, str(root / "state" / "reviewer" / registry.name),
             str(root), str(draft)],
            cwd=ROOT, capture_output=True, text=True, timeout=1800,
        )
        return result.stdout, str(root)


def parse_failures(stdout: str) -> list[dict]:
    """Pull the FAIL lines into structured records.

    The gate's line format is the contract here, so a format change shows up as an
    empty list rather than as a silently short re-pin list -- and the assertion
    below turns that into a loud failure.
    """
    out = []
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped.startswith("FAIL "):
            continue
        parts = stripped.split(None, 2)
        if len(parts) < 2:
            continue
        row_id = parts[1]
        rest = parts[2] if len(parts) > 2 else ""
        measured = current = None
        if "artifact" in rest and "!=" in rest:
            left, _, right = rest.partition("!=")
            try:
                measured = float(left.replace("artifact", "").strip())
            except ValueError:
                measured = left.replace("artifact", "").strip() or None
            current = right.split("[")[0].strip()
            try:
                current = float(current)
            except ValueError:
                pass
        out.append({
            "row": row_id,
            "measured": measured,
            "registry_holds": current,
            "reason": reason_for(row_id),
        })
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=None)
    parser.add_argument("--reg-ref", default=DEFAULT_REF)
    parser.add_argument("--draft-ref", default=DEFAULT_DRAFT)
    args = parser.parse_args()

    if args.registry:
        registry = args.registry
    else:
        blob = subprocess.run(
            ["git", "show", f"{args.reg_ref}:{DEFAULT_REGISTRY}"],
            cwd=ROOT, capture_output=True, text=True,
        )
        if blob.returncode != 0:
            print(f"cannot read {DEFAULT_REGISTRY} at {args.reg_ref}")
            return 2
        registry = Path(tempfile.mkdtemp()) / "claims_registry.py"
        registry.write_text(blob.stdout)

    stdout, _ = run_gate(registry, args.draft_ref)
    failures = parse_failures(stdout)

    if not failures:
        print("RE-PIN REQUESTS — the registry reported no failures, so there is")
        print("nothing to re-pin. If that is unexpected, the gate's output format")
        print("has probably changed and the parser needs updating; an empty list")
        print("must never be read as 'nothing outstanding'.")
        return 1

    unexplained = [f["row"] for f in failures if not f["reason"]]
    payload = {
        "case": "repin_requests",
        "generated_from": {
            "registry": DEFAULT_REGISTRY,
            "registry_ref": args.reg_ref,
            "draft_ref": args.draft_ref,
        },
        "rows": failures,
        "rows_total": len(failures),
        "rows_with_a_stated_reason": len(failures) - len(unexplained),
        "rows_without_a_stated_reason": unexplained,
        "what_this_is_not": (
            "a decision. Whether a row is re-pinned, given a tolerance, or replaced "
            "by a claim about a distribution is the reviewer's call (D55c.6). This "
            "exists so that twelve sixteen-significant-figure values are not "
            "transcribed by hand from prose into a file I do not own."
        ),
        "regenerate_with": "python experiments/make_repin_requests.py",
    }
    try:
        sys.path.insert(0, str(ROOT / "experiments"))
        from provenance import provenance
        payload["provenance"] = provenance(
            ROOT / "experiments" / "make_repin_requests.py"
        )
    except Exception as exc:                          # pragma: no cover
        payload["provenance_error"] = f"{type(exc).__name__}: {exc}"

    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    print("RE-PIN REQUESTS — generated from the gate's own output\n")
    print(f"  registry : {DEFAULT_REGISTRY} @ {args.reg_ref}")
    print(f"  draft    : {args.draft_ref}")
    print(f"  rows     : {len(failures)} failing, "
          f"{len(failures) - len(unexplained)} with a stated reason")
    print()
    for f in failures:
        measured = f["measured"]
        held = f["registry_holds"]
        rel = ""
        if isinstance(measured, float) and isinstance(held, (int, float)) and held:
            rel = f"  ({100 * (measured / held - 1):+.2f}%)"
        print(f"  {f['row']:<28} measured {measured}  row holds {held}{rel}")
        print(f"  {'':<28} {'reason stated' if f['reason'] else 'NO REASON STATED'}")
    if unexplained:
        print(f"\n  !! {len(unexplained)} row(s) with no stated reason: {unexplained}")
        print("     They are listed rather than dropped. An unexplained failure is")
        print("     still a failure, and a list that hid them would read as closed.")
    print(f"\n  wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
