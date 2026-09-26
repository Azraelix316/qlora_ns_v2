"""Argparse helpers that fail loudly instead of quietly dropping half a run.

**Why this exists.** On 2026-09-26 a launch script passed ``--re 5000 --re 1000``
to ``run_crossover.py``. ``--re`` is declared ``nargs="+"``, which means it takes
a *list of values*; it is not an accumulating flag. Argparse therefore kept the
**last** occurrence, the run covered Re=1000 only, and the driver wrote that
partial artifact **over a complete one** -- deleting the paper's central result
(the Re=5000 crossover surface) from the file, with nothing in the output to
say so. It was caught by a registry row failing with ``no key '5000'``, not by
the run itself.

The same shape had already cost an hour that day in a different form: a shell
script passed ``--dt`` once in a shared argument list and again per case, and
argparse kept the last, so one case ran at twice its recorded timestep.

Seventeen list-valued flags across eight drivers had this property. Fixing the
one instance would have left sixteen, so this module makes the whole class loud:

    parser.add_argument("--re", nargs="+", type=float, action=ListOnce, ...)

``ListOnce`` refuses a second occurrence and says what the right form is. The
alternative -- quietly accepting it -- is the failure mode: a run that covers
half its parameter space produces a complete-looking artifact, and nothing
downstream can tell the difference between "this configuration was requested" and
"this configuration survived".

The error is raised at parse time, so it costs no compute and cannot leave a
half-written artifact behind.
"""
from __future__ import annotations

import argparse

__all__ = ["ListOnce"]


class ListOnce(argparse.Action):
    """Accept a list-valued flag exactly once, and explain itself if given twice.

    ``nargs="+"`` consumes *values* after one flag, so a second occurrence
    replaces the first rather than extending it. That is almost never what
    someone means, and when it happens the run does not fail -- it just covers
    less than intended, which is the worst way for it to go wrong.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        flag = option_string or f"--{self.dest}"
        seen = getattr(namespace, "_list_once_seen", None)
        if seen is None:
            seen = set()
            setattr(namespace, "_list_once_seen", seen)
        if self.dest in seen:
            shown = " ".join(str(v) for v in values)
            parser.error(
                f"{flag} was given more than once. It takes a LIST of values, so "
                f"a second occurrence replaces the first instead of adding to it: "
                f"the run would cover only the last group, and write a partial "
                f"artifact under the intended name.\n"
                f"  wrong:  {flag} A {flag} B   ->  covers B only\n"
                f"  right:  {flag} A B         ->  covers A and B\n"
                f"(this occurrence carried: {shown})"
            )
        seen.add(self.dest)
        setattr(namespace, self.dest, values)
