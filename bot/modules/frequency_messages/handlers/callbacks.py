from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.utils.update_user_field import update_user_fields
from bot.database.utils.get_user_field import get_user_field
from bot.modules.main_menu import MESSAGE_FREQUENCY_CALL
from ..keyboards.inline_keyboards import (
    get_morning_keyboard,
    get_evening_keyboard,
    get_daytime_keyboard,
    reminder_slot_selection_keyboard,
    MORNING_MESSAGES_CALL,
    NIGHT_MESSAGES_CALL,
    DAILY_MESSAGES_CALL,
    MORNING_ON_CALL,
    MORNING_OFF_CALL,
    EVENING_ON_CALL,
    EVENING_OFF_CALL,
    DAYTIME_RARE_CALL,
    DAYTIME_NONE_CALL,
    TIME_7_830_CALL,
    TIME_830_10_CALL,
    TIME_10_1130_CALL
)
import logging


logging.getLogger(__name__)

router = Router()


# --- Вход в настройку напоминаний ---
@router.callback_query(F.data == MESSAGE_FREQUENCY_CALL)
async def show_reminder_slot_selection(callback: CallbackQuery):
    await callback.message.edit_text(
        "🌤️ <b>Когда тебе удобно получать сообщения?</b>\n\n"
        "Выбери подходящее время суток:",
        reply_markup=reminder_slot_selection_keyboard
    )
    await callback.answer()


# --- Утро ---
@router.callback_query(F.data == MORNING_MESSAGES_CALL)
async def handle_morning_selection(callback: CallbackQuery, session: AsyncSession):
    telegram_id = callback.from_user.id
    is_enabled = await get_user_field(session, telegram_id, "notify_morning") or False
    notify_morning_time = await get_user_field(session, telegram_id, "notify_morning_time")
    logging.debug(f"Выбранное время: {notify_morning_time}")
    await callback.message.edit_text(
        "🌅 <b>Утренние напоминания</b>\n\n"
        "Хочешь, чтобы я писал тебе утром?",
        reply_markup=get_morning_keyboard(is_enabled=bool(is_enabled), selected_time=notify_morning_time)
    )
    await callback.answer()


# --- Вечер ---
@router.callback_query(F.data == NIGHT_MESSAGES_CALL)
async def handle_evening_selection(callback: CallbackQuery, session: AsyncSession):
    is_enabled = await get_user_field(session, callback.from_user.id, "notify_evening") or False
    await callback.message.edit_text(
        "🌃 <b>Вечерние напоминания</b>\n\n"
        "Хочешь получать сообщения вечером?",
        reply_markup=get_evening_keyboard(is_enabled=bool(is_enabled))
    )
    await callback.answer()


# --- День ---
@router.callback_query(F.data == DAILY_MESSAGES_CALL)
async def handle_daytime_selection(callback: CallbackQuery, session: AsyncSession):
    daytime_mode = await get_user_field(session, callback.from_user.id, "notify_day_touches")
    await callback.message.edit_text(
        "🏙 <b>Дневные касания</b>\n\n"
        "Иногда я могу написать днём — коротко и бережно.\n"
        "Как тебе удобнее?",
        reply_markup=get_daytime_keyboard(is_enabled=daytime_mode)
    )
    await callback.answer()


# --- Переключение утра ---
@router.callback_query(F.data.in_({MORNING_ON_CALL, MORNING_OFF_CALL}))
async def toggle_morning(callback: CallbackQuery, session: AsyncSession):
    telegram_id = callback.from_user.id
    is_now_enabled = callback.data == MORNING_ON_CALL
    notify_morning_time = await get_user_field(session, telegram_id, "notify_morning_time")
    await update_user_fields(
        session=session,
        telegram_id=callback.from_user.id,
        notify_morning=is_now_enabled
    )
    await callback.message.edit_reply_markup(
        reply_markup=get_morning_keyboard(is_enabled=bool(is_now_enabled), selected_time=notify_morning_time)
    )
    await callback.answer("✅ Утро обновлено")


# --- Выбор утреннего времени ---
@router.callback_query(F.data.in_({TIME_7_830_CALL, TIME_830_10_CALL, TIME_10_1130_CALL}))
async def set_morning_time(callback: CallbackQuery, session: AsyncSession):
    time_map = {
        TIME_7_830_CALL: "07:00",
        TIME_830_10_CALL: "08:30",
        TIME_10_1130_CALL: "10:00"
    }
    selected_time = time_map[callback.data]
    await update_user_fields(
        session=session,
        telegram_id=callback.from_user.id,
        notify_morning_time=selected_time
    )

    await callback.message.edit_text(
        "🌅 <b>Утренние напоминания</b>\n\n"
        "Хочешь, чтобы я писал тебе утром?",
        reply_markup=get_morning_keyboard(is_enabled=True, selected_time=selected_time)
    )
    await callback.answer(f"🕗 Выбрано: {selected_time}")


# --- Переключение вечера ---
@router.callback_query(F.data.in_({EVENING_ON_CALL, EVENING_OFF_CALL}))
async def toggle_evening(callback: CallbackQuery, session: AsyncSession):
    is_now_enabled = callback.data == EVENING_ON_CALL
    await update_user_fields(
        session=session,
        telegram_id=callback.from_user.id,
        notify_evening=is_now_enabled
    )
    await callback.message.edit_reply_markup(
        reply_markup=get_evening_keyboard(is_enabled=is_now_enabled)
    )
    await callback.answer("✅ Вечер обновлён")


# --- Выбор режима дня ---
@router.callback_query(F.data.in_({DAYTIME_RARE_CALL, DAYTIME_NONE_CALL}))
async def set_daytime_mode(callback: CallbackQuery, session: AsyncSession):
    is_rare = callback.data == DAYTIME_RARE_CALL
    await update_user_fields(
        session=session,
        telegram_id=callback.from_user.id,
        notify_day_touches=is_rare
    )
    await callback.message.edit_reply_markup(
        reply_markup=get_daytime_keyboard(is_enabled=is_rare)
    )
    label = "Редко" if is_rare else "Нет"
    await callback.answer(f"✅ День: {label}")
