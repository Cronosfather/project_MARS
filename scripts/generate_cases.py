"""Generate SU2 case directories from project_config.yaml."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

from generate_geometry import load_simple_yaml


ROOT = Path(__file__).resolve().parents[1]
SPEED_OF_SOUND_M_S = 340.294


def render_template(template: str, values: dict[str, Any]) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{" + key + "}", str(value))
    return rendered


def case_values(config: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    geom = config["geometry"]
    flow = config["flow"]
    chord = float(geom["chord_m"])
    span = float(geom["span_m"])
    u_inf = float(case["u_inf_m_s"])
    include_cylinder = bool(case["include_cylinder"])
    cylinder_x_over_c = float(case.get("cylinder_x_over_c", geom["cylinder_x_over_c"]))
    cylinder_z_over_c = float(case.get("cylinder_z_over_c", geom["cylinder_z_over_c"]))
    cylinder_marker = ", cylinder" if include_cylinder else ""
    solid_wall_markers = "wing, cylinder, ground" if include_cylinder else "wing, ground"

    lam = case.get("lambda")
    omega_rad_s = None
    rpm = None
    if lam is not None:
        radius = float(geom["cylinder_radius_m"])
        omega_rad_s = float(lam) * u_inf / radius
        rpm = omega_rad_s * 60.0 / (2.0 * math.pi)

    moving_markers = ["ground"]
    surface_movements = ["MOVING_WALL"]
    motion_origins = [(0.0, 0.0, 0.0)]
    translation_rates = [(u_inf, 0.0, 0.0)]
    rotation_rates = [(0.0, 0.0, 0.0)]
    if include_cylinder and lam not in {None, 0.0}:
        moving_markers.append("cylinder")
        surface_movements.append("MOVING_WALL")
        motion_origins.append(
            (
                cylinder_x_over_c * chord,
                0.0,
                cylinder_z_over_c * chord,
            )
        )
        translation_rates.append((0.0, 0.0, 0.0))
        rotation_rates.append((0.0, float(omega_rad_s), 0.0))

    def flat_vector(values: list[tuple[float, float, float]]) -> str:
        return ", ".join(f"{component:.8f}" for vector in values for component in vector)

    return {
        "mesh_filename": f"../../geometry/generated/{case['name']}.su2",
        "mach_number": f"{u_inf / SPEED_OF_SOUND_M_S:.8f}",
        "angle_of_attack_deg": float(geom["angle_of_attack_deg"]),
        "density_kg_m3": float(flow["density_kg_m3"]),
        "viscosity_kg_ms": float(flow["viscosity_kg_ms"]),
        "reynolds_number": f"{float(flow['density_kg_m3']) * u_inf * chord / float(flow['viscosity_kg_ms']):.8f}",
        "chord_m": chord,
        "reference_area_m2": chord * span,
        "cylinder_marker": cylinder_marker,
        "solid_wall_markers": solid_wall_markers,
        "adiabatic_wall_markers": ", ".join(f"{marker}, 0.0" for marker in solid_wall_markers.split(", ")),
        "moving_markers": ", ".join(moving_markers),
        "surface_movements": ", ".join(surface_movements),
        "surface_motion_origins": flat_vector(motion_origins),
        "surface_translation_rates": flat_vector(translation_rates),
        "surface_rotation_rates": flat_vector(rotation_rates),
        "case_name": case["name"],
        "u_inf_m_s": u_inf,
        "cylinder_x_over_c": "none" if not include_cylinder else f"{cylinder_x_over_c:.8f}",
        "cylinder_z_over_c": "none" if not include_cylinder else f"{cylinder_z_over_c:.8f}",
        "lambda": "none" if lam is None else lam,
        "omega_rad_s": "none" if omega_rad_s is None else f"{omega_rad_s:.8f}",
        "rpm": "none" if rpm is None else f"{rpm:.8f}",
    }


def write_case_metadata(path: Path, values: dict[str, Any]) -> None:
    lines = [
        f"name: {values['case_name']}",
        f"u_inf_m_s: {values['u_inf_m_s']}",
        f"cylinder_x_over_c: {values['cylinder_x_over_c']}",
        f"cylinder_z_over_c: {values['cylinder_z_over_c']}",
        f"mach_number: {values['mach_number']}",
        f"lambda: {values['lambda']}",
        f"omega_rad_s: {values['omega_rad_s']}",
        f"rpm: {values['rpm']}",
        f"mesh_filename: {values['mesh_filename']}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/project_config.yaml")
    parser.add_argument("--template", default="config/su2_template.cfg")
    parser.add_argument("--case-dir", default="cases")
    args = parser.parse_args()

    config = load_simple_yaml(ROOT / args.config)
    template = (ROOT / args.template).read_text(encoding="utf-8")
    case_root = ROOT / args.case_dir
    case_root.mkdir(parents=True, exist_ok=True)

    for case in config["cases"]["initial"]:
        values = case_values(config, case)
        out_dir = case_root / case["name"]
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "config.cfg").write_text(render_template(template, values), encoding="utf-8")
        write_case_metadata(out_dir / "case.yaml", values)
        print(f"Wrote {out_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
