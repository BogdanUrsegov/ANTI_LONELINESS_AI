from aiogram.fsm.state import State, StatesGroup


class UserNameState(StatesGroup):
    """Состояние для ввода имени пользователя."""
    waiting_for_name = State()  # Ожидание текстового ввода имени


class WorryState(StatesGroup):
    """Состояние для выбора или ввода того, что беспокоит."""
    choosing_worry = State()   # Показ инлайн-клавиатуры с вариантами
    entering_custom_worry = State()  # Ручной ввод (если выбрано 'Другое')