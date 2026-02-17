import logging
from sqlalchemy import delete
from typing import Optional

from bot.database.session import AsyncSessionLocal
from ..models import ChatMessage  # импорт модели из вашего модуля


logger = logging.getLogger(__name__)


async def delete_user_messages(
    telegram_id: int
) -> bool:
    """
    Удаляет все сообщения пользователя из таблицы chat_messages.
    
    Args:
        session: Асинхронная сессия SQLAlchemy
        telegram_id: Telegram ID пользователя
    
    Returns:
        True если удаление выполнено успешно, иначе False
    """
    async with AsyncSessionLocal() as session:
        try:
            stmt = delete(ChatMessage).where(ChatMessage.telegram_id == telegram_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка delete_user_messages: {e}")
            await session.rollback()
            raise