from fastapi import APIRouter, HTTPException
from models.models import AdvertRequest

router = APIRouter()

@router.post("/")
async def predict(advertisement: AdvertRequest) -> bool:
    """
    Предсказывает, есть ли в объявлении нарушения
    """
    try:
        return advertisement.is_verified_seller or advertisement.images_qty > 0 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")