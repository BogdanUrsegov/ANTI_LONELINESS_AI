import asyncio
import logging
import os
from aiohttp import web
from redis.asyncio import Redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Локальные импорты
from bot.database.session import AsyncSessionLocal, init_db
from bot.middlewares.scheduler import SchedulerMiddleware
from bot.middlewares.db import DbSessionMiddleware
from bot.middlewares.registration import RegistrationMiddleware
from bot.scheduler.tasks import daily_evening_message, daily_day_touches_message, daily_morning_message
from .create_bot import bot, ADMIN_ID
from .routers import router

# === Настройки ===
REDIS_URL = os.getenv("REDIS_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
BASE_URL = os.getenv("WEBHOOK_BASE_URL", "")
HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
PORT = int(os.getenv("WEBHOOK_PORT", "8000"))

IS_POLLING = os.getenv("IS_POLLING", "1").strip().lower() in ("1", "true", "yes", "on")

if not REDIS_URL:
    raise ValueError("❌ REDIS_URL is required")
if not IS_POLLING and (not BASE_URL or not WEBHOOK_PATH):
    raise ValueError("❌ Webhook mode requires WEBHOOK_BASE_URL and WEBHOOK_PATH")

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# === 1. Сама логика On Startup ===
async def on_startup(bot: Bot, scheduler: AsyncIOScheduler) -> None:
    """Основная логика запуска: БД, Шедулер, Задачи"""
    await init_db()
    logger.info("✅ Database initialized")

    # Конфигурация шедулера
    scheduler.configure(job_defaults={
        'coalesce': False,
        'max_instances': 1,
        'misfire_grace_time': 60
    })

    scheduler.add_job(
        func=daily_evening_message,     # Функция из tasks.py
        trigger='cron',                 # Тип: расписание (как крон в Linux)
        hour=16,                        # Час в UTC (16:00 UTC = 19:00 Москва)
        minute=0,                       # Минуты
        id='daily_evening_report',      # Уникальный ID задачи
        replace_existing=True,          # Перезаписать, если задача с таким ID уже есть
        misfire_grace_time=None         # Не выполнять, если бот был выключен в это время
    )

    scheduler.add_job(
        func=daily_day_touches_message,
        trigger='cron',
        hour=11,                        # Час в UTC (11:00 UTC = 14:00 Москва)
        minute=0,
        id='daily_day_touches_report',
        replace_existing=True,
        misfire_grace_time=None
    )

    scheduler.add_job(
        func=daily_morning_message,
        trigger='cron',
        hour=6,                        # Час в UTC (6:00 UTC = 9:00 Москва)
        minute=0,
        id='daily_morning_report',
        replace_existing=True,
        misfire_grace_time=None
    )
    
    scheduler.start()
    logger.info("✅ Scheduler started")

    # Webhook логика
    if not IS_POLLING:
        webhook_url = f"{BASE_URL}{WEBHOOK_PATH}"
        await bot.set_webhook(webhook_url)
        logger.info(f"✅ Webhook set: {webhook_url}")

    # Уведомление админа
    try:
        await bot.send_message(ADMIN_ID, "✅ Бот запущен!")
    except Exception as e:
        logger.warning(f"Не удалось отправить сообщение админу: {e}")


# === 2. Логика On Shutdown ===
async def on_shutdown(bot: Bot, scheduler: AsyncIOScheduler, redis: Redis) -> None:
    """Логика остановки"""
    logger.info("🛑 Shutting down...")
    scheduler.shutdown()
    await redis.close()
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await bot.send_message(ADMIN_ID, "🛑 Бот остановлен!")
    except Exception:
        pass


# === 3. Фабрики-обертки
def make_startup_handler(scheduler: AsyncIOScheduler):
    async def handler(bot: Bot):
        await on_startup(bot, scheduler)
    return handler

def make_shutdown_handler(scheduler: AsyncIOScheduler, redis: Redis):
    async def handler(bot: Bot):
        await on_shutdown(bot, scheduler, redis)
    return handler


# === 4. Фабрика Диспетчера ===
def create_dispatcher() -> Dispatcher:
    redis_client = Redis.from_url(REDIS_URL)
    storage = RedisStorage(redis=redis_client)
    dp = Dispatcher(storage=storage)
    
    scheduler = AsyncIOScheduler(timezone='UTC')

    
    dp.update.middleware(SchedulerMiddleware(scheduler))
    dp.update.middleware(DbSessionMiddleware(AsyncSessionLocal))
    dp.update.middleware(RegistrationMiddleware())
    
    dp.include_router(router)
    
    # Регистрируем обертки, которые вызовут наши функции
    dp.startup.register(make_startup_handler(scheduler))
    dp.shutdown.register(make_shutdown_handler(scheduler, redis_client))
    
    return dp


# === Режимы запуска ===
async def run_polling():
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("🧹 Webhook deleted")
    dp = create_dispatcher()
    await dp.start_polling(bot)

def run_webhook():
    dp = create_dispatcher()
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    logger.info(f"🚀 Webhook server running on http://{HOST}:{PORT}{WEBHOOK_PATH}")
    web.run_app(app, host=HOST, port=PORT)

if __name__ == "__main__":
    try:
        if IS_POLLING:
            asyncio.run(run_polling())
        else:
            run_webhook()
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Shutdown signal received")