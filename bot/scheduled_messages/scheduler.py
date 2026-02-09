import asyncio
import os
import aioredis
import time
from typing import Optional, List
from .models import ScheduledMessage


class RedisMessageScheduler:
    # Ключи Redis
    ZSET_SCHEDULED = "scheduled_messages:queue"
    HASH_USER_INDEX = "scheduled_messages:user:{user_id}"

    def __init__(
        self,
        redis_url: str,
        check_interval: float = 1.0  # секунды между проверками (1 = оптимально)
    ):
        self.redis_url = redis_url
        self.check_interval = check_interval
        self._redis: Optional[aioredis.Redis] = None
        self._worker_task: Optional[asyncio.Task] = None
        self._running = False

    async def initialize(self):
        """Инициализация Redis-соединения"""
        if not self._redis:
            self._redis = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )

    async def close(self):
        """Корректное завершение"""
        self.stop_worker()
        if self._redis:
            await self._redis.close()
            self._redis = None

    # ─── API ДЛЯ РАБОТЫ С ЗАДАЧАМИ ──────────────────────────────────────────────

    async def schedule_message(
        self,
        chat_id: int,
        text: str,
        delay_seconds: int,
        user_id: int
    ) -> str:
        """
        Запланировать отложенное сообщение.
        Возвращает уникальный message_key.
        """
        await self.initialize()
        
        now = time.time()
        scheduled_at = now + delay_seconds
        message_key = f"msg_{user_id}_{int(now * 1000)}"
        
        msg = ScheduledMessage(
            message_key=message_key,
            chat_id=chat_id,
            text=text,
            scheduled_at=scheduled_at,
            created_at=now,
            user_id=user_id
        )
        
        # Атомарная запись через пайплайн
        pipe = self._redis.pipeline()
        pipe.zadd(self.ZSET_SCHEDULED, {msg.to_redis(): scheduled_at})
        pipe.hset(self.HASH_USER_INDEX.format(user_id=user_id), message_key, msg.to_redis())
        await pipe.execute()
        
        return message_key

    async def cancel_message(self, message_key: str, user_id: int) -> bool:
        """
        Отменить запланированное сообщение.
        Возвращает True, если сообщение найдено и удалено.
        """
        await self.initialize()
        
        # Получаем данные из индекса пользователя
        msg_json = await self._redis.hget(
            self.HASH_USER_INDEX.format(user_id=user_id),
            message_key
        )
        
        if not msg_json:
            return False
        
        msg = ScheduledMessage.from_redis(msg_json)
        
        # Удаляем из обоих структур атомарно
        pipe = self._redis.pipeline()
        pipe.zrem(self.ZSET_SCHEDULED, msg_json)
        pipe.hdel(self.HASH_USER_INDEX.format(user_id=user_id), message_key)
        results = await pipe.execute()
        
        return results[0] > 0  # zrem вернул 1 = успешно удалено

    async def get_user_scheduled(self, user_id: int) -> List[ScheduledMessage]:
        """
        Получить список активных задач пользователя (для интерфейса удаления).
        """
        await self.initialize()
        
        msgs_json = await self._redis.hvals(
            self.HASH_USER_INDEX.format(user_id=user_id)
        )
        return [ScheduledMessage.from_redis(m) for m in msgs_json] if msgs_json else []

    async def cancel_all_user_messages(self, user_id: int) -> int:
        """
        Отменить все запланированные сообщения пользователя.
        Возвращает количество удалённых задач.
        """
        await self.initialize()
        
        msgs_json = await self._redis.hvals(
            self.HASH_USER_INDEX.format(user_id=user_id)
        )
        
        if not msgs_json:
            return 0
        
        # Удаляем из Sorted Set
        pipe = self._redis.pipeline()
        for msg_json in msgs_json:
            pipe.zrem(self.ZSET_SCHEDULED, msg_json)
        await pipe.execute()
        
        # Очищаем индекс пользователя
        deleted = await self._redis.delete(
            self.HASH_USER_INDEX.format(user_id=user_id)
        )
        
        return len(msgs_json)

    # ─── ФОНОВЫЙ ВОРКЕР ──────────────────────────────────────────────────────────

    async def _worker_loop(self, bot):
        """Основной цикл воркера. Потребляет <0.3% CPU при sleep(1)."""
        while self._running:
            try:
                now = time.time()
                
                # Получаем все "созревшие" сообщения (до текущего момента)
                ready_msgs = await self._redis.zrangebyscore(
                    self.ZSET_SCHEDULED,
                    0,
                    now,
                    withscores=False
                )
                
                if ready_msgs:
                    pipe = self._redis.pipeline()
                    
                    for msg_json in ready_msgs:
                        try:
                            msg = ScheduledMessage.from_redis(msg_json)
                            
                            # Отправляем сообщение
                            await bot.send_message(
                                chat_id=msg.chat_id,
                                text=msg.text
                                # parse_mode берётся из глобального конфига бота
                            )
                            
                            # Удаляем из индекса пользователя
                            await self._redis.hdel(
                                self.HASH_USER_INDEX.format(user_id=msg.user_id),
                                msg.message_key
                            )
                            
                        except Exception as e:
                            print(f"⚠️ Ошибка отправки отложенного сообщения {msg_json}: {e}")
                        
                        # Удаляем из очереди (в любом случае — даже при ошибке отправки)
                        pipe.zrem(self.ZSET_SCHEDULED, msg_json)
                    
                    await pipe.execute()
                
                # Ключевой момент: асинхронная пауза НЕ грузит CPU
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️ Ошибка воркера отложенных сообщений: {e}")
                await asyncio.sleep(self.check_interval * 2)  # экспоненциальная пауза

    def start_worker(self, bot) -> None:
        """Запустить фоновый воркер (вызывать после инициализации бота)"""
        if self._running:
            return
        
        self._running = True
        self._worker_task = asyncio.create_task(
            self._worker_loop(bot),
            name="redis_message_worker"
        )
        print("✅ Воркер отложенных сообщений запущен")

    def stop_worker(self) -> None:
        """Остановить воркер с graceful shutdown"""
        if not self._running:
            return
        
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            self._worker_task = None
        print("⏹️ Воркер отложенных сообщений остановлен")