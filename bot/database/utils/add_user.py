from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import User


async def add_user(session: AsyncSession, telegram_id: int):
    new_user = User(telegram_id=telegram_id)
    session.add(new_user)
    await session.commit()