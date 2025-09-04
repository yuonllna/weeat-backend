from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ReviewBase(BaseModel):
    phone_number: str
    rating: int
    content: Optional[str] = None
    photo_urls: Optional[str] = None  # JSON 배열 형태
    
    class Config:
        # 추가 필드 허용 (프론트엔드에서 예상치 못한 필드가 와도 무시)
        extra = "ignore"

class ReviewCreate(ReviewBase):
    pass  # place_id는 URL 경로에서 받음

class ReviewUpdate(BaseModel):
    phone_number: Optional[str] = None
    rating: Optional[int] = None
    content: Optional[str] = None
    photo_urls: Optional[str] = None

class ReviewOut(ReviewBase):
    id: int
    place_id: int
    created_at: datetime

    class Config:
        orm_mode = True
