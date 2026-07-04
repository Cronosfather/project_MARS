"""Generate NACA 4-digit airfoil coordinate files."""

from __future__ import annotations

import argparse
import math
from pathlib import Path


def cosine_spacing(n: int) -> list[float]:
    if n < 3:
        raise ValueError("n must be at least 3")
    return [0.5 * (1.0 - math.cos(math.pi * i / (n - 1))) for i in range(n)]


def naca_4_digit_symmetric(thickness: float, chord: float, n: int) -> list[tuple[float, float]]:
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
        x = x_over_c * chord
        upper.append((x, yt))
        lower.append((x, -yt))

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
    parser.add_argument("--output", default="geometry/airfoils/inverted_NACA0012.dat")
    parser.add_argument("--chord", type=float, default=0.30)
    parser.add_argument("--points", type=int, default=101)
    parser.add_argument("--thickness", type=float, default=0.12)
    parser.add_argument("--inverted", action="store_true", default=True)
    args = parser.parse_args()

    coords = naca_4_digit_symmetric(args.thickness, args.chord, args.points)
    write_dat(Path(args.output), coords, args.inverted)
    print(f"Wrote {len(coords)} points to {args.output}")


if __name__ == "__main__":
    main()
