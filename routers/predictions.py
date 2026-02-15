from fastapi import APIRouter, HTTPException, Depends
from models.models import AdvertRequest
from services.prediction_service import PredictionService
from services.async_moderation_service import AsyncModerationService
from dependencies import get_prediction_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/predict")
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

@router.post("/simple_predict")
async def simple_predict(
    item_id: int,
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """
    Предсказывает, есть ли в объявлении нарушения
    """
    try:
        logger.info("Получен запрос на предсказание нарушения")
        predictions = await prediction_service.predict_violation_by_item_id(item_id)
        
        if predictions is None:
            raise HTTPException(status_code=404, detail="Объявление не найдено")
        
        logger.info("Предсказание успешно")
        return predictions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

@router.post("/async_predict")
async def async_predict(item_id: int):
    try:
        from main import app
        kafka_producer = app.state.kafka_producer
        if kafka_producer is None:
            raise HTTPException(status_code=503, detail="кафка недосупна")
        service = AsyncModerationService(kafka_producer)
        result = await service.create_moderation_task(item_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Объявление не найдено")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

@router.get("/moderation_result/{task_id}")
async def get_moderation_result(task_id: int):
    try:
        from main import app
        kafka_producer = app.state.kafka_producer
        if kafka_producer is None:
            raise HTTPException(status_code=503, detail="кафка недосупна")
        service = AsyncModerationService(kafka_producer)
        result = await service.get_moderation_result(task_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")