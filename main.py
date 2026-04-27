import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from redis.asyncio import Redis

from core.config import config
from database.engine import init_db, async_session
from handlers import common, recipes, profile
from services.ai_service import GigaChatService
from middlewares.db_middleware import DbSessionMiddleware


async def setup_bot_commands(bot: Bot):
    main_commands = [
        BotCommand(command="/start", description="Запустить бота / В главное меню"),
        BotCommand(command="/my_recipes", description="Мои сохраненные рецепты"),
        BotCommand(
            command="/profile", description="Мои предпочтения (аллергии, диеты)"
        ),
    ]
    await bot.set_my_commands(main_commands)


async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()

    redis = Redis(host=config.redis_host, port=config.redis_port)
    storage = RedisStorage(redis=redis)

    bot = Bot(
        token=config.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    await setup_bot_commands(bot)

    dp = Dispatcher(storage=storage)

    dp.update.outer_middleware(DbSessionMiddleware(async_session))

    dp.include_router(common.router)
    dp.include_router(recipes.router)
    dp.include_router(profile.router)

    ai_service = GigaChatService()
    await dp.start_polling(bot, ai_service=ai_service)


if __name__ == "__main__":
    asyncio.run(main())
