from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from bot.modules.main_menu import SUBSCRIPTION_CALL


router = Router()


@router.callback_query(F.data == SUBSCRIPTION_CALL)
async def callback_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("🔴 Этот раздел недоступен")