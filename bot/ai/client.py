# bot/ai/client.py
import httpx
import os
from asyncio import Semaphore

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
AI_BASE_URL = os.getenv("AI_BASE_URL")

# ⚠️ Ограничение параллельных запросов к ИИ
# Подбери число под свои лимиты (free-модели часто дают 1–2 RPS)
AI_CONCURRENT_LIMIT = int(os.getenv("AI_CONCURRENT_LIMIT", "2"))
ai_semaphore = Semaphore(AI_CONCURRENT_LIMIT)

http_client = httpx.AsyncClient(
    base_url=AI_BASE_URL,
    headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Anti-Loneliness AI",
    },
    timeout=30.0
)