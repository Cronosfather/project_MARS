# 다음 작업 목록

## 최우선 목표

RANS/moving-wall dry-run, 50 iteration smoke-test, 대표 3개 케이스의 200 iteration 수렴성 점검, refined mesh 계산, stable 300 비교까지 완료했다. 200~300 iteration은 RANS 수렴 판단에 부족하므로, 10000 iteration long-run 템플릿과 케이스를 준비했고 후보 케이스 dry-run까지 통과했다.

## 바로 할 일

1. 일차 후보를 `x/c = 0.02`, `z/c = 0.10`, `lambda = 1.0`으로 고정한다.
2. `results/rans_200_summary.csv`는 수렴성 점검 결과로만 보관하고, 성능 결론에는 사용하지 않는다.
3. `cases_rans_long_10000`에서 후보 케이스 10000 iteration을 overnight/batch로 실행한다.
4. 후보 long-run이 안정되면 같은 설정으로 wing-only와 static cylinder를 실행한다.
5. long-run에서도 force가 계속 drift하거나 주기적으로 흔들리면 steady RANS 결론을 중단하고 URANS 또는 2D/quasi-2D 검증으로 전환한다.
6. stable 300까지는 rotating candidate의 다운포스 개선이 재현되지 않았으므로 긍정 결론을 내리지 않는다.
7. 보고서에는 “파이프라인 구축 및 후보 탐색 완료, 장시간 RANS 수렴 검증 필요”로 쓴다.
8. `CMy(cylinder)` 기반 torque 계산식은 후속 연구 전에 convention 검증을 마친다.

## 현재 고정 후보

```text
airfoil = inverted NACA6412
U_inf = 30 m/s
cylinder_x_over_c = 0.02
cylinder_z_over_c = 0.10
lambda = +1.0
```

고정 이유:

1. 회전 방향 반전 smoke-test에서 `lambda > 0` 방향이 `lambda < 0`보다 다운포스 증가 방향에 가깝다.
2. 위치 sweep에서 `x/c = 0.02`, `z/c = 0.10`이 기존 위치 `x/c = 0.08`보다 크게 나았다.
3. 순수 다운포스는 `x/c = 0.00`이 약간 높았지만, motor power 보정 후 효율은 `x/c = 0.02`가 더 좋았다.
4. 아직 미수렴 smoke-test 기반이므로, 이 후보는 최종 설계가 아니라 refined-mesh 검증용 기준점이다.

## mesh 보강

1. 현재 refined mesh는 prism boundary-layer mesh가 아니라 box-based near-wall refinement다.
2. 대표 3개 케이스의 refined mesh 생성, SU2 dry-run, 50 iteration smoke-test는 완료됐다.
3. stable 300에서도 residual은 약 `-3.46~-3.56` 수준이고 force drift가 남아 있다.
4. stable 300 최종 시점에서 static cylinder와 rotating candidate는 `C_DF < 0`이다.
5. 10000 iteration long-run으로 steady RANS가 실제로 정착하는지 먼저 확인한다.
6. long-run이 정착하지 않으면 단순 검증 문제에서 물리 효과를 먼저 확인한다.
7. 이후 prism layer, y+, wall treatment, coarse/medium/fine mesh 비교를 준비한다.

## 후처리 작업

1. `scripts/postprocess_cases.py`는 RANS 결과와 per-surface 계수를 이미 읽는다.
2. cylinder moment 또는 torque 계산 기준을 검증한다.
3. `P_motor = M * omega / eta_m` 계산의 부호와 절댓값 처리 기준을 확정한다.
4. `D_eq = D_aero + P_motor / U_inf` 기준을 확정한다.
5. `eta_net = F_down / D_eq` 기준을 확정한다.
6. 200 iteration force history에서 coefficient drift를 자동으로 확인하는 진단 지표는 추가됐다.
7. lambda별 `C_DF`, `CD`, `C_DF/abs(CD)`, `eta_net` 그래프를 생성한다.

## 확장 작업

1. 후보 10000 iteration long-run 실행
2. wing-only/static 10000 iteration 비교 실행
3. 2D 또는 quasi-2D rotating-cylinder/airfoil 검증 문제 구성
4. URANS 전환 여부 결정
5. prism boundary-layer mesh와 y+ 기준 설정
6. 안정화된 검증 문제에서 lambda sweep 재개
7. 후속 연구 항목으로 endplate, 차체 포함 모델, 풍동 실험 정리

## 완료 판단 기준

- RANS/moving-wall 실제 계산이 wing-only, static cylinder, rotating cylinder에서 모두 실행된다.
- ground와 cylinder moving wall이 solver log에서 확인된다.
- wing, cylinder, ground marker별 force/moment를 분리할 수 있다.
- cylinder torque 또는 등가 moment로 motor power를 계산할 수 있다.
- 결과를 `results/summary.csv`로 재현 가능하게 정리할 수 있다.
- residual과 force coefficient가 둘 다 안정된 대표 계산을 확보한다.
- refined mesh 기반 dry-run이 대표 3개 케이스에서 통과한다.
- refined mesh 기반 50 iteration smoke-test가 대표 3개 케이스에서 통과한다.
- refined 200 후보 계산에서 force drift가 크다는 사실을 문서화한다.
- stable 300 비교에서 회전 실린더 다운포스 개선을 입증하지 못했다는 사실을 문서화한다.
- 10000 iteration long-run 케이스가 dry-run을 통과한다.

## 하지 말아야 할 것

- Euler 검증 결과로 물리 결론을 내리지 않는다.
- RANS 실제 계산 전에는 rotating case를 성능 비교에 사용하지 않는다.
- boundary-layer mesh 없이 RANS 결과를 최종 결과처럼 쓰지 않는다.
- 200 iteration 미수렴 결과를 최종 성능 수치처럼 쓰지 않는다.
- refined mesh를 최종 boundary-layer mesh라고 표현하지 않는다.
- stable 300 결과를 긍정 성능 결론으로 해석하지 않는다.
- 자동차 전체 공력 성능으로 과장해서 표현하지 않는다.
## 2026-07-06 update: 500-iteration long-run checkpoint

The first 10000-iteration steady RANS candidate run was started for
`inv6412_wing_cylinder_rotating_x0p020_z0p100_U30_lam1p0` and stopped after the
500-iteration restart checkpoint was written.

Checkpoint summary:

```text
last recorded iteration = 525
rms[Rho]                = -3.327018
CL                      = -6.653672
CD                      = -0.539330
C_DF                    =  6.653672
last-50-row Delta CL    =  1.810160
last-50-row Delta C_DF  = -1.810160
```

Decision:

1. Do not treat this as a converged performance result.
2. Do not launch broad 3D steady-RANS sweeps yet.
3. Keep the `restart.dat` checkpoint, but pause blind continuation to 10000 iterations.
4. Move the next research step to URANS setup or a simpler 2D/quasi-2D rotating-cylinder validation case.
5. Use the simplified case to verify rotation convention, torque sign, force averaging, and expected Magnus behavior before returning to expensive 3D runs.
