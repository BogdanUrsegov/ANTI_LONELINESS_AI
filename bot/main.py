import logging
import os
from aiohttp import web
from aiogram import Dispatcher
from redis.asyncio import Redis
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from bot.database.session import AsyncSessionLocal, init_db
from aiogram.fsm.storage.redis import RedisStorage
from bot.middlewares.db import DbSessionMiddleware
from bot.middlewares.scheduler import SchedulerMiddleware
from bot.scheduled_messages import RedisMessageScheduler


from .create_bot import bot, ADMIN_ID
from .routers import router


REDIS_URL = os.getenv("REDIS_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
BASE_URL = os.getenv("WEBHOOK_BASE_URL")
HOST = os.getenv("WEBHOOK_HOST")
PORT = int(os.getenv("WEBHOOK_PORT", 8000))

if not all((REDIS_URL, WEBHOOK_PATH, BASE_URL, HOST, PORT)):
    raise ValueError("Constans are empty")

scheduler = RedisMessageScheduler(
        redis_url=REDIS_URL,
        check_interval=1.0
    )

async def on_startup() -> None:
    # Инициализация БД
    await init_db()
    logging.info("✅ Database tables initialized")

    await scheduler.initialize()
    scheduler.start_worker(bot)
    logging.info("✅ scheduler works!")


    await bot.set_webhook(f"{BASE_URL}{WEBHOOK_PATH}")
    await bot.send_message(chat_id=ADMIN_ID, text="✅ Бот запущен!")


async def on_shutdown() -> None:
    redis_client = Redis.from_url(REDIS_URL)
    scheduler.stop_worker()
    await scheduler.close()

    await bot.send_message(chat_id=ADMIN_ID, text="🛑 Бот остановлен!")
    await bot.delete_webhook(drop_pending_updates=True)


def main() -> None:
    redis_client = Redis.from_url(REDIS_URL)
    storage = RedisStorage(redis=redis_client)
    dp = Dispatcher(storage=storage)
    dp["session_maker"] = AsyncSessionLocal

    dp.update.middleware(DbSessionMiddleware(AsyncSessionLocal))
    dp.update.middleware(SchedulerMiddleware(scheduler))
    #dp.update.middleware(ChannelLoggerMiddleware(channel_id=LOG_CHANNEL_ID))

    dp.include_router(router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host=HOST, port=PORT)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    main()