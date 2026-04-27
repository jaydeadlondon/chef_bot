import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from redis.asyncio import Redis

from core.config import config
from database.engine import init_db, async_session
from handlers import common, recipes
from services.ai_service import GigaChatService
from middlewares.db_middleware import DbSessionMiddleware


async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()

    redis = Redis(host=config.redis_host, port=config.redis_port)
    storage = RedisStorage(redis=redis)

    bot = Bot(
        token=config.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    dp = Dispatcher(storage=storage)

    dp.message.middleware(DbSessionMiddleware(async_session))

    dp.include_router(common.router)
    dp.include_router(recipes.router)

    ai_service = GigaChatService()
    await dp.start_polling(bot, ai_service=ai_service)


if __name__ == "__main__":
    asyncio.run(main())
