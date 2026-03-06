import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_user_integration(test_client):
    response = test_client.post("/users", json={
        "name": "Test User",
        "is_verified": True
    })
    
    assert response.status_code == 200
    result = response.json()
    assert "id" in result
    assert result["name"] == "Test User"
    assert result["is_verified"] is True

@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_advertisement_integration(test_client):
    user_response = test_client.post("/users", json={
        "name": "",
        "is_verified": True
    })
    user_id = user_response.json()["id"]
    
    ad_response = test_client.post("/advertisements", json={
        "user_id": user_id,
        "item_id": 12345,
        "name": "",
        "description": "",
        "category": 5,
        "images_qty": 3
    })
    
    assert ad_response.status_code == 200
    result = ad_response.json()
    assert "id" in result
    assert result["item_id"] == 12345

@pytest.mark.integration
@pytest.mark.asyncio
async def test_close_advertisement_integration(test_client):
    user_response = test_client.post("/users", json={
        "name": "",
        "is_verified": True
    })
    user_id = user_response.json()["id"]
    
    ad_response = test_client.post("/advertisements", json={
        "user_id": user_id,
        "item_id": 54321,
        "name": "",
        "description": "",
        "category": 5,
        "images_qty": 3
    })
    
    assert ad_response.status_code == 200
    
    close_response = test_client.delete("/close", params={"item_id": 54321})
    
    assert close_response.status_code == 200
    result = close_response.json()
    assert result["item_id"] == 54321
    assert "message" in result

@pytest.mark.integration
@pytest.mark.asyncio
async def test_close_nonexistent_advertisement(test_client):
    close_response = test_client.delete("/close", params={"item_id": 999999})
    
    assert close_response.status_code == 404