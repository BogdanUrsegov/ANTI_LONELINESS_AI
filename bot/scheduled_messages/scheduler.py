import asyncio
import aioredis
import time
import json
from datetime import datetime
from typing import Optional, List, Callable, Dict, Any, Union
from .models import ScheduledTask
from dataclasses import dataclass


class RedisMessageScheduler:
    ZSET_SCHEDULED = "scheduled_tasks:queue"
    HASH_USER_INDEX = "scheduled_tasks:user:{user_id}"

    def __init__(
        self,
        redis_url: str,
        check_interval: float = 1.0
    ):
        self.redis_url = redis_url
        self.check_interval = check_interval
        self._redis: Optional[aioredis.Redis] = None
        self._worker_task: Optional[asyncio.Task] = None
        self._running = False

        # Реестры обработчиков
        self._function_registry: Dict[str, Callable] = {}
        self._task_handlers: Dict[str, Callable] = {
            "message": self._handle_send_message,
            "function": self._handle_function_task,
        }

    async def initialize(self):
        if not self._redis:
            self._redis = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )

    async def close(self):
        self.stop_worker()
        if self._redis:
            await self._redis.close()
            self._redis = None

    # ─── РЕГИСТРАЦИЯ ────────────────────────────────────────────────────────

    def register_function(self, name: str, func: Callable) -> None:
        """Регистрация кастомной асинхронной функции по имени."""
        if not asyncio.iscoroutinefunction(func):
            raise ValueError(f"Function '{name}' must be async (defined with 'async def').")
        self._function_registry[name] = func

    def register_task_handler(self, task_type: str, handler: Callable) -> None:
        """Регистрация обработчика для нового типа задач."""
        self._task_handlers[task_type] = handler

    # ─── ПЛАНИРОВАНИЕ ЗАДАЧ ─────────────────────────────────────────────────

    async def schedule_message(
        self,
        chat_id: int,
        text: str,
        delay_seconds: int,
        user_id: int
    ) -> str:
        """Совместимость со старым интерфейсом."""
        return await self.schedule_task(
            task_type="message",
            payload={"chat_id": chat_id, "text": text},
            delay_seconds=delay_seconds,
            user_id=user_id
        )

    async def schedule_function(
        self,
        function_name: str,
        delay_seconds: int,
        user_id: int,
        **kwargs
    ) -> str:
        """Планирование кастомной функции."""
        if function_name not in self._function_registry:
            raise ValueError(f"Function '{function_name}' not registered. Use register_function() first.")
        return await self.schedule_task(
            task_type="function",
            payload={"function_name": function_name, "kwargs": kwargs},
            delay_seconds=delay_seconds,
            user_id=user_id
        )

    async def schedule_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        delay_seconds: int,
        user_id: int
    ) -> str:
        """Универсальный метод планирования задачи."""
        await self.initialize()
        now = time.time()
        scheduled_at = now + delay_seconds
        task_key = f"task_{user_id}_{int(now * 1000)}"
        task = ScheduledTask(
            task_key=task_key,
            task_type=task_type,
            payload=payload,
            scheduled_at=scheduled_at,
            created_at=now,
            user_id=user_id
        )
        pipe = self._redis.pipeline()
        pipe.zadd(self.ZSET_SCHEDULED, {task.to_redis(): scheduled_at})
        pipe.hset(self.HASH_USER_INDEX.format(user_id=user_id), task_key, task.to_redis())
        await pipe.execute()
        return task_key

    # ─── УПРАВЛЕНИЕ ЗАДАЧАМИ ───────────────────────────────────────────────

    async def cancel_task(self, task_key: str, user_id: int) -> bool:
        task_json = await self._redis.hget(
            self.HASH_USER_INDEX.format(user_id=user_id),
            task_key
        )
        if not task_json:
            return False
        pipe = self._redis.pipeline()
        pipe.zrem(self.ZSET_SCHEDULED, task_json)
        pipe.hdel(self.HASH_USER_INDEX.format(user_id=user_id), task_key)
        results = await pipe.execute()
        return results[0] > 0

    async def get_user_scheduled(self, user_id: int) -> List[ScheduledTask]:
        msgs_json = await self._redis.hvals(
            self.HASH_USER_INDEX.format(user_id=user_id)
        )
        return [ScheduledTask.from_redis(m) for m in msgs_json] if msgs_json else []

    async def cancel_all_user_tasks(self, user_id: int) -> int:
        msgs_json = await self._redis.hvals(
            self.HASH_USER_INDEX.format(user_id=user_id)
        )
        if not msgs_json:
            return 0
        pipe = self._redis.pipeline()
        for msg_json in msgs_json:
            pipe.zrem(self.ZSET_SCHEDULED, msg_json)
        await pipe.execute()
        deleted = await self._redis.delete(
            self.HASH_USER_INDEX.format(user_id=user_id)
        )
        return len(msgs_json)

    # ─── ВСТРОЕННЫЕ ОБРАБОТЧИКИ ─────────────────────────────────────────────

    async def _handle_send_message(self, payload: Dict[str, Any], bot) -> None:
        await bot.send_message(
            chat_id=payload["chat_id"],
            text=payload["text"]
        )

    async def _handle_function_task(self, payload: Dict[str, Any], bot) -> None:
        func_name = payload["function_name"]
        kwargs = payload.get("kwargs", {})
        func = self._function_registry.get(func_name)
        if not func:
            raise RuntimeError(f"Function '{func_name}' missing in registry at execution time")
        # Автоматически передаём bot, если функция его ожидает
        if "bot" in func.__code__.co_varnames[:func.__code__.co_argcount]:
            kwargs["bot"] = bot
        await func(**kwargs)

    # ─── ФОНОВЫЙ ВОРКЕР ─────────────────────────────────────────────────────

    async def _worker_loop(self, bot):
        while self._running:
            try:
                now = time.time()
                ready_tasks = await self._redis.zrangebyscore(
                    self.ZSET_SCHEDULED,
                    0,
                    now,
                    withscores=False
                )
                if ready_tasks:
                    pipe = self._redis.pipeline()
                    for task_json in ready_tasks:
                        try:
                            task = ScheduledTask.from_redis(task_json)
                            handler = self._task_handlers.get(task.task_type)
                            if not handler:
                                print(f"⚠️ No handler for task type: {task.task_type}")
                                pipe.zrem(self.ZSET_SCHEDULED, task_json)
                                continue
                            try:
                                await asyncio.wait_for(handler(task.payload, bot), timeout=60.0)
                            except asyncio.TimeoutError:
                                print(f"⚠️ Task {task.task_key} timed out after 60s")
                            except Exception as e:
                                print(f"⚠️ Error in task {task.task_key}: {e}")
                        except Exception as e:
                            print(f"⚠️ Deserialization error: {e}")
                        pipe.zrem(self.ZSET_SCHEDULED, task_json)
                    await pipe.execute()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️ Worker loop error: {e}")
                await asyncio.sleep(self.check_interval * 2)

    def start_worker(self, bot) -> None:
        if self._running:
            return
        self._running = True
        self._worker_task = asyncio.create_task(
            self._worker_loop(bot),
            name="redis_scheduler_worker"
        )
        print("✅ Универсальный шедулер запущен")

    def stop_worker(self) -> None:
        if not self._running:
            return
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            self._worker_task = None
        print("⏹️ Универсальный шедулер остановлен")