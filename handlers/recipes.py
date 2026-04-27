from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from states.recipe import RecipeStates
from services.ai_service import AIService

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
    await message.answer("Шеф готовит ответ... ⏳")
    prompt = f"Продукты: {data['ingredients']}, предпочтения: {data['preferences']}, порции: {message.text}"
    res = await ai_service.get_recipe_suggestions(prompt)
    await message.answer(res)
    await state.clear()
