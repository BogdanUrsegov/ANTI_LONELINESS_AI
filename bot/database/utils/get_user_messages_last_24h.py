from datetime import datetime, timedelta, timezone
import logging
from typing import List, Tuple
from sqlalchemy import select
from bot.database.models import ChatMessage

from bot.database.session import AsyncSessionLocal


logger = logging.getLogger(__name__)


async def get_user_messages_last_24h(telegram_id: int) -> list[str]:
    """Возвращает тексты сообщений пользователя (role='user') за последние 24ч."""
    now = datetime.now(timezone.utc)
    one_day_ago = now - timedelta(hours=24)
    async with AsyncSessionLocal() as session:
        try:
            stmt = (
                select(ChatMessage.content)
                .where(
                    ChatMessage.telegram_id == telegram_id,
                    ChatMessage.role == "user",
                    ChatMessage.created_at >= one_day_ago
                )
                .order_by(ChatMessage.created_at)
            )
            result = await session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Ошибка get_user_messages_last_24h: {e}")
            await session.rollback()
            raise