# ML 입문 33 — 모델 평가 / 교차검증 (Evaluation & Cross-Validation)

> **대상**: 분류(30)·회귀(31)·전처리(32)를 마친 단계. ML 입문의 **마지막**.
> **목표**: "정확도만으로는 부족하다"를 이해하고, **혼동행렬 / 정밀도·재현율 / 교차검증**으로 모델을 제대로 평가하기.

지금까지 모델을 "정확도(accuracy)"로만 봤습니다. 하지만 정확도는 **속을 수 있는 지표**예요 — 특히 데이터가 한쪽으로 치우치면(불균형). 이 단계에서 "진짜 좋은 모델인지" 제대로 재는 법을 배웁니다. 곧 만날 타이타닉·이상거래 탐지에서 바로 쓰입니다.

---

## 0) 정확도의 함정 — 불균형 데이터

암 환자 5%, 정상 95%인 데이터를 생각해 봅시다. **"무조건 정상이라고 찍는" 멍청한 모델**의 정확도는?

```python
import numpy as np
from sklearn.metrics import accuracy_score, recall_score

y_true = np.array([0]*95 + [1]*5)    # 정상 95명, 환자 5명
y_dumb = np.array([0]*100)            # 전부 "정상"이라고 찍음

accuracy_score(y_true, y_dumb)        # 0.95  ← 정확도 95%?!
recall_score(y_true, y_dumb)          # 0.0   ← 환자는 한 명도 못 잡음
```

> **정확도 95%인데 환자를 0명 잡는** 쓸모없는 모델입니다. 정확도만 보면 "와 95%!"라고 속아요. 불균형 데이터(사기 탐지, 질병 진단)에선 **정확도 대신 다른 지표**가 필요합니다.

---

## 1) 혼동행렬 (Confusion Matrix) — 어디서 틀렸나

먼저 1·2번에서 함께 쓸 **데이터·모델을 준비**합니다. 유방암 데이터에 (스케일+로지스틱) 파이프라인(32)을 학습해 `y_test`와 `pred`를 만들어 둡니다.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

bc = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(
    bc.data, bc.target, test_size=0.3, random_state=42, stratify=bc.target)

pipe = Pipeline([("sc", StandardScaler()),
                 ("clf", LogisticRegression(max_iter=5000))]).fit(X_train, y_train)
pred = pipe.predict(X_test)     # ← 아래 1·2번이 이 y_test / pred 를 사용
```

이제 예측을 **정답×예측의 표**로 펼칩니다. "무엇을 무엇으로 틀렸는지" 한눈에.

```python
from sklearn.metrics import confusion_matrix

confusion_matrix(y_test, pred)
# [[63  1]      실제 음성(0): 63개 맞음(TN), 1개를 양성으로 틀림(FP)
#  [ 1 106]]    실제 양성(1):  1개를 음성으로 틀림(FN), 106개 맞음(TP)
```

|  | 예측 음성 | 예측 양성 |
|--|----------|----------|
| **실제 음성** | TN (참음성) | FP (거짓양성) |
| **실제 양성** | FN (거짓음성) | TP (참양성) |

> 4칸의 의미:
> - **TP** (True Positive): 양성을 양성으로 — 맞음
> - **TN** (True Negative): 음성을 음성으로 — 맞음
> - **FP** (False Positive): 음성인데 양성이라 함 — **오경보**
> - **FN** (False Negative): 양성인데 음성이라 함 — **놓침** (암을 정상이라 하는 위험한 실수)

---

## 2) 정밀도 & 재현율 — 정확도가 못 보는 것

혼동행렬에서 두 핵심 지표가 나옵니다.

```python
from sklearn.metrics import precision_score, recall_score, f1_score

precision_score(y_test, pred)   # 정밀도: 양성이라 한 것 중 진짜 양성 비율
recall_score(y_test, pred)      # 재현율: 진짜 양성 중 잡아낸 비율
f1_score(y_test, pred)          # F1: 정밀도·재현율의 조화평균
```

| 지표 | 정의 | "이걸 신경 쓸 때" |
|------|------|------------------|
| **정밀도** (Precision) | TP / (TP+FP) | 오경보(FP)를 줄이고 싶을 때 (스팸함에 정상메일 가면 안 됨) |
| **재현율** (Recall) | TP / (TP+FN) | 놓침(FN)을 줄이고 싶을 때 (암을 놓치면 안 됨) |
| **F1** | 둘의 조화평균 | 둘 다 균형있게 보고 싶을 때 |

> 위 불균형 예시: "전부 정상"이라 찍으면 환자(양성)를 다 놓쳐 **재현율 0**. 정확도는 못 잡은 이 문제를 재현율은 잡아냅니다. **불균형 데이터에선 재현율·F1을 봐야** 하는 이유.

> 정밀도 vs 재현율은 **트레이드오프**가 있습니다. 둘을 한 번에 보려면 `classification_report(y_test, pred)`가 편합니다.

---

## 3) 교차검증 (Cross-Validation) — 한 번의 분할은 운빨

`train_test_split`은 **한 번만** 쪼갭니다. 그 한 번이 운 좋게(나쁘게) 쪼개졌을 수 있어요. **교차검증**은 데이터를 여러 조각(fold)으로 나눠 **돌아가며 평가**해 평균을 냅니다.

```python
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import load_iris

iris = load_iris()
pipe = Pipeline([("sc", StandardScaler()), ("knn", KNeighborsClassifier())])

scores = cross_val_score(pipe, iris.data, iris.target, cv=5)   # 5조각으로 5번 평가
scores              # [0.967 0.967 0.933 0.933 1.0]
scores.mean()       # 0.96   ← 평균 성능 (더 믿을 만함)
scores.std()        # 0.025  ← 편차 (작을수록 안정적)
```

> **5-fold**: 데이터를 5등분 → 4조각으로 학습, 1조각으로 평가 → 평가 조각을 바꿔가며 5번 → 점수 5개. **평균**이 "진짜 실력"에 가깝고, **표준편차**가 작으면 "어떻게 쪼개도 일관적"이라는 뜻.

> 핵심: **`Pipeline`을 통째로 넣는 것**(32와 연결)이 중요합니다. 그래야 각 fold마다 train으로만 스케일러를 fit해 **누수가 안 생깁니다**. 전처리를 따로 하면 교차검증에서 누수가 새요.

---

## 대표 예제 — 유방암 데이터 전체 평가

> 유방암 데이터로 (스케일+로지스틱) 파이프라인을 학습하고, 정확도·혼동행렬·정밀도·재현율·F1을 모두 구하라.

(1번에서 준비한 것과 같은 데이터·모델입니다. 여기선 한 셀에 모아 "전체 평가"를 한 번에 봅니다.)

```python
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix,
                             precision_score, recall_score, f1_score)

bc = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(
    bc.data, bc.target, test_size=0.3, random_state=42, stratify=bc.target)

pipe = Pipeline([("sc", StandardScaler()),
                 ("clf", LogisticRegression(max_iter=5000))]).fit(X_train, y_train)
pred = pipe.predict(X_test)

print(f"정확도: {accuracy_score(y_test, pred):.4f}")   # 0.9883
print("혼동행렬:\n", confusion_matrix(y_test, pred))    # [[63 1] [1 106]]
print(f"정밀도: {precision_score(y_test, pred):.4f}")   # 0.9907
print(f"재현율: {recall_score(y_test, pred):.4f}")      # 0.9907
print(f"F1:     {f1_score(y_test, pred):.4f}")          # 0.9907
```

> 가르칠 포인트: 이 데이터는 모델이 좋아서 모든 지표가 높습니다(0.99). 하지만 **혼동행렬을 보면 FN=1**(암 1명을 정상이라 함) — 의료에선 이 1명이 중요하죠. "정확도 한 숫자"가 아니라 **혼동행렬로 어떤 실수를 했는지**까지 보는 게 제대로 된 평가입니다.

---

## 검증 (노트북에서 실행)

```python
import numpy as np
from sklearn.datasets import load_breast_cancer, load_iris
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, recall_score, f1_score

# 불균형 함정: 전부 0으로 찍으면 정확도 0.95지만 재현율 0
y_true = np.array([0]*95 + [1]*5)
y_dumb = np.array([0]*100)
assert accuracy_score(y_true, y_dumb) == 0.95
assert recall_score(y_true, y_dumb, zero_division=0) == 0.0

# 유방암 파이프라인 평가
bc = load_breast_cancer()
Xtr, Xte, ytr, yte = train_test_split(
    bc.data, bc.target, test_size=0.3, random_state=42, stratify=bc.target)
pipe = Pipeline([("sc", StandardScaler()),
                 ("clf", LogisticRegression(max_iter=5000))]).fit(Xtr, ytr)
pred = pipe.predict(Xte)
assert abs(f1_score(yte, pred) - 0.9907) < 0.001

# 교차검증
iris = load_iris()
cvpipe = Pipeline([("sc", StandardScaler()), ("knn", KNeighborsClassifier())])
scores = cross_val_score(cvpipe, iris.data, iris.target, cv=5)
assert abs(scores.mean() - 0.96) < 0.001
print("통과 ✅")
```

---

## 직접 풀어보기 (연습)

`TODO`를 채운 뒤 검증 셀을 실행하세요.

### 연습 1 — 재현율 직접 계산

> 혼동행렬 값(TP, FN)으로 재현율을 계산해 반환하라. (재현율 = TP / (TP+FN))
> **힌트**: 공식 그대로. 분모 0은 신경 안 써도 됨.

```python
def solution(tp, fn):
    # TODO: TP / (TP + FN)
    pass

assert solution(106, 1) == 106 / 107
assert solution(8, 2) == 0.8
print("통과 ✅")
```

### 연습 2 — 불균형에서 정확도 vs 재현율

> "전부 다수 클래스(0)로 찍는" 모델의 (정확도, 재현율)을 튜플로 반환하라. y는 0이 `n0`개, 1이 `n1`개.
> **힌트**: 정확도 = n0/(n0+n1), 재현율 = 0 (양성을 하나도 못 맞힘).

```python
def solution(n0, n1):
    # TODO: (정확도, 재현율) — round 4자리
    pass

assert solution(95, 5) == (0.95, 0.0)
assert solution(90, 10) == (0.9, 0.0)
print("통과 ✅")
```

### 연습 3 — 교차검증 평균 (도전)

> iris 데이터로 (스케일+KNN) 파이프라인을 5-fold 교차검증하고, 평균 점수를 round 2자리로 반환하라.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

def solution():
    iris = load_iris()
    # TODO: Pipeline → cross_val_score(cv=5) → 평균 round 2자리
    pass

assert solution() == 0.96
print("통과 ✅")
```

---

## 치트시트

| 하고 싶은 것 | 코드 |
|-------------|------|
| 혼동행렬 | `confusion_matrix(y_test, pred)` |
| 정밀도 / 재현율 | `precision_score` / `recall_score` |
| F1 | `f1_score(y_test, pred)` |
| 한 번에 보기 | `classification_report(y_test, pred)` |
| 교차검증 | `cross_val_score(pipe, X, y, cv=5)` |
| 평균 / 편차 | `scores.mean()` / `scores.std()` |

> 평가 핵심 한 줄: **정확도 하나만 믿지 마라. 불균형이면 재현율·F1, 어떤 실수인지는 혼동행렬, 운빨 제거는 교차검증.**

---

## 정리

| 예제/연습 | 핵심 |
|-----------|------|
| 불균형 함정 | 정확도 95%인데 재현율 0 |
| 혼동행렬 | TP/TN/FP/FN으로 실수 분석 |
| 정밀도·재현율·F1 | 정확도가 못 보는 것 |
| 교차검증 | 여러 분할 평균으로 안정적 평가 |

> 핵심 한 줄: **좋은 평가 = (정확도 너머) 혼동행렬로 실수를 보고, 정밀도·재현율·F1로 불균형을 잡고, 교차검증으로 한 번의 운을 제거.**

---

## 🎉 ML 입문 완료 (30~33)

| # | 주제 | 핵심 |
|---|------|------|
| 30 | 분류 기초 | 4단계 흐름, fit/predict |
| 31 | 회귀 | 연속값, MSE/R² |
| 32 | 전처리/파이프라인 | 스케일링·인코딩, Pipeline |
| 33 | 평가/교차검증 | 혼동행렬, 재현율, CV |

> 이제 **5단계 첫 프로젝트 — Kaggle 타이타닉**으로 갑니다. 지금까지 배운 pandas 전처리 + Pipeline + 분류 + 평가가 **하나의 실전 프로젝트로 합쳐집니다.**