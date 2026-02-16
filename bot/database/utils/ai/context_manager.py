from typing import List, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import ChatMessage


async def load_context(telegram_id: int, session: AsyncSession, limit: int = 25) -> List[Dict[str, Optional[dict]]]:
    """Загружает последние N сообщений пользователя из БД (в хронологическом порядке)."""
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.telegram_id == telegram_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    records = result.scalars().all()
    
    # Возвращаем в хронологическом порядке (от старых к новым)
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "reasoning_details": msg.reasoning_details,
        }
        for msg in reversed(records)
    ]


async def save_message(
    telegram_id: int,
    role: str,
    content: str,
    reasoning_details: Optional[dict],
    session: AsyncSession,
) -> None:
    """Сохраняет сообщение в PostgreSQL."""
    msg = ChatMessage(
        telegram_id=telegram_id,
        role=role,
        content=content,
        reasoning_details=reasoning_details,
    )
    session.add(msg)
    await session.commit()