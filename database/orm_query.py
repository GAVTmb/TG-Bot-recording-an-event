import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Event, Participant, Feedback, Admin


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


async def orm_add_feedback(session: AsyncSession, data: dict):
    obj = Feedback(
        participant_id=int(data["participant_id"]),
        public_feedback=data["public_feedback"],
        closed_feedback=data["closed_feedback"],
    )
    session.add(obj)
    await session.commit()


# Выдает все события
async def orm_get_all_events(session: AsyncSession):
    query = select(Event)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_upcoming_events(session: AsyncSession):
    query = (select(Event).where(Event.beginning_event >= datetime.date.today()))
    result = await session.execute(query)
    return result.scalars().all()


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


async def orm_get_past_events(session: AsyncSession):
    query = select(Event).where(Event.the_end_event <= datetime.date.today())
    result = await session.execute(query)
    return result.scalars().all()


# Находит событие по id
async def orm_get_event(session: AsyncSession, event_id: int):
    query = select(Event).where(Event.id == event_id)
    result = await session.execute(query)
    return result.scalar()


# Находит Админа по id
async def orm_get_admin(session: AsyncSession, tg_id_admin: str):
    query = select(Admin).where(Admin.tg_id_admin == tg_id_admin)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_all_admin(session: AsyncSession):
    query = select(Admin).where(Admin.main_admin != True)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_update_admin_access(session: AsyncSession, tg_id_admin: str, data: bool):
    query = update(Admin).where(Admin.tg_id_admin == tg_id_admin).values(
        admin_access=data,)
    await session.execute(query)
    await session.commit()


async def orm_get_events_with_user(session: AsyncSession, tg_user_id: str):
    query = (select(Event).where(Participant.tg_user_id == tg_user_id)
             .join(Participant, Participant.event_id == Event.id))
    result = await session.execute(query)
    return result.scalars().all()


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


async def orm_get_participants(session: AsyncSession, event_id: int):
    query = select(Participant).where(Participant.event_id == event_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_participants_mailing(session: AsyncSession, event_id: int):
    query = select(Participant.tg_user_id, Participant.name).where(Participant.event_id == event_id)
    result = await session.execute(query)
    return result.all()


async def orm_get_participants_tg_user_id(session: AsyncSession, event_id: int):
    query = select(Participant.tg_user_id).where(Participant.event_id == event_id)
    result = await session.execute(query)
    tg_user_id_list = []
    for tg_user_id in result.scalars().all():
        tg_user_id_list.append(int(tg_user_id))
    return tg_user_id_list


async def orm_get_participant_tg_user_id_event_id(session: AsyncSession, event_id: int, tg_user_id: str):
    query = select(Participant.id).where(Participant.event_id == event_id, Participant.tg_user_id == tg_user_id )
    result = await session.execute(query)
    return result.scalar()


async def orm_get_feedbacks_admin(session: AsyncSession, event_id: int):
    query = (select(Event.name_event, Participant.surname, Participant.name,
                    Feedback.public_feedback, Feedback.closed_feedback)
             .join(Participant, Participant.event_id == Event.id)
             .join(Feedback, Feedback.participant_id == Participant.id)
             .where(Participant.event_id == event_id))
    result = await session.execute(query)
    generated_text = []
    for feedback_ in result.all():
        if feedback_[3] is None:
            text = f"{feedback_[1]} {feedback_[2]}\nПриватный отзыв: {feedback_[4]}\n\n"
            generated_text.append(text)
        elif feedback_[4] is None:
            text = f"{feedback_[1]} {feedback_[2]}\nПубличный отзыв: {feedback_[3]}\n\n"
            generated_text.append(text)
        else:
            text = (f"{feedback_[1]} {feedback_[2]}\nПриватный отзыв: {feedback_[3]}"
                    f"\nПубличный отзыв: {feedback_[4]}\n\n")
            generated_text.append(text)
    return generated_text


async def orm_get_feedbacks_user(session: AsyncSession, event_id: int):
    query = (select(Event.name_event, Participant.surname, Participant.name,
                    Feedback.public_feedback, Feedback.closed_feedback)
             .join(Participant, Participant.event_id == Event.id)
             .join(Feedback, Feedback.participant_id == Participant.id)
             .where(Participant.event_id == event_id))
    result = await session.execute(query)
    generated_text = []
    for feedback_ in result.all():
        if feedback_[3]:
            text = f"{feedback_[1]} {feedback_[2]}:\n{feedback_[3]}\n\n"
            generated_text.append(text)
    return generated_text



