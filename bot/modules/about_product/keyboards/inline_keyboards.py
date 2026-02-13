from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.modules.main_menu import MAIN_MENU_CALL


goto_main_menu_kb = (InlineKeyboardBuilder()
    .button(text="⬅️ Назад", callback_data=MAIN_MENU_CALL)
    .as_markup()
)