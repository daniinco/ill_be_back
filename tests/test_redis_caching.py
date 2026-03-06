import pytest
from unittest.mock import patch, AsyncMock
from repositories.prediction_repository import PredictionRedisStorage, PredictionRepository

RAW_PREDICTION = {
    "is_violation": True,
    "probability": 0.85
}

@pytest.mark.asyncio
async def test_get_cached_prediction_hit():
    with patch.object(
        PredictionRedisStorage,
        PredictionRedisStorage.get.__name__,
        AsyncMock(return_value=RAW_PREDICTION),
    ) as redis_get:
        prediction_repo = PredictionRepository()
        result = await prediction_repo.get_cached_prediction(1)
        
        redis_get.assert_called_once_with(1)
        assert result == RAW_PREDICTION

@pytest.mark.asyncio
async def test_get_cached_prediction_miss():
    with patch.object(
        PredictionRedisStorage,
        PredictionRedisStorage.get.__name__,
        AsyncMock(return_value=None),
    ) as redis_get:
        prediction_repo = PredictionRepository()
        result = await prediction_repo.get_cached_prediction(1)
        
        redis_get.assert_called_once_with(1)
        assert result is None

@pytest.mark.asyncio
async def test_cache_prediction():
    with patch.object(
        PredictionRedisStorage,
        PredictionRedisStorage.set.__name__,
        AsyncMock(),
    ) as redis_set:
        prediction_repo = PredictionRepository()
        result = await prediction_repo.cache_prediction(1, RAW_PREDICTION)
        
        redis_set.assert_called_once_with(1, RAW_PREDICTION)
        assert result is None

@pytest.mark.asyncio
async def test_invalidate_prediction():
    with patch.object(
        PredictionRedisStorage,
        PredictionRedisStorage.delete.__name__,
        AsyncMock(),
    ) as redis_delete:
        prediction_repo = PredictionRepository()
        result = await prediction_repo.invalidate_prediction(1)
        
        redis_delete.assert_called_once_with(1)
        assert result is None

@pytest.mark.integration
@pytest.mark.asyncio
async def test_redis_storage_set_and_get():
    storage = PredictionRedisStorage()
    item_id = 999999
    
    await storage.set(item_id, RAW_PREDICTION)
    
    result = await storage.get(item_id)
    assert result is not None
    assert result["is_violation"] == RAW_PREDICTION["is_violation"]
    assert result["probability"] == RAW_PREDICTION["probability"]
    
    await storage.delete(item_id)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_redis_storage_get_nonexistent():
    storage = PredictionRedisStorage()
    item_id = 888888
    
    result = await storage.get(item_id)
    assert result is None

@pytest.mark.integration
@pytest.mark.asyncio
async def test_redis_storage_delete():
    storage = PredictionRedisStorage()
    item_id = 777777
    
    await storage.set(item_id, RAW_PREDICTION)
    result = await storage.get(item_id)
    assert result is not None
    
    await storage.delete(item_id)
    result = await storage.get(item_id)
    assert result is None