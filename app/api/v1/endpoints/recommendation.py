from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_database
from app.crud.place import get_places
from app.crud.menu import get_menus_by_place
from app.models.place import Place
from app.models.menu import Menu
from app.schemas.place import PlaceOut
from app.schemas.menu import MenuOut
from typing import List, Dict, Any
import random

router = APIRouter()

@router.get("/")
async def get_recommendations(
    count: int = Query(3, description="추천 개수", ge=1, le=10),
    db: AsyncSession = Depends(get_database)
):
    """가게 + 메뉴 랜덤 추천 (카테고리 중복 없이)"""
    # 모든 가게 조회
    places = await get_places(db)
    
    if not places:
        return []
    
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
        menus = await get_menus_by_place(db, place.id)
        
        # 랜덤 메뉴 선택 (메뉴가 있는 경우)
        selected_menu = None
        if menus:
            selected_menu = random.choice(menus)
        
        # 추천 결과 구성
        recommendation = {
            "place": PlaceOut.from_orm(place),
            "menu": MenuOut.from_orm(selected_menu) if selected_menu else None,
            "category": category
        }
        
        recommendations.append(recommendation)
    
    return recommendations
