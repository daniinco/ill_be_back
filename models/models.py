from pydantic import BaseModel
from typing import Optional

class AdvertRequest(BaseModel):
    seller_id: int
    is_verified_seller: bool
    item_id: int
    name: str
    description: str
    category: int
    images_qty: int

class PreprocessedAdvertRequest(BaseModel):
    is_verified_seller: float
    description_length: float
    category: float
    images_qty: float

class AsyncPredictResponse(BaseModel):
    task_id: int
    status: str
    message: str

class ModerationResultResponse(BaseModel):
    task_id: int
    status: str
    is_violation: Optional[bool] = None
    probability: Optional[float] = None
    error_message: Optional[str] = None

class CreateUserRequest(BaseModel):
    name: str
    is_verified: bool

class CreateAdvertRequest(BaseModel):
    user_id: int
    item_id: int
    name: str
    description: str
    category: int
    images_qty: int