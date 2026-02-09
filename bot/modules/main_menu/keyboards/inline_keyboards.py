from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Константы коллбэк-данных
MAIN_MENU_CALL = "main_menu"
COMMUNICATION_FORMAT_CALL = "comm_format"
MESSAGE_FREQUENCY_CALL = "msg_freq"
PAUSE_CALL = "pause"
CLEAR_MEMORY_CALL = "clear_mem"
SUBSCRIPTION_CALL = "subscribe"
ABOUT_PRODUCT_CALL = "about_product"


goto_main_menu_kb = (InlineKeyboardBuilder()
    .button(text="🙋‍♂️ В меню", callback_data=MAIN_MENU_CALL)
    .as_markup()
)

main_menu_builder = InlineKeyboardBuilder()
    
buttons = [
    ("💬 Мой формат общения", COMMUNICATION_FORMAT_CALL),
    ("⏰ Частота сообщений", MESSAGE_FREQUENCY_CALL),
    ("⏸ Пауза", PAUSE_CALL),
    ("🧹 Очистить память", CLEAR_MEMORY_CALL),
    ("💳 Подписка", SUBSCRIPTION_CALL),
    ("ℹ️ О продукте", ABOUT_PRODUCT_CALL)
]
    
for text, callback in buttons:
    main_menu_builder.button(text=text, callback_data=callback)

main_menu_builder.adjust(1)

main_menu_keyboard = main_menu_builder.as_markup()