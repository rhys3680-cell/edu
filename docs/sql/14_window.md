# SQL 14 — 윈도우 함수 (Window Functions)

> **대상**: SQL 13 (서브쿼리)을 마친 단계. SQL 문법 정리의 **마지막**.
> **목표**: "행을 합치지 않고, 각 행 옆에 그룹 통계·순위를 붙이는" 윈도우 함수 — `RANK` / `PARTITION BY` / 누적 — 익히기.

`GROUP BY`는 여러 행을 **하나로 합칩니다**(부서별 1줄). 하지만 "부서별 연봉 **순위**"처럼 **개별 행은 그대로 두고 그룹 통계를 옆에 붙이고** 싶을 때가 있습니다. 이게 윈도우 함수입니다 — SQL의 꽃이라 불리는 강력한 도구죠.

> 참고: 윈도우 함수는 SQLite 3.25+ 에서 지원됩니다. (이 프로젝트 환경은 충족)

---

## 0) 샘플 데이터 (10~13과 동일)

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect(":memory:")
def q(sql):
    return pd.read_sql_query(sql, conn)

conn.executescript("""
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;
CREATE TABLE departments (dept_id INTEGER PRIMARY KEY, dept_name TEXT NOT NULL);
CREATE TABLE employees (
    emp_id INTEGER PRIMARY KEY, name TEXT NOT NULL,
    dept_id INTEGER, salary INTEGER, hire_year INTEGER
);
INSERT INTO departments VALUES (1,'개발'),(2,'영업'),(3,'인사'),(4,'마케팅');
INSERT INTO employees VALUES
    (1,'김철수',1,5000,2018),(2,'이영희',1,6000,2017),(3,'박민수',2,4500,2020),
    (4,'최지은',2,5500,2019),(5,'정현우',3,4000,2021),(6,'강서연',1,7000,2015),
    (7,'윤도현',2,4800,2022),(8,'한예슬',NULL,5200,2019);
""")
```

---

## 1) 핵심 문법 — OVER ()

윈도우 함수는 **함수() OVER (창 정의)** 형태입니다. `OVER ()`가 "어떤 행들을 한 묶음(window)으로 볼지" 정합니다.

```sql
-- 연봉 높은 순으로 전체 순위 매기기
SELECT name, salary,
       RANK() OVER (ORDER BY salary DESC) AS 순위
FROM employees;
```

> 결과: 강서연(7000)=1위, 이영희(6000)=2위, ... `GROUP BY`와 달리 **8명이 그대로 다 나오면서** 각자 순위가 옆에 붙습니다. 이게 핵심 차이.

---

## 2) 순위 3형제 — ROW_NUMBER / RANK / DENSE_RANK

동점이 있을 때 셋이 다르게 동작합니다. 차이를 또렷이 보려고 **동점이 있는 작은 표 `t`**를 따로 만듭니다.

```python
# 동점(A·B 둘 다 90)이 있는 점수 표
conn.executescript("""
DROP TABLE IF EXISTS t;
CREATE TABLE t (name TEXT, score INTEGER);
INSERT INTO t VALUES ('A',90),('B',90),('C',80),('D',70);
""")
```

```sql
SELECT name, score,
       ROW_NUMBER() OVER (ORDER BY score DESC) AS rn,
       RANK()       OVER (ORDER BY score DESC) AS rnk,
       DENSE_RANK() OVER (ORDER BY score DESC) AS dense
FROM t;   -- 점수: A=90, B=90, C=80, D=70
```

| name | score | ROW_NUMBER | RANK | DENSE_RANK |
|------|-------|-----------|------|-----------|
| A | 90 | 1 | 1 | 1 |
| B | 90 | **2** | **1** | **1** |
| C | 80 | 3 | **3** | **2** |
| D | 70 | 4 | 4 | 3 |

> 차이 정리:
> - **ROW_NUMBER**: 동점이어도 무조건 1,2,3,4 (유일 번호).
> - **RANK**: 동점은 같은 등수, 다음은 **건너뜀** (1,1,3).
> - **DENSE_RANK**: 동점은 같은 등수, 다음은 **안 건너뜀** (1,1,2).
>
> "공동 2등 다음이 3등이냐(DENSE) 4등이냐(RANK)"가 갈림. 상황에 맞게 고릅니다.

---

## 3) PARTITION BY — 그룹별로 따로 (핵심)

`PARTITION BY`는 "이 열별로 따로 창을 나눠서" 계산합니다. `GROUP BY`의 "~별"을 **합치지 않고** 적용하는 셈.

```sql
-- 부서별로 연봉 순위 (각 부서 안에서 1등부터)
SELECT name, dept_id, salary,
       RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS 부서내순위
FROM employees
ORDER BY dept_id, 부서내순위;
```

> 결과: 개발 안에서 강서연=1·이영희=2·김철수=3, 영업 안에서 최지은=1·윤도현=2·박민수=3... **부서마다 순위가 1로 리셋**됩니다. `PARTITION BY` 없는 1번과 비교해 보세요.

**부서별 1등만 뽑기** (윈도우 함수는 WHERE에 못 써서, 서브쿼리로 감쌉니다):

```sql
SELECT name FROM (
    SELECT name,
           RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS r
    FROM employees
    WHERE dept_id IS NOT NULL
) WHERE r = 1;
-- 강서연(개발), 최지은(영업), 정현우(인사)
```

> ⚠️ 중요: **윈도우 함수는 `WHERE`에서 못 씁니다** (계산 시점이 늦음). "순위 = 1만" 같은 조건은 **서브쿼리로 한 번 감싼 뒤** 바깥에서 거릅니다. 윈도우 함수의 단골 패턴.

---

## 4) 집계 윈도우 — 합치지 않는 집계

`AVG`, `SUM` 같은 집계도 `OVER`로 쓰면 "행을 남긴 채" 그룹 통계를 붙입니다.

```sql
-- 각 직원 옆에 그 부서의 평균 연봉 (13의 FROM 서브쿼리를 한 줄로!)
SELECT name, dept_id, salary,
       AVG(salary) OVER (PARTITION BY dept_id) AS 부서평균
FROM employees;
```

> 개발팀 3명 모두 옆에 `6000.0`이 붙습니다. 13에서 FROM 서브쿼리로 했던 "부서평균 붙이기"가 윈도우 함수로 훨씬 짧아집니다.

```sql
-- 연봉 누적합 (높은 순으로 쌓기) — ORDER BY가 있으면 "현재 행까지" 누적
SELECT name, salary,
       SUM(salary) OVER (ORDER BY salary DESC) AS 누적합
FROM employees;
```

---

## 대표 예제 — 부서별 연봉 순위

> "각 직원의 이름·부서·연봉과, 그 부서 안에서의 연봉 순위를, 부서·순위 순으로."

```python
print(q("""
    SELECT name, dept_id, salary,
           RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS 부서내순위
    FROM employees
    ORDER BY dept_id, 부서내순위
"""))
```

**기대 결과:**

```
  name  dept_id  salary  부서내순위
0  한예슬      NaN    5200       1   -- NULL 그룹(혼자) → 1등
1  강서연      1.0    7000       1
2  이영희      1.0    6000       2
3  김철수      1.0    5000       3
4  최지은      2.0    5500       1
5  윤도현      2.0    4800       2
6  박민수      2.0    4500       3
7  정현우      3.0    4000       1
```

> 가르칠 포인트: `PARTITION BY dept_id`로 **부서마다 순위가 1로 리셋**. 한예슬(NULL)도 "NULL 부서 그룹"으로 묶여 혼자 1등. GROUP BY와 달리 **8명이 모두 보이면서** 순위가 붙습니다.

---

## 검증 (노트북에서 실행)

```python
# 전체 순위
allrank = q("SELECT name, RANK() OVER (ORDER BY salary DESC) r FROM employees ORDER BY r")
assert allrank.iloc[0]["name"] == "강서연"   # 7000 → 1위

# 부서별 1등
top = q("""SELECT name FROM (
    SELECT name, RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) r
    FROM employees WHERE dept_id IS NOT NULL
) WHERE r=1""")
assert set(top["name"]) == {"강서연", "최지은", "정현우"}

# 개발팀 부서평균이 모두 6000
devavg = q("""SELECT DISTINCT AVG(salary) OVER (PARTITION BY dept_id) a
              FROM employees WHERE dept_id=1""")
assert devavg["a"][0] == 6000.0
print("통과 ✅")
```

---

## 직접 풀어보기 (연습)

연습 1~2는 작은 샘플, 연습 3은 **Chinook 실제 DB**로 풉니다.

### 연습 1 — 연봉 상위 3명 (ROW_NUMBER)

> 연봉 높은 순으로 번호를 매겨, 상위 3명의 이름을 조회하라.
> **힌트**: `ROW_NUMBER() OVER (ORDER BY salary DESC)`로 번호를 만들고, 서브쿼리로 감싸 `WHERE rn <= 3`.

```python
df = q("""
    -- TODO: ROW_NUMBER 후 서브쿼리로 rn<=3
""")
assert list(df["name"]) == ["강서연", "이영희", "최지은"]
print("통과 ✅")
```

### 연습 2 — 부서별 연봉 2등

> 각 부서에서 연봉이 두 번째로 높은 직원의 이름을 조회하라. (직원 2명 이상인 부서만 자연히 해당)
> **힌트**: `PARTITION BY dept_id ORDER BY salary DESC`로 순위를 매기고, 서브쿼리로 감싸 `WHERE r = 2`.

```python
df = q("""
    -- TODO
""")
# 개발 2등=이영희, 영업 2등=윤도현 (인사는 1명뿐이라 2등 없음)
assert set(df["name"]) == {"이영희", "윤도현"}
print("통과 ✅")
```

### 연습 3 — Chinook: 장르별 트랙 수 순위 (실제 DB)

> Chinook에서 장르별 트랙 수를 세고, 많은 순으로 순위를 매겨 상위 3개를 조회하라.

```python
import sqlite3, pandas as pd
cconn = sqlite3.connect("../../data/chinook.db")
def cq(sql):
    return pd.read_sql_query(sql, cconn)

df = cq("""
    -- TODO: Genre JOIN Track, GROUP BY 장르, COUNT + RANK OVER, 상위 3
""")
assert list(df["Name"]) == ["Rock", "Latin", "Metal"]
print("통과 ✅")
```

---

## 치트시트

| 하고 싶은 것 | 형태 |
|-------------|------|
| 전체 순위 | `RANK() OVER (ORDER BY x DESC)` |
| 그룹별 순위 | `RANK() OVER (PARTITION BY g ORDER BY x)` |
| 유일 번호 (동점도 구분) | `ROW_NUMBER() OVER (...)` |
| 동점 후 안 건너뛰기 | `DENSE_RANK() OVER (...)` |
| 그룹 통계를 행에 붙이기 | `AVG(x) OVER (PARTITION BY g)` |
| 누적합 | `SUM(x) OVER (ORDER BY ...)` |
| "순위=N만" 거르기 | 서브쿼리로 감싸 바깥 `WHERE` |

> 윈도우 함수 vs GROUP BY: **GROUP BY는 행을 합치고, 윈도우 함수는 행을 남긴다.** "개별 행 + 그룹 통계/순위를 같이 보고 싶다" → 윈도우 함수. 그리고 **윈도우 함수는 WHERE에 못 쓰니 서브쿼리로 감싸기.**

---

## 정리

| 예제/연습 | 핵심 |
|-----------|------|
| 부서별 연봉 순위 | `RANK() OVER (PARTITION BY dept ORDER BY salary)` |
| 상위 3명 | `ROW_NUMBER` + 서브쿼리 `rn<=3` |
| 부서별 2등 | `PARTITION BY` + `r=2` |
| Chinook 장르 순위 | `COUNT + RANK OVER` |

> 핵심 한 줄: **윈도우 함수 = 함수() OVER (PARTITION BY 그룹 ORDER BY 정렬). 행을 안 합치고 순위·통계를 옆에 붙임. 순위로 거르려면 서브쿼리로 감싸기.**

---

## 🎉 SQL 문법 정리 완료 (09~14)

| # | 주제 | 핵심 |
|---|------|------|
| 09 | Chinook 둘러보기 | 파일 DB, 테이블 관계 |
| 10 | 기초 조회 | SELECT/WHERE/ORDER BY |
| 11 | 집계 | GROUP BY/HAVING |
| 12 | 조인 | INNER/LEFT JOIN |
| 13 | 서브쿼리 | 스칼라/IN/상관/FROM |
| 14 | 윈도우 함수 | RANK/PARTITION BY |

> 다음(15)은 **파일 DB 다루기 + 실무 RDBMS 맛보기**로, "실무에선 DB를 이렇게 쓴다"를 체험합니다. 이후 로드맵은 데이터 핸들링(pandas) → ML로 이어집니다.