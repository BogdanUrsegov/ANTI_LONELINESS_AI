# middleware/registration.py
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy import select
from bot.database.models import User


class RegistrationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session = data.get("session")
        if not session:
            return await handler(event, data)

        user_id = None
        is_start = False

        if isinstance(event, Message):
            user_id = event.from_user.id
            if event.text and event.text.strip().split()[0] == "/start":
                is_start = True
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        # Пропускаем /start без проверки
        if is_start:
            return await handler(event, data)

        if user_id is None:
            return await handler(event, data)

        # Запрашиваем ТОЛЬКО is_complete
        result = await session.execute(
            select(User.is_complete).where(User.telegram_id == user_id)
        )
        is_complete = result.scalar_one_or_none()

        if is_complete is not True:
            msg = "<b>⚙️ Завершите регистрацию</b>"
            if isinstance(event, Message):
                await event.answer(msg)
            elif isinstance(event, CallbackQuery):
                await event.answer()
                await event.message.answer(msg)
            return  # блокируем обработчик

        return await handler(event, data)