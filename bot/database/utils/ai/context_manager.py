import logging
from typing import List, Dict, Optional
from sqlalchemy import select
from bot.database.models import ChatMessage
from bot.database.session import AsyncSessionLocal


logger = logging.getLogger(__name__)


async def load_context(telegram_id: int, limit: int = 25) -> List[Dict[str, Optional[dict]]]:
    """Загружает последние N сообщений пользователя из БД (в хронологическом порядке)."""
    async with AsyncSessionLocal() as session:
        try:
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
        except Exception as e:
            logger.error(f"Ошибка load_context: {e}")
            await session.rollback()
            raise

async def save_message(
    telegram_id: int,
    role: str,
    content: str,
    reasoning_details: Optional[dict]
) -> None:
    """Сохраняет сообщение в PostgreSQL."""
    async with AsyncSessionLocal() as session:
        try:
            msg = ChatMessage(
                telegram_id=telegram_id,
                role=role,
                content=content,
                reasoning_details=reasoning_details,
            )
            session.add(msg)
            await session.commit()
        except Exception as e:
                logger.error(f"Ошибка save_message: {e}")
                await session.rollback()
                raise