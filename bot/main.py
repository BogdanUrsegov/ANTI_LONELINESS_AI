import asyncio
import logging
import os
from aiohttp import web
from redis.asyncio import Redis

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Локальные импорты
from bot.database.session import AsyncSessionLocal, init_db
from bot.middlewares.db import DbSessionMiddleware
from bot.middlewares.scheduler import SchedulerMiddleware
from bot.middlewares.registration import RegistrationMiddleware
from bot.scheduled_messages import RedisMessageScheduler
from .create_bot import bot, ADMIN_ID
from .routers import router

# === Настройки из окружения ===
REDIS_URL = os.getenv("REDIS_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
BASE_URL = os.getenv("WEBHOOK_BASE_URL", "")
HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
PORT = int(os.getenv("WEBHOOK_PORT", "8000"))

# Парсим IS_POLLING как bool: поддерживаем "0"/"1", "true"/"false"
IS_POLLING = os.getenv("IS_POLLING", "1").strip().lower() in ("1", "true", "yes", "on")

# Проверка обязательных переменных
if not REDIS_URL:
    raise ValueError("❌ REDIS_URL is required")

if not IS_POLLING:
    if not BASE_URL or not WEBHOOK_PATH:
        raise ValueError("❌ Webhook mode requires WEBHOOK_BASE_URL and WEBHOOK_PATH")


# === Глобальный планировщик сообщений ===
scheduler = RedisMessageScheduler(
    redis_url=REDIS_URL,
    check_interval=1.0
)


# === Обработчики событий жизненного цикла ===
async def on_startup(bot: Bot) -> None:
    await init_db()
    logging.info("✅ Database tables initialized")

    await scheduler.initialize()
    scheduler.start_worker(bot)
    logging.info("✅ Scheduler worker started")

    if not IS_POLLING:
        webhook_url = f"{BASE_URL}{WEBHOOK_PATH}"
        await bot.set_webhook(webhook_url)
        logging.info(f"✅ Webhook set to {webhook_url}")

    await bot.send_message(chat_id=ADMIN_ID, text="✅ Бот запущен!")


async def on_shutdown(bot: Bot) -> None:
    scheduler.stop_worker()
    await scheduler.close()

    await bot.send_message(chat_id=ADMIN_ID, text="🛑 Бот остановлен!")
    await bot.delete_webhook(drop_pending_updates=True)


# === Создание диспетчера (вынесено для DRY) ===
def create_dispatcher() -> Dispatcher:
    redis_client = Redis.from_url(REDIS_URL)
    storage = RedisStorage(redis=redis_client)
    dp = Dispatcher(storage=storage)
    dp["session_maker"] = AsyncSessionLocal

    dp.update.middleware(DbSessionMiddleware(AsyncSessionLocal))
    dp.update.middleware(RegistrationMiddleware())
    dp.update.middleware(SchedulerMiddleware(scheduler))
    dp.include_router(router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    return dp


# === Режим: Long Polling ===
async def run_polling():
    # 🔥 Критически важно: удалить webhook перед polling
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("🧹 Webhook deleted (if any)")

    dp = create_dispatcher()
    await dp.start_polling(bot)


# === Режим: Webhook ===
def run_webhook():
    dp = create_dispatcher()

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    logging.info(f"🚀 Starting webhook server on http://{HOST}:{PORT}{WEBHOOK_PATH}")
    web.run_app(app, host=HOST, port=PORT)


# === Точка входа ===
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    try:
        if IS_POLLING:
            asyncio.run(run_polling())
        else:
            run_webhook()
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Received shutdown signal")