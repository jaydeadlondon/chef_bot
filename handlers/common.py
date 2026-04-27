from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from database.repositories import RecipeRepository, UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.clear()

    repo = UserRepository(session)
    await repo.get_or_create_user(message.from_user.id, message.from_user.username)

    kb = [
        [types.KeyboardButton(text="Найти рецепт 🍳")],
        [
            types.KeyboardButton(text="👤 Мой профиль"),
            types.KeyboardButton(text="⭐ Избранное"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Привет! Я твой Шеф-бот. Что сделаем?", reply_markup=keyboard)


@router.message(F.text == "/my_recipes")
@router.message(Command("my_recipes"))
async def show_favorites(message: types.Message, session: AsyncSession):
    repo = RecipeRepository(session)
    recipes = await repo.get_user_recipes(message.from_user.id)

    if not recipes:
        await message.answer(
            "У вас пока нет сохраненных рецептов. Сначала приготовьте что-нибудь! 👨‍🍳"
        )
        return

    builder = InlineKeyboardBuilder()
    for r in recipes:
        builder.row(
            types.InlineKeyboardButton(text=r.title, callback_data=f"view_{r.id}")
        )

    await message.answer(
        "<b>Ваша кулинарная книга:</b>\nВыберите рецепт для просмотра:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.message(F.text == "👤 Мой профиль")
async def profile_btn(message: types.Message, session: AsyncSession):
    from handlers.profile import show_profile

    await show_profile(message, session)


@router.message(F.text == "⭐ Избранное")
async def favorites_btn(message: types.Message, session: AsyncSession):
    from handlers.common import show_favorites

    await show_favorites(message, session)
