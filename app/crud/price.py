from typing import List, Optional, Tuple
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from sqlalchemy.sql import func

from app.models.price import Price
from app.schemas.price import PriceCreate


class PriceCRUD:
    """CRUD operations for Price model."""
    
    def __init__(self, model):
        self.model = model
    
    async def create(self, db: AsyncSession, *, obj_in: PriceCreate) -> Price:
        """Create a new price record."""
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: int) -> Optional[Price]:
        """Get price by ID."""
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        ticker: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Price]:
        """Get multiple price records by ticker."""
        result = await db.execute(
            select(self.model)
            .where(self.model.ticker == ticker)
            .order_by(desc(self.model.timestamp))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_latest(self, db: AsyncSession, *, ticker: str) -> Optional[Price]:
        """Get the latest price for a ticker."""
        result = await db.execute(
            select(self.model)
            .where(self.model.ticker == ticker)
            .order_by(desc(self.model.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_by_date(
        self, 
        db: AsyncSession, 
        *, 
        ticker: str, 
        date_param: date
    ) -> List[Price]:
        """Get prices for a specific date."""
        # Convert date to timestamp range
        start_timestamp = int(datetime.combine(date_param, datetime.min.time()).timestamp())
        end_timestamp = int(datetime.combine(date_param, datetime.max.time()).timestamp())
        
        result = await db.execute(
            select(self.model)
            .where(
                and_(
                    self.model.ticker == ticker,
                    self.model.timestamp >= start_timestamp,
                    self.model.timestamp <= end_timestamp
                )
            )
            .order_by(self.model.timestamp)
        )
        return result.scalars().all()
    
    async def get_count(self, db: AsyncSession, *, ticker: str) -> int:
        """Get count of price records for a ticker."""
        result = await db.execute(
            select(func.count(self.model.id))
            .where(self.model.ticker == ticker)
        )
        return result.scalar()
    
    async def create_multi(
        self, 
        db: AsyncSession, 
        *, 
        objs_in: List[PriceCreate]
    ) -> List[Price]:
        """Create multiple price records."""
        db_objs = [self.model(**obj.dict()) for obj in objs_in]
        db.add_all(db_objs)
        await db.commit()
        
        # Refresh all objects
        for obj in db_objs:
            await db.refresh(obj)
        
        return db_objs


# Create instance
price_crud = PriceCRUD(Price)