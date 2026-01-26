from fastapi import APIRouter, HTTPException, Depends
from models.models import AdvertRequest
from services.prediction_service import PredictionService
from dependencies import get_prediction_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/")
def predict(
    advertisement: AdvertRequest,
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """
    Предсказывает, есть ли в объявлении нарушения
    """
    try:
        logger.info("Получен запрос на предсказание нарушения")
        predictions = prediction_service.predict_violation(advertisement)
        logger.info("Предсказание успешно")
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")