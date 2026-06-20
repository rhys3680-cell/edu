# SQL 10 — 기초 조회 (SELECT)

> **대상**: 코딩테스트 단계(00~08)를 마친 단계.
> **목표**: "필요한 행과 열만 골라 가져오는" SQL의 기본기 — `SELECT` / `WHERE` / `ORDER BY` / `LIMIT` — 익히기.

SQL은 "데이터를 어떻게 가져올지 **선언**"하는 언어입니다. 파이썬 반복문처럼 "어떻게 순회할지"를 쓰는 게 아니라, **"무엇을 원하는지"**만 적으면 DB가 알아서 가져옵니다.

---

## 0) 실습 환경 — SQLite (설치 불필요)

이 단계는 모두 **SQLite**로 실습합니다. 파이썬 표준 라이브러리 `sqlite3`로 노트북에서 바로 쓸 수 있어 설치·계정·비밀번호가 필요 없습니다.

```python
import sqlite3
import pandas as pd

# 메모리상의 임시 DB (노트북을 닫으면 사라짐 → 매번 깨끗하게 재현)
conn = sqlite3.connect(":memory:")

# 쿼리 결과를 pandas DataFrame으로 보기 좋게 출력하는 헬퍼
def q(sql):
    return pd.read_sql_query(sql, conn)
```

> 팁: `pd.read_sql_query`로 결과를 DataFrame으로 받으면 표 형태로 깔끔하게 보입니다. (pandas는 3단계에서 본격적으로 배우지만, 여기선 "예쁜 출력 도구"로만 씁니다.)

---

## 1) 샘플 데이터 만들기 (모든 SQL 노트북 공통)

부서(`departments`)와 직원(`employees`) 두 테이블을 씁니다. **이 스키마를 SQL 단계 내내 재사용**합니다.

```python
conn.executescript("""
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    dept_id   INTEGER PRIMARY KEY,
    dept_name TEXT NOT NULL
);

CREATE TABLE employees (
    emp_id    INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    dept_id   INTEGER,           -- 어느 부서 소속인지 (departments.dept_id 참조)
    salary    INTEGER,
    hire_year INTEGER
);

INSERT INTO departments VALUES
    (1, '개발'), (2, '영업'), (3, '인사'), (4, '마케팅');

INSERT INTO employees VALUES
    (1, '김철수', 1, 5000, 2018),
    (2, '이영희', 1, 6000, 2017),
    (3, '박민수', 2, 4500, 2020),
    (4, '최지은', 2, 5500, 2019),
    (5, '정현우', 3, 4000, 2021),
    (6, '강서연', 1, 7000, 2015),
    (7, '윤도현', 2, 4800, 2022),
    (8, '한예슬', NULL, 5200, 2019);   -- 아직 부서 미배정
""")
```

> `8번 한예슬`은 `dept_id`가 `NULL`(부서 미배정)입니다. NULL 처리는 SQL의 단골 함정이라 일부러 넣어뒀습니다.

---

## 2) SELECT — 열 고르기

```sql
-- 모든 열
SELECT * FROM employees;

-- 특정 열만
SELECT name, salary FROM employees;

-- 별칭(AS)으로 열 이름 바꾸기
SELECT name AS 이름, salary AS 연봉 FROM employees;
```

> `*`는 "모든 열". 실무에선 필요한 열만 명시하는 게 좋습니다(성능·가독성).

---

## 3) WHERE — 행 거르기

```sql
-- 연봉이 5000 이상인 직원
SELECT name, salary FROM employees WHERE salary >= 5000;

-- 개발팀(dept_id=1) 직원
SELECT name FROM employees WHERE dept_id = 1;

-- 여러 조건: AND / OR
SELECT name FROM employees WHERE dept_id = 1 AND salary >= 6000;

-- 범위: BETWEEN
SELECT name FROM employees WHERE hire_year BETWEEN 2018 AND 2020;

-- 목록: IN
SELECT name FROM employees WHERE dept_id IN (1, 2);

-- 문자열 패턴: LIKE (%=아무 글자들)
SELECT name FROM employees WHERE name LIKE '김%';   -- '김'으로 시작
```

> ⚠️ **NULL 주의**: `WHERE dept_id = NULL`은 작동하지 않습니다(아무것도 안 나옴). NULL은 `IS NULL` / `IS NOT NULL`로 비교해야 합니다.
> ```sql
> SELECT name FROM employees WHERE dept_id IS NULL;   -- 한예슬
> ```

---

## 4) ORDER BY / LIMIT — 정렬과 개수 제한

```sql
-- 연봉 높은 순 (내림차순)
SELECT name, salary FROM employees ORDER BY salary DESC;

-- 부서별로 묶고, 그 안에서 연봉 높은 순 (다중 정렬)
SELECT name, dept_id, salary FROM employees ORDER BY dept_id ASC, salary DESC;

-- 상위 3명만
SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 3;
```

> `ORDER BY 열 DESC/ASC`는 02 정렬의 `key`와 같은 발상 — "무엇을 기준으로 줄 세울지". 다중 정렬도 콤마로 1순위, 2순위.

---

## 대표 예제 — 조건 + 정렬 조합

> "2018년 이후 입사한 직원 중 연봉 5000 이상인 사람을, 연봉 높은 순으로 이름과 연봉만."

```python
print(q("""
    SELECT name, salary
    FROM employees
    WHERE hire_year >= 2018 AND salary >= 5000
    ORDER BY salary DESC
"""))
```

**기대 결과 (3명):**

```
   name  salary
0  최지은    5500   -- 2019, 5500  ✓
1  한예슬    5200   -- 2019, 5200  ✓ (부서 NULL이지만 이 조건엔 무관)
2  김철수    5000   -- 2018, 5000  ✓
```

> 짚어볼 점: 강서연(7000, 2015)·이영희(6000, 2017)는 `hire_year >= 2018`에서 걸러집니다. 그리고 **한예슬은 부서가 NULL이지만 이 조건(입사연도·연봉)과는 무관**하므로 그대로 포함됩니다. "NULL이면 빠질 것"이라는 선입견을 조심하세요 — NULL은 그 열을 비교할 때만 문제가 됩니다.

---

## 검증 (노트북에서 실행)

```python
# 결과 행 수와 값을 직접 확인
df = q("""
    SELECT name, salary FROM employees
    WHERE hire_year >= 2018 AND salary >= 5000
    ORDER BY salary DESC
""")
print(df)

assert list(df["name"]) == ["최지은", "한예슬", "김철수"]   # 5500, 5200, 5000 순
assert len(q("SELECT * FROM employees WHERE dept_id IS NULL")) == 1   # 한예슬
assert len(q("SELECT * FROM employees WHERE dept_id = 1")) == 3       # 개발팀 3명
print("통과 ✅")
```

---

## 직접 풀어보기 (연습)

`q("...")`에 SQL을 채운 뒤 검증 셀을 실행하세요. **"어떤 열(SELECT) · 어떤 행(WHERE) · 어떤 순서(ORDER BY)"**를 먼저 정합니다.

### 연습 1 — 영업팀 직원 이름

> 영업팀(`dept_id = 2`) 직원의 이름을 `emp_id` 순으로 조회하라.

```python
df = q("""
    -- TODO: 직접 작성
""")
assert list(df["name"]) == ["박민수", "최지은", "윤도현"]
print("통과 ✅")
```

### 연습 2 — 연봉 상위 3명

> 연봉이 높은 순으로 직원 이름과 연봉 상위 3명을 조회하라.

```python
df = q("""
    -- TODO: 직접 작성 (ORDER BY + LIMIT)
""")
assert list(df["name"]) == ["강서연", "이영희", "최지은"]   # 7000, 6000, 5500
print("통과 ✅")
```

### 연습 3 — 이름이 '이'로 시작하거나 부서 미배정

> 이름이 '이'로 시작하거나(`LIKE`) 부서가 없는(`IS NULL`) 직원의 이름을 조회하라.

```python
df = q("""
    -- TODO: 직접 작성 (LIKE + OR + IS NULL)
""")
assert set(df["name"]) == {"이영희", "한예슬"}
print("통과 ✅")
```

---

## 치트시트

| 하고 싶은 것 | 절(clause) |
|-------------|-----------|
| 열 고르기 | `SELECT 열1, 열2` |
| 모든 열 | `SELECT *` |
| 행 거르기 | `WHERE 조건` |
| 범위 / 목록 / 패턴 | `BETWEEN` / `IN` / `LIKE` |
| NULL 비교 | `IS NULL` / `IS NOT NULL` (= 안 됨!) |
| 정렬 | `ORDER BY 열 ASC/DESC` |
| 개수 제한 | `LIMIT n` |

> SQL 실행 순서(중요): **`FROM` → `WHERE` → `SELECT` → `ORDER BY` → `LIMIT`**. 작성 순서와 다릅니다. "어디서(FROM) 가져와 → 거르고(WHERE) → 고르고(SELECT) → 정렬(ORDER BY)"로 읽으면 이해가 쉽습니다.

---

## 정리

| 예제/연습 | 핵심 |
|-----------|------|
| 조건 + 정렬 | `WHERE ... ORDER BY ... DESC` |
| 영업팀 조회 | `WHERE dept_id = 2` |
| 상위 3명 | `ORDER BY ... DESC LIMIT 3` |
| 패턴/NULL | `LIKE '이%' OR dept_id IS NULL` |

> 핵심 한 줄: **SELECT = (어떤 열) FROM (어디서) WHERE (어떤 행) ORDER BY (어떤 순서) LIMIT (몇 개).**