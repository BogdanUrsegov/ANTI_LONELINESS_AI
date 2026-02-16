from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.modules.main_menu import MAIN_MENU_CALL



DELETE_HISTORY_CALL = "delete_history"


delete_history_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить историю", callback_data=DELETE_HISTORY_CALL)],
        [InlineKeyboardButton(text="⬅️ Отмена", callback_data=MAIN_MENU_CALL)]
    ]
)