from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ..config import WARM_SUPPORTIVE, CALM_MENTOR, FRIENDLY_LIGHT
from bot.modules.main_menu import MAIN_MENU_CALL


WARM_SUPPORTIVE_CALL = WARM_SUPPORTIVE
CALM_MENTOR_CALL = CALM_MENTOR
FRIENDLY_LIGHT_CALL = FRIENDLY_LIGHT

SETTING_WARM_SUPPORTIVE_CALL = f"setting_{WARM_SUPPORTIVE}"
SETTING_CALM_MENTOR_CALL = f"setting_{CALM_MENTOR}"
SETTING_FRIENDLY_LIGHT_CALL = f"setting_{FRIENDLY_LIGHT}"


archetype_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🤗 Тёплый и поддерживающий", callback_data=WARM_SUPPORTIVE_CALL)],
        [InlineKeyboardButton(text="🧘 Спокойный наставник", callback_data=CALM_MENTOR_CALL)],
        [InlineKeyboardButton(text="😄 Дружелюбный и лёгкий", callback_data=FRIENDLY_LIGHT_CALL)]
    ]
)

setting_archetype_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🤗 Тёплый и поддерживающий", callback_data=SETTING_WARM_SUPPORTIVE_CALL)],
        [InlineKeyboardButton(text="🧘 Спокойный наставник", callback_data=SETTING_CALM_MENTOR_CALL)],
        [InlineKeyboardButton(text="😄 Дружелюбный и лёгкий", callback_data=SETTING_FRIENDLY_LIGHT_CALL)],
        [InlineKeyboardButton(text="⏪ Назад", callback_data=MAIN_MENU_CALL)]
    ]
)
