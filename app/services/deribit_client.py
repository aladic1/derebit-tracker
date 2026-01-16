import aiohttp
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime

from app.core.config import settings


logger = logging.getLogger(__name__)


class DeribitClient:
    """Client for interacting with Deribit API."""
    
    def __init__(self):
        self.base_url = settings.DERIBIT_BASE_URL
        self.api_url = settings.DERIBIT_API_URL
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_index_price(self, currency: str) -> Optional[Dict]:
        """
        Get index price for a currency.
        
        Args:
            currency: Currency code (BTC, ETH)
            
        Returns:
            Dictionary with price data or None if error
        """
        if not self.session:
            raise RuntimeError("Client session not initialized. Use async context manager.")
        
        try:
            # Используем полный API URL
            url = f"{self.api_url}/get_index_price"
            params = {"index_name": f"{currency.lower()}_usd"}
            
            logger.debug(f"Fetching price for {currency} from {url}")
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get("result", {})
                    
                    if "index_price" in result:
                        price_data = {
                            "ticker": currency.upper(),
                            "price": float(result["index_price"]),
                            "timestamp": int(datetime.now().timestamp())
                        }
                        logger.info(f"Successfully fetched price for {currency}: {price_data['price']}")
                        return price_data
                    else:
                        logger.error(f"No index_price in response for {currency}: {result}")
                        return None
                else:
                    error_text = await response.text()
                    logger.error(f"API error for {currency}: {response.status} - {error_text}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching price for {currency}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Client error fetching price for {currency}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching price for {currency}: {e}")
            return None
    
    async def get_multiple_prices(self, currencies: list) -> Dict[str, Optional[Dict]]:
        """
        Get prices for multiple currencies concurrently.
        
        Args:
            currencies: List of currency codes
            
        Returns:
            Dictionary mapping currency to price data or None
        """
        tasks = [self.get_index_price(currency) for currency in currencies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for currency, result in zip(currencies, results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching price for {currency}: {result}")
                prices[currency] = None
            else:
                prices[currency] = result
        
        return prices