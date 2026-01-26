from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from routers.predictions import router as predictions_router
from model import load_model
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
    yield

    del app.state.model

app = FastAPI(lifespan=lyfespan)

@app.get("/")
async def root():
    return {'message': 'Hello World'}

app.include_router(predictions_router, prefix="/predict")