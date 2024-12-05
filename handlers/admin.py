from aiogram import F, types, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

from database.orm_query import (orm_add_event, orm_get_all_events, orm_delete_event,
                                orm_update_event, orm_get_event, orm_get_participants, orm_get_feedbacks_admin)
from keyboards import kb
from keyboards.inline import get_callback_buts

ADMIN_LIST = [1903314478, ]

admin_router = Router()


class AddEvent(StatesGroup):
    name_event = State()
    description_event = State()
    image = State()
    price = State()
    beginning_event = State()
    the_end_event = State()
    location_event = State()
    number_participants = State()

    event_for_change = None

    texts = {"AddEvent:name_event": "Напиши название заново!",
             "AddEvent:description_event": "Напиши описание заново!",
             "AddEvent:image": "Загрузи изображение заново!",
             "AddEvent:price": "Напиши стоимость участия заново!",
             "AddEvent:beginning_event": "Напиши дату начала события заново!",
             "AddEvent:the_end_event": "Напиши дату окончания события заново!",
             "AddEvent:location_event": "Напиши место проведения заново!",
             "AddEvent:number_participants": "Напиши колличество учасников заново!",
             }


@admin_router.message(Command("admin"))
async def admin_login(message: types.Message):
    print("Вы вошли в режим аминистратора!")
    # if message.from_user.id in ADMIN_LIST:
    await message.answer("Вы вошли в режим аминистратора!",
                         reply_markup=kb.start_kb_admin.as_markup(resize_keyboard=True))


@admin_router.message(F.text == "Посмотреть события")
async def show_all_events_admin(message: types.Message, session: AsyncSession):
    for event in await orm_get_all_events(session):
        beg_event = event.beginning_event
        end_event = event.the_end_event
        await message.answer_photo(
            event.image,
            caption=f"{event.name_event}\n\n{event.description_event}\n\nСтоимость участия - {event.price}руб.\n"
                    f"Пройдет с {beg_event.day}.{beg_event.month}.{beg_event.year} "
                    f"по {end_event.day}.{end_event.month}.{end_event.year}\n"
                    f"Место проведения: {event.location_event}\n"
                    f"Количество мест - {event.number_participants}",
            reply_markup=get_callback_buts(buts={
                "Удалить": f"delete_{event.id}",
                "Изменить": f"change_{event.id}",
                "Отзывы": f"feedbacks_{event.id}",
                "Участники": f"participants_{event.id}"
            }, sizes=(2, 2))
        )


@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_event_admin(callback: types.CallbackQuery, session: AsyncSession):
    event_id = callback.data.split("_")[-1]
    await orm_delete_event(session, int(event_id))

    await callback.answer("Событие удалено!", show_alert=True)
    await callback.message.answer("Событие удалено!")


@admin_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_event_admin(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    event_id = callback.data.split("_")[-1]
    event_for_change = await orm_get_event(session, int(event_id))

    AddEvent.event_for_change = event_for_change
    await callback.answer()
    await callback.message.answer(
        "Напиши новое название", reply_markup=kb.kb_skip_admin.as_markup(resize_keyboard=True)
    )
    await state.set_state(AddEvent.name_event)


@admin_router.callback_query(F.data.startswith("feedbacks_"))
async def feedback_event_admin(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    event_id = callback.data.split("_")[-1]
    event = await orm_get_event(session, int(event_id))
    feedback_list = await orm_get_feedbacks_admin(session, int(event_id))
    if feedback_list:
        await callback.answer()
        await callback.message.answer_photo(event.image, caption=f"{event.name_event}\n\n{"".join(feedback_list)}",
                                            reply_markup=kb.start_kb_admin.as_markup(resize_keyboard=True))
    else:
        await callback.answer()
        await callback.message.answer_photo(event.image, caption=f"{event.name_event}"
                                                                 f"\n\nУ этого события еще нет отзывов.",
                                            reply_markup=kb.start_kb_admin.as_markup(resize_keyboard=True))


@admin_router.callback_query(F.data.startswith("participants_"))
async def participants_event_admin(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    event_id = callback.data.split("_")[-1]
    event = await orm_get_event(session, int(event_id))
    participants_list = await orm_get_participants(session, int(event_id))
    if participants_list:
        await callback.answer()
        await callback.message.answer_photo(event.image, caption=f"{event.name_event}\n\n{"".join(participants_list)}",
                                            reply_markup=kb.start_kb_admin.as_markup(resize_keyboard=True))
    else:
        await callback.answer()
        await callback.message.answer_photo(event.image, caption=f"{event.name_event}"
                                                                 f"\n\nВ этом событии еще нет участников.",
                                            reply_markup=kb.start_kb_admin.as_markup(resize_keyboard=True))


@admin_router.message(F.text == "Выход")
async def exit_admin(message: types.Message):
    await message.answer("Досвидания!", reply_markup=kb.start_kb_user.as_markup(resize_keyboard=True))


# Отлавливает нажатие кнопки "Добавить событие". Входит в режим FSM, отправляет сообщение пользователю
# "Напиши название". Становится в состояние "name_event"
@admin_router.message(StateFilter(None), F.text == "Добавить событие")
async def start_fsm_admin(message: types.Message, state: FSMContext):
    await message.answer("Давай добавим событие!!!\nНапиши название",
                         reply_markup=kb.kb_cancel_admin.as_markup(resize_keyboard=True))
    await state.set_state(AddEvent.name_event)


# Отменяет все действия выходит из режима FSM
@admin_router.message(StateFilter("*"), Command("Отменить"))
@admin_router.message(StateFilter("*"), F.text == "Отменить")
async def cancel_handler_admin(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddEvent.event_for_change:
        AddEvent.event_for_change = None
    await state.clear()
    await message.answer("Отменил!", reply_markup=kb.start_kb_admin.as_markup(resize_keyboard=True))


# Возвращает на шаг незад
@admin_router.message(StateFilter("*"), Command("Назад_"))
@admin_router.message(StateFilter("*"), F.text == "Назад_")
async def return_handler_admin(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AddEvent.name_event:
        await message.answer("эээ... назад некуда... пиши название или жми отмена")
        return

    previous = None
    for step in AddEvent.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Вернул к предыдущему шагу. \n"
                                 f" {AddEvent.texts[previous.state]}")
            return
        previous = step


# Отлавливает сообщение написаное в режиме "name_event" и сохраняет. Отправляет сообщение "Наниши описание!".
# Становится в состояние "description_event"
@admin_router.message(StateFilter(AddEvent.name_event), F.text)
async def add_name_event_admin(message: types.Message, state: FSMContext):
    print(message.text)
    if message.text == "Пропустить":
        await state.update_data(name_event=AddEvent.event_for_change.name_event)
        await message.answer("Наниши описание!",
                             reply_markup=kb.kb_skip_admin.as_markup(resize_keyboard=True))
    else:
        await state.update_data(name_event=message.text)
        if AddEvent.event_for_change is None:
            await message.answer("Наниши описание!",
                                 reply_markup=kb.kb_cancel_admin.as_markup(resize_keyboard=True))
        else:
            await message.answer("Наниши описание!",
                                 reply_markup=kb.kb_skip_admin.as_markup(resize_keyboard=True))
    await state.set_state(AddEvent.description_event)


@admin_router.message(StateFilter(AddEvent.name_event))
async def add_name_event_admin(message: types.Message, state: FSMContext):
    await message.answer("Что то пошло не так! Напиши название еще раз.")


# Отлавливает сообщение написаное в режиме "description_event" и сохраняет. Отправляет сообщение "Зазгузи изображение!".
# Становится в состояние "image"
@admin_router.message(StateFilter(AddEvent.description_event), or_f(F.text, F.text == "Пропустить"))
async def add_description_event_admin(message: types.Message, state: FSMContext):
    print(message.text)
    if message.text == "Пропустить":
        await state.update_data(description_event=AddEvent.event_for_change.description_event)
        await message.answer("Зазгузи изображение!",
                             reply_markup=kb.kb_skip_admin.as_markup(resize_keyboard=True))
    else:
        await state.update_data(description_event=message.text)
        if AddEvent.event_for_change is None:
            await message.answer("Зазгузи изображение!",
                                 reply_markup=kb.kb_cancel_admin.as_markup(resize_keyboard=True))
        else:
            await message.answer("Зазгузи изображение!",
                                 reply_markup=kb.kb_skip_admin.as_markup(resize_keyboard=True))
    await state.set_state(AddEvent.image)


@admin_router.message(StateFilter(AddEvent.description_event))
async def add_description_event_admin(message: types.Message, state: FSMContext):
    await message.answer("Что то пошло не так! Наниши описание еще раз!")


# Отлавливает сообщение написаное в режиме "image" и сохраняет. Отправляет сообщение "Напиши стоимость участия!".
# Становится в состояние "price"
@admin_router.message(StateFilter(AddEvent.image), or_f(F.photo, F.text == "Пропустить"))
async def add_image_admin(message: types.Message, state: FSMContext):
    print(message.photo)
    if message.text == "Пропустить":
        await state.update_data(image=AddEvent.event_for_change.image)
        await message.answer("Напиши стоимость участия, цифрами!",
                             reply_markup=kb.kb_skip_admin.as_markup(resize_keyboard=True))
    else:
        await state.update_data(image=message.photo[-1].file_id)
        if AddEvent.event_for_change is None:
            await message.answer("Напиши стоимость участия, цифрами! ",
                                 reply_markup=kb.kb_cancel_admin.as_markup(resize_keyboard=True))
        else:
            await message.answer("Напиши стоимость участия, цифрами!",
                                 reply_markup=kb.kb_skip_admin.as_markup(resize_keyboard=True))
    await state.set_state(AddEvent.price)


@admin_router.message(StateFilter(AddEvent.image))
async def add_image_admin(message: types.Message, state: FSMContext):
    await message.answer("Что то пошло не так! Зазгузи изображение еще раз!")


# Отлавливает сообщение написаное в режиме "price" и сохраняет. Отправляет сообщение "Напиши дату начала события!".
# Становится в состояние "beginning_event"
@admin_router.message(StateFilter(AddEvent.price), or_f(F.text, F.text == "Пропустить"))
async def add_price_admin(message: types.Message, state: FSMContext):
    print(message.text)
    try:
        if message.text == "Пропустить":
            await state.update_data(price=AddEvent.event_for_change.price)
            await message.answer("Напиши дату начала события! В формате число.месяц.год (10.10.2024)",
                                 reply_markup=kb.kb_skip_admin.as_markup(resize_keyboard=True))
        else:
            price_int = int(message.text)
            await state.update_data(price=price_int)
            if AddEvent.event_for_change is None:
                await message.answer("Напиши дату начала события! В формате число.месяц.год (10.10.2024)",
                                     reply_markup=kb.kb_cancel_admin.as_markup(resize_keyboard=True))
            else:
                await message.answer("Напиши дату начала события! В формате число.месяц.год (10.10.2024)",
                                     reply_markup=kb.kb_skip_admin.as_markup(resize_keyboard=True))
        await state.set_state(AddEvent.beginning_event)
    except Exception as error:
        print(error)
        await message.answer(f"Ошибка:{str(error)}\nВы ввели недопустимые значения. Напиши стоимость участия, цифрами!",
                             reply_markup=kb.start_kb_admin.as_markup(resize_keyboard=True))


@admin_router.message(StateFilter(AddEvent.price))
async def add_price_admin(message: types.Message, state: FSMContext):
    await message.answer("Что то пошло не так! Напиши стоимость участия, цифрами еще раз!")


# Отлавливает сообщение написаное в режиме "beginning_event" и сохраняет. Отправляет сообщение
# "Напиши дату окончания события!". Становится в состояние "the_end_event"
@admin_router.message(StateFilter(AddEvent.beginning_event), or_f(F.text, F.text == "Пропустить"))
async def add_beginning_event_admin(message: types.Message, state: FSMContext):
    print(message.text)
    try:
        if message.text == "Пропустить":
            await state.update_data(beginning_event=AddEvent.event_for_change.beginning_event)
            await message.answer("Напиши дату окончания события! В формате число.месяц.год (10.10.2024)",
                                 reply_markup=kb.kb_skip_admin.as_markup(resize_keyboard=True))
        else:
            received_date = message.text
            result = datetime.date(int(received_date[6:]), int(received_date[3:5]), int(received_date[0:2]))
            await state.update_data(beginning_event=result)
            if AddEvent.event_for_change is None:
                await message.answer("Напиши дату окончания события! В формате число.месяц.год (10.10.2024)",
                                     reply_markup=kb.kb_cancel_admin.as_markup(resize_keyboard=True))
            else:
                await message.answer("Напиши дату окончания события! В формате число.месяц.год (10.10.2024)",
                                     reply_markup=kb.kb_skip_admin.as_markup(resize_keyboard=True))
        await state.set_state(AddEvent.the_end_event)
    except Exception as error:
        print(error)
        await message.answer(f"Ошибка:{str(error)}\nВы ввели недопустимые значения. "
                             f"Напиши дату начала события! В формате число.месяц.год (10.10.2024)",
                             reply_markup=kb.start_kb_admin.as_markup(resize_keyboard=True))


@admin_router.message(StateFilter(AddEvent.beginning_event))
async def add_beginning_event_admin(message: types.Message, state: FSMContext):
    await message.answer("Что то пошло не так! Напиши дату начала события! "
                         "В формате число.месяц.год (10.10.2024) еще раз!")


# Отлавливает сообщение написаное в режиме "the_end_event" и сохраняет. Отправляет сообщение
# "Напиши место проведения события". Становится в состояние "location_event"
@admin_router.message(StateFilter(AddEvent.the_end_event), or_f(F.text, F.text == "Пропустить"))
async def add_the_end_event_admin(message: types.Message, state: FSMContext):
    print(message.text)
    try:
        if message.text == "Пропустить":
            await state.update_data(the_end_event=AddEvent.event_for_change.the_end_event)
            await message.answer("Напиши место проведения события",
                                 reply_markup=kb.kb_skip_admin.as_markup(resize_keyboard=True))
        else:
            received_date = message.text
            result = datetime.date(int(received_date[6:]), int(received_date[3:5]), int(received_date[0:2]))
            await state.update_data(the_end_event=result)
            if AddEvent.event_for_change is None:
                await message.answer("Напиши место проведения события",
                                     reply_markup=kb.kb_cancel_admin.as_markup(resize_keyboard=True))
            else:
                await message.answer("Напиши место проведения события",
                                     reply_markup=kb.kb_skip_admin.as_markup(resize_keyboard=True))
        await state.set_state(AddEvent.location_event)
    except Exception as error:
        print(error)
        await message.answer(f"Ошибка:{str(error)}\nВы ввели недопустимые значения. "
                             f"Напиши дату окончания события! В формате число.месяц.год (10.10.2024)",
                             reply_markup=kb.start_kb_admin.as_markup(resize_keyboard=True))


@admin_router.message(StateFilter(AddEvent.beginning_event))
async def add_beginning_event_admin(message: types.Message, state: FSMContext):
    await message.answer("Что то пошло не так! Напиши дату окончания события! "
                         "В формате число.месяц.год (10.10.2024) еще раз!")


@admin_router.message(StateFilter(AddEvent.location_event), or_f(F.text, F.text == "Пропустить"))
async def add_location_event_admin(message: types.Message, state: FSMContext):
    print(message.text)
    try:
        if message.text == "Пропустить":
            await state.update_data(location_event=AddEvent.event_for_change.location_event)
            await message.answer("Напиши количество участников, цифрами! Если количество не ограничено, напиши 0",
                                 reply_markup=kb.kb_skip_admin.as_markup(resize_keyboard=True))
        else:
            await state.update_data(location_event=message.text)
            if AddEvent.event_for_change is None:
                await message.answer("Напиши количество участников, цифрами!"
                                     " Если количество не ограничено, напиши 0",
                                     reply_markup=kb.kb_cancel_admin.as_markup(resize_keyboard=True))
            else:
                await message.answer("Напиши количество участников, цифрами!"
                                     " Если количество не ограничено, напиши 0",
                                     reply_markup=kb.kb_skip_admin.as_markup(resize_keyboard=True))
        await state.set_state(AddEvent.number_participants)
    except Exception as error:
        print(error)
        await message.answer(f"Ошибка:{str(error)}\nВы ввели недопустимые значения. "
                             f"Напиши место проведения события",
                             reply_markup=kb.start_kb_admin.as_markup(resize_keyboard=True))


@admin_router.message(StateFilter(AddEvent.the_end_event))
async def add_location_event_admin(message: types.Message, state: FSMContext):
    await message.answer("Что то пошло не так! Напиши место проведения события еще раз!")


# Отправляет сообщение пользователю, что все добавлено. Формирует словарь с данными отправляет в БД.
# После чего удаляет из памяти и выходит из режима FSM.
@admin_router.message(StateFilter(AddEvent.number_participants), F.text)
async def add_number_participants_admin(message: types.Message, state: FSMContext, session: AsyncSession):
    print(message.text)
    try:
        if message.text == "Пропустить":
            await state.update_data(number_participants=AddEvent.event_for_change.number_participants)
        else:
            number_participants_int = int(message.text)
            await state.update_data(number_participants=number_participants_int)
        data = await state.get_data()

        if AddEvent.event_for_change:
            await orm_update_event(session, AddEvent.event_for_change.id, data)
            await message.answer("Собысие изменено!",
                                 reply_markup=kb.start_kb_admin.as_markup(resize_keyboard=True))
        else:
            await orm_add_event(session, data)
            await message.answer("Собысие добавлено!",
                                 reply_markup=kb.start_kb_admin.as_markup(resize_keyboard=True))
        await state.clear()
        AddEvent.event_for_change = None
    except Exception as error:
        await message.answer(f"Ошибка:\n{str(error)}\nВы ввели недопустимые значения. "
                             f"Напиши количество участников, цифрами! Если количество не ограничено, напиши 0",
                             reply_markup=kb.start_kb_admin.as_markup(resize_keyboard=True))


@admin_router.message(StateFilter(AddEvent.number_participants))
async def add_number_participants_admin(message: types.Message, state: FSMContext):
    await message.answer("Что то пошло не так! Напиши количество участников, цифрами! "
                         "Если количество не ограничено, напиши 0!")
