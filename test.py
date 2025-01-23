import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query_event import orm_add_event
from database.orm_query_participant import orm_add_participant
from database.orm_query_feedback import orm_add_feedback


async def uploading_db(session: AsyncSession):
    for item in data_db_event:
        await orm_add_event(session, item)
    for item1 in data_db_participant:
        await orm_add_participant(session, item1)
    for item2 in data_db_feedback:
        await orm_add_feedback(session, item2)


data_db_event = [
    {"name_event": "Первое тестовое событие!",
     "description_event": "Событие создается как прошедшее.",
     "image": "AgACAgIAAxkBAAIHsmc92nHRgi3NUKWn0pwDZzriEyS_AAJq5TEbq6jxScI2uLZglvlOAQADAgADeQADNgQ",
     "price": 5,
     "beginning_event": datetime.date(2024, 11, 10),
     "the_end_event": datetime.date(2024, 11, 10),
     "location_event": "г. Тамбов, ул. Лёнина, дом 1",
     "number_participants": 10},
    {"name_event": "Второе тестовое событие!",
     "description_event": "Сождаеться как предстоящее.",
     "image": "AgACAgIAAxkBAAIIf2dDM3r_qxXXlx7RDeUl6ZbwFic7AAKn5jEb2W0gSg07MsICiznWAQADAgADeQADNgQ",
     "price": 10,
     "beginning_event": datetime.date(2024, 11, 30),
     "the_end_event": datetime.date(2024, 11, 30),
     "location_event": "г. Тамбов. Баня у Димана!",
     "number_participants": 5
    }
]

data_db_participant = [
    {
        "event_id": 1,
        "tg_user_id": "12345",
        "surname": "Головач",
        "name": "Лена",
        "phone_number": "8 800 123 55 66"
    },
    {
        "event_id": 1,
        "tg_user_id": "1111111",
        "surname": "Душный",
        "name": "Эдуард",
        "phone_number": "+7 (900) 123 33 33"
    },
    {
        "event_id": 1,
        "tg_user_id": "111112",
        "surname": "Воробей",
        "name": "Джек",
        "phone_number": "89207658787"
    },
    {
        "event_id": 1,
        "tg_user_id": "1112311",
        "surname": "Саркисян",
        "name": "Ашот",
        "phone_number": "8 900 777 77 77"
    },
    {
        "event_id": 1,
        "tg_user_id": "11223366",
        "surname": "Старк",
        "name": "Тони",
        "phone_number": "8 900 900 09 09"
    },
    {
        "event_id": 1,
        "tg_user_id": "112223344",
        "surname": "Норис",
        "name": "Чак",
        "phone_number": "8 888 888 88 88"
    },
    {
        "event_id": 1,
        "tg_user_id": "11225566",
        "surname": "Джан-Клод",
        "name": "Вандам-Терминатор",
        "phone_number": "8 735 962 27 50"
    },
    {
        "event_id": 1,
        "tg_user_id": "11239900",
        "surname": "Камушкин",
        "name": "Пися",
        "phone_number": "8 300 300 1111"
    },
    {
        "event_id": 1,
        "tg_user_id": "2388890",
        "surname": "Бузова",
        "name": "Оля",
        "phone_number": "8 954 900 00 00"
    },
    {
        "event_id": 1,
        "tg_user_id": "3657890",
        "surname": "Джакнамбек",
        "name": "Зухра",
        "phone_number": "8 915 653 92 46"
    }
]

data_db_feedback = [
    {
        "participant_id": 2,
        "public_feedback": "Я ожидал Большего... Место проведение не очень, Вином не угощали.",
        "closed_feedback": ""
    },
    {
        "participant_id": 9,
        "public_feedback": "Очень вдохновилась, но все же очень мало половин. Сергей, твои слова водица...",
        "closed_feedback": ""
    },
    {
        "participant_id": 6,
        "public_feedback": "Было очень весело. Попросили сыграть на гитаре, я сыграл и выиграл",
        "closed_feedback": ""
    },
    {
        "participant_id": 8,
        "public_feedback": "",
        "closed_feedback": "Все очень понравилось, но хочется что бы бутылки заменили на стулья."
    },
    {
        "participant_id": 10,
        "public_feedback": "сипасиба ваш виступлений мнэ очин памок. тепер мая слова сильный.",
        "closed_feedback": ""
    },
    {
        "participant_id": 5,
        "public_feedback": "Все супер!!!",
        "closed_feedback": "Предлагаю сделать тренинг Как стать железным человеком."
    }
]
