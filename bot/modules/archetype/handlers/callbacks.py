from aiogram import F, Router
from aiogram.types import CallbackQuery
from ..keyboards.inline_keyboards import archetype_kb
from aiogram.fsm.context import FSMContext
from bot.modules.mini_form import UserNameState
from bot.modules.age_gate import ADULT_CALL
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.utils.update_user_field import update_user_fields
from ..keyboards.inline_keyboards import WARM_SUPPORTIVE_CALL, CALM_MENTOR_CALL, FRIENDLY_LIGHT_CALL


router = Router()


@router.callback_query(F.data == ADULT_CALL)
async def adult_handler(callback: CallbackQuery):
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "<b>Какой формат общения тебе сейчас ближе?</b>\n\n"

        "<i>Выбери того, с кем тебе будет комфортно. Ты сможешь сменить это позже</i>",
        reply_markup=archetype_kb
    )
    await callback.answer()


@router.callback_query(F.data.in_([WARM_SUPPORTIVE_CALL, CALM_MENTOR_CALL, FRIENDLY_LIGHT_CALL]))
async def archetype_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "<b>Отлично! Давай начнем знакомство с тобой</b>\n\n"

        "<i>Какое у тебя имя?</i>"
    )
    field_value = {
        WARM_SUPPORTIVE_CALL: "Тёплый и поддерживающий",
        CALM_MENTOR_CALL: "Спокойный наставник",
        FRIENDLY_LIGHT_CALL: "Дружелюбный и лёгкий"
        }[callback.data]
    await update_user_fields(
        session=session,
        telegram_id=callback.from_user.id,
        archetype=field_value
    )
    await state.set_state(UserNameState.waiting_for_name)
    await callback.answer()