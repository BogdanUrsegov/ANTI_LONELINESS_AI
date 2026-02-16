from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from ..models import ChatMessage  # импорт модели из вашего модуля


async def delete_user_messages(
    session: AsyncSession,
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
    try:
        stmt = delete(ChatMessage).where(ChatMessage.telegram_id == telegram_id)
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0
    except Exception:
        await session.rollback()
        return False