import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_predict_verified():
    """is_verified_seller == True, images_qty == 0"""
    request_data = {
        "seller_id": 1,
        "is_verified_seller": True,
        "item_id": 1,
        "name": "Booba",
        "description": "bebebe",
        "category": 1,
        "images_qty": 0
    }
    
    response = client.post("/predict/", json=request_data)
    assert response.status_code == 200
    assert response.json() is True # странно, но просили "На выход данный обработчик должен вернуть лишь одно булево значение." так что наверное надо так

def test_predict_unverified_images():
    """is_verified_seller == False, images_qty != 0"""
    request_data = {
        "seller_id": 1,
        "is_verified_seller": False,
        "item_id": 1,
        "name": "",
        "description": "",
        "category": 1,
        "images_qty": 3
    }
    
    response = client.post("/predict/", json=request_data)
    assert response.status_code == 200
    assert response.json() is True

def test_predict_unverified_no_images():
    """is_verified_seller == False, images_qty == 0"""
    request_data = {
        "seller_id": 1,
        "is_verified_seller": False,
        "item_id": 1,
        "name": "",
        "description": "",
        "category": 1,
        "images_qty": 0
    }
    
    response = client.post("/predict/", json=request_data)
    assert response.status_code == 200
    assert response.json() is False

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

def test_predict_invalid_fields_1():
    """Bad fields"""
    request_data = {
        "seller_id": 2.5,
        "is_verified_seller": False,
        "item_id": 1,
        "name": "",
        "description": "",
        "category": 1,
        "images_qty": 1
    }
    
    response = client.post("/predict/", json=request_data)
    assert response.status_code == 422

def test_predict_invalid_fields_2():
    """Bad fields"""
    request_data = {
        "seller_id": 2,
        "is_verified_seller": 4,
        "item_id": 1,
        "name": "",
        "description": "",
        "category": 1,
        "images_qty": 1
    }
    
    response = client.post("/predict/", json=request_data)
    assert response.status_code == 422
