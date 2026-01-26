from fastapi import Request, Depends
from services.prediction_service import PredictionService

def get_model(request: Request):
    return request.app.state.model

def get_prediction_service(request: Request, model = Depends(get_model)) -> PredictionService:
    return PredictionService(model)