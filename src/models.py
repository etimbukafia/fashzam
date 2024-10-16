from pydantic import BaseModel, Field 
from typing import List, Any, Optional, Dict
from bson import ObjectId
from fastapi import File, UploadFile


class Products(BaseModel):
    _id: str
    filename: str = Field(..., alias="id")
    gender: str
    masterCategory: str
    subCategory: float
    articleType: int
    baseColour: float
    productName: str = Field(..., alias="productDisplayName")
    cloudinaryUrl: Optional[str] = Field(..., alias="image_link")

class Product(BaseModel):
    productName: str
    gender: str
    articleType: str
    image_link: Optional[str] 
    score: float

    class Config:
        json_encoders = {
            ObjectId: str
        }

class SearchResponse(BaseModel):
    products: List[Product]

class SearchRequest(BaseModel):
    image: UploadFile = File(...)