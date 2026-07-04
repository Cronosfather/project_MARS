# 현재 프로젝트 상태

## 한 줄 요약

이 프로젝트는 자동차 전체 형상을 해석하지 않고, 자동차용 리어윙을 단순화한 3D finite wing 모델에 회전 실린더를 적용하여 다운포스 증가와 모터 전력 보정 후 순효율을 평가하는 CFD 연구이다.

## 현재 기준일

- 정리일: 2026-07-04
- 현재 단계: 문서 정리 완료, 계산용 코드와 격자는 아직 생성하지 않음

## 현재 연구 방향

기존 아이디어는 2D 자동차 단면 뒤쪽에 리어윙과 회전 실린더를 배치하는 것이었다. 그러나 최종 방향은 다음과 같이 수정되었다.

- 자동차 전체 형상은 제외한다.
- 2D airfoil 단면을 span 방향으로 extrusion한 3D finite wing을 사용한다.
- 리어윙 앞전 근처에 회전 실린더를 배치한다.
- 회전 실린더의 마그누스 효과가 다운포스와 효율에 미치는 영향을 평가한다.
- moving ground 조건은 가능하면 포함한다.
- 최종 결론은 자동차 전체 공력 성능이 아니라 자동차용 리어윙 단품 수준의 가능성 평가로 제한한다.

## 연구 제목

권장 제목은 다음과 같다.

```text
3차원 CFD를 이용한 마그누스 효과 기반 회전 실린더 리어윙의 다운포스 향상 및 전력 보정 효율 평가
```

## 확정한 해석 대상

### 기본 리어윙

- 형상: inverted NACA 0012
- Chord length: 0.30 m
- Span: 1.20 m를 우선 사용
- Aspect ratio: 4.0
- Angle of attack: 단일 고정값으로 시작
- Endplate: 초기에는 제외

### 회전 실린더

- 반지름 R: 0.02 m
- 길이: 리어윙 span과 동일
- 위치: 리어윙 leading edge 근처
- 회전 방향: 리어윙 주변 순환을 강화하여 다운포스를 증가시키는 방향

### 지면 조건

- moving ground 조건을 우선 검토한다.
- 초기 ground clearance는 리어윙 최저점 기준 0.20 m를 권장한다.

## 비교군

최소 비교군은 다음 3개이다.

1. `wing_only`
2. `wing_cylinder_static`
3. `wing_cylinder_rotating`

비회전 실린더 조건은 반드시 포함한다. 이유는 실린더 장착으로 인한 단순 형상 변화 효과와 실린더 회전으로 인한 마그누스 효과를 분리하기 위해서이다.

## 유동 조건

초기 유입 속도는 다음 3개를 사용한다.

- U_inf = 20 m/s
- U_inf = 30 m/s
- U_inf = 40 m/s

회전 조건은 RPM이 아니라 속도비 lambda로 정의한다.

```text
lambda = omega * R / U_inf
omega = lambda * U_inf / R
RPM = omega * 60 / (2 * pi)
```

초기 lambda 조건은 다음과 같다.

- lambda = 0
- lambda = 0.5
- lambda = 1.0
- lambda = 1.5
- lambda = 2.0

lambda = 0은 비회전 실린더 조건이다.

## 권장 초기 케이스 순서

모든 sweep을 바로 만들지 말고 다음 순서로 진행한다.

1. `wing_only_U30`
2. `wing_cylinder_static_U30`
3. `wing_cylinder_rotating_U30_lam1p0`
4. `wing_cylinder_rotating_U30_lam2p0`
5. 위 4개 케이스가 정상 작동하면 U_inf와 lambda sweep 확장

## 사용할 도구

- Geometry and mesh: Gmsh
- CFD solver: SU2
- Automation: Python
- Post-processing: Python, matplotlib

## 권장 폴더 구조

아직 계산용 폴더와 코드는 생성하지 않았다. 다음 단계에서 아래 구조를 만들면 된다.

```text
MARS_project/
  docs/
    current_status.md
    project_plan_3d_finite_wing.md
  research/
    2026-07-04_research_log.md
  config/
    project_config.yaml
    su2_template.cfg
  geometry/
    airfoils/
    gmsh_templates/
    generated/
  cases/
  scripts/
    generate_airfoil.py
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

## 아직 하지 않은 일

- NACA 0012 좌표 생성 코드 작성
- Gmsh 3D geometry template 작성
- wing only mesh 생성
- cylinder 포함 geometry 생성
- SU2 config template 작성
- rotating wall 또는 moving wall 조건 검증
- 단일 케이스 계산 실행
- 결과 후처리 코드 작성

## 다음 작업 지시용 문장

새 대화에서 바로 이어가려면 다음처럼 요청하면 된다.

```text
docs/current_status.md 읽고, 다음 단계인 프로젝트 기본 폴더 구조와 NACA 0012 기반 3D finite wing geometry 생성 코드부터 만들어줘.
```

## 주의할 점

이 프로젝트는 자동차 전체를 직접 모델링하지 않는다. 따라서 보고서와 결론에서 "자동차 전체 다운포스가 증가했다"고 쓰면 안 된다. 정확한 표현은 "자동차용 리어윙 단품 모델에서 회전 실린더 적용 가능성을 평가했다"이다.

3D 해석은 2D보다 계산 비용이 크므로 처음부터 전체 sweep을 돌리면 안 된다. 반드시 단일 U_inf = 30 m/s 조건에서 wing only, static cylinder, rotating cylinder 순서로 검증한 뒤 sweep으로 확장한다.
