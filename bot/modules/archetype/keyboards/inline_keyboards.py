from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


WARM_SUPPORTIVE_CALL = "warm_supportive"
CALM_MENTOR_CALL = "calm_mentor"
FRIENDLY_LIGHT_CALL = "friendly_light"


archetype_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🤗 Тёплый и поддерживающий", callback_data=WARM_SUPPORTIVE_CALL)],
        [InlineKeyboardButton(text="🧘 Спокойный наставник", callback_data=CALM_MENTOR_CALL)],
        [InlineKeyboardButton(text="😄 Дружелюбный и лёгкий", callback_data=FRIENDLY_LIGHT_CALL)]
    ]
)
