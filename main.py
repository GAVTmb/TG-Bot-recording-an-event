import asyncio
import os

from aiogram import Bot, Dispatcher

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from database.engine import create_db, session_maker, drop_db

from middlewares.db import DataBaseSession

from handlers.admin import admin_router
from handlers.user import user_router


bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

dp.include_router(admin_router)
dp.include_router(user_router)


async def main():
    # await drop_db()
    await create_db()
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
