import logging
from sqlalchemy import select, delete

from bot.database.session import AsyncSessionLocal

from ..models import User  # замените your_module на ваш путь


logger = logging.getLogger(__name__)


async def delete_user_by_telegram_id(telegram_id: int) -> bool:
    """Удаляет пользователя и все его сообщения по telegram_id."""
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                delete(User).where(User.telegram_id == telegram_id)
            )
            deleted = result.rowcount > 0
            if deleted:
                await session.commit()
            return deleted
        except Exception as e:
            logger.error(f"Ошибка delete_user_by_telegram_id: {e}")
            await session.rollback()
            raise