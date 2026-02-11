# test_openai.py
import asyncio
import os
from openai import AsyncOpenAI


OPENROUTER_API_KEY = "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"
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

async def main():
    resp = await client.chat.completions.create(
        model="stepfun/step-3.5-flash:free",
        messages=[
            {"role": "system", "content": "Ответь 'OK'"},
            {"role": "user", "content": "Привет"}
        ]
    )
    print(resp.choices[0].message.content)

asyncio.run(main())