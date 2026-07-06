# ParaView Animation Workflow

## Prepared Setup

Use this template for a short URANS visualization run:

```text
config/su2_template_urans_moving_wall_visualization.cfg
```

Generated case directory:

```text
cases_urans_visualization/
```

Candidate case:

```text
inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0
```

## Output Settings

The visualization template enables ParaView output:

```text
OUTPUT_FILES = ( RESTART, PARAVIEW )
OUTPUT_WRT_FREQ = 2
TIME_ITER = 20
INNER_ITER = 30
```

This creates a short time series while keeping disk usage controlled. Increase `TIME_ITER` only after the short run is confirmed.

## Run Command

```text
wsl bash -lc "cd /mnt/d/RAGNAROK/3_ing/MARS_project && python3 scripts/run_case.py inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0 --case-dir cases_urans_visualization --threads 4"
```

## ParaView Steps

1. Open `flow_timeseries.pvd` if it exists. Otherwise open the generated `.vtu` files as a file series.
2. If ParaView asks to group files as a time series, accept it.
3. Apply coloring by velocity magnitude, pressure, or vorticity/Q-criterion if available.
4. Use the time controls to play the sequence.
5. Export with `File > Save Animation` after the view is configured.

If SU2 writes only individual `.vtu` files, create a `.pvd` index:

```text
python scripts/write_paraview_pvd.py cases_urans_visualization/inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0
```

## Caution

3D volume output grows quickly. Keep `OUTPUT_WRT_FREQ` coarse and `TIME_ITER` short until the animation workflow is verified.

## Completed Short Run

The first visualization run completed successfully for:

```text
cases_urans_visualization/inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0
```

SU2 completed `TIME_ITER = 20` and exited successfully.

Generated ParaView files:

```text
flow_00000.vtu
flow_00002.vtu
flow_00004.vtu
flow_00006.vtu
flow_00008.vtu
flow_00010.vtu
flow_00012.vtu
flow_00014.vtu
flow_00016.vtu
flow_00018.vtu
flow_00019.vtu
flow_timeseries.pvd
```

Open this file in ParaView:

```text
cases_urans_visualization/inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0/flow_timeseries.pvd
```
