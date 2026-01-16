import logging
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.price import PriceCreate
from app.crud.price import price_crud
from app.services.deribit_client import DeribitClient

logger = logging.getLogger(__name__)


class PriceService:
    """Service for handling price-related operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def fetch_and_store_prices(self, currencies: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Fetch prices from Deribit and store them in database.
        
        Args:
            currencies: List of currency codes to fetch
            
        Returns:
            Dictionary with fetched prices
        """
        logger.info(f"Fetching prices for currencies: {currencies}")
        
        async with DeribitClient() as client:
            prices = await client.get_multiple_prices(currencies)
        
        # Store valid prices in database
        stored_prices = {}
        for currency, price_data in prices.items():
            if price_data:
                try:
                    # Create price record
                    price_create = PriceCreate(**price_data)
                    stored_price = await price_crud.create(
                        db=self.db,
                        obj_in=price_create
                    )
                    stored_prices[currency] = {
                        "id": stored_price.id,
                        "price": stored_price.price,
                        "timestamp": stored_price.timestamp
                    }
                    logger.info(f"Stored price for {currency}: {stored_price.price}")
                except Exception as e:
                    logger.error(f"Error storing price for {currency}: {e}")
                    stored_prices[currency] = None
            else:
                stored_prices[currency] = None
        
        return stored_prices
    
    async def fetch_all_prices(self) -> Dict[str, Optional[Dict]]:
        """
        Fetch prices for all allowed currencies.
        
        Returns:
            Dictionary with fetched prices
        """
        from app.core.config import settings
        
        currencies = settings.allowed_tickers_list
        return await self.fetch_and_store_prices(currencies)