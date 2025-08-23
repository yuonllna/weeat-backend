from pydantic import BaseModel
from typing import Optional

class MenuBase(BaseModel):
    name: str
    price: Optional[int] = None

class MenuCreate(MenuBase):
    place_id: int

class MenuUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None

class MenuOut(MenuBase):
    id: int
    place_id: int

    class Config:
        orm_mode = True
