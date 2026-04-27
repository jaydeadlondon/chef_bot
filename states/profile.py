from aiogram.fsm.state import StatesGroup, State


class ProfileStates(StatesGroup):
    waiting_for_bio = State()
