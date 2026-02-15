from repositories.user_repository import UserRepository
from repositories.advertisement_repository import AdvertisementRepository
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.ad_repo = AdvertisementRepository()
    
    async def create_user(self, name: str, is_verified: bool) -> dict:
        user_id = await self.user_repo.create_user(name, is_verified)
        logger.info(f"User created id: {user_id}")
        return {
            "id": user_id,
            "name": name,
            "is_verified": is_verified
        }
    
    async def create_advertisement(
        self,
        user_id: int,
        item_id: int,
        name: str,
        description: str,
        category: int,
        images_qty: int
    ) -> dict:
        logger.info(f"Creating advertisement user_id: {user_id}")
        
        user = await self.user_repo.get_user(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail=f"id={user_id} не найден")
        
        ad_id = await self.ad_repo.create_advertisement(
            user_id=user_id,
            item_id=item_id,
            name=name,
            description=description,
            category=category,
            images_qty=images_qty
        )
        logger.info(f"Advertisement created id: {ad_id}")
        
        return {
            "id": ad_id,
            "user_id": user_id,
            "item_id": item_id,
            "name": name,
            "description": description,
            "category": category,
            "images_qty": images_qty
        }