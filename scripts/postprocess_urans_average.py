"""Average URANS force history over physical time steps."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DRIVETRAIN_EFFICIENCY = 0.8


def read_case_metadata(path: Path) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata


def read_config_scalar(path: Path, key: str) -> float | None:
    prefix = f"{key}="
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("%", 1)[0].strip()
        if line.startswith(prefix):
            return float(line.split("=", 1)[1].strip())
    return None


def read_history_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [{key.strip().strip('"'): value.strip() for key, value in row.items()} for row in reader]


def as_float(value: str | None) -> float | None:
    if value is None or value == "" or value.lower() == "none":
        return None
    return float(value)


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def sample_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    return math.sqrt(sum((value - avg) ** 2 for value in values) / (len(values) - 1))


def final_inner_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_time: dict[int, dict[str, str]] = {}
    for row in rows:
        time_iter = int(row["Time_Iter"])
        inner_iter = int(row["Inner_Iter"])
        previous = by_time.get(time_iter)
        if previous is None or inner_iter > int(previous["Inner_Iter"]):
            by_time[time_iter] = row
    return [by_time[key] for key in sorted(by_time)]


def window_rows(rows: list[dict[str, str]], start_time_iter: int | None, last_fraction: float) -> list[dict[str, str]]:
    if not rows:
        raise ValueError("No rows available for averaging")
    if start_time_iter is not None:
        selected = [row for row in rows if int(row["Time_Iter"]) >= start_time_iter]
    else:
        keep = max(1, math.ceil(len(rows) * last_fraction))
        selected = rows[-keep:]
    if not selected:
        raise ValueError("Averaging window is empty")
    return selected


def row_float(row: dict[str, str], key: str) -> float | None:
    return as_float(row.get(key))


def values(rows: list[dict[str, str]], key: str) -> list[float]:
    result = []
    for row in rows:
        value = row_float(row, key)
        if value is not None:
            result.append(value)
    return result


def summarize_case(case_dir: Path, start_time_iter: int | None, last_fraction: float) -> dict[str, str]:
    metadata = read_case_metadata(case_dir / "case.yaml")
    all_rows = read_history_rows(case_dir / "history.csv")
    physical_rows = final_inner_rows(all_rows)
    avg_rows = window_rows(physical_rows, start_time_iter, last_fraction)
    first = avg_rows[0]
    last = avg_rows[-1]

    cd_values = values(avg_rows, "CD")
    cl_values = values(avg_rows, "CL")
    cmy_cylinder_values = values(avg_rows, "CMy(cylinder)")
    ref_force = row_float(last, "RefForce")
    ref_length = read_config_scalar(case_dir / "config.cfg", "REF_LENGTH")
    omega = as_float(metadata.get("omega_rad_s"))

    mean_cd = mean(cd_values)
    mean_cl = mean(cl_values)
    mean_downforce = -mean_cl
    mean_cmy_cylinder = mean(cmy_cylinder_values) if cmy_cylinder_values else None

    mean_motor_power = None
    mean_equivalent_drag = None
    mean_eta_net = None
    if mean_cmy_cylinder is not None and ref_force is not None and ref_length is not None and omega is not None:
        mean_moment_y = mean_cmy_cylinder * ref_force * ref_length
        mean_motor_power = mean_moment_y * omega / DEFAULT_DRIVETRAIN_EFFICIENCY
        u_inf = float(metadata["u_inf_m_s"])
        aerodynamic_drag_n = abs(mean_cd * ref_force)
        mean_equivalent_drag = aerodynamic_drag_n + abs(mean_motor_power) / u_inf
        mean_downforce_n = mean_downforce * ref_force
        if mean_equivalent_drag != 0.0:
            mean_eta_net = mean_downforce_n / mean_equivalent_drag

    return {
        "case": metadata["name"],
        "u_inf_m_s": metadata["u_inf_m_s"],
        "lambda": metadata["lambda"],
        "cylinder_x_over_c": metadata.get("cylinder_x_over_c", ""),
        "cylinder_z_over_c": metadata.get("cylinder_z_over_c", ""),
        "omega_rad_s": metadata["omega_rad_s"],
        "rpm": metadata["rpm"],
        "physical_steps_total": str(len(physical_rows)),
        "average_rows": str(len(avg_rows)),
        "average_start_time_iter": first["Time_Iter"],
        "average_end_time_iter": last["Time_Iter"],
        "mean_cd": f"{mean_cd:.10g}",
        "std_cd": f"{sample_std(cd_values):.10g}",
        "mean_cl": f"{mean_cl:.10g}",
        "std_cl": f"{sample_std(cl_values):.10g}",
        "mean_c_downforce": f"{mean_downforce:.10g}",
        "std_c_downforce": f"{sample_std([-value for value in cl_values]):.10g}",
        "mean_c_downforce_over_abs_cd": f"{(mean_downforce / abs(mean_cd)):.10g}" if mean_cd != 0.0 else "",
        "mean_cmy_cylinder": "" if mean_cmy_cylinder is None else f"{mean_cmy_cylinder:.10g}",
        "mean_motor_power_w_eta_0p8": "" if mean_motor_power is None else f"{mean_motor_power:.10g}",
        "mean_equivalent_drag_n_abs": "" if mean_equivalent_drag is None else f"{mean_equivalent_drag:.10g}",
        "mean_eta_net_abs_drag": "" if mean_eta_net is None else f"{mean_eta_net:.10g}",
        "last_time_iter": last["Time_Iter"],
        "last_inner_iter": last["Inner_Iter"],
        "last_rms_rho": last["rms[Rho]"],
        "solver_log": str((case_dir / "su2.log").relative_to(ROOT)) if (case_dir / "su2.log").exists() else "",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-dir", default="cases_urans_production")
    parser.add_argument("--output", default="results/urans_average_summary.csv")
    parser.add_argument("--start-time-iter", type=int)
    parser.add_argument("--last-fraction", type=float, default=0.5)
    args = parser.parse_args()

    case_root = ROOT / args.case_dir
    rows = []
    for case_dir in sorted(path for path in case_root.iterdir() if path.is_dir()):
        if (case_dir / "case.yaml").exists() and (case_dir / "history.csv").exists():
            rows.append(summarize_case(case_dir, args.start_time_iter, args.last_fraction))

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
        "physical_steps_total",
        "average_rows",
        "average_start_time_iter",
        "average_end_time_iter",
        "mean_cd",
        "std_cd",
        "mean_cl",
        "std_cl",
        "mean_c_downforce",
        "std_c_downforce",
        "mean_c_downforce_over_abs_cd",
        "mean_cmy_cylinder",
        "mean_motor_power_w_eta_0p8",
        "mean_equivalent_drag_n_abs",
        "mean_eta_net_abs_drag",
        "last_time_iter",
        "last_inner_iter",
        "last_rms_rho",
        "solver_log",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {output_path.relative_to(ROOT)} with {len(rows)} rows")


if __name__ == "__main__":
    main()
