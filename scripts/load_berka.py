"""
Berka(체코 은행, PKDD'99) 데이터셋을 Supabase(PostgreSQL)에 적재하는 스크립트.

사용법:
    1. Kaggle에서 데이터 받기 (data/berka/*.csv 생성):
         uv run kaggle datasets download -d marceloventura/the-berka-dataset -p data/berka
         cd data/berka && unzip the-berka-dataset.zip
    2. .env 파일에 Supabase 연결 URL 넣기 (대시보드 > Settings > Database):
         SUPABASE_DB_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
       (Session pooler URL 권장 — 포트 5432 또는 6543)
    3. 실행:
         uv run python scripts/load_berka.py

주의:
    - trans 테이블이 106만 행이라 적재에 수 분 걸릴 수 있음 (chunksize로 분할 전송).
    - if_exists="replace"라 재실행하면 테이블을 새로 만듦 (멱등).
    - .env는 커밋 금지 (.gitignore에 이미 포함).
"""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# ── 설정 ────────────────────────────────────────────────────────────
load_dotenv()

DB_URL = os.environ.get("SUPABASE_DB_URL")
if not DB_URL:
    raise SystemExit(
        "SUPABASE_DB_URL이 없습니다. .env에 Supabase 연결 URL을 넣어주세요.\n"
        "예: SUPABASE_DB_URL=postgresql://postgres:PW@HOST:5432/postgres"
    )

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "berka"
engine = create_engine(DB_URL)


def yymmdd(series: pd.Series) -> pd.Series:
    """YYMMDD 정수(930101)를 날짜(1993-01-01)로 변환. 앞 6자리만 사용."""
    s = series.astype(str).str.zfill(6).str[:6]
    return pd.to_datetime(s, format="%y%m%d", errors="coerce")


def load_csv(name: str) -> pd.DataFrame:
    # low_memory=False: 큰 파일(trans)에서 열 타입이 섞였다는 경고 방지
    return pd.read_csv(DATA_DIR / f"{name}.csv", sep=";", low_memory=False)


# ── 테이블별 적재 ───────────────────────────────────────────────────
def load_district():
    df = load_csv("district")
    # 헤더가 A1~A16이라 실제 컬럼명으로 매핑
    df.columns = [
        "district_id", "district_name", "region", "population",
        "n_muni_lt499", "n_muni_500_1999", "n_muni_2000_9999", "n_muni_gt10000",
        "n_cities", "urban_ratio", "avg_salary",
        "unemployment_95", "unemployment_96",
        "entrepreneurs_per_1000", "crimes_95", "crimes_96",
    ]
    # A12(unemp_95), A15(crimes_95)에 '?' 결측 1개씩 → 숫자 변환(coerce)
    for col in ["unemployment_95", "crimes_95"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_account():
    df = load_csv("account")
    df["date"] = yymmdd(df["date"])   # 계좌 개설일
    return df


def load_client():
    df = load_csv("client")
    return df   # birth_number는 원본 유지(성별·생일 인코딩, 문자열)


def load_disp():
    return load_csv("disp")   # 계좌-고객 연결(OWNER/DISPONENT)


def load_loan():
    df = load_csv("loan")
    df["date"] = yymmdd(df["date"])   # 대출 승인일
    return df


def load_order():
    return load_csv("order")   # 이체 지시(날짜 없음)


def load_card():
    df = load_csv("card")
    df["issued"] = yymmdd(df["issued"])   # '931107 00:00:00' → 앞 6자리
    return df


def load_trans():
    df = load_csv("trans")
    df["date"] = yymmdd(df["date"])   # 거래일 (106만 행)
    return df


LOADERS = {
    "district": load_district,   # 다른 테이블이 참조하므로 먼저
    "account": load_account,
    "client": load_client,
    "disp": load_disp,
    "loan": load_loan,
    "order": load_order,
    "card": load_card,
    "trans": load_trans,
}


def main():
    for name, loader in LOADERS.items():
        print(f"[{name}] 읽는 중...", end=" ", flush=True)
        df = loader()
        print(f"{len(df):,}행 → 적재 중...", end=" ", flush=True)
        # trans는 커서 chunk로 분할 전송(메모리·타임아웃 완화)
        df.to_sql(
            name, engine, if_exists="replace", index=False,
            chunksize=10_000, method="multi",
        )
        print("완료 ✅")
    print("\n모든 테이블 적재 완료.")


if __name__ == "__main__":
    main()