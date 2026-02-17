import logging
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
from bot.database.models import ChatMessage
from bot.database.session import AsyncSessionLocal


logger = logging.getLogger(__name__)


async def get_user_telegram_ids_active_last_24h(session) -> list[int]:
    """Возвращает telegram_id пользователей, писавших за последние 24 часа."""
    one_day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
    async with AsyncSessionLocal() as session:
        try:
            stmt = (
                select(ChatMessage.telegram_id)
                .where(
                    ChatMessage.role == "user",
                    ChatMessage.created_at >= one_day_ago
                )
                .distinct()
            )
            result = await session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Ошибка get_user_telegram_ids_active_last_24h: {e}")
            await session.rollback()
            raise