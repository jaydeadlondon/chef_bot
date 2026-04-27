from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from states.recipe import RecipeStates
from services.ai_service import AIService
from database.repositories import RecipeRepository, UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
import asyncio
from handlers.common import get_main_kb

router = Router()


def is_refusal(text: str) -> bool:
    stop_phrases = [
        "чувствительные темы",
        "не обладают собственным мнением",
        "разговоры на чувствительные темы",
        "извините, я не могу",
        "некорректный запрос",
    ]
    return any(phrase in text.lower() for phrase in stop_phrases)


@router.message(F.text.contains("Найти рецепт"))
async def start_wizard(message: types.Message, state: FSMContext):
    await state.set_state(RecipeStates.waiting_for_ingredients)
    await message.answer(
        "Что есть в холодильнике?", reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(RecipeStates.waiting_for_ingredients)
async def process_ingredients(message: types.Message, state: FSMContext):
    if len(message.text) < 3:
        await message.answer(
            "Слишком короткое название. Напишите подробнее, что у вас есть?"
        )
        return

    await state.update_data(ingredients=message.text)
    await state.set_state(RecipeStates.waiting_for_preferences)
    await message.answer("Любые пожелания (веган, без соли и т.д.)?")


@router.message(RecipeStates.waiting_for_preferences)
async def process_prefs(message: types.Message, state: FSMContext):
    await state.update_data(preferences=message.text)
    await state.set_state(RecipeStates.waiting_for_servings)
    await message.answer("На сколько человек?")


@router.message(RecipeStates.waiting_for_servings)
async def process_servings(
    message: types.Message,
    state: FSMContext,
    ai_service: AIService,
    session: AsyncSession,
):
    data = await state.get_data()
    user_repo = UserRepository(session)
    user = await user_repo.get_user(message.from_user.id)

    wait_msg = await message.answer(
        "Шеф составляет рецепт, учитывая ваши пожелания... ⏳"
    )

    prompt = (
        f"Продукты: {data.get('ingredients')}. "
        f"Разовые пожелания: {data.get('preferences')}. "
        f"Постоянные ограничения профиля: {user.preferences}. "
        f"Порций: {message.text}."
    )

    try:
        recipe_text = await ai_service.get_recipe_suggestions(prompt)

        await wait_msg.delete()

        if is_refusal(recipe_text):
            await message.answer(
                "🤨 Похоже, эти продукты не слишком съедобные. Попробуйте другие."
            )
            await state.clear()
            return

        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="⭐ Сохранить", callback_data="save_recipe"
                    ),
                    types.InlineKeyboardButton(
                        text="📋 Список покупок", callback_data="get_shopping_list"
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        text="⏱️ Засечь время", callback_data="set_timer"
                    ),
                    types.InlineKeyboardButton(
                        text="⬅️ Назад", callback_data="start_new_search"
                    ),
                ],
            ]
        )

        await message.answer(recipe_text, reply_markup=kb, parse_mode="MARKDOWN")
        await state.clear()

    except Exception as e:
        logging.error(f"AI Service Error: {e}")
        await wait_msg.edit_text(
            "❌ Произошла ошибка при связи с Шефом. Попробуйте через минуту."
        )
        await state.clear()


@router.message(RecipeStates.waiting_for_timer)
async def start_timer(message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await state.clear()
        from handlers.common import get_main_kb

        await message.answer("Таймер отменен.", reply_markup=get_main_kb())
        return

    try:
        minutes = int("".join(filter(str.isdigit, message.text)))
    except ValueError:
        await message.answer("Пожалуйста, введите число минут (например, 15).")
        return

    if minutes <= 0 or minutes > 180:
        await message.answer("Введите время от 1 до 180 минут.")
        return

    from handlers.common import get_main_kb

    await message.answer(
        f"✅ Таймер запущен на {minutes} мин! Я напишу, когда время выйдет.",
        reply_markup=get_main_kb(),
    )
    await state.clear()

    asyncio.create_task(timer_worker(message, minutes))


async def timer_worker(message: types.Message, minutes: int):
    await asyncio.sleep(minutes * 60)
    await message.answer(
        f"🔔 **ВРЕМЯ ВЫШЛО! ({minutes} мин)**\nПора проверить ваше блюдо! 👨‍🍳"
    )


@router.callback_query(F.data == "save_recipe")
async def save_to_favorites(callback: types.CallbackQuery, session: AsyncSession):
    repo = RecipeRepository(session)

    recipe_text = callback.message.text
    title = recipe_text.split("\n")[0][:50]

    await repo.save_recipe(
        tg_id=callback.from_user.id, title=title, content=recipe_text
    )

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.answer("Рецепт сохранен!")
    await callback.message.answer(
        "✅ Рецепт в вашей кулинарной книге. Что дальше?", reply_markup=get_main_kb()
    )


@router.callback_query(F.data.startswith("view_"))
async def view_recipe(callback: types.CallbackQuery, session: AsyncSession):
    recipe_id = int(callback.data.split("_")[1])
    repo = RecipeRepository(session)
    recipe = await repo.get_recipe_by_id(recipe_id)

    if not recipe:
        await callback.answer("Рецепт не найден.")
        return

    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text="🗑 Удалить", callback_data=f"delete_{recipe.id}"
        )
    )
    kb.row(
        types.InlineKeyboardButton(
            text="⬅️ Назад к списку", callback_data="back_to_list"
        )
    )

    await callback.message.edit_text(
        recipe.content, reply_markup=kb.as_markup(), parse_mode="MARKDOWN"
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_list")
async def back_to_list(callback: types.CallbackQuery, session: AsyncSession):
    from handlers.common import show_favorites_logic

    await show_favorites_logic(callback.message, callback.from_user.id, session)
    await callback.answer()


@router.callback_query(F.data == "start_new_search")
async def start_new_search(callback: types.CallbackQuery):
    await callback.message.answer("Выберите действие в меню ниже 👇")
    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data.startswith("delete_"))
async def delete_recipe(callback: types.CallbackQuery, session: AsyncSession):
    recipe_id = int(callback.data.split("_")[1])
    repo = RecipeRepository(session)
    await repo.delete_recipe(recipe_id)
    await callback.answer("Рецепт удален!")
    await back_to_list(callback, session)


@router.callback_query(F.data == "get_shopping_list")
async def shopping_list_callback(callback: types.CallbackQuery, ai_service: AIService):
    await callback.answer("Составляю список... 🛒")

    recipe_text = callback.message.text

    try:
        shopping_list = await ai_service.get_shopping_list(recipe_text)

        await callback.message.answer(
            f"🛒 **Ваш список покупок:**\n\n{shopping_list}", parse_mode="MARKDOWN"
        )
    except Exception as e:
        logging.error(f"Shopping List Error: {e}")
        await callback.message.answer(
            "❌ Не удалось составить список покупок. Попробуйте вручную."
        )


@router.callback_query(F.data == "set_timer")
async def timer_request(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(RecipeStates.waiting_for_timer)

    builder = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="5 мин"), types.KeyboardButton(text="10 мин")],
            [types.KeyboardButton(text="20 мин"), types.KeyboardButton(text="30 мин")],
            [types.KeyboardButton(text="Отмена")],
        ],
        resize_keyboard=True,
    )

    await callback.message.answer(
        "На сколько минут завести таймер?", reply_markup=builder
    )
    await callback.answer()
