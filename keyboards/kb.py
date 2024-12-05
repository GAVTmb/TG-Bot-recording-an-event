from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

del_kb = ReplyKeyboardRemove()


start_kb_admin = ReplyKeyboardBuilder()
start_kb_admin.add(
    KeyboardButton(text="Добавить событие"),
    KeyboardButton(text="Посмотреть события"),
    KeyboardButton(text="Выход"),
)
start_kb_admin.adjust(2, 1)


kb_cancel_admin = ReplyKeyboardBuilder()
kb_cancel_admin.add(
    KeyboardButton(text="Отменить"),
    KeyboardButton(text="Назад_"),
)
kb_cancel_admin.adjust(2,)


kb_skip_admin = ReplyKeyboardBuilder()
kb_skip_admin.attach(kb_cancel_admin)
kb_skip_admin.row(KeyboardButton(text="Пропустить"),)


start_kb_user = ReplyKeyboardBuilder()
start_kb_user.add(
    KeyboardButton(text="Посмотреть все события"),
    KeyboardButton(text="Записаться на предстоящее"),
    KeyboardButton(text="Оставить отзыв"),
)
start_kb_user.adjust(2, 1)


kb_cancel_user = ReplyKeyboardBuilder()
kb_cancel_user.add(
    KeyboardButton(text="Отмена"),
)
kb_cancel_admin.adjust(1,)

kb_cancel_back_user = ReplyKeyboardBuilder()
kb_cancel_back_user.attach(kb_cancel_user)
kb_cancel_back_user.row(KeyboardButton(text="Назад"),)
