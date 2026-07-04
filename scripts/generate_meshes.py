"""Generate SU2 meshes from generated Gmsh .geo files."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from generate_geometry import load_simple_yaml


ROOT = Path(__file__).resolve().parents[1]


def configured_cases(config_path: Path) -> list[str]:
    config = load_simple_yaml(config_path)
    return [case["name"] for case in config["cases"]["initial"]]


def generate_mesh(case_name: str, gmsh: str, output_dir: Path) -> None:
    geo_path = output_dir / f"{case_name}.geo"
    su2_path = output_dir / f"{case_name}.su2"
    log_path = output_dir / f"{case_name}_su2_export.log"
    if not geo_path.exists():
        raise FileNotFoundError(f"Missing generated geometry: {geo_path}")

    cmd = [gmsh, "-3", str(geo_path), "-format", "su2", "-o", str(su2_path)]
    with log_path.open("w", encoding="utf-8") as log:
        subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    print(f"Wrote {su2_path.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/project_config.yaml")
    parser.add_argument("--output-dir", default="geometry/generated")
    parser.add_argument("--gmsh", default=shutil.which("gmsh") or "gmsh")
    parser.add_argument("--case", action="append", help="Case name to mesh; repeat for multiple cases")
    args = parser.parse_args()

    output_dir = ROOT / args.output_dir
    cases = args.case or configured_cases(ROOT / args.config)
    for case_name in cases:
        generate_mesh(case_name, args.gmsh, output_dir)


if __name__ == "__main__":
    main()
