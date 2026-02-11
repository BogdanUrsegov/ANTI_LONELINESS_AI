from aiogram import F, Router, types
from sqlalchemy.ext.asyncio import AsyncSession
from ..keyboards.inline_keyboards import main_menu_keyboard, MAIN_MENU_CALL


router = Router()


@router.callback_query(F.data == MAIN_MENU_CALL)
async def callback_menu(callback: types.CallbackQuery, session: AsyncSession):
    await callback.message.edit_reply_markup()
    await callback.answer()
    await callback.message.answer("⚙️ <b>Меню</b>", reply_markup=main_menu_keyboard)
