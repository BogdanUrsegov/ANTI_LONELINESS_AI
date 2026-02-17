import logging
from bot.database.utils.get_evening_users_with_context import get_evening_users_with_context
from aiogram import Bot


logger = logging.getLogger(__name__)


async def first_generated_message(bot: Bot, user_id: int):
    text = (
        "Я просто хотел сказать, что не надо быть сильным всё время.\n\n"
        "Как ты сейчас?"
    )
    await bot.send_message(chat_id=user_id, text=text)

async def run_daily_aggregation(bot: Bot):
    logger.debug("Ежедневная функция")

async def daily_evening_message(bot: Bot):
    users_data = await get_evening_users_with_context()

    for telegram_id, name, history in users_data:
        logger.info(f"{telegram_id}\n{name}\n{history}")