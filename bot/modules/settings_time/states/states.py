from aiogram.fsm.state import State, StatesGroup


class NotificationSettings(StatesGroup):
    """Настройка времени уведомлений."""
    morning_choice = State()      # Выбор: писать ли утром?
    morning_time_input = State()  # Ввод утреннего времени (если "Да")
    evening_choice = State()      # Писать ли вечером?
    day_touches_choice = State()  # Дневные касания