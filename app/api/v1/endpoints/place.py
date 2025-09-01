from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import get_database
from app.crud.place import get_places, get_place, get_places_by_category
from app.crud.menu import get_menus_by_place
from app.crud.review import get_reviews_by_place
from app.schemas.place import PlaceOut
from app.schemas.menu import MenuOut
from app.schemas.review import ReviewOut
from typing import List, Optional
import logging
import os
from dotenv import load_dotenv

# 로깅 설정
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[PlaceOut])
async def get_all_places(
    category: Optional[str] = Query(None, description="카테고리별 필터링")
):
    """가게 조회 (카테고리별 필터링 가능) - 직접 연결 방식"""
    try:
        logger.info("직접 연결 방식으로 가게 조회 시작...")
        load_dotenv()
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="데이터베이스 URL이 설정되지 않았습니다."
            )
        
        # debug_db.py와 동일한 엔진 설정
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=0,
            pool_timeout=10
        )
        
        async with engine.begin() as conn:
            # places 테이블 데이터 직접 조회
            if category:
                result = await conn.execute(
                    text("SELECT * FROM places WHERE category = :category"),
                    {"category": category}
                )
            else:
                result = await conn.execute(text("SELECT * FROM places"))
            
            places_data = result.fetchall()
            
            # PlaceOut 형태로 변환
            places = []
            for row in places_data:
                place = PlaceOut(
                    id=row[0],
                    name=row[1],
                    category=row[2],
                    distance_note=row[3],
                    address=row[4],
                    hero_image_url=row[5]
                )
                places.append(place)
            
            await engine.dispose()
            logger.info(f"가게 조회 성공: {len(places)}개")
            return places
            
    except Exception as e:
        logger.error(f"가게 조회 실패: {str(e)}")
        if 'engine' in locals():
            await engine.dispose()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"가게 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/{place_id}", response_model=PlaceOut)
async def get_place_detail(
    place_id: int,
    db: AsyncSession = Depends(get_database)
):
    """가게 상세 조회"""
    try:
        place = await get_place(db, place_id)
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="가게를 찾을 수 없습니다."
            )
        return place
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"가게 상세 조회 실패 (ID: {place_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"가게 상세 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/{place_id}/reviews", response_model=List[ReviewOut])
async def get_place_reviews(
    place_id: int,
    db: AsyncSession = Depends(get_database)
):
    """가게 리뷰 조회"""
    try:
        # 가게 존재 확인
        place = await get_place(db, place_id)
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="가게를 찾을 수 없습니다."
            )
        
        reviews = await get_reviews_by_place(db, place_id)
        return reviews
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"가게 리뷰 조회 실패 (ID: {place_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"리뷰 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/{place_id}/menus", response_model=List[MenuOut])
async def get_place_menus(
    place_id: int,
    db: AsyncSession = Depends(get_database)
):
    """가게 메뉴 조회"""
    try:
        # 가게 존재 확인
        place = await get_place(db, place_id)
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="가게를 찾을 수 없습니다."
            )
        
        menus = await get_menus_by_place(db, place_id)
        return menus
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"가게 메뉴 조회 실패 (ID: {place_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 조회 중 오류가 발생했습니다: {str(e)}"
        )
