from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class PriceBase(BaseModel):
    """Base price schema."""
    ticker: str = Field(..., description="Currency ticker (BTC, ETH)")
    price: float = Field(..., description="Price value", ge=0)
    timestamp: int = Field(..., description="UNIX timestamp")


class PriceCreate(PriceBase):
    """Schema for creating a price record."""
    pass


class PriceResponse(PriceBase):
    """Schema for price response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PriceListResponse(BaseModel):
    """Schema for list of prices response."""
    ticker: str
    count: int
    prices: List[PriceResponse]
    
    class Config:
        from_attributes = True


class Price(BaseModel):
    """Simplified price schema for API responses."""
    ticker: str
    price: float
    timestamp: int
    
    class Config:
        from_attributes = True
    
    def dict(self, **kwargs):
        """Override dict to include datetime."""
        d = super().dict(**kwargs)
        # Добавляем datetime из timestamp
        from datetime import datetime
        d['datetime'] = datetime.fromtimestamp(self.timestamp).isoformat()
        return d