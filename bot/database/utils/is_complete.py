import logging
from sqlalchemy import select
from bot.database.models import User
from bot.database.session import AsyncSessionLocal


logger = logging.getLogger(__name__)


async def is_complete(telegram_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        try:
            query = select(User.name, User.archetype, User.main_topic, User.is_complete).where(
                User.telegram_id == telegram_id
            ).limit(1)
            result = await session.execute(query)
            row = result.fetchone()
            if not row:
                return False
            name, archetype, main_topic, is_complete = row
            return bool(
                name and archetype and main_topic and is_complete is True
            )
        except Exception as e:
            logger.error(f"Ошибка is_complete: {e}")
            await session.rollback()
            raise