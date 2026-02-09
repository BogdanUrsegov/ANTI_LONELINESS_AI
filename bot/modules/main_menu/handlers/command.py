from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from ..keyboards.inline_keyboards import main_menu_keyboard
from bot.database.utils import user_checker, add_user
from ..keyboards.inline_keyboards import start_menu


router = Router()


@router.message(Command("menu"))
async def cmd_menu(message: types.Message, session: AsyncSession):
    await message.answer("⚙️ <b>Меню</b>", reply_markup=main_menu_keyboard)
