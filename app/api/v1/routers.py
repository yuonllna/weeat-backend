from fastapi import APIRouter
from app.api.v1.endpoints import place, review, recommendation

api_router = APIRouter()

# 장소 관련 라우터
api_router.include_router(
    place.router,
    prefix="/places",
    tags=["장소"]
)

# 리뷰 관련 라우터
api_router.include_router(
    review.router,
    prefix="/places",  # /places/{place_id}/reviews 형태로 연결
    tags=["리뷰"]
)

# 추천 관련 라우터
api_router.include_router(
    recommendation.router,
    prefix="/recommendations",
    tags=["추천"]
)
