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

## Decision Rule

Continue the long run unless one of these happens:

- residual blows up or becomes NaN
- SU2 exits with an error
- force coefficients grow without bound for many consecutive checkpoints
- the run becomes impractically slow and needs a restart/batch strategy

Use the final 500 to 1000 iterations for force-drift assessment. If the force remains periodic or drifting after the long run, switch from steady RANS to URANS or a simplified 2D/quasi-2D validation problem.
