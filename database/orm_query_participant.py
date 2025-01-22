from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Participant


# Добавляет участника события в БД.
async def orm_add_participant(session: AsyncSession, data: dict):
    obj = Participant(
        event_id=int(data["event_id"]),
        tg_user_id=data["tg_user_id"],
        surname=data["surname"],
        name=data["name"],
        phone_number=data["phone_number"],
    )
    session.add(obj)
    await session.commit()


# Находит всех участников определенного события по id события.
async def orm_get_participants(session: AsyncSession, event_id: int):
    query = select(Participant).where(Participant.event_id == event_id)
    result = await session.execute(query)
    return result.scalars().all()


# Находит телеграм id участников определенного события и формирет из них список.
async def orm_get_participants_tg_user_id(session: AsyncSession, event_id: int):
    query = select(Participant.tg_user_id).where(Participant.event_id == event_id)
    result = await session.execute(query)
    tg_user_id_list = []
    for tg_user_id in result.scalars().all():
        tg_user_id_list.append(int(tg_user_id))
    return tg_user_id_list


# Находит и выдает id участника определенного события.
async def orm_get_participant_tg_user_id_event_id(session: AsyncSession, event_id: int, tg_user_id: str):
    query = select(Participant.id).where(Participant.event_id == event_id,
                                         Participant.tg_user_id == tg_user_id)
    result = await session.execute(query)
    return result.scalar()
