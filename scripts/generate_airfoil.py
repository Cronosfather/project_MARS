"""Generate NACA 4-digit airfoil coordinate files."""

from __future__ import annotations

import argparse
import math
from pathlib import Path


def cosine_spacing(n: int) -> list[float]:
    if n < 3:
        raise ValueError("n must be at least 3")
    return [0.5 * (1.0 - math.cos(math.pi * i / (n - 1))) for i in range(n)]


def parse_naca_4_digit(airfoil: str) -> tuple[float, float, float]:
    code = airfoil.upper().replace("NACA", "").strip()
    if len(code) != 4 or not code.isdigit():
        raise ValueError(f"Expected a NACA 4-digit airfoil, got {airfoil!r}")
    max_camber = int(code[0]) / 100.0
    camber_position = int(code[1]) / 10.0
    thickness = int(code[2:]) / 100.0
    return max_camber, camber_position, thickness


def naca_4_digit(airfoil: str, chord: float, n: int) -> list[tuple[float, float]]:
    max_camber, camber_position, thickness = parse_naca_4_digit(airfoil)
    x_values = cosine_spacing(n)
    upper: list[tuple[float, float]] = []
    lower: list[tuple[float, float]] = []

    for x_over_c in x_values:
        yt = 5.0 * thickness * chord * (
            0.2969 * math.sqrt(x_over_c)
            - 0.1260 * x_over_c
            - 0.3516 * x_over_c**2
            + 0.2843 * x_over_c**3
            - 0.1015 * x_over_c**4
        )
        if max_camber == 0.0 or camber_position == 0.0:
            yc = 0.0
            dyc_dx = 0.0
        elif x_over_c < camber_position:
            yc = max_camber / camber_position**2 * (
                2.0 * camber_position * x_over_c - x_over_c**2
            )
            dyc_dx = 2.0 * max_camber / camber_position**2 * (camber_position - x_over_c)
        else:
            yc = max_camber / (1.0 - camber_position) ** 2 * (
                (1.0 - 2.0 * camber_position) + 2.0 * camber_position * x_over_c - x_over_c**2
            )
            dyc_dx = 2.0 * max_camber / (1.0 - camber_position) ** 2 * (camber_position - x_over_c)

        theta = math.atan(dyc_dx)
        x = x_over_c * chord
        zc = yc * chord
        upper.append((x - yt * math.sin(theta), zc + yt * math.cos(theta)))
        lower.append((x + yt * math.sin(theta), zc - yt * math.cos(theta)))

    # Closed loop: trailing edge upper -> leading edge -> trailing edge lower.
    return list(reversed(upper)) + lower[1:]


def write_dat(path: Path, coords: list[tuple[float, float]], inverted: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("# x_m z_m\n")
        for x, z in coords:
            if inverted:
                z = -z
            f.write(f"{x:.10f} {z:.10f}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--airfoil", default="NACA6412")
    parser.add_argument("--output", default=None)
    parser.add_argument("--chord", type=float, default=0.30)
    parser.add_argument("--points", type=int, default=101)
    parser.add_argument("--inverted", action="store_true", default=True)
    args = parser.parse_args()

    output = args.output
    if output is None:
        prefix = "inverted_" if args.inverted else ""
        output = f"geometry/airfoils/{prefix}{args.airfoil.upper()}.dat"

    coords = naca_4_digit(args.airfoil, args.chord, args.points)
    write_dat(Path(output), coords, args.inverted)
    print(f"Wrote {len(coords)} points to {output}")


if __name__ == "__main__":
    main()
