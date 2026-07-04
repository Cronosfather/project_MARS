"""Run one generated SU2 case."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SU2_CFD = shutil.which("SU2_CFD") or "/home/ragnarok/opt/su2/bin/SU2_CFD"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", help="Case directory name under cases/")
    parser.add_argument("--dry-run", action="store_true", help="Only run SU2 preprocessing checks")
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()

    case_dir = ROOT / "cases" / args.case
    cfg = case_dir / "config.cfg"
    if not cfg.exists():
        raise FileNotFoundError(f"Missing case config: {cfg}")

    cmd = [SU2_CFD, "-t", str(args.threads)]
    if args.dry_run:
        cmd.append("--dryrun")
    cmd.append("config.cfg")
    log_name = "su2_dryrun.log" if args.dry_run else "su2.log"
    with (case_dir / log_name).open("w", encoding="utf-8") as log:
        subprocess.run(cmd, cwd=case_dir, stdout=log, stderr=subprocess.STDOUT, check=True)
    print(f"Wrote {case_dir.relative_to(ROOT) / log_name}")


if __name__ == "__main__":
    main()
