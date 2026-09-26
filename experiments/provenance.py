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

**Captured at launch, not at write.**  This was wrong until 2026-09-26 and the
error is worth stating, because it made the central field vacuous.

The first version read ``HEAD`` and hashed the driver *at the moment the artifact
was written*.  For a run that outlasts a commit those two are read together, so
``driver_matches_HEAD`` compared the driver against itself and read ``true``.  It
was demonstrated, not argued: a crossover run started at 07:40, a commit landed at
07:45, the artifact was written at 08:24 and recorded

    driver_sha256  98b3d61b2496d313   (the file at 08:24)
    actually ran   4b2ca8f8bb0bc599   (the file as loaded at 07:40)
    driver_matches_HEAD   true
    reproducible           true

Both verdicts were wrong, and the note claimed "git_commit is HEAD at launch" --
so the *intent* was right and the implementation had drifted away from it, which
is the same failure as everywhere else this cycle: a true sentence about the
design, and code that did something else.

The fix needs no driver changes.  At import -- process start, which is when the
code is loaded -- this module snapshots the SHA-256 of every ``.py`` under
``experiments/`` and ``solvers/``, and records the wall-clock time.  Then:

* ``git_commit`` is the commit that was HEAD *at that time*, found with
  ``git log -1 --before=<launch>``;
* ``driver_sha256`` is the driver as it was at launch, from the snapshot;
* ``driver_matches_HEAD`` compares that against the driver **in that commit**.

Write-time state is still recorded, under its own names, because a reader
comparing the two learns something useful: if the tree moved during the run, that
is a fact about the run, not a reason to discard the launch-time verdict.
"""
from __future__ import annotations

import hashlib
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: Wall-clock time at import, i.e. when this process loaded its code.  Everything
#: below is anchored to it, because a long run is exactly the case that broke the
#: write-time version.
LAUNCH_TIME_UNIX = time.time()


def _rel(path: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def _snapshot_sources() -> dict[str, str]:
    """SHA-256 of every Python file in the code directories, at import time.

    Taken over the whole tree rather than just the driver because the interesting
    failure is not always in the file named as the driver: a helper in
    ``solvers/`` can change the numbers just as effectively.
    """
    shas: dict[str, str] = {}
    for sub in ("experiments", "solvers"):
        directory = ROOT / sub
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.py")):
            try:
                shas[_rel(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError:
                continue
    return shas


#: Populated once, at import, and never refreshed.  A later reader of this
#: module inside a running process must not be able to see a newer tree.
LAUNCH_SOURCE_SHAS: dict[str, str] = _snapshot_sources()


def _git(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        )
    except (OSError, subprocess.CalledProcessError):
        return None


def _commit_at(moment: float) -> tuple[str, str]:
    """The commit that was HEAD at ``moment``, and how it was obtained."""
    head = (_git("rev-parse", "HEAD") or "").strip()
    found = (
        _git("log", "-1", "--format=%H", f"--before={moment:.0f}") or ""
    ).strip()
    if found:
        return found, f"git log -1 --before={moment:.0f}"
    return head or "unknown", "git rev-parse HEAD (no commit predates the launch)"


def sources_fingerprint() -> str:
    """One hash over the whole code tree as it was at launch."""
    blob = "\n".join(f"{k} {v}" for k, v in sorted(LAUNCH_SOURCE_SHAS.items()))
    return hashlib.sha256(blob.encode()).hexdigest()


def provenance(driver: Path) -> dict:
    """Record the launch-time commit and driver hash, and whether that is committed.

    Both the launch-time and the write-time facts are recorded, under names that
    say which is which.  ``driver_matches_HEAD`` is the launch-time verdict and is
    what ``reproducible`` follows; ``*_at_write`` is informational.
    """
    commit, how = _commit_at(LAUNCH_TIME_UNIX)
    out: dict = {
        "git_commit": commit,
        "git_commit_how": how,
        "captured_at": "launch",
    }

    try:
        rel = _rel(Path(driver))
    except Exception:                                       # pragma: no cover
        rel = str(driver)
    out["driver"] = rel

    # The driver as it was when the process loaded it, which is what ran.
    launch_sha = LAUNCH_SOURCE_SHAS.get(rel)
    if launch_sha is None and Path(driver).exists():
        launch_sha = hashlib.sha256(Path(driver).read_bytes()).hexdigest()
        out["driver_sha256_source"] = (
            "read from disk: the driver is outside experiments/ and solvers/, so "
            "the launch snapshot did not cover it, and this may be a later edit"
        )
    if launch_sha is not None:
        out["driver_sha256"] = launch_sha
        committed = subprocess.run(
            ["git", "show", f"{commit}:{rel}"], cwd=ROOT, capture_output=True,
        )
        if committed.returncode == 0:
            out["driver_matches_HEAD"] = (
                hashlib.sha256(committed.stdout).hexdigest() == launch_sha
            )
        else:
            # The driver is not in that commit at all: new and uncommitted.  That
            # is the worst case for reproducibility and must not read as
            # "unknown".
            out["driver_matches_HEAD"] = False
            out["driver_matches_HEAD_note"] = (
                f"{rel} is not in {commit[:8]}: new or uncommitted at launch"
            )
    else:
        out["driver_matches_HEAD"] = False
        out["driver_matches_HEAD_note"] = f"{rel} was not readable at launch"

    out["sources_fingerprint_at_launch"] = sources_fingerprint()
    out["sources_files_at_launch"] = len(LAUNCH_SOURCE_SHAS)

    # --- write-time state, kept separate and clearly named -------------------
    write_commit = (_git("rev-parse", "HEAD") or "unknown").strip()
    out["git_commit_at_write"] = write_commit
    out["tree_moved_during_run"] = write_commit != commit
    diff = _git("diff", "HEAD")
    out["working_tree_dirty"] = bool(diff and diff.strip())
    if diff and diff.strip():
        out["working_tree_diff_sha256"] = hashlib.sha256(diff.encode()).hexdigest()
    out["working_tree_dirty_paths"] = [
        line for line in ((_git("diff", "--name-only", "HEAD") or "").splitlines())
        if line.strip()
    ]
    if Path(driver).exists():
        out["driver_dirty"] = bool((_git("diff", "HEAD", "--", rel) or "").strip())
        out["driver_sha256_at_write"] = hashlib.sha256(
            Path(driver).read_bytes()
        ).hexdigest()
        out["driver_matches_HEAD_at_write"] = (
            out["driver_sha256_at_write"] == launch_sha
        )

    out["reproducible"] = out.get("driver_matches_HEAD") is True
    out["note"] = (
        "git_commit, driver_sha256 and driver_matches_HEAD are all captured at "
        "LAUNCH -- the commit that was HEAD when the process loaded its code, "
        "and the driver as it was then. driver_matches_HEAD compares that hash "
        "against the driver in that commit, and is what reproducible follows. "
        "An earlier version read HEAD and hashed the driver when the artifact was "
        "WRITTEN; for any run that outlasts a commit those were read together and "
        "the check compared the driver against itself, reporting true while the "
        "artifact recorded a driver the run never used. *_at_write and "
        "tree_moved_during_run are informational: a tree that moved during a run "
        "is a fact about the run, not a reason to discard the launch verdict. "
        "working_tree_dirty is recorded too, but a rewritten result file alone "
        "does not invalidate a run."
    )
    return out
