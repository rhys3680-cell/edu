# SQL 12 — 조인 (JOIN)

> **대상**: SQL 11 (집계)을 마친 단계.
> **목표**: 여러 테이블을 **ID로 연결**해 한 결과로 합치는 `JOIN` — 특히 **INNER vs LEFT** 차이 — 익히기.

09에서 봤듯, 실무 DB는 데이터가 여러 테이블에 나뉘어 있습니다. `employees`엔 `dept_id`(숫자)만 있고 부서 **이름**은 `departments`에 있죠. 둘을 합쳐 보려면 **JOIN**이 필요합니다. JOIN은 SQL의 진짜 힘이 시작되는 지점입니다.

---

## 0) 샘플 데이터 (10·11과 동일)

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

> 기억할 두 가지 특이점: **한예슬은 `dept_id`가 NULL**(부서 없음), **마케팅(4번) 부서엔 직원이 없음**. 이 둘이 JOIN 종류를 가르는 시험대입니다.

---

## 1) INNER JOIN — 양쪽 다 있는 것만

`employees`와 `departments`를 `dept_id`로 연결합니다. **양쪽에 짝이 있는 행만** 결과에 남습니다.

```sql
SELECT e.name, d.dept_name
FROM employees e
JOIN departments d ON e.dept_id = d.dept_id;
```

- `e`, `d`는 **테이블 별칭**(긴 이름 줄이기). `e.name`은 "employees의 name".
- `ON e.dept_id = d.dept_id` — **연결 조건**(어떤 열로 짝을 맞출지).
- 그냥 `JOIN`은 `INNER JOIN`과 같습니다.

> 결과: **7행**. 한예슬은 `dept_id`가 NULL이라 어느 부서와도 짝이 안 맞아 **빠집니다**. (마케팅도 안 보이지만, 이건 "직원이 없는 부서"라 직원 기준 조회엔 원래 안 나옴)

---

## 2) LEFT JOIN — 왼쪽은 무조건 다, 짝 없으면 NULL

**왼쪽 테이블(FROM 뒤)의 모든 행을 남기고**, 오른쪽에 짝이 없으면 그 열을 NULL로 채웁니다.

```sql
SELECT e.name, d.dept_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.dept_id;
```

> 결과: **8행**. 한예슬도 남고, `dept_name`이 **NULL(None)**로 나옵니다. "직원은 다 보여주되, 부서 없으면 빈칸"이 필요할 때 LEFT JOIN.

**방향을 바꾸면 "직원 없는 부서"도 볼 수 있습니다:**

```sql
-- 부서를 기준(왼쪽)으로 → 직원 없는 마케팅도 살아남음
SELECT d.dept_name, COUNT(e.emp_id) AS 인원
FROM departments d
LEFT JOIN employees e ON d.dept_id = e.dept_id
GROUP BY d.dept_id
ORDER BY d.dept_id;
-- 개발 3, 영업 3, 인사 1, 마케팅 0
```

> ⚠️ 함정: 여기서 `COUNT(*)`가 아니라 **`COUNT(e.emp_id)`**를 써야 마케팅이 0으로 나옵니다. `COUNT(*)`는 LEFT JOIN으로 생긴 NULL 행까지 1로 세서 마케팅이 1이 돼버립니다. (11의 "COUNT(*) vs COUNT(열)" 함정과 연결)

---

## 3) INNER vs LEFT 한눈에

| | 남는 행 | 짝 없으면 |
|--|--------|----------|
| `INNER JOIN` | 양쪽 다 있는 것만 | 제외 |
| `LEFT JOIN` | 왼쪽 전부 | 오른쪽 열을 NULL로 |

> 판단: **"짝 없는 것도 보여줘야 하나?"** → 예면 LEFT, 아니면 INNER. "주문 없는 고객도", "직원 없는 부서도", "안 팔린 상품도" 류는 전부 LEFT JOIN 신호.

---

## 대표 예제 — 부서명까지 붙여 집계

> "부서 이름별 인원과 평균 연봉을, 직원이 없는 부서도 포함해서, dept_id 순으로."

```python
print(q("""
    SELECT d.dept_name,
           COUNT(e.emp_id)        AS 인원,
           AVG(e.salary)          AS 평균연봉
    FROM departments d
    LEFT JOIN employees e ON d.dept_id = e.dept_id
    GROUP BY d.dept_id
    ORDER BY d.dept_id
"""))
```

**기대 결과:**

```
  dept_name  인원         평균연봉
0       개발    3  6000.000000
1       영업    3  4933.333333
2       인사    1  4000.000000
3      마케팅    0          NaN   -- 직원 없음 → 인원 0, 평균은 NULL
```

> 가르칠 포인트: **`departments`를 왼쪽에 둔 LEFT JOIN** 덕에 직원 없는 마케팅도 살아남습니다. 평균 연봉은 더할 직원이 없어 `NULL(NaN)`. 한예슬(부서 NULL)은 `departments`에 짝이 없으니 이 결과(부서 기준)엔 안 나옵니다.

---

## 검증 (노트북에서 실행)

```python
inner = q("SELECT e.name FROM employees e JOIN departments d ON e.dept_id=d.dept_id")
left  = q("SELECT e.name FROM employees e LEFT JOIN departments d ON e.dept_id=d.dept_id")
assert len(inner) == 7      # 한예슬 제외
assert len(left)  == 8      # 한예슬 포함

# 한예슬은 LEFT JOIN에서 dept_name이 NULL
row = q("SELECT d.dept_name FROM employees e LEFT JOIN departments d ON e.dept_id=d.dept_id WHERE e.name='한예슬'")
assert row["dept_name"].isna().all()

# 부서 기준 LEFT JOIN: 마케팅 인원 0
cnt = q("""SELECT d.dept_name, COUNT(e.emp_id) c FROM departments d
           LEFT JOIN employees e ON d.dept_id=e.dept_id
           GROUP BY d.dept_id ORDER BY d.dept_id""")
assert list(cnt["c"]) == [3, 3, 1, 0]
print("통과 ✅")
```

---

## 직접 풀어보기 (연습)

연습 1~2는 작은 샘플(`:memory:`), 연습 3은 **Chinook 실제 DB**로 풉니다.

### 연습 1 — 직원 이름 + 부서 이름 (INNER)

> 부서가 배정된 직원의 이름과 부서 이름을 `emp_id` 순으로 조회하라.

```python
df = q("""
    -- TODO: employees JOIN departments
""")
assert len(df) == 7                       # 한예슬 제외
assert df.iloc[0]["dept_name"] == "개발"   # emp_id=1 김철수 → 개발
print("통과 ✅")
```

### 연습 2 — 부서별 최고 연봉자 (JOIN + 집계)

> 부서 이름별 최고 연봉을, 직원이 있는 부서만, 부서 이름과 함께 조회하라.

```python
df = q("""
    -- TODO: JOIN 후 GROUP BY, MAX(salary)
""")
# 개발 7000, 영업 5500, 인사 4000 (마케팅은 직원 없어 INNER면 제외)
assert set(zip(df["dept_name"], df.iloc[:, 1])) == {("개발",7000),("영업",5500),("인사",4000)}
print("통과 ✅")
```

### 연습 3 — Chinook: 아티스트별 앨범 수 (실제 DB)

> Chinook에서 아티스트별 앨범 수를 구해, 앨범이 많은 순 상위 3명을 조회하라.
> (별도 connection 필요 — 아래 셀 참고)

```python
import sqlite3, pandas as pd
cconn = sqlite3.connect("../../data/chinook.db")   # 노트북 위치 기준 경로
def cq(sql):
    return pd.read_sql_query(sql, cconn)

df = cq("""
    -- TODO: Artist JOIN Album, GROUP BY 아티스트, COUNT(앨범), ORDER BY DESC LIMIT 3
""")
assert list(df["Name"]) == ["Iron Maiden", "Led Zeppelin", "Deep Purple"]
assert list(df.iloc[:, 1]) == [21, 14, 11]
print("통과 ✅")
```

---

## 치트시트

| 하고 싶은 것 | 절(clause) |
|-------------|-----------|
| 두 테이블 합치기 (짝 있는 것만) | `A JOIN B ON A.id = B.id` |
| 왼쪽 전부 + 짝 없으면 NULL | `A LEFT JOIN B ON ...` |
| 테이블 이름 줄이기 | `FROM employees e` (별칭) |
| 3개 이상 테이블 | `A JOIN B ON ... JOIN C ON ...` |
| LEFT JOIN 후 개수 셀 때 | `COUNT(B.열)` (NULL 안 셈), `COUNT(*)` 아님! |

> JOIN의 첫 판단: **"짝 없는 행도 결과에 남겨야 하나?"** → 예면 LEFT, 아니면 INNER. 그리고 **연결 열(`ON`)을 무엇으로 할지**가 두 번째.

---

## 정리

| 예제/연습 | 핵심 |
|-----------|------|
| 부서명 붙여 집계 | `departments LEFT JOIN employees` → 직원 0 부서도 |
| 직원+부서 이름 | `INNER JOIN` (짝 있는 7명) |
| 부서별 최고 연봉 | `JOIN + GROUP BY + MAX` |
| Chinook 앨범 수 | `Artist JOIN Album` (실제 DB) |

> 핵심 한 줄: **JOIN = (연결 열을 ON으로) → (INNER면 짝 있는 것만 / LEFT면 왼쪽 전부) → (필요하면 GROUP BY로 집계).**