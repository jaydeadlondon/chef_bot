from aiogram.fsm.state import StatesGroup, State


class RecipeStates(StatesGroup):
    waiting_for_ingredients = State()
    waiting_for_preferences = State()
    waiting_for_servings = State()
    waiting_for_timer = State()
