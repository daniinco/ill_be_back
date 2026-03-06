import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import json
import numpy as np
from repositories.user_repository import UserRepository
from repositories.advertisement_repository import AdvertisementRepository
from repositories.moderation_repository import ModerationRepository

@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_task():
    from main import app
    
    mock_kafka = AsyncMock()
    app.state.kafka_producer = mock_kafka
    
    user_repo = UserRepository()
    ad_repo = AdvertisementRepository()
    
    user_id = await user_repo.create_user("", True)
    ad_id = await ad_repo.create_advertisement(
        user_id=user_id,
        item_id=1,
        name='',
        description='',
        category=1,
        images_qty=1
    )
    
    response = TestClient(app).post(f"/async_predict?item_id={ad_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert 'task_id' in data
    assert data['status'] == 'pending'
    
    mock_kafka.send_json.assert_called_once()
    topic, message = mock_kafka.send_json.call_args[0]
    assert topic == 'moderation'
    assert message['item_id'] == ad_id
    
    await user_repo.delete_user(user_id)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_moderation_result_returns_status():
    from main import app
    
    app.state.kafka_producer = AsyncMock()
    
    user_repo = UserRepository()
    ad_repo = AdvertisementRepository()
    mod_repo = ModerationRepository()
    
    user_id = await user_repo.create_user("", True)
    ad_id = await ad_repo.create_advertisement(
        user_id=user_id,
        item_id=1,
        name='',
        description='',
        category=1,
        images_qty=1
    )
    
    task_id = await mod_repo.create_moderation_task(ad_id)
    await mod_repo.mark_completed(task_id, is_violation=True, probability=0.85)
    
    response = TestClient(app).get(f"/moderation_result/{task_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['task_id'] == task_id
    assert data['status'] == 'completed'
    assert data['is_violation'] == True
    assert data['probability'] == 0.85
    
    await user_repo.delete_user(user_id)


# других тестов не будет