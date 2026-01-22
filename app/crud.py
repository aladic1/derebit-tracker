from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from . import models, schemas

def create_ticker_data(db: Session, ticker_data: schemas.TickerDataCreate):
    db_ticker_data = models.TickerData(
        ticker=ticker_data.ticker,
        price=ticker_data.price,
        timestamp=ticker_data.timestamp
    )
    db.add(db_ticker_data)
    db.commit()
    db.refresh(db_ticker_data)
    return db_ticker_data

def get_ticker_data(db: Session, ticker: str, skip: int = 0, limit: int = 100) -> List[models.TickerData]:
    return db.query(models.TickerData)\
        .filter(models.TickerData.ticker == ticker)\
        .order_by(desc(models.TickerData.timestamp))\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_latest_price(db: Session, ticker: str) -> Optional[models.TickerData]:
    return db.query(models.TickerData)\
        .filter(models.TickerData.ticker == ticker)\
        .order_by(desc(models.TickerData.timestamp))\
        .first()

def get_price_by_date(db: Session, ticker: str, date: datetime) -> Optional[models.TickerData]:
    # Преобразуем дату в UNIX timestamp
    target_timestamp = int(date.timestamp())
    
    # Находим ближайшую запись по времени
    result = db.query(models.TickerData)\
        .filter(models.TickerData.ticker == ticker)\
        .order_by(desc(models.TickerData.timestamp))\
        .all()
    
    # Ищем самую близкую запись по времени
    closest_record = None
    min_diff = float('inf')
    
    for record in result:
        diff = abs(record.timestamp - target_timestamp)
        if diff < min_diff:
            min_diff = diff
            closest_record = record
    
    return closest_record