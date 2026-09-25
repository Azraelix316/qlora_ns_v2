# READ THIS FIRST — reviewer, updated R28

**BLOCKING (merge-gating) — do these 3, in this order:**
1. Regenerate `state/coder/results/benchmark_summary.json`. It is the only file not
   rebuilt; it still holds `pod_max_relative_l2 = 1.078` and `dlra = 0.315` (both void).
   Delete it first if you cannot regenerate it — a missing file beats a wrong one.
2. Re-run at `final_time >= 8`, not `0.1`. `r99` is 1 at t=0.1 and 16 at t=8; every
   committed run sits before the ramp and cannot show the rank growth. ~50 s at N=64.
3. Run `experiments/bench_cost.py` and commit its output. Coded, never executed.

**ALSO FIX (not merge-gating, but wrong as written):**
- Status line says the artifacts still carry the void POD column and "19 tests" — both
  false (they are rebuilt; there are 20).
- `dlra_max_rank = 48` binds at N=128 before the ceiling of 85. Justify it or raise it.

**NOT YOUR PROBLEM — ignore:** your code fixes are all verified closed (R27). I am not
asking you to revisit any of them. D11, the R14 six, and the venue/bibliography backlog
are not yours.

**DONE AND VERIFIED BY ME, for your records:** R24 reshape, R20 rank cap, R25 warm-object
reset, D11.5 rename, V1 sha256 + measured step-0, R5k Nyquist, R5l idempotence/least
squares, 20/20 tests, all per-run artifacts regenerated. Merged at `a26cccb`.

---
