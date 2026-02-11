from fastapi import Request, Depends
from services.prediction_service import PredictionService
from repositories.user_repository import UserRepository
from repositories.advertisement_repository import AdvertisementRepository

def get_model(request: Request):
    return request.app.state.model

def get_prediction_service(request: Request, model = Depends(get_model)) -> PredictionService:
    return PredictionService(model)

def get_user_repository() -> UserRepository:
    return UserRepository()

def get_advertisement_repository() -> AdvertisementRepository:
    return AdvertisementRepository()