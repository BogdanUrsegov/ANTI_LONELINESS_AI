from aiogram import F, Router
from aiogram.types import CallbackQuery
from ..keyboards.inline_keyboards import archetype_kb
from bot.modules.age_gate import ADULT_CALL


router = Router()


@router.callback_query(F.data == ADULT_CALL)
async def adult_handler(callback: CallbackQuery):
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "<b>Какой формат общения тебе сейчас ближе?</b>\n\n"

        "<i>Выбери того, с кем тебе будет комфортно</i>",
        reply_markup=archetype_kb
    )
    await callback.answer()