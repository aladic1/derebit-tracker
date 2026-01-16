from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.price import price_crud
from app.schemas.price import PriceResponse, PriceListResponse, Price
from app.api.dependencies import validate_ticker, validate_limit, validate_skip, validate_date

router = APIRouter()


@router.get("/prices", response_model=PriceListResponse)
async def get_prices(
    ticker: str = Depends(validate_ticker),
    limit: int = Depends(validate_limit),
    skip: int = Depends(validate_skip),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all price data for a specific currency ticker.
    
    - **ticker**: Currency ticker (BTC or ETH) - required
    - **limit**: Number of records to return (default: 100, max: 1000)
    - **skip**: Number of records to skip for pagination
    """
    prices = await price_crud.get_multi(
        db=db,
        ticker=ticker,
        skip=skip,
        limit=limit
    )
    
    count = await price_crud.get_count(db=db, ticker=ticker)
    
    return PriceListResponse(
        ticker=ticker,
        count=count,
        prices=prices
    )


@router.get("/prices/latest", response_model=Price)
async def get_latest_price(
    ticker: str = Depends(validate_ticker),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the latest price for a specific currency ticker.
    
    - **ticker**: Currency ticker (BTC or ETH) - required
    """
    price = await price_crud.get_latest(db=db, ticker=ticker)
    
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No price data found for ticker: {ticker}"
        )
    
    return Price(
        ticker=price.ticker,
        price=price.price,
        timestamp=price.timestamp
    )


@router.get("/prices/date", response_model=List[Price])
async def get_price_by_date(
    ticker: str = Depends(validate_ticker),
    date_param: date = Query(..., description="Date in YYYY-MM-DD format", alias="date"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get price data for a specific currency ticker and date.
    
    - **ticker**: Currency ticker (BTC or ETH) - required
    - **date**: Date in YYYY-MM-DD format - required
    """
    # Validate that date is not in the future
    today = date.today()
    if date_param > today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date cannot be in the future"
        )
    
    prices = await price_crud.get_by_date(
        db=db,
        ticker=ticker,
        date_param=date_param
    )
    
    if not prices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No price data found for ticker: {ticker} on date: {date_param}"
        )
    
    return [
        Price(
            ticker=price.ticker,
            price=price.price,
            timestamp=price.timestamp
        )
        for price in prices
    ]