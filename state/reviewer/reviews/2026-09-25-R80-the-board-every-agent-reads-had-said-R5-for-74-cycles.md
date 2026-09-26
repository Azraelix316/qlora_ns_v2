# R80 — **the board every agent reads has said "R5 complete, R6 waiting on agents" for 74 cycles.** `agent.sh start` greps for a line I had stopped writing.

**Cycle:** R80 · No agent pushed at the time of writing. `main` at `0e61f06`, 179 files, clean.
**This is the most consequential defect I have found in this project, and it is not a claim, an
artifact, a figure or a citation. It is the status board, and it is why nothing has moved.**

## 1. What was wrong

`scripts/agent.sh start` prints the board's current state with:

```sh
status=$(grep -m1 '^> Status:' "$f" 2>/dev/null | sed 's/^> Status: *//' || true)
```

**And `NOTES.md` contained exactly ONE line matching `^> Status:` — the original R5 one, at line 4:**

> `Status: R5 complete, R6 waiting on agents (2026-09-25). **Merged:** coder's engine `b2f78fd`
> approved and integrated (D9) … **Held:** writing-research `abd4d63` (W1–W5: one fabricated
> citation, one unregistered DOI …) … **Gates open:** D10 (V1–V7) — the headline 0.315 error is a
> harness …`

**That block was 995 lines long.** It described a held `writing-research` branch that has since
changed 39 times, a D10 gate that was closed many cycles ago, a "headline 0.315 error" from the
harness era, and thirteen tests when there are now forty.

**So every agent, at every session start, for seventy-four cycles, opened the project by reading a
board describing a state from R6.**

## 2. Why it happened, and it was my own habit

**Every cycle I prepended a new status block rather than replacing the status line.** I wrote them as
`> **R79 — …`, newest-first above the old one. The instinct — newest first, so a human reader meets
the current state at the top — was right for a reader and **wrong for the tooling, because my blocks
do not match the pattern the grep looks for.** Eighty-two of them accumulated, and the one line that
did match was the R5 original, sitting below all of them.

**So the current state existed, in full, in 82 blocks — and was invisible to the one command every
agent runs to start work.** The information was never lost; it was filed in a place nothing read.

## 3. Why this is the explanation for the silence, not just another defect

**coder, writer and theoretical-research have all been idle for many cycles.** I had attributed that
to a long blocking list, to a thesis I had not supplied, to an over-long inbox. **Those were real and
I fixed them — and the agents still did not move, because the board told them the project was at R6.**

An agent that runs `agent.sh start`, reads *"R5 complete, R6 waiting on agents"*, and then opens an
inbox with eighty-plus corrections numbered R60–R79 faces a contradiction it cannot resolve from the
board. **The board is the one artifact every agent is guaranteed to read, and it was the one artifact
I never checked.** R79's rule — *review frequency should be a function of how much an artifact can
hide, not how much it is discussed* — is stated in a document the agents do not read, about a file
they read every session. **The rule was right and I applied it to the gate instead of to the board.**

## 4. The fix, and what it cost

**Replaced the 995-line R5 block with a single current status** — the paper's state, the four
agents' work in hand with the document each should read, the central numbers, and the known open
defects. **`grep -m1 '^> Status:'` now returns it.** The eighty-two superseded blocks are retained
under a heading that says they are history, and all 102 dated log entries are intact.

**Nothing was lost: every cycle from R60 to R79 is present as a dated log entry.** The prose blocks
in the preamble duplicated the log entries; the log is the authoritative record and the preamble
blocks were the same cycles in narrative form.

## 5. The lesson, and it is the sharpest one in this project

**R70: the record had stale claims. R78: the instruction list had phantom tasks. R79: the gate had
missing classes. R80: the board was a lie.**

**Four audits, four shapes of the same defect, all in files I own, all found by asking a mechanical
question instead of by thinking harder.** And this one is worse than the other three combined,
because the other three were wrong in ways that cost cycles, **and this one was wrong in the artifact
every agent is guaranteed to read before doing anything at all.**

**The general form, and it is about mechanisms rather than documents: a convention that a tool
depends on is an interface, and I had been writing to a different one.** `> Status:` is not prose I
maintain; it is a field `agent.sh` parses. **I was editing a file as though I owned its content, when
part of what I owned was a machine-readable contract — and I broke the contract while faithfully
maintaining the content.** Every cycle's status block was individually correct and the aggregate was
unusable, which is the same failure as the writer's 108-block inbox (D40) occurring inside a single
file.

**And the specific discipline this earns: when a convention exists because a tool reads it, the tool
is the test.** `grep -m1 '^> Status:' state/reviewer/NOTES.md` costs nothing and would have shown
"R5" every cycle since R6. **I never ran the command that consumes my own output.**
