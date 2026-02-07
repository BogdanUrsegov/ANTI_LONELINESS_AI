from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Утро
MORNING_ENABLED_CALL = "notify:morning:yes"
MORNING_DISABLED_CALL = "notify:morning:no"

# Вечер
EVENING_ENABLED_CALL = "notify:evening:yes"
EVENING_DISABLED_CALL = "notify:evening:no"

# Дневные касания
DAY_TOUCHES_ENABLED_CALL = "notify:day_touches:sometimes"
DAY_TOUCHES_DISABLED_CALL = "notify:day_touches:no"

MORNING_TIME_7_CALL = "morning_time:07:00"
MORNING_TIME_8_CALL = "morning_time:08:30"
MORNING_TIME_10_CALL = "morning_time:10:00"


morning_time_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="7:00 – 8:30", callback_data=MORNING_TIME_7_CALL),
        InlineKeyboardButton(text="8:30 – 10:00", callback_data=MORNING_TIME_8_CALL),
    ],
    [
        InlineKeyboardButton(text="10:00 – 11:30", callback_data=MORNING_TIME_10_CALL),
    ],
    [
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_morning_choice")
    ]
])

morning_setting_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data=MORNING_ENABLED_CALL),
            InlineKeyboardButton(text="Нет", callback_data=MORNING_DISABLED_CALL)
        ]
    ]
)

evening_setting_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data=EVENING_ENABLED_CALL),
            InlineKeyboardButton(text="Нет", callback_data=EVENING_DISABLED_CALL)
        ]
    ]
)

day_touches_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Иногда", callback_data=DAY_TOUCHES_ENABLED_CALL),
            InlineKeyboardButton(text="Не нужно", callback_data=DAY_TOUCHES_DISABLED_CALL)
        ]
    ]
)