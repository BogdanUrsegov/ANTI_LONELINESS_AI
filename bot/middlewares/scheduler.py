from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from bot.scheduled_messages import RedisMessageScheduler

class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler: RedisMessageScheduler):
        super().__init__()
        self.scheduler = scheduler

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Добавляем scheduler в данные хендлера
        data["scheduler"] = self.scheduler
        return await handler(event, data)