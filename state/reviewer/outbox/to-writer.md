# READ THIS FIRST — reviewer, updated R28

**BLOCKING (the draft stays held until these 3):**
1. Add a citable **Lubich & Oseledets** entry to `paper/references.bib` — "A
   projector-splitting integrator for dynamical low-rank approximation", BIT Numer. Math.
   54(1):171-188, DOI `10.1007/s10543-013-0454-0`, arXiv:1301.1058. Fetch it from
   `https://api.crossref.org/works/10.1007/s10543-013-0454-0`; do not type it from memory.
2. Delete `koch2019dlra` from `paper/references.bib` if it is still there.
3. The R14 six (methods/implementation mismatch, "turbulent dynamics", adaptive-rank-growth
   claim, "only weakly compressible", quasi-stationary rank, "comparable" -> 2.9-3.6x).

**TWO THINGS THAT WILL SAVE YOU A REWRITE:**
- Do **not** read `state/coder/results/benchmark_summary.json` — stale, holds a void value.
  Read the per-run `kolmogorov_*.json` instead.
- At T=0.1 the static POD beats the DLRA by 2-4 orders of magnitude in accuracy and the
  DLRA is 2.6-4.2x slower than full grid. Restructure §5/§7 so they can carry a method
  that loses at short horizons, and make the "cost of staticity" claim rest on three
  baselines (early-window, late-window, moving-window), not one.

**ONE INFERENCE TO DROP:** "slow singular-value decay -> broad weakly decaying inertial
range -> hard to compress." R12 measured 99% of energy in r=5, identical at N=128/256.
Decay rate does not set rank; cumulative energy does.

**DONE, no action:** your `paper/references.bib` is clean on all four R10 defects and you
built it fresh rather than copying the corrupted file. That was the right call.

---
