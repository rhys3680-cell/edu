# 유형 01 — 자료구조 기초 (스택 / 큐 / 해시)

> **대상**: Lv.0 패턴(반복·조건·문자열)은 손에 익은 단계.
> **목표**: "어떤 자료구조를 고르느냐가 곧 시간복잡도를 결정한다"를 체득하기.

이 유형은 알고리즘이라기보다 **도구 선택 훈련**입니다. 같은 문제도 리스트로 풀면 O(n²)인데 해시로 풀면 O(n)이 됩니다.

---

## 1) 스택 (Stack) — LIFO (후입선출)

마지막에 넣은 게 먼저 나옵니다. **"직전 것과 비교 / 취소 / 짝 맞추기"** 패턴에 강합니다.

```python
stack = []
stack.append(1)    # push
stack.append(2)
top = stack.pop()  # pop → 2 (마지막에 넣은 것)
```

Python에서는 **리스트의 `append`/`pop`이 곧 스택**입니다. 둘 다 O(1).

**대표 패턴 — 짝 지어 제거**

```python
# "같은 글자가 연속으로 두 번 나오면 짝지어 제거. 모두 지워지면 1, 아니면 0"
def solution(s):
    stack = []
    for ch in s:
        if stack and stack[-1] == ch:   # 직전 글자와 같으면 짝 → 제거
            stack.pop()
        else:
            stack.append(ch)
    return 1 if not stack else 0
```

**검증 — 같은 입력이면 이 답이 나와야 합니다:**

```python
print(solution("baabaa"))   # 1  (b-aa-b-aa → 전부 짝지어 사라짐)
print(solution("cdcd"))     # 0  (연속 중복이 없어 하나도 못 지움)

# assert로 기대값 고정 (틀리면 AssertionError로 알려줌)
assert solution("baabaa") == 1
assert solution("cdcd") == 0
print("통과 ✅")
```

> 핵심: 지문에 **"직전", "바로 앞", "괄호", "취소"**가 나오면 스택을 의심하세요. `stack[-1]`로 맨 위(가장 최근)를 들여다보는 게 패턴의 절반입니다.

---

## 2) 큐 (Queue) — FIFO (선입선출)

먼저 넣은 게 먼저 나옵니다. **순서대로 처리 / 대기열 / BFS**에 쓰입니다.

```python
from collections import deque

q = deque()
q.append(1)         # enqueue (뒤로 넣기)
q.append(2)
first = q.popleft() # dequeue → 1 (먼저 넣은 것), O(1)
```

> ⚠️ **중요**: `list.pop(0)`은 O(n)이라 큐로 쓰면 시간초과의 단골 원인입니다. 반드시 `collections.deque`를 쓰세요.

**대표 패턴 — 회전하며 처리**

```python
# "우선순위가 더 높은 작업이 뒤에 있으면 현재 작업을 맨 뒤로 보낸다"
from collections import deque

def solution(priorities, location):
    q = deque((p, i) for i, p in enumerate(priorities))
    order = 0
    while q:
        cur = q.popleft()
        if any(cur[0] < other[0] for other in q):
            q.append(cur)          # 더 높은 우선순위가 뒤에 있으면 맨 뒤로
        else:
            order += 1             # 실행
            if cur[1] == location:
                return order
```

**검증:**

```python
print(solution([2, 1, 3, 2], 2))        # 1  (location=2 작업이 가장 먼저 실행됨)
print(solution([1, 1, 9, 1, 1, 1], 0))  # 5  (앞쪽 1들은 뒤의 9에 밀려 한참 뒤에 실행)

assert solution([2, 1, 3, 2], 2) == 1
assert solution([1, 1, 9, 1, 1, 1], 0) == 5
print("통과 ✅")
```

> 핵심: **"먼저 온 순서대로", "한 바퀴 돌려서", "대기"**가 나오면 큐. 꺼낸 걸 다시 뒤에 넣으면 "회전"이 됩니다.

---

## 3) 해시 (Hash) — dict / set

**"빠른 조회 / 개수 세기 / 중복 제거"**가 필요할 때. 평균 O(1) 검색이 핵심 무기입니다.

```python
# dict: 키 → 값
count = {}
count['a'] = count.get('a', 0) + 1   # 없으면 0에서 시작해 +1

# set: 존재 여부만, 중복 없음
seen = set()
seen.add('x')
'x' in seen          # O(1) 검색
```

**더 편한 도구 두 개:**

```python
from collections import Counter, defaultdict

Counter(['a', 'b', 'a'])     # {'a': 2, 'b': 1}  ← 카운팅 자동
d = defaultdict(int)         # 없는 키 접근 시 자동으로 0
d['x'] += 1                  # KeyError 없이 바로 누적
```

> 핵심: 리스트에서 `in`으로 찾으면 O(n)이지만, **set/dict의 `in`은 O(1)**. "찾기"가 반복되면 해시로 바꾸세요.

---

## 대표 문제 풀이 — 완주하지 못한 선수 (프로그래머스 42576)

> 참가자(`participant`) 중 완주자(`completion`)에 없는 한 명을 찾기. 동명이인 가능.

**① 신호**: "~중에 없는", "누가 빠졌나", "동명이인(개수가 중요)"
**② 패턴**: 해시 (개수 세기)

**나이브한 방법 (틀림/느림)**: 리스트에서 하나씩 `remove` → O(n²), 시간초과.

**해시로 카운팅 (정답, O(n))**:

```python
from collections import Counter

def solution(participant, completion):
    # 참가자 전원 카운트 - 완주자 전원 카운트
    answer = Counter(participant) - Counter(completion)
    # 남는 한 명(카운트가 1 이상인 키)이 미완주자
    return list(answer.keys())[0]
```

**`Counter` 없이 원리 이해용**:

```python
def solution(participant, completion):
    d = {}
    for p in participant:
        d[p] = d.get(p, 0) + 1      # 참가자 +1
    for c in completion:
        d[c] -= 1                   # 완주자 -1
    for name, cnt in d.items():
        if cnt > 0:                 # 안 빠진 사람 = 미완주
            return name
```

**검증:**

```python
print(solution(["leo", "kiki", "eden"], ["eden", "kiki"]))   # leo
print(solution(["mislav", "stanko", "mislav", "ana"],
               ["stanko", "ana", "mislav"]))                 # mislav (동명이인 주의)

assert solution(["leo", "kiki", "eden"], ["eden", "kiki"]) == "leo"
assert solution(["mislav", "stanko", "mislav", "ana"],
                ["stanko", "ana", "mislav"]) == "mislav"
print("통과 ✅")
```

> 가르칠 포인트: **"리스트에서 찾기(O(n))를 dict 조회(O(1))로 바꾸는 것"**이 이 유형의 본질입니다. 동명이인 때문에 set이 아니라 **개수를 세는 dict/Counter**를 써야 한다는 점도 중요.
>
> 두 번째 검증(`mislav` 동명이인)이 **set으로 풀면 틀리는 케이스**입니다. set은 중복을 지워버려서 "두 명 중 한 명만 완주"를 구분 못 합니다. 직접 set 버전으로 풀어 보고 이 입력에서 깨지는 걸 확인하면 "왜 개수를 세야 하는지"가 와닿습니다.

---

## 이 유형의 판단 기준 (치트시트)

| 지문에 이런 말이 나오면 | 선택 |
|------------------------|------|
| "직전 / 바로 앞 / 괄호 / 취소 / 짝" | **스택** (`list` + `append`/`pop`) |
| "순서대로 / 먼저 온 것 먼저 / 대기열 / 한 바퀴" | **큐** (`deque` + `popleft`) |
| "~에 있나? / 개수 / 중복 제거 / 빠르게 찾기" | **해시** (`set`/`dict`/`Counter`) |

> 시간복잡도 관점: "리스트에서 반복적으로 찾는다"가 보이면 거의 항상 **해시로 바꿔 O(n²) → O(n)** 으로 줄일 수 있습니다.

---

## 직접 풀어보기 (연습)

힌트를 보고 `TODO`를 채운 뒤, 검증 셀을 실행해 통과하는지 확인하세요. 막히면 위 패턴 설명으로 돌아가 어떤 자료구조인지부터 판단합니다.

### 연습 1 — 올바른 괄호 (프로그래머스 12909)

> `(`와 `)`로만 이루어진 문자열이 올바른 괄호이면 `True`, 아니면 `False`.
> **힌트(스택)**: `(`면 push, `)`면 — 짝이 있으면 pop, 없으면 실패. 끝까지 갔을 때 스택이 비어 있으면 올바른 괄호.

```python
def solution(s):
    # TODO: 직접 작성
    pass

# 검증
assert solution("()()") == True
assert solution("(())()") == True
assert solution(")(") == False      # 닫는 괄호가 먼저 옴
assert solution("(()(") == False    # 끝에 짝 없는 ( 가 남음
print("통과 ✅")
```

### 연습 2 — 폰켓몬 (프로그래머스 1845)

> `N`마리 중 정확히 `N/2`마리를 골라야 한다. 최대 몇 **종류**를 가질 수 있나?
> **힌트(해시/set)**: 고를 수 있는 수는 `N/2`. 종류 수는 `set`으로 중복 제거한 개수. 둘 중 **작은 값**이 답.

```python
def solution(nums):
    # TODO: 직접 작성
    pass

# 검증
assert solution([3, 1, 2, 3]) == 2          # N/2=2, 종류 {1,2,3}=3 → min=2
assert solution([3, 3, 3, 2, 2, 4]) == 3    # N/2=3, 종류 {2,3,4}=3 → min=3
assert solution([3, 3, 3, 2, 2, 2]) == 2    # N/2=3, 종류 {2,3}=2 → min=2
print("통과 ✅")
```

## 연습 추천 (프로그래머스) — 더 풀어볼 문제

| 자료구조 | 문제 | 번호 |
|----------|------|------|
| 스택 | 같은 숫자는 싫어 | 12906 |
| 스택 | 올바른 괄호 | 12909 |
| 큐 | 프로세스 | 42587 |
| 큐 | 다리를 지나는 트럭 | 42583 |
| 해시 | 완주하지 못한 선수 | 42576 |
| 해시 | 폰켓몬 | 1845 |