from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.menu import Menu
from app.schemas.menu import MenuCreate

async def get_menus_by_place(db: AsyncSession, place_id: int):
    result = await db.execute(select(Menu).where(Menu.place_id == place_id))
    return result.scalars().all()

async def get_menu(db: AsyncSession, menu_id: int):
    result = await db.execute(select(Menu).where(Menu.id == menu_id))
    return result.scalar_one_or_none()

async def create_menu(db: AsyncSession, menu: Menu):
    db.add(menu)
    await db.commit()
    await db.refresh(menu)
    return menu

async def update_menu(db: AsyncSession, menu_id: int, menu_data: dict):
    result = await db.execute(select(Menu).where(Menu.id == menu_id))
    menu = result.scalar_one_or_none()
    if menu:
        for key, value in menu_data.items():
            setattr(menu, key, value)
        await db.commit()
        await db.refresh(menu)
    return menu

async def delete_menu(db: AsyncSession, menu_id: int):
    result = await db.execute(select(Menu).where(Menu.id == menu_id))
    menu = result.scalar_one_or_none()
    if menu:
        await db.delete(menu)
        await db.commit()
    return menu

async def get_all_menus(db: AsyncSession):
    result = await db.execute(select(Menu))
    return result.scalars().all()
