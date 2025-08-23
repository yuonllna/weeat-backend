from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class ReviewBase(BaseModel):
    rating: int
    content: Optional[str] = None
    visited_at: Optional[date] = None
    menu: Optional[str] = None
    price_text: Optional[str] = None
    photo_url: Optional[str] = None

class ReviewCreate(ReviewBase):
    place_id: int
    user_id: Optional[int] = None

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    content: Optional[str] = None
    visited_at: Optional[date] = None
    menu: Optional[str] = None
    price_text: Optional[str] = None
    photo_url: Optional[str] = None

class ReviewOut(ReviewBase):
    id: int
    place_id: int
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True
