from bot.create_bot import bot


async def first_generated_message(user_id: int):
    text = (
        "Я просто хотел сказать, что не надо быть сильным всё время.\n\n"
        "Как ты сейчас?"
    )
    await bot.send_message(chat_id=user_id, text=text)