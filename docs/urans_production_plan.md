# URANS Production Plan

## Current Decision

The short URANS visualization run looked numerically sane: no obvious blow-up, moving-wall interaction is visible, and ParaView output works. The next step is not more steady RANS. It is a longer URANS run with time-averaged force and torque.

## Prepared Production Template

Template:

```text
config/su2_template_urans_moving_wall_production.cfg
```

Case directory:

```text
cases_urans_production/
```

Key settings:

```text
TIME_STEP = 4.18879020479E-05
TIME_ITER = 500
INNER_ITER = 40
OUTPUT_FILES = ( RESTART )
OUTPUT_WRT_FREQ = 50
```

At `omega = 1500 rad/s`, one cylinder revolution is about 100 physical time steps. `TIME_ITER = 500` is about 5 cylinder revolutions.

## Averaging Rule

URANS results must be averaged over physical time, not read from the final row only.

Use:

```text
scripts/postprocess_urans_average.py
```

The script:

- keeps only the final inner iteration for each physical `Time_Iter`
- averages `CD`, `CL`, downforce, and cylinder moment over a selected time window
- reports standard deviation to show oscillation strength
- estimates motor power from average cylinder moment

Initial recommendation:

```text
python scripts/postprocess_urans_average.py --case-dir cases_urans_production --output results/urans_production_average_summary.csv --start-time-iter 250
```

This discards the first half of a 500-step run as transient.

## Execution Order

1. Run the rotating candidate first.
2. If it completes, run static cylinder with the same URANS settings.
3. If needed, run wing-only with the same URANS settings.
4. Compare time-averaged downforce, drag, torque, and net efficiency.

Do not launch a broad parameter sweep until the first production run has a stable averaging window.

## 2026-07-07 Status

The ParaView screenshots from the short URANS visualization run were reviewed.

Visual judgment:

- The visualization pipeline is working.
- The cylinder/wing/ground geometry is intact.
- No obvious NaN-like color blow-up or broken-cell artifact is visible.
- The rotating cylinder visibly affects the local flow.
- The wake and low-speed region evolve over time, so URANS is justified.
- The current 20-step run is still only an initial transient and must not be used for performance conclusions.

Production dry-run status:

```text
cases_urans_production/inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0/su2_dryrun.log
```

Confirmed by dry-run:

```text
Maximum number of physical time-steps: 500
Maximum number of solver subiterations: 40
Surface(s) in motion: ground, cylinder
RESTART output frequency: 50
```

The averaging script was tested on the short visualization run:

```text
results/urans_visualization_average_summary.csv
```

That short-run summary is only a pipeline check. The averaging window covers the early transient, so its mean force values are not a final aerodynamic result.

Next command for the first long URANS run:

```text
wsl bash -lc "cd /mnt/d/RAGNAROK/3_ing/MARS_project && python3 scripts/run_case.py inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0 --case-dir cases_urans_production --threads 4"
```

Expected runtime is much longer than the 20-step visualization run. Start it as a deliberate long/batch job, then postprocess with:

```text
python scripts/postprocess_urans_average.py --case-dir cases_urans_production --output results/urans_production_average_summary.csv --start-time-iter 250
```
