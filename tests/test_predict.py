import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.parametrize("is_verified_seller, name, description, images_qty, expected_result", [
    (True, "Booba", "bebebe", 0, True),  # verified, no images
    (False, "", "", 3, True),  # unverified, with images
    (False, "", "", 0, False),  # uverified, no images
])
def test_predict_valid_fields(is_verified_seller, name, description, images_qty, expected_result):
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
    assert response.json() is expected_result # странно, но просили "На выход данный обработчик должен вернуть лишь одно булево значение." так что наверное надо так

def test_predict_missing_fields():
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
def test_predict_invalid_fields(field_name, invalid_value):
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
