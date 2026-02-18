from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.modules.main_menu import MAIN_MENU_CALL, MESSAGE_FREQUENCY_CALL


# Переключатели утро
MORNING_ON_CALL = "REMINDER_MORNING_ON"
MORNING_OFF_CALL = "REMINDER_MORNING_OFF"

# Переключатели вечер
EVENING_ON_CALL = "REMINDER_EVENING_ON"
EVENING_OFF_CALL = "REMINDER_EVENING_OFF"

# Переключатели день
DAYTIME_RARE_CALL = "REMINDER_DAYTIME_RARE"
DAYTIME_NONE_CALL = "REMINDER_DAYTIME_NONE"

# Временные слоты для утра
TIME_7_830_CALL = "REMINDER_TIME:07:00"
TIME_830_10_CALL = "REMINDER_TIME:8:30"
TIME_10_1130_CALL = "REMINDER_TIME:10:00"

MORNING_MESSAGES_CALL = "morning_messages"
NIGHT_MESSAGES_CALL = "night_messages"
DAILY_MESSAGES_CALL = "daily_messages"


reminder_slot_selection_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌅 Утро", callback_data=MORNING_MESSAGES_CALL)],
        [InlineKeyboardButton(text="🌃 Вечер", callback_data=NIGHT_MESSAGES_CALL)],
        [InlineKeyboardButton(text="🏙 День", callback_data=DAILY_MESSAGES_CALL)],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=MAIN_MENU_CALL)]
    ])

def get_morning_keyboard(is_enabled: bool, selected_time: str | None = None) -> InlineKeyboardMarkup:
    """Клавиатура настроек утренних напоминаний"""
    rows = [
        [
            InlineKeyboardButton(
                text="✅ Включено" if is_enabled else "❌ Выключено",
                callback_data=MORNING_ON_CALL if not is_enabled else MORNING_OFF_CALL
            )
        ]
    ]

    if is_enabled:
        # Определяем слоты в нужном порядке
        slots = [
            ("07:00", "07:00 – 08:30", TIME_7_830_CALL),
            ("08:30", "08:30 – 10:00", TIME_830_10_CALL),
            ("10:00", "10:00 – 11:30", TIME_10_1130_CALL),
        ]

        # Формируем кнопки с галочкой, если совпадает selected_time
        buttons = []
        for start_time, display_text, callback in slots:
            text = f"{display_text} ✅" if selected_time == start_time else display_text
            buttons.append(InlineKeyboardButton(text=text, callback_data=callback))

        rows.extend([
            [buttons[0], buttons[1]],
            [buttons[2]]
        ])

    rows.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data=MESSAGE_FREQUENCY_CALL)
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)

def get_evening_keyboard(is_enabled: bool) -> InlineKeyboardMarkup:
    """Клавиатура настроек вечерних напоминаний"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Включено" if is_enabled else "❌ Выключено",
                callback_data=EVENING_ON_CALL if not is_enabled else EVENING_OFF_CALL
            )
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data=MESSAGE_FREQUENCY_CALL)
        ]
    ])


def get_daytime_keyboard(is_enabled: bool) -> InlineKeyboardMarkup:
    """
    Клавиатура настроек дневных напоминаний
    :param mode: "rare" | "none"
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Включено" if is_enabled else "❌ Выключено",
                callback_data=DAYTIME_RARE_CALL if not is_enabled else DAYTIME_NONE_CALL
            )
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data=MESSAGE_FREQUENCY_CALL)
        ]
    ])