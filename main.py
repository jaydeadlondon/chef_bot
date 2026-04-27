import asyncio
import logging
from aiogram import Bot, Dispatcher
from core.config import config
from handlers import common, recipes
from services.ai_service import GigaChatService
from database.engine import init_db


async def main():
    logging.basicConfig(level=logging.INFO)

    await init_db()

    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    ai_service = GigaChatService()

    dp.include_router(common.router)
    dp.include_router(recipes.router)

    await dp.start_polling(bot, ai_service=ai_service)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
