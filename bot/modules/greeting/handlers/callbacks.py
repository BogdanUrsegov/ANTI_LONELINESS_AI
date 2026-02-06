from aiogram.types import CallbackQuery
from aiogram import F, Router
from ..keyboards.inline_keyboards import FURTHER_CALL, WHAT_CAN_CALL, continue_kb


router = Router()


@router.callback_query(F.data == WHAT_CAN_CALL)
async def what_call_handler(callback: CallbackQuery):
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "<b>Я могу:</b>\n\n"

        "<i>✍️ писать тебе утром и вечером</i>\n"
        "<i>🧠 помнить важные для тебя вещи</i>\n"
        "<i>💬 поддерживать, когда трудно</i>\n"
        "<i>🤍 быть спокойным собеседником</i>\n\n"

        "<u>Я не лечу и не даю диагнозов</u>",
        reply_markup=continue_kb
    )
    await callback.answer()