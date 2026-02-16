from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from ..models import User  # замените your_module на ваш путь


async def delete_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> bool:
    """Удаляет пользователя и все его сообщения по telegram_id."""
    result = await session.execute(
        delete(User).where(User.telegram_id == telegram_id)
    )
    deleted = result.rowcount > 0
    if deleted:
        await session.commit()
    return deleted