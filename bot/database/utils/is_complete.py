from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import User


async def is_complete(session: AsyncSession, telegram_id: int) -> bool:
    query = select(User.name, User.archetype, User.main_topic, User.is_complete).where(
        User.telegram_id == telegram_id
    ).limit(1)
    result = await session.execute(query)
    row = result.fetchone()
    if not row:
        return False
    name, archetype, main_topic, is_complete = row
    return bool(
        name and archetype and main_topic and is_complete is True
    )