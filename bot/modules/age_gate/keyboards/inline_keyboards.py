from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


"""
Кнопки:

Да, мне 18+

Нет
"""

ADULT_CALL = "adult"
NOT_ADULT_CALL = "not_adult"


adult_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, мне 18+", callback_data=ADULT_CALL)]
    ]
)


not_adult_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Нет", callback_data=NOT_ADULT_CALL)]
    ]
)

is_adult_menu = InlineKeyboardMarkup(
    inline_keyboard=adult_kb.inline_keyboard + not_adult_kb.inline_keyboard
)