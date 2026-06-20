# SQL 11 — 집계 (GROUP BY)

> **대상**: SQL 10 (기초 조회)를 마친 단계.
> **목표**: "여러 행을 묶어 하나의 값으로 요약"하는 집계 — 집계 함수 / `GROUP BY` / `HAVING` — 익히기.

10에서는 "행을 골랐다"면, 여기선 **"행들을 묶어 통계를 낸다"**입니다. 부서별 평균 연봉, 연도별 입사 인원처럼 **"~별 ~의 합/평균/개수"**가 모두 집계입니다. 02·07에서 본 "그룹별 모으기"를 SQL로 하는 셈이죠.

---

## 0) 샘플 데이터 (10과 동일)

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

## 1) 집계 함수 — 전체를 하나로 요약

`GROUP BY` 없이 쓰면 **테이블 전체**가 하나의 그룹입니다.

```sql
SELECT COUNT(*)      FROM employees;   -- 전체 행 수: 8
SELECT COUNT(dept_id) FROM employees;  -- NULL 제외 개수: 7  (한예슬 제외!)
SELECT SUM(salary)   FROM employees;   -- 연봉 합계
SELECT AVG(salary)   FROM employees;   -- 평균
SELECT MAX(salary), MIN(salary) FROM employees;  -- 최대/최소
```

> ⚠️ **`COUNT(*)` vs `COUNT(열)`**: `COUNT(*)`는 모든 행을 세지만, `COUNT(열)`은 **그 열이 NULL인 행을 빼고** 셉니다. 한예슬의 `dept_id`가 NULL이라 `COUNT(dept_id)=7`. SQL 면접 단골 함정입니다.

> 참고: `AVG`, `SUM` 등 다른 집계 함수도 NULL은 **무시**하고 계산합니다 (0으로 치지 않음).

---

## 2) GROUP BY — ~별로 묶어 집계

**"부서별", "연도별"** 같은 "~별"이 나오면 `GROUP BY`입니다.

```sql
-- 부서별 인원 수
SELECT dept_id, COUNT(*) AS 인원
FROM employees
GROUP BY dept_id;

-- 부서별 평균 연봉
SELECT dept_id, AVG(salary) AS 평균연봉
FROM employees
GROUP BY dept_id;

-- 입사 연도별 인원
SELECT hire_year, COUNT(*) AS 인원
FROM employees
GROUP BY hire_year
ORDER BY hire_year;
```

> 핵심 규칙: **`SELECT`에 오는 열은 (1) `GROUP BY`에 쓴 열이거나 (2) 집계 함수**여야 합니다. "부서별로 묶었는데 개인 이름을 뽑으라"는 건 말이 안 되니까요(한 그룹에 여러 이름).

> NULL도 하나의 그룹: `dept_id`가 NULL인 한예슬은 "NULL 그룹"으로 따로 집계됩니다.

---

## 3) HAVING — 집계 결과를 거르기

`WHERE`는 **묶기 전 행**을 거르고, `HAVING`은 **묶은 후 그룹**을 거릅니다.

```sql
-- 평균 연봉이 5000 이상인 부서만
SELECT dept_id, AVG(salary) AS 평균연봉
FROM employees
GROUP BY dept_id
HAVING AVG(salary) >= 5000;

-- 인원이 2명 이상인 부서만
SELECT dept_id, COUNT(*) AS 인원
FROM employees
GROUP BY dept_id
HAVING COUNT(*) >= 2;
```

> 결정적 차이: **`WHERE`엔 집계 함수를 못 씁니다** (아직 안 묶였으니까). "그룹의 합/평균/개수로 거르기"는 무조건 `HAVING`.
>
> 둘을 같이 쓰면: `WHERE`(행 거르기) → `GROUP BY`(묶기) → `HAVING`(그룹 거르기) 순서로 적용됩니다.

```sql
-- 2018년 이후 입사자만 대상으로, 부서별 평균이 5000 이상인 부서
SELECT dept_id, AVG(salary) AS 평균연봉
FROM employees
WHERE hire_year >= 2018       -- 먼저 행을 거르고
GROUP BY dept_id              -- 부서별로 묶은 뒤
HAVING AVG(salary) >= 5000;   -- 그룹 평균으로 거름
```

---

## 대표 예제 — 부서별 통계 + 조건

> "부서별 인원과 평균 연봉을, 인원이 2명 이상인 부서만, 평균 연봉 높은 순으로."

```python
print(q("""
    SELECT dept_id,
           COUNT(*)    AS 인원,
           AVG(salary) AS 평균연봉
    FROM employees
    GROUP BY dept_id
    HAVING COUNT(*) >= 2
    ORDER BY 평균연봉 DESC
"""))
```

**기대 결과:**

```
   dept_id  인원       평균연봉
0      1.0    3  6000.000000   -- 개발: (5000+6000+7000)/3
1      2.0    3  4933.333333   -- 영업: (4500+5500+4800)/3
```

> 인사(3번)는 1명, NULL 그룹(한예슬)도 1명이라 `HAVING COUNT(*) >= 2`에서 제외됩니다. 개발·영업만 남습니다.

---

## 검증 (노트북에서 실행)

```python
# 부서별 인원
df = q("SELECT dept_id, COUNT(*) AS cnt FROM employees GROUP BY dept_id ORDER BY dept_id")
print(df)

assert q("SELECT COUNT(*) AS c FROM employees")["c"][0] == 8
assert q("SELECT COUNT(dept_id) AS c FROM employees")["c"][0] == 7   # NULL 제외
assert q("SELECT AVG(salary) AS a FROM employees WHERE dept_id=1")["a"][0] == 6000
# HAVING: 인원 2명 이상 부서 수 (개발3, 영업3 → 2개 부서)
assert len(q("SELECT dept_id FROM employees GROUP BY dept_id HAVING COUNT(*)>=2")) == 2
print("통과 ✅")
```

---

## 직접 풀어보기 (연습)

`q("...")`에 SQL을 채운 뒤 검증 셀을 실행하세요. **"무엇별로(GROUP BY) · 무엇을(집계함수) · 어떤 그룹만(HAVING)"**을 먼저 정합니다.

### 연습 1 — 부서별 최고 연봉

> 부서별 가장 높은 연봉을 `dept_id` 순으로 조회하라. (NULL 그룹 포함)

```python
df = q("""
    -- TODO: 직접 작성 (GROUP BY + MAX)
""")
# SQLite는 ORDER BY에서 NULL을 맨 앞에 둠 → NULL그룹(5200), 1(7000), 2(5500), 3(4000)
assert list(df.iloc[:, 1]) == [5200, 7000, 5500, 4000]
print("통과 ✅")
```

> 참고: SQLite는 `ORDER BY`에서 **NULL을 가장 작은 값으로 취급해 맨 앞**에 둡니다. (DBMS마다 다를 수 있고, `NULLS LAST`로 바꿀 수도 있습니다.)

### 연습 2 — 입사 연도별 인원

> 입사 연도별 인원 수를, 연도 오름차순으로 조회하라.

```python
df = q("""
    -- TODO: 직접 작성 (GROUP BY hire_year)
""")
# 2015:1, 2017:1, 2018:1, 2019:2, 2020:1, 2021:1, 2022:1
assert list(df["인원"]) == [1, 1, 1, 2, 1, 1, 1]
print("통과 ✅")
```

### 연습 3 — 평균 연봉이 5000 이상인 부서 (HAVING, 도전)

> 부서별 평균 연봉이 5000 이상인 부서의 `dept_id`만 조회하라.

```python
df = q("""
    -- TODO: 직접 작성 (GROUP BY + HAVING AVG)
""")
# 개발(6000)만 5000 이상. 영업 4933, 인사 4000, NULL그룹 5200
# → 개발(1)과 NULL그룹(5200) 두 개
assert set(df["dept_id"].dropna()) == {1}        # 부서 중엔 개발만
assert len(df) == 2                              # 개발 + NULL그룹
print("통과 ✅")
```

---

## 치트시트

| 하고 싶은 것 | 절(clause) |
|-------------|-----------|
| 전체 개수 / NULL 제외 개수 | `COUNT(*)` / `COUNT(열)` |
| 합 / 평균 / 최대 / 최소 | `SUM` / `AVG` / `MAX` / `MIN` |
| ~별로 묶기 | `GROUP BY 열` |
| 묶은 결과 거르기 | `HAVING 집계조건` |
| 묶기 전 행 거르기 | `WHERE 행조건` |

> 실행 순서: **`FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY`**. "거르고(WHERE) → 묶고(GROUP BY) → 그룹 거르고(HAVING) → 정렬(ORDER BY)".

> WHERE vs HAVING 한 줄 정리: **개별 행 조건은 WHERE, 그룹 집계 조건은 HAVING.**

---

## 정리

| 예제/연습 | 핵심 |
|-----------|------|
| 부서별 통계 | `GROUP BY + COUNT/AVG + HAVING` |
| 부서별 최고 연봉 | `GROUP BY dept_id + MAX` |
| 연도별 인원 | `GROUP BY hire_year + COUNT` |
| 평균 5000+ 부서 | `HAVING AVG(salary) >= 5000` |

> 핵심 한 줄: **집계 = (WHERE로 행 거르고) → (GROUP BY로 묶고) → (집계함수로 요약) → (HAVING으로 그룹 거르기).**