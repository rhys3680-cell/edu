# 유형 08 — 그래프 (최단경로)

> **대상**: DFS/BFS(유형 05)와 우선순위 큐 개념을 접한 단계. 코딩테스트 유형 정리의 **마지막**.
> **목표**: 그래프를 자료구조로 표현하고, **최단경로**를 상황에 맞는 알고리즘으로 구하기 — 가중치 없으면 **BFS**, 가중치 있으면 **다익스트라**.

05의 BFS가 "한 칸씩 퍼지는 최단거리"였다면, 여기선 **간선마다 비용(가중치)이 다른** 경우로 확장합니다. 핵심은 **"가중치 유무로 알고리즘이 갈린다"**는 것입니다.

---

## 0) 최단경로 — 무엇을 언제 쓰나

| 상황 | 알고리즘 | 도구 |
|------|----------|------|
| 간선 가중치가 **모두 같음**(=1) | **BFS** | `deque` |
| 간선 가중치가 **다름**(양수) | **다익스트라** | `heapq` (우선순위 큐) |
| 음수 간선이 있음 | 벨만-포드 | (코테 빈도 낮음) |
| 모든 쌍 최단거리 | 플로이드-워셜 | 3중 for (n이 작을 때) |

> 가장 중요한 분기: **"가중치가 다 같으면 BFS, 다르면 다익스트라."** 코테 최단경로의 90%는 이 둘입니다.

---

## 1) 그래프 표현 — 인접 리스트

대부분 **인접 리스트**(각 노드의 이웃 목록)로 표현합니다. 노드 수가 많고 간선이 적을 때 효율적이죠.

```python
from collections import defaultdict

# 무방향 그래프: 간선 (1,2), (1,3), (2,4)
graph = defaultdict(list)
edges = [(1, 2), (1, 3), (2, 4)]
for a, b in edges:
    graph[a].append(b)
    graph[b].append(a)        # 무방향이라 양쪽 다

# graph[1] == [2, 3], graph[2] == [1, 4]

# 가중치 그래프: (출발, 도착, 비용)
wgraph = defaultdict(list)
for a, b, w in [(1, 2, 4), (1, 3, 1), (3, 2, 2)]:
    wgraph[a].append((b, w))  # (이웃, 비용)
```

> 패턴: **무방향이면 양쪽에 추가**, 가중치가 있으면 `(이웃, 비용)` 튜플로 저장.

---

## 2) 가중치 없는 최단거리 — BFS

간선 비용이 모두 1이면, BFS로 "출발점에서 각 노드까지의 거리"를 한 번에 구합니다.

```python
from collections import deque

def bfs_dist(graph, start, n):
    dist = [-1] * (n + 1)     # -1 = 아직 방문 안 함
    dist[start] = 0
    q = deque([start])
    while q:
        node = q.popleft()
        for nxt in graph[node]:
            if dist[nxt] == -1:           # 처음 도달했을 때가 최단
                dist[nxt] = dist[node] + 1
                q.append(nxt)
    return dist
```

> 핵심: **`dist`를 방문 체크 겸 거리 저장으로 겸용.** 처음 도달한 순간이 최단거리 (BFS의 성질).

---

## 3) 가중치 있는 최단거리 — 다익스트라

간선 비용이 다르면, **"지금까지 가장 가까운 노드부터"** 처리해야 합니다 → 우선순위 큐(`heapq`).

```python
import heapq

def dijkstra(wgraph, start, n):
    INF = float('inf')
    dist = [INF] * (n + 1)
    dist[start] = 0
    pq = [(0, start)]          # (누적 비용, 노드)
    while pq:
        cost, node = heapq.heappop(pq)   # 가장 가까운 노드 꺼냄
        if cost > dist[node]:            # 이미 더 짧게 온 적 있으면 skip
            continue
        for nxt, w in wgraph[node]:
            new_cost = cost + w
            if new_cost < dist[nxt]:     # 더 짧으면 갱신
                dist[nxt] = new_cost
                heapq.heappush(pq, (new_cost, nxt))
    return dist
```

> 핵심 3가지:
> 1. **`heapq`는 최소 힙** — `(비용, 노드)` 튜플을 넣으면 비용이 가장 작은 것이 먼저 나옴.
> 2. **`if cost > dist[node]: continue`** — 오래된(더 비싼) 항목 무시. 이게 없으면 비효율.
> 3. **양수 가중치 전제** — 음수 간선엔 다익스트라가 틀립니다.

---

## 대표 문제 풀이 — 가장 먼 노드 (프로그래머스 49189)

> 노드 `n`개, 양방향 간선 `edge`. 1번 노드에서 **가장 멀리 떨어진 노드의 개수**를 구하라. (간선 비용은 모두 1)

**① 신호**: "간선 비용 모두 1", "1번에서 가장 먼" — 가중치 없는 최단거리
**② 패턴**: BFS (1번에서 각 노드까지 거리 → 최댓값인 노드 수 세기)

```python
from collections import deque, defaultdict

def solution(n, edge):
    graph = defaultdict(list)
    for a, b in edge:
        graph[a].append(b)
        graph[b].append(a)        # 양방향

    dist = [-1] * (n + 1)
    dist[1] = 0
    q = deque([1])
    while q:
        node = q.popleft()
        for nxt in graph[node]:
            if dist[nxt] == -1:
                dist[nxt] = dist[node] + 1
                q.append(nxt)

    max_dist = max(dist[1:])              # 가장 먼 거리
    return dist[1:].count(max_dist)       # 그 거리인 노드 개수
```

**검증:**

```python
print(solution(6, [[3, 6], [4, 3], [3, 2], [1, 3], [1, 2], [2, 4], [5, 2]]))  # 3

assert solution(6, [[3, 6], [4, 3], [3, 2], [1, 3], [1, 2], [2, 4], [5, 2]]) == 3
print("통과 ✅")
```

> 가르칠 포인트:
> 1. **간선 비용이 1이라 다익스트라가 아니라 BFS** — "비용 모두 1"을 보고 알고리즘을 고르는 게 핵심.
> 2. **거리 배열에서 최댓값 → 그 개수** — `max`로 가장 먼 거리를 구하고 `count`로 셈. (`dist[1:]`은 1번 노드 자신을 제외하기 위함이 아니라 0번 인덱스 더미를 빼는 것)

---

## 직접 풀어보기 (연습)

힌트를 보고 `TODO`를 채운 뒤 검증 셀을 실행하세요. **"가중치가 같으면 BFS, 다르면 다익스트라"**부터 판단합니다.

### 연습 1 — 모든 노드까지의 거리 (BFS)

> 노드 `n`개(1~n), 양방향 간선 `edges`(비용 1). 1번에서 각 노드까지의 **최단 거리 리스트**를 반환하라. (`dist[i]` = 1에서 i까지 거리, 못 가면 -1, dist[0]은 무시용 -1)
> **힌트**: 위의 BFS 틀 그대로. `dist`를 방문 체크 겸용으로.

```python
from collections import deque, defaultdict

def solution(n, edges):
    # TODO: BFS로 dist 배열 채우기
    pass

# 검증
assert solution(4, [[1, 2], [2, 3], [3, 4]]) == [-1, 0, 1, 2, 3]
assert solution(3, [[1, 2]]) == [-1, 0, 1, -1]   # 3번은 고립
print("통과 ✅")
```

### 연습 2 — 가중치 그래프 최단 비용 (다익스트라)

> 노드 `n`개(1~n), 방향 간선 `edges`가 `[출발, 도착, 비용]` 리스트로 주어진다. `start`에서 각 노드까지의 **최소 비용 리스트**를 반환하라. (못 가면 무한대 대신 -1, dist[0]은 -1)
> **힌트**: 위 다익스트라 틀. 마지막에 `INF`를 -1로 바꿔 반환.

```python
import heapq
from collections import defaultdict

def solution(n, edges, start):
    # TODO: 다익스트라로 직접 작성
    pass

# 검증
assert solution(4, [[1, 2, 1], [1, 3, 5], [2, 3, 1], [3, 4, 2]], 1) == [-1, 0, 1, 2, 4]
assert solution(2, [[1, 2, 7]], 1) == [-1, 0, 7]
print("통과 ✅")
```

### 연습 3 — 배달 (프로그래머스 12978, 도전)

> 마을 `N`개(1번이 시작), 도로 `road`가 `[a, b, 비용]`(양방향). 1번에서 **시간 `K` 이내**에 도달 가능한 마을의 개수를 구하라.
> **힌트**: 1번에서 다익스트라로 모든 마을까지 최소 비용을 구한 뒤, `K` 이하인 마을을 센다. 같은 두 마을 사이 도로가 여러 개일 수 있음(다익스트라가 자연히 최소를 고름).

```python
import heapq
from collections import defaultdict

def solution(N, road, K):
    # TODO: 다익스트라 후 K 이하 개수 세기
    pass

# 검증
assert solution(5, [[1, 2, 1], [2, 3, 3], [5, 2, 2], [1, 5, 1], [5, 3, 1], [5, 4, 2]], 3) == 5
assert solution(6, [[1, 2, 1], [1, 3, 2], [2, 3, 2], [3, 4, 3], [3, 5, 2], [3, 5, 3], [5, 6, 1]], 4) == 4
print("통과 ✅")
```

---

## 이 유형의 판단 기준 (치트시트)

| 지문에 이런 말이 나오면 | 접근 |
|------------------------|------|
| "간선 비용이 모두 같다 / 1" | **BFS** |
| "거리/비용/시간이 간선마다 다름" | **다익스트라** (`heapq`) |
| "가장 먼 / 도달 가능한 개수" | 최단거리 구한 뒤 집계 |
| "모든 쌍 사이 거리" (n 작음) | 플로이드-워셜 |
| 그래프를 만들 때 | 인접 리스트 `defaultdict(list)`, 무방향이면 양쪽 |

> 최단경로의 첫 판단: **"간선 가중치가 다 같은가?"** → 같으면 BFS, 다르면 다익스트라. 이 한 줄이 유형 08의 핵심입니다.

---

## 정리

| 예제/연습 | 알고리즘 |
|-----------|----------|
| 가장 먼 노드 | BFS 최단거리 + 집계 |
| 모든 노드까지 거리 | BFS |
| 가중치 최단 비용 | 다익스트라 |
| 배달 | 다익스트라 + K 이하 집계 |

> 핵심 한 줄: **최단경로 = (그래프를 인접 리스트로) → (가중치 같으면 BFS / 다르면 다익스트라) → (거리 배열로 집계).**

---

## 🎉 코딩테스트 유형 정리 완료 (00~08)

축하합니다 — 코딩테스트 핵심 유형 9개를 모두 마쳤습니다.

| # | 유형 | 핵심 무기 |
|---|------|----------|
| 00 | Lv.0 문법 패턴 | 지문 → 코드 번역 |
| 01 | 자료구조 | 스택/큐/해시 |
| 02 | 정렬 | `key` 설계 |
| 03 | 완전탐색 | itertools/재귀 |
| 04 | 그리디 | 손해 없는 선택 |
| 05 | DFS/BFS | 탐색 + visited |
| 06 | 이분탐색 | 파라메트릭 서치 |
| 07 | DP | 점화식 |
| 08 | 그래프 | BFS/다익스트라 |

> 다음 단계는 로드맵의 **SQL → 데이터 핸들링 → ML → 캐글 프로젝트**로 이어집니다.