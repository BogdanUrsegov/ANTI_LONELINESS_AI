from aiogram import Bot
from datetime import date, timedelta
from bot.database.session import AsyncSessionLocal  # ← твой sessionmaker
from datetime import datetime
from bot.database.utils import get_user_telegram_ids_active_last_24h, get_user_messages_last_24h
import logging


logging.getLogger(__name__)


async def run_daily_aggregation(bot: Bot) -> None:
    async with AsyncSessionLocal() as session:
        # Получаем только ID
        user_ids = await get_user_telegram_ids_active_last_24h(session)
        
        for telegram_id in user_ids:
            try:
                # Собираем ВСЕ сообщения этого пользователя за последние 24ч
                messages = await get_user_messages_last_24h(session, telegram_id)
                
                # # Прогоняем через классификатор
                # analysis = await classify_messages(messages)
                
                # # Сохраняем результат (например, в таблицу daily_analysis)
                # await save_daily_analysis(session, telegram_id, analysis)
                
            except Exception as e:
                print(f"⚠️ Ошибка обработки {telegram_id}: {e}")
                continue
        
        await session.commit()  # если были INSERT/UPDATE
    
    next_run = (datetime.now().replace(hour=2, minute=0, second=0, microsecond=0) 
                + timedelta(days=1))
    delay = max(0, int((next_run - datetime.now()).total_seconds()))
    await bot.scheduler.schedule_function(
        "run_daily_aggregation",
        delay_seconds=delay,
        user_id=0
    )