from datetime import datetime, timezone, timedelta
from sqlalchemy import select, update
import logging

from bot.database.models import User
from bot.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

async def set_user_pause(telegram_id: int, days: int | None = None) -> bool:
    """
    Устанавливает паузу для пользователя.
    
    :param telegram_id: ID пользователя
    :param days: Количество дней паузы. 
                 Если None — снимает паузу.
                 Если > 3650 (примерно 10 лет) — считает как "навсегда".
    :return: True если успешно, False если пользователь не найден.
    """
    async with AsyncSessionLocal() as session:
        try:
            now_utc = datetime.now(timezone.utc)
            
            if days is None:
                # Снять паузу
                pause_until = None
            elif days > 3650:
                # "Навсегда" (ставим дату на 2099 год)
                pause_until = datetime(2099, 12, 31, tzinfo=timezone.utc)
            else:
                # На конкретное количество дней
                pause_until = now_utc + timedelta(days=days)

            # Оптимизированный UPDATE без предварительного SELECT
            stmt = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(pause_until=pause_until)
            )
            
            result = await session.execute(stmt)
            
            if result.rowcount == 0:
                logger.warning(f"Пользователь {telegram_id} не найден для обновления паузы.")
                return False
            
            await session.commit()
            return True

        except Exception as e:
            logger.error(f"Ошибка set_user_pause: {e}")
            await session.rollback()
            raise