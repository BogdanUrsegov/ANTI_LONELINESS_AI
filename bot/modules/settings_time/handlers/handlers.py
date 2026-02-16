import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.utils.ai.context_manager import save_message
from bot.scheduled_messages import RedisMessageScheduler
from bot.modules.main_menu import goto_main_menu_kb
from ..states.states import NotificationSettings

from ..keyboards.inline_keyboards import (
    morning_setting_keyboard,
    evening_setting_keyboard,
    day_touches_keyboard,
    morning_time_keyboard
)

from ..keyboards.inline_keyboards import (
    MORNING_ENABLED_CALL, MORNING_DISABLED_CALL,
    EVENING_ENABLED_CALL, EVENING_DISABLED_CALL,
    DAY_TOUCHES_ENABLED_CALL, DAY_TOUCHES_DISABLED_CALL,
    MORNING_TIME_7_CALL, MORNING_TIME_8_CALL, MORNING_TIME_10_CALL
)

from bot.database.utils.update_user_field import update_user_fields
from bot.modules.mini_form import SET_SETTINGS_CALL

router = Router()

# --- Запуск настройки ---
@router.callback_query(F.data == SET_SETTINGS_CALL)
async def start_notification_setup(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "🌤️ <b>Давай настроим, когда мне лучше писать тебе.</b>\n\n"
        "Это важно, чтобы я не был навязчивым.\n\n"
        "🔔 <b>Утро</b>\n"
        "Хочешь, чтобы я писал тебе утром?",
        reply_markup=morning_setting_keyboard
    )
    await state.set_state(NotificationSettings.morning_choice)
    await callback.answer()


# --- Утро: Да → показываем слоты ---
@router.callback_query(NotificationSettings.morning_choice, F.data == MORNING_ENABLED_CALL)
async def morning_enabled(callback: CallbackQuery, state: FSMContext):
    await state.update_data(morning_enabled=True)

    opt = {
        MORNING_ENABLED_CALL: "✅ Писать",
        MORNING_DISABLED_CALL: "❌ Не писать"
    }.get(callback.data) or ""
    await callback.message.edit_text(
        f"{callback.message.html_text}\n\n"

        f"<b>{opt}</b>"
        )
    
    await callback.message.answer("📌 <b>Выбери удобное утреннее время:</b>", reply_markup=morning_time_keyboard)
    await state.set_state(NotificationSettings.morning_time_input)
    await callback.answer()


# --- Утро: Нет → пропускаем время ---
@router.callback_query(NotificationSettings.morning_choice, F.data == MORNING_DISABLED_CALL)
async def morning_disabled(callback: CallbackQuery, state: FSMContext):
    await state.update_data(morning_enabled=False, morning_time=None)
    await _ask_evening(callback, state)
    await callback.answer()


# --- Выбор конкретного времени утром ---
@router.callback_query(NotificationSettings.morning_time_input, F.data.startswith("morning_time:"))
async def process_morning_time(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.split(":", 1)[1]
    await state.update_data(morning_time=time_str)
    await _ask_evening(callback, state)
    await callback.answer()


# --- Кнопка "Назад" из выбора времени ---
@router.callback_query(NotificationSettings.morning_time_input, F.data == "back_to_morning_choice")
async def back_to_morning_choice(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔔 <b>Утро</b>\n"
        "Хочешь, чтобы я писал тебе утром?"
    )
    await callback.message.edit_reply_markup(reply_markup=morning_setting_keyboard)
    await state.set_state(NotificationSettings.morning_choice)
    await callback.answer()


# --- Вечер: Да / Нет ---
@router.callback_query(NotificationSettings.evening_choice, F.data == EVENING_ENABLED_CALL)
async def evening_enabled(callback: CallbackQuery, state: FSMContext):
    await state.update_data(evening_enabled=True)
    await _ask_day_touches(callback, state)
    await callback.answer()


@router.callback_query(NotificationSettings.evening_choice, F.data == EVENING_DISABLED_CALL)
async def evening_disabled(callback: CallbackQuery, state: FSMContext):
    await state.update_data(evening_enabled=False)
    await _ask_day_touches(callback, state)
    await callback.answer()


# --- Дневные касания ---
@router.callback_query(NotificationSettings.day_touches_choice, F.data == DAY_TOUCHES_ENABLED_CALL)
async def day_touches_enabled(callback: CallbackQuery, state: FSMContext, session: AsyncSession, scheduler: RedisMessageScheduler):
    await state.update_data(day_touches=True)
    await _finish_setup(callback, state, session, scheduler)
    await callback.answer()


@router.callback_query(NotificationSettings.day_touches_choice, F.data == DAY_TOUCHES_DISABLED_CALL)
async def day_touches_disabled(callback: CallbackQuery, state: FSMContext, session: AsyncSession, scheduler: RedisMessageScheduler):
    await state.update_data(day_touches=False)
    await _finish_setup(callback, state, session, scheduler)
    await callback.answer()


# --- Вспомогательные функции ---

async def _ask_evening(callback: CallbackQuery, state: FSMContext):
    message = callback.message
    callback_data = callback.data

    opt = {
        MORNING_TIME_7_CALL: "🕖 7:00 – 8:30",
        MORNING_TIME_8_CALL: "🕣 8:30 – 10:00",
        MORNING_TIME_10_CALL: "🕙 10:00 – 11:30",
        MORNING_DISABLED_CALL: "❌ Не писать"
    }.get(callback_data) or ""
    await message.edit_text(
        f"{message.html_text}\n\n"

        f"<b>{opt}</b>"
        )
    
    await message.answer(
        "🌙 <b>Вечер</b>\n\n"
        "А вечером?",
        reply_markup=evening_setting_keyboard
    )
    await state.set_state(NotificationSettings.evening_choice)


async def _ask_day_touches(callback: CallbackQuery, state: FSMContext):
    message = callback.message
    callback_data = callback.data

    opt = {
        EVENING_ENABLED_CALL: "✅ Писать",
        EVENING_DISABLED_CALL: "❌ Не писать"
    }.get(callback_data) or ""
    await message.edit_text(
        f"{message.html_text}\n\n"

        f"<b>{opt}</b>"
        )
    
    await message.answer(
        "🕊️ <b>Дневные касания</b>\n\n"
        "Иногда я могу писать тебе днём — коротко, без давления.\n"
        "Хочешь?",
        reply_markup=day_touches_keyboard
    )
    await state.set_state(NotificationSettings.day_touches_choice)


async def _finish_setup(callback: CallbackQuery, state: FSMContext, session: AsyncSession, scheduler: RedisMessageScheduler):
    data = await state.get_data()
    message = callback.message
    callback_data = callback.data

    opt = {
        DAY_TOUCHES_ENABLED_CALL: "✅ Писать",
        DAY_TOUCHES_DISABLED_CALL: "❌ Не писать"
    }.get(callback_data) or ""
    await message.edit_text(
        f"{message.html_text}\n\n"

        f"<b>{opt}</b>"
    )

    await update_user_fields(
        session=session,
        telegram_id=callback.from_user.id,
        notify_morning=data.get("morning_enabled"),
        notify_morning_time=data.get("morning_time"),
        notify_evening=data.get("evening_enabled"),
        notify_day_touches=data.get("day_touches"),
        is_complete=True
    )
    await message.answer(
        "✅ <b>Настройки сохранены!</b>\n\n"
        
        "<i>Спасибо, что сказал мне, когда тебе удобно писать!</i>"
    )

    await state.clear()

    await asyncio.sleep(0.2)

    await message.answer(
        "<b>🎯 Ты в деле!</b>\n\n"
        "<i>Все подготовительные шаги позади — добро пожаловать в основной функционал!</i>",
        reply_markup=goto_main_menu_kb
    )

    user_id = callback.from_user.id
    text_for_scheduler = (
        f"Я просто хотел сказать, что не надо быть сильным всё время.\n\n"

        "Как ты сейчас?"
    )
    await save_message(user_id, "assistant", text_for_scheduler, None, session)
    await scheduler.schedule_message(
        chat_id=user_id,
        text=text_for_scheduler,
        delay_seconds=30,
        user_id=user_id
    )