from aiogram import Router, types
from aiogram.filters import CommandStart
from database.repositories import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, session: AsyncSession):
    repo = UserRepository(session)
    user = await repo.get_or_create_user(
        message.from_user.id, message.from_user.username
    )

    await message.answer(
        f"Привет, {user.username or 'Шеф'}! Я помогу приготовить ужин из того, что есть.\n"
        "Просто пришли мне список продуктов."
    )
