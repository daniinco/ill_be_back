from repositories.advertisement_repository import AdvertisementRepository
from repositories.moderation_repository import ModerationRepository
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class AsyncModerationService:
    def __init__(self, kafka_producer):
        self.kafka_producer = kafka_producer
        self.ad_repo = AdvertisementRepository()
        self.mod_repo = ModerationRepository()
    
    async def create_moderation_task(self, item_id: int):
        ad = await self.ad_repo.get_advertisement(item_id)
        if not ad:
            return None
            
        task_id = await self.mod_repo.create_moderation_task(item_id)
        
        msg = {
            "item_id": item_id,
            "task_id": task_id,
            "timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        }
        
        await self.kafka_producer.send_json("moderation", msg)
        logger.info(f"Задача модерации создана: task_id={task_id}")
        
        result = {
            "task_id": task_id,
            "status": "pending",
            "message": "Moderation request acepted"
        }
        return result
    
    async def get_moderation_result(self, task_id: int):
        task = await self.mod_repo.get_moderation_task(task_id)
        if not task:
            return None
            
        result = {
            "task_id": task['id'],
            "status": task['status'],
            "is_violation": task.get('is_violation'),
            "probability": task.get('probability'),
            "error_message": task.get('error_message')
        }
        return result