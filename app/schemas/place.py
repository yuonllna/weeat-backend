from pydantic import BaseModel
from typing import Optional, List
from .menu import MenuOut

class PlaceBase(BaseModel):
    name: str
    category: str
    distance_note: Optional[str] = None
    address: Optional[str] = None
    hero_image_url: Optional[str] = None
    budget_range: Optional[int] = None  # 예산 범위 (원 단위)

class PlaceCreate(PlaceBase):
    pass

class PlaceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    distance_note: Optional[str] = None
    address: Optional[str] = None
    hero_image_url: Optional[str] = None
    budget_range: Optional[int] = None

class PlaceOut(PlaceBase):
    id: int
    rating: float = 0.0  # 계산된 평균 평점 (소수점 1자리, 기본값 0.0)
    review_count: int = 0  # 리뷰 개수

    class Config:
        from_attributes = True

class PlaceDetailOut(PlaceOut):
    menus: List[MenuOut] = []  # 해당 가게의 메뉴 목록

    class Config:
        from_attributes = True
