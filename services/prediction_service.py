from models.models import AdvertRequest, PreprocessedAdvertRequest
from repositories.advertisement_repository import AdvertisementRepository
from repositories.prediction_repository import PredictionRepository
from observability.metrics import (
    PREDICTIONS_TOTAL,
    PREDICTION_DURATION_SECONDS,
    PREDICTION_ERRORS_TOTAL,
    MODEL_PREDICTION_PROBABILITY
)
import numpy as np
import logging
import time

logger = logging.getLogger(__name__)

class PredictionService:
    def __init__(self, model):
        self.model = model

    def predict_violation(self, advertisement: AdvertRequest) -> dict:
        """
        Предсказывает, есть ли в объявлении нарушения
        """
        logger.info("Предсказываем нарушение")
        logger.info(f"Advertisement: {advertisement}")
        try:
            preprocessed_advert = self.preprocess_advert(advertisement)
            prediction, probability = self.model_predict(preprocessed_advert)
            logger.info(f"Prediction: {prediction}, probability: {probability}")
            
            result_label = "violation" if prediction else "no_violation"
            PREDICTIONS_TOTAL.labels(result=result_label).inc()
            MODEL_PREDICTION_PROBABILITY.observe(probability)
            
            return {"is_violation": prediction, "probability": probability}
        except Exception as e:
            PREDICTION_ERRORS_TOTAL.labels(error_type="prediction_error").inc()
            raise
    
    async def predict_violation_by_item_id(self, item_id: int) -> dict:
        """
        Предсказывает по идентификатору объявления
        """
        logger.info(f"Предсказываем для объявления {item_id}")
        
        try:
            prediction_repository = PredictionRepository()
            
            if cached_result := await prediction_repository.get_cached_prediction(item_id):
                logger.info(f"Возвращаем результат из кэша для {item_id}")
                return cached_result
            
            ad_repository = AdvertisementRepository()
            ad_data = await ad_repository.get_advertisement(item_id)
            
            if not ad_data:
                return None
            
            advertisement = AdvertRequest(
                seller_id=ad_data['user_id'],
                is_verified_seller=ad_data['is_verified'],
                item_id=ad_data['item_id'],
                name=ad_data['name'],
                description=ad_data['description'],
                category=ad_data['category'],
                images_qty=ad_data['images_qty']
            )
            
            preprocessed_advert = self.preprocess_advert(advertisement)
            prediction, probability = self.model_predict(preprocessed_advert)
            logger.info(f"Prediction: {prediction}, probability: {probability}")
            
            result_label = "violation" if prediction else "no_violation"
            PREDICTIONS_TOTAL.labels(result=result_label).inc()
            MODEL_PREDICTION_PROBABILITY.observe(probability)
            
            result = {"is_violation": prediction, "probability": probability}
            await prediction_repository.cache_prediction(item_id, result)
            
            return result
        except Exception as e:
            PREDICTION_ERRORS_TOTAL.labels(error_type="prediction_error").inc()
            raise
    
    def preprocess_advert(self, advertisement: AdvertRequest) -> PreprocessedAdvertRequest:
        """
        Препроцессинг объявления
        """
        return PreprocessedAdvertRequest(
            is_verified_seller=float(advertisement.is_verified_seller),
            description_length=len(advertisement.description) / 1000,
            category=advertisement.category / 100,
            images_qty=advertisement.images_qty / 10,
        )
    
    def model_predict(self, preprocessed_advert: PreprocessedAdvertRequest) -> tuple:
        start_time = time.time()
        try:
            features = np.array([
                preprocessed_advert.is_verified_seller,
                preprocessed_advert.description_length,
                preprocessed_advert.category,
                preprocessed_advert.images_qty,
            ]).reshape(1, -1)
            prediction = self.model.predict(features)[0]
            probability = self.model.predict_proba(features)[0, 1]
            prediction = bool(prediction)
            probability = float(probability)
            return prediction, probability
        finally:
            duration = time.time() - start_time
            PREDICTION_DURATION_SECONDS.observe(duration)