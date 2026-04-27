from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.repositories import UserRepository
from states.profile import ProfileStates
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()


@router.message(Command("profile"))
async def show_profile(message: types.Message, session: AsyncSession):
    repo = UserRepository(session)
    user = await repo.get_user(message.from_user.id)

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="⚙️ Изменить настройки", callback_data="edit_profile"
                )
            ]
        ]
    )

    await message.answer(
        f"<b>Ваш профиль:</b>\n\n"
        f"👤 Имя: {user.username or 'Не указано'}\n"
        f"🥗 Предпочтения: {user.preferences}\n\n"
        "Эти данные учитываются при каждом поиске рецептов.",
        reply_markup=kb,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "edit_profile")
async def edit_profile(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ProfileStates.waiting_for_bio)
    await callback.message.answer(
        "Напишите ваши предпочтения в еде одним сообщением.\n"
        "Например: <i>'Я вегетарианец, у меня аллергия на арахис, не люблю лук'</i>",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(ProfileStates.waiting_for_bio)
async def save_profile(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    repo = UserRepository(session)
    await repo.update_preferences(message.from_user.id, message.text)
    await state.clear()
    await message.answer("✅ Настройки профиля сохранены!")
