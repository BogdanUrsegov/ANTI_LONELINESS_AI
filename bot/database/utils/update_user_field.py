from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
import logging

from bot.database.models import User
from bot.database.session import AsyncSessionLocal


logger = logging.getLogger(__name__)

async def update_user_fields(
    telegram_id: int,
    **fields
) -> bool:
    """
    Обновляет одно или несколько полей пользователя по telegram_id.

    :param session: асинхронная сессия SQLAlchemy
    :param telegram_id: идентификатор пользователя в Telegram
    :param fields: именованные аргументы — поля модели User и их новые значения
                   (например, name="Анна", archetype="Искатель")
    :return: True, если пользователь найден и обновление выполнено; False — если не найден
    :raises AttributeError: если передано поле, отсутствующее в модели User
    """
    if not fields:
        return True  # ничего не обновлять — считаем успешным

    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one()

            # Проверяем существование всех полей в модели
            for field_name in fields:
                if not hasattr(user, field_name):
                    raise AttributeError(f"Модель User не содержит поля '{field_name}'")

            # Обновляем поля
            for field_name, value in fields.items():
                setattr(user, field_name, value)

            await session.commit()
            return True

        except Exception as e:
            logger.error(f"Ошибка update_user_fields: {e}")
            await session.rollback()
            raise