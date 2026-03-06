import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from services.data_service import DataService
from repositories.advertisement_repository import AdvertisementRepository
from repositories.prediction_repository import PredictionRepository

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

@pytest.mark.asyncio
async def test_close_advertisement_success():
    with patch.object(
        AdvertisementRepository,
        AdvertisementRepository.get_advertisement.__name__,
        AsyncMock(return_value=RAW_AD_DATA),
    ) as ad_get, patch.object(
        AdvertisementRepository,
        AdvertisementRepository.delete_advertisement.__name__,
        AsyncMock(return_value=True),
    ) as ad_delete, patch.object(
        PredictionRepository,
        PredictionRepository.invalidate_prediction.__name__,
        AsyncMock(),
    ) as cache_invalidate:
        service = DataService()
        result = await service.close_advertisement(100)
        
        ad_get.assert_called_once_with(100)
        ad_delete.assert_called_once_with(1)
        cache_invalidate.assert_called_once_with(100)
        assert result["item_id"] == 100
        assert "message" in result

@pytest.mark.asyncio
async def test_close_advertisement_not_found():
    with patch.object(
        AdvertisementRepository,
        AdvertisementRepository.get_advertisement.__name__,
        AsyncMock(return_value=None),
    ):
        service = DataService()
        
        with pytest.raises(HTTPException) as exc_info:
            await service.close_advertisement(100)
        
        assert exc_info.value.status_code == 404

@pytest.mark.asyncio
async def test_close_advertisement_delete_failed():
    with patch.object(
        AdvertisementRepository,
        AdvertisementRepository.get_advertisement.__name__,
        AsyncMock(return_value=RAW_AD_DATA),
    ), patch.object(
        AdvertisementRepository,
        AdvertisementRepository.delete_advertisement.__name__,
        AsyncMock(return_value=False),
    ):
        service = DataService()
        
        with pytest.raises(HTTPException) as exc_info:
            await service.close_advertisement(100)
        
        assert exc_info.value.status_code == 500