from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from ..keyboards.inline_keyboards import pause_period_kb, PAUSE_1D_CALL, PAUSE_FOREVER_CALL, PAUSE_WEEK_CALL
from bot.modules.main_menu import PAUSE_CALL


router = Router()


@router.callback_query(F.data == PAUSE_CALL)
async def callback_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>Иногда полезно сделать паузу</b>\n\n"

        "<i>Я не буду писать, пока ты не захочешь продолжить</i>",
        reply_markup=pause_period_kb)
    await callback.answer()


@router.callback_query(F.data == PAUSE_1D_CALL)
async def pause_1d(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "⏸️ <b>Пауза на 1 день</b>\n\n"
        "Я буду молчать до завтра. Скучать не буду — обещаю 😉",
        reply_markup=pause_period_kb
    )


@router.callback_query(F.data == PAUSE_WEEK_CALL)
async def pause_week(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "⏸️ <b>Пауза на неделю</b>\n\n"
        "До встречи через 7 дней! Отдыхай и набирайся сил 🌿",
        reply_markup=pause_period_kb
    )


@router.callback_query(F.data == PAUSE_FOREVER_CALL)
async def pause_forever(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "⏸️ <b>Пауза на неопределённое время</b>\n\n"
        "Я подожду, пока ты сам(а) захочешь вернуться. Просто напиши — и я буду рядом 💙",
        reply_markup=pause_period_kb
    )