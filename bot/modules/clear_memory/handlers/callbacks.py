from aiogram.types import CallbackQuery
from aiogram import F, Router
from bot.modules.main_menu import CLEAR_MEMORY_CALL
from ..keyboards.inline_keyboards import DELETE_HISTORY_CALL, delete_history_kb
from bot.modules.main_menu.keyboards import goto_main_menu_kb
from bot.database.utils import delete_user_messages


router = Router()


@router.callback_query(F.data == CLEAR_MEMORY_CALL)
async def is_clear_memory_handler(callback: CallbackQuery):
    await callback.message.edit_text(
            "<b>Я забуду личные детали, которые были в нашем диалоге</b>\n\n"

            "<i>Ты точно хочешь этого?</i>",
            reply_markup=delete_history_kb
        )
    await callback.answer()

@router.callback_query(F.data == DELETE_HISTORY_CALL)
async def clear_memory_handler(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    try:
        await delete_user_messages(telegram_id)
        await callback.message.edit_text(
            "<b>Я больше не помню личные детали, но по-прежнему рядом и на связи.</b>",
            reply_markup=goto_main_menu_kb
        )
    except:
        await callback.message.edit_text(
            "<i>Не получилось очистить память</i>",
            reply_markup=goto_main_menu_kb
        )
    await callback.answer()