from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from contextlib import asynccontextmanager
from routers.predictions import router as predictions_router
from routers.data import router as data_router
from clients.kafka import KafkaProducer
from model import load_model
from observability.middleware import PrometheusMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@asynccontextmanager
async def lyfespan(app: FastAPI):
    logger.info("Loading model")
    try:
        app.state.model = load_model()
        logger.info("Model loaded")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise HTTPException(status_code=503, detail=f"Ошибка: {str(e)}")
    
    app.state.kafka_producer = None
    try:
        logger.info("Starting Kafka")
        app.state.kafka_producer = KafkaProducer("localhost:9092")
        await app.state.kafka_producer.start()
        logger.info("Kafka started")
    except Exception as e:
        logger.warning(f"Kafka not available: {e}")
        app.state.kafka_producer = None
    
    yield
    
    if app.state.kafka_producer:
        await app.state.kafka_producer.stop()
        logger.info("Kafka stopped")
    
    del app.state.model

app = FastAPI(lifespan=lyfespan)

app.add_middleware(PrometheusMiddleware)

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    return {'message': 'Hello World'}

app.include_router(predictions_router)
app.include_router(data_router)