from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text
from app.core.config import get_database
from app.crud.review import create_review, get_review, update_review, delete_review, get_reviews_by_phone
from app.crud.place import get_place
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewOut, ReviewUpdate
from typing import List, Optional
import os
import time
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

router = APIRouter()

@router.post("/{place_id}/reviews", response_model=ReviewOut)
async def create_place_review(
    place_id: int,
    phone_number: str = Form(...),
    rating: int = Form(...),
    content: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    photos: Optional[List[UploadFile]] = File(None)
):
    """가게 리뷰 작성 (multipart/form-data 지원) - 직접 연결 방식"""
    try:
        print(f"DEBUG: place_id = {place_id}")
        print(f"DEBUG: phone_number = {phone_number}")
        print(f"DEBUG: rating = {rating}")
        print(f"DEBUG: content = {content}")
        print(f"DEBUG: files = {files}")
        print(f"DEBUG: file = {file}")
        print(f"DEBUG: image = {image}")
        print(f"DEBUG: photos = {photos}")
        
        # 모든 파일 필드 확인
        all_files = []
        if files:
            all_files.extend(files)
        if file:
            all_files.append(file)
        if image:
            all_files.append(image)
        if photos:
            all_files.extend(photos)
            
        print(f"DEBUG: 총 파일 개수 = {len(all_files)}")
        
        load_dotenv()
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="데이터베이스 URL이 설정되지 않았습니다."
            )
        
        # 직접 연결 방식
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=0,
            pool_timeout=10
        )
        
        async with engine.begin() as conn:
            # 가게 존재 확인
            place_result = await conn.execute(
                text("SELECT id FROM places WHERE id = :place_id"),
                {"place_id": place_id}
            )
            if not place_result.fetchone():
                await engine.dispose()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="가게를 찾을 수 없습니다."
                )
            
            # 리뷰 데이터 검증
            if rating < 1 or rating > 5:
                await engine.dispose()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="평점은 1-5 사이의 값이어야 합니다."
                )
            
            # 파일 저장 및 URL 생성
            photo_urls = None
            if all_files:
                print(f"DEBUG: 파일 개수 = {len(all_files)}")
                file_urls = []
                for i, file in enumerate(all_files):
                    print(f"DEBUG: 파일 {i} = {file.filename}, 크기 = {file.size if hasattr(file, 'size') else 'unknown'}")
                    if file.filename:
                        try:
                            # 파일 저장
                            file_content = await file.read()
                            print(f"DEBUG: 파일 내용 크기 = {len(file_content)} bytes")
                            
                            file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
                            unique_filename = f"review_{place_id}_{int(time.time())}_{i}.{file_extension}"
                            
                            # S3 업로드
                            s3_client = boto3.client(
                                's3',
                                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                                region_name=os.getenv('AWS_REGION', 'ap-northeast-2')
                            )
                            
                            bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
                            s3_key = f"reviews/{unique_filename}"
                            
                            print(f"DEBUG: S3 업로드 시작 - 버킷: {bucket_name}, 키: {s3_key}")
                            
                            # S3에 파일 업로드
                            s3_client.put_object(
                                Bucket=bucket_name,
                                Key=s3_key,
                                Body=file_content,
                                ContentType=file.content_type or 'image/jpeg'
                            )
                            
                            print(f"DEBUG: S3 업로드 완료")
                            
                            # S3 URL 생성
                            file_url = f"https://{bucket_name}.s3.{os.getenv('AWS_REGION', 'ap-northeast-2')}.amazonaws.com/{s3_key}"
                            file_urls.append(file_url)
                            print(f"DEBUG: 생성된 S3 URL = {file_url}")
                            
                        except Exception as e:
                            print(f"ERROR: 파일 저장 실패 = {str(e)}")
                            continue
                
                photo_urls = str(file_urls) if file_urls else None
                print(f"DEBUG: 최종 photo_urls = {photo_urls}")
            else:
                print("DEBUG: 모든 파일 필드가 None이거나 비어있음")
            
            # 리뷰 생성 (직접 SQL)
            result = await conn.execute(
                text("""
                    INSERT INTO reviews (place_id, phone_number, rating, content, photo_urls, created_at)
                    VALUES (:place_id, :phone_number, :rating, :content, :photo_urls, NOW())
                    RETURNING id, place_id, phone_number, rating, content, photo_urls, created_at
                """),
                {
                    "place_id": place_id,
                    "phone_number": phone_number,
                    "rating": rating,
                    "content": content,
                    "photo_urls": photo_urls
                }
            )
            
            review_data = result.fetchone()
            
            await engine.dispose()
            
            # ReviewOut 형태로 변환
            review = ReviewOut(
                id=review_data[0],
                place_id=review_data[1],
                phone_number=review_data[2],
                rating=review_data[3],
                content=review_data[4],
                photo_urls=review_data[5],
                created_at=review_data[6]
            )
            
            print(f"DEBUG: 리뷰 생성 성공: {review.id}")
            return review
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: 리뷰 생성 실패: {str(e)}")
        if 'engine' in locals():
            await engine.dispose()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"리뷰 생성 중 오류가 발생했습니다: {str(e)}"
        )

@router.put("/reviews/{review_id}", response_model=ReviewOut)
async def update_place_review(
    review_id: int,
    review_data: ReviewUpdate,
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
    
    await delete_review(db, review_id)
    return {"message": "리뷰가 삭제되었습니다."}

@router.get("/reviews/phone/{phone_number}", response_model=List[ReviewOut])
async def get_reviews_by_phone_number(
    phone_number: str,
    db: AsyncSession = Depends(get_database)
):
    """전화번호로 리뷰 조회"""
    reviews = await get_reviews_by_phone(db, phone_number)
    return reviews
