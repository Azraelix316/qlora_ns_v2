"""Generate the scheme card: what the code does, with citations that are checked.

**Why this exists.** `paper/sections/04_methods.tex` and `05_experimental_setup.tex`
carry three open `PENDING-CODER` markers asking for the de-aliasing policy, the
exact rank rule and tolerances, the exact step order, and the projection
subspace. None of that was written down anywhere the writer could read it: it was
in the source, and in the artifact `parameters` blocks as *values* without
*meanings*. A writer reading the source for it is a writer who can and does get it
wrong -- which is how `fig:tg`'s caption came to promise a rank decay `3 -> 2 -> 1`
that a single Fourier mode cannot produce.

So the facts are stated here, and every one carries a `file:line` citation that
this script **verifies by reading the line**. A citation whose text no longer
matches is a hard error, not a stale pointer: the whole value of a card like this
is that it cannot drift, and a card that silently cites the wrong line is worse
than no card.

    python experiments/make_scheme_card.py

Output: ``state/coder/results/scheme_card.md`` and a JSON sibling carrying the same
content plus the provenance of the generator. The prose is the deliverable; the
citations are the mechanism.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "experiments") not in sys.path:
    sys.path.insert(0, str(ROOT / "experiments"))

RESULTS = ROOT / "state" / "coder" / "results"

# (section, [(label, file, line, text_that_must_appear_on_that_line)])
#
# The expected text is what makes the citation a check rather than a pointer. It
# is deliberately short and specific -- an identifier, not a sentence -- so that
# editing a comment does not invalidate it but moving or renaming the construct
# does.
CARD = [
    (
        "State variable and exact divergence-freeness",
        [
            ("the state is the real stream function, and the velocity is its curl",
             "solvers/ns_psi.py", 5, "u = (d_y psi, -d_x psi)"),
            ("so every state, including a truncated one, is divergence-free by "
             "construction -- this is structural, not a numerical accuracy claim",
             "solvers/ns_psi.py", 8, "zero divergence by construction"),
            ("all three methods call the same step kernel",
             "solvers/ns_psi.py", 11, "StreamFunctionNS.step"),
        ],
    ),
    (
        "De-aliasing policy",
        [
            ("rectangular 2/3 rule on the spectral mask",
             "solvers/spectral.py", 79, "Rectangular 2/3 dealiasing mask"),
            ("the cutoff is two thirds of the Nyquist wavenumber",
             "solvers/spectral.py", 80, "cutoff = (2.0 / 3.0) * (N // 2)"),
            ("the mask is applied to the advecting velocity",
             "solvers/ns_psi.py", 96, "q_hat *= grid.dealias_mask"),
        ],
    ),
    (
        "Time step: Strang split with an exact diffusion semigroup",
        [
            ("the step is documented as a Strang/midpoint split",
             "solvers/ns_psi.py", 132, "Strang/midpoint split step"),
            ("half a diffusion step first",
             "solvers/ns_psi.py", 143, "self.diffuse(state, 0.5 * dt)"),
            ("the advection-plus-forcing term is explicit midpoint",
             "solvers/ns_psi.py", 155, "state + 0.5 * dt * y0"),
            ("the nonlinear term is re-evaluated at the midpoint",
             "solvers/ns_psi.py", 164, "nonlinear_forcing(midpoint, t + 0.5 * dt)"),
            ("then the full step and a final half diffusion step",
             "solvers/ns_psi.py", 165, "state = state + dt * ymid"),
        ],
    ),
    (
        "Projection: four points per step, and what each one is for",
        [
            ("after the first diffusion half-step",
             "solvers/ns_psi.py", 148, "after_diffusion_half"),
            ("at the explicit midpoint",
             "solvers/ns_psi.py", 159, "after_midpoint"),
            ("after the nonlinear term, which is where rank growth is detected",
             "solvers/ns_psi.py", 169, "after_nonlinear"),
            ("after the final diffusion half-step",
             "solvers/ns_psi.py", 179, "after_diffusion_half_final"),
            ("the count is four when a projector is supplied and zero otherwise",
             "solvers/ns_psi.py", 187, "projection_count"),
        ],
    ),
    (
        "Rank rule and the spectrum it reads",
        [
            ("the amplitude criterion counts modes above a relative threshold",
             "solvers/dlra.py", 317,
             "count_nonzero(s > self.relative_amplitude_cutoff * s[0])"),
            ("the retained rank is clipped to the configured bounds",
             "solvers/dlra.py", 282, "def _target_from_spectrum"),
            ("the rule normally reads the projection's own singular values",
             "solvers/dlra.py", 214, "def _rank_spectrum"),
            ("with rank_basis='fluctuations' the zonal mode is removed first, so "
             "the rule reads a different spectrum -- which quantity a rule reads is "
             "part of what it means",
             "solvers/dlra.py", 226, "zonal_mean(field)"),
        ],
    ),
    (
        "When the rank and the basis are recomputed",
        [
            ("adaptation is gated on a step counter, not on every step",
             "solvers/dlra.py", 506, "self.steps % self.check_every == 0"),
            ("the candidate read is the UNPROJECTED post-nonlinear state, so modes "
             "lost at the stage projection can still trigger growth",
             "solvers/dlra.py", 507, 'candidate("after_nonlinear")'),
            ("the same gate refreshes the basis as well as the rank -- it is not a "
             "rank-only switch",
             "solvers/dlra.py", 514, "self.basis_builds += 1"),
        ],
    ),
]


def verify() -> list[str]:
    """Check every citation by reading the line. Returns the problems found."""
    problems: list[str] = []
    for section, entries in CARD:
        for label, rel, line_no, expected in entries:
            path = ROOT / rel
            if not path.exists():
                problems.append(f"{rel} does not exist (cited by {label!r})")
                continue
            lines = path.read_text().splitlines()
            if not 1 <= line_no <= len(lines):
                problems.append(
                    f"{rel}:{line_no} is cited by {label!r} but the file has "
                    f"{len(lines)} lines"
                )
                continue
            text = lines[line_no - 1]
            if expected not in text:
                problems.append(
                    f"{rel}:{line_no} does not contain {expected!r}\n"
                    f"    cited by: {label}\n"
                    f"    line reads: {text.strip()[:100]}"
                )
    return problems


def render() -> str:
    out = [
        "# Scheme card — what the code does, with checked citations",
        "",
        "GENERATED by `experiments/make_scheme_card.py`. Do not edit: every "
        "`file:line` below is verified by reading that line, so this document "
        "cannot cite code it does not describe. Each entry answers a "
        "`PENDING-CODER` marker in `paper/sections/04_methods.tex` or "
        "`05_experimental_setup.tex`.",
        "",
        "The values used for the runs are in each artifact's `parameters` block; "
        "this card says what those values *mean* and where the behaviour lives.",
        "",
    ]
    for section, entries in CARD:
        out.append(f"## {section}")
        out.append("")
        for label, rel, line_no, _ in entries:
            out.append(f"- {label}  \n  `{rel}:{line_no}`")
        out.append("")
    out.append("## What this card deliberately does not say")
    out.append("")
    out.append(
        "- **No claim that the rank rule is optimal.** It is a threshold on a "
        "singular spectrum, and the threshold is a configuration, not a result."
    )
    out.append(
        "- **No mode count.** The de-aliasing cutoff bounds a *wavenumber*. The "
        "resolved band carries far more degrees of freedom than that number "
        "(1849 at N=64), so expressing a rank as a multiple of the cutoff is "
        "meaningless (D30.2)."
    )
    out.append(
        "- **No conservation claim for the reduced integrator.** It violates the "
        "full PDE's energy balance by the price of the projection, which is a "
        "different statement from the balance it does satisfy; the artifact's "
        "`energy_residual_semantics` block says which is which."
    )
    out.append("")
    return "\n".join(out)


def main() -> int:
    # `--check` verifies without writing. A test that regenerates the artifact in
    # place leaves the working tree dirty, and a dirty tree is how this project
    # detects contamination -- so a test that dirties it destroys the signal it is
    # meant to preserve.
    #
    # Parsed with argparse rather than by scanning `sys.argv`, which is the point:
    # this script previously read `"--check" in sys.argv` and **ignored every
    # other flag**, so `make_scheme_card.py --help` regenerated the card instead of
    # printing help. `test_every_driver_can_print_its_own_help` runs `--help` on
    # every driver, so the suite was silently rewriting this artifact on every run
    # and no amount of `--check` in the tests could stop it. **Third instance of
    # this pattern today** -- `check_driver_flags.py --help` exited 1, and this one
    # did the work it was asked not to do -- which is why it is named here.
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--check", action="store_true",
        help=(
            "verify the committed card against the code and write nothing; exit 1 "
            "if it is stale. Compares the card's CONTENT, not its provenance block, "
            "so a card written by this commit does not report itself stale."
        ),
    )
    args = parser.parse_args()
    check_only = args.check

    problems = verify()
    if problems:
        print("SCHEME CARD — CITATION CHECK FAILED\n")
        for problem in problems:
            print(f"  - {problem}")
        print(
            "\n  The card is not written. A card whose citations no longer "
            "resolve is worse than no card, because a writer cannot tell which "
            "parts to trust."
        )
        return 1

    n = sum(len(entries) for _, entries in CARD)
    RESULTS.mkdir(parents=True, exist_ok=True)
    markdown = render()
    md_path = RESULTS / "scheme_card.md"
    if check_only and not md_path.exists():
        print("scheme_card.md is absent; run without --check to write it")
        return 1

    from provenance import provenance

    payload = {
        "case": "scheme_card",
        "sections": [
            {
                "title": title,
                "facts": [
                    {"claim": label, "citation": f"{rel}:{line}", "expect": expected}
                    for label, rel, line, expected in entries
                ],
            }
            for title, entries in CARD
        ],
        "citations_verified": n,
        "provenance": provenance(ROOT / "experiments" / "make_scheme_card.py"),
    }
    serialised = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    json_path = RESULTS / "scheme_card.json"
    if check_only:
        # Compare the CONTENT, not the provenance. This first version compared the
        # serialised JSON including its `provenance` block, and so reported STALE
        # against a card it had just written -- because the block records the
        # commit and the working-tree hash at generation time, and rewriting the
        # card changes both. A check that can never be green is a check nobody
        # reads. The question here is "is the card current with the code", and the
        # provenance answers a different one.
        stale = []
        if md_path.read_text() != markdown:
            stale.append("scheme_card.md")
        if not json_path.exists():
            stale.append("scheme_card.json")
        else:
            on_disk = json.loads(json_path.read_text())
            for key in ("sections", "citations_verified", "case"):
                if on_disk.get(key) != payload.get(key):
                    stale.append(f"scheme_card.json:{key}")
        if stale:
            print("SCHEME CARD — STALE: " + ", ".join(stale))
            print("  Run without --check to regenerate. The card is a deliverable the")
            print("  writer reads, so a stale one is worse than a missing citation.")
            return 1
        print(f"SCHEME CARD — current: {len(CARD)} sections, {n} citations, "
              "all verified, content matches")
        return 0
    md_path.write_text(markdown)
    json_path.write_text(serialised)
    print(f"SCHEME CARD — {len(CARD)} sections, {n} citations, all verified")
    print(f"  wrote {md_path}")
    print(f"  wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
