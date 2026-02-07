from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Время суток
MORNING_CALL = "hard_time:morning"
DAY_CALL = "hard_time:day"
EVENING_CALL = "hard_time:evening"
NIGHT_CALL = "hard_time:night"

# Темы беспокойства
LONELINESS_CALL = "worry:loneliness"
ANXIETY_CALL = "worry:anxiety"
RELATIONSHIPS_CALL = "worry:relationships"
DISCIPLINE_CALL = "worry:discipline"
OTHER_CALL = "worry:other"

SET_SETTINGS_CALL = "set_settings"


# Вопрос 2: В какое время сложнее всего?
hard_time_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🌅 Утро", callback_data=MORNING_CALL),
            InlineKeyboardButton(text="☀️ День", callback_data=DAY_CALL),
        ],
        [
            InlineKeyboardButton(text="🌙 Вечер", callback_data=EVENING_CALL),
            InlineKeyboardButton(text="🌃 Ночь", callback_data=NIGHT_CALL),
        ]
    ]
)

# Вопрос 3: Что беспокоит?
worry_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Одиночество", callback_data=LONELINESS_CALL)],
        [InlineKeyboardButton(text="Тревога", callback_data=ANXIETY_CALL)],
        [InlineKeyboardButton(text="Отношения", callback_data=RELATIONSHIPS_CALL)],
        [InlineKeyboardButton(text="Дисциплина", callback_data=DISCIPLINE_CALL)],
        [InlineKeyboardButton(text="Другое", callback_data=OTHER_CALL)],
    ]
)

set_settings_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⚙️ Настроить время сообщений", callback_data=SET_SETTINGS_CALL)
        ]
    ]
)