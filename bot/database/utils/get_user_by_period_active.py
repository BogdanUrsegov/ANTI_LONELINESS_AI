import logging
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from collections import defaultdict

from bot.database.session import AsyncSessionLocal
from ..models import User, ChatMessage

logger = logging.getLogger(__name__)

# Тип возвращаемого элемента для ясности
UserContextData = Dict[str, Any]

async def get_user_by_period_active(
    field_name: str,
    messages_limit: int = 15
) -> List[UserContextData]:
    """
    Возвращает список пользователей с включенным notify_evening и их контекстом.
    
    Returns:
        Список словарей вида:
        {
            "telegram_id": int,
            "name": str | None,
            "archetype": str | None,
            "main_topic": str | None,
            "history": [{"role": str, "content": str}, ...]
        }
        История сообщений отсортирована по времени (от старых к новым).
    """
    
    async with AsyncSessionLocal() as session:
        try:
            # 1. Получаем ID и дополнительные поля пользователей
            notify_column = getattr(User, field_name)
            stmt_users = select(
                User.telegram_id, 
                User.name, 
                User.archetype, 
                User.main_topic
            ).where(notify_column.is_(True))
            
            result_users = await session.execute(stmt_users)
            users_data = result_users.all()
            
            if not users_data:
                return []

            # Мапа: telegram_id -> {name, archetype, main_topic}
            user_info_map: Dict[int, Dict[str, Optional[str]]] = {}
            target_telegram_ids = []

            for row in users_data:
                t_id = row.telegram_id
                target_telegram_ids.append(t_id)
                user_info_map[t_id] = {
                    "name": row.name,
                    "archetype": row.archetype,
                    "main_topic": row.main_topic
                }

            # 2. Получаем историю сообщений для всех выбранных пользователей одним запросом
            stmt_messages = (
                select(ChatMessage.telegram_id, ChatMessage.role, ChatMessage.content)
                .where(ChatMessage.telegram_id.in_(target_telegram_ids))
                .order_by(ChatMessage.telegram_id, ChatMessage.created_at.desc()) 
            )
            
            result_messages = await session.execute(stmt_messages)
            all_messages = result_messages.all()

            # 3. Группируем сообщения по telegram_id
            grouped_messages: Dict[int, List[tuple[str, str]]] = defaultdict(list)
            
            for msg in all_messages:
                grouped_messages[msg.telegram_id].append((msg.role, msg.content))

            # 4. Формируем финальный список словарей
            final_result: List[UserContextData] = []
            
            for t_id in target_telegram_ids:
                raw_msgs = grouped_messages.get(t_id, [])
                
                # Берем последние N сообщений (так как сортировка DESC, берем срез)
                limited_raw = raw_msgs[:messages_limit]
                
                # Разворачиваем в хронологический порядок (ASC)
                limited_raw.reverse()
                
                # Преобразуем в список словарей для истории
                history_list = [
                    {"role": role, "content": content} 
                    for role, content in limited_raw
                ]
                
                info = user_info_map.get(t_id, {})
                
                final_result.append({
                    "telegram_id": t_id,
                    "name": info.get("name"),
                    "archetype": info.get("archetype"),
                    "main_topic": info.get("main_topic"),
                    "history": history_list
                })

            return final_result

        except Exception as e:
            logger.error(f"Ошибка get_evening_users_with_context: {e}")
            await session.rollback()
            raise