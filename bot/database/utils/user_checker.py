from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.models import User


async def user_checker(session: AsyncSession, telegram_id: int):
    query = select(User.telegram_id).where(User.telegram_id == telegram_id).limit(1)
    result = await session.execute(query)
    return result.scalar_one_or_none() is not None