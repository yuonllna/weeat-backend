import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

# 데이터베이스 설정
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://username:password@localhost/weeat_db"
)

# 비동기 엔진 생성 - debug_db.py와 동일한 설정
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 개발 환경에서 SQL 로그 출력
    pool_pre_ping=True,
    pool_size=1,  # 연결 풀 크기를 1로 제한
    max_overflow=0,  # 오버플로우 연결 없음
    pool_timeout=10,  # 연결 대기 시간
    pool_recycle=300,
)

# 비동기 세션 팩토리 - 더 안전한 설정
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# 데이터베이스 의존성 - 단순화된 방식
async def get_database() -> AsyncGenerator[AsyncSession, None]:
    # debug_db.py와 동일한 방식으로 단순하게 세션 생성
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# 환경 변수 (인증 관련 설정 제거됨)

# API 설정
API_V1_STR = "/api/v1"
PROJECT_NAME = "WeEat API"

# CORS 설정
BACKEND_CORS_ORIGINS = os.getenv(
    "BACKEND_CORS_ORIGINS",
    "http://localhost:3000,http://localhost:8080"
).split(",")
