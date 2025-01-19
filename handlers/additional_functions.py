from aiogram import Bot
from database.orm_query import (orm_get_upcoming_events_mailing, orm_get_participants_mailing,
                                orm_mailing_after_the_event)
from database.engine import engine

from keyboards.inline import get_callback_buts


# Функция рассылки сообщений участникам события с напоминанием, что оно состоится завтра.
# Срабатывает раз в день в 10:00 по МСК.
async def mailing_before_the_event(bot: Bot):
    async with engine.begin() as session:
        for event in await orm_get_upcoming_events_mailing(session):
            for participant in await orm_get_participants_mailing(session, int(event[0])):
                print(participant[0], participant[1])
                await bot.send_message(int(participant[0]),
                                       f"Здавствуйте {participant[1]}! "
                                       f"Напоминаем что вы записаны на событие {event[1]}, "
                                       f"которе пройдет по адресу {event[2]}. Ждем вас завтра!")


# Функция рассылки сообщений участникам события после его окончания с просьбой оставить отзыв.
# Срабатывает раз в день в 20:00 по МСК.
async def mailing_after_the_event(bot: Bot):
    async with engine.begin() as session:
        for event in await orm_mailing_after_the_event(session):
            print(f"event - {event}")
            for participant in await orm_get_participants_mailing(session, int(event[0])):
                print(participant[0], participant[1])
                await bot.send_message(int(participant[0]),
                                       f"Здавствуйте {participant[1]}! "
                                       f"Вы принимали участие в событии {event[1]}. "
                                       f"Нам будет приятно если вы оставите свой отзыв.",
                                       reply_markup=get_callback_buts(buts={
                                           "Оставить отзыв": f"addfeedbackuser_{event.id}",
                                       }, sizes=(1,))
                                       )
