import pytest
from models.models import AdvertRequest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from main import app

@pytest.mark.parametrize("is_verified_seller, name, description, images_qty", [
    (True, "Booba", "bebebe", 0),  # verified, no images
    (False, "", "", 3),  # unverified, with images
    (False, "", "", 0),  # unverified, no images
])
def test_predict_valid_fields(client, is_verified_seller, name, description, images_qty):
    """Valid prediction parameters"""
    request_data = {
        "seller_id": 1,
        "is_verified_seller": is_verified_seller,
        "item_id": 1,
        "name": name,
        "description": description,
        "category": 1,
        "images_qty": images_qty
    }
    
    response = client.post("/predict/", json=request_data)
    assert response.status_code == 200
    result = response.json()
    assert "is_violation" in result
    assert "probability" in result
    assert isinstance(result["is_violation"], bool)
    assert isinstance(result["probability"], float)
    assert 0 <= result["probability"] <= 1

def test_predict_missing_fields(client):
    """Missing fields"""
    request_data = {
        "is_verified_seller": False,
        "item_id": 1,
        "name": "",
        "description": "",
        "images_qty": 1
    }
    
    response = client.post("/predict/", json=request_data)
    assert response.status_code == 422

@pytest.mark.parametrize("field_name, invalid_value", [
    ("seller_id", 2.5),
    ("is_verified_seller", 4),
    ("item_id", "string"),
    ("name", 123),
    ("description", 456),
    ("category", "string"),
    ("images_qty", "string"),
])
def test_predict_invalid_fields(client, field_name, invalid_value):
    """Invalid prediction parameters"""
    request_data = {
        "seller_id": 1,
        "is_verified_seller": False,
        "item_id": 1,
        "name": "",
        "description": "",
        "category": 1,
        "images_qty": 1
    }
    request_data[field_name] = invalid_value
    
    response = client.post("/predict/", json=request_data)
    assert response.status_code == 422

@pytest.mark.parametrize("is_verified_seller, images_qty, answer", [
    ("False", 0, True),
    ("True", 5, False),
])
def test_predict_violation_true_false(client, is_verified_seller, images_qty, answer):
    """Test True"""
    request_data = {
        "seller_id": 1,
        "is_verified_seller": is_verified_seller,
        "item_id": 1,
        "name": "Test Item",
        "description": "Test Description",
        "category": 1,
        "images_qty": images_qty
    }
    
    response = client.post("/predict/", json=request_data)
    assert response.status_code == 200
    result = response.json()
    assert "is_violation" in result
    assert "probability" in result
    assert isinstance(result["is_violation"], bool)
    assert isinstance(result["probability"], float)
    assert result["is_violation"] is answer

def test_model_unavailable():
    """Test unavailable"""
    with TestClient(app) as test_client:
        app.state.model = 5
        
        request_data = {
            "seller_id": 1,
            "is_verified_seller": False,
            "item_id": 1,
            "name": "",
            "description": "",
            "category": 1,
            "images_qty": 0
        }
        
        response = test_client.post("/predict/", json=request_data)
        
        assert response.status_code == 500
        result = response.json()
        assert "detail" in result
        assert "Ошибка" in result["detail"]
