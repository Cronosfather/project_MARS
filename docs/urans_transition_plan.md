# URANS Transition Plan

## Why This Is Needed

The rotating-cylinder 3D steady RANS candidate did not settle cleanly by the 500-iteration checkpoint.

Observed at the 500-checkpoint run:

```text
last recorded iteration = 525
rms[Rho]                = -3.327018
CL                      = -6.653672
CD                      = -0.539330
last-50-row Delta CL    =  1.810160
```

This is not a converged steady result. The force history moved through large positive and negative CL ranges, so the next research step should treat the flow as potentially unsteady.

## Prepared URANS Smoke Setup

Template:

```text
config/su2_template_urans_moving_wall_smoke.cfg
```

Case directory:

```text
cases_urans_smoke/
```

Verified candidate dry-run:

```text
cases_urans_smoke/inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0/su2_dryrun.log
```

Dry-run confirmed:

- dual-time unsteady RANS is recognized
- physical time step is `4.18879020479E-05 s`
- physical time steps: `20`
- inner iterations per step: `30`
- moving surfaces: `ground, cylinder`
- rotating cylinder angular velocity: `1500 rad/s`

The time step corresponds to roughly 100 time steps per cylinder revolution at `omega = 1500 rad/s`.

## Next Execution

Run the short URANS smoke case first:

```text
wsl bash -lc "cd /mnt/d/RAGNAROK/3_ing/MARS_project && python3 scripts/run_case.py inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0 --case-dir cases_urans_smoke --threads 4"
```

Smoke-test success criteria:

1. SU2 completes all 20 physical time steps.
2. No NaN or solver crash occurs.
3. Moving-wall messages remain correct.
4. `history.csv` contains time-iteration output that postprocessing can parse or can be adapted to parse.

## Production Direction

If the URANS smoke test passes:

1. Increase to at least 5 to 10 cylinder revolutions.
2. Discard early transient cycles.
3. Average force and torque over the last several cycles.
4. Compare rotating cylinder against static cylinder and wing-only with the same unsteady settings.

If the URANS smoke test fails or is too expensive:

1. Build a simplified 2D or quasi-2D validation case.
2. Verify rotation convention and Magnus-force direction.
3. Verify cylinder moment sign and motor-power calculation.
4. Return to the 3D case only after the simplified case behaves consistently.
