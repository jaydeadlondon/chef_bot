from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from states.recipe import RecipeStates
from services.ai_service import AIService
from database.repositories import RecipeRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()


@router.message(F.text.contains("Найти рецепт"))
async def start_wizard(message: types.Message, state: FSMContext):
    await state.set_state(RecipeStates.waiting_for_ingredients)
    await message.answer(
        "Что есть в холодильнике?", reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(RecipeStates.waiting_for_ingredients)
async def process_ingredients(message: types.Message, state: FSMContext):
    await state.update_data(ingredients=message.text)
    await state.set_state(RecipeStates.waiting_for_preferences)
    await message.answer("Любые пожелания (веган, без соли и т.д.)?")


@router.message(RecipeStates.waiting_for_preferences)
async def process_prefs(message: types.Message, state: FSMContext):
    await state.update_data(preferences=message.text)
    await state.set_state(RecipeStates.waiting_for_servings)
    await message.answer("На сколько человек?")


@router.message(RecipeStates.waiting_for_servings)
async def process_finish(
    message: types.Message, state: FSMContext, ai_service: AIService
):
    data = await state.get_data()
    wait_msg = await message.answer("Шеф готовит ответ... ⏳")

    prompt = f"Продукты: {data['ingredients']}, предпочтения: {data['preferences']}, порции: {message.text}"
    recipe_text = await ai_service.get_recipe_suggestions(prompt)

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="⭐ Сохранить в избранное", callback_data="save_recipe"
                )
            ]
        ]
    )

    await wait_msg.delete()
    await message.answer(recipe_text, reply_markup=kb)
    await state.clear()


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
