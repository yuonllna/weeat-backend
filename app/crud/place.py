from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.place import Place
from app.schemas.place import PlaceCreate

async def get_places(db: AsyncSession, category: str = None):
    stmt = select(Place)
    if category:
        stmt = stmt.where(Place.category == category)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_place(db: AsyncSession, place_id: int):
    result = await db.execute(select(Place).where(Place.id == place_id))
    return result.scalar_one_or_none()

async def create_place(db: AsyncSession, place: Place):
    db.add(place)
    await db.commit()
    await db.refresh(place)
    return place

async def update_place(db: AsyncSession, place_id: int, place_data: dict):
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.scalar_one_or_none()
    if place:
        for key, value in place_data.items():
            setattr(place, key, value)
        await db.commit()
        await db.refresh(place)
    return place

async def delete_place(db: AsyncSession, place_id: int):
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.scalar_one_or_none()
    if place:
        await db.delete(place)
        await db.commit()
    return place

async def get_places_by_category(db: AsyncSession, category: str):
    result = await db.execute(select(Place).where(Place.category == category))
    return result.scalars().all()
