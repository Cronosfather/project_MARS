# 현재 프로젝트 상태

## 한 줄 요약

이 프로젝트는 자동차 전체 형상을 직접 해석하지 않고, 자동차용 리어윙을 단순화한 3D finite wing 모델에 회전 실린더를 적용하여 다운포스 증가와 모터 전력 보정 후 순효율을 평가하는 CFD 연구이다.

## 현재 기준

- 정리일: 2026-07-06
- 현재 단계: NACA0012 검증 baseline과 NACA6412 성능 평가용 초기 케이스의 geometry/mesh/SU2 dry-run 파이프라인 구축 완료
- 추가 진행: NACA6412 RANS moving-wall smoke-test, 회전 방향 반전, 실린더 위치 sweep, 일차 후보 200 iteration 수렴성 점검, refined mesh 계산, stable 300 iteration 비교 완료
- 핵심 주의점: 현재까지의 steady RANS 결과로는 회전 실린더 다운포스 증가를 입증하지 못했다. Stable 300 설정에서도 residual과 force가 완전히 수렴하지 않았고, rotating candidate의 다운포스 개선은 재현되지 않았다.

## 연구 방향

- 자동차 전체 형상은 제외한다.
- 2D airfoil 단면을 span 방향으로 extrusion한 3D finite wing을 사용한다.
- 리어윙 leading edge 근처에 회전 실린더를 배치한다.
- 회전 실린더의 마그누스 효과가 다운포스와 효율에 미치는 영향을 평가한다.
- moving ground 조건을 포함한다.
- 최종 결론은 자동차 전체 공력 성능이 아니라 자동차용 리어윙 단품 수준의 가능성 평가로 제한한다.

## 익형 전략

- 검증용 baseline: inverted NACA0012
- 성능 평가용 기본 익형: inverted NACA6412

NACA0012는 대칭 익형이므로 geometry, mesh, marker, solver I/O 검증용으로 유지한다. 실제 다운포스 성능 비교는 camber가 있는 inverted NACA6412를 기본으로 진행한다.

## 해석 대상

### 기본 리어윙

- Chord length: 0.30 m
- Span: 1.20 m
- Aspect ratio: 4.0
- Angle of attack: 0.0 deg로 시작
- Endplate: 초기 범위에서는 제외

### 회전 실린더

- 반지름 R: 0.02 m
- 길이: 리어윙 span과 동일
- 위치: chord 기준 x/c = 0.08, z/c = 0.10
- 회전 조건: RPM 직접 지정이 아니라 속도비 lambda로 정의

### 지면 조건

- Ground clearance: 0.20 m
- RANS/moving-wall 템플릿에서 ground moving wall 설정 dry-run 통과

## 주요 케이스

NACA0012 검증 케이스:

1. `wing_only_U30`
2. `wing_cylinder_static_U30`
3. `wing_cylinder_rotating_U30_lam1p0`
4. `wing_cylinder_rotating_U30_lam2p0`

NACA6412 성능 평가용 초기 케이스:

1. `inv6412_wing_only_U30`
2. `inv6412_wing_cylinder_static_U30`
3. `inv6412_wing_cylinder_rotating_U30_lam1p0`
4. `inv6412_wing_cylinder_rotating_U30_lam2p0`
5. `inv6412_wing_cylinder_rotating_U30_lamneg1p0`
6. `inv6412_wing_cylinder_rotating_U30_lamneg2p0`
7. `inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0`
8. `inv6412_wing_cylinder_rotating_x0p050_z0p100_U30_lam1p0`
9. `inv6412_wing_cylinder_rotating_x0p120_z0p100_U30_lam1p0`
10. `inv6412_wing_cylinder_rotating_x0p160_z0p100_U30_lam1p0`
11. `inv6412_wing_cylinder_rotating_x0p000_z0p100_U30_lam1p0`
12. `inv6412_wing_cylinder_rotating_x0p010_z0p100_U30_lam1p0`
13. `inv6412_wing_cylinder_rotating_x0p030_z0p100_U30_lam1p0`
14. `inv6412_wing_cylinder_rotating_x0p040_z0p100_U30_lam1p0`
15. `inv6412_wing_cylinder_rotating_x0p020_z0p080_U30_lam1p0`
16. `inv6412_wing_cylinder_rotating_x0p020_z0p120_U30_lam1p0`

## 작성된 자동화 코드

- `scripts/generate_airfoil.py`: NACA 4-digit airfoil 좌표 생성. NACA0012와 NACA6412 모두 지원
- `scripts/generate_geometry.py`: config와 Gmsh template 기반 `.geo` 생성. wing/cylinder/ground/wake box 기반 near-wall refinement field 지원
- `scripts/generate_cases.py`: SU2 `config.cfg`, `case.yaml` 생성
- `scripts/generate_meshes.py`: Gmsh를 실행하여 SU2 `.su2` mesh 생성
- `scripts/run_case.py`: 단일 SU2 케이스 dry-run 또는 solver 실행. `--case-dir` 지원
- `scripts/postprocess_cases.py`: 완료된 `history.csv`를 모아 `results/summary.csv` 생성

## 주요 설정 파일

- `config/project_config.yaml`: 기본 형상과 초기 케이스 정의. 현재 기본 airfoil은 NACA6412
- `config/su2_template.cfg`: Euler 파이프라인 검증용 템플릿
- `config/su2_template_rans_moving_wall.cfg`: 실험용 RANS/moving-wall 템플릿
- `geometry/gmsh_templates/finite_wing.geo.tpl`: Gmsh 3D finite wing template

## 완료한 일

- NACA0012 baseline airfoil 생성
- NACA6412 cambered airfoil 생성
- NACA6412 좌표가 chord 범위를 약간 벗어나던 문제를 처리하도록 Gmsh wing bounding box를 실제 airfoil 좌표 범위 기반으로 수정
- NACA6412 초기 4개 케이스 `.geo` 생성 완료
- NACA6412 초기 4개 케이스 SU2 `.su2` mesh 생성 완료
- NACA6412 초기 4개 케이스 Euler dry-run 통과
- `inv6412_wing_only_U30` Euler 200 iteration 실행 완료
- `inv6412_wing_cylinder_static_U30` Euler 200 iteration 실행 완료
- RANS/moving-wall 템플릿 작성
- `cases_rans/`에 NACA6412 RANS/moving-wall config 생성
- RANS/moving-wall dry-run 4개 케이스 통과
- SU2 로그에서 `Surface(s) in motion: ground, cylinder` 및 `Setting the moving wall velocities.` 확인
- RANS/moving-wall 50 iteration smoke-test 4개 케이스 실행 완료
- RANS history에 marker별 `CD(wing)`, `CD(cylinder)`, `CMy(cylinder)` 등 per-surface 계수 출력 확인
- cylinder `CMy(cylinder)` 기반 임시 motor power 계산을 `results/rans_smoke_summary.csv`에 추가
- 회전 방향 반전 케이스 `lambda = -1.0`, `lambda = -2.0` smoke-test 완료
- 사용자가 요청을 정정하여 반지름 sweep 산출물은 삭제하고, 회전 방향 반전 케이스로 대체
- 실린더 x 위치 sweep smoke-test 완료: `x/c = 0.02, 0.05, 0.12, 0.16`, `z/c = 0.10`, `lambda = 1.0`
- 일차 후보 `x/c = 0.02`, `z/c = 0.10` 주변 보강 sweep 완료: `x/c = 0.00, 0.01, 0.03, 0.04`, `z/c = 0.08, 0.12`
- `results/summary.csv` 생성 스크립트 작성 및 실행
- 200 iteration RANS/moving-wall 수렴성 점검 완료: wing-only, static cylinder, 일차 후보 rotating case
- 200 iteration 결과를 `results/rans_200_summary.csv`로 정리
- `scripts/postprocess_cases.py`에 마지막 50 iteration force drift 진단 컬럼 추가
- Gmsh background field 기반 coarse near-wall refinement 추가
- refined mesh 3개 생성 완료: wing-only, static cylinder, 일차 후보 rotating case
- refined mesh 대표 3개 케이스 SU2 dry-run 통과
- refined mesh 대표 3개 케이스 RANS/moving-wall 50 iteration smoke-test 완료
- refined mesh 50 iteration 결과를 `results/rans_refined_50_summary.csv`로 정리
- refined mesh 일차 후보 rotating case 200 iteration 실행 완료
- refined mesh 200 iteration 결과를 `results/rans_refined_200_summary.csv`로 정리
- stable 300 설정 작성: `config/su2_template_rans_moving_wall_stable_300.cfg`
- stable 300 비교 완료: wing-only, static cylinder, rotating candidate
- stable 300 결과를 `results/rans_stable_300_summary.csv`로 정리
- 10000 iteration long-run 템플릿 작성: `config/su2_template_rans_moving_wall_long_10000.cfg`
- 10000 iteration long-run 케이스 생성: `cases_rans_long_10000/`
- long-run 후보 케이스 dry-run 통과: `inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0`
- 연구 마무리 요약 작성: `docs/research_closure_summary.md`

## 케이스별 최신 상태

| Case | Euler mesh | Euler dry-run | Euler solver run | RANS/moving-wall dry-run | 비고 |
|---|---:|---:|---:|---:|---|
| `wing_only_U30` | 완료 | 통과 | 완료 | 미생성 | NACA0012 baseline |
| `wing_cylinder_static_U30` | 완료 | 통과 | 완료 | 미생성 | NACA0012 baseline |
| `wing_cylinder_rotating_U30_lam1p0` | 완료 | 통과 | 미실행 | 미생성 | Euler에서는 회전 물리 없음 |
| `wing_cylinder_rotating_U30_lam2p0` | 미완료 | 미완료 | 미실행 | 미생성 | NACA0012 후순위 |
| `inv6412_wing_only_U30` | 완료 | 통과 | 완료 | 통과 및 50 iter 실행 | 성능 평가용 baseline |
| `inv6412_wing_cylinder_static_U30` | 완료 | 통과 | 완료 | 통과 및 50 iter 실행 | static cylinder 비교군 |
| `inv6412_wing_cylinder_rotating_U30_lam1p0` | 완료 | 통과 | 미실행 | 통과 및 50 iter 실행 | moving ground + rotating cylinder |
| `inv6412_wing_cylinder_rotating_U30_lam2p0` | 완료 | 통과 | 미실행 | 통과 및 50 iter 실행 | moving ground + rotating cylinder |
| `inv6412_wing_cylinder_rotating_U30_lamneg1p0` | 완료 | 통과 | 미실행 | 통과 및 50 iter 실행 | 회전 방향 반전 |
| `inv6412_wing_cylinder_rotating_U30_lamneg2p0` | 완료 | 통과 | 미실행 | 통과 및 50 iter 실행 | 회전 방향 반전 |
| `inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0` | 완료 | 통과 | 미실행 | 통과 및 50 iter 실행 | 위치 sweep |
| `inv6412_wing_cylinder_rotating_x0p050_z0p100_U30_lam1p0` | 완료 | 통과 | 미실행 | 통과 및 50 iter 실행 | 위치 sweep |
| `inv6412_wing_cylinder_rotating_x0p120_z0p100_U30_lam1p0` | 완료 | 통과 | 미실행 | 통과 및 50 iter 실행 | 위치 sweep |
| `inv6412_wing_cylinder_rotating_x0p160_z0p100_U30_lam1p0` | 완료 | 통과 | 미실행 | 통과 및 50 iter 실행 | 위치 sweep |
| `inv6412_wing_cylinder_rotating_x0p000_z0p100_U30_lam1p0` | 완료 | 통과 | 미실행 | 통과 및 50 iter 실행 | 후보 주변 sweep |
| `inv6412_wing_cylinder_rotating_x0p010_z0p100_U30_lam1p0` | 완료 | 통과 | 미실행 | 통과 및 50 iter 실행 | 후보 주변 sweep |
| `inv6412_wing_cylinder_rotating_x0p030_z0p100_U30_lam1p0` | 완료 | 통과 | 미실행 | 통과 및 50 iter 실행 | 후보 주변 sweep |
| `inv6412_wing_cylinder_rotating_x0p040_z0p100_U30_lam1p0` | 완료 | 통과 | 미실행 | 통과 및 50 iter 실행 | 후보 주변 sweep |
| `inv6412_wing_cylinder_rotating_x0p020_z0p080_U30_lam1p0` | 완료 | 통과 | 미실행 | 통과 및 50 iter 실행 | 후보 주변 sweep |
| `inv6412_wing_cylinder_rotating_x0p020_z0p120_U30_lam1p0` | 완료 | 통과 | 미실행 | 통과 및 50 iter 실행 | 후보 주변 sweep |

200 iteration RANS/moving-wall 추가 확인:

| Case | 200 iter RANS | 비고 |
|---|---:|---|
| `inv6412_wing_only_U30` | 완료 | force drift 큼, 최종 성능 판단 금지 |
| `inv6412_wing_cylinder_static_U30` | 완료 | force drift 큼, 최종 성능 판단 금지 |
| `inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0` | 완료 | 일차 후보 수렴성 점검 완료, 아직 미수렴 |

coarse near-wall refined mesh 추가 확인:

| Case | Refined mesh | Nodes | Tetrahedra | 비고 |
|---|---:|---:|---:|---|
| `inv6412_wing_only_U30` | 완료 | 245607 | 1571683 | dry-run 및 50 iter 완료 |
| `inv6412_wing_cylinder_static_U30` | 완료 | 244539 | 1571383 | dry-run 및 50 iter 완료 |
| `inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0` | 완료 | 247616 | 1591475 | dry-run 및 50 iter 완료 |

refined mesh는 최종 prism boundary-layer mesh가 아니라, wing/cylinder/ground/wake 주변에 box-based background field를 추가한 coarse near-wall refinement다. 첫 목적은 solver 안정성과 force drift 개선 여부 확인이다.

## 최근 Euler 검증 결과

현재 결과는 파이프라인 검증용이다. 수렴 목표 `rms[Rho] = -8`에는 도달하지 않았고, Euler이므로 점성, 벽면 전단, 난류, 회전벽 torque를 반영하지 않는다.

| Case | Iter | rms[Rho] | CD | CL | C_DF = -CL |
|---|---:|---:|---:|---:|---:|
| `wing_only_U30` | 199 | -5.99611 | -0.18577 | 0.02245 | -0.02245 |
| `wing_cylinder_static_U30` | 199 | -5.45736 | -0.31027 | 0.40834 | -0.40834 |
| `inv6412_wing_only_U30` | 199 | -6.07510 | -0.19234 | -0.36796 | 0.36796 |
| `inv6412_wing_cylinder_static_U30` | 199 | -5.41136 | -0.24823 | -0.21530 | 0.21530 |

`results/summary.csv`에는 위 계산이 자동 요약되어 있다. 현재 drag 부호는 SU2 좌표/방향 convention 영향을 받으므로 `cd_abs`와 `c_downforce_over_abs_cd`도 함께 저장한다.

## RANS/moving-wall smoke-test 상태

템플릿: `config/su2_template_rans_moving_wall.cfg`

현재 smoke-test iteration: `ITER = 50`

사용한 주요 SU2 설정:

```text
MARKER_HEATFLUX
MARKER_MOVING
SURFACE_MOVEMENT
SURFACE_MOTION_ORIGIN
SURFACE_TRANSLATION_RATE
SURFACE_ROTATION_RATE
```

확인된 내용:

- `inv6412_wing_only_U30`: ground가 moving surface로 인식됨
- `inv6412_wing_cylinder_static_U30`: ground moving wall, wing/cylinder heat-flux wall 인식
- `inv6412_wing_cylinder_rotating_U30_lam1p0`: ground와 cylinder가 moving surface로 인식됨
- `inv6412_wing_cylinder_rotating_U30_lam2p0`: ground와 cylinder가 moving surface로 인식됨

50 iteration smoke-test 결과:

| Case | lambda | Iter | rms[Rho] | CD | CL | C_DF | CMy(cylinder) | P_motor eta=0.8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `inv6412_wing_only_U30` | none | 49 | -3.19961 | 0.64826 | -3.80122 | 3.80122 |  |  |
| `inv6412_wing_cylinder_static_U30` | 0.0 | 49 | -3.18224 | 2.66733 | -1.18207 | 1.18207 | 0.27985 | 0 W |
| `inv6412_wing_cylinder_rotating_U30_lam1p0` | 1.0 | 49 | -3.18263 | 2.30144 | -1.29713 | 1.29713 | 0.27112 | 30262.98 W |
| `inv6412_wing_cylinder_rotating_U30_lam2p0` | 2.0 | 49 | -3.18349 | 1.94534 | -1.43117 | 1.43117 | 0.25613 | 57179.44 W |
| `inv6412_wing_cylinder_rotating_U30_lamneg1p0` | -1.0 | 49 | -3.18238 | 3.04137 | -1.08356 | 1.08356 | 0.28256 | 1654.86 W |
| `inv6412_wing_cylinder_rotating_U30_lamneg2p0` | -2.0 | 49 | -3.18305 | 3.42194 | -1.00170 | 1.00170 | 0.27930 | 2757.43 W |
| `inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0` | 1.0 | 49 | -3.17859 | 2.11996 | -2.33021 | 2.33021 | 0.29504 | 33045.63 W |
| `inv6412_wing_cylinder_rotating_x0p050_z0p100_U30_lam1p0` | 1.0 | 49 | -3.18200 | 2.15882 | -1.68693 | 1.68693 | 0.25337 | 28378.03 W |
| `inv6412_wing_cylinder_rotating_x0p120_z0p100_U30_lam1p0` | 1.0 | 49 | -3.19298 | 2.44781 | -1.00195 | 1.00195 | 0.24487 | 27425.48 W |
| `inv6412_wing_cylinder_rotating_x0p160_z0p100_U30_lam1p0` | 1.0 | 49 | -3.19935 | 2.70119 | -1.09450 | 1.09450 | 0.26632 | 29828.97 W |
| `inv6412_wing_cylinder_rotating_x0p000_z0p100_U30_lam1p0` | 1.0 | 49 | -3.17859 | 2.18443 | -2.38679 | 2.38679 | 0.36018 | 40269.61 W |
| `inv6412_wing_cylinder_rotating_x0p010_z0p100_U30_lam1p0` | 1.0 | 49 | -3.18120 | 2.18182 | -2.17210 | 2.17210 | 0.34611 | 38695.71 W |
| `inv6412_wing_cylinder_rotating_x0p030_z0p100_U30_lam1p0` | 1.0 | 49 | -3.18069 | 2.13735 | -2.03214 | 2.03214 | 0.29571 | 33120.59 W |
| `inv6412_wing_cylinder_rotating_x0p040_z0p100_U30_lam1p0` | 1.0 | 49 | -3.18108 | 2.15790 | -1.82631 | 1.82631 | 0.28252 | 31642.72 W |
| `inv6412_wing_cylinder_rotating_x0p020_z0p080_U30_lam1p0` | 1.0 | 49 | -3.19614 | 2.17059 | -0.94916 | 0.94916 | 0.63219 | 70804.62 W |
| `inv6412_wing_cylinder_rotating_x0p020_z0p120_U30_lam1p0` | 1.0 | 49 | -3.18448 | 2.84040 | -1.44337 | 1.44337 | 0.41011 | 45922.17 W |

위 값은 아직 수렴 전 smoke-test 값이다. 회전 조건과 marker별 후처리 파이프라인이 동작한다는 확인용으로만 사용한다.

현재 smoke-test 기준으로는 양의 회전 방향이 static cylinder보다 다운포스를 늘리고, 음의 회전 방향은 static cylinder보다 다운포스를 줄인다. 따라서 현재 SU2 회전 방향 convention에서는 `lambda > 0` 방향이 의도한 다운포스 증가 방향에 더 가깝다. 단, 아직 미수렴 smoke-test이므로 정량 결론은 금지한다.

위치 sweep 기준으로는 `x/c = 0.02`, `z/c = 0.10`, `lambda = 1.0`이 현재 테스트한 위치 중 가장 높은 `C_DF = 2.33021`을 보였다. 여전히 wing-only `C_DF = 3.80122`보다 낮지만, 기존 위치 `x/c = 0.08`의 `C_DF = 1.29713`보다는 크게 개선됐다. 다음 위치 탐색은 `x/c = 0.00~0.04` 근방과 `z/c` 변화가 우선이다.

후보 주변 보강 sweep에서는 순수 다운포스만 보면 `x/c = 0.00`, `z/c = 0.10`이 `C_DF = 2.38679`로 가장 컸다. 그러나 motor power 보정 후 `eta_net_abs_drag`는 `x/c = 0.02`, `z/c = 0.10`이 더 높다. 따라서 일차 후보는 `x/c = 0.02`, `z/c = 0.10`, `lambda = 1.0`으로 고정한다.

RANS smoke summary:

```text
results/rans_smoke_summary.csv
```

## 200 iteration RANS/moving-wall 수렴성 점검

템플릿: `config/su2_template_rans_moving_wall_200.cfg`

결과 파일:

```text
results/rans_200_summary.csv
```

대표 3개 케이스를 200 iteration까지 실행했다.

| Case | Iter | rms[Rho] | CD | CL | C_DF = -CL | 판단 |
|---|---:|---:|---:|---:|---:|---|
| `inv6412_wing_only_U30` | 199 | -3.26853 | 0.12105 | -27.73438 | 27.73438 | 미수렴 |
| `inv6412_wing_cylinder_static_U30` | 199 | -3.21426 | 0.60627 | -21.51169 | 21.51169 | 미수렴 |
| `inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0` | 199 | -3.22265 | 0.12747 | -21.82789 | 21.82789 | 미수렴 |

200 iteration까지 실행은 성공했지만 `rms[Rho]`가 약 `-3.2` 수준에 머물고, force coefficient가 큰 폭으로 drift한다. 마지막 50 iteration 기준 `C_DF` drift는 wing-only `+10.98`, static cylinder `+5.88`, 일차 후보 rotating `+5.60` 수준이다. 따라서 위 계수는 최종 성능 비교에 사용하지 않는다. 이 결과는 현재 격자와 RANS 설정에서 긴 iteration만 늘리는 방식으로는 신뢰 가능한 결론에 도달하기 어렵다는 신호다.

현재 고정된 일차 후보는 다음과 같다.

```text
airfoil = inverted NACA6412
cylinder_x_over_c = 0.02
cylinder_z_over_c = 0.10
lambda = +1.0
U_inf = 30 m/s
```

이 후보는 50 iteration smoke-test 기준으로 motor power 보정 후 효율이 가장 좋아 보였기 때문에 다음 refined-mesh 연구의 기준점으로만 사용한다. 최종 성능 우열은 boundary-layer/near-wall mesh 보강 후 재계산해야 한다.

## refined mesh 준비 상태

추가한 mesh 설정:

```text
near_wall_size_m = 0.006
ground_refine_size_m = 0.015
wake_refine_size_m = 0.020
```

Gmsh mesh 생성, SU2 dry-run, RANS/moving-wall 50 iteration smoke-test가 대표 3개 케이스에서 통과했다.

결과 파일:

```text
results/rans_refined_50_summary.csv
```

refined 50 iteration 결과:

| Case | Iter | rms[Rho] | CD | CL | C_DF = -CL | Last-window C_DF drift |
|---|---:|---:|---:|---:|---:|---:|
| `inv6412_wing_only_U30` | 49 | -3.37268 | 1.28532 | -1.95121 | 1.95121 | 1.93446 |
| `inv6412_wing_cylinder_static_U30` | 49 | -3.34473 | 3.92486 | -0.21679 | 0.21679 | 0.19324 |
| `inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0` | 49 | -3.33296 | 3.45991 | -0.05934 | 0.05934 | 0.03843 |

기존 50 iteration smoke-test와 refined 50 iteration 결과가 크게 다르다. 특히 일차 후보 rotating case는 기존 coarse smoke-test에서 `C_DF = 2.33021`였지만 refined 50에서는 `C_DF = 0.05934`로 낮아졌다. 이는 후보가 나쁘다는 결론이 아니라, 현재 50 iteration 결과가 mesh와 초기 transient에 매우 민감하다는 뜻이다. refined mesh에서는 `C_DF` drift 자체는 작아졌지만, residual은 여전히 `-3.3` 수준이고 최종 성능 판단에는 부족하다.

refined 200 iteration 후보 결과:

```text
results/rans_refined_200_summary.csv
```

| Case | Iter | rms[Rho] | CD | CL | C_DF = -CL | Last-window C_DF drift |
|---|---:|---:|---:|---:|---:|---:|
| `inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0` | 199 | -3.32974 | -0.74677 | -24.64227 | 24.64227 | 12.03285 |

refined 200에서도 마지막 50 iteration 동안 `C_DF`가 `+12.03` 변했다. 50 iteration 시점의 `C_DF = 0.05934`에서 200 iteration 시점의 `C_DF = 24.64227`까지 크게 이동했으므로, 현재 계산은 긴 transient 또는 수치 불안정을 포함한다. Mesh를 단순히 촘촘하게 하는 것만으로는 수렴성이 해결되지 않았고, 다음 우선순위는 solver 안정화 설정과 벽면/난류 모델 설정 재검토다.

## stable 300 수렴성 점검

템플릿:

```text
config/su2_template_rans_moving_wall_stable_300.cfg
```

결과 파일:

```text
results/rans_stable_300_summary.csv
```

안정화 설정:

```text
CFL_NUMBER = 0.2
JST_SENSOR_COEFF = (0.8, 0.05)
LINEAR_SOLVER_ERROR = 1E-7
LINEAR_SOLVER_ITER = 30
ITER = 300
```

stable 300 결과:

| Case | Iter | rms[Rho] | CD | CL | C_DF = -CL | Last-window C_DF drift |
|---|---:|---:|---:|---:|---:|---:|
| `inv6412_wing_only_U30` | 299 | -3.56074 | 1.06856 | -0.06092 | 0.06092 | 0.46172 |
| `inv6412_wing_cylinder_static_U30` | 299 | -3.48698 | 3.35635 | 1.51304 | -1.51304 | 0.70286 |
| `inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0` | 299 | -3.46105 | 2.83840 | 1.23837 | -1.23837 | 1.17541 |

보수적인 solver 설정은 force drift를 줄였지만 수렴해를 만들지는 못했다. 특히 stable 300 최종 시점에서 static cylinder와 rotating candidate는 `C_DF < 0`, 즉 다운포스가 아니라 양력 방향이다. 따라서 현재 후보가 다운포스를 개선한다고 결론 내릴 수 없다.

현재 연구 결론은 `긍정`이 아니라 `부정/보류`다. 파이프라인 구축과 후보 탐색은 완료했지만, steady RANS에서 회전 실린더 효과를 신뢰성 있게 입증하지 못했다.

## 10000 iteration long-run 준비

RANS 수렴 판단에는 200~300 iteration이 부족하므로 10000 iteration용 설정을 추가했다.

템플릿:

```text
config/su2_template_rans_moving_wall_long_10000.cfg
```

케이스 디렉터리:

```text
cases_rans_long_10000/
```

후보 케이스 dry-run:

```text
cases_rans_long_10000/inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0/su2_dryrun.log
```

long-run 설정:

```text
ITER = 10000
CFL_NUMBER = 0.2
JST_SENSOR_COEFF = (0.8, 0.05)
LINEAR_SOLVER_ERROR = 1E-7
LINEAR_SOLVER_ITER = 30
OUTPUT_FILES = ( RESTART )
OUTPUT_WRT_FREQ = 500
```

실행 명령:

```text
wsl bash -lc "cd /mnt/d/RAGNAROK/3_ing/MARS_project && python3 scripts/run_case.py inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0 --case-dir cases_rans_long_10000 --threads 4"
```

현재 환경 기준으로 10000 iteration은 장시간 실행 작업이다. 따라서 이 문서 업데이트 시점에는 dry-run까지만 완료했고, 실제 10000 iteration solver는 overnight/batch 계산으로 수행해야 한다.

10000 iteration 결과 판단 기준:

- residual이 최소한 `rms[Rho] < -5` 이하로 계속 감소하는지 확인
- 마지막 500~1000 iteration에서 `CL`, `CD`, `C_DF` drift가 충분히 작은지 확인
- rotating candidate만 보지 말고, 같은 long-run 설정으로 wing-only/static도 비교
- long-run에서도 force가 주기적으로 흔들리면 steady RANS가 아니라 URANS 검토로 전환

## 아직 하지 않은 일

- RANS/moving-wall 장시간 계산이 안정적으로 수렴하도록 solver/mesh 개선
- solver 안정화 설정 추가 검토: limiter, initialization, restart strategy
- 10000 iteration long-run 실제 실행 및 후처리
- RANS wall treatment 및 난류 모델 설정 재검토
- prism boundary-layer mesh 또는 추가 near-wall refinement 설계
- 필요 시 2D 또는 quasi-2D 검증 문제로 단순화
- y+ 또는 wall treatment 기준 확인
- cylinder torque 또는 moment 기반 motor power 계산 방식 검증
- `P_motor`, `D_eq`, `eta_net` 후처리 추가
- lambda, U_inf sweep 자동 확장
- 격자 독립성 확인
- 그래프 자동 생성

## 다음 작업 지시용 문장

새 대화에서 바로 이어가려면 다음처럼 요청하면 된다.

```text
docs/current_status.md와 docs/next_steps.md 읽고, RANS smoke-test가 끝난 상태에서 boundary-layer mesh 설계와 RANS 수렴 계산 준비를 진행해줘.
```

## 보고서 표현 주의점

이 프로젝트는 자동차 전체를 직접 모델링하지 않는다. 따라서 보고서와 결론에서 “자동차 전체 다운포스가 증가했다”고 쓰면 안 된다. 정확한 표현은 “자동차용 리어윙 단품 모델에서 회전 실린더 적용 가능성을 평가했다”이다.

현재 Euler 결과로 성능 결론을 내리면 안 된다. 회전 실린더 성능 평가는 RANS/moving-wall 실제 계산과 후처리 검증 이후에만 가능하다.
