import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from repositories.advertisement_repository import AdvertisementRepository
from repositories.moderation_repository import ModerationRepository
from models.models import AdvertRequest, PreprocessedAdvertRequest
from model import load_model
import numpy as np
import logging
from datetime import datetime

from .settings import KAFKA_BOOTSTRAP, TOPIC, DLQ_TOPIC, CONSUMER_GROUP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModerationWorker:
    def __init__(self):
        self.model = None
        self.ad_repo = AdvertisementRepository()
        self.mod_repo = ModerationRepository()
        
    def preprocess_advert(self, ad: AdvertRequest):
        preprocessed = PreprocessedAdvertRequest(
            is_verified_seller=float(ad.is_verified_seller),
            description_length=len(ad.description) / 1000,
            category=ad.category / 100,
            images_qty=ad.images_qty / 10,
        )
        return preprocessed
    
    def model_predict(self, preprocessed_ad):
        features = np.array([
            preprocessed_ad.is_verified_seller,
            preprocessed_ad.description_length,
            preprocessed_ad.category,
            preprocessed_ad.images_qty,
        ]).reshape(1, -1)
        
        pred = self.model.predict(features)[0]
        prob = self.model.predict_proba(features)[0, 1]
        
        return bool(pred), float(prob)
    
    async def process_message(self, msg, dlq_producer):
        item_id = msg.get("item_id")
        task_id = msg.get("task_id")
        
        try:
            ad_data = await self.ad_repo.get_advertisement(item_id)
            
            if not ad_data:
                raise ValueError(f"Advertisement not found: item_id={item_id}")
            
            ad = AdvertRequest(
                seller_id=ad_data['user_id'],
                is_verified_seller=ad_data['is_verified'],
                item_id=ad_data['item_id'],
                name=ad_data['name'],
                description=ad_data['description'],
                category=ad_data['category'],
                images_qty=ad_data['images_qty']
            )
            
            preprocessed = self.preprocess_advert(ad)
            is_violation, prob = self.model_predict(preprocessed)
            
            await self.mod_repo.mark_completed(task_id, is_violation, prob)
            
        except Exception as e:
            err_msg = str(e)
            
            await self.mod_repo.mark_failed(task_id, err_msg)
            
            dlq_msg = {
                "original_message": msg,
                "error": err_msg,
                "timestamp": datetime.utcnow().isoformat(),
                "retry_count": 1
            }
            
            dlq_data = json.dumps(dlq_msg).encode("utf-8")
            await dlq_producer.send_and_wait(DLQ_TOPIC, dlq_data)

async def main():
    worker = ModerationWorker()
    
    worker.model = load_model()
    
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=CONSUMER_GROUP,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )
    
    dlq_producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP)
    
    await consumer.start()
    await dlq_producer.start()
    
    logger.info(f"Worker consuming from topic '{TOPIC}' as group '{CONSUMER_GROUP}'")
    
    try:
        async for msg in consumer:
            try:
                message = json.loads(msg.value.decode("utf-8"))
                
                await worker.process_message(message, dlq_producer)
                
                await consumer.commit()
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await consumer.commit()
                
    finally:
        await consumer.stop()
        await dlq_producer.stop()

if __name__ == "__main__":
    asyncio.run(main())