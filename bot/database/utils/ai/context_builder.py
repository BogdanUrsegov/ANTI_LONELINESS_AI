# bot/ai/context_builder.py
import logging
from sqlalchemy import select
from bot.database.models import User, ChatMessage
from bot.database.session import AsyncSessionLocal


logger = logging.getLogger(__name__)


async def fetch_user_context(
    telegram_id: int
) -> dict:
    """
    Собирает данные пользователя и его историю сообщений.
    
    Возвращает словарь:
    {
        "name": str | None,
        "archetype": str | None,
        "main_topic": str | None,
        "history": List[{"role": str, "content": str}]
    }
    """
    # Получаем пользователя
    async with AsyncSessionLocal() as session:
        try:
            user_result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {
                    "name": None,
                    "archetype": None,
                    "main_topic": None,
                    "history": []
                }

            # Получаем историю (только роль и контент, без reasoning)
            messages_result = await session.execute(
                select(ChatMessage)
                .where(ChatMessage.telegram_id == telegram_id)
                .order_by(ChatMessage.created_at.asc())  # от старых к новым
            )
            messages = messages_result.scalars().all()

            history = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            return {
                "name": user.name,
                "archetype": user.archetype,
                "main_topic": user.main_topic,
                "history": history
            }
        except Exception as e:
            logger.error(f"Ошибка fetch_user_context: {e}")
            await session.rollback()
            raise