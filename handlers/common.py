from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from database.repositories import RecipeRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="Найти рецепт 🍳")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Привет! Нажми кнопку, чтобы начать.", reply_markup=keyboard)


@router.message(F.text == "/my_recipes")
@router.message(Command("my_recipes"))
async def show_favorites(message: types.Message, session: AsyncSession):
    repo = RecipeRepository(session)
    recipes = await repo.get_user_recipes(message.from_user.id)

    if not recipes:
        await message.answer("У вас пока нет сохраненных рецептов.")
        return

    response = "<b>Ваши сохраненные рецепты:</b>\n\n"
    for idx, r in enumerate(recipes, 1):
        response += f"{idx}. {r.title}\n"

    response += "\n<i>Чтобы прочитать рецепт полностью, просто нажмите на его название (функция в разработке)</i>"

    await message.answer(response, parse_mode="HTML")
