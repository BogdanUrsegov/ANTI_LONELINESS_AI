from datetime import datetime, timedelta
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.database.utils.ai.context_manager import save_message
from bot.scheduler.tasks.first_generated_message import first_generated_message
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
    DAY_TOUCHES_ENABLED_CALL, DAY_TOUCHES_DISABLED_CALL
)

from bot.database.utils.update_user_field import update_user_fields
from bot.modules.mini_form import SET_SETTINGS_CALL


logger = logging.getLogger(__name__)

router = Router()

# --- Запуск настройки (редактируем исходное сообщение) ---
@router.callback_query(F.data == SET_SETTINGS_CALL)
async def start_notification_setup(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🌤️ <b>Давай настроим, когда мне лучше писать тебе.</b>\n\n"
        "Это важно, чтобы я не был навязчивым.\n\n"
        "🔔 <b>Утро</b>\n"
        "Хочешь, чтобы я писал тебе утром?",
        reply_markup=morning_setting_keyboard
    )
    await state.set_state(NotificationSettings.morning_choice)
    await callback.answer("🕗 Начинаем настройку уведомлений")


# --- Утро: Да → выбор времени (редактируем то же сообщение) ---
@router.callback_query(NotificationSettings.morning_choice, F.data == MORNING_ENABLED_CALL)
async def morning_enabled(callback: CallbackQuery, state: FSMContext):
    await state.update_data(morning_enabled=True)
    await callback.message.edit_text(
        "📌 <b>Выбери удобное утреннее время:</b>",
        reply_markup=morning_time_keyboard
    )
    await state.set_state(NotificationSettings.morning_time_input)
    await callback.answer("✅ Утро: включено")


# --- Утро: Нет → сразу к вечеру ---
@router.callback_query(NotificationSettings.morning_choice, F.data == MORNING_DISABLED_CALL)
async def morning_disabled(callback: CallbackQuery, state: FSMContext):
    await state.update_data(morning_enabled=False, morning_time=None)
    await callback.message.edit_text(
        "🌙 <b>Вечер</b>\n\n"
        "А вечером хочешь получать сообщения?",
        reply_markup=evening_setting_keyboard
    )
    await state.set_state(NotificationSettings.evening_choice)
    await callback.answer("❌ Утро: отключено")


# --- Выбор времени утром ---
@router.callback_query(NotificationSettings.morning_time_input, F.data.startswith("morning_time:"))
async def process_morning_time(callback: CallbackQuery, state: FSMContext):
    time_key = callback.data.split(":", 1)[1]
    time_map = {
        "7": "🕖 7:00–8:30",
        "8": "🕗 8:30–10:00",
        "10": "🕙 10:00–11:30"
    }
    await state.update_data(morning_time=time_key)
    await callback.message.edit_text(
        "🌙 <b>Вечер</b>\n\n"
        "А вечером хочешь получать сообщения?",
        reply_markup=evening_setting_keyboard
    )
    await state.set_state(NotificationSettings.evening_choice)
    await callback.answer(f"✅ Утро: {time_key}")


# --- Кнопка "Назад" из выбора времени ---
@router.callback_query(NotificationSettings.morning_time_input, F.data == "back_to_morning_choice")
async def back_to_morning_choice(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔔 <b>Утро</b>\n"
        "Хочешь, чтобы я писал тебе утром?",
        reply_markup=morning_setting_keyboard
    )
    await state.set_state(NotificationSettings.morning_choice)
    await callback.answer("↩️ Возврат к выбору утра")


# --- Вечер: Да / Нет ---
@router.callback_query(NotificationSettings.evening_choice, F.data == EVENING_ENABLED_CALL)
async def evening_enabled(callback: CallbackQuery, state: FSMContext):
    await state.update_data(evening_enabled=True)
    await callback.message.edit_text(
        "🕊️ <b>Дневные касания</b>\n\n"
        "Иногда я могу писать тебе днём — коротко, без давления.\n"
        "Хочешь?",
        reply_markup=day_touches_keyboard
    )
    await state.set_state(NotificationSettings.day_touches_choice)
    await callback.answer("✅ Вечер: включено")


@router.callback_query(NotificationSettings.evening_choice, F.data == EVENING_DISABLED_CALL)
async def evening_disabled(callback: CallbackQuery, state: FSMContext):
    await state.update_data(evening_enabled=False)
    await callback.message.edit_text(
        "🕊️ <b>Дневные касания</b>\n\n"
        "Иногда я могу писать тебе днём — коротко, без давления.\n"
        "Хочешь?",
        reply_markup=day_touches_keyboard
    )
    await state.set_state(NotificationSettings.day_touches_choice)
    await callback.answer("❌ Вечер: отключено")


# --- Дневные касания: Да / Нет → финал ---
@router.callback_query(NotificationSettings.day_touches_choice, F.data == DAY_TOUCHES_ENABLED_CALL)
async def day_touches_enabled(callback: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler):
    await state.update_data(day_touches=True)
    await _finish_setup(callback, state, scheduler)
    await callback.answer("✅ Дневные касания: включены")


@router.callback_query(NotificationSettings.day_touches_choice, F.data == DAY_TOUCHES_DISABLED_CALL)
async def day_touches_disabled(callback: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler):
    await state.update_data(day_touches=False)
    await _finish_setup(callback, state, scheduler)
    await callback.answer("❌ Дневные касания: отключены")


# --- Финальное сохранение (редактируем исходное сообщение) ---
async def _finish_setup(callback: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler):
    data = await state.get_data()
    
    # Сохранение в БД
    await update_user_fields(
        
        telegram_id=callback.from_user.id,
        notify_morning=data.get("morning_enabled"),
        notify_morning_time=data.get("morning_time"),
        notify_evening=data.get("evening_enabled"),
        notify_day_touches=data.get("day_touches"),
        is_complete=True
    )
    
    # Редактируем ИСХОДНОЕ сообщение на финальное
    await callback.message.edit_text(
        "✅ <b>Настройки сохранены!</b>\n\n"
        "<i>Спасибо, что сказал мне, когда тебе удобно писать!</i>\n\n"
        "<b>🎯 Ты в деле!</b>\n\n"
        "<i>Все подготовительные шаги позади — добро пожаловать в основной функционал!</i>",
        reply_markup=goto_main_menu_kb
    )
    
    await state.clear()
    
    # Планирование первого сообщения
    user_id = callback.from_user.id
    text_for_scheduler = (
        "Я просто хотел сказать, что не надо быть сильным всё время.\n\n"
        "Как ты сейчас?"
    )
    await save_message(user_id, "assistant", text_for_scheduler, None)

    job_id = f"first_generated_message_{user_id}"
    run_time = datetime.now() + timedelta(seconds=15)
    scheduler.add_job(
        func=first_generated_message,       # Функция, которую вызовем
        trigger='date',                # Тип: однократный запуск в дату
        run_date=run_time,             # Конкретное время запуска
        id=job_id,                     # ID для управления
        kwargs={'user_id': user_id},
        replace_existing=True
    )

    logger.info(f"Создана задача для планировщика: {job_id}")