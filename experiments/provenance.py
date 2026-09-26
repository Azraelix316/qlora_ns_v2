"""Provenance that says whether the code that ran is the code that is committed.

One place, because this is the check D14.4 makes load-bearing and three copies
of it would drift.  The distinction it draws is between two things that are
routinely confused:

* a dirty **tree** -- a run rewrites its own result file, so the *next* run
  starts on a dirty tree without any code having changed.  That is routine.
* a dirty **driver** -- uncommitted edits to the file doing the measuring.  That
  is what invalidates the numbers, because the artifact names a commit that does
  not contain the code that produced it.

So the driver records its own SHA-256 and whether that hash equals the committed
file at the named commit.  A reader can check the hash directly and does not have
to trust a boolean, and a boolean that would otherwise flip for a harmless reason
is not the thing being relied on.
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _git(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        )
    except (OSError, subprocess.CalledProcessError):
        return None


def provenance(driver: Path) -> dict:
    """Record the commit, the driver's hash, and whether that hash is committed."""
    commit = (_git("rev-parse", "HEAD") or "unknown").strip()
    out: dict = {"git_commit": commit}

    diff = _git("diff", "HEAD")
    out["working_tree_dirty"] = bool(diff and diff.strip())
    if diff and diff.strip():
        out["working_tree_diff_sha256"] = hashlib.sha256(diff.encode()).hexdigest()
    # WHICH paths were dirty, not only that something was.  The module's own note
    # exempts "a rewritten result file alone", which implies a rewritten *source*
    # file would not be exempt -- and with only a boolean and a hash a reader
    # cannot tell those two cases apart, so the exemption is unclaimable by
    # anyone reading the artifact.  The path list is also what lets a later
    # reader tell a benign re-run of a results file from real contamination
    # without re-deriving anything.
    out["working_tree_dirty_paths"] = [
        line for line in ((_git("diff", "--name-only", "HEAD") or "").splitlines())
        if line.strip()
    ]

    try:
        rel = str(Path(driver).resolve().relative_to(ROOT))
    except ValueError:
        rel = str(driver)
    if Path(driver).exists():
        out["driver"] = rel
        out["driver_sha256"] = hashlib.sha256(
            Path(driver).read_bytes()
        ).hexdigest()
        out["driver_dirty"] = bool((_git("diff", "HEAD", "--", rel) or "").strip())
        committed = subprocess.run(
            ["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True,
        )
        if committed.returncode == 0:
            out["driver_matches_HEAD"] = (
                hashlib.sha256(committed.stdout).hexdigest()
                == out["driver_sha256"]
            )
        else:
            # The driver is not in HEAD at all: new and uncommitted.  That is the
            # worst case for reproducibility and must not read as "unknown".
            out["driver_matches_HEAD"] = False
    out["reproducible"] = out.get("driver_matches_HEAD") is True
    out["note"] = (
        "git_commit is HEAD at launch. driver_matches_HEAD compares the driver "
        "file on disk with the one in that commit, and is the check that decides "
        "reproducibility; working_tree_dirty is recorded too, but a rewritten "
        "result file alone does not invalidate a run."
    )
    return out
