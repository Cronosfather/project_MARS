# 연구 마무리 요약

## 결론

현재 모델과 계산 설정으로는 `inverted NACA6412` finite wing에 회전 실린더를 적용했을 때 다운포스 증가를 신뢰성 있게 입증하지 못했다.

초기 50 iteration smoke-test에서는 `x/c = 0.02`, `z/c = 0.10`, `lambda = +1.0` 후보가 좋아 보였지만, refined mesh와 안정화된 solver 설정에서 결과가 크게 바뀌었다. 따라서 초기 smoke-test 결과는 후보 탐색용 힌트일 뿐 성능 결론으로 사용할 수 없다.

## 고정 후보

```text
airfoil = inverted NACA6412
U_inf = 30 m/s
cylinder_x_over_c = 0.02
cylinder_z_over_c = 0.10
lambda = +1.0
```

이 후보는 초기 탐색에서 motor-power 보정 효율이 가장 좋아 보여서 선정했다. 그러나 이후 refined/stable 계산에서 성능 우위가 유지되지 않았다.

## 수행한 계산

1. NACA0012 baseline geometry/mesh/SU2 pipeline 검증
2. NACA6412 cambered airfoil 생성 및 inverted rear-wing 모델 적용
3. moving ground, moving cylinder wall 조건 dry-run 검증
4. 회전 방향 sweep: `lambda > 0` 방향이 의도한 다운포스 증가 방향에 더 가까움
5. 실린더 위치 sweep: 초기 smoke-test 기준 `x/c = 0.02`, `z/c = 0.10` 후보 선정
6. refined mesh 생성: wing/cylinder/ground/wake 주변 box-based near-wall refinement
7. refined 50 iteration 및 refined 200 iteration 수렴성 점검
8. 안정화 설정 300 iteration 비교: wing-only, static cylinder, rotating candidate

## 주요 결과

### 초기 50 iteration smoke-test

| Case | Iter | rms[Rho] | CD | C_DF = -CL | 판단 |
|---|---:|---:|---:|---:|---|
| wing-only | 49 | -3.19961 | 0.64826 | 3.80122 | 미수렴 |
| static cylinder | 49 | -3.18224 | 2.66733 | 1.18207 | 미수렴 |
| rotating candidate | 49 | -3.17859 | 2.11996 | 2.33021 | 미수렴 |

초기 smoke-test만 보면 rotating candidate가 static cylinder보다 좋아 보인다. 그러나 50 iteration 결과는 force drift가 크고 mesh 의존성이 강해서 최종 결론으로 사용할 수 없다.

### refined 200 후보 결과

| Case | Iter | rms[Rho] | CD | C_DF = -CL | Last 50 iter C_DF drift |
|---|---:|---:|---:|---:|---:|
| rotating candidate | 199 | -3.32974 | -0.74677 | 24.64227 | 12.03285 |

refined mesh에서 200 iteration까지 돌렸지만 마지막 50 iteration에도 `C_DF`가 `+12.03` 변했다. 수렴 계산이 아니다.

### stable 300 비교

안정화 설정:

```text
CFL_NUMBER = 0.2
JST_SENSOR_COEFF = (0.8, 0.05)
LINEAR_SOLVER_ERROR = 1E-7
LINEAR_SOLVER_ITER = 30
ITER = 300
```

| Case | Iter | rms[Rho] | CD | CL | C_DF = -CL | Last 50 iter C_DF drift |
|---|---:|---:|---:|---:|---:|---:|
| wing-only | 299 | -3.56074 | 1.06856 | -0.06092 | 0.06092 | 0.46172 |
| static cylinder | 299 | -3.48698 | 3.35635 | 1.51304 | -1.51304 | 0.70286 |
| rotating candidate | 299 | -3.46105 | 2.83840 | 1.23837 | -1.23837 | 1.17541 |

stable 300에서도 residual은 `-3.46` to `-3.56` 수준으로 목표 `-8`에 도달하지 못했다. force drift는 이전보다 줄었지만 여전히 남아 있고, rotating candidate와 static cylinder는 최종 시점에서 다운포스가 아니라 양력 방향이다.

## 연구적 판단

현재까지의 증거로는 회전 실린더가 리어윙 단품 모델의 다운포스를 신뢰성 있게 증가시킨다고 말할 수 없다.

더 정확한 표현은 다음과 같다.

```text
본 연구에서는 inverted NACA6412 finite wing과 회전 실린더 조합의 CFD 파이프라인을 구축하고 후보 위치를 탐색했다. 그러나 refined mesh 및 보수적 solver 설정에서도 steady RANS 계산의 force coefficient가 충분히 안정되지 않았고, rotating candidate의 다운포스 개선은 재현되지 않았다. 따라서 현재 모델과 계산 조건에서는 회전 실린더 적용 효과를 긍정적으로 결론 내릴 수 없다.
```

## 보고서에 쓰면 안 되는 표현

- 자동차 전체 다운포스가 증가했다.
- 회전 실린더가 다운포스를 증가시킨다.
- `x/c = 0.02`, `z/c = 0.10`이 최적 위치다.
- refined 200 또는 stable 300의 최종 force 값을 수렴해로 간주한다.

## 보고서에 쓸 수 있는 표현

- 자동화된 geometry/mesh/SU2 pipeline을 구축했다.
- moving ground와 rotating cylinder moving-wall 조건을 SU2에서 구현하고 dry-run으로 확인했다.
- 초기 smoke-test에서는 특정 후보가 유망해 보였지만, refined/stable 계산에서 결과가 재현되지 않았다.
- 현재 steady RANS 설정으로는 성능 우위를 입증하지 못했다.
- 후속 연구에서는 wall-resolved 또는 wall-function에 맞춘 boundary-layer mesh, unsteady 계산, 더 보수적인 검증 절차가 필요하다.

## 후속 연구 판단

연구를 여기서 마무리한다면 결론은 `부정/보류`가 맞다. 계속 이어간다면 다음 중 하나를 먼저 선택해야 한다.

1. `steady RANS 유지`: prism boundary-layer mesh와 y+ 기준을 명확히 맞춘 뒤 solver 안정화 재시도
2. `URANS 전환`: 회전 실린더와 ground effect가 본질적으로 unsteady일 가능성을 인정하고 time-accurate 계산으로 전환
3. `모델 단순화`: 2D 단면 또는 무한 span 모델로 먼저 회전 실린더 효과를 검증한 뒤 3D finite wing으로 복귀

현재 상태에서 가장 방어 가능한 선택은 3번이다. 2D 또는 준-2D 검증 없이 3D finite wing + rotating cylinder + moving ground를 바로 최적화하면, 수치 불안정과 물리 효과를 분리하기 어렵다.
