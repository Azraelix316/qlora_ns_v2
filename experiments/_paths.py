"""Paths and the canonical suite configuration, shared by the results-layer tests.

The reproduction test needs to re-run *exactly* the configuration the committed
artifact records, and the way to guarantee that is to use the same argument list
the project's own documentation and drivers use, rather than a second copy that
can drift from the first. A second copy of a parameter list is a second thing to
keep correct, and this one would silently make the reproduction test vacuous --
re-running something *near* the committed configuration and calling the agreement
reproducibility.

So the canonical arguments live here, once, and anything that needs to reproduce
the suite uses them.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = REPO_ROOT / "experiments"
RESULTS = REPO_ROOT / "state" / "coder" / "results"

#: The canonical suite configuration (P0). The IC fingerprint these produce is
#: ``ebcef128e52e73f7...`` with energy 22.206703312933374 and numerical rank 17.
CANONICAL_ARGS = [
    "--re", "5000",
    "--N", "64",
    "--dt", "0.0005",
    "--steps", "200",
    "--force-amplitude", "0.5",
    "--base-speed", "0.5",
    "--perturbation-velocity-rms", "1.0",
    "--cutoff", "8",
    "--seed", "20260925",
    "--train-steps", "100",
    "--snapshot-stride", "5",
    "--compare-stride", "20",
    "--pod-rank", "16",
    "--dlra-rank", "2",
    "--dlra-min-rank", "2",
    "--dlra-relative-amplitude-cutoff", "1e-10",
    "--dlra-check-every", "5",
]
