from dataclasses import dataclass
from typing import Optional, Dict, Any
import json
import time

@dataclass(frozen=True)
class ScheduledTask:
    """Универсальная задача для шедулера"""
    task_key: str          # Уникальный ключ: task_{user_id}_{timestamp}
    task_type: str         # "message" | "function" | кастомный тип
    payload: Dict[str, Any]  # Данные задачи (сериализуемый dict)
    scheduled_at: float    # timestamp UTC
    created_at: float      # timestamp UTC
    user_id: int           # для быстрого поиска по пользователю

    def to_redis(self) -> str:
        return json.dumps({
            "task_key": self.task_key,
            "task_type": self.task_type,
            "payload": self.payload,
            "scheduled_at": self.scheduled_at,
            "created_at": self.created_at,
            "user_id": self.user_id
        }, ensure_ascii=False)

    @staticmethod
    def from_redis(data: str | bytes) -> "ScheduledTask":
        obj = json.loads(data)
        return ScheduledTask(
            task_key=obj["task_key"],
            task_type=obj["task_type"],
            payload=obj["payload"],
            scheduled_at=obj["scheduled_at"],
            created_at=obj["created_at"],
            user_id=obj["user_id"]
        )

    # Совместимость со старым интерфейсом
    @property
    def message_key(self) -> str:
        return self.task_key

    @property
    def chat_id(self) -> int:
        return self.payload.get("chat_id", 0)

    @property
    def text(self) -> str:
        return self.payload.get("text", "")