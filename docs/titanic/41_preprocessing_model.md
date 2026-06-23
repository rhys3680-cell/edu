# 타이타닉 41 — 전처리 & 모델링

> **대상**: 타이타닉 EDA(40)를 마친 단계.
> **목표**: EDA에서 찾은 특성으로 **결측치 처리 → 인코딩 → Pipeline → 모델 학습**까지, 32에서 배운 전처리를 실전 데이터에 적용하기.

40에서 "성별·등급이 생존을 가른다"는 걸 찾았고, "Age·Cabin·Embarked에 결측치가 있다"는 것도 봤습니다. 이제 그 데이터를 **모델이 먹을 수 있게 다듬어** 학습시킵니다. 핵심 도구는 32에서 본 `Pipeline`과, 수치/범주를 따로 처리하는 **`ColumnTransformer`**입니다.

---

## 0) 데이터 로드 & 특성 선택

```python
import pandas as pd
from pathlib import Path

DATA_DIR = Path.cwd().parent.parent / "data" / "titanic"
train = pd.read_csv(DATA_DIR / "train.csv")

# 쓸 특성: 수치형 / 범주형 구분 (전처리가 다르므로)
num_features = ["Age", "Fare", "SibSp", "Parch"]      # 수치 → 결측 채움 + 스케일
cat_features = ["Pclass", "Sex", "Embarked"]          # 범주 → 결측 채움 + 원핫

X = train[num_features + cat_features]
y = train["Survived"]                                  # 정답
```

> **특성 선택**: `Name`·`Ticket`·`Cabin`·`PassengerId`는 뺐습니다. `Cabin`은 결측 77%라 버리고, `Name`/`Ticket`은 그대로는 쓰기 어렵습니다(나중에 가공 가능). 40의 EDA가 "Pclass·Sex가 핵심"이라고 알려줬으니 그것들을 중심으로.

> 수치형과 범주형을 **나눈 이유**: 둘은 전처리가 다릅니다 — 수치는 "결측을 중앙값으로 채우고 스케일링", 범주는 "결측을 최빈값으로 채우고 원-핫". 이걸 한 번에 처리하는 게 `ColumnTransformer`(3번).

---

## 1) 결측치 채우기 — SimpleImputer

40에서 본 결측치(Age 177, Embarked 2)를 채웁니다. 모델은 빈 값(NaN)을 못 먹으니까요.

```python
from sklearn.impute import SimpleImputer

# 수치형: 중앙값(median)으로 채움 — 이상치에 강함
num_imputer = SimpleImputer(strategy="median")
# Age의 중앙값은 28.0 → 빈 Age 177개가 모두 28.0으로 채워짐

# 범주형: 최빈값(most_frequent)으로 채움
cat_imputer = SimpleImputer(strategy="most_frequent")
# Embarked의 최빈값은 'S' → 빈 Embarked 2개가 'S'로
```

> **왜 median인가**: 평균(mean)은 이상치(아주 비싼 Fare 등)에 흔들리지만 중앙값은 안정적입니다. 나이·운임 같은 데이터엔 median이 무난해요. 범주형은 "가장 흔한 값"으로 채우는 게 자연스럽습니다.

---

## 2) 전처리 묶기 — 수치/범주 각각의 Pipeline

수치형은 "채우기 → 스케일", 범주형은 "채우기 → 원핫"을 각각 `Pipeline`(32)으로 묶습니다.

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder

num_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

cat_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore")),   # 처음 보는 범주 무시
])
```

> `handle_unknown="ignore"`: test 데이터에 train엔 없던 범주가 나와도 에러 없이 처리(전부 0). 실전에서 중요한 안전장치입니다.

---

## 3) ColumnTransformer — 열마다 다른 전처리 (핵심)

`ColumnTransformer`로 "수치 열엔 num_pipe, 범주 열엔 cat_pipe"를 **한 번에** 적용합니다.

```python
from sklearn.compose import ColumnTransformer

preprocessor = ColumnTransformer([
    ("num", num_pipe, num_features),   # num_features 열에 num_pipe
    ("cat", cat_pipe, cat_features),   # cat_features 열에 cat_pipe
])
```

> 이게 32의 `Pipeline`을 실전으로 확장한 것입니다. 표 데이터는 열마다 타입이 다르니(숫자/글자), **열별로 다른 전처리**가 필수예요. `ColumnTransformer`가 그걸 하나의 전처리기로 묶어줍니다.

---

## 4) 전처리 + 모델 = 최종 Pipeline

전처리기와 모델을 다시 `Pipeline`으로 묶으면 **하나의 모델**이 됩니다.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

model = Pipeline([
    ("preprocessor", preprocessor),    # 전처리 (채우기+스케일+원핫)
    ("classifier", LogisticRegression(max_iter=1000)),
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

model.fit(X_train, y_train)            # 전처리+학습이 이 한 줄에
model.score(X_test, y_test)            # ≈ 0.80  (test 정확도)
```

> **누수 방지**(32·33): `model.fit(X_train, ...)`은 전처리기를 train으로만 fit합니다. test의 중앙값·범주를 미리 보지 않아요. Pipeline으로 묶었기에 자동으로 안전합니다. test 예측 시엔 train에서 배운 중앙값/스케일을 그대로 적용.

---

## 대표 예제 — 두 모델 비교 (교차검증)

> 로지스틱 회귀와 랜덤포레스트를 같은 전처리로 학습하고, 5-fold 교차검증으로 비교하라.

```python
import pandas as pd
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

DATA_DIR = Path.cwd().parent.parent / "data" / "titanic"
train = pd.read_csv(DATA_DIR / "train.csv")

num_features = ["Age", "Fare", "SibSp", "Parch"]
cat_features = ["Pclass", "Sex", "Embarked"]
X, y = train[num_features + cat_features], train["Survived"]

preprocessor = ColumnTransformer([
    ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                      ("sc", StandardScaler())]), num_features),
    ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                      ("oh", OneHotEncoder(handle_unknown="ignore"))]), cat_features),
])

for name, clf in [("로지스틱", LogisticRegression(max_iter=1000)),
                  ("랜덤포레스트", RandomForestClassifier(random_state=42))]:
    pipe = Pipeline([("pre", preprocessor), ("clf", clf)])
    cv = cross_val_score(pipe, X, y, cv=5).mean()
    print(f"{name}: {cv:.4f}")
```

**기대 결과:**

```
로지스틱: 0.7901
랜덤포레스트: 0.8059
```

> 가르칠 포인트: **같은 전처리, 모델만 교체**(30의 인터페이스 일관성). 랜덤포레스트가 살짝 높네요(0.81 vs 0.79). 교차검증으로 비교했으니 "한 번 운 좋은" 결과가 아닙니다. 타이타닉 베이스라인으로 80% 정도면 무난한 출발점이에요. (캐글 상위권은 특성 공학으로 83%+를 노립니다 — 42에서 개선)

---

## 검증 (노트북에서 실행)

```python
import pandas as pd
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score

DATA_DIR = Path.cwd().parent.parent / "data" / "titanic"
train = pd.read_csv(DATA_DIR / "train.csv")
num_f = ["Age", "Fare", "SibSp", "Parch"]
cat_f = ["Pclass", "Sex", "Embarked"]
X, y = train[num_f + cat_f], train["Survived"]

# Age 중앙값 = 28.0
assert SimpleImputer(strategy="median").fit(train[["Age"]]).statistics_[0] == 28.0

pre = ColumnTransformer([
    ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                      ("sc", StandardScaler())]), num_f),
    ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                      ("oh", OneHotEncoder(handle_unknown="ignore"))]), cat_f),
])
model = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])

# test 정확도 ≈ 0.80
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
model.fit(Xtr, ytr)
assert abs(model.score(Xte, yte) - 0.8045) < 0.001

# CV 평균 ≈ 0.79
assert abs(cross_val_score(model, X, y, cv=5).mean() - 0.7901) < 0.001
print("통과 ✅")
```

---

## 직접 풀어보기 (연습)

`TODO`를 채운 뒤 검증 셀을 실행하세요.

### 연습 1 — Age 중앙값 채우기

> SimpleImputer로 Age를 중앙값으로 채울 때, 그 중앙값을 반환하라.
> **힌트**: `SimpleImputer(strategy="median").fit(df[["Age"]]).statistics_[0]`.

```python
from sklearn.impute import SimpleImputer

def solution(train):
    # TODO: Age 중앙값 반환
    pass

assert solution(train) == 28.0
print("통과 ✅")
```

### 연습 2 — 핵심 특성만으로 모델 (Sex + Pclass)

> Sex와 Pclass **두 특성만** 원-핫 인코딩해 로지스틱 회귀로 5-fold 교차검증 평균을 구하라. (round 4자리)
> **힌트**: `ColumnTransformer([("cat", OneHotEncoder(), ["Sex","Pclass"])])` + Pipeline + `cross_val_score`.

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

def solution(train):
    X = train[["Sex", "Pclass"]]
    y = train["Survived"]
    # TODO: 원핫 → 로지스틱 → cross_val_score(cv=5) 평균 round 4
    pass

# 단 2개 특성만으로도 0.79 — EDA가 찾은 핵심 특성의 힘!
assert abs(solution(train) - 0.7867) < 0.001
print("통과 ✅")
```

### 연습 3 — 모델 바꿔 정확도 (도전)

> 전체 전처리 + `RandomForestClassifier(random_state=42)`로 test 정확도를 구하라. (`test_size=0.2, random_state=42, stratify`)

```python
from sklearn.ensemble import RandomForestClassifier

def solution(train, preprocessor):
    X = train[["Age","Fare","SibSp","Parch","Pclass","Sex","Embarked"]]
    y = train["Survived"]
    # TODO: Pipeline(preprocessor + RF) → 분할 → fit → test 정확도 round 4
    pass

# preprocessor는 위에서 만든 것 재사용
assert abs(solution(train, pre) - 0.8156) < 0.001
print("통과 ✅")
```

---

## 치트시트

| 하고 싶은 것     | 코드                                                          |
| ---------------- | ------------------------------------------------------------- |
| 결측치 채우기    | `SimpleImputer(strategy="median" / "most_frequent")`          |
| 수치 전처리      | `Pipeline([imputer, StandardScaler])`                         |
| 범주 전처리      | `Pipeline([imputer, OneHotEncoder(handle_unknown="ignore")])` |
| 열별 다른 전처리 | `ColumnTransformer([("num",...,num_f), ("cat",...,cat_f)])`   |
| 전처리+모델      | `Pipeline([("pre", preprocessor), ("clf", model)])`           |
| 모델 비교        | `cross_val_score(pipe, X, y, cv=5).mean()`                    |

> 실전 전처리 사고법: **(1) 수치/범주 열을 나눈다 → (2) 각각 결측 채우기+변환을 Pipeline으로 → (3) ColumnTransformer로 묶는다 → (4) 모델과 합쳐 최종 Pipeline. 누수는 Pipeline이 자동 방지.**

---

## 정리

| 예제/연습    | 핵심                              |
| ------------ | --------------------------------- |
| 두 모델 비교 | ColumnTransformer + Pipeline + CV |
| Age 중앙값   | `SimpleImputer(median)` = 28.0    |
| Sex+Pclass만 | 핵심 특성 2개로 0.79              |
| 랜덤포레스트 | 모델 교체 0.82                    |

> 핵심 한 줄: **실전 전처리 = 수치(채우기+스케일)/범주(채우기+원핫)를 ColumnTransformer로 묶고, 모델과 합쳐 Pipeline. EDA가 고른 특성으로 베이스라인 80%.**
