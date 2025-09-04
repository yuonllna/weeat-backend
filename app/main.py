from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.routers import api_router
from app.core.config import get_database
from app.models import Base
from sqlalchemy.ext.asyncio import AsyncEngine
import os

app = FastAPI(
    title="WeEat API",
    description="맛집 추천 및 리뷰 서비스 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static 파일 서빙 설정
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# API 라우터 등록
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "WeEat API에 오신 것을 환영합니다!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 데이터베이스 초기화 (선택사항)
@app.on_event("startup")
async def startup_event():
    # 데이터베이스 연결 확인
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # 데이터베이스 연결 종료
    pass
