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
async def get_place_detail(place_id: int):
    """가게 상세 조회 - 직접 연결 방식"""
    try:
        logger.info(f"직접 연결 방식으로 가게 상세 조회 시작 (ID: {place_id})...")
        load_dotenv()
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="데이터베이스 URL이 설정되지 않았습니다."
            )
        
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=0,
            pool_timeout=10
        )
        
        async with engine.begin() as conn:
            # 가게 존재 확인 및 데이터 조회
            result = await conn.execute(
                text("SELECT * FROM places WHERE id = :place_id"),
                {"place_id": place_id}
            )
            place_data = result.fetchone()
            
            if not place_data:
                await engine.dispose()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="가게를 찾을 수 없습니다."
                )
            
            # PlaceOut 형태로 변환
            place = PlaceOut(
                id=place_data[0],
                name=place_data[1],
                category=place_data[2],
                distance_note=place_data[3],
                address=place_data[4],
                hero_image_url=place_data[5]
            )
            
            await engine.dispose()
            logger.info(f"가게 상세 조회 성공: {place.name}")
            return place
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"가게 상세 조회 실패 (ID: {place_id}): {str(e)}")
        if 'engine' in locals():
            await engine.dispose()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"가게 상세 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/{place_id}/reviews", response_model=List[ReviewOut])
async def get_place_reviews(place_id: int):
    """가게 리뷰 조회 - 직접 연결 방식"""
    try:
        logger.info(f"직접 연결 방식으로 가게 리뷰 조회 시작 (ID: {place_id})...")
        load_dotenv()
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="데이터베이스 URL이 설정되지 않았습니다."
            )
        
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=0,
            pool_timeout=10
        )
        
        async with engine.begin() as conn:
            # 가게 존재 확인
            place_result = await conn.execute(
                text("SELECT id FROM places WHERE id = :place_id"),
                {"place_id": place_id}
            )
            if not place_result.fetchone():
                await engine.dispose()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="가게를 찾을 수 없습니다."
                )
            
            # 리뷰 조회
            result = await conn.execute(
                text("SELECT * FROM reviews WHERE place_id = :place_id"),
                {"place_id": place_id}
            )
            reviews_data = result.fetchall()
            
            # ReviewOut 형태로 변환
            reviews = []
            for row in reviews_data:
                review = ReviewOut(
                    id=row[0],
                    place_id=row[1],
                    user_id=row[2],
                    rating=row[3],
                    comment=row[4],
                    created_at=row[5]
                )
                reviews.append(review)
            
            await engine.dispose()
            logger.info(f"가게 리뷰 조회 성공: {len(reviews)}개")
            return reviews
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"가게 리뷰 조회 실패 (ID: {place_id}): {str(e)}")
        if 'engine' in locals():
            await engine.dispose()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"리뷰 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/{place_id}/menus", response_model=List[MenuOut])
async def get_place_menus(place_id: int):
    """가게 메뉴 조회 - 직접 연결 방식"""
    try:
        logger.info(f"직접 연결 방식으로 가게 메뉴 조회 시작 (ID: {place_id})...")
        load_dotenv()
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="데이터베이스 URL이 설정되지 않았습니다."
            )
        
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=0,
            pool_timeout=10
        )
        
        async with engine.begin() as conn:
            # 가게 존재 확인
            place_result = await conn.execute(
                text("SELECT id FROM places WHERE id = :place_id"),
                {"place_id": place_id}
            )
            if not place_result.fetchone():
                await engine.dispose()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="가게를 찾을 수 없습니다."
                )
            
            # 메뉴 조회
            result = await conn.execute(
                text("SELECT * FROM menus WHERE place_id = :place_id"),
                {"place_id": place_id}
            )
            menus_data = result.fetchall()
            
            # MenuOut 형태로 변환
            menus = []
            for row in menus_data:
                menu = MenuOut(
                    id=row[0],
                    place_id=row[1],
                    name=row[2],
                    price=row[3]
                )
                menus.append(menu)
            
            await engine.dispose()
            logger.info(f"가게 메뉴 조회 성공: {len(menus)}개")
            return menus
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"가게 메뉴 조회 실패 (ID: {place_id}): {str(e)}")
        if 'engine' in locals():
            await engine.dispose()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 조회 중 오류가 발생했습니다: {str(e)}"
        )
