# Coder experiment drivers

The engine uses a periodic `[0, 2*pi)^2` grid and the convention

```text
u = (psi_y, -psi_x),    omega = -Delta(psi).
```

Thus every stream-function state, including SVD- and POD-projected states, is
 divergence-free by construction.  `run_taylor_green.py` is the laminar
validation; `run_kolmogorov.py` compares full-grid spectral integration,
static POD-Galerkin, and adaptive SVD-DLRA at a chosen Reynolds number.
`bench.py` runs the binding Re=100, 1000, 5000 suite.
`run_rank_growth_sweep.py` records the rank/error tradeoff as the adaptive
singular-value threshold is tightened.  `run_long_time.py` provides a
full-grid/DLRA sustained-time check without the unstable long-horizon POD
baseline.

Typical commands (from the worktree root, with the project venv):

```bash
~/.venvs/ns/bin/python -m pytest -q
~/.venvs/ns/bin/python experiments/run_taylor_green.py \
  --N 64 --nu 0.02 --dt 0.01 --steps 200 \
  --output state/coder/results/taylor_green.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ~/.venvs/ns/bin/python experiments/bench.py \
  --N 64 --dt 0.0005 --steps 200 --train-steps 100 \
  --snapshot-stride 5 --compare-stride 20 --force-amplitude 0.5 \
  --perturbation-velocity-rms 1.0 --pod-rank 16 --dlra-rank 2 \
  --dlra-min-rank 2 --dlra-max-rank 48 --dlra-tolerance 1e-10 \
  --output-dir state/coder/results
```

The stream-function constant is treated as a gauge: SVD inputs are centered,
but the rank-r reconstruction is not mean-subtracted a second time (that would
add a rank-one constant).  The integrator centers before physical operators,
and reduced-vs-full errors compare centered states.

The reported forcing-aware diagnostic is the finite-difference residual of

```text
dE/dt + nu*||omega||^2 - <psi,zeta> + <psi,(u.grad)omega> = 0,
E = 1/2*||grad psi||^2.
```

The advection inner product is retained in the JSON even though it vanishes
for the exact incompressible velocity.  For reduced runs, the JSON also
reports the measured projection energy increment and a discrete balance with
that control work removed; the uncorrected full-PDE residual is reported
separately.  `stable` means finite and within deliberately broad
scale-aware sanity limits (relative energy <=10, relative enstrophy <=100,
divergence <=1e-10, CFL <=0.5), not a claim of long-time stability.

The DLRA timing includes every SVD projection; the current implementation
evaluates the nonlinear residual on the full grid, so a speedup is not
implied.  Result JSON files record the driver, parameters, and git commit used
for the run.
