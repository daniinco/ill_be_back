import pytest
from repositories.user_repository import UserRepository
from repositories.advertisement_repository import AdvertisementRepository

@pytest.mark.integration
@pytest.mark.asyncio
async def test_sp_pos(client):
    user_repo = UserRepository()
    ad_repo = AdvertisementRepository()
    
    user_id = await user_repo.create_user("", True)
    ad_id = await ad_repo.create_advertisement(
        user_id=user_id,
        item_id=1,
        name="",
        description="",
        category=1,
        images_qty=1
    )
    
    response = client.post(f"/simple_predict?item_id={ad_id}")
    
    assert response.status_code == 200
    result = response.json()
    assert "is_violation" in result
    assert "probability" in result
    assert isinstance(result["is_violation"], bool)
    assert isinstance(result["probability"], float)
    assert result["is_violation"] is False
    
    await ad_repo.delete_advertisement(ad_id)
    await user_repo.delete_user(user_id)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_sp_neg(client):
    user_repo = UserRepository()
    ad_repo = AdvertisementRepository()
    
    user_id = await user_repo.create_user("", False)
    ad_id = await ad_repo.create_advertisement(
        user_id=user_id,
        item_id=1,
        name="",
        description="",
        category=1,
        images_qty=0
    )
    
    response = client.post(f"/simple_predict?item_id={ad_id}")
    
    assert response.status_code == 200
    result = response.json()
    assert "is_violation" in result
    assert "probability" in result
    assert isinstance(result["is_violation"], bool)
    assert isinstance(result["probability"], float)
    assert result["is_violation"] is True
    
    await ad_repo.delete_advertisement(ad_id)
    await user_repo.delete_user(user_id)

@pytest.mark.integration
def test_sp_not_fund(client):
    response = client.post("/simple_predict?item_id=666")
    
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "не найдено" in result["detail"].lower()

def test_sp_invalid(client):
    response = client.post("/simple_predict?item_id=bebee")
    
    assert response.status_code == 422