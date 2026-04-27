from aiogram import Router, types
from services.ai_service import AIService
import logging

router = Router()


@router.message()
async def handle_ingredients(message: types.Message, ai_service: AIService):
    wait_message = await message.answer("Шеф думает над рецептом...👨‍🍳")

    try:
        recipe = await ai_service.get_recipe_suggestions(message.text)
        await wait_message.edit_text(recipe)
    except Exception as e:
        await wait_message.edit_text(
            "Произошла ошибка при обращении к Шефу. Попробуйте позже."
        )
        logging.error(f"AI Error: {e}")
