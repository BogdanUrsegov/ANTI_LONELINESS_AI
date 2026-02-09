# bot/ai/utils/chat.py
from ..client import openrouter_client
from ..system_prompt import system_prompt


async def get_ai_response(
    messages: str,
    model: str = "stepfun/step-3.5-flash:free",
    reasoning: bool = True
) -> dict:
    """
    Возвращает полный объект сообщения от модели, включая reasoning_details (если есть).
    """
    extra_body = {"reasoning": {"enabled": reasoning}} if reasoning else {}
    request_body = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": messages
                }
            ]
    response = await openrouter_client.chat.completions.create(
        model=model,
        messages=request_body,
        extra_body=extra_body
    )
    
    message = response.choices[0].message
    
    # OpenRouter может не всегда возвращать reasoning_details — проверяем
    return message.content