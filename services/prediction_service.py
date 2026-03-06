from models.models import AdvertRequest, PreprocessedAdvertRequest
from repositories.advertisement_repository import AdvertisementRepository
from repositories.prediction_repository import PredictionRepository
import numpy as np
import logging

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
        preprocessed_advert = self.preprocess_advert(advertisement)
        prediction, probability = self.model_predict(preprocessed_advert)
        logger.info(f"Prediction: {prediction}, probability: {probability}")
        return {"is_violation": prediction, "probability": probability}
    
    async def predict_violation_by_item_id(self, item_id: int) -> dict:
        """
        Предсказывает по идентификатору объявления
        """
        logger.info(f"Предсказываем для объявления {item_id}")
        
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
        
        result = {"is_violation": prediction, "probability": probability}
        await prediction_repository.cache_prediction(item_id, result)
        
        return result
    
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