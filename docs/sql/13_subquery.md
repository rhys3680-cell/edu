# SQL 13 — 서브쿼리 (Subquery)

> **대상**: SQL 12 (JOIN)을 마친 단계.
> **목표**: "쿼리 안에 또 쿼리"를 넣어, **다른 쿼리 결과를 기준으로** 조회하는 서브쿼리 익히기.

"평균보다 연봉이 높은 사람"을 구하려면, 먼저 **평균을 구하고** 그 값으로 다시 거릅니다. 이렇게 **한 쿼리의 결과를 다른 쿼리가 사용**하는 게 서브쿼리입니다. 들여다보면 "단계를 한 문장에 합친 것"일 뿐입니다.

---

## 0) 샘플 데이터 (10~12와 동일)

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

## 1) WHERE 안의 서브쿼리 — 단일 값 기준

서브쿼리가 **값 하나**를 돌려주면, 그 값을 조건에 바로 씁니다.

```sql
-- 전체 평균 연봉보다 높은 직원
SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);   -- 괄호 안이 먼저 실행됨
```

> 흐름: 안쪽 `(SELECT AVG(salary) ...)`가 먼저 `5250`을 구하고 → 바깥쪽이 `salary > 5250`으로 거름. 결과: 이영희(6000)·최지은(5500)·강서연(7000).

> 핵심: 단일 값 비교(`=`, `>`, `<`)엔 서브쿼리가 **딱 한 값**을 돌려줘야 합니다. 여러 행이 나오면 에러.

---

## 2) IN 서브쿼리 — 여러 값 목록 기준

서브쿼리가 **여러 값**을 돌려주면 `IN`으로 받습니다.

```sql
-- '개발' 부서에 속한 직원 (부서 이름 → dept_id 목록 → 직원)
SELECT name
FROM employees
WHERE dept_id IN (SELECT dept_id FROM departments WHERE dept_name = '개발');
```

> 이건 JOIN으로도 풀 수 있습니다. "부서 이름으로 직원 찾기"를 **JOIN 대신 서브쿼리로** 표현한 것 — 같은 문제, 다른 도구. 가독성에 따라 고릅니다.

---

## 3) 상관 서브쿼리 — 바깥 행마다 다시 계산 (핵심)

서브쿼리가 **바깥 쿼리의 각 행을 참조**하면 "상관(correlated) 서브쿼리"입니다. 행마다 서브쿼리가 다시 돕니다.

```sql
-- 자기 부서의 평균 연봉보다 높은 직원
SELECT name, salary, dept_id
FROM employees e
WHERE salary > (
    SELECT AVG(salary) FROM employees
    WHERE dept_id = e.dept_id      -- 바깥의 e.dept_id를 참조 → 부서마다 다른 평균
);
```

> 결과: 최지은(영업 평균 4933 < 5500), 강서연(개발 평균 6000 < 7000). "**같은 부서 안에서** 평균보다 높은 사람"이라, 전체 평균 기준과 결과가 다릅니다.

> 한예슬(부서 NULL)은? `dept_id = e.dept_id`에서 NULL 비교가 되어 짝이 안 맞아 **빠집니다**. (NULL 함정 또 등장 — 11·12와 연결)

---

## 4) FROM 안의 서브쿼리 — "임시 테이블"처럼

서브쿼리 결과를 **하나의 테이블처럼** FROM에 놓고 JOIN할 수 있습니다.

```sql
-- 각 직원 옆에 그 부서의 평균 연봉을 붙이기
SELECT e.name, e.salary, da.avg_sal
FROM employees e
JOIN (
    SELECT dept_id, AVG(salary) AS avg_sal
    FROM employees
    GROUP BY dept_id
) da ON e.dept_id = da.dept_id;
```

> 안쪽 서브쿼리가 "부서별 평균" 테이블(`da`)을 만들고, 바깥에서 직원과 JOIN. 김철수(5000)는 개발 평균 6000과 나란히 보입니다. "집계 결과를 원본에 다시 붙이기" 패턴.

---

## 대표 예제 — 전체 평균 이상 받는 직원

> "회사 전체 평균 연봉 이상을 받는 직원의 이름과 연봉을, 연봉 높은 순으로."

```python
print(q("""
    SELECT name, salary
    FROM employees
    WHERE salary >= (SELECT AVG(salary) FROM employees)
    ORDER BY salary DESC
"""))
```

**기대 결과:**

```
  name  salary
0  강서연    7000
1  이영희    6000
2  최지은    5500
3  한예슬    5200   -- 5200 >= 5250? 아니오! → 실제론 제외됨
```

> 잠깐 — 한예슬(5200)은 전체 평균 **5250 미만**이라 빠집니다. 결과는 강서연·이영희·최지은 **3명**. (5200 < 5250을 눈으로 놓치기 쉬워 일부러 넣었습니다. 직접 실행해 확인하세요.)

---

## 검증 (노트북에서 실행)

```python
avg = q("SELECT AVG(salary) a FROM employees")["a"][0]
assert avg == 5250.0

# 전체 평균 초과
over = q("SELECT name FROM employees WHERE salary > (SELECT AVG(salary) FROM employees) ORDER BY emp_id")
assert list(over["name"]) == ["이영희", "최지은", "강서연"]

# IN 서브쿼리: 개발팀
dev = q("""SELECT name FROM employees
           WHERE dept_id IN (SELECT dept_id FROM departments WHERE dept_name='개발')""")
assert set(dev["name"]) == {"김철수", "이영희", "강서연"}

# 상관 서브쿼리: 부서 평균 초과 (한예슬은 NULL이라 제외)
corr = q("""SELECT name FROM employees e
            WHERE salary > (SELECT AVG(salary) FROM employees WHERE dept_id=e.dept_id)
            ORDER BY emp_id""")
assert list(corr["name"]) == ["최지은", "강서연"]
print("통과 ✅")
```

---

## 직접 풀어보기 (연습)

연습 1~2는 작은 샘플, 연습 3은 **Chinook 실제 DB**로 풉니다.

### 연습 1 — 최고 연봉자

> 가장 높은 연봉을 받는 직원의 이름을 조회하라. (서브쿼리로 MAX를 구해 비교)

```python
df = q("""
    -- TODO: WHERE salary = (SELECT MAX(salary) ...)
""")
assert list(df["name"]) == ["강서연"]   # 7000
print("통과 ✅")
```

### 연습 2 — 직원이 있는 부서 이름

> 직원이 한 명이라도 있는 부서의 이름을 조회하라. (마케팅 제외)
> **힌트**: `dept_id IN (SELECT DISTINCT dept_id FROM employees ...)`. employees의 dept_id 목록에 있는 부서만.

```python
df = q("""
    -- TODO: departments에서, employees에 등장하는 dept_id만
""")
assert set(df["dept_name"]) == {"개발", "영업", "인사"}   # 마케팅 제외
print("통과 ✅")
```

### 연습 3 — Chinook: 평균보다 긴 트랙 수 (실제 DB)

> Chinook에서 평균 재생시간(`Milliseconds`)보다 긴 트랙의 개수를 구하라.

```python
import sqlite3, pandas as pd
cconn = sqlite3.connect("../../data/chinook.db")
def cq(sql):
    return pd.read_sql_query(sql, cconn)

df = cq("""
    -- TODO: WHERE Milliseconds > (SELECT AVG(Milliseconds) FROM Track)
""")
assert df.iloc[0, 0] == 494
print("통과 ✅")
```

---

## 치트시트

| 하고 싶은 것 | 형태 |
|-------------|------|
| 단일 값 기준 비교 | `WHERE x > (SELECT ... )` |
| 여러 값 목록 기준 | `WHERE x IN (SELECT ...)` |
| 행마다 다른 기준 | 상관 서브쿼리 (`WHERE ... = e.col`) |
| 집계 결과를 테이블처럼 | `FROM (SELECT ...) AS 별칭` |
| 존재 여부 | `WHERE EXISTS (SELECT ...)` (심화) |

> 서브쿼리 vs JOIN: 많은 경우 **둘 다 가능**합니다. "목록으로 거르기"는 `IN` 서브쿼리가 읽기 쉽고, "여러 테이블 열을 한꺼번에 보기"는 JOIN이 낫습니다. 상관 서브쿼리는 "행마다 다른 기준"이 필요할 때 강력합니다.

---

## 정리

| 예제/연습 | 핵심 |
|-----------|------|
| 전체 평균 이상 | `WHERE salary >= (SELECT AVG...)` |
| 최고 연봉자 | `= (SELECT MAX...)` |
| 직원 있는 부서 | `dept_id IN (SELECT ... FROM employees)` |
| 부서 평균 초과 | 상관 서브쿼리 |
| Chinook 긴 트랙 | `> (SELECT AVG(Milliseconds)...)` |

> 핵심 한 줄: **서브쿼리 = (안쪽 쿼리가 먼저 값/목록/테이블을 만들고) → (바깥 쿼리가 그걸 기준으로 조회). 행마다 달라야 하면 상관 서브쿼리.**