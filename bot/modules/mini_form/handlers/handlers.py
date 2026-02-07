from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
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

router = Router()

# --- Шаг 1: Имя ---
@router.message(UserNameState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("🫣 Пожалуйста, напиши, как тебя зовут.")
        return

    await state.update_data(name=name)
    await message.answer(
        "🌤️ <b>В какое время суток тебе обычно сложнее всего?</b>\n\n"
        "Выбери наиболее подходящий вариант:",
        reply_markup=hard_time_keyboard
    )
    await state.set_state(WorryState.choosing_worry)


# --- Шаг 2: Время суток ---
@router.callback_query(F.data.in_([
    MORNING_CALL, DAY_CALL, EVENING_CALL, NIGHT_CALL
]))
async def process_hard_time(callback: CallbackQuery, state: FSMContext):
    hard_time_key = callback.data.split(":")[1]  # 'morning', 'day' и т.д.

    await state.update_data(hard_time=hard_time_key)

    # Удаляем кнопки из предыдущего сообщения
    await callback.message.edit_text(
        "💭 <b>Что сейчас беспокоит тебя больше всего?</b>\n\n"
        "Можешь выбрать из списка или написать своё:",
        reply_markup=worry_keyboard
    )
    await state.set_state(WorryState.choosing_worry)
    await callback.answer()

# --- Шаг 3: Выбор беспокойства (готовые варианты) ---

async def _completion_onboarding(message: Message, state: FSMContext, worry: str, session: AsyncSession):
    data = await state.get_data()
    name = data["name"]
    hard_time = {
        "morning": "Утро",
        "day": "День",
        "evening": "Вечер",
        "night": "Ночь",
    }.get(data["hard_time"], data["hard_time"])

    await update_user_fields(
        session=session,
        telegram_id=message.from_user.id,
        name=name,
        hard_time=hard_time,
        main_topic=worry
        )
    response = await get_ai_response(
f"""Сгенерируй персональное сообщение от Telegram-бота эмоционального сопровождения для {name} с переживаниями {worry}, например:

Спасибо, что рассказал(а) мне это, {name}.

Я буду рядом с тобой, особенно в те моменты, когда тебе труднее всего — {hard_time}.

Ты можешь писать мне в любой момент.
А я буду иногда писать тебе сам.""")
    
    await message.answer(response["content"], reply_markup=set_settings_keyboard)
    await state.clear()

@router.callback_query(
    WorryState.choosing_worry,
    F.data.in_([
        LONELINESS_CALL, ANXIETY_CALL, RELATIONSHIPS_CALL,
        DISCIPLINE_CALL
    ])
)
async def process_worry_choice(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.edit_reply_markup()
    await callback.answer()
    worry_mapping = {
        LONELINESS_CALL: "Одиночество",
        ANXIETY_CALL: "Тревога",
        RELATIONSHIPS_CALL: "Отношения",
        DISCIPLINE_CALL: "Дисциплина",
    }
    worry = worry_mapping[callback.data]

    await _completion_onboarding(message=callback.message, state=state, worry=worry, session=session)


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
async def process_custom_worry(message: Message, state: FSMContext, session: AsyncSession):
    custom_worry = message.text.strip()
    if not custom_worry:
        await message.answer("🫤 Пожалуйста, напиши, что тебя тревожит.")
        return

    await _completion_onboarding(message=message, state=state, worry=custom_worry, session=session)