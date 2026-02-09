from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.utils import user_checker, add_user, is_complete
from bot.modules.main_menu import goto_main_menu_kb
from ..keyboards.inline_keyboards import start_menu, fill_again_kb


router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, session: AsyncSession):
    telegram_id = message.from_user.id
    text_message = (
            "<b>Я — AI-компаньон для эмоциональной поддержки и регулярного общения</b>\n\n"
            "<i>Я не психолог и не заменяю людей, но могу быть рядом и поддерживать тебя каждый день</i>"
        )

    # Проверяем, существует ли пользователь
    is_user = await user_checker(session, telegram_id)

    if not is_user:
        # Создаём нового пользователя
        await add_user(session, telegram_id)
        await message.answer(
            text_message,
            reply_markup=start_menu
        )
    else:
        if await is_complete(session, telegram_id):
            await message.answer(
                text_message,
                reply_markup=goto_main_menu_kb
            )
        else:
            await message.answer(
                text_message,
                reply_markup=fill_again_kb
            )