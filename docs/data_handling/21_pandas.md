# 데이터 핸들링 21 — pandas

> **대상**: numpy(20)와 SQL(09~14)을 마친 단계.
> **목표**: 표 형태 데이터를 다루는 **DataFrame** — 선택/필터/정렬/`groupby`/`merge` — 익히기. **SQL과 1:1로 대조**하며 배웁니다.

pandas는 데이터 분석의 **주력 도구**입니다. 핵심 자료구조 `DataFrame`은 **"파이썬 안의 표(테이블)"** — SQL 테이블과 거의 똑같습니다. 그래서 SQL을 배운 우리에겐 큰 장점이 있죠: **SQL의 `SELECT`/`WHERE`/`GROUP BY`/`JOIN`이 pandas에서 무엇인지 짝지으면** 절반은 끝납니다.

---

## 0) 샘플 데이터 — SQL과 같은 employees/departments

SQL 단계에서 쓴 그 데이터를 DataFrame으로 만듭니다.

```python
import pandas as pd

emp = pd.DataFrame({
    "emp_id":    [1, 2, 3, 4, 5, 6, 7, 8],
    "name":      ["김철수","이영희","박민수","최지은","정현우","강서연","윤도현","한예슬"],
    "dept_id":   [1, 1, 2, 2, 3, 1, 2, None],   # 한예슬은 부서 없음(NaN)
    "salary":    [5000, 6000, 4500, 5500, 4000, 7000, 4800, 5200],
    "hire_year": [2018, 2017, 2020, 2019, 2021, 2015, 2022, 2019],
})
dept = pd.DataFrame({
    "dept_id":   [1, 2, 3, 4],
    "dept_name": ["개발", "영업", "인사", "마케팅"],
})
```

> `DataFrame`은 **열(column)마다 이름이 있는 2차원 표**입니다. `emp.head()`로 앞 몇 줄, `emp.shape`로 (행, 열), `emp.info()`로 요약을 봅니다.

---

## 1) 열 선택 — SQL의 SELECT

```python
emp["name"]                 # 한 열 (Series)
emp[["name", "salary"]]     # 여러 열 (DataFrame) — 대괄호 두 개!
```

| SQL | pandas |
|-----|--------|
| `SELECT name FROM emp` | `emp["name"]` |
| `SELECT name, salary FROM emp` | `emp[["name", "salary"]]` |

> 헷갈림 주의: 한 열은 `emp["name"]`, 여러 열은 **리스트로** `emp[["name","salary"]]`.

---

## 2) 행 필터 — SQL의 WHERE (불리언 인덱싱)

20의 numpy 불리언 인덱싱이 그대로 이어집니다.

```python
emp[emp["salary"] >= 5000]                       # 연봉 5000 이상
emp[(emp["dept_id"] == 1) & (emp["salary"] >= 6000)]   # AND는 &
emp[emp["dept_id"].isna()]                       # 부서 없음(NULL) → 한예슬
```

| SQL | pandas |
|-----|--------|
| `WHERE salary >= 5000` | `emp[emp["salary"] >= 5000]` |
| `WHERE a = 1 AND b >= 6000` | `emp[(emp.a==1) & (emp.b>=6000)]` |
| `WHERE dept_id IS NULL` | `emp[emp["dept_id"].isna()]` |

> ⚠️ 주의 두 가지: (1) `AND`/`OR` 대신 **`&`/`|`**, 각 조건은 **괄호로** 감쌀 것. (2) NULL은 `== None`이 아니라 **`.isna()`** (SQL의 `IS NULL`과 같은 함정).

---

## 3) 정렬 & 상위 N — ORDER BY / LIMIT

```python
emp.sort_values("salary", ascending=False)          # 연봉 내림차순
emp.sort_values("salary", ascending=False).head(3)  # 상위 3명
```

| SQL | pandas |
|-----|--------|
| `ORDER BY salary DESC` | `.sort_values("salary", ascending=False)` |
| `LIMIT 3` | `.head(3)` |

---

## 4) 집계 — GROUP BY (핵심)

SQL `GROUP BY`가 pandas `groupby`입니다. 거의 똑같이 생겼어요.

```python
emp.groupby("dept_id")["salary"].mean()    # 부서별 평균 연봉
emp.groupby("dept_id").size()              # 부서별 인원 (COUNT(*))
emp.groupby("dept_id")["salary"].agg(["mean", "max", "count"])  # 여러 집계
```

| SQL | pandas |
|-----|--------|
| `GROUP BY dept_id` | `.groupby("dept_id")` |
| `AVG(salary)` | `["salary"].mean()` |
| `COUNT(*)` | `.size()` |
| `HAVING avg >= 5000` | `groupby 결과를 다시 불리언 필터` |

> `groupby`의 결과도 다시 필터링됩니다 — SQL의 `HAVING`은 "groupby 결과에 불리언 인덱싱"으로:
> ```python
> g = emp.groupby("dept_id")["salary"].mean()
> g[g >= 5000]      # 평균 5000 이상 부서 (HAVING AVG >= 5000)
> ```

> 참고: `groupby`도 NaN(한예슬)은 기본적으로 그룹에서 **제외**합니다 (11의 NULL 그룹 처리와 다른 점 — pandas 기본값).

---

## 5) 테이블 합치기 — JOIN (merge)

SQL `JOIN`이 pandas `merge`입니다.

```python
emp.merge(dept, on="dept_id")                 # INNER JOIN (기본)
emp.merge(dept, on="dept_id", how="left")     # LEFT JOIN
```

| SQL | pandas |
|-----|--------|
| `emp JOIN dept ON emp.dept_id=dept.dept_id` | `emp.merge(dept, on="dept_id")` |
| `emp LEFT JOIN dept ...` | `emp.merge(dept, on="dept_id", how="left")` |

> 12에서 본 그대로: **INNER는 7행**(한예슬 제외), **LEFT는 8행**(한예슬 `dept_name`=NaN). SQL JOIN 직관이 그대로 적용됩니다.

---

## 6) 새 열 만들기 — 파생 변수 (ML 전처리의 핵심)

```python
emp["bonus"] = emp["salary"] * 0.1            # 연봉의 10%
emp["tenure"] = 2026 - emp["hire_year"]       # 근속 연수
emp["high_paid"] = emp["salary"] >= 5500      # 조건 → True/False 열
```

> SQL에선 `SELECT salary * 0.1 AS bonus`처럼 조회 때 계산했지만, pandas에선 **표에 새 열을 추가**합니다. ML에서 "피처(feature) 만들기"가 바로 이것 — 원본 데이터에서 새 변수를 파생시킵니다.

---

## 대표 예제 — 부서명 붙여 부서별 평균 (merge + groupby)

> "부서 이름별 평균 연봉을, 평균 높은 순으로." (12 JOIN + 11 GROUP BY를 pandas로)

```python
import pandas as pd

result = (
    emp.merge(dept, on="dept_id")              # 부서명 붙이고 (INNER)
       .groupby("dept_name")["salary"]         # 부서명별로 묶어
       .mean()                                  # 평균
       .sort_values(ascending=False)            # 높은 순
)
print(result)
```

**기대 결과:**

```
dept_name
개발    6000.000000
영업    4933.333333
인사    4000.000000
Name: salary, dtype: float64
```

> 가르칠 포인트: **메서드 체이닝** — `.merge().groupby().mean().sort_values()`를 점으로 이어 한 흐름으로. SQL이 `JOIN → GROUP BY → ORDER BY`를 한 쿼리로 쓴 것과 같은 발상입니다. 한예슬(부서 NaN)은 INNER merge에서 빠지고, 마케팅(직원 없음)도 안 나옵니다.

---

## 검증 (노트북에서 실행)

```python
import pandas as pd

# 필터 (WHERE)
assert emp[emp["salary"] >= 5000]["name"].tolist() == ["김철수","이영희","최지은","강서연","한예슬"]
# 정렬 + 상위 (ORDER BY + LIMIT)
assert emp.sort_values("salary", ascending=False).head(3)["name"].tolist() == ["강서연","이영희","최지은"]
# groupby (GROUP BY)
assert emp.groupby("dept_id")["salary"].mean()[1.0] == 6000.0
# merge (JOIN)
assert len(emp.merge(dept, on="dept_id")) == 7              # INNER
assert len(emp.merge(dept, on="dept_id", how="left")) == 8  # LEFT
# NULL 필터 (IS NULL)
assert emp[emp["dept_id"].isna()]["name"].tolist() == ["한예슬"]
print("통과 ✅")
```

---

## 직접 풀어보기 (연습)

`emp`/`dept`를 써서 `TODO`를 채운 뒤 검증 셀을 실행하세요. **"SQL이라면 어떻게 썼지?"**를 떠올리면 pandas 표현이 따라옵니다.

### 연습 1 — 영업팀 직원 이름 (WHERE)

> 영업팀(`dept_id == 2`) 직원의 이름을 `emp_id` 순으로 리스트로 반환하라.

```python
def solution(emp):
    # TODO: 필터링 후 name 리스트
    pass

assert solution(emp) == ["박민수", "최지은", "윤도현"]
print("통과 ✅")
```

### 연습 2 — 부서별 최고 연봉 (groupby)

> 부서별(`dept_id`) 최고 연봉을 dict로 반환하라. (`{dept_id: max_salary}`)
> **힌트**: `.groupby("dept_id")["salary"].max().to_dict()`.

```python
def solution(emp):
    # TODO
    pass

# NaN 그룹은 pandas groupby에서 제외됨 → 1,2,3만
assert solution(emp) == {1.0: 7000, 2.0: 5500, 3.0: 4000}
print("통과 ✅")
```

### 연습 3 — 부서명별 인원 (merge + groupby)

> 직원이 있는 부서의 이름별 인원 수를 dict로 반환하라. (`{dept_name: count}`)
> **힌트**: `emp.merge(dept, on="dept_id").groupby("dept_name").size().to_dict()`.

```python
def solution(emp, dept):
    # TODO
    pass

assert solution(emp, dept) == {"개발": 3, "영업": 3, "인사": 1}   # 마케팅 0명은 INNER라 제외
print("통과 ✅")
```

---

## 치트시트 — SQL ↔ pandas

| SQL | pandas |
|-----|--------|
| `SELECT col` | `df["col"]` / `df[["a","b"]]` |
| `WHERE cond` | `df[df["col"] > x]` |
| `AND` / `OR` | `&` / `\|` (각 조건 괄호) |
| `IS NULL` | `df["col"].isna()` |
| `ORDER BY col DESC` | `df.sort_values("col", ascending=False)` |
| `LIMIT n` | `df.head(n)` |
| `GROUP BY` + 집계 | `df.groupby("col")["x"].mean()` |
| `HAVING` | groupby 결과에 불리언 필터 |
| `JOIN` / `LEFT JOIN` | `df.merge(df2, on="key")` / `how="left"` |
| 파생 열 | `df["new"] = ...` |

> pandas 사고법: **"표를 만들고 → 거르고(필터) → 묶고(groupby) → 합치고(merge) → 새 열 추가."** SQL과 같은 흐름, 다른 문법.

---

## 정리

| 예제/연습 | SQL 대응 |
|-----------|----------|
| 부서별 평균 (merge+groupby) | `JOIN` + `GROUP BY` + `ORDER BY` |
| 영업팀 직원 | `WHERE dept_id=2` |
| 부서별 최고 연봉 | `GROUP BY + MAX` |
| 부서명별 인원 | `JOIN + GROUP BY + COUNT` |

> 핵심 한 줄: **pandas DataFrame = 파이썬 안의 SQL 테이블. SELECT→`[]`, WHERE→불리언 인덱싱, GROUP BY→`groupby`, JOIN→`merge`. 메서드 체이닝으로 한 흐름.**