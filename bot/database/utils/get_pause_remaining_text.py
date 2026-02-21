from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
import logging

from bot.database.models import User
from bot.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

async def get_pause_status_text(telegram_id: int) -> str:
    """
    Получает статус паузы по ID пользователя и возвращает читаемую строку.
    
    Логика:
    - Нет паузы или истекла: ""
    - < 1 дня: "менее 1 дня"
    - 1–7 дней: "X дн."
    - > 7 дней: "неопределенное время"
    """
    async with AsyncSessionLocal() as session:
        try:
            # Быстрый запрос только нужного поля
            result = await session.execute(
                select(User.pause_until).where(User.telegram_id == telegram_id)
            )
            pause_until: Optional[datetime] = result.scalar_one_or_none()

            if not pause_until:
                return ""

            now = datetime.now(timezone.utc)
            
            # Если время уже истекло
            if pause_until <= now:
                return ""

            delta = pause_until - now
            total_seconds = int(delta.total_seconds())
            
            # Меньше 24 часов (86400 секунд)
            if total_seconds < 86400:
                return "менее 1 дня"
            
            days_left = delta.days
            
            # Больше 7 дней
            if days_left > 7:
                return "неопределенное время"
            
            # От 1 до 7 дней
            return f"{days_left} дн."

        except Exception as e:
            logger.error(f"Ошибка получения статуса паузы для {telegram_id}: {e}")
            return "Ошибка статуса"