"""Collect final SU2 history values into results/summary.csv."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DRIVETRAIN_EFFICIENCY = 0.8
FORCE_DRIFT_WINDOW = 50


def read_case_metadata(path: Path) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata


def read_history_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = [{key.strip().strip('"'): value.strip() for key, value in row.items()} for row in reader]
    if not rows:
        raise ValueError(f"No history rows in {path}")
    return rows


def read_config_scalar(path: Path, key: str) -> float | None:
    prefix = f"{key}="
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("%", 1)[0].strip()
        if line.startswith(prefix):
            return float(line.split("=", 1)[1].strip())
    return None


def as_float(value: str) -> float | None:
    if value.lower() == "none":
        return None
    return float(value)


def force_drift(history_rows: list[dict[str, str]], window: int = FORCE_DRIFT_WINDOW) -> dict[str, str]:
    tail = history_rows[-min(window, len(history_rows)) :]
    first = tail[0]
    last = tail[-1]
    cd_first = float(first["CD"])
    cd_last = float(last["CD"])
    cl_first = float(first["CL"])
    cl_last = float(last["CL"])
    cdf_first = -cl_first
    cdf_last = -cl_last

    def relative_change(first_value: float, last_value: float) -> str:
        scale = max(abs(first_value), 1e-12)
        return f"{((last_value - first_value) / scale):.10g}"

    return {
        "force_drift_window_rows": str(len(tail)),
        "cd_drift_last_window": f"{(cd_last - cd_first):.10g}",
        "cd_drift_pct_last_window": relative_change(cd_first, cd_last),
        "cl_drift_last_window": f"{(cl_last - cl_first):.10g}",
        "cl_drift_pct_last_window": relative_change(cl_first, cl_last),
        "c_downforce_drift_last_window": f"{(cdf_last - cdf_first):.10g}",
        "c_downforce_drift_pct_last_window": relative_change(cdf_first, cdf_last),
    }


def summarize_case(case_dir: Path) -> dict[str, str]:
    metadata = read_case_metadata(case_dir / "case.yaml")
    history_rows = read_history_rows(case_dir / "history.csv")
    history = history_rows[-1]
    drift = force_drift(history_rows)
    cl = float(history["CL"])
    cd = float(history["CD"])
    cdf = -cl
    ref_force = float(history.get("RefForce", "nan"))
    ref_length = read_config_scalar(case_dir / "config.cfg", "REF_LENGTH")
    omega = as_float(metadata["omega_rad_s"])
    cmy_cylinder = history.get("CMy(cylinder)")
    cylinder_moment_y_nm = None
    motor_power_w = None
    equivalent_drag_n = None
    eta_net = None
    if cmy_cylinder is not None and ref_length is not None and omega is not None:
        cylinder_moment_y_nm = float(cmy_cylinder) * ref_force * ref_length
        motor_power_w = cylinder_moment_y_nm * omega / DEFAULT_DRIVETRAIN_EFFICIENCY
        u_inf = float(metadata["u_inf_m_s"])
        aerodynamic_drag_n = abs(cd * ref_force)
        equivalent_drag_n = aerodynamic_drag_n + abs(motor_power_w) / u_inf
        downforce_n = cdf * ref_force
        if equivalent_drag_n != 0.0:
            eta_net = downforce_n / equivalent_drag_n
    return {
        "case": metadata["name"],
        "u_inf_m_s": metadata["u_inf_m_s"],
        "lambda": metadata["lambda"],
        "cylinder_x_over_c": metadata.get("cylinder_x_over_c", ""),
        "cylinder_z_over_c": metadata.get("cylinder_z_over_c", ""),
        "omega_rad_s": metadata["omega_rad_s"],
        "rpm": metadata["rpm"],
        "inner_iter": history["Inner_Iter"],
        "rms_rho": history["rms[Rho]"],
        "cd": f"{cd:.10g}",
        "cd_abs": f"{abs(cd):.10g}",
        "cl": f"{cl:.10g}",
        "c_downforce": f"{cdf:.10g}",
        "c_downforce_over_cd": f"{(cdf / cd):.10g}" if cd != 0.0 else "",
        "c_downforce_over_abs_cd": f"{(cdf / abs(cd)):.10g}" if cd != 0.0 else "",
        "cmx": history["CMx"],
        "cmy": history["CMy"],
        "cmz": history["CMz"],
        "cd_wing": history.get("CD(wing)", ""),
        "cd_cylinder": history.get("CD(cylinder)", ""),
        "cd_ground": history.get("CD(ground)", ""),
        "cl_wing": history.get("CL(wing)", ""),
        "cl_cylinder": history.get("CL(cylinder)", ""),
        "cl_ground": history.get("CL(ground)", ""),
        "cmy_wing": history.get("CMy(wing)", ""),
        "cmy_cylinder": history.get("CMy(cylinder)", ""),
        "cmy_ground": history.get("CMy(ground)", ""),
        "cylinder_moment_y_nm": "" if cylinder_moment_y_nm is None else f"{cylinder_moment_y_nm:.10g}",
        "motor_power_w_eta_0p8": "" if motor_power_w is None else f"{motor_power_w:.10g}",
        "equivalent_drag_n_abs": "" if equivalent_drag_n is None else f"{equivalent_drag_n:.10g}",
        "eta_net_abs_drag": "" if eta_net is None else f"{eta_net:.10g}",
        **drift,
        "dry_run_log": str((case_dir / "su2_dryrun.log").relative_to(ROOT)),
        "solver_log": str((case_dir / "su2.log").relative_to(ROOT)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-dir", default="cases")
    parser.add_argument("--output", default="results/summary.csv")
    args = parser.parse_args()

    case_root = ROOT / args.case_dir
    rows = []
    for case_dir in sorted(path for path in case_root.iterdir() if path.is_dir()):
        if (case_dir / "case.yaml").exists() and (case_dir / "history.csv").exists():
            rows.append(summarize_case(case_dir))

    output_path = ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case",
        "u_inf_m_s",
        "lambda",
        "cylinder_x_over_c",
        "cylinder_z_over_c",
        "omega_rad_s",
        "rpm",
        "inner_iter",
        "rms_rho",
        "cd",
        "cd_abs",
        "cl",
        "c_downforce",
        "c_downforce_over_cd",
        "c_downforce_over_abs_cd",
        "cmx",
        "cmy",
        "cmz",
        "cd_wing",
        "cd_cylinder",
        "cd_ground",
        "cl_wing",
        "cl_cylinder",
        "cl_ground",
        "cmy_wing",
        "cmy_cylinder",
        "cmy_ground",
        "cylinder_moment_y_nm",
        "motor_power_w_eta_0p8",
        "equivalent_drag_n_abs",
        "eta_net_abs_drag",
        "force_drift_window_rows",
        "cd_drift_last_window",
        "cd_drift_pct_last_window",
        "cl_drift_last_window",
        "cl_drift_pct_last_window",
        "c_downforce_drift_last_window",
        "c_downforce_drift_pct_last_window",
        "dry_run_log",
        "solver_log",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {output_path.relative_to(ROOT)} with {len(rows)} rows")


if __name__ == "__main__":
    main()
