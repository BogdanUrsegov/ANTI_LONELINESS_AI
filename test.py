# test_openai.py
import asyncio
import os
from openai import AsyncOpenAI


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