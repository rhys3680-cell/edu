# 유형 05 — DFS / BFS

> **대상**: 완전탐색(재귀, 유형 03)과 큐(유형 01)를 익힌 단계.
> **목표**: "연결된 것을 빠짐없이 탐색"하는 두 방식 — **DFS(깊이 우선)**와 **BFS(너비 우선)** — 을 구분해서 쓰기.

DFS/BFS는 **"갈 수 있는 곳을 모두 방문"**하는 탐색입니다. 03의 재귀가 "모든 경우 만들기"였다면, 여기선 **"칸/노드를 이동하며 방문 표시"**가 추가됩니다. 핵심은 **방문 체크(`visited`)** — 안 하면 무한 루프에 빠집니다.

---

## 0) DFS vs BFS — 한눈에

| | DFS (깊이 우선) | BFS (너비 우선) |
|--|----------------|----------------|
| 방식 | 한 길을 끝까지 파고든 뒤 되돌아옴 | 가까운 곳부터 한 겹씩 펼침 |
| 도구 | **재귀** 또는 **스택** | **큐 (`deque`)** |
| 잘하는 것 | 경로 존재 여부, 모든 경우, 백트래킹 | **최단 거리 / 최소 횟수** |
| 신호 | "연결돼 있나", "모든 ~를 방문" | "**최소 몇 번**", "**가장 빠른**" |

> 가장 중요한 한 줄: **"최단/최소"가 나오면 BFS.** BFS는 가까운 것부터 퍼지므로, 목표에 처음 도달한 순간이 곧 최단 거리입니다.

---

## 1) DFS — 재귀 (가장 흔한 형태)

```python
# 인접 리스트로 표현된 그래프를 DFS로 방문
def dfs(node, graph, visited):
    visited.add(node)              # 방문 표시 (먼저!)
    for nxt in graph[node]:
        if nxt not in visited:     # 안 가본 곳만
            dfs(nxt, graph, visited)

graph = {1: [2, 3], 2: [1, 4], 3: [1], 4: [2]}
visited = set()
dfs(1, graph, visited)
# visited = {1, 2, 3, 4}
```

> 패턴: **방문 표시 → 이웃 순회 → 안 가본 이웃으로 재귀.** 03의 "선택→재귀→되돌리기"에서, 여기선 `visited`로 "이미 한 선택"을 막는 게 추가됐습니다.

---

## 2) BFS — 큐 (최단 거리의 정석)

```python
from collections import deque

def bfs(start, graph):
    visited = {start}
    q = deque([start])
    while q:
        node = q.popleft()         # 큐에서 꺼내고
        for nxt in graph[node]:
            if nxt not in visited:
                visited.add(nxt)   # 넣을 때 방문 표시 (중복 방지 핵심)
                q.append(nxt)
    return visited
```

> ⚠️ 핵심: **큐에 넣는 순간 `visited` 표시**해야 합니다. 꺼낼 때 표시하면 같은 노드가 큐에 여러 번 들어가 터집니다.

---

## 3) 2차원 격자 탐색 (코테 단골)

대부분의 DFS/BFS 문제는 **2D 지도**입니다. 상하좌우 이동이 핵심.

```python
from collections import deque

def bfs_grid(grid, sr, sc):
    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    dr = [-1, 1, 0, 0]     # 상, 하
    dc = [0, 0, -1, 1]     # 좌, 우
    q = deque([(sr, sc)])
    visited[sr][sc] = True
    while q:
        r, c = q.popleft()
        for d in range(4):
            nr, nc = r + dr[d], c + dc[d]
            # 격자 범위 안 + 안 가봤고 + 갈 수 있는 칸(1)이면
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == 1:
                visited[nr][nc] = True
                q.append((nr, nc))
```

> 패턴: **`dr/dc` 방향 배열 + 범위 체크 + 방문 체크 + 통행 가능 체크.** 이 네 조건이 격자 탐색의 골격입니다.

---

## 대표 문제 풀이 — 타겟 넘버 (프로그래머스 43165)

> 숫자 배열 `numbers`의 각 수에 `+` 또는 `-`를 붙여 모두 더했을 때 `target`이 되는 경우의 수를 구하라.

**① 신호**: "각 수에 +/-", "되는 경우의 수" — 모든 부호 조합을 탐색
**② 패턴**: DFS (각 숫자에서 +/- 두 갈래로 깊이 탐색)

```python
def solution(numbers, target):
    answer = 0

    def dfs(idx, total):
        nonlocal answer
        if idx == len(numbers):     # 끝까지 부호를 다 정했으면
            if total == target:     # 합이 타겟이면 카운트
                answer += 1
            return
        dfs(idx + 1, total + numbers[idx])   # 이 수를 +
        dfs(idx + 1, total - numbers[idx])   # 이 수를 -

    dfs(0, 0)
    return answer
```

**검증:**

```python
print(solution([1, 1, 1, 1, 1], 3))         # 5
print(solution([4, 1, 2, 1], 4))            # 2

assert solution([1, 1, 1, 1, 1], 3) == 5
assert solution([4, 1, 2, 1], 4) == 2
print("통과 ✅")
```

> 가르칠 포인트:
> 1. **두 갈래 재귀** — 각 숫자에서 `+`와 `-` 두 경로로 dfs를 호출하면, 잎(leaf)에 도달했을 때 하나의 부호 조합이 완성됩니다. (03의 완전탐색 재귀와 동일 구조, `visited`가 없는 건 같은 칸을 다시 안 밟기 때문)
> 2. **`nonlocal answer`** — 중첩 함수에서 바깥 변수를 누적할 때 필요. (리스트를 쓰거나 반환값을 합치는 방법도 있음)

---

## 직접 풀어보기 (연습)

힌트를 보고 `TODO`를 채운 뒤 검증 셀을 실행하세요. **"최소/최단이면 BFS, 모든 경우/연결이면 DFS"**부터 판단합니다.

### 연습 1 — 섬의 개수 (DFS/BFS 둘 다 가능)

> `1`(땅)과 `0`(바다)로 된 2D 격자 `grid`에서, 상하좌우로 이어진 땅 덩어리(섬)의 개수를 구하라.
> **힌트**: 모든 칸을 돌며 아직 방문 안 한 `1`을 만나면 +1 하고, 거기서 DFS/BFS로 연결된 땅을 전부 방문 표시. "덩어리 개수 = 탐색을 새로 시작한 횟수".

```python
def solution(grid):
    # TODO: 직접 작성 (방문 표시를 잊지 마세요)
    pass

# 검증
assert solution([[1, 1, 0], [0, 1, 0], [0, 0, 1]]) == 2
assert solution([[1, 0, 1], [0, 0, 0], [1, 0, 1]]) == 4
assert solution([[0, 0], [0, 0]]) == 0
print("통과 ✅")
```

### 연습 2 — 최단 거리 미로 (BFS)

> `0`(벽)과 `1`(길)로 된 격자 `maze`에서, 왼쪽 위 `(0,0)`에서 오른쪽 아래 `(n-1,m-1)`까지 가는 **최소 칸 수**를 구하라. (시작·도착 칸 포함, 못 가면 -1)
> **힌트(BFS)**: 큐에 `(행, 열, 거리)`를 넣고 퍼뜨린다. 도착 칸을 처음 꺼내는 순간의 거리가 최단. 못 가면 -1.

```python
from collections import deque

def solution(maze):
    # TODO: BFS로 직접 작성
    pass

# 검증
assert solution([[1, 1], [0, 1]]) == 3
assert solution([[1, 0], [0, 1]]) == -1     # 대각선은 못 감
assert solution([[1, 1, 1], [0, 0, 1], [1, 1, 1]]) == 5
print("통과 ✅")
```

### 연습 3 — 네트워크 (프로그래머스 43162, 도전)

> 컴퓨터 `n`대. `computers[i][j]==1`이면 i와 j가 연결됨. 서로 연결된 컴퓨터의 **네트워크(연결 덩어리) 개수**를 구하라.
> **힌트**: 섬의 개수와 같은 구조 — 인접 행렬 버전. 방문 안 한 컴퓨터에서 DFS/BFS 시작할 때마다 +1.

```python
def solution(n, computers):
    # TODO: 직접 작성
    pass

# 검증
assert solution(3, [[1, 1, 0], [1, 1, 0], [0, 0, 1]]) == 2
assert solution(3, [[1, 1, 0], [1, 1, 1], [0, 1, 1]]) == 1
print("통과 ✅")
```

---

## 이 유형의 판단 기준 (치트시트)

| 지문에 이런 말이 나오면 | 접근 |
|------------------------|------|
| "최소 횟수 / 최단 거리 / 가장 빨리" | **BFS** (큐) |
| "연결돼 있나 / 모든 곳 방문 / 경로 존재" | **DFS** (재귀/스택) |
| "덩어리/그룹 개수" | 탐색을 새로 시작한 횟수 세기 (섬·네트워크) |
| "상하좌우로 이동" | 2D 격자 + `dr/dc` 방향 배열 |
| "모든 부호/선택 조합" | DFS 두 갈래 재귀 (타겟 넘버) |

> 빠지기 쉬운 함정: **방문 표시(`visited`)를 빠뜨리면 무한 루프**. BFS는 **큐에 넣을 때** 표시하는 게 정석.

---

## 정리

| 예제/연습 | 핵심 |
|-----------|------|
| 타겟 넘버 | DFS 두 갈래 재귀 + `nonlocal` |
| 섬의 개수 | 격자 탐색, 덩어리 = 시작 횟수 |
| 최단 거리 미로 | BFS (거리 함께 전파) |
| 네트워크 | 인접 행렬 연결 덩어리 |

> 핵심 한 줄: **최단/최소면 BFS(큐), 연결/모든경우면 DFS(재귀) — 그리고 항상 `visited`.**