# URANS Production Result

## Case

```text
inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0
```

Setup:

```text
airfoil = inverted NACA6412
cylinder_x_over_c = 0.02
cylinder_z_over_c = 0.10
lambda = +1.0
TIME_ITER = 500
INNER_ITER = 40
```

The run completed successfully:

```text
Maximum number of time iterations reached (TIME_ITER = 500).
Exit Success (SU2_CFD)
```

## Primary Averaging Window

Primary postprocessing window:

```text
Time_Iter = 250..499
```

Result:

```text
mean_CD                      = -1.120963
mean_CL                      = -1.646654
mean_C_DF                    =  1.646654
std_C_DF                     =  0.170976
mean_C_DF / abs(mean_CD)     =  1.468963
mean_CMy(cylinder)           =  2.037437
mean_motor_power_eta_0p8     =  227424 W
mean_equivalent_drag_abs     =  7803 N
mean_eta_net_abs_drag        =  0.041875
last_rms[Rho]                = -4.355740
```

Interpretation:

- The rotating cylinder produces positive mean downforce over the selected averaging window.
- The total aerodynamic `CD` is negative because the powered rotating cylinder contributes thrust-like streamwise force.
- Negative aerodynamic `CD` is not a free benefit. Motor power must be included through equivalent drag.
- With the current motor-power correction, the net efficiency metric remains positive but small.

## Averaging-Window Sensitivity

The same completed run was averaged with three windows.

| Window | mean_CD | mean_C_DF | std_C_DF | mean_motor_power_eta_0p8 | mean_eta_net_abs_drag |
|---|---:|---:|---:|---:|---:|
| 100..499 | -1.093446 | 1.547464 | 0.424585 | 216861 W | 0.041243 |
| 250..499 | -1.120963 | 1.646654 | 0.170976 | 227424 W | 0.041875 |
| 400..499 | -1.142236 | 1.666811 | 0.052572 | 233081 W | 0.041366 |

The late-window standard deviation is much lower than the early-window standard deviation, so the force history is settling by the end of the 500-step run.

## Static-Cylinder Baseline Check

The static-cylinder URANS baseline was also run in the same
`cases_urans_production` directory:

```text
inv6412_wing_cylinder_static_U30
```

Important caveat:

```text
last recorded Time_Iter = 447
physical_steps_total   = 448
```

The solver log contains an interrupt message before the nominal 500-step end.
Therefore this baseline is usable as a preliminary comparison, but it should
not be described as a clean 500-step completed run.

Primary averaging window:

```text
Time_Iter = 250..447
```

Result:

```text
mean_CD                      =  0.338587
mean_CL                      = -0.049654
mean_C_DF                    =  0.049654
std_C_DF                     =  0.181802
mean_C_DF / abs(mean_CD)     =  0.146650
mean_motor_power_eta_0p8     =  0 W
mean_equivalent_drag_abs     =  67 N
mean_eta_net_abs_drag        =  0.146650
last_rms[Rho]                = -4.706445
```

Late-window check:

| Window | mean_CD | mean_C_DF | std_C_DF | mean_motor_power_eta_0p8 | mean_eta_net_abs_drag |
|---|---:|---:|---:|---:|---:|
| 400..447 | 0.331295 | -0.021945 | 0.003312 | 0 W | -0.066239 |

Interpretation:

- The static-cylinder baseline is far weaker than the rotating candidate in
  downforce production.
- The late static-cylinder window has almost no positive downforce and slightly
  negative mean `C_DF`.
- Because the run stopped at `Time_Iter = 447`, repeat or continue this case if
  a strict clean-baseline table is required.

## Wing-Only Baseline Check

The wing-only URANS baseline was run with the same production settings:

```text
inv6412_wing_only_U30
```

The run completed successfully:

```text
Maximum number of time iterations reached (TIME_ITER = 500).
Exit Success (SU2_CFD)
```

Primary averaging window:

```text
Time_Iter = 250..499
```

Result:

```text
mean_CD                      =  0.107731
mean_CL                      = -0.147733
mean_C_DF                    =  0.147733
std_C_DF                     =  0.103081
mean_C_DF / abs(mean_CD)     =  1.371320
last_rms[Rho]                = -6.219895
```

Late-window check:

| Window | mean_CD | mean_C_DF | std_C_DF | mean_C_DF / abs(mean_CD) |
|---|---:|---:|---:|---:|
| 400..499 | 0.106653 | 0.153903 | 0.016722 | 1.443018 |

Interpretation:

- The wing-only baseline is the cleanest of the three production runs by
  residual level and late-window force stability.
- The wing alone produces modest positive downforce.
- This baseline is now the main reference for deciding whether the rotating
  cylinder adds enough downforce to justify its power requirement.

## Current Comparison

Using the primary averaging windows available now:

| Case | Steps | Window | mean_CD | mean_C_DF | std_C_DF | mean_motor_power_eta_0p8 | mean_eta_net_abs_drag |
|---|---:|---|---:|---:|---:|---:|---:|
| rotating candidate | 500 | 250..499 | -1.120963 | 1.646654 | 0.170976 | 227424 W | 0.041875 |
| static cylinder | 448 | 250..447 | 0.338587 | 0.049654 | 0.181802 | 0 W | 0.146650 |
| wing-only | 500 | 250..499 | 0.107731 | 0.147733 | 0.103081 | n/a | n/a |

Late-window comparison:

| Case | Steps | Window | mean_CD | mean_C_DF | std_C_DF | mean_C_DF / abs(mean_CD) |
|---|---:|---|---:|---:|---:|---:|
| rotating candidate | 500 | 400..499 | -1.142236 | 1.666811 | 0.052572 | 1.459253 |
| static cylinder | 448 | 400..447 | 0.331295 | -0.021945 | 0.003312 | -0.066239 |
| wing-only | 500 | 400..499 | 0.106653 | 0.153903 | 0.016722 | 1.443018 |

This comparison supports the qualitative result that the powered rotating
cylinder produces much more downforce than both the static-cylinder and
wing-only baselines. However, the rotating case requires roughly
`227-233 kW` of estimated motor power in these averaging windows. Therefore the
result should be described as a strong downforce gain with a large actuation
power cost, not as a free aerodynamic efficiency improvement.

## Research Judgment

This is the first usable URANS production comparison across rotating cylinder,
static cylinder, and wing-only baselines.

Current defensible conclusion:

- The selected rotating-cylinder candidate substantially increases downforce
  relative to both baselines.
- The static cylinder by itself does not improve the wing in the late-window
  production result.
- The wing-only baseline is numerically cleaner than the cylinder cases and
  provides the best reference for final reporting.
- The rotating-cylinder benefit is tied to a large motor-power requirement, so
  the final objective should report both downforce gain and power-corrected net
  efficiency.

Remaining caveat:

- The static-cylinder case stopped at `Time_Iter = 447`, not the nominal
  500-step end. If strict run parity is required, rerun or continue static
  cylinder to a clean 500-step completion before freezing the final table.
