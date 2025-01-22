import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Event, Participant


async def orm_get_upcoming_events_mailing(session: AsyncSession):
    query = (select(Event.id, Event.name_event, Event.location_event)
             .where(Event.beginning_event - datetime.date.today() == 1))
    result = await session.execute(query)
    return result.all()


async def orm_mailing_after_the_event(session: AsyncSession):
    print("Сработала фунция orm_mailing_after_the_event!")
    query = select(Event).where(Event.the_end_event == datetime.date.today())
    result = await session.execute(query)
    return result.all()


async def orm_get_participants_mailing(session: AsyncSession, event_id: int):
    query = select(Participant.tg_user_id, Participant.name).where(Participant.event_id == event_id)
    result = await session.execute(query)
    return result.all()
