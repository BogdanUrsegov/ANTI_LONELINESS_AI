# bot/ai/client.py
import httpx
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
AI_BASE_URL = os.getenv("AI_BASE_URL")

http_client = httpx.AsyncClient(
    base_url=AI_BASE_URL,
    headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:8000",  # обязательно для OpenRouter
        "X-Title": "Anti-Loneliness AI",
    },
    timeout=30.0
)