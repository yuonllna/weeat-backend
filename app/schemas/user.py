from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    display_name: str
    email: Optional[EmailStr] = None
    auth_provider: Optional[str] = None
    auth_sub: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = None

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 새로운 소셜 로그인 스키마들
class KakaoLogin(BaseModel):
    access_token: str

class GoogleLogin(BaseModel):
    id_token: str

class SocialLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: 'UserOut'

class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserInDB(UserBase):
    id: int
    password_hash: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

# 순환 참조 해결
SocialLoginResponse.model_rebuild()
