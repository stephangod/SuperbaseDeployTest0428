from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
#추가
from urllib.parse import quote_plus

#추가2
from dotenv import load_dotenv
load_dotenv() 

# ⭐ 변경된 부분: MariaDB URL에서 Supabase PostgreSQL URL로 교체
# 보안을 위해 환경변수 사용을 권장하며, 비밀번호 부분은 실제 비밀번호로 채워야 합니다.
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))  # 특수문자 안전하게 인코딩
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")



SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# 한글 주석: DATABASE_URL이 None이면 서버 실행을 중단하고 에러 메시지를 보여줍니다.
if SQLALCHEMY_DATABASE_URL is None:
    raise ValueError("에러: .env 파일에 DATABASE_URL 설정이 누락되었습니다.")

# ⭐ 변경된 부분: PostgreSQL 최적화 엔진 설정
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
) # 한글 주석: pool_pre_ping은 연결 유효성을 검사하여 'Connection Lost' 에러를 방지합니다.

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()