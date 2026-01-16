from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.sql import func

from app.core.database import Base


class Price(Base):
    """Price model for storing cryptocurrency prices."""
    
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    price = Column(Float, nullable=False)
    timestamp = Column(Integer, nullable=False, index=True)  # UNIX timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Composite index for faster queries by ticker and timestamp
    __table_args__ = (
        Index('idx_ticker_timestamp', 'ticker', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Price(ticker='{self.ticker}', price={self.price}, timestamp={self.timestamp})>"