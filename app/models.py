from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .database import Base

class TickerData(Base):
    __tablename__ = "ticker_data"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(Integer, nullable=False)  # UNIX timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<TickerData(ticker={self.ticker}, price={self.price}, timestamp={self.timestamp})>"