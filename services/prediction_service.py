from models.models import AdvertRequest, PreprocessedAdvertRequest
import numpy as np
import logging

logger = logging.getLogger(__name__)

class PredictionService:
    def __init__(self, model):
        self.model = model

    def predict_violation(self, advertisement: AdvertRequest) -> bool:
        """
        Предсказывает, есть ли в объявлении нарушения
        """
        logger.info("Предсказываем нарушение")
        logger.info(f"Advertisement: {advertisement}")
        preprocessed_advert = self.preprocess_advert(advertisement)
        prediction, probability = self.model_predict(preprocessed_advert)
        logger.info(f"Prediction: {prediction}, probability: {probability}")
        return {"is_violation": prediction, "probability": probability}
    
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
    
    def model_predict(self, preprocessed_advert: PreprocessedAdvertRequest) -> bool:
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