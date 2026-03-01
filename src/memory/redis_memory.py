"""
Redis-backed conversation memory for production use.

Falls back to in-memory storage if Redis is unavailable.
"""

import json
import logging

import redis.asyncio as redis

from src.config import REDIS_URL

logger = logging.getLogger(__name__)


class RedisMemory:
    """Stores conversation history per session in Redis."""

    def __init__(self, max_messages: int = 40):
        self._max_messages = max_messages
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        try:
            self._client = redis.from_url(REDIS_URL, decode_responses=True)
            await self._client.ping()
            logger.info("Connected to Redis at %s", REDIS_URL)
        except Exception as e:
            logger.warning("Redis unavailable (%s), using in-memory only", e)
            self._client = None

    async def disconnect(self) -> None:
        if self._client:
            await self._client.aclose()

    def _key(self, session_id: str) -> str:
        return f"musingdoc:chat:{session_id}"

    async def add_message(self, session_id: str, role: str, content: str) -> None:
        if not self._client:
            return
        key = self._key(session_id)
        message = json.dumps({"role": role, "content": content})
        await self._client.rpush(key, message)
        await self._client.ltrim(key, -self._max_messages, -1)
        await self._client.expire(key, 86400)  # 24h TTL

    async def get_history(self, session_id: str) -> list[dict]:
        if not self._client:
            return []
        key = self._key(session_id)
        raw = await self._client.lrange(key, 0, -1)
        return [json.loads(m) for m in raw]

    async def clear_session(self, session_id: str) -> None:
        if not self._client:
            return
        await self._client.delete(self._key(session_id))


redis_memory = RedisMemory()
