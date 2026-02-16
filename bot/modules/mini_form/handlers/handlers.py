from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging
from aiogram.enums import ChatAction
from ..states.states import UserNameState, WorryState
from bot.database.utils.update_user_field import update_user_fields
from sqlalchemy.ext.asyncio import AsyncSession
from bot.ai.utils.chat import get_ai_response
from ..keyboards.inline_keyboards import hard_time_keyboard, worry_keyboard, set_settings_keyboard
from ..keyboards.inline_keyboards import (
    MORNING_CALL, DAY_CALL, EVENING_CALL, NIGHT_CALL,
    LONELINESS_CALL, ANXIETY_CALL, RELATIONSHIPS_CALL,
    DISCIPLINE_CALL, OTHER_CALL
)


logger = logging.getLogger(__name__)
router = Router()

# --- Шаг 1: Имя ---
@router.message(UserNameState.waiting_for_name)
async def process_name(message: Message, state: FSMContext, bot: Bot):
    name = message.text.strip()
    if not name:
        await message.answer("🫣 Пожалуйста, напиши, как тебя зовут.")
        return
    await state.update_data(name=name)
    await message.delete()
    data = await state.get_data()
    message_id = data.get("message_id")
    text = (
            "<b>В какое время тебе обычно сложнее всего?</b>\n\n"
            "<i>Я буду особенно внимателен в эти моменты. 🌙</i>"
            )
    try:
        await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=message_id, reply_markup=hard_time_keyboard)
    except:
        await bot.send_message(text=text, chat_id=message.from_user.id, message_id=message_id, reply_markup=hard_time_keyboard)
    await state.set_state(WorryState.choosing_worry)


# --- Шаг 2: Время суток ---
@router.callback_query(F.data.in_([
    MORNING_CALL, DAY_CALL, EVENING_CALL, NIGHT_CALL
]))
async def process_hard_time(callback: CallbackQuery, state: FSMContext):
    hard_time_key = callback.data.split(":")[1]  # 'morning', 'day' и т.д.

    await state.update_data(hard_time=hard_time_key)

    await callback.message.edit_reply_markup()

    opt = {
        MORNING_CALL: "🌅 Утро",
        DAY_CALL: "☀️ День",
        EVENING_CALL: "🌆 Вечер",
        NIGHT_CALL: "🌃 Ночь"
    }.get(callback.data) or ""

    await callback.message.edit_text(
        "💭 <b>Что сейчас беспокоит тебя больше всего?</b>\n\n"
        "Можешь выбрать из списка или написать своё:",
        reply_markup=worry_keyboard
    )

    await state.update_data(message_id=callback.message.message_id)

    await state.set_state(WorryState.choosing_worry)
    await callback.answer(opt)

# --- Шаг 3: Выбор беспокойства (готовые варианты) ---

async def _completion_onboarding(bot: Bot, state: FSMContext, telegram_id: int, worry: str, session: AsyncSession):
    data = await state.get_data()
    name = data["name"]
    hard_time = {
        "morning": "Утро",
        "day": "День",
        "evening": "Вечер",
        "night": "Ночь",
    }.get(data["hard_time"], data["hard_time"])

    logging.debug(f"Данные для записи: {name}, {hard_time}, {worry}")

    res = await update_user_fields(
        session=session,
        telegram_id=telegram_id,
        name=name,
        hard_time=hard_time,
        main_topic=worry
        )
    logging.debug(f"Результат записи данных из мини формы в бд: {res}")
    temp_mess = await bot.send_message(telegram_id, "⏳ Пожалуйста, дай мне время обдумать...")

    text_pattern = (
            f"Спасибо, что рассказал(а) мне это, {name}.\n\n"

            f"Я буду рядом с тобой, особенно в те моменты, когда тебе труднее всего — {hard_time}.\n\n"

            "Ты можешь писать мне в любой момент.\n"
            "А я буду иногда писать тебе сам."
        )
    response = ""
    try:
        response = await get_ai_response(
            f"Сгенерируй персональное сообщение от Telegram-бота эмоционального сопровождения для {name} с переживаниями {worry}, сложное время суток: {hard_time}, например:"

            f"{text_pattern}")
    except Exception as e:
        print(f"Error getting AI response: {e}")
        response = text_pattern

    if response:
        await bot.send_message(telegram_id, response, reply_markup=set_settings_keyboard)
    else:
        await bot.send_message(telegram_id, text_pattern, reply_markup=set_settings_keyboard)
        
    await bot.delete_message(chat_id=telegram_id, message_id=temp_mess.message_id)
    await state.clear()

@router.callback_query(
    WorryState.choosing_worry,
    F.data.in_([
        LONELINESS_CALL, ANXIETY_CALL, RELATIONSHIPS_CALL,
        DISCIPLINE_CALL
    ])
)
async def process_worry_choice(callback: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):
    telegram_id = callback.from_user.id
    worry_mapping = {
        LONELINESS_CALL: "Одиночество",
        ANXIETY_CALL: "Тревога",
        RELATIONSHIPS_CALL: "Отношения",
        DISCIPLINE_CALL: "Дисциплина",
    }
    worry = worry_mapping[callback.data]
    await callback.answer(worry)


    await callback.message.delete()

    await _completion_onboarding(bot=bot, state=state, telegram_id=telegram_id, worry=worry, session=session)


# --- Шаг 3: "Другое" → ожидание текста ---
@router.callback_query(WorryState.choosing_worry, F.data == OTHER_CALL)
async def process_worry_other(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✏️ <b>Напиши, что именно тебя беспокоит.</b>\n\n"
        "Можешь описать кратко или подробно — как тебе удобно."
    )
    await state.set_state(WorryState.entering_custom_worry)
    await callback.answer()


# --- Обработка кастомного текста ---
@router.message(WorryState.entering_custom_worry)
async def process_custom_worry(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    telegram_id = message.from_user.id
    custom_worry = message.text.strip()
    if not custom_worry:
        await message.answer("🫤 Пожалуйста, напиши, что тебя тревожит.")
        return

    data = await state.get_data()
    message_id = data.get("message_id")
    await bot.delete_messages(chat_id=telegram_id, message_ids=(message.message_id, message_id))

    await _completion_onboarding(bot=bot, state=state, telegram_id=telegram_id, worry=custom_worry, session=session)