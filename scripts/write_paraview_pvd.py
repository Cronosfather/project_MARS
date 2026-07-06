"""Write a ParaView .pvd index for SU2 flow_*.vtu outputs."""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path


VTU_STEP_RE = re.compile(r"_(\d+)\.vtu$")


def step_from_name(path: Path) -> int:
    match = VTU_STEP_RE.search(path.name)
    if not match:
        raise ValueError(f"Could not parse time step from {path.name}")
    return int(match.group(1))


def indent(element: ET.Element, level: int = 0) -> None:
    padding = "\n" + level * "  "
    child_padding = "\n" + (level + 1) * "  "
    if len(element):
        if not element.text or not element.text.strip():
            element.text = child_padding
        for child in element:
            indent(child, level + 1)
        if not element[-1].tail or not element[-1].tail.strip():
            element[-1].tail = padding
    if level and (not element.tail or not element.tail.strip()):
        element.tail = padding


def write_pvd(case_dir: Path, pattern: str, output: Path, time_step: float) -> int:
    vtu_files = sorted(case_dir.glob(pattern), key=step_from_name)
    if not vtu_files:
        raise FileNotFoundError(f"No VTU files matching {pattern} in {case_dir}")

    root = ET.Element("VTKFile", type="Collection", version="0.1", byte_order="LittleEndian")
    collection = ET.SubElement(root, "Collection")

    for vtu_file in vtu_files:
        step = step_from_name(vtu_file)
        ET.SubElement(
            collection,
            "DataSet",
            timestep=f"{step * time_step:.12g}",
            group="",
            part="0",
            file=vtu_file.name,
        )

    indent(root)
    tree = ET.ElementTree(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output, encoding="utf-8", xml_declaration=True)
    return len(vtu_files)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--pattern", default="flow_*.vtu")
    parser.add_argument("--output", default="flow_timeseries.pvd")
    parser.add_argument("--time-step", type=float, default=4.18879020479e-5)
    args = parser.parse_args()

    case_dir = args.case_dir
    output = case_dir / args.output
    count = write_pvd(case_dir, args.pattern, output, args.time_step)
    print(f"Wrote {output} with {count} VTU files")


if __name__ == "__main__":
    main()
