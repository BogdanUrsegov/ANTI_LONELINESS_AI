# bot/ai/utils/chat.py
import os
import httpx
from ..client import http_client
from ..system_prompt import system_prompt
import logging


AI_MODEL = os.getenv("AI_MODEL")

logger = logging.getLogger(__name__)

async def get_ai_response(
    messages: str,
    model: str = AI_MODEL
) -> str:
    """
    Возвращает текст ответа от модели через прямой HTTP-запрос.
    """
    try:
        response = await http_client.post(
            "/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": messages}
                ]
            }
        )
        
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        logger.debug(f"AI response preview: {content[:60]}...")
        return content.strip()
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        raise RuntimeError(f"Ошибка API: {e.response.status_code}")
    except Exception as e:
        logger.error(f"AI request failed: {e}", exc_info=True)
        raise RuntimeError(f"Ошибка генерации ответа ИИ: {str(e)}")


async def generate_personalized_ai_response(
    user_context: dict,
    user_message: str,
    model: str = AI_MODEL
) -> str:
    """
    Формирует персонализированный системный промпт, добавляет историю и новое сообщение,
    отправляет запрос в ИИ и возвращает ТОЛЬКО текст ответа.
    """
    # --- 1. Персонализируем системный промпт ---
    name = user_context.get("name") or "друг"
    archetype = user_context.get("archetype") or "нейтральный"
    main_topic = user_context.get("main_topic") or "общение"

    personalized_system = (f"{system_prompt} "
                           f"Твоего собеседника зовут: {name}. "
                           f"У него проблема: {main_topic}. "
                           f"Общайся в стиле: {archetype}")

    # --- 2. Формируем полный контекст ---
    history = user_context.get("history", [])
    full_context = (
        [{"role": "system", "content": personalized_system}]
        + history
        + [{"role": "user", "content": user_message}]
    )

    # --- 3. Отправляем запрос ---
    try:
        response = await http_client.post(
            "/chat/completions",
            json={
                "model": model,
                "messages": full_context
            }
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return content.strip()
        
    except Exception as e:
        # Логирование по желанию
        raise RuntimeError(f"Ошибка генерации ответа ИИ: {str(e)}")