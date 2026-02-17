from aiogram import Router, types
from aiogram.filters import Command
from ..keyboards.inline_keyboards import main_menu_keyboard
from bot.database.utils import user_checker, add_user
from ..keyboards.inline_keyboards import main_menu_keyboard


router = Router()


@router.message(Command("menu"))
async def cmd_menu(message: types.Message):
    await message.answer("⚙️ <b>Меню</b>", reply_markup=main_menu_keyboard)
