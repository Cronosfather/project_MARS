# 3D 회전 실린더 리어윙 CFD 프로젝트 진행 계획

## 1. 연구 방향

본 프로젝트는 기존 2차원 자동차 단면 기반 아이디어를 수정하여, 자동차 전체 형상을 직접 모델링하지 않고 자동차용 리어윙을 단순화한 3차원 유한 날개 모델을 해석 대상으로 삼는다.

기본 형상은 2D inverted airfoil 단면을 span 방향으로 extrusion한 finite wing이며, 리어윙 앞전 근처에 회전 실린더를 배치한다. 이를 통해 마그누스 효과 기반 회전 실린더가 리어윙의 다운포스를 증가시키는지, 그리고 모터 구동 전력까지 고려했을 때 실효성이 있는지를 평가한다.

이 접근은 2D 해석보다 실제 리어윙과 가까운 3D 효과를 포함할 수 있지만, 자동차 차체 전체의 후류와 간섭은 포함하지 않는다. 따라서 최종 결론은 "자동차 전체 공력 성능"이 아니라 "자동차용 리어윙 단품 수준의 가능성 평가"로 제한한다.

## 2. 연구 제목 후보

### 주 제목

3차원 CFD를 이용한 마그누스 효과 기반 회전 실린더 리어윙의 다운포스 향상 및 전력 보정 효율 평가

### 보조 설명

자동차용 리어윙을 단순화한 3차원 유한 날개 모델을 대상으로, 회전 실린더 적용에 따른 다운포스, 항력, 모터 전력 보정 순효율을 비교한다.

## 3. 해석 대상 형상

### 기본 리어윙

- 검증용 Airfoil: inverted NACA 0012
- 성능 평가용 Airfoil: inverted NACA 6412
- Chord length: 0.30 m
- Span: 1.20 m를 우선 사용
- Aspect ratio: 4.0
- Angle of attack: 고정값 1개로 시작하며, 초기값은 별도 검토 후 확정
- Endplate: 초기 해석에서는 제외, 후속 확장 항목으로 둠

NACA0012는 대칭 익형이므로 회전 실린더 효과와 계산 파이프라인을 검증하기 위한 baseline으로 사용한다. 최종 성능 비교는 다운포스 목적에 더 자연스러운 cambered airfoil인 inverted NACA6412를 기본으로 진행한다.

### 회전 실린더

- Cylinder radius: 0.02 m
- Cylinder span: 리어윙 span과 동일하게 설정
- 위치: 리어윙 leading edge 근처
- 회전 방향: 리어윙 주변 순환을 증가시켜 다운포스를 키우는 방향
- 속도 조건: RPM 직접 지정이 아니라 속도비 lambda 기준으로 정의

### 지면 조건

- 자동차 전체 형상은 제외하되, 자동차용 리어윙이라는 맥락을 반영하기 위해 moving ground 조건을 포함하는 방향을 우선 검토한다.
- Ground clearance는 리어윙 최저점 기준 0.20 m를 초기 기준값으로 둔다.

## 4. 비교군

최소 비교군은 다음 3개로 구성한다.

1. `wing_only`: 3D finite wing only
2. `wing_cylinder_static`: 3D finite wing + non-rotating cylinder
3. `wing_cylinder_rotating`: 3D finite wing + rotating cylinder

비회전 실린더 조건을 별도로 두는 이유는, 실린더를 붙였다는 형상 변화 자체의 영향과 회전에 의한 마그누스 효과를 분리하기 위해서이다.

## 5. 주요 변수

### 유입 속도

- U_inf = 20 m/s
- U_inf = 30 m/s
- U_inf = 40 m/s

### 속도비

속도비는 다음과 같이 정의한다.

```text
lambda = omega * R / U_inf
```

여기서 omega는 실린더 각속도, R은 실린더 반지름, U_inf는 유입 속도이다.

초기 sweep 조건은 다음과 같이 둔다.

- lambda = 0
- lambda = 0.5
- lambda = 1.0
- lambda = 1.5
- lambda = 2.0

lambda = 0은 비회전 실린더 조건이다.

각속도와 RPM은 다음 식으로 계산한다.

```text
omega = lambda * U_inf / R
RPM = omega * 60 / (2 * pi)
```

## 6. 해석 도구

- Geometry and mesh: Gmsh
- CFD solver: SU2
- Automation and post-processing: Python
- Plotting: matplotlib

초기 목표는 모든 과정을 한 번에 완성하는 것이 아니라, 다음 순서로 안정적으로 확장하는 것이다.

1. wing only geometry 생성
2. wing + cylinder geometry 생성
3. Gmsh mesh 생성
4. SU2 config 자동 생성
5. 단일 케이스 계산 실행
6. 여러 U_inf, lambda 조건 자동 sweep
7. 결과 추출 및 summary.csv 작성
8. 그래프 자동 생성

## 6.1. 초기 검증 케이스

처음부터 모든 유속과 속도비 조건을 계산하지 않는다. 다음 4개 케이스를 먼저 만들어 geometry, mesh, boundary marker, SU2 설정이 정상인지 확인한다.

1. `wing_only_U30`
2. `wing_cylinder_static_U30`
3. `wing_cylinder_rotating_U30_lam1p0`
4. `wing_cylinder_rotating_U30_lam2p0`

이 네 케이스에서 force coefficient와 residual 출력이 정상적으로 확인되면 전체 sweep으로 확장한다.

## 7. 권장 프로젝트 구조

```text
MARS_project/
  MARS_project.md
  docs/
    project_plan_3d_finite_wing.md
  research/
    YYYY-MM-DD_research_log.md
  config/
    project_config.yaml
    su2_template.cfg
  geometry/
    airfoils/
    gmsh_templates/
    generated/
  cases/
  scripts/
    generate_geometry.py
    generate_cases.py
    run_cases.py
    postprocess.py
    plot_results.py
  results/
    summary.csv
    figures/
    flowfields/
```

오늘은 `docs`와 `research`만 정리한다. 실제 계산용 폴더와 코드는 다음 단계에서 만든다.

현재 상태를 새 대화에서 이어받기 위한 요약 문서는 `docs/current_status.md`에 둔다.

## 8. 해석 방법

### Solver

저속 외부 유동이므로 SU2의 incompressible RANS 해석을 기본으로 한다.

- Solver: INC_RANS
- Turbulence model: SST 계열 우선 검토
- 초기 단계: steady RANS
- 후속 단계: 대표 조건에 대해 unsteady 또는 시간 평균 해석 검토

### Boundary condition

- Inlet: velocity inlet
- Outlet: pressure outlet
- Farfield 또는 top/side boundary: symmetry/slip/farfield 중 SU2 설정에 맞춰 결정
- Wing surface: no-slip wall
- Cylinder surface: rotating wall 또는 moving wall
- Ground: moving wall 조건 우선 검토

## 9. 결과 지표

리어윙은 다운포스가 관심 대상이므로 lift coefficient를 그대로 쓰지 않고 downforce coefficient를 정의한다.

```text
C_DF = -C_L
```

주요 출력값은 다음과 같다.

- C_L
- C_D
- C_DF
- C_DF / C_D
- Cylinder torque
- P_motor
- Equivalent drag
- eta_net
- convergence status

모터 전력은 다음과 같이 계산한다.

```text
P_motor = M_z * omega / eta_m
```

여기서 eta_m은 모터 및 구동계 효율이며, 실제 측정값이 없으면 0.8로 가정하고 보고서에 명시한다.

모터 전력을 등가 항력으로 환산한다.

```text
D_eq = D_aero + P_motor / U_inf
```

최종 순효율은 다음과 같이 정의한다.

```text
eta_net = F_down / D_eq
```

## 10. 최종 판단 기준

회전 실린더 리어윙이 의미 있다고 판단하려면 다음 조건을 함께 만족해야 한다.

1. 일반 finite wing보다 다운포스가 증가해야 한다.
2. 비회전 실린더 조건보다 회전 실린더 조건의 다운포스가 증가해야 한다.
3. 항력 대비 다운포스 효율이 크게 나빠지지 않아야 한다.
4. 모터 전력 보정 후 eta_net이 일반 wing과 비슷하거나 더 좋아야 한다.
5. 요구 RPM이 현실적인 범위에 있어야 한다.

## 11. 단계별 진행 계획

### 1단계: 문서 정리

- 3D finite wing 연구 방향 확정
- 비교군, 변수, 결과 지표 정리
- 프로젝트 폴더 구조 설계

### 2단계: 형상 생성

- NACA 0012 airfoil 좌표 생성
- inverted airfoil 적용
- span 방향 extrusion
- leading edge 근처 실린더 추가
- Gmsh geometry template 작성

### 3단계: 단일 케이스 검증

- wing only case 생성
- wing + non-rotating cylinder case 생성
- lambda = 1.0 rotating cylinder case 생성
- mesh 품질과 boundary marker 확인

### 4단계: 자동화

- config 파일 기반 case 자동 생성
- Gmsh 실행 자동화
- SU2 config 자동 생성
- SU2 실행 자동화

### 5단계: 결과 분석

- history 파일에서 force coefficient 추출
- torque와 motor power 계산
- summary.csv 생성
- lambda별 C_DF, C_D, C_DF/C_D, eta_net 그래프 작성

### 6단계: 검증 및 한계 정리

- 대표 조건에서 격자 독립성 확인
- 필요 시 unsteady 해석 검토
- 자동차 전체 모델이 아니라는 한계 명시
- 후속 연구로 차체 포함 3D CFD, endplate, 풍동 실험 제안

## 12. 현재 결정 사항

- 자동차 2D 단면 대신 3D finite wing 모델로 연구 방향을 수정한다.
- 자동차 전체 형상은 이번 범위에서 제외한다.
- moving ground는 가능하면 포함한다.
- endplate는 초기 범위에서 제외하고 후속 확장으로 둔다.
- 최종 결론은 자동차 전체 성능이 아니라 자동차용 리어윙 단품 가능성으로 제한한다.
