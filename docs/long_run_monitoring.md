# Long-Run RANS Monitoring

## Active Case

- Case: `inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0`
- Case directory: `cases_rans_long_10000/`
- Airfoil: inverted NACA6412
- Cylinder position: `x/c = 0.02`, `z/c = 0.10`
- Rotation ratio: `lambda = +1.0`
- Solver: steady RANS, SST
- Iteration limit: `10000`
- Started after commit: `5211105`

## Initial Checkpoint

At iteration 112:

```text
rms[Rho] = -3.500301
CL       =  0.561563
CD       =  6.154255
C_DF     = -0.561563
```

Interpretation:

- The solver is running without an immediate crash or NaN.
- Residual is decreasing from the initial value, so the setup is not instantly divergent.
- The force coefficients are still moving strongly and must not be used as a final performance result.
- CL has crossed into positive lift by this early checkpoint, so the long-run result must be judged by late-window force drift, not by early smoke-test values.

## 500-Iteration Checkpoint

The steady RANS long-run was stopped after a valid restart checkpoint was written.

Files preserved:

```text
cases_rans_long_10000/inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0/restart.dat
cases_rans_long_10000/inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0/history.csv
cases_rans_long_10000/inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0/su2.log
results/rans_long_500_checkpoint_summary.csv
```

Postprocessed final row at iteration 525:

```text
rms[Rho] = -3.327018
CL       = -6.653672
CD       = -0.539330
C_DF     =  6.653672
```

Last 50-row drift:

```text
Delta CL   =  1.810160
Delta C_DF = -1.810160
Delta CD   = -0.458996
```

Key observation:

- The solver did not crash, and it wrote `restart.dat` at iteration 500.
- Residual improved early, then degraded from about `rms[Rho] = -3.56` to `-3.33`.
- Force history showed a large sweep: CL moved from positive lift to strong downforce and was still drifting at the checkpoint.
- The 500-iteration checkpoint is not a converged steady RANS result.
- Continuing to 10000 iterations may still be possible from `restart.dat`, but the current force behavior suggests the flow is not settling cleanly as a steady problem.

Practical decision:

- Do not use this run as a performance result.
- Treat it as evidence that the rotating-cylinder case is likely unsteady or numerically stiff in steady RANS.
- Next priority should be URANS setup or a simplified 2D/quasi-2D validation problem before spending more time on 3D steady-RANS sweeps.

## Decision Rule

Continue the long run unless one of these happens:

- residual blows up or becomes NaN
- SU2 exits with an error
- force coefficients grow without bound for many consecutive checkpoints
- the run becomes impractically slow and needs a restart/batch strategy

Use the final 500 to 1000 iterations for force-drift assessment. If the force remains periodic or drifting after the long run, switch from steady RANS to URANS or a simplified 2D/quasi-2D validation problem.
