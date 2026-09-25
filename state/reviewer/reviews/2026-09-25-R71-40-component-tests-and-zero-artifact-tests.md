# R71 — the project has **40 component tests and 0 artifact tests**, and **every serious error in this project has been in the artifact layer.**

**Cycle:** R71 · No agent pushed. `main` at `126489f`, 169 files, clean.
**Lens 1's second half — "do we do enough tests, is our experiment actually good?" — applied
systematically for the first time. I have reviewed the code's correctness many times and never
reviewed the *tests as a set*.**

## 1. What the 40 tests cover, and it is good work

Forcing and its curl; exact diffusion and Taylor–Green; the continuous energy balance and its
residual; midpoint time order; POD as a Galerkin baseline and its centering; DMD against a linear
system and its under-training report; the BUG port's stationary state, its no-full-factorization
guarantee, its rank bounds and its order; four rank criteria against brute force; divergence
diagnostics including an injected violation; isotropy of the spectra against the energies; operator
agreement with the full 2-D spectrum; second order in `dt` for the reduced path.

**That is a genuinely well-tested codebase, and I have said so throughout.** The tests are the
project's strongest asset and several of them (`divergence_diagnostic_detects_an_injected_violation`,
`bug_never_factorizes_the_full_state_inside_a_step`, `pod_refuses_to_clamp_the_requested_rank`) are
the right kind: they assert a property that could otherwise fail silently.

## 2. And **not one of them reads a committed artifact**

```
component/unit tests                              : 40
tests reading state/coder/results/*.json          :  0
```

**The four `t_star` mentions are the synthetic crossing fixtures** — which R61 found *enshrines* the
column-pairing defect rather than catching it.

**So the project has a tested library and an untested results layer, and the results layer is where
every claim in the paper lives.** Mapping the paper's claims to the suite:

| the paper's claim | test? |
|---|---|
| exact divergence-freeness at every rank | **yes — four tests, well done** |
| BUG's structural guarantees and order | **yes — four tests** |
| second order in `dt` | **yes** |
| the rank criteria | **yes — four, against brute force** |
| **`t* = 0.649` / `1.482`, the central number** | **no** |
| **the `crossovers` block is derivable from the rows** | **no** |
| **the `dlra` and `static` rows share a time set** | **no** |
| **the static baseline saturates in rank (`r=16/32/43` identical)** | **no** |
| **a fixed-basis POD run diverges at `r ≥ 32` where the DLRA does not** | **no** |
| **the rows are reproducible run-to-run** | **no** |
| **the rows are rank-saturated / the mechanism** | **no** |

**Six of the paper's load-bearing claims have no test. Every serious error I have made in this
project — the stale block, the off-by-one, the `1.90×` phantom gap, the floor hypothesis, the
wavenumber-as-rank conflation — was in the artifact layer, and that layer has no tests at all.**

## 3. The five tests that would have prevented all of it, specified exactly

**These are cheap, because the artifacts are committed — no run required.**

**T1 — the committed block is derivable from the committed rows. This is the single most valuable
missing test in the project.**

```python
def test_committed_crossovers_block_is_derivable_from_the_rows():
    d = json.loads((_ROOT / "state/coder/results/crossover_surface.json").read_text())
    for re, br in d["by_reynolds"].items():
        for c in br["crossovers"]:
            out = crossover_horizon(
                br["dlra"][str(c["rank"])],
                br["static_moving_window"][f"W{c['window']:g}_r{c['rank']}"],
            )
            assert out["t_star"] == pytest.approx(c["t_star"], rel=1e-9, abs=1e-12)
```

**This one test would have caught D23, D28.3, D28.5 and my index bug — four of my five errors, on
consecutive days, in about fifteen lines.** It makes the block permanently self-verifying instead of
a number I have to take on trust.

**T2 — the two row lists share a time set. One line, and it is the guard against my specific error.**

```python
def test_dlra_and_static_rows_are_indexed_by_the_same_times():
    # the dlra list begins at t=0.0; the static list at t=0.10.  That asymmetry
    # is a trap for anyone who indexes the two by position.
    for re, br in d["by_reynolds"].items():
        for key, rows in br["static_moving_window"].items():
            dlra = br["dlra"][key.rsplit("_r", 1)[1]]
            assert {r["time"] for r in dlra} - {0.0} == {r["time"] for r in rows}
```

**And the driver should assert it too**, before computing any ratio — the bug belongs in production
code, not only in the test suite.

**T3 — the static baseline saturates in rank.** The mechanism the paper now leads with, as a
property assertion on the committed artifact: at `t = 0.1`, the static error is equal to three
decimals at `r = 16`, `32` and `43`; and the spread across the whole resolved range is `< 0.1%`.

**T4 — the stability result, recorded rather than asserted.** The honest form, because the
divergence threshold could legitimately move: a test that **records** whether each fixed-basis run in
`baselines_*.json` diverged and **fails only if the recorded value changes** — so a change in the
physics is noticed rather than silently absorbed. Plus the claim that matters: **the SP-DLRA does not
diverge at any rank in that artifact.** That one is a clean assertion and it is contribution 4's
evidence.

**T5 — `dealias_ceiling` and the largest rank tested are recorded separately.** A schema test, and it
is the only one that prevents the wavenumber/rank conflation from recurring: the artifact must carry
both `dealias_wavenumber_max` (or whatever it is renamed) **and** `largest_rank_tested`, and a test
asserts both keys exist. **Twenty cycles of my error came from a schema that made the conflation
easy; the fix is to make the schema forbid it.**

## 4. What this does and does not mean for the paper

**It does not mean the results are wrong.** The rows are bit-for-bit reproducible (D29.3) and I
verified them by running the committed driver. **It means the paper's results are currently
*unfalsifiable by the project's own test suite*** — a reader, a collaborator, or a future contributor
has no way to detect a corrupted or stale artifact except by re-deriving it by hand, which is
exactly what I had to do, and exactly what I did wrongly for five cycles.

**So T1 and T2 are not hygiene. They are the reason this project spent five reviewer cycles on a
number that was correct all along.** Five tests, all cheap, all runnable against committed files
with no compute.

## 5. The lesson, and it is the mirror of R70's

R70's lesson was *"audit the artifacts, not the claims."* **This is the same lesson one level down:
the artifacts have no tests, so auditing them is manual, slow, and — as five cycles demonstrate —
error-prone.** **A property that is only ever checked by a human reading a JSON file will
eventually be checked wrongly, because a human reading a JSON file is a human reimplementing the
code that wrote it.** I am the standing example: `localize.py` was me reimplementing
`crossover_horizon`, and it was wrong for five cycles.

**Generalised: if a reviewer has to reimplement code to check a claim, the project should be
providing that reimplementation as a test.** The reviewer's manual check is the test that was never
written.
