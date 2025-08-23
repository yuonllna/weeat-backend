import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

# 데이터베이스 설정
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://username:password@localhost/weeat_db"
)

# 비동기 엔진 생성
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 개발 환경에서 SQL 로그 출력
    pool_pre_ping=True,
    pool_recycle=300,
)

# 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 데이터베이스 의존성
async def get_database() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 환경 변수
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# API 설정
API_V1_STR = "/api/v1"
PROJECT_NAME = "WeEat API"

# CORS 설정
BACKEND_CORS_ORIGINS = os.getenv(
    "BACKEND_CORS_ORIGINS",
    "http://localhost:3000,http://localhost:8080"
).split(",")
