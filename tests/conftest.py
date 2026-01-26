import pytest
from fastapi.testclient import TestClient
from main import app
from model import load_model

@pytest.fixture
def client():
    model = load_model()
    
    app.state.model = model
    
    with TestClient(app) as test_client:
        yield test_client