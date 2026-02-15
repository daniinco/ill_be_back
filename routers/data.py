from fastapi import APIRouter, HTTPException
from models.models import CreateUserRequest, CreateAdvertRequest
from services.data_service import DataService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/users")
async def create_user(user: CreateUserRequest):
    try:
        service = DataService()
        return await service.create_user(user.name, user.is_verified)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

@router.post("/advertisements")
async def create_advertisement(ad: CreateAdvertRequest):
    try:
        service = DataService()
        return await service.create_advertisement(
            user_id=ad.user_id,
            item_id=ad.item_id,
            name=ad.name,
            description=ad.description,
            category=ad.category,
            images_qty=ad.images_qty
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating advertisement: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")