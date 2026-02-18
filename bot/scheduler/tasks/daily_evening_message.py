import asyncio
from aiogram.exceptions import TelegramAPIError
import logging
from bot.ai.utils.chat import generate_personalized_ai_response
from bot.database.utils.get_evening_users_with_context import get_evening_users_with_context
from bot.database.utils.get_morning_users_with_context import get_morning_users_with_context
from bot.database.utils.get_day_touches_users_with_context import get_day_touches_users_with_context
from bot.create_bot import bot


logger = logging.getLogger(__name__)


async def daily_evening_message():
    # 1. Получаем данные
    users_data = await get_evening_users_with_context()
    logger.info(f"Начало вечерней рассылки. Найдено пользователей: {len(users_data)}")

    if not users_data:
        return

    # 2. Формируем список задач для параллельного выполнения
    tasks = []
    for user in users_data:
        tasks.append(process_single_user(user))

    # 3. Запускаем все задачи параллельно с ограничением через semaphore внутри generate_personalized_ai_response
    # return_exceptions=True гарантирует, что ошибка у одного пользователя не убьет всю рассылку
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 4. Логируем ошибки (если были)
    errors_count = sum(1 for r in results if isinstance(r, Exception))
    if errors_count:
        logger.warning(f"Вечерняя рассылка завершена. Ошибок: {errors_count} из {len(users_data)}")
    else:
        logger.info("Вечерняя рассылка успешно завершена.")
        

MAX_RETRIES = 3  # Количества попыток
RETRY_DELAY = 2  # Базовая задержка в секундах

async def process_single_user(user: dict):
    """Обработка одного пользователя с повторными попытками генерации ИИ."""
    telegram_id = user["telegram_id"]
    trigger_message = "(Начни разговор сам. Тепло поприветствуй и спроси, как прошел день, пиши коротко)"
    
    ai_text = None
    
    # --- Блок повторных попыток для генерации ИИ ---
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            ai_text = await generate_personalized_ai_response(
                user_context=user,
                user_message=trigger_message
            )
            # Если успешно, выходим из цикла попыток
            break 
        except Exception as e:
            if attempt == MAX_RETRIES:
                # Если это была последняя попытка, логируем критическую ошибку и прерываем обработку этого юзера
                logger.error(f"Не удалось сгенерировать ответ для {telegram_id} после {MAX_RETRIES} попыток: {e}")
                return # Выходим из функции, не отправляем сообщение
            
            # Если есть еще попытки, ждем и пробуем снова (задержка: 2с, 4с...)
            wait_time = RETRY_DELAY * attempt
            logger.warning(f"Попытка {attempt} неудачна для {telegram_id}. Повтор через {wait_time}с... Ошибка: {e}")
            await asyncio.sleep(wait_time)

    # Если текст успешно сгенерирован, отправляем его
    if ai_text:
        try:
            await bot.send_message(
                chat_id=telegram_id,
                text=ai_text
            )
            logger.debug(f"Сообщение успешно отправлено пользователю {telegram_id}")
            
        except TelegramAPIError as e:
            # Ошибки Телеграма (бот заблокирован, нет доступа) не требуют повторной генерации
            logger.error(f"Ошибка отправки Telegram пользователю {telegram_id}: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке пользователю {telegram_id}: {e}")
    else:
        logger.warning(f"ai_text пустой для пользователя {telegram_id}")