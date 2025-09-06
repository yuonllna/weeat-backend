from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routers import api_router
from app.core.config import get_database
from app.models import Base
from sqlalchemy.ext.asyncio import AsyncEngine

app = FastAPI(
    title="WeEat API",
    description="맛집 추천 및 리뷰 서비스 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite React 개발용
        "http://localhost:3000",      # Create React App 개발용 (백업)
        "https://weeat.site",         # 메인 도메인
        "https://www.weeat.site",     # www 서브도메인
        "https://api.weeat.site",     # API 서브도메인 (HTTPS)
        "http://weeat.site"          # HTTP 메인 도메인
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Static 파일 서빙 설정 제거 (S3 사용으로 변경)

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
