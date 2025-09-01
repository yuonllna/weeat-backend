from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import get_database
from app.crud.place import get_places
from app.crud.menu import get_menus_by_place
from app.models.place import Place
from app.models.menu import Menu
from app.schemas.place import PlaceOut
from app.schemas.menu import MenuOut
from typing import List, Dict, Any
import random
import logging
import os
from dotenv import load_dotenv

# 로깅 설정
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def get_recommendations(
    count: int = Query(3, description="추천 개수", ge=1, le=10)
):
    """가게 + 메뉴 랜덤 추천 (카테고리 중복 없이) - 직접 연결 방식"""
    try:
        logger.info(f"직접 연결 방식으로 추천 조회 시작 (개수: {count})...")
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
            # 모든 가게 조회
            result = await conn.execute(text("SELECT * FROM places"))
            places_data = result.fetchall()
            
            if not places_data:
                await engine.dispose()
                return []
            
            # Place 객체로 변환
            places = []
            for row in places_data:
                place = Place(
                    id=row[0],
                    name=row[1],
                    category=row[2],
                    distance_note=row[3],
                    address=row[4],
                    hero_image_url=row[5],
                    budget_range=row[6]  # budget_range 필드 추가
                )
                places.append(place)
            
            # 카테고리별로 가게 그룹화
            category_places: Dict[str, List[Place]] = {}
            for place in places:
                if place.category not in category_places:
                    category_places[place.category] = []
                category_places[place.category].append(place)
            
            # 카테고리 중복 없이 랜덤 선택
            available_categories = list(category_places.keys())
            selected_categories = random.sample(
                available_categories, 
                min(count, len(available_categories))
            )
            
            recommendations = []
            
            for category in selected_categories:
                # 해당 카테고리에서 랜덤 가게 선택
                place = random.choice(category_places[category])
                
                # 해당 가게의 메뉴들 조회
                menu_result = await conn.execute(
                    text("SELECT * FROM menus WHERE place_id = :place_id"),
                    {"place_id": place.id}
                )
                menus_data = menu_result.fetchall()
                
                # Menu 객체로 변환
                menus = []
                for menu_row in menus_data:
                    menu = Menu(
                        id=menu_row[0],
                        place_id=menu_row[1],
                        name=menu_row[2],
                        price=menu_row[3]
                    )
                    menus.append(menu)
                
                # 랜덤 메뉴 선택 (메뉴가 있는 경우)
                selected_menu = None
                if menus:
                    selected_menu = random.choice(menus)
                
                # 해당 가게의 평균 평점과 리뷰 수 계산
                rating_result = await conn.execute(
                    text("SELECT AVG(rating), COUNT(*) FROM reviews WHERE place_id = :place_id"),
                    {"place_id": place.id}
                )
                rating_data = rating_result.fetchone()
                avg_rating = rating_data[0]
                review_count = rating_data[1]
                
                # 평점이 없으면 0.0, 있으면 소수점 1자리로 반올림
                rating = round(float(avg_rating), 1) if avg_rating else 0.0
                
                # 추천 결과 구성
                recommendation = {
                    "place": PlaceOut(
                        id=place.id,
                        name=place.name,
                        category=place.category,
                        distance_note=place.distance_note,
                        address=place.address,
                        hero_image_url=place.hero_image_url,
                        budget_range=place.budget_range,  # budget_range 필드 추가
                        rating=rating,  # 계산된 평균 평점
                        review_count=review_count  # 리뷰 개수
                    ),
                    "menu": MenuOut(
                        id=selected_menu.id,
                        place_id=selected_menu.place_id,
                        name=selected_menu.name,
                        price=selected_menu.price
                    ) if selected_menu else None,
                    "category": category
                }
                
                recommendations.append(recommendation)
            
            await engine.dispose()
            logger.info(f"추천 조회 성공: {len(recommendations)}개")
            return recommendations
            
    except Exception as e:
        logger.error(f"추천 조회 실패: {str(e)}")
        if 'engine' in locals():
            await engine.dispose()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"추천 조회 중 오류가 발생했습니다: {str(e)}"
        )
