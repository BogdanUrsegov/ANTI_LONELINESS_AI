from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.utils import user_checker, add_user
from ..keyboards.inline_keyboards import start_menu


router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, session: AsyncSession):
    await message.answer(
        "Приветствуем!",
        reply_markup=start_menu
    )
        
    telegram_id = message.from_user.id

    # Проверяем, существует ли пользователь
    is_user = await user_checker(session, telegram_id)

    if not is_user:
        # Создаём нового пользователя
        await add_user(session, telegram_id)