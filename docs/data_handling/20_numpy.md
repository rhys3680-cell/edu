# 데이터 핸들링 20 — numpy

> **대상**: 코딩테스트·SQL 단계를 마친 단계. 데이터 분석/ML의 첫 도구.
> **목표**: "리스트 반복" 대신 **배열 전체를 한 번에 계산**하는 numpy 사고법 — 벡터 연산 / 브로드캐스팅 / 불리언 인덱싱 — 익히기.

numpy는 pandas·scikit-learn·머신러닝 전체의 **밑바탕**입니다. 핵심은 단 하나: **"`for`로 하나씩 돌지 말고, 배열 전체에 연산을 한 번에 건다."** 이게 빠르고(C로 구현됨), 코드도 짧아집니다.

---

## 0) 왜 numpy인가 — 리스트 vs 배열

파이썬 리스트로 "모든 원소에 2를 곱하기"는 반복이 필요합니다:

```python
nums = [1, 2, 3, 4, 5]
doubled = [x * 2 for x in nums]   # 반복으로 하나씩
```

numpy는 **배열 전체에 한 번에** 적용합니다:

```python
import numpy as np

a = np.array([1, 2, 3, 4, 5])
doubled = a * 2          # [2 4 6 8 10] — 반복 없이!
```

> 이게 **벡터 연산(vectorization)**입니다. 코딩테스트에서 `for`로 돌던 걸, 데이터 분석에선 배열 연산 한 줄로 바꿉니다. 수백만 원소도 한 줄로, 그리고 훨씬 빠르게.

---

## 1) 배열 만들기 & 기본 속성

```python
import numpy as np

a = np.array([1, 2, 3, 4, 5])
a.dtype      # dtype('int64')  — 원소 타입 (리스트와 달리 한 종류로 통일)
a.shape      # (5,)            — 형태 (1차원, 5개)
len(a)       # 5

# 자주 쓰는 생성 함수
np.arange(0, 10, 2)    # [0 2 4 6 8]  (start, stop, step)
np.zeros(3)            # [0. 0. 0.]
np.ones(3)             # [1. 1. 1.]
np.linspace(0, 1, 5)   # [0. 0.25 0.5 0.75 1.]  (0~1을 5등분)
```

> `dtype`이 핵심: numpy 배열은 **모든 원소가 같은 타입**이라 빠릅니다. 정수만 있으면 `int64`, 소수가 섞이면 `float64`.

---

## 2) 벡터 연산 — 배열끼리, 배열과 숫자

```python
a = np.array([1, 2, 3, 4, 5])

a + 10        # [11 12 13 14 15]  — 모든 원소에 +10
a * 2         # [ 2  4  6  8 10]
a ** 2        # [ 1  4  9 16 25]

b = np.array([10, 20, 30, 40, 50])
a + b         # [11 22 33 44 55]  — 같은 위치끼리
a * b         # [10 40 90 160 250]
```

> 리스트로는 `[x+y for x,y in zip(a,b)]`였던 게, numpy로는 그냥 `a + b`. "같은 위치끼리 자동으로" 계산됩니다.

---

## 3) 집계 — sum / mean / max ...

```python
a = np.array([1, 2, 3, 4, 5])

a.sum()       # 15
a.mean()      # 3.0
a.max(), a.min()   # (5, 1)
a.std()       # 표준편차

# 통계 한 방에
scores = np.array([90, 80, 70, 60, 100])
scores.mean()      # 80.0
scores.std()       # 14.142...
```

> SQL의 `SUM`/`AVG`/`MAX`와 같은 개념 — 단, 여기선 배열 메서드로. 데이터 분석에서 "평균·표준편차"는 매일 씁니다.

---

## 4) 불리언 인덱싱 — 조건으로 고르기 (핵심)

조건을 배열에 걸면 **True/False 배열**이 나오고, 그걸로 원소를 고릅니다.

```python
a = np.array([1, 2, 3, 4, 5])

a > 2          # [False False  True  True  True]
a[a > 2]       # [3 4 5]  — True인 것만 추출!

# 조건 만족 개수 / 합
(a > 2).sum()  # 3   (True=1로 세짐)
a[a % 2 == 0]  # [2 4]  (짝수만)
```

> 이게 numpy의 가장 강력한 패턴입니다. SQL의 `WHERE`, pandas의 필터링이 모두 이 불리언 인덱싱 위에 있습니다. "조건 → True/False 배열 → 추출".

---

## 5) 2차원 배열 & axis

```python
m = np.array([[1, 2, 3],
              [4, 5, 6]])
m.shape        # (2, 3)  — 2행 3열

m.sum()        # 21  (전체)
m.sum(axis=0)  # [5 7 9]   — 열 방향(↓): 각 열의 합
m.sum(axis=1)  # [6 15]    — 행 방향(→): 각 행의 합

np.arange(6).reshape(2, 3)   # [[0 1 2] [3 4 5]]  — 형태 바꾸기
```

> `axis` 헷갈림 방지: **`axis=0`은 행을 따라 아래로 합쳐 "열별 결과"**, **`axis=1`은 열을 따라 옆으로 합쳐 "행별 결과"**. pandas의 `groupby` 집계에서도 이 개념이 이어집니다.

---

## 6) 브로드캐스팅 — 형태가 달라도 자동 확장

```python
m = np.array([[1, 2, 3],
              [4, 5, 6]])
v = np.array([10, 20, 30])

m + v    # [[11 22 33]
         #  [14 25 36]]  — v가 각 행에 자동으로 더해짐
```

> 작은 배열(`v`)이 큰 배열(`m`)의 형태에 맞춰 **자동으로 늘어나** 계산됩니다. "각 열에 다른 가중치 더하기" 같은 게 반복 없이 한 줄. 처음엔 낯설지만 ML에서 자주 만납니다.

---

## 대표 예제 — 점수 정규화 (표준화)

> 점수 배열을 **평균 0, 표준편차 1로 표준화**하라. (ML 전처리의 기본 — `(x - 평균) / 표준편차`)

```python
import numpy as np

scores = np.array([90, 80, 70, 60, 100])
normalized = (scores - scores.mean()) / scores.std()
print(normalized)
# [ 0.707  0.    -0.707 -1.414  1.414]
```

**기대 결과:**

```
[ 0.70710678  0.         -0.70710678 -1.41421356  1.41421356]
```

> 가르칠 포인트: **벡터 연산의 힘** — `scores - scores.mean()`이 "모든 점수에서 평균을 뺀다"를 반복 없이 한 번에. 이어서 `/ scores.std()`까지. 이 한 줄이 scikit-learn의 `StandardScaler`가 내부에서 하는 일입니다. (4단계 ML에서 다시 만남)

---

## 검증 (노트북에서 실행)

```python
import numpy as np

a = np.array([1, 2, 3, 4, 5])
assert (a * 2).tolist() == [2, 4, 6, 8, 10]
assert a[a > 2].tolist() == [3, 4, 5]
assert a.sum() == 15 and a.mean() == 3.0

m = np.array([[1, 2, 3], [4, 5, 6]])
assert m.sum(axis=0).tolist() == [5, 7, 9]
assert m.sum(axis=1).tolist() == [6, 15]

# 표준화: 평균≈0, 표준편차≈1
scores = np.array([90, 80, 70, 60, 100])
z = (scores - scores.mean()) / scores.std()
assert abs(z.mean()) < 1e-9
assert abs(z.std() - 1.0) < 1e-9
print("통과 ✅")
```

---

## 직접 풀어보기 (연습)

`np`를 써서 `TODO`를 채운 뒤 검증 셀을 실행하세요. **"반복 대신 배열 연산"**으로 생각하는 게 핵심입니다.

### 연습 1 — 합격자 수 세기 (불리언 인덱싱)

> 점수 배열에서 60점 이상인 원소의 개수를 구하라. (`for` 없이)
> **힌트**: `(scores >= 60).sum()`.

```python
import numpy as np

def solution(scores):
    scores = np.array(scores)
    # TODO: 60 이상 개수
    pass

assert solution([90, 50, 60, 30, 100, 59]) == 3   # 90, 60, 100
assert solution([10, 20, 30]) == 0
print("통과 ✅")
```

### 연습 2 — 평균보다 높은 원소만 (불리언 인덱싱)

> 배열에서 평균보다 큰 원소만 골라 리스트로 반환하라.
> **힌트**: `a[a > a.mean()]`.

```python
import numpy as np

def solution(nums):
    a = np.array(nums)
    # TODO: 평균 초과 원소만 → .tolist()
    pass

assert solution([1, 2, 3, 4, 5]) == [4, 5]       # 평균 3
assert solution([10, 10, 10]) == []              # 평균과 같음 → 없음
print("통과 ✅")
```

### 연습 3 — 행별 합계 (2D, axis)

> 2차원 배열에서 각 행의 합을 리스트로 반환하라.
> **힌트**: `m.sum(axis=1)`.

```python
import numpy as np

def solution(matrix):
    m = np.array(matrix)
    # TODO: 행별 합 → .tolist()
    pass

assert solution([[1, 2, 3], [4, 5, 6]]) == [6, 15]
assert solution([[10, 20], [30, 40], [50, 60]]) == [30, 70, 110]
print("통과 ✅")
```

---

## 치트시트

| 하고 싶은 것 | numpy |
|-------------|-------|
| 배열 만들기 | `np.array([...])`, `np.arange`, `np.zeros` |
| 모든 원소에 연산 | `a * 2`, `a + 10` (벡터 연산) |
| 배열끼리 | `a + b`, `a * b` (같은 위치끼리) |
| 집계 | `a.sum()`, `a.mean()`, `a.std()`, `a.max()` |
| 조건으로 고르기 | `a[a > 2]` (불리언 인덱싱) |
| 조건 개수 | `(a > 2).sum()` |
| 2D 열별/행별 | `m.sum(axis=0)` / `m.sum(axis=1)` |
| 형태 바꾸기 | `m.reshape(2, 3)` |

> numpy 사고법 한 줄: **"`for`로 하나씩 돌고 싶으면, 배열 연산으로 바꿀 수 있는지 먼저 생각하라."**

---

## 정리

| 예제/연습 | 핵심 |
|-----------|------|
| 점수 표준화 | 벡터 연산 `(x - mean) / std` |
| 합격자 수 | 불리언 `(scores >= 60).sum()` |
| 평균 초과 | 불리언 인덱싱 `a[a > a.mean()]` |
| 행별 합 | `m.sum(axis=1)` |

> 핵심 한 줄: **numpy = 배열 전체에 한 번에 연산(벡터화) + 조건으로 고르기(불리언 인덱싱) + 축으로 집계(axis). pandas·ML의 토대.**