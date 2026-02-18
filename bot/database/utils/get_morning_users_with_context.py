import logging
from sqlalchemy import select
from typing import List, Tuple, Dict, Any
from collections import defaultdict

from bot.database.session import AsyncSessionLocal
from ..models import User, ChatMessage
from datetime import datetime


logger = logging.getLogger(__name__)


async def get_morning_users_with_context(
    messages_limit: int = 15
) -> List[Tuple[int, str, List[Dict[str, Any]]]]:
    """
    Возвращает список пользователей с включенным notify_morning и их историей сообщений.
    
    Returns:
        Список кортежей: (telegram_id, name, [список сообщений])
        где сообщение — это dict: {'role': 'user'|'assistant', 'content': '...'}
        Сообщения отсортированы по времени (от старых к новым).
    """
    
    # 1. Получаем ID и имена пользователей, у которых notify_morning = True
    async with AsyncSessionLocal() as session:
        try:
            stmt_users = select(User.telegram_id, User.name).where(
                User.notify_morning.is_(True)
            )
            result_users = await session.execute(stmt_users)
            users_data = result_users.all()
            
            if not users_data:
                return []

            # Создаем мапу для быстрого доступа и сохранения порядка/имен
            # telegram_id -> name
            user_names_map = {row.telegram_id: row.name for row in users_data}
            target_telegram_ids = list(user_names_map.keys())

            # 2. Одним запросом получаем историю сообщений для ВСЕХ этих пользователей
            # Выбираем только нужные поля для экономии памяти
            stmt_messages = (
                select(ChatMessage.telegram_id, ChatMessage.role, ChatMessage.content)
                .where(ChatMessage.telegram_id.in_(target_telegram_ids))
                .order_by(ChatMessage.telegram_id, ChatMessage.created_at.desc()) # Сортируем для удобной группировки
            )
            
            result_messages = await session.execute(stmt_messages)
            all_messages = result_messages.all()

            # 3. Группируем сообщения по telegram_id в памяти
            # Структура: { telegram_id: [ (role, content), ... ] }
            grouped_messages: Dict[int, List[Tuple[str, str]]] = defaultdict(list)
            
            for msg in all_messages:
                # msg.telegram_id, msg.role, msg.content
                grouped_messages[msg.telegram_id].append((msg.role, msg.content))

            # 4. Формируем финальный результат
            final_result: List[Tuple[int, str, List[Dict[str, Any]]]] = []
            
            for t_id in target_telegram_ids:
                raw_msgs = grouped_messages.get(t_id, [])
                
                # Берем только последние N сообщений (так как сортировка была DESC, берем срез [:limit])
                limited_raw = raw_msgs[:messages_limit]
                
                # Разворачиваем обратно в хронологический порядок (ASC) для корректного контекста ИИ
                limited_raw.reverse()
                
                # Преобразуем кортежи в словари для удобства использования в промптах
                context_list = [
                    {"role": role, "content": content} 
                    for role, content in limited_raw
                ]
                
                name = user_names_map.get(t_id, "Пользователь")
                final_result.append((t_id, name, context_list))

            return final_result
        except Exception as e:
            logger.error(f"Ошибка get_morning_users_with_context: {e}")
            await session.rollback()
            raise