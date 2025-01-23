import os
from aiogram import F, types, Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import LabeledPrice, PreCheckoutQuery
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

from keyboards import kb
from keyboards.inline import get_callback_buts
from test import uploading_db

from database.orm_query_feedback import orm_get_feedbacks_user, orm_add_feedback
from database.orm_query_event import (orm_get_all_events, orm_get_upcoming_events,
                                      orm_get_event, orm_get_events_with_user)
from database.orm_query_participant import (orm_get_participants_tg_user_id, orm_add_participant,
                                            orm_get_participant_tg_user_id_event_id)

user_router = Router()


class AddUser(StatesGroup):
    event_id = State()
    tg_user_id = State()
    surname = State()
    name = State()
    phone_number = State()

    user_data = None

    texts = {
        "AddUser:surname": "Напишите вашу фамилию заново.",
        "AddUser:name": "Напишите ваше имя заново.",
        "AddUser:phone_number": "Напишите ваш номер телефона заново."
    }


class AddFeedbackUser(StatesGroup):
    participant_id = State()
    public_feedback = State()
    closed_feedback = State()

    text_feedback = None


@user_router.message(F.text == "Старт")
async def start_user(message: types.Message, session: AsyncSession):
    # await uploading_db(session)
    await message.answer("Здравствуйте, чем вам помочь?",
                         reply_markup=kb.start_kb_user.as_markup(resize_keyboard=True))


@user_router.message(F.text == "Посмотреть все события")
async def show_all_events(message: types.Message, session: AsyncSession):
    for event in await orm_get_all_events(session):
        beg_event = event.beginning_event
        end_event = event.the_end_event
        if beg_event >= datetime.date.today():
            await message.answer_photo(
                event.image,
                caption=f"{event.name_event}\n\n{event.description_event}\n\nСтоимость участия - {event.price}руб.\n"
                        f"Пройдет с {beg_event.day}.{beg_event.month}.{beg_event.year} "
                        f"по {end_event.day}.{end_event.month}.{end_event.year}\n"
                        f"Количество мест - {event.number_participants}",
                reply_markup=get_callback_buts(buts={
                    "Записаться": f"registration_{event.id}",
                }, sizes=(1, ))
            )
        else:
            await message.answer_photo(
                event.image,
                caption=f"{event.name_event}\n\n{event.description_event}\n\nСтоимость участия - {event.price}руб.\n"
                        f"Проводилось с {beg_event.day}.{beg_event.month}.{beg_event.year} "
                        f"по {end_event.day}.{end_event.month}.{end_event.year}\n",
                reply_markup=get_callback_buts(buts={
                    "Посмотреть отзывы": f"getfeedbacksuser_{event.id}",
                }, sizes=(1,))
            )


@user_router.message(F.text == "Записаться на предстоящее")
async def upcoming_events(message: types.Message, session: AsyncSession):
    event_data = await orm_get_upcoming_events(session)
    if event_data:
        for event in event_data:
            beg_event = event.beginning_event
            end_event = event.the_end_event
            print('if')
            await message.answer_photo(
                event.image,
                caption=f"{event.name_event}\n\n{event.description_event}\n\nСтоимость участия - {event.price}руб.\n"
                        f"Пройдет с {beg_event.day}.{beg_event.month}.{beg_event.year} "
                        f"по {end_event.day}.{end_event.month}.{end_event.year}\n"
                        f"Место проведения: {event.location_event}\n"
                        f"Количество мест - {event.number_participants}",
                reply_markup=get_callback_buts(buts={
                    "Записаться": f"registration_{event.id}",
                }, sizes=(1,))
            )
    else:
        print("else")
        await message.answer("Предстоящих событий еще нет!")


@user_router.message(F.text == "Оставить отзыв")
async def leave_feedback_event_user_mes(message: types.Message, session: AsyncSession):
    tg_user_id = message.from_user.id
    event_list = await orm_get_events_with_user(session, str(tg_user_id))
    if len(event_list) > 0:
        for event in event_list:
            if event.the_end_event <= datetime.date.today():
                await message.answer_photo(
                    event.image,
                    caption=f"{event.name_event}\n\n{event.description_event}\n"
                            f"Проводилось с "
                            f"{event.beginning_event.day}.{event.beginning_event.month}.{event.beginning_event.year} "
                            f"по {event.the_end_event.day}.{event.the_end_event.month}.{event.the_end_event.year}\n",
                    reply_markup=get_callback_buts(buts={
                        "Оставить отзыв": f"addfeedbackuser_{event.id}",
                    }, sizes=(1,))
                )
    else:
        await message.answer(f"Оставлять отзывы могут только участники событий. "
                             f"Вы ешё не принимали участия ни в одном событии.",
                             reply_markup=kb.start_kb_user.as_markup(resize_keyboard=True))


@user_router.callback_query(F.data.startswith("getfeedbacksuser_"))
async def feedback_event_user(callback: types.CallbackQuery, session: AsyncSession):
    event_id = callback.data.split("_")[-1]
    event = await orm_get_event(session, int(event_id))
    feedback_list_user = await orm_get_feedbacks_user(session, int(event_id))
    if feedback_list_user:
        await callback.answer()
        await callback.message.answer_photo(event.image, caption=f"{event.name_event}\n\n{"".join(feedback_list_user)}",
                                            reply_markup=kb.start_kb_user.as_markup(resize_keyboard=True))
    else:
        await callback.answer()
        await callback.message.answer_photo(event.image, caption=f"{event.name_event}"
                                                                 f"\n\nУ этого события еще нет отзывов.",
                                            reply_markup=kb.start_kb_user.as_markup(resize_keyboard=True))


@user_router.callback_query(StateFilter(None), F.data.startswith("addfeedbackuser_"))
async def add_feedback_user(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    event_id = callback.data.split("_")[-1]
    tg_user_id = callback.from_user.id
    id_participant = await orm_get_participant_tg_user_id_event_id(session, int(event_id), str(tg_user_id))
    await state.update_data(participant_id=int(id_participant))
    await callback.answer()
    await callback.message.answer(f"Напишите ваш отзыв!",
                                  reply_markup=kb.kb_cancel_user.as_markup(resize_keyboard=True))
    await state.set_state(AddFeedbackUser.participant_id)


@user_router.message(StateFilter("*"), Command("Отмена"))
@user_router.message(StateFilter("*"), F.text == "Отмена")
async def cancel_handler_user(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddUser.user_data:
        AddUser.user_data = None
    await state.clear()
    await message.answer("Отменил!", reply_markup=kb.start_kb_user.as_markup(resize_keyboard=True))


# Возвращает на шаг незад
@user_router.message(StateFilter("*"), Command("Назад"))
@user_router.message(StateFilter("*"), F.text == "Назад")
async def return_handler_user(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AddUser.surname:
        await message.answer("Напишите вашу фамилию или жми отмена")
        return

    previous = None
    for step in AddUser.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Вернул к предыдущему шагу.\n"
                                 f" {AddUser.texts[previous.state]}")
            return
        previous = step


@user_router.message(StateFilter(AddFeedbackUser.participant_id), F.text)
async def selection_type_feedback(message: types.Message, state: FSMContext):
    AddFeedbackUser.text_feedback = message.text
    await message.answer(f"Хотите оставить отзыв публично или приватно? "
                         f"Публичный отзыв бубет виден всем, приватный только организаторам.",
                         reply_markup=get_callback_buts(buts={
                             "Публичный": f"public_",
                             "Приватный": f"private_",
                         }, sizes=(2, )))
    await state.set_state(AddFeedbackUser.public_feedback)


@user_router.callback_query(StateFilter(AddFeedbackUser.public_feedback), F.data.startswith("public_"))
async def add_feedback_public(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.update_data(public_feedback=str(AddFeedbackUser.text_feedback))
    await state.update_data(closed_feedback="")
    dict_feedback = await state.get_data()
    await orm_add_feedback(session, dict_feedback)
    print(dict_feedback)
    await state.clear()
    AddFeedbackUser.text_feedback = None
    await callback.answer()
    await callback.message.answer(f"Публичный отзыв добавлен.",
                                  reply_markup=kb.start_kb_user.as_markup(resize_keyboard=True))


@user_router.callback_query(StateFilter(AddFeedbackUser.public_feedback), F.data.startswith("private_"))
async def add_feedback_private(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.update_data(public_feedback="")
    await state.update_data(closed_feedback=str(AddFeedbackUser.text_feedback))
    dict_feedback = await state.get_data()
    await orm_add_feedback(session, dict_feedback)
    print(dict_feedback)
    await state.clear()
    AddFeedbackUser.text_feedback = None
    await callback.answer()
    await callback.message.answer(f"Приватный отзыв добавлен.",
                                  reply_markup=kb.start_kb_user.as_markup(resize_keyboard=True))


@user_router.callback_query(StateFilter(None), F.data.startswith("registration_"))
async def register_event(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    event_id = callback.data.split("_")[-1]
    tg_user_id = callback.from_user.id
    tg_user_id_list = await orm_get_participants_tg_user_id(session, int(event_id))
    print(f"tg_user_id in register_event - !!!{tg_user_id}!!!")
    if tg_user_id in tg_user_id_list:
        await callback.answer()
        await callback.message.answer(f"Вы уже зарегестрированы на данное событие!",
                                      reply_markup=kb.start_kb_user.as_markup(resize_keyboard=True))
    else:
        await state.update_data(event_id=int(event_id))
        await state.update_data(tg_user_id=str(tg_user_id))
        await callback.answer()
        await callback.message.answer(f"Давайте запишемся!\n Напиши свою фамилию.",
                                      reply_markup=kb.kb_cancel_back_user.as_markup(resize_keyboard=True))
        await state.set_state(AddUser.surname)


@user_router.message(StateFilter(AddUser.surname), F.text)
async def add_surname_user(message: types.Message, state: FSMContext):
    print(message.text)
    await state.update_data(surname=message.text)
    await message.answer("Напиши свое имя.",
                         reply_markup=kb.kb_cancel_back_user.as_markup(resize_keyboard=True))
    await state.set_state(AddUser.name)


@user_router.message(StateFilter(AddUser.name), F.text)
async def add_name_user(message: types.Message, state: FSMContext):
    print(message.text)
    await state.update_data(name=message.text)
    await message.answer("Напиши свой номер телефона.",
                         reply_markup=kb.kb_cancel_back_user.as_markup(resize_keyboard=True))
    await state.set_state(AddUser.phone_number)


@user_router.message(StateFilter(AddUser.phone_number), F.text)
async def add_phone_number(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    print(message.text)
    await state.update_data(phone_number=message.text)
    user_data = await state.get_data()
    AddUser.user_data = user_data
    event = await orm_get_event(session, int(user_data["event_id"]))
    await bot.send_invoice(
        chat_id=message.chat.id,
        title=event.name_event,
        description=event.description_event,
        payload=f"Test{message.chat.id}!!!",
        provider_token=os.getenv("PAYMENT_TOKEN"),
        currency=os.getenv("CURRENCY"),
        prices=[
            LabeledPrice(
                label=f"Оплата {event.name_event}",
                amount=int(event.price) * 100
            )
        ],
        photo_url=event.image,
        photo_size=100,
        photo_width=800,
        photo_height=600
    )
    await message.answer("Вы можете отменить это действие нажав кнопку отмена.",
                         reply_markup=kb.kb_cancel_user.as_markup(resize_keyboard=True))


@user_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@user_router.message(F.successful_payment)
async def process_successful_payment(message: types.Message, state: FSMContext, session: AsyncSession):
    print(AddUser.user_data)
    event = await orm_get_event(session, int(AddUser.user_data["event_id"]))
    await orm_add_participant(session, AddUser.user_data)
    await state.clear()
    AddUser.user_data = None
    text = f"Оплата прошла успешно! Вы записаны на {event.name_event}"
    await message.answer(text, reply_markup=kb.start_kb_user.as_markup(resize_keyboard=True))

