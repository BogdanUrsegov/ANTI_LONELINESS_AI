from aiogram.types import CallbackQuery
from aiogram import F, Router
from bot.modules.greeting import FURTHER_CALL
from ..keyboards.inline_keyboards import ADULT_CALL, NOT_ADULT_CALL, is_adult_menu


router = Router()


@router.callback_query(F.data == FURTHER_CALL)
async def is_adult_handler(callback: CallbackQuery):
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "<b>Этот бот предназначен только для взрослых</b>\n\n"

        "<i>Тебе есть 18 лет?</i>",
        reply_markup=is_adult_menu
    )
    await callback.answer()

@router.callback_query(F.data == NOT_ADULT_CALL)
async def not_adult_handler(callback: CallbackQuery):
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "<b>Извини, я не могу продолжить разговор</b>\n\n"

        "<i>Береги себя 🤍</i>"
    )
    await callback.answer()