# bot/ai/client.py
from openai import AsyncOpenAI
import os


openrouter_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")  # храни в .env!
)