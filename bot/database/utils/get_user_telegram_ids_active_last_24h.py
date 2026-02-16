from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
from bot.database.models import ChatMessage

async def get_user_telegram_ids_active_last_24h(session) -> list[int]:
    """Возвращает telegram_id пользователей, писавших за последние 24 часа."""
    one_day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
    
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