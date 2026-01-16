from typing import Optional
from datetime import date
from fastapi import Query, HTTPException, status

from app.core.config import settings


def validate_ticker(ticker: str = Query(..., description="Currency ticker (BTC, ETH)")):
    """Validate ticker parameter."""
    from app.core.config import settings
    
    ticker = ticker.upper().strip()
    
    # Получаем список разрешенных тикеров
    allowed_tickers = settings.allowed_tickers_list
    
    if ticker not in allowed_tickers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ticker. Allowed values: {', '.join(allowed_tickers)}"
        )
    return ticker


def validate_limit(limit: int = Query(100, ge=1, le=1000, description="Number of records to return")):
    """Validate limit parameter."""
    return limit


def validate_skip(skip: int = Query(0, ge=0, description="Number of records to skip")):
    """Validate skip parameter."""
    return skip


def validate_date(date_param: Optional[date] = Query(None, description="Date in YYYY-MM-DD format")):
    """Validate date parameter."""
    if date_param:
        # Validate that date is not in the future
        today = date.today()
        if date_param > today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date cannot be in the future"
            )
    return date_param