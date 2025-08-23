from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_database
from app.crud.review import create_review, get_review, update_review, delete_review
from app.crud.place import get_place
from app.models.user import User
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewOut, ReviewUpdate
from app.api.deps import get_current_user, get_optional_current_user
from typing import List

router = APIRouter()

@router.post("/{place_id}/reviews", response_model=ReviewOut)
async def create_place_review(
    place_id: int,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """가게 리뷰 작성"""
    # 가게 존재 확인
    place = await get_place(db, place_id)
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가게를 찾을 수 없습니다."
        )
    
    # 리뷰 데이터 검증
    if review_data.rating < 1 or review_data.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="평점은 1-5 사이의 값이어야 합니다."
        )
    
    # 리뷰 생성
    review = Review(
        place_id=place_id,
        user_id=current_user.id,
        rating=review_data.rating,
        content=review_data.content,
        visited_at=review_data.visited_at,
        menu=review_data.menu,
        price_text=review_data.price_text,
        photo_url=review_data.photo_url
    )
    
    created_review = await create_review(db, review)
    return created_review

@router.put("/reviews/{review_id}", response_model=ReviewOut)
async def update_place_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """리뷰 수정"""
    # 리뷰 조회
    review = await get_review(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="리뷰를 찾을 수 없습니다."
        )
    
    # 권한 확인 (자신의 리뷰만 수정 가능)
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="자신의 리뷰만 수정할 수 있습니다."
        )
    
    # 평점 검증
    if review_data.rating is not None and (review_data.rating < 1 or review_data.rating > 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="평점은 1-5 사이의 값이어야 합니다."
        )
    
    # 업데이트할 데이터 준비
    update_data = review_data.dict(exclude_unset=True)
    
    updated_review = await update_review(db, review_id, update_data)
    return updated_review

@router.delete("/reviews/{review_id}")
async def delete_place_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """리뷰 삭제"""
    # 리뷰 조회
    review = await get_review(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="리뷰를 찾을 수 없습니다."
        )
    
    # 권한 확인 (자신의 리뷰만 삭제 가능)
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="자신의 리뷰만 삭제할 수 있습니다."
        )
    
    await delete_review(db, review_id)
    return {"message": "리뷰가 삭제되었습니다."}
