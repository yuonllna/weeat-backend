from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_database
from app.crud.place import get_places, get_place, get_places_by_category
from app.crud.menu import get_menus_by_place
from app.crud.review import get_reviews_by_place
from app.schemas.place import PlaceOut
from app.schemas.menu import MenuOut
from app.schemas.review import ReviewOut
from typing import List, Optional

router = APIRouter()

@router.get("/", response_model=List[PlaceOut])
async def get_all_places(
    category: Optional[str] = Query(None, description="카테고리별 필터링"),
    db: AsyncSession = Depends(get_database)
):
    """가게 조회 (카테고리별 필터링 가능)"""
    if category:
        places = await get_places_by_category(db, category)
    else:
        places = await get_places(db)
    
    return places

@router.get("/{place_id}", response_model=PlaceOut)
async def get_place_detail(
    place_id: int,
    db: AsyncSession = Depends(get_database)
):
    """가게 상세 조회"""
    place = await get_place(db, place_id)
    if not place:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다."
        )
    return place

@router.get("/{place_id}/reviews", response_model=List[ReviewOut])
async def get_place_reviews(
    place_id: int,
    db: AsyncSession = Depends(get_database)
):
    """가게 리뷰 조회"""
    # 가게 존재 확인
    place = await get_place(db, place_id)
    if not place:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다."
        )
    
    reviews = await get_reviews_by_place(db, place_id)
    return reviews

@router.get("/{place_id}/menus", response_model=List[MenuOut])
async def get_place_menus(
    place_id: int,
    db: AsyncSession = Depends(get_database)
):
    """가게 메뉴 조회"""
    # 가게 존재 확인
    place = await get_place(db, place_id)
    if not place:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다."
        )
    
    menus = await get_menus_by_place(db, place_id)
    return menus
