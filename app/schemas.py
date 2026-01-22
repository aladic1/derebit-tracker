from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TickerDataBase(BaseModel):
    ticker: str
    price: float
    timestamp: int

class TickerDataCreate(TickerDataBase):
    pass

class TickerData(TickerDataBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TickerDataResponse(BaseModel):
    success: bool = True
    data: List[TickerData]
    count: int

class PriceResponse(BaseModel):
    success: bool = True
    ticker: str
    price: float
    timestamp: int
    created_at: datetime

class ErrorResponse(BaseModel):
    success: bool = False
    error: str