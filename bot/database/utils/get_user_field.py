from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
import logging

from bot.database.models import User
from bot.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def get_user_field(
    telegram_id: int,
    field_name: str
):
    """
    Возвращает значение указанного поля пользователя по telegram_id.

    :param session: асинхронная сессия SQLAlchemy
    :param telegram_id: идентификатор пользователя в Telegram
    :param field_name: имя поля модели User (например, "name", "archetype")
    :return: значение поля, если пользователь найден; иначе None
    :raises AttributeError: если поле отсутствует в модели User
    """
    if not hasattr(User, field_name):
        raise AttributeError(f"Модель User не содержит поля '{field_name}'")

    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one()
            return getattr(user, field_name)

        except Exception as e:
            logger.error(f"Ошибка get_user_field: {e}")
            await session.rollback()
            raise