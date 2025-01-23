from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Event, Participant, Feedback


# Добавляет отзыв.
async def orm_add_feedback(session: AsyncSession, data: dict):
    obj = Feedback(
        participant_id=int(data["participant_id"]),
        public_feedback=data["public_feedback"],
        closed_feedback=data["closed_feedback"],
    )
    session.add(obj)
    await session.commit()


# Находит название определенного события, имя и фамилию участников,
# публичные и приватные озывы, формирует из них список с текстом для отправки обратного сообщения.
async def orm_get_feedbacks_admin(session: AsyncSession, event_id: int):
    query = (select(Event.name_event, Participant.surname, Participant.name,
                    Feedback.public_feedback, Feedback.closed_feedback)
             .join(Participant, Participant.event_id == Event.id)
             .join(Feedback, Feedback.participant_id == Participant.id)
             .where(Participant.event_id == event_id))
    result = await session.execute(query)
    generated_text = []
    for feedback_ in result.all():
        text = (f"{feedback_[2]} {feedback_[1]}\nПриватный отзыв: {feedback_[4]}"
                f"\nПубличный отзыв: {feedback_[3]}\n\n")
        generated_text.append(text)
    return generated_text


# Находит название определенного события, имя и фамилию участников,
# публичные озывы и формирует из них список с текстом для отправки обратного сообщения.
async def orm_get_feedbacks_user(session: AsyncSession, event_id: int):
    query = (select(Event.name_event, Participant.surname, Participant.name,
                    Feedback.public_feedback)
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

