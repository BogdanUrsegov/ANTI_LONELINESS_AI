from aiogram import F, Router, types
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from ..keyboards.inline_keyboards import goto_main_menu_kb
from bot.modules.main_menu import ABOUT_PRODUCT_CALL


router = Router()


@router.callback_query(F.data == ABOUT_PRODUCT_CALL)
async def callback_menu(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    text = (
        "<b>О продукте</b>"
    )
    await callback.message.edit_text(text, reply_markup=goto_main_menu_kb)
    await state.clear()
