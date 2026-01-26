from fastapi import APIRouter, HTTPException
from models.models import AdvertRequest
from services.prediction_service import PredictionService

router = APIRouter()

@router.post("/")
async def predict(advertisement: AdvertRequest) -> bool:
    """
    Предсказывает, есть ли в объявлении нарушения
    """
    try:
        return PredictionService.predict_violation(advertisement)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")