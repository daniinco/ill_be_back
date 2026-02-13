import json
from aiokafka import AIOKafkaProducer

class KafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self._bootstrap = bootstrap_servers
        self._producer = None  # AIOKafkaProducer

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(bootstrap_servers=self._bootstrap)
        await self._producer.start()

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()

    async def send_json(self, topic: str, payload: dict) -> None:
        assert self._producer is not None
        data = json.dumps(payload).encode("utf-8")
        await self._producer.send_and_wait(topic, data)