# edu

프로젝트 사전 강의용 프로젝트입니다.

데이터 분석/머신러닝 입문부터 실전 프로젝트까지 단계적으로 학습하는 커리큘럼입니다.
Python 코딩 기초 → SQL → 데이터 핸들링 → ML 입문 → 첫 캐글 프로젝트 → 도메인 심화 프로젝트 순서로 진행합니다.

## 학습 로드맵

### 1. Python 코딩 기초 (프로그래머스)

코딩테스트 핵심 유형을 **유형 1개당 노트북 1개**로 정리합니다.
자료구조에 들어가기 전에, 문법을 코드로 옮기는 응용력을 다지는 **Lv.0 패턴 단계**부터 시작합니다.
각 유형은 교안([`docs/`](docs/))과 실습 노트북([`notebooks/`](notebooks/))으로 구성되며,
설명 → 완성 예제(assert 검증) → 직접 풀어보기(빈칸 연습) 흐름을 따릅니다. **(00~08 완료 ✅)**

| # | 유형 | 대표 문제 (프로그래머스) | 자료 |
|---|------|------------------------|------|
| 00 | Lv.0 문법 패턴 (반복·조건·리스트·문자열) | 프로그래머스 Lv.0 입문 문제 모음 | [교안](docs/00_basics_patterns.md) · [노트북](notebooks/00_basics_patterns.ipynb) |
| 01 | 자료구조 기초 (스택/큐/해시) | 완주하지 못한 선수 (42576) | [교안](docs/01_data_structures.md) · [노트북](notebooks/01_data_structures.ipynb) |
| 02 | 정렬 (Sorting) | 가장 큰 수 (42746) | [교안](docs/02_sorting.md) · [노트북](notebooks/02_sorting.ipynb) |
| 03 | 완전탐색 (Brute Force) | 모의고사 (42840) | [교안](docs/03_brute_force.md) · [노트북](notebooks/03_brute_force.ipynb) |
| 04 | 그리디 (Greedy) | 체육복 (42862) | [교안](docs/04_greedy.md) · [노트북](notebooks/04_greedy.ipynb) |
| 05 | DFS/BFS | 타겟 넘버 (43165) | [교안](docs/05_dfs_bfs.md) · [노트북](notebooks/05_dfs_bfs.ipynb) |
| 06 | 이분탐색 (Binary Search) | 입국심사 (43238) | [교안](docs/06_binary_search.md) · [노트북](notebooks/06_binary_search.ipynb) |
| 07 | 동적계획법 (DP) | N으로 표현 (42895) | [교안](docs/07_dynamic_programming.md) · [노트북](notebooks/07_dynamic_programming.ipynb) |
| 08 | 그래프 (최단경로) | 가장 먼 노드 (49189) | [교안](docs/08_graph.md) · [노트북](notebooks/08_graph.ipynb) |

### 2. SQL

실습 DB는 **SQLite**를 사용합니다 (설치·자격증명 불필요, 노트북에서 바로 실행, 완전 재현 가능).
실무 RDBMS(Supabase/PostgreSQL) 연결은 5단계 타이타닉 프로젝트에서 짧게 맛봅니다.

- 기초 조회 (`SELECT`, `WHERE`, `ORDER BY`)
- 집계 (`GROUP BY`, `HAVING`, 집계 함수)
- 조인 (`JOIN`)
- 서브쿼리
- 윈도우 함수

### 3. 데이터 핸들링

라이브러리별로 **노트북 1개씩** 진행합니다.

- `numpy` — 배열 연산, 브로드캐스팅
- `pandas` — 데이터프레임, 전처리, `groupby`/`merge` (SQL과 대조)
- `matplotlib` / `seaborn` — 시각화

### 4. ML 입문 (scikit-learn)

- 전처리 파이프라인
- 모델 학습 (분류/회귀)
- 모델 평가 (지표, 교차검증)

### 5. 첫 프로젝트 — Kaggle 타이타닉

- 생존 예측 (이진 분류)
- 전처리 → 모델링 → 평가 전 과정 통합 실습
- 실무 RDBMS(Supabase 등) 연결 맛보기

### 6. 심화 프로젝트 (2팀 분기)

#### 트랙 A — 금융 리스크 / 고객 분석
- 카드 이상거래 탐지 시스템 (불균형 분류, 이상탐지)
- 고객 생애 가치(CLV) 및 이탈 예측

#### 트랙 B — 시계열 / 투자
- 주가 예측 시스템 (시계열 예측)
- 퀀트 투자 (포트폴리오 구성, 리밸런싱, 백테스팅)

## 환경

- Python 3.13+
- 패키지 관리: [uv](https://github.com/astral-sh/uv)
- 주요 라이브러리: numpy, pandas, matplotlib, seaborn, scikit-learn
- 개발 도구: jupyter, ipython