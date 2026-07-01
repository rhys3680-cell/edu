-- ────────────────────────────────────────────────────────────────
-- Berka 실습용 읽기 전용(read-only) 계정 생성
--
-- 목적: 학생들에게는 SELECT만 가능한 계정을 주어, 비밀번호가 새도
--       데이터 변경/삭제가 불가능하게 한다. (강사 계정과 분리)
--
-- 사용법: Supabase 대시보드 > SQL Editor 에 붙여넣고 실행.
--        아래 'CHANGE_ME_강한비밀번호'를 실제 비밀번호로 바꿀 것.
--        (적재(load_berka.py)를 먼저 끝낸 뒤 실행 — 테이블이 있어야 권한 부여됨)
-- ────────────────────────────────────────────────────────────────

-- 1) 읽기 전용 역할(role) 생성
--    이미 있으면 에러 나므로, 다시 만들 땐 먼저 DROP ROLE student; 실행
CREATE ROLE student LOGIN PASSWORD 'CHANGE_ME_강한비밀번호';

-- 2) 데이터베이스·스키마 접근 허용
GRANT CONNECT ON DATABASE postgres TO student;
GRANT USAGE ON SCHEMA public TO student;

-- 3) 현재 존재하는 모든 테이블에 SELECT 권한
GRANT SELECT ON ALL TABLES IN SCHEMA public TO student;

-- 4) (선택) 앞으로 생길 테이블에도 자동으로 SELECT 부여 — 재적재 대비 편의.
--    ⚠️ Supabase SQL Editor에서는 ALTER DEFAULT PRIVILEGES가 문법 에러를 낼 수 있음
--       (에디터가 문을 래핑하는 특성). 에러 나면 이 줄은 그냥 생략할 것.
--    생략해도 문제 없음: 재적재하면 아래 3번 GRANT만 한 번 더 실행하면 된다.
-- ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT TO student;

-- ────────────────────────────────────────────────────────────────
-- 수업 외 시간에 계정 잠그기 / 다시 열기
--   (접속 자체를 막아, 수업 시간에만 열어둔다)
-- ────────────────────────────────────────────────────────────────
-- 잠그기:  ALTER ROLE student NOLOGIN;
-- 열기:    ALTER ROLE student LOGIN;

-- 계정 완전 삭제(다시 만들 때):
--   REASSIGN OWNED BY student TO postgres;  -- 소유물 있으면
--   DROP OWNED BY student;
--   DROP ROLE student;

-- ────────────────────────────────────────────────────────────────
-- 학생에게 공유할 접속 정보 (읽기 전용)
--   host:     <Supabase 프로젝트 호스트>
--   port:     5432 (또는 pooler 6543)
--   database: postgres
--   user:     student
--   password: 위에서 정한 비밀번호
--
--   ⚠️ 강사(postgres) 비밀번호는 절대 공유하지 말 것.
-- ────────────────────────────────────────────────────────────────