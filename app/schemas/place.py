from pydantic import BaseModel
from typing import Optional

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

    class Config:
        orm_mode = True
