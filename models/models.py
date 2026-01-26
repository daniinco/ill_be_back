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