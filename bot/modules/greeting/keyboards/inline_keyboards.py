from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


FURTHER_CALL = "further"
WHAT_CAN_CALL = "what_can"


continue_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⏩ Продолжить", callback_data=FURTHER_CALL)]
    ]
)


what_can_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Что ты умеешь?", callback_data=WHAT_CAN_CALL)]
    ]
)


start_menu = InlineKeyboardMarkup(
    inline_keyboard=continue_kb.inline_keyboard + what_can_kb.inline_keyboard
)