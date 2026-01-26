from models.models import AdvertRequest

class PredictionService:
    @staticmethod
    def predict_violation(advertisement: AdvertRequest) -> bool:
        """
        Предсказывает, есть ли в объявлении нарушения
        """
        return advertisement.is_verified_seller or advertisement.images_qty > 0