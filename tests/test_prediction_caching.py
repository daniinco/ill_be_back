import pytest
import numpy as np
from unittest.mock import patch, AsyncMock, MagicMock
from services.prediction_service import PredictionService
from repositories.prediction_repository import PredictionRepository
from repositories.advertisement_repository import AdvertisementRepository

RAW_AD_DATA = {
    'id': 1,
    'user_id': 1,
    'item_id': 100,
    'name': 'Test Ad',
    'description': 'Test Description',
    'category': 5,
    'images_qty': 3,
    'is_verified': True
}

RAW_PREDICTION = {
    "is_violation": False,
    "probability": 0.25
}

@pytest.mark.asyncio
async def test_predict_violation_by_item_id_cache_hit():
    mock_model = MagicMock()
    
    with patch.object(
        PredictionRepository,
        PredictionRepository.get_cached_prediction.__name__,
        AsyncMock(return_value=RAW_PREDICTION),
    ) as cache_get, patch.object(
        AdvertisementRepository,
        AdvertisementRepository.get_advertisement.__name__,
        AsyncMock(return_value=RAW_AD_DATA),
    ) as ad_get:
        service = PredictionService(mock_model)
        result = await service.predict_violation_by_item_id(100)
        
        cache_get.assert_called_once_with(100)
        ad_get.assert_not_called()
        assert result == RAW_PREDICTION

@pytest.mark.asyncio
async def test_predict_violation_by_item_id_cache_miss():
    mock_model = MagicMock()
    mock_model.predict.return_value = [0]
    mock_model.predict_proba.return_value = [[0.75, 0.25]]
    

    mock_model.predict_proba.return_value = np.array([[0.75, 0.25]])
    
    with patch.object(
        PredictionRepository,
        PredictionRepository.get_cached_prediction.__name__,
        AsyncMock(return_value=None),
    ) as cache_get, patch.object(
        AdvertisementRepository,
        AdvertisementRepository.get_advertisement.__name__,
        AsyncMock(return_value=RAW_AD_DATA),
    ) as ad_get, patch.object(
        PredictionRepository,
        PredictionRepository.cache_prediction.__name__,
        AsyncMock(),
    ) as cache_set:
        service = PredictionService(mock_model)
        result = await service.predict_violation_by_item_id(100)
        
        cache_get.assert_called_once_with(100)
        ad_get.assert_called_once_with(100)
        cache_set.assert_called_once()
        assert "is_violation" in result
        assert "probability" in result

@pytest.mark.asyncio
async def test_predict_violation_by_item_id_not_found():
    mock_model = MagicMock()
    
    with patch.object(
        PredictionRepository,
        PredictionRepository.get_cached_prediction.__name__,
        AsyncMock(return_value=None),
    ), patch.object(
        AdvertisementRepository,
        AdvertisementRepository.get_advertisement.__name__,
        AsyncMock(return_value=None),
    ):
        service = PredictionService(mock_model)
        result = await service.predict_violation_by_item_id(100)
        
        assert result is None