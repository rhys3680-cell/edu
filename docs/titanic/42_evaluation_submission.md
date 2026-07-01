# 타이타닉 42 — 평가 & 제출

> **대상**: 타이타닉 전처리·모델링(41)을 마친 단계. 첫 프로젝트의 **마무리**.
> **목표**: 33의 평가 도구로 모델을 제대로 진단하고, **특성 공학**으로 성능을 올린 뒤, test를 예측해 **캐글 제출 파일**을 만들기.

41에서 베이스라인 ~80%를 만들었습니다. 이제 (1) **어떤 사람을 잘못 예측하는지** 들여다보고(33), (2) **새 특성을 만들어** 성능을 올리고, (3) test.csv를 예측해 **submission.csv**를 생성합니다 — 캐글 프로젝트의 완결.

---

## 0) 데이터 로드 (41과 동일)

```python
import pandas as pd
from pathlib import Path

DATA_DIR = Path.cwd().parent.parent / "data" / "titanic"
train = pd.read_csv(DATA_DIR / "train.csv")
test  = pd.read_csv(DATA_DIR / "test.csv")
```

---

## 1) 모델 진단 — 혼동행렬·정밀도·재현율 (33 실전)

정확도 한 숫자 말고, **어떤 실수를 했는지** 봅니다. (41의 로지스틱 모델 기준)

```python
from sklearn.metrics import confusion_matrix, precision_score, recall_score, classification_report

# (41의 model을 train/test 분할로 학습했다고 가정)
pred = model.predict(X_test)

confusion_matrix(y_test, pred)
# [[99 11]      실제 사망 110명: 99명 맞음, 11명을 생존으로 오판(FP)
#  [18 51]]     실제 생존  69명: 18명을 사망으로 놓침(FN), 51명 맞음

precision_score(y_test, pred)   # 0.82  생존 예측 중 진짜 생존 비율
recall_score(y_test, pred)      # 0.74  진짜 생존자 중 잡아낸 비율
```

> 가르칠 포인트: 재현율 0.74 — **실제 생존자 69명 중 18명을 "사망"으로 놓쳤습니다**(FN). 정확도(0.80)만 봤으면 몰랐을 약점이죠. `classification_report(y_test, pred)`로 클래스별 지표를 한 번에 볼 수 있습니다. (33에서 배운 그대로)

---

## 2) 특성 공학 (Feature Engineering) — 성능 올리기

기존 열을 **조합·가공**해 새 특성을 만듭니다. 모델이 더 잘 배우도록 돕는 핵심 단계예요.

```python
def add_features(df):
    df = df.copy()
    # (a) 가족 크기: 형제/배우자 + 부모/자녀 + 본인
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1

    # (b) 이름에서 직함(Title) 추출 — "Braund, Mr. Owen" → "Mr"
    df["Title"] = df["Name"].str.extract(r",\s*([^\.]+)\.")
    # 표기 통일 + 희귀 직함 묶기
    df["Title"] = df["Title"].replace(["Mlle", "Ms"], "Miss").replace("Mme", "Mrs")
    rare = df["Title"].value_counts()[df["Title"].value_counts() < 10].index
    df["Title"] = df["Title"].replace(rare, "Rare")
    return df

train_fe = add_features(train)
train_fe.groupby("Title")["Survived"].mean().round(3)
# Mr      0.157    Master  0.575
# Miss    0.703    Mrs     0.794    Rare    0.348
```

> **왜 Title인가**: 이름 자체는 못 쓰지만, **직함**엔 정보가 가득합니다 — `Mr`(성인 남성) 생존율 16%, `Mrs`/`Miss`(여성) 70~79%, `Master`(남자아이) 58%. 성별·나이·결혼여부가 직함 하나에 압축돼 있어요. 이게 **특성 공학** — 도메인 지식으로 숨은 정보를 끄집어내는 것.

---

## 3) 특성 공학 효과 — 모델에 따라 다르다 (중요)

새 특성으로 다시 교차검증해 봅니다.

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

num_f = ["Age", "Fare", "FamilySize"]
cat_f = ["Pclass", "Sex", "Embarked", "Title"]
X, y = train_fe[num_f + cat_f], train_fe["Survived"]

pre = ColumnTransformer([
    ("num", Pipeline([("i", SimpleImputer(strategy="median")), ("s", StandardScaler())]), num_f),
    ("cat", Pipeline([("i", SimpleImputer(strategy="most_frequent")),
                      ("o", OneHotEncoder(handle_unknown="ignore"))]), cat_f),
])
model = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])

cross_val_score(model, X, y, cv=5).mean()   # 0.8272  (41 베이스라인 0.79에서 상승!)
```

> 결과: 로지스틱 회귀가 **0.79 → 0.83**으로 올랐습니다. 핵심 교훈: **선형 모델(로지스틱)은 특성 공학의 덕을 크게 봅니다.** 반면 랜덤포레스트는 이미 특성 간 상호작용을 잘 잡아서 효과가 작아요(0.806 → 0.805). "어떤 모델엔 특성 공학이 더 중요한가"를 아는 게 실전 감각입니다.

---

## 4) test 예측 → 제출 파일 만들기 (캐글 완결)

전체 train으로 학습한 뒤, test.csv를 예측해 **submission.csv**를 만듭니다.

```python
# test에도 같은 특성 공학 적용 (train과 똑같이!)
test_fe = add_features(test)

# 전체 train으로 학습 (이제 분할 안 함 — 가진 데이터 전부 사용)
model.fit(X, y)

# test 예측
test_pred = model.predict(test_fe[num_f + cat_f])

# 캐글 제출 형식: PassengerId + Survived
submission = pd.DataFrame({
    "PassengerId": test["PassengerId"],
    "Survived": test_pred,
})
submission.to_csv(DATA_DIR / "submission.csv", index=False)

submission.head()
#    PassengerId  Survived
# 0          892         0
# 1          893         1
# 2          894         0
```

> 핵심 두 가지:
> 1. **test에도 똑같은 전처리·특성 공학**을 적용해야 합니다. train만 가공하면 열이 안 맞아 에러. (`add_features`를 test에도 호출)
> 2. **제출 형식**은 `gender_submission.csv`와 같아야 합니다 — `PassengerId`, `Survived` 두 열, 418행. `index=False`로 저장(인덱스 열이 들어가면 형식 깨짐).

> 이 `submission.csv`를 캐글에 업로드하면 채점됩니다. (대회 페이지 → Submit Predictions) 리더보드 점수는 보통 CV와 비슷하거나 살짝 낮습니다.

---

## 대표 예제 — 전체 파이프라인 (학습 → 제출)

> 특성 공학을 적용한 로지스틱 모델을 전체 train으로 학습하고, test 예측으로 제출 DataFrame을 만들어 행 수·열을 확인하라.

```python
import pandas as pd
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression

DATA_DIR = Path.cwd().parent.parent / "data" / "titanic"
train = pd.read_csv(DATA_DIR / "train.csv")
test  = pd.read_csv(DATA_DIR / "test.csv")

def add_features(df):
    df = df.copy()
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1
    df["Title"] = df["Name"].str.extract(r",\s*([^\.]+)\.")
    df["Title"] = df["Title"].replace(["Mlle", "Ms"], "Miss").replace("Mme", "Mrs")
    rare = df["Title"].value_counts()[df["Title"].value_counts() < 10].index
    df["Title"] = df["Title"].replace(rare, "Rare")
    return df

train_fe, test_fe = add_features(train), add_features(test)
num_f = ["Age", "Fare", "FamilySize"]
cat_f = ["Pclass", "Sex", "Embarked", "Title"]
X, y = train_fe[num_f + cat_f], train_fe["Survived"]

pre = ColumnTransformer([
    ("num", Pipeline([("i", SimpleImputer(strategy="median")), ("s", StandardScaler())]), num_f),
    ("cat", Pipeline([("i", SimpleImputer(strategy="most_frequent")),
                      ("o", OneHotEncoder(handle_unknown="ignore"))]), cat_f),
])
model = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))]).fit(X, y)

submission = pd.DataFrame({
    "PassengerId": test["PassengerId"],
    "Survived": model.predict(test_fe[num_f + cat_f]),
})
print(submission.shape)              # (418, 2)
print(submission.columns.tolist())   # ['PassengerId', 'Survived']
```

> 가르칠 포인트: **train/test에 같은 가공 → 전체 train으로 학습 → test 예측 → 형식 맞춰 저장.** 이 흐름이 모든 캐글 프로젝트의 뼈대입니다. 30~33 + 40~42가 여기서 하나로 합쳐졌어요.

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
from sklearn.model_selection import cross_val_score

DATA_DIR = Path.cwd().parent.parent / "data" / "titanic"
train = pd.read_csv(DATA_DIR / "train.csv")
test  = pd.read_csv(DATA_DIR / "test.csv")

def add_features(df):
    df = df.copy()
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1
    df["Title"] = df["Name"].str.extract(r",\s*([^\.]+)\.")
    df["Title"] = df["Title"].replace(["Mlle", "Ms"], "Miss").replace("Mme", "Mrs")
    rare = df["Title"].value_counts()[df["Title"].value_counts() < 10].index
    df["Title"] = df["Title"].replace(rare, "Rare")
    return df

train_fe, test_fe = add_features(train), add_features(test)
num_f = ["Age", "Fare", "FamilySize"]
cat_f = ["Pclass", "Sex", "Embarked", "Title"]
X, y = train_fe[num_f + cat_f], train_fe["Survived"]
pre = ColumnTransformer([
    ("num", Pipeline([("i", SimpleImputer(strategy="median")), ("s", StandardScaler())]), num_f),
    ("cat", Pipeline([("i", SimpleImputer(strategy="most_frequent")),
                      ("o", OneHotEncoder(handle_unknown="ignore"))]), cat_f),
])
model = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])

# 특성 공학으로 CV ≈ 0.83 (41 베이스라인 0.79보다 상승)
assert abs(cross_val_score(model, X, y, cv=5).mean() - 0.8272) < 0.001

# Title 추출 확인
assert set(train_fe["Title"].unique()) == {"Mr", "Miss", "Mrs", "Master", "Rare"}

# 제출 파일 형식
model.fit(X, y)
submission = pd.DataFrame({"PassengerId": test["PassengerId"],
                           "Survived": model.predict(test_fe[num_f + cat_f])})
assert submission.shape == (418, 2)
assert list(submission.columns) == ["PassengerId", "Survived"]
assert not submission["Survived"].isna().any()    # 결측 없어야 제출 가능
print("통과 ✅")
```

---

## 직접 풀어보기 (연습)

`TODO`를 채운 뒤 검증 셀을 실행하세요.

### 연습 1 — 직함별 생존율

> 특성 공학된 데이터에서 직함(`Title`)별 생존율을 dict로 반환하라. (round 3자리)
> **힌트**: `groupby("Title")["Survived"].mean()`.

```python
def solution(train_fe):
    # TODO: Title별 생존율 → round(3) → to_dict()
    pass

result = solution(train_fe)
assert abs(result["Mr"] - 0.157) < 0.001     # 성인 남성 생존율 낮음
assert abs(result["Mrs"] - 0.794) < 0.001    # 기혼 여성 높음
print("통과 ✅")
```

### 연습 2 — 혼동행렬에서 FN 세기

> 모델 예측의 혼동행렬에서 FN(실제 생존인데 사망으로 놓친 수)을 반환하라.
> **힌트**: `confusion_matrix(y_test, pred)`의 `[1][0]` 위치.

```python
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

def solution(X, y, model):
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model.fit(Xtr, ytr)
    pred = model.predict(Xte)
    cm = confusion_matrix(yte, pred)
    # TODO: FN = cm[1][0]
    pass

assert solution(X, y, model) == 18    # 생존자 18명을 놓침
print("통과 ✅")
```

### 연습 3 — 제출 파일 생성 (도전)

> 모델을 전체 train으로 학습하고 test를 예측해, 생존(1)으로 예측된 사람 수를 반환하라.

```python
def solution(X, y, test_fe, num_f, cat_f, model):
    model.fit(X, y)
    pred = model.predict(test_fe[num_f + cat_f])
    # TODO: 생존(1) 예측 수 반환 — int(pred.sum())
    pass

# test 418명 중 생존 예측 인원
assert solution(X, y, test_fe, num_f, cat_f, model) == 168
print("통과 ✅")
```

---

## 치트시트

| 하고 싶은 것 | 코드 |
|-------------|------|
| 모델 진단 | `confusion_matrix`, `classification_report` |
| 가족 수 특성 | `df["SibSp"] + df["Parch"] + 1` |
| 이름→직함 | `df["Name"].str.extract(r",\s*([^\.]+)\.")` |
| 전체 학습 | `model.fit(X, y)` (분할 없이 전부) |
| test 예측 | `model.predict(test_fe[features])` |
| 제출 저장 | `submission.to_csv(..., index=False)` |

> 캐글 제출 사고법: **train/test에 같은 가공 → 전체 train 학습 → test 예측 → PassengerId+Survived로 저장(index=False).** 그리고 특성 공학은 선형 모델일수록 효과가 크다.

---

## 정리

| 예제/연습 | 핵심 |
|-----------|------|
| 전체 파이프라인 | 학습→예측→제출 형식 |
| 직함별 생존율 | 특성 공학의 정보력 |
| FN 세기 | 혼동행렬 진단 |
| 제출 생성 | test 예측 (생존 168명) |

> 핵심 한 줄: **평가는 혼동행렬로 약점을 보고, 특성 공학(Title 등)으로 성능을 올리고(0.79→0.83), test 예측을 PassengerId+Survived로 저장해 캐글에 제출. 5단계 완결.**

---

## 🎉 타이타닉 프로젝트 완료 (40~42)

| # | 단계 | 핵심 |
|---|------|------|
| 40 | EDA | 결측치·그룹별 생존율 → 핵심 특성 발견 |
| 41 | 전처리·모델링 | ColumnTransformer + Pipeline, 베이스라인 0.80 |
| 42 | 평가·제출 | 혼동행렬 진단, 특성 공학 0.83, submission.csv |

> 30~33(ML 입문)에서 배운 fit/predict·전처리·평가가 **하나의 실전 프로젝트로 합쳐졌습니다.** 다음은 **6단계 심화 프로젝트(2트랙)** — 이상거래 탐지(불균형 분류)·CLV(고객 분석) 또는 주가 예측·퀀트로 갈라집니다.