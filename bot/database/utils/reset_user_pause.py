from sqlalchemy import update
import logging

from bot.database.models import User
from bot.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

async def reset_user_pause(telegram_id: int) -> bool:
    """
    Обнуляет поле pause_until (снимает паузу) для пользователя.
    
    :param telegram_id: ID пользователя в Telegram
    :return: True если пользователь найден и обновлен, False если не найден
    """
    async with AsyncSessionLocal() as session:
        try:
            stmt = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(pause_until=None) # Обнуляем поле
            )
            
            result = await session.execute(stmt)
            
            if result.rowcount == 0:
                logger.warning(f"Пользователь {telegram_id} не найден для сброса паузы.")
                return False
            
            await session.commit()
            return True

        except Exception as e:
            logger.error(f"Ошибка reset_user_pause: {e}")
            await session.rollback()
            raise