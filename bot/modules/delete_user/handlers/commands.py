from aiogram import Router, types
from aiogram.filters import Command
from bot.database.utils import delete_user_by_telegram_id


router = Router()


@router.message(Command("delete_me"))
async def cmd_delete_me(message: types.Message):
    user_id = message.from_user.id
    await delete_user_by_telegram_id(telegram_id=user_id)
    await message.answer("Удален")
