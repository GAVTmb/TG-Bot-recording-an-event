from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Admin


# Добавляет адина в БД. На вход принимант словарь с данными.
async def orm_add_admin(session: AsyncSession, data: dict):
    obj = Admin(
        tg_user_id=data["tg_id"],
        surname=data["surname"],
        name=data["name"],
        phone_number=data["phone_number"],
        admin_access=data["admin_access"],
        main_admin=data["main_admin"],
    )
    session.add(obj)
    await session.commit()


# Находит Админа по телеграм id
async def orm_get_admin(session: AsyncSession, tg_id_admin: str):
    query = select(Admin).where(Admin.tg_id_admin == tg_id_admin)
    result = await session.execute(query)
    return result.scalar()


# Находит всех админов (Простых админов).
async def orm_get_all_admin(session: AsyncSession):
    query = select(Admin).where(Admin.main_admin != True)
    result = await session.execute(query)
    return result.scalars().all()


# Изменяет значение в admin_access у определенного админа.
# На вход принимает телеграм id и новое значение True или False
async def orm_update_admin_access(session: AsyncSession, tg_id_admin: str, data: bool):
    query = update(Admin).where(Admin.tg_id_admin == tg_id_admin).values(
        admin_access=data,)
    await session.execute(query)
    await session.commit()

