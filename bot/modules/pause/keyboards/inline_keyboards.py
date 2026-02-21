from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.modules.main_menu import MAIN_MENU_CALL


PAUSE_1D_CALL = "delete_1d"
PAUSE_WEEK_CALL = "delete_week"
PAUSE_FOREVER_CALL = "delete_forever"
REMOVE_PAUSE_CALL = "remove_pause"


pause_period_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📅 На 1 день", callback_data=PAUSE_1D_CALL)],
        [InlineKeyboardButton(text="📆 На неделю", callback_data=PAUSE_WEEK_CALL)],
        [InlineKeyboardButton(text="♾️ На неопределённое время", callback_data=PAUSE_FOREVER_CALL)],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=MAIN_MENU_CALL)]
    ]
)

remove_pause_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⏩ Снять с паузы", callback_data=REMOVE_PAUSE_CALL)],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=MAIN_MENU_CALL)]
    ]
)