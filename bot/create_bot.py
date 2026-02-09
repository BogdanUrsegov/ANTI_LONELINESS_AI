import os
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot
from bot.database.session import AsyncSessionLocal

# Читаем переменные
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

if not all([BOT_TOKEN, ADMIN_ID]):
    raise ValueError("Missing required env vars: BOT_TOKEN, REDIS_URL, ADMIN_ID")

# Создаём компоненты
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))


# Экспортируем
__all__ = ["bot", "dp", "ADMIN_ID"]