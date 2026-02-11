from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.ai.utils.chat import get_ai_response
from bot.database.utils.ai.context_manager import load_context, save_message
from sqlalchemy.ext.asyncio import AsyncSession


router = Router()

@router.message(F.text)
async def handle_ai_query(message: Message, state: FSMContext, session: AsyncSession):
    user_id = message.from_user.id
    user_text = message.text

    # 1. Загружаем контекст
    context = await load_context(user_id, session)

    # 2. Добавляем новое сообщение от пользователя
    full_context = context + [{"role": "user", "content": user_text}]

    # 3. Отправляем в ИИ
    response = await get_ai_response("Привет")

    # 4. Сохраняем оба сообщения
    await save_message(user_id, "user", user_text, None, session)
    await save_message(
        user_id,
        "assistant",
        response.content,
        getattr(response, "reasoning_details", None),
        session,
    )

    # 5. Отправляем ответ пользователю
    await message.answer(response.content)