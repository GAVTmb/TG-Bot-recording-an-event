import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Event, Participant


# Добавление нового собыдия в БД через админку.
async def orm_add_event(session: AsyncSession, data: dict):
    obj = Event(
        name_event=data["name_event"],
        description_event=data["description_event"],
        image=data["image"],
        price=data["price"],
        beginning_event=data["beginning_event"],
        the_end_event=data["the_end_event"],
        location_event=data["location_event"],
        number_participants=data["number_participants"],
    )
    session.add(obj)
    await session.commit()


# Выдает все события.
async def orm_get_all_events(session: AsyncSession):
    query = select(Event)
    result = await session.execute(query)
    return result.scalars().all()


# Находит и выдает предстоящие события.
async def orm_get_upcoming_events(session: AsyncSession):
    query = (select(Event).where(Event.beginning_event >= datetime.date.today()))
    result = await session.execute(query)
    return result.scalars().all()


# Находит и выдает прошедшие события.
async def orm_get_past_events(session: AsyncSession):
    query = select(Event).where(Event.the_end_event <= datetime.date.today())
    result = await session.execute(query)
    return result.scalars().all()


# Находит событие по id
async def orm_get_event(session: AsyncSession, event_id: int):
    query = select(Event).where(Event.id == event_id)
    result = await session.execute(query)
    return result.scalar()


# Изменеие События
async def orm_update_event(session: AsyncSession, event_id: int, data):
    query = update(Event).where(Event.id == event_id).values(
        name_event=data["name_event"],
        description_event=data["description_event"],
        image=data["image"],
        price=data["price"],
        beginning_event=data["beginning_event"],
        the_end_event=data["the_end_event"],
        location_event=data["location_event"],
        number_participants=int(data["number_participants"]),)
    await session.execute(query)
    await session.commit()


# Удалить событие
async def orm_delete_event(session: AsyncSession, event_id: int):
    query = delete(Event).where(Event.id == event_id)
    await session.execute(query)
    await session.commit()


# Находит события в которых участвовал конкретный пользователь.
async def orm_get_events_with_user(session: AsyncSession, tg_user_id: str):
    query = (select(Event).where(Participant.tg_user_id == tg_user_id)
             .join(Participant, Participant.event_id == Event.id))
    result = await session.execute(query)
    return result.scalars().all()
