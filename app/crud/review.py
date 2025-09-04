from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.review import Review
from app.schemas.review import ReviewCreate

async def get_reviews_by_place(db: AsyncSession, place_id: int):
    result = await db.execute(select(Review).where(Review.place_id == place_id))
    return result.scalars().all()

async def get_review(db: AsyncSession, review_id: int):
    result = await db.execute(select(Review).where(Review.id == review_id))
    return result.scalar_one_or_none()

async def create_review(db: AsyncSession, review: Review):
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review

async def update_review(db: AsyncSession, review_id: int, review_data: dict):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if review:
        for key, value in review_data.items():
            setattr(review, key, value)
        await db.commit()
        await db.refresh(review)
    return review

async def delete_review(db: AsyncSession, review_id: int):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if review:
        await db.delete(review)
        await db.commit()
    return review

async def get_reviews_by_phone(db: AsyncSession, phone_number: str):
    result = await db.execute(select(Review).where(Review.phone_number == phone_number))
    return result.scalars().all()

async def get_all_reviews(db: AsyncSession):
    result = await db.execute(select(Review))
    return result.scalars().all()
