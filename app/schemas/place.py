from pydantic import BaseModel
from typing import Optional

class PlaceBase(BaseModel):
    name: str
    category: str
    distance_note: Optional[str] = None
    address: Optional[str] = None
    hero_image_url: Optional[str] = None

class PlaceCreate(PlaceBase):
    pass

class PlaceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    distance_note: Optional[str] = None
    address: Optional[str] = None
    hero_image_url: Optional[str] = None

class PlaceOut(PlaceBase):
    id: int

    class Config:
        orm_mode = True
