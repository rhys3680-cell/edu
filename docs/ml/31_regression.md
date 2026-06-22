# ML 입문 31 — 회귀 (Regression)

> **대상**: 분류 기초(30)를 마친 단계.
> **목표**: **연속값**(집값·점수·연봉처럼 숫자)을 예측하는 회귀를 익히고, 분류와 다른 **평가 지표(MSE·R²)**를 이해하기.

30의 분류가 "**범주**를 맞히기"(품종 3종 중 하나)였다면, **회귀(regression)**는 "**숫자 값**을 맞히기"입니다 — 공부 시간으로 점수 예측, 평수로 집값 예측처럼. 좋은 소식: **30의 4단계 흐름(분할→fit→predict→평가)이 그대로 반복**됩니다. 바뀌는 건 **모델**과 **평가 지표**뿐이에요.

---

## 0) 분류 vs 회귀 — 무엇이 다른가

| | 분류 (30) | 회귀 (31) |
|--|----------|----------|
| 맞히는 것 | **범주** (품종, 생존여부) | **연속값** (점수, 집값) |
| y의 형태 | 0/1/2 같은 라벨 | 71.2, 5000 같은 숫자 |
| 대표 모델 | KNN, 결정트리 | **LinearRegression** |
| 평가 지표 | 정확도(accuracy) | **MSE, R²** |

> 4단계 흐름은 동일: `train_test_split` → `fit` → `predict` → 평가. "정답이 숫자냐 범주냐"가 분류/회귀를 가릅니다.

---

## 1) 가장 단순한 회귀 — 직선 찾기 (직관)

회귀의 본질은 **데이터에 가장 잘 맞는 직선(또는 곡선)을 찾는 것**입니다. 1개 특성으로 감을 잡습니다.

```python
import numpy as np
from sklearn.linear_model import LinearRegression

# 공부 시간(x) → 점수(y), 대략 선형 관계
X = np.array([[1], [2], [3], [4], [5], [6], [7], [8]])   # 특성은 항상 2차원
y = np.array([30, 42, 50, 65, 70, 82, 91, 100])

model = LinearRegression()
model.fit(X, y)                  # 직선을 학습

model.coef_[0]                   # 기울기 ≈ 9.95  (시간당 점수 증가)
model.intercept_                 # 절편 ≈ 21.46
model.predict([[5]])             # x=5 → ≈ 71.2 점 예측
```

> **`y = 기울기 × x + 절편`** — `fit`이 데이터에 가장 잘 맞는 기울기·절편을 찾아줍니다. 여기선 `점수 ≈ 9.95 × 시간 + 21.46`. "1시간 더 공부하면 약 9.95점 오른다"로 해석됩니다.

> ⚠️ 주의: 특성 `X`는 **항상 2차원**(`[[1],[2],...]`)이어야 합니다. 1차원 `[1,2,3]`을 넣으면 에러. (행=샘플, 열=특성)

---

## 2) 평가 지표 — MSE와 R²

분류의 "정확도"는 회귀에 못 씁니다(숫자를 정확히 맞히긴 어려움). 대신 **"얼마나 빗나갔나"**를 잽니다.

```python
from sklearn.metrics import mean_squared_error, r2_score

pred = model.predict(X)

mean_squared_error(y, pred)   # MSE: 오차(예측-정답)를 제곱해 평균 → 작을수록 좋음
r2_score(y, pred)             # R²: 0~1, 1에 가까울수록 잘 설명 (≈0.99)
```

| 지표 | 의미 | 좋은 값 |
|------|------|---------|
| **MSE** (평균제곱오차) | 오차²의 평균 | **작을수록** 좋음 (0이 완벽) |
| **R²** (결정계수) | 모델이 데이터를 설명하는 정도 | **1에 가까울수록** 좋음 (0=평균만큼, 음수=평균보다 나쁨) |

> MSE는 단위가 "값²"이라 절대값 해석이 어렵고(작을수록 좋다 정도), **R²는 0~1로 정규화돼 직관적**입니다. "R²=0.45면 데이터 변동의 45%를 설명"으로 읽습니다. 둘을 같이 봅니다.

---

## 3) 실전 데이터 — diabetes (다특성 회귀)

내장 당뇨 진행도 데이터(442명, 특성 10개)로 실전 회귀를 봅니다.

```python
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

d = load_diabetes()
X, y = d.data, d.target          # X: 10개 특성(나이·BMI 등), y: 1년 후 진행도

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)
# 회귀는 보통 stratify 안 씀 (연속값이라 클래스 비율 개념이 없음)

model = LinearRegression().fit(X_train, y_train)
pred = model.predict(X_test)

r2_score(y_test, pred)           # ≈ 0.4526
mean_squared_error(y_test, pred) # ≈ 2900.19
```

> R²가 0.45 정도 — 붓꽃 분류(1.0)와 달리 **실전 데이터는 완벽하지 않습니다.** 당뇨 진행도가 이 10개 특성만으로 다 설명되진 않으니까요. "현실 데이터는 R²가 낮은 게 정상"이라는 감각이 중요합니다.

---

## 대표 예제 — 단순 회귀 학습 & 예측

> 공부 시간으로 점수를 예측하는 선형 회귀를 만들고, 기울기·절편·R²를 구하라.

```python
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

X = np.array([[1], [2], [3], [4], [5], [6], [7], [8]])
y = np.array([30, 42, 50, 65, 70, 82, 91, 100])

model = LinearRegression().fit(X, y)

print(f"기울기: {model.coef_[0]:.2f}")        # 9.95
print(f"절편:   {model.intercept_:.2f}")       # 21.46
print(f"R²:     {model.score(X, y):.4f}")      # 0.9949
print(f"x=5 예측: {model.predict([[5]])[0]:.2f}")  # 71.23
```

> 가르칠 포인트: **`model.score(X, y)`는 회귀에선 R²를 돌려줍니다** (분류에선 정확도). 같은 `.score()` 메서드인데 모델 종류에 따라 적절한 지표가 나오는 게 scikit-learn의 일관성. 그리고 **기울기·절편으로 모델을 "해석"** 할 수 있는 게 선형 회귀의 큰 장점(왜 그렇게 예측했는지 설명 가능).

---

## 검증 (노트북에서 실행)

```python
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

# 단순 회귀
X = np.array([[1],[2],[3],[4],[5],[6],[7],[8]])
y = np.array([30,42,50,65,70,82,91,100])
m = LinearRegression().fit(X, y)
assert abs(m.coef_[0] - 9.95) < 0.1
assert abs(m.predict([[5]])[0] - 71.23) < 0.1
assert m.score(X, y) > 0.99

# diabetes 다특성 회귀
d = load_diabetes()
Xtr, Xte, ytr, yte = train_test_split(d.data, d.target, test_size=0.2, random_state=42)
lr = LinearRegression().fit(Xtr, ytr)
assert abs(r2_score(yte, lr.predict(Xte)) - 0.4526) < 0.001
print("통과 ✅")
```

---

## 직접 풀어보기 (연습)

`TODO`를 채운 뒤 검증 셀을 실행하세요. **30의 4단계**가 그대로 반복됩니다.

### 연습 1 — 기울기와 절편

> 주어진 데이터로 선형 회귀를 학습하고, (기울기, 절편)을 소수 2자리로 반올림해 튜플로 반환하라.
> **힌트**: `model.coef_[0]`, `model.intercept_`.

```python
import numpy as np
from sklearn.linear_model import LinearRegression

def solution(X, y):
    model = LinearRegression().fit(X, y)
    # TODO: (round(기울기,2), round(절편,2)) 반환
    pass

X = np.array([[1], [2], [3], [4], [5]])
y = np.array([3, 5, 7, 9, 11])          # y = 2x + 1 (완벽한 직선)
assert solution(X, y) == (2.0, 1.0)
print("통과 ✅")
```

### 연습 2 — 예측값 구하기

> 학습한 모델로 `x=10`일 때의 예측값을 소수 2자리로 반환하라.

```python
def solution(X, y, x_new):
    model = LinearRegression().fit(X, y)
    # TODO: x_new에 대한 예측 → round(.., 2)
    pass

X = np.array([[1], [2], [3], [4], [5]])
y = np.array([3, 5, 7, 9, 11])          # y = 2x + 1
assert solution(X, y, 10) == 21.0       # 2*10+1
print("통과 ✅")
```

### 연습 3 — diabetes R² (도전)

> diabetes 데이터를 `random_state=42, test_size=0.2`로 분할해 선형 회귀를 학습하고, test R²를 소수 4자리로 반환하라.

```python
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

def solution():
    d = load_diabetes()
    # TODO: 분할 → 학습 → test R² 반환 (round 4자리)
    pass

assert solution() == 0.4526
print("통과 ✅")
```

---

## 치트시트

| 하고 싶은 것 | 코드 |
|-------------|------|
| 회귀 모델 | `LinearRegression()` |
| 학습 | `model.fit(X, y)` |
| 예측 | `model.predict(X_new)` |
| 기울기 / 절편 | `model.coef_` / `model.intercept_` |
| R² | `model.score(X, y)` 또는 `r2_score(y, pred)` |
| MSE | `mean_squared_error(y, pred)` |

> 분류 vs 회귀 한 줄: **범주를 맞히면 분류(accuracy), 숫자를 맞히면 회귀(MSE·R²). 4단계 흐름과 fit/predict는 똑같다.**

---

## 정리

| 예제/연습 | 핵심 |
|-----------|------|
| 공부시간→점수 | 직선 찾기, 기울기·절편 해석 |
| 기울기/절편 | `coef_` / `intercept_` |
| 예측값 | `predict` |
| diabetes R² | 다특성 회귀, 실전 R²=0.45 |

> 핵심 한 줄: **회귀 = 연속값 예측. `LinearRegression`으로 직선을 찾고, MSE(작을수록)·R²(1에 가까울수록)로 평가. 분류와 흐름은 동일.**