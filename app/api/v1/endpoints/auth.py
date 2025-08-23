from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_database
from app.crud.user import get_user_by_email, get_user_by_social, create_user, delete_user
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserLogin, UserOut, 
    KakaoLogin, GoogleLogin, SocialLoginResponse
)
from app.api.deps import get_current_user, create_access_token
from app.core.oauth import verify_social_token
from passlib.context import CryptContext
from datetime import timedelta

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/email/sign-up", response_model=UserOut)
async def email_signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_database)
):
    """이메일 회원가입"""
    # 이메일 중복 확인
    if user_data.email:
        existing_user = await get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 이메일입니다."
            )
    
    # 비밀번호 해시화
    password_hash = None
    if user_data.password:
        password_hash = get_password_hash(user_data.password)
    
    # 사용자 생성
    user = User(
        display_name=user_data.display_name,
        email=user_data.email,
        password_hash=password_hash,
        auth_provider=user_data.auth_provider,
        auth_sub=user_data.auth_sub
    )
    
    created_user = await create_user(db, user)
    return created_user

@router.post("/email/sign-in")
async def email_signin(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_database)
):
    """이메일 로그인"""
    # 사용자 조회
    user = await get_user_by_email(db, user_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다."
        )
    
    # 비밀번호 확인
    if not user.password_hash or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다."
        )
    
    # JWT 토큰 생성
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserOut.from_orm(user)
    }

@router.post("/kakao/sign-in", response_model=SocialLoginResponse)
async def kakao_signin(
    kakao_data: KakaoLogin,
    db: AsyncSession = Depends(get_database)
):
    """카카오 소셜 로그인"""
    # 카카오 토큰 검증 및 사용자 정보 조회
    user_info = await verify_social_token("kakao", kakao_data.access_token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 카카오 토큰입니다."
        )
    
    # 기존 사용자 조회
    user = await get_user_by_social(db, "kakao", user_info["auth_sub"])
    
    if not user:
        # 새 사용자 생성
        user = User(
            display_name=user_info["display_name"],
            email=user_info.get("email"),
            auth_provider="kakao",
            auth_sub=user_info["auth_sub"]
        )
        user = await create_user(db, user)
    
    # JWT 토큰 생성
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return SocialLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.from_orm(user)
    )

@router.post("/google/sign-in", response_model=SocialLoginResponse)
async def google_signin(
    google_data: GoogleLogin,
    db: AsyncSession = Depends(get_database)
):
    """구글 소셜 로그인"""
    # 구글 토큰 검증 및 사용자 정보 조회
    user_info = await verify_social_token("google", google_data.id_token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 구글 토큰입니다."
        )
    
    # 기존 사용자 조회
    user = await get_user_by_social(db, "google", user_info["auth_sub"])
    
    if not user:
        # 새 사용자 생성
        user = User(
            display_name=user_info["display_name"],
            email=user_info.get("email"),
            auth_provider="google",
            auth_sub=user_info["auth_sub"]
        )
        user = await create_user(db, user)
    
    # JWT 토큰 생성
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return SocialLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.from_orm(user)
    )

@router.delete("/user")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """회원 탈퇴"""
    # 소셜 로그인 사용자인지 확인
    if current_user.auth_provider:
        # 소셜 로그인 사용자: 데이터베이스에서만 삭제
        # (소셜 계정과의 연결 해제는 프론트엔드에서 처리)
        await delete_user(db, current_user.id)
        return {
            "message": "회원 탈퇴가 완료되었습니다.",
            "note": f"{current_user.auth_provider} 계정과의 연결을 해제하려면 해당 서비스에서 앱 권한을 해제하세요."
        }
    else:
        # 이메일 로그인 사용자: 일반 삭제
        await delete_user(db, current_user.id)
        return {"message": "회원 탈퇴가 완료되었습니다."}

@router.post("/user/revoke-social")
async def revoke_social_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """소셜 계정 연결 해제 (회원탈퇴 전)"""
    if not current_user.auth_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="소셜 로그인 사용자가 아닙니다."
        )
    
    # 소셜 계정 정보만 삭제 (사용자 계정은 유지)
    current_user.auth_provider = None
    current_user.auth_sub = None
    
    await db.commit()
    await db.refresh(current_user)
    
    return {
        "message": "소셜 계정 연결이 해제되었습니다.",
        "note": "이제 이메일과 비밀번호로 로그인할 수 있습니다."
    }
