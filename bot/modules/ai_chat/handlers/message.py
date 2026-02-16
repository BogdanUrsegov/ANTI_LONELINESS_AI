# bot/modules/ai_chat/handlers/message.py
from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.enums import ChatAction
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.utils.ai.context_builder import fetch_user_context
from bot.ai.utils.chat import generate_personalized_ai_response
from bot.database.utils.ai.context_manager import save_message


logger = logging.getLogger(__name__)

router = Router()

@router.message(F.text)
async def handle_ai_query(message: Message, session: AsyncSession, bot: Bot):
    telegram_id = message.from_user.id
    user_text = message.text

    # 1. Собираем контекст из БД
    context = await fetch_user_context(telegram_id, session)

    # 2. Генерируем ответ от ИИ
    try:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        ai_response = await generate_personalized_ai_response(context, user_text)

        # 3. Сохраняем сообщения
        await save_message(telegram_id, "user", user_text, None, session)
        await save_message(telegram_id, "assistant", ai_response, None, session)

        # 4. Отправляем пользователю
        await message.answer(ai_response)
    except Exception as e:
        logging.error(f"Ошибка при отправке ответа для {telegram_id} от ии: {e}")
        await message.answer("<i>Мой дорогой друг, при создании ответа для тебя произошла ошибка. Я попробую ответить как можно скорее!</i>")