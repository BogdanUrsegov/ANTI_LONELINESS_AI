from dataclasses import dataclass
from typing import Optional
import json
import time

@dataclass(frozen=True)
class ScheduledMessage:
    """DTO для отложенного сообщения"""
    message_key: str      # Уникальный ключ: user_{user_id}_{timestamp}
    chat_id: int
    text: str
    scheduled_at: float   # timestamp UTC
    created_at: float     # timestamp UTC
    user_id: int          # для быстрого поиска по пользователю

    def to_redis(self) -> str:
        """Сериализация в JSON для Redis"""
        return json.dumps({
            "message_key": self.message_key,
            "chat_id": self.chat_id,
            "text": self.text,
            "scheduled_at": self.scheduled_at,
            "created_at": self.created_at,
            "user_id": self.user_id
        }, ensure_ascii=False)

    @staticmethod
    def from_redis(data: str | bytes) -> "ScheduledMessage":
        """Десериализация из Redis"""
        obj = json.loads(data)
        return ScheduledMessage(
            message_key=obj["message_key"],
            chat_id=obj["chat_id"],
            text=obj["text"],
            scheduled_at=obj["scheduled_at"],
            created_at=obj["created_at"],
            user_id=obj["user_id"]
        )