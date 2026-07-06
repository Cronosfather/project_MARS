"""Generate Gmsh .geo files for the initial 3D finite wing cases."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "null":
        return None
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith("[") and value.endswith("]"):
        return ast.literal_eval(value)
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def load_simple_yaml(path: Path) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line:
            continue
        indent = len(line) - len(line.lstrip(" "))
        text = line.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if text.startswith("- "):
            item_text = text[2:]
            if isinstance(parent, list):
                if item_text.endswith(":"):
                    item: dict[str, Any] = {}
                    parent.append({item_text[:-1]: item})
                    stack.append((indent, item))
                elif ": " in item_text:
                    key, value = item_text.split(": ", 1)
                    item = {key: parse_scalar(value)}
                    parent.append(item)
                    stack.append((indent, item))
                else:
                    parent.append(parse_scalar(item_text))
            continue

        key, _, value = text.partition(":")
        if value.strip():
            parent[key] = parse_scalar(value)
            continue

        next_container: dict[str, Any] | list[Any]
        next_container = [] if key in {"initial"} else {}
        parent[key] = next_container
        stack.append((indent, next_container))

    return root


def read_airfoil(path: Path) -> list[tuple[float, float]]:
    coords: list[tuple[float, float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        x, z = line.split()[:2]
        coords.append((float(x), float(z)))
    if len(coords) < 4:
        raise ValueError(f"Not enough airfoil points in {path}")
    return coords


def configured_airfoil_path(config: dict[str, Any]) -> Path:
    geom = config["geometry"]
    if "airfoil_file" in geom:
        return ROOT / str(geom["airfoil_file"])
    prefix = "inverted_" if bool(geom.get("inverted", False)) else ""
    airfoil = str(geom["airfoil"]).upper()
    return ROOT / "geometry" / "airfoils" / f"{prefix}{airfoil}.dat"


def airfoil_geo_block(coords: list[tuple[float, float]], y_offset: float = 0.0) -> tuple[str, str]:
    point_lines: list[str] = []
    curve_ids: list[str] = []
    point_start = 10001
    curve_start = 11001
    for idx, (x, z) in enumerate(coords, start=1):
        point_id = point_start + idx - 1
        point_lines.append(f"Point({point_id}) = {{{x:.10f}, {y_offset:.10f}, {z:.10f}, wing_size}};")
    for idx in range(1, len(coords)):
        curve_id = curve_start + idx - 1
        point_a = point_start + idx - 1
        point_b = point_start + idx
        point_lines.append(f"Line({curve_id}) = {{{point_a}, {point_b}}};")
        curve_ids.append(str(curve_id))
    closing_id = curve_start + len(coords) - 1
    point_lines.append(f"Line({closing_id}) = {{{point_start + len(coords) - 1}, {point_start}}};")
    curve_ids.append(str(closing_id))
    return "\n".join(point_lines), ", ".join(curve_ids)


def cylinder_geo_block(include_cylinder: bool, span: float) -> tuple[str, str, str]:
    if not include_cylinder:
        return "", "", ""
    block = f"""
Cylinder(300) = {{cyl_x, 0.0, cyl_z, 0.0, {span:.10f}, 0.0, cyl_r, 2*Pi}};
cylinder_volume() = Volume In BoundingBox {{cyl_x - cyl_r - 1e-6, -1e-6, cyl_z - cyl_r - 1e-6,
                                           cyl_x + cyl_r + 1e-6, span + 1e-6, cyl_z + cyl_r + 1e-6}};
"""
    boolean_volume = "Volume{cylinder_volume()};"
    physical = 'Physical Surface("cylinder") = Surface In BoundingBox {cyl_x - cyl_r - 1e-6, -1e-6, cyl_z - cyl_r - 1e-6,\n                                                            cyl_x + cyl_r + 1e-6, span + 1e-6, cyl_z + cyl_r + 1e-6};'
    return block.strip(), boolean_volume, physical


def refinement_field_block(
    *,
    include_cylinder: bool,
    airfoil_x_min: float,
    airfoil_x_max: float,
    airfoil_z_min: float,
    airfoil_z_max: float,
    span: float,
    chord: float,
    cylinder_x: float,
    cylinder_z: float,
    cylinder_radius: float,
    ground_z: float,
    base_size: float,
    near_wall_size: float,
    ground_refine_size: float,
    wake_refine_size: float,
) -> str:
    """Create robust box-based near-wall and wake mesh refinement fields."""
    wing_pad_x = 0.20 * chord
    wing_pad_z = 0.12 * chord
    wing_pad_y = 0.04 * span
    ground_height = 0.25 * chord

    fields = [
        f"""Field[1] = Box;
Field[1].VIn = near_wall_size;
Field[1].VOut = base_size;
Field[1].XMin = {airfoil_x_min - wing_pad_x:.10f};
Field[1].XMax = {airfoil_x_max + wing_pad_x:.10f};
Field[1].YMin = {-wing_pad_y:.10f};
Field[1].YMax = {span + wing_pad_y:.10f};
Field[1].ZMin = {airfoil_z_min - wing_pad_z:.10f};
Field[1].ZMax = {airfoil_z_max + wing_pad_z:.10f};""",
        f"""Field[2] = Box;
Field[2].VIn = ground_refine_size;
Field[2].VOut = base_size;
Field[2].XMin = {-0.25 * chord:.10f};
Field[2].XMax = {2.50 * chord:.10f};
Field[2].YMin = {-0.10 * span:.10f};
Field[2].YMax = {1.10 * span:.10f};
Field[2].ZMin = {ground_z:.10f};
Field[2].ZMax = {ground_z + ground_height:.10f};""",
        f"""Field[3] = Box;
Field[3].VIn = wake_refine_size;
Field[3].VOut = base_size;
Field[3].XMin = {airfoil_x_min:.10f};
Field[3].XMax = {2.50 * chord:.10f};
Field[3].YMin = {-0.05 * span:.10f};
Field[3].YMax = {1.05 * span:.10f};
Field[3].ZMin = {airfoil_z_min - 0.15 * chord:.10f};
Field[3].ZMax = {airfoil_z_max + 0.20 * chord:.10f};""",
    ]
    field_ids = ["1", "2", "3"]

    if include_cylinder:
        cyl_pad = 2.5 * cylinder_radius
        fields.append(
            f"""Field[4] = Box;
Field[4].VIn = near_wall_size;
Field[4].VOut = base_size;
Field[4].XMin = {cylinder_x - cyl_pad:.10f};
Field[4].XMax = {cylinder_x + cyl_pad:.10f};
Field[4].YMin = {-0.04 * span:.10f};
Field[4].YMax = {span + 0.04 * span:.10f};
Field[4].ZMin = {cylinder_z - cyl_pad:.10f};
Field[4].ZMax = {cylinder_z + cyl_pad:.10f};"""
        )
        field_ids.append("4")

    fields.append(
        f"""Field[10] = Min;
Field[10].FieldsList = {{{", ".join(field_ids)}}};
Background Field = 10;"""
    )
    return "\n\n".join(fields)


def render_case(config: dict[str, Any], case: dict[str, Any], template: str, airfoil_path: Path) -> str:
    geom = config["geometry"]
    mesh = config["mesh"]
    coords = read_airfoil(airfoil_path)
    airfoil_points, airfoil_curve_ids = airfoil_geo_block(coords)
    x_values = [x for x, _ in coords]
    z_values = [z for _, z in coords]
    span = float(geom["span_m"])
    chord = float(geom["chord_m"])
    cylinder_x_over_c = float(case.get("cylinder_x_over_c", geom["cylinder_x_over_c"]))
    cylinder_z_over_c = float(case.get("cylinder_z_over_c", geom["cylinder_z_over_c"]))
    cylinder_radius = float(geom["cylinder_radius_m"])
    cylinder_x = cylinder_x_over_c * chord
    cylinder_z = cylinder_z_over_c * chord
    ground_z = -float(geom["ground_clearance_m"])
    base_size = float(mesh["base_size_m"])
    near_wall_size = float(mesh.get("near_wall_size_m", min(float(mesh["wing_size_m"]), float(mesh["cylinder_size_m"]))))
    ground_refine_size = float(mesh.get("ground_refine_size_m", max(near_wall_size * 2.0, float(mesh["wing_size_m"]))))
    wake_refine_size = float(mesh.get("wake_refine_size_m", max(near_wall_size * 3.0, float(mesh["wing_size_m"]))))
    cylinder_block, cylinder_boolean_volume, cylinder_physical_surface = cylinder_geo_block(
        bool(case["include_cylinder"]), span
    )
    refine_block = refinement_field_block(
        include_cylinder=bool(case["include_cylinder"]),
        airfoil_x_min=min(x_values),
        airfoil_x_max=max(x_values),
        airfoil_z_min=min(z_values),
        airfoil_z_max=max(z_values),
        span=span,
        chord=chord,
        cylinder_x=cylinder_x,
        cylinder_z=cylinder_z,
        cylinder_radius=cylinder_radius,
        ground_z=ground_z,
        base_size=base_size,
        near_wall_size=near_wall_size,
        ground_refine_size=ground_refine_size,
        wake_refine_size=wake_refine_size,
    )
    values = {
        "chord_m": chord,
        "span_m": span,
        "airfoil_x_min_m": min(x_values),
        "airfoil_x_max_m": max(x_values),
        "airfoil_z_min_m": min(z_values),
        "airfoil_z_max_m": max(z_values),
        "cylinder_radius_m": cylinder_radius,
        "cylinder_x_m": cylinder_x,
        "cylinder_z_m": cylinder_z,
        "ground_z_m": ground_z,
        "farfield_upstream_m": float(mesh["farfield_upstream_m"]),
        "farfield_downstream_m": float(mesh["farfield_downstream_m"]),
        "farfield_side_m": float(mesh["farfield_side_m"]),
        "farfield_top_m": float(mesh["farfield_top_m"]),
        "base_size_m": base_size,
        "wing_size_m": float(mesh["wing_size_m"]),
        "cylinder_size_m": float(mesh["cylinder_size_m"]),
        "near_wall_size_m": near_wall_size,
        "ground_refine_size_m": ground_refine_size,
        "wake_refine_size_m": wake_refine_size,
        "airfoil_point_block": airfoil_points,
        "airfoil_curve_ids": airfoil_curve_ids,
        "cylinder_block": cylinder_block,
        "cylinder_boolean_volume": cylinder_boolean_volume,
        "cylinder_physical_surface": cylinder_physical_surface,
        "refinement_field_block": refine_block,
    }
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{" + key + "}", str(value))
    return rendered


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/project_config.yaml")
    parser.add_argument("--airfoil", default=None)
    parser.add_argument("--template", default="geometry/gmsh_templates/finite_wing.geo.tpl")
    parser.add_argument("--output-dir", default="geometry/generated")
    args = parser.parse_args()

    config = load_simple_yaml(ROOT / args.config)
    template = (ROOT / args.template).read_text(encoding="utf-8")
    airfoil_path = ROOT / args.airfoil if args.airfoil else configured_airfoil_path(config)
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    for case in config["cases"]["initial"]:
        name = case["name"]
        geo = render_case(config, case, template, airfoil_path)
        output_path = output_dir / f"{name}.geo"
        output_path.write_text(geo, encoding="utf-8")
        print(f"Wrote {output_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
