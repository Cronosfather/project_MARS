#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

python3 scripts/run_case.py \
  inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0 \
  --case-dir cases_urans_production \
  --threads 4
