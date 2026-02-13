from aiogram import F, Router
from aiogram.types import CallbackQuery
from ..keyboards.inline_keyboards import archetype_kb, setting_archetype_kb
from aiogram.fsm.context import FSMContext
from bot.modules.mini_form import UserNameState
from bot.modules.age_gate import ADULT_CALL
from bot.modules.main_menu import COMMUNICATION_FORMAT_CALL
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.exceptions import TelegramBadRequest
from bot.database.utils.update_user_field import update_user_fields
from bot.database.utils.get_user_field import get_user_field
from ..keyboards.inline_keyboards import WARM_SUPPORTIVE_CALL, CALM_MENTOR_CALL, FRIENDLY_LIGHT_CALL, SETTING_WARM_SUPPORTIVE_CALL, SETTING_CALM_MENTOR_CALL, SETTING_FRIENDLY_LIGHT_CALL


router = Router()


@router.callback_query(F.data == COMMUNICATION_FORMAT_CALL)
async def communication_format_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    telegram_id = callback.from_user.id
    archetype = await get_user_field(session=session, 
                                     telegram_id=telegram_id,
                                     field_name="archetype")
    await callback.message.edit_text(f"<b>Выбрано:</b> <i>{archetype}</i>\n\n"
                                  "<b>Выбери мой архетип при общении</b>", 
                                  reply_markup=setting_archetype_kb)
    await callback.answer()

@router.callback_query(F.data.in_([
        SETTING_WARM_SUPPORTIVE_CALL, SETTING_CALM_MENTOR_CALL, SETTING_FRIENDLY_LIGHT_CALL
    ]))
async def process_change_archetype(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    telegram_id = callback.from_user.id
    field_value = {
        SETTING_WARM_SUPPORTIVE_CALL: "Тёплый и поддерживающий",
        SETTING_CALM_MENTOR_CALL: "Спокойный наставник",
        SETTING_FRIENDLY_LIGHT_CALL: "Дружелюбный и лёгкий"
    }[callback.data]
    
    await callback.answer(field_value)

    await update_user_fields(
        session=session, 
        telegram_id=telegram_id,
        archetype=field_value
    )
    try:
        await callback.message.edit_text(f"<b>Выбрано:</b> <i>{field_value}</i>\n\n"
                                    "<b>Выбери мой архетип при общении</b>", 
                                    reply_markup=setting_archetype_kb)
    except TelegramBadRequest as e:
        if "message is not modified" not in e.message:
            raise  # пропускаем только эту конкретную ошибку


@router.callback_query(F.data == ADULT_CALL)
async def adult_handler(callback: CallbackQuery):
    await callback.message.edit_reply_markup()
    await callback.message.edit_text(
        f"{callback.message.html_text}\n\n"

        "✅ <b>Есть 18 лет</b>"
    ) 
    
    await callback.message.answer(
        "<b>Какой формат общения тебе сейчас ближе?</b>\n\n"

        "<i>Выбери того, с кем тебе будет комфортно. Ты сможешь сменить это позже</i>",
        reply_markup=archetype_kb
    )
    await callback.answer()

@router.callback_query(F.data.in_([WARM_SUPPORTIVE_CALL, CALM_MENTOR_CALL, FRIENDLY_LIGHT_CALL]))
async def archetype_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.edit_reply_markup()
    field_value = {
        WARM_SUPPORTIVE_CALL: "Тёплый и поддерживающий",
        CALM_MENTOR_CALL: "Спокойный наставник",
        FRIENDLY_LIGHT_CALL: "Дружелюбный и лёгкий"
        }[callback.data]
        
    await callback.message.edit_text(
        f"{callback.message.html_text}\n\n"

        f"🗣 <b>{field_value}</b>"
    ) 
    await update_user_fields(
        session=session,
        telegram_id=callback.from_user.id,
        archetype=field_value
    )
    await callback.message.answer(
        "<b>Отлично! Давай начнем знакомство с тобой</b>\n\n"

        "<b>Как я могу к тебе обращаться?</b>\n\n"
        "<i>Или как тебе комфортно, чтобы я тебя называл? 💌</i>"
    )
    await state.set_state(UserNameState.waiting_for_name)
    await callback.answer()