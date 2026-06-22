# ML 입문 30 — 분류 기초 (Classification)

> **대상**: 데이터 핸들링(numpy/pandas/시각화)을 마친 단계. 머신러닝의 첫걸음.
> **목표**: ML의 **전체 흐름**(데이터 → 분할 → 학습 → 예측 → 평가)을 분류 문제로 처음부터 끝까지 경험하기.

머신러닝은 "데이터로부터 **규칙을 스스로 학습**해 새 데이터를 예측"하는 것입니다. **분류(classification)**는 그중 "어떤 **범주**에 속하는지 맞히는" 문제예요 — 스팸/정상, 생존/사망, 붓꽃 품종 등. scikit-learn으로 그 전체 과정을 한 번 돌려봅니다.

---

## 0) ML의 4단계 흐름 (가장 중요)

scikit-learn의 모든 지도학습은 **똑같은 4단계**를 따릅니다. 이 패턴만 익히면 모델이 뭐든 똑같이 씁니다.

```
1. 데이터 준비   X(특성, feature)와 y(정답, label)로 나눔
2. 학습/평가 분할  train_test_split — 배운 데이터로 평가하면 반칙(과적합 못 잡음)
3. 학습          model.fit(X_train, y_train)   ← 규칙을 배움
4. 예측 & 평가    model.predict(X_test) → 정확도 측정
```

> 핵심 원칙: **"배운 문제로 시험 보면 안 된다."** 그래서 데이터를 train(학습용)/test(시험용)로 나눕니다. test는 모델이 한 번도 못 본 데이터여야 진짜 실력이 측정됩니다.

---

## 1) 데이터 준비 — 붓꽃(iris)

scikit-learn에 내장된 붓꽃 데이터를 씁니다. 꽃잎/꽃받침 크기로 **품종 3종**을 맞히는 분류 문제.

```python
from sklearn.datasets import load_iris

iris = load_iris()
X = iris.data        # 특성 4개: 꽃받침 길이/너비, 꽃잎 길이/너비
y = iris.target      # 정답: 0/1/2 (품종 3종)

X.shape              # (150, 4)  — 150송이 × 특성 4개
iris.target_names    # ['setosa' 'versicolor' 'virginica']
iris.feature_names   # ['sepal length (cm)', ...]
```

> 용어: **X = 특성(feature)**, 예측에 쓰는 입력. **y = 레이블(label)**, 맞혀야 할 정답. ML은 "X로 y를 맞히는 규칙"을 배웁니다. (행=샘플, 열=특성 — pandas DataFrame과 같은 구조)

---

## 2) 학습/평가 분할 — train_test_split

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,        # 20%를 시험용으로
    random_state=42,      # 재현성 — 같은 분할이 나오게 고정
    stratify=y            # 클래스 비율을 train/test에 똑같이 유지
)

X_train.shape[0], X_test.shape[0]    # (120, 30)
```

> 세 옵션의 의미:
>
> - **`test_size=0.2`** — 120개 학습 / 30개 시험.
> - **`random_state=42`** — 안 정하면 매번 다르게 쪼개져 결과가 바뀜. 고정하면 누구나 같은 결과(재현성). 숫자는 아무거나, 관례로 42를 자주 씀.
> - **`stratify=y`** — 세 품종이 train/test에 고르게 들어가게. 분류에선 거의 항상 권장.

---

## 3) 학습 — model.fit

분류 모델 하나를 골라 학습시킵니다. 첫 모델로 **KNN**(K-최근접 이웃)을 씁니다 — "가까운 이웃 k개가 무슨 품종인지 보고 다수결로 정함".

```python
from sklearn.neighbors import KNeighborsClassifier

model = KNeighborsClassifier(n_neighbors=3)   # 가장 가까운 3개 이웃을 봄
model.fit(X_train, y_train)                    # 학습 — 이 한 줄이 "배우기"
```

> `fit(X_train, y_train)`이 **학습**입니다. 모델이 "이런 특성이면 이런 품종"이라는 규칙을 데이터에서 뽑아냅니다. scikit-learn의 모든 모델이 `.fit()`으로 학습 — 일관된 인터페이스.

---

## 4) 예측 & 평가 — predict / accuracy

```python
from sklearn.metrics import accuracy_score

pred = model.predict(X_test)                   # 시험용 데이터로 예측
accuracy = accuracy_score(y_test, pred)        # 정답과 비교 → 정확도
print(f"정확도: {accuracy:.4f}")               # 1.0 (30개 다 맞힘)

# 새로운 꽃 한 송이 예측
sample = [[5.1, 3.5, 1.4, 0.2]]
print(iris.target_names[model.predict(sample)[0]])   # 'setosa'
```

> **정확도(accuracy)** = 맞힌 개수 / 전체. 1.0이면 100%. 붓꽃은 쉬운 데이터라 KNN이 30개를 다 맞힙니다. (실전 데이터는 보통 이렇게 높지 않음)

---

## 대표 예제 — 전체 흐름 한 번에

> 붓꽃 데이터로 KNN 분류기를 학습하고 test 정확도를 구하라. (4단계 전부)

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# 1. 데이터
iris = load_iris()
X, y = iris.data, iris.target

# 2. 분할
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

# 3. 학습
model = KNeighborsClassifier(n_neighbors=3)
model.fit(X_train, y_train)

# 4. 예측 & 평가
acc = accuracy_score(y_test, model.predict(X_test))
print(f"정확도: {acc:.4f}")   # 1.0000
```

> 가르칠 포인트: **이 4단계가 모든 지도학습의 뼈대**입니다. 데이터가 타이타닉이든 주가든, 모델이 KNN이든 랜덤포레스트든 구조는 똑같아요. `fit`(학습) → `predict`(예측) → 점수. 31(회귀)·다음 프로젝트들이 전부 이 패턴의 반복입니다.

---

## 검증 (노트북에서 실행)

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

iris = load_iris()
X, y = iris.data, iris.target
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

# KNN
knn = KNeighborsClassifier(n_neighbors=3).fit(X_train, y_train)
assert accuracy_score(y_test, knn.predict(X_test)) == 1.0

# 결정트리 (같은 분할로) — random_state 고정 시 0.9333
dt = DecisionTreeClassifier(random_state=42).fit(X_train, y_train)
acc_dt = accuracy_score(y_test, dt.predict(X_test))
assert abs(acc_dt - 0.9333) < 0.001

# 새 샘플은 setosa(0)
assert knn.predict([[5.1, 3.5, 1.4, 0.2]])[0] == 0
print("통과 ✅")
```

---

## 직접 풀어보기 (연습)

`TODO`를 채운 뒤 검증 셀을 실행하세요. **"4단계 흐름"**을 그대로 따라가면 됩니다.

### 연습 1 — 결정트리로 분류

> 붓꽃을 `DecisionTreeClassifier`로 학습하고 test 정확도를 반환하라. (`random_state=42`로 분할·모델 둘 다 고정)
> **힌트**: KNN 자리에 `DecisionTreeClassifier(random_state=42)`만 바꾸면 됨.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

def solution():
    iris = load_iris()
    X, y = iris.data, iris.target
    # TODO: 분할(random_state=42, stratify=y) → 학습 → 정확도 반환
    pass

assert abs(solution() - 0.9333) < 0.001
print("통과 ✅")
```

### 연습 2 — 이웃 수(k) 바꿔보기

> KNN의 `n_neighbors`를 5로 바꿔 학습하고 test 정확도를 반환하라.
> **힌트**: `KNeighborsClassifier(n_neighbors=5)`.

```python
def solution():
    iris = load_iris()
    X, y = iris.data, iris.target
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    # TODO: k=5로 학습 → 정확도 반환
    pass

assert solution() == 1.0     # iris는 k=5도 30개 다 맞힘
print("통과 ✅")
```

### 연습 3 — 예측 결과 세어보기 (도전)

> KNN(k=3)으로 test를 예측한 뒤, 세 품종이 각각 몇 개로 예측됐는지 리스트로 반환하라. (`[setosa수, versicolor수, virginica수]`)
> **힌트**: `np.bincount(예측결과)`. stratify로 분할했으니 각 10개씩일 것.

```python
import numpy as np

def solution():
    iris = load_iris()
    X, y = iris.data, iris.target
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    knn = KNeighborsClassifier(n_neighbors=3).fit(X_tr, y_tr)
    pred = knn.predict(X_te)
    # TODO: np.bincount(pred).tolist()
    pass

assert solution() == [10, 10, 10]
print("통과 ✅")
```

---

## 치트시트

| 단계        | 코드                                                                |
| ----------- | ------------------------------------------------------------------- |
| 데이터 로드 | `load_iris()`, `.data` / `.target`                                  |
| 분할        | `train_test_split(X, y, test_size=.2, random_state=42, stratify=y)` |
| 모델 생성   | `KNeighborsClassifier(n_neighbors=3)`                               |
| 학습        | `model.fit(X_train, y_train)`                                       |
| 예측        | `model.predict(X_test)`                                             |
| 정확도      | `accuracy_score(y_test, pred)`                                      |
| 새 샘플     | `model.predict([[...]])`                                            |

> ML 사고법 한 줄: **모든 지도학습 = `fit`(학습) → `predict`(예측) → 점수. 단, 반드시 train/test를 나눠서.**

---

## 정리

| 예제/연습 | 핵심                                  |
| --------- | ------------------------------------- |
| 붓꽃 KNN  | 4단계 흐름, 정확도 1.0                |
| 결정트리  | 모델만 교체(0.9333) — 인터페이스 동일 |
| k=5       | 하이퍼파라미터 바꿔보기               |
| 예측 분포 | `np.bincount`로 결과 분석             |

> 핵심 한 줄: **분류 = X로 범주 y를 맞히기. 데이터→분할→fit→predict→accuracy. 이 4단계가 ML 전체의 뼈대다.**
