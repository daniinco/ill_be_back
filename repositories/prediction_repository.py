from dataclasses import dataclass
from typing import Mapping, Any, Optional
from clients.redis import get_redis_connection
from json import loads, dumps
from datetime import timedelta

@dataclass(frozen=True)
class PredictionRedisStorage:
    _TTL: timedelta = timedelta(days=1)

    async def set(self, item_id: int, prediction_result: Mapping[str, Any]) -> None:
        async with get_redis_connection() as connection:
            pipeline = connection.pipeline()
            pipeline.set(
                name=f"prediction:{item_id}",
                value=dumps(prediction_result),
            )
            pipeline.expire(f"prediction:{item_id}", self._TTL)
            await pipeline.execute()
    
    async def get(self, item_id: int) -> Optional[Mapping[str, Any]]:
        async with get_redis_connection() as connection:
            result = await connection.get(f"prediction:{item_id}")

            if result:
                return loads(result)
            
            return None

    async def delete(self, item_id: int) -> None:
        async with get_redis_connection() as connection:
            await connection.delete(f"prediction:{item_id}")

@dataclass(frozen=True)
class PredictionRepository:
    prediction_redis_storage: PredictionRedisStorage = PredictionRedisStorage()

    async def get_cached_prediction(self, item_id: int) -> Optional[Mapping[str, Any]]:
        return await self.prediction_redis_storage.get(item_id)

    async def cache_prediction(self, item_id: int, prediction_result: Mapping[str, Any]) -> None:
        await self.prediction_redis_storage.set(item_id, prediction_result)

    async def invalidate_prediction(self, item_id: int) -> None:
        await self.prediction_redis_storage.delete(item_id)