import logging
import os
import traceback
from aiogram import Dispatcher, Bot
from aiogram.types import ErrorEvent, Message, CallbackQuery
from aiogram.filters import ExceptionTypeFilter

# 1. Настройка стандартного логгера (файл + консоль)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")


# 2. Хендлер ошибок (вместо миддлвари и декораторов)
async def errors_handler(event: ErrorEvent, bot: Bot):
    exception = event.exception
    update = event.update
    
    # Получаем пользователя безопасно
    user = None
    if update.message: user = update.message.from_user
    elif update.callback_query: user = update.callback_query.from_user
    
    # Лог в файл
    logger.error(f"Error: {type(exception).__name__}", exc_info=exception)

    # Уведомление в админ-канал (только критические ошибки)
    if isinstance(exception, Exception): # Фильтруйте нужные классы ошибок
        try:
            text = (
                f"❌ <b>Ошибка:</b> {type(exception).__name__}\n"
                f"👤 <b>User:</b> {user.full_name if user else 'Unknown'} ({user.id if user else 0})\n"
                f"📝 <b>Trace:</b>\n<code>{traceback.format_exc()[-1000:]}</code>"
            )
            await bot.send_message(chat_id=LOG_CHANNEL_ID, text=text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Failed to send error log to admin: {e}")

    # Ответ пользователю
    if isinstance(update.event, Message):
        await update.event.answer("⚠️ Произошла ошибка. Попробуйте позже.", parse_mode="HTML")
    elif isinstance(update.event, CallbackQuery):
        await update.event.answer("⚠️ Ошибка", show_alert=True)