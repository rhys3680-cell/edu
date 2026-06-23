# ML 입문 32 — 전처리 / 파이프라인 (Preprocessing & Pipeline)

> **대상**: 분류(30)·회귀(31)를 마친 단계.
> **목표**: 모델에 넣기 전에 데이터를 다듬는 **전처리**(스케일링·인코딩)와, 전처리+모델을 하나로 묶는 **`Pipeline`**(데이터 누수 방지) 익히기.

지금까지는 붓꽃처럼 **깨끗한** 데이터를 바로 모델에 넣었습니다. 하지만 실전 데이터(곧 만날 타이타닉)는 **스케일이 제각각이고, 글자(범주형)가 섞여 있고, 빈 값**이 있습니다. 모델이 잘 학습하려면 먼저 **전처리**가 필요해요. 20(numpy 표준화)·21(pandas)이 여기서 ML과 합쳐집니다.

---

## 0) 왜 전처리인가 — 스케일이 모델을 망친다

특성마다 **숫자 범위(스케일)가 다르면**, KNN·로지스틱 같은 "거리 기반" 모델이 큰 숫자 특성에 휘둘립니다.

예: wine 데이터는 특성 평균이 **0.36 ~ 746.89**로 천차만별 → 큰 특성이 거리 계산을 지배.

```python
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

w = load_wine()
X_train, X_test, y_train, y_test = train_test_split(
    w.data, w.target, test_size=0.3, random_state=42, stratify=w.target)

# 스케일링 없이
knn = KNeighborsClassifier().fit(X_train, y_train)
accuracy_score(y_test, knn.predict(X_test))    # ≈ 0.72  (낮음!)
```

> 같은 모델인데 스케일링만 하면 **0.72 → 0.94**로 뜁니다(아래). 전처리가 모델 성능을 좌우한다는 가장 직관적인 증거.

---

## 1) 스케일링 — StandardScaler (20의 표준화!)

`StandardScaler`는 각 특성을 **평균 0, 표준편차 1**로 맞춥니다. **20에서 numpy로 손계산했던 `(x - mean) / std`가 바로 이것**입니다.

```python
from sklearn.preprocessing import StandardScaler
import numpy as np

X = np.array([[90], [80], [70], [60], [100]], dtype=float)

scaler = StandardScaler()
scaler.fit(X)              # 평균·표준편차를 "학습"
scaler.mean_              # [80.0]
scaler.scale_             # [14.14...]  (표준편차)

scaler.transform(X)[0]    # [0.7071]  ← (90-80)/14.14, 20에서 본 그 값!
```

> `fit`으로 평균·표준편차를 구하고 `transform`으로 변환. 둘을 한 번에 하는 `fit_transform`도 있습니다. 변환 후엔 모든 특성이 같은 스케일이라 거리 기반 모델이 공정하게 동작합니다.

> ⚠️ **결정적 규칙**: `fit`은 **train 데이터에만** 합니다. test의 평균·표준편차를 쓰면 "시험 정보를 미리 본" 셈(데이터 누수, leakage). 이 실수를 막아주는 게 다음의 `Pipeline`입니다.

---

## 2) 범주형 인코딩 — OneHotEncoder

모델은 숫자만 이해합니다. `'개발'`, `'영업'` 같은 **글자(범주형)는 숫자로 바꿔야** 합니다.

```python
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

df = pd.DataFrame({"dept": ["개발", "영업", "개발", "인사"]})

enc = OneHotEncoder(sparse_output=False)
enc.fit_transform(df[["dept"]])
# [[1 0 0]    개발 → (개발=1, 영업=0, 인사=0)
#  [0 1 0]    영업
#  [1 0 0]    개발
#  [0 0 1]]   인사
enc.categories_[0]    # ['개발' '영업' '인사']
```

> **원-핫 인코딩**: 범주마다 열을 하나씩 만들어 해당하면 1, 아니면 0. "개발/영업/인사"를 3개 열로. (`개발=0, 영업=1, 인사=2`처럼 숫자만 매기면 모델이 "인사 > 영업 > 개발" 같은 크기 관계로 오해할 수 있어, 순서 없는 범주는 원-핫이 안전합니다.)

---

## 3) Pipeline — 전처리 + 모델을 하나로 (핵심)

전처리와 모델을 **하나의 객체로 묶으면**, `fit`/`predict`를 한 번에 하고 **데이터 누수도 자동으로 막힙니다**.

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

pipe = Pipeline([
    ("scaler", StandardScaler()),       # 1단계: 스케일링
    ("knn", KNeighborsClassifier()),    # 2단계: 모델
])

pipe.fit(X_train, y_train)              # 스케일러 fit → 변환 → 모델 fit, 한 번에
pipe.predict(X_test)                    # test도 train 기준으로 변환 후 예측
accuracy_score(y_test, pipe.predict(X_test))   # ≈ 0.94  (0.72에서 상승!)
```

> Pipeline의 핵심 이점 두 가지:
> 1. **누수 방지**: `pipe.fit(X_train, ...)`은 스케일러를 **train으로만** fit하고, `predict` 때 test를 그 기준으로 변환. 직접 `scaler.fit(전체)`하는 실수를 원천 차단.
> 2. **간결함**: 전처리+모델이 **하나의 모델**처럼 동작 → `fit`/`predict`/`score` 그대로. 교차검증(33)·하이퍼파라미터 탐색에도 통째로 들어감.

---

## 대표 예제 — 스케일링 효과 비교

> wine 데이터에서 KNN을 (a) 스케일링 없이 (b) Pipeline으로 스케일링 후, 두 정확도를 비교하라.

```python
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

w = load_wine()
X_train, X_test, y_train, y_test = train_test_split(
    w.data, w.target, test_size=0.3, random_state=42, stratify=w.target)

# (a) 스케일링 없이
raw = KNeighborsClassifier().fit(X_train, y_train)
acc_raw = accuracy_score(y_test, raw.predict(X_test))

# (b) Pipeline으로 스케일링 + KNN
pipe = Pipeline([("sc", StandardScaler()), ("knn", KNeighborsClassifier())])
pipe.fit(X_train, y_train)
acc_pipe = accuracy_score(y_test, pipe.predict(X_test))

print(f"스케일링 없이: {acc_raw:.4f}")    # 0.7222
print(f"스케일링 후:   {acc_pipe:.4f}")    # 0.9444
```

> 가르칠 포인트: **같은 모델·같은 데이터인데 전처리 하나로 0.72 → 0.94.** 전처리는 "있으면 좋은" 게 아니라 **모델 성능의 핵심**입니다. 그리고 그걸 안전하게(누수 없이) 하는 표준 도구가 `Pipeline`. 타이타닉부터 모든 실전에서 이 패턴을 씁니다.

---

## 검증 (노트북에서 실행)

```python
import numpy as np
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# StandardScaler == numpy 표준화
X = np.array([[90],[80],[70],[60],[100]], dtype=float)
sc = StandardScaler().fit(X)
assert abs(sc.mean_[0] - 80.0) < 1e-9
assert abs(sc.transform(X)[0,0] - 0.7071) < 1e-3

# 스케일링 효과 (wine)
w = load_wine()
Xtr, Xte, ytr, yte = train_test_split(
    w.data, w.target, test_size=0.3, random_state=42, stratify=w.target)
raw = KNeighborsClassifier().fit(Xtr, ytr)
pipe = Pipeline([("sc", StandardScaler()), ("knn", KNeighborsClassifier())]).fit(Xtr, ytr)
assert abs(accuracy_score(yte, raw.predict(Xte)) - 0.7222) < 0.001
assert abs(accuracy_score(yte, pipe.predict(Xte)) - 0.9444) < 0.001
print("통과 ✅")
```

---

## 직접 풀어보기 (연습)

`TODO`를 채운 뒤 검증 셀을 실행하세요.

### 연습 1 — StandardScaler 변환값

> 배열을 `StandardScaler`로 변환해, 변환된 값들의 평균과 표준편차를 (round 6자리) 튜플로 반환하라. (표준화하면 평균≈0, 표준편차≈1)
> **힌트**: `fit_transform` 후 `.mean()`, `.std()`.

```python
import numpy as np
from sklearn.preprocessing import StandardScaler

def solution(values):
    X = np.array(values, dtype=float).reshape(-1, 1)
    # TODO: 변환 후 (round(mean,6), round(std,6)) 반환
    pass

assert solution([90, 80, 70, 60, 100]) == (0.0, 1.0)
print("통과 ✅")
```

### 연습 2 — 원-핫 인코딩 열 수

> 범주형 데이터를 원-핫 인코딩했을 때 생기는 열(범주) 개수를 반환하라.
> **힌트**: `OneHotEncoder().fit(...).categories_[0]`의 길이, 또는 변환 결과의 `.shape[1]`.

```python
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

def solution(categories):
    df = pd.DataFrame({"c": categories})
    # TODO: 원-핫 인코딩 후 열 개수 반환
    pass

assert solution(["개발", "영업", "개발", "인사"]) == 3       # 개발/영업/인사
assert solution(["A", "B", "A", "A"]) == 2                  # A/B
print("통과 ✅")
```

### 연습 3 — Pipeline 정확도 (도전)

> wine 데이터를 `random_state=42, test_size=0.3, stratify`로 분할하고, `StandardScaler + KNN` 파이프라인의 test 정확도를 (round 4자리) 반환하라.

```python
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

def solution():
    w = load_wine()
    # TODO: 분할 → Pipeline(스케일+KNN) 학습 → test 정확도
    pass

assert solution() == 0.9444
print("통과 ✅")
```

---

## 치트시트

| 하고 싶은 것 | 코드 |
|-------------|------|
| 표준화 (평균0·표준편차1) | `StandardScaler()` → `fit_transform` |
| 범주형 → 숫자 | `OneHotEncoder(sparse_output=False)` |
| 전처리+모델 묶기 | `Pipeline([("sc", ...), ("clf", ...)])` |
| 묶은 채로 학습/예측 | `pipe.fit(X_tr, y_tr)` / `pipe.predict(X_te)` |
| 열별 다른 전처리 | `ColumnTransformer` (수치=스케일, 범주=원핫) |

> 전처리 핵심 규칙: **`fit`은 train에만. test는 train 기준으로 `transform`만.** 이걸 자동으로 지켜주는 게 `Pipeline`.

---

## 정리

| 예제/연습 | 핵심 |
|-----------|------|
| wine 스케일링 비교 | 전처리로 0.72→0.94 |
| StandardScaler | 20의 표준화 = `(x-mean)/std` |
| OneHotEncoder | 범주 → 0/1 열 |
| Pipeline | 전처리+모델, 누수 방지 |

> 핵심 한 줄: **전처리 = 스케일링(StandardScaler)·인코딩(OneHotEncoder)으로 데이터를 모델이 먹기 좋게. Pipeline으로 묶어 train에만 fit → 누수 방지.**