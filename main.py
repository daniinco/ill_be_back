from fastapi import FastAPI
from routers.predictions import router as predictions_router

app = FastAPI()

@app.get("/")
async def root():
    return {'message': 'Hello World'}

app.include_router(predictions_router, prefix="/predict")