from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from bot.database.utils.get_pause_remaining_text import get_pause_status_text
from bot.database.utils.reset_user_pause import reset_user_pause
from bot.database.utils.set_user_pause import set_user_pause
from ..keyboards.inline_keyboards import pause_period_kb, remove_pause_kb, PAUSE_1D_CALL, PAUSE_FOREVER_CALL, PAUSE_WEEK_CALL, REMOVE_PAUSE_CALL
from bot.modules.main_menu import PAUSE_CALL


router = Router()


@router.callback_query(F.data == PAUSE_CALL)
async def pause_menu(callback: types.CallbackQuery, state: FSMContext):
    pause_period = await get_pause_status_text(callback.from_user.id)
    if pause_period:
        await callback.message.edit_text(
            "✋ <b>На паузе</b>\n\n"
            f"<i>До конца паузы: {pause_period}</i>",
            reply_markup=remove_pause_kb
        )
        await callback.answer(f"До конца паузы: {pause_period}")
    else:
        await callback.message.edit_text(
            "<b>Иногда полезно сделать паузу</b>\n\n"

            "<i>Я не буду писать, пока ты не захочешь продолжить</i>",
            reply_markup=pause_period_kb
        )
        await callback.answer()

@router.callback_query(F.data == REMOVE_PAUSE_CALL)
async def remove_pause_menu(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    success = await reset_user_pause(user_id)
    if success:
        await callback.message.edit_text(
            "<b>Иногда полезно сделать паузу</b>\n\n"

            "<i>Я не буду писать, пока ты не захочешь продолжить</i>",
            reply_markup=pause_period_kb
        )
        await callback.answer("Снял c паузы")
    else:
        await callback.answer("Не получилось снять с паузы")
        

@router.callback_query(F.data == PAUSE_1D_CALL)
async def pause_1d(callback: types.CallbackQuery, state: FSMContext):
    success = await set_user_pause(callback.from_user.id, days=1)
    if success:
        await callback.message.edit_text(
            "⏸️ <b>Пауза на день</b>\n\n"
            "<i>Я буду молчать до истечения паузы. Скучать не буду — обещаю 😉</i>\n\n"
            "<i>Ты можешь вручную снять с паузы</i>",
            reply_markup=remove_pause_kb
        )
        await callback.answer("Пауза на день")
    else:
        await callback.answer("❌ Ошибка установки паузы.")


@router.callback_query(F.data == PAUSE_WEEK_CALL)
async def pause_week(callback: types.CallbackQuery, state: FSMContext):
    success = await set_user_pause(callback.from_user.id, days=7)
    if success:
        await callback.message.edit_text(
            "⏸️ <b>Пауза на неделю</b>\n\n"
            "Я буду молчать до истечения паузы. Скучать не буду — обещаю 😉\n\n"
            "<i>Ты можешь вручную снять с паузы</i>",
            reply_markup=remove_pause_kb
        )
        await callback.answer("Пауза на неделю")
    else:
        await callback.answer("❌ Ошибка установки паузы.")


@router.callback_query(F.data == PAUSE_FOREVER_CALL)
async def pause_forever(callback: types.CallbackQuery, state: FSMContext):
    success = await set_user_pause(callback.from_user.id, days=9999)
    if success:
        await callback.message.edit_text(
            "⏸️ <b>Пауза на неопределённое время</b>\n\n"
            "<i>Я подожду, пока ты не захочешь вернуться. Просто напиши — и я буду рядом 💙</i>\n\n"
            "<i>Ты можешь вручную снять с паузы</i>",
            reply_markup=remove_pause_kb
        )
        await callback.answer("Пауза на неопределённое время")
    else:
        await callback.answer("❌ Ошибка установки паузы.")