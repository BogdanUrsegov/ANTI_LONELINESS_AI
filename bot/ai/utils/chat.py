# bot/ai/utils/chat.py
from ..client import openrouter_client

async def get_ai_response(
    messages: list[dict],
    model: str = "stepfun/step-3.5-flash:free",
    reasoning: bool = True
) -> dict:
    """
    Возвращает полный объект сообщения от модели, включая reasoning_details (если есть).
    """
    extra_body = {"reasoning": {"enabled": reasoning}} if reasoning else {}
    
    response = await openrouter_client.chat.completions.create(
        model=model,
        messages=messages,
        extra_body=extra_body
    )
    
    message = response.choices[0].message
    
    # OpenRouter может не всегда возвращать reasoning_details — проверяем
    return {
        "content": message.content or "",
        "reasoning_details": getattr(message, "reasoning_details", None)
    }