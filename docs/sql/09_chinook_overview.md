# SQL 09 — 실제 DB 둘러보기 (Chinook)

> **대상**: SQL 단계를 시작하는 단계. 본격 문법(10~) 전에 "실무 DB는 어떻게 생겼나"를 먼저 체험.
> **목표**: 실제 SQLite **파일 DB**에 연결해 테이블 구조를 둘러보고, "데이터가 여러 테이블에 나뉘어 관계로 연결된다"는 감을 잡기.

10번부터는 개념을 또렷이 보여주려고 작은 샘플(`employees`/`departments`)을 쓰지만, 그 전에 **실무에 가까운 진짜 DB**를 한 번 보고 갑니다. 여기서 쓰는 **Chinook**은 가상의 **음악 상점** 데이터로, SQL 교육의 사실상 표준 샘플입니다.

---

## 0) 파일 DB에 연결하기

지금까지의 `:memory:`(임시 메모리 DB)와 달리, 실무에선 **파일로 저장된 DB**에 연결합니다. 이 프로젝트엔 `data/chinook.db` 파일이 들어 있습니다.

```python
import sqlite3
import pandas as pd

# 파일 DB에 연결 (:memory: 대신 파일 경로)
conn = sqlite3.connect("data/chinook.db")

def q(sql):
    return pd.read_sql_query(sql, conn)
```

> 차이점: `:memory:`는 노트북을 닫으면 사라지지만, **파일 DB는 디스크에 영속**합니다. 실제 서비스의 DB가 이렇게 동작합니다. (경로는 노트북 위치 기준 — 노트북이 `notebooks/sql/`에 있으면 `"../../data/chinook.db"`처럼 맞춰야 할 수 있습니다.)

---

## 1) 어떤 테이블이 있나

```python
print(q("""
    SELECT name FROM sqlite_master
    WHERE type='table'
    ORDER BY name
"""))
```

Chinook에는 11개 테이블이 있습니다:

| 테이블 | 내용 | 대략 행 수 |
|--------|------|-----------|
| `Artist` | 아티스트(가수/밴드) | 275 |
| `Album` | 앨범 | 347 |
| `Track` | 트랙(곡) | 3,503 |
| `Genre` | 장르 | 25 |
| `MediaType` | 미디어 형식 | 5 |
| `Playlist` | 재생목록 | 18 |
| `PlaylistTrack` | 재생목록-트랙 연결 | 다수 |
| `Customer` | 고객 | 59 |
| `Employee` | 직원 | 8 |
| `Invoice` | 송장(주문) | 412 |
| `InvoiceLine` | 송장 항목(주문 상세) | 2,240 |

> `sqlite_master`는 SQLite가 스키마를 저장하는 시스템 테이블입니다. "이 DB에 뭐가 있지?"를 알고 싶을 때 여기를 봅니다.

---

## 2) 테이블 안을 들여다보기

```python
# 아티스트 몇 개만
print(q("SELECT * FROM Artist LIMIT 5"))
#    ArtistId      Name
# 0         1     AC/DC
# 1         2    Accept
# 2         3 Aerosmith
# ...

# 트랙의 열 구조 (어떤 정보가 있나)
print(q("SELECT * FROM Track LIMIT 3"))
# TrackId, Name, AlbumId, GenreId, Composer, Milliseconds, UnitPrice ...
```

> `LIMIT 5`로 항상 **조금만** 먼저 봅니다. 3,503행짜리 Track을 통째로 출력하면 화면이 넘칩니다. "큰 테이블은 LIMIT으로 맛보기"가 습관.

---

## 3) 테이블이 "관계"로 연결된다 (핵심 감각)

실무 DB의 핵심은 **데이터가 한 테이블에 다 들어있지 않고, 여러 테이블에 나뉘어 ID로 연결**된다는 점입니다.

```
Artist (아티스트)
   │  ArtistId
   ▼
Album (앨범)  ── ArtistId로 Artist를 가리킴
   │  AlbumId
   ▼
Track (트랙)  ── AlbumId로 Album을 가리킴, GenreId로 Genre를 가리킴
   │  TrackId
   ▼
InvoiceLine (주문 상세) ── TrackId로 Track을, InvoiceId로 Invoice를 가리킴
   │  InvoiceId
   ▼
Invoice (송장) ── CustomerId로 Customer를 가리킴
   ▼
Customer (고객)
```

예를 들어 `Album` 테이블엔 아티스트 **이름**이 없고 `ArtistId`(숫자)만 있습니다. 이름을 보려면 `Artist` 테이블과 **연결(JOIN)**해야 합니다 — 이게 12번에서 배울 핵심입니다.

```python
# 앨범 제목 + 아티스트 이름을 함께 보려면 두 테이블을 ID로 연결
print(q("""
    SELECT Album.Title, Artist.Name
    FROM Album
    JOIN Artist ON Album.ArtistId = Artist.ArtistId
    LIMIT 3
"""))
# For Those About To Rock We Salute You | AC/DC
# Balls to the Wall                     | Accept
# Restless and Wild                     | Accept
```

> 지금은 "이렇게 연결하는구나" 정도만 느끼면 됩니다. `JOIN` 문법은 12번에서 차근히 다룹니다.

---

## 4) 맛보기 질문 몇 개

실제 DB가 있으면 이런 질문에 SQL로 답할 수 있습니다 (앞으로 배울 것들):

```python
# 장르 목록 (10: SELECT)
print(q("SELECT Name FROM Genre LIMIT 8"))
# Rock, Jazz, Metal, Alternative & Punk, ...

# 국가별 고객 수 (11: GROUP BY)
print(q("""
    SELECT Country, COUNT(*) AS 고객수
    FROM Customer
    GROUP BY Country
    ORDER BY 고객수 DESC
    LIMIT 5
"""))
# USA 13, Canada 8, France 5, Brazil 5, Germany 4
```

> 이 둘은 각각 10(SELECT)·11(GROUP BY)에서 이미 배운/배울 문법입니다. **작은 샘플로 문법을 익히고, 이렇게 실제 DB에 적용**하는 흐름입니다.

---

## 정리

| 개념 | 핵심 |
|------|------|
| 파일 DB 연결 | `sqlite3.connect("data/chinook.db")` — 영속 |
| 테이블 목록 | `SELECT name FROM sqlite_master WHERE type='table'` |
| 큰 테이블 맛보기 | 항상 `LIMIT`으로 조금만 |
| 관계 | 데이터가 여러 테이블에 나뉘고 **ID로 연결** → JOIN(12) |

> 핵심 한 줄: **실무 DB = 여러 테이블이 ID로 연결된 파일. 둘러볼 땐 `sqlite_master` + `LIMIT`, 합쳐 볼 땐 `JOIN`.**
>
> 다음(10~14)은 작은 샘플로 문법을 또렷이 익히고, 필요할 때 이 Chinook으로 실전 감각을 더합니다.