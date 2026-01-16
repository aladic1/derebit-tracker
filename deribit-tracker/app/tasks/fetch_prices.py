import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.crud.price import price_crud
from app.schemas.price import PriceCreate
from app.services.deribit_client import DeribitClient

logger = logging.getLogger(__name__)

# Создаем engine для Celery
celery_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)


async def fetch_and_store_prices():
    """Async function to fetch and store prices."""
    async_session = sessionmaker(
        bind=celery_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as db:
        try:
            logger.info("Fetching prices from Deribit...")
            
            # Используем Deribit клиент
            async with DeribitClient() as client:
                prices = await client.get_multiple_prices(settings.allowed_tickers_list)
            
            # Сохраняем полученные цены
            saved_prices = []
            for currency, price_data in prices.items():
                if price_data:
                    try:
                        price_create = PriceCreate(**price_data)
                        stored_price = await price_crud.create(db=db, obj_in=price_create)
                        saved_prices.append({
                            "currency": currency,
                            "price": stored_price.price,
                            "timestamp": stored_price.timestamp
                        })
                        logger.info(f"Stored price for {currency}: {stored_price.price}")
                    except Exception as e:
                        logger.error(f"Error storing price for {currency}: {e}")
                else:
                    logger.warning(f"No price data for {currency}")
            
            await db.commit()
            
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "saved_prices": saved_prices,
                "total_fetched": len([p for p in prices.values() if p]),
                "total_currencies": len(prices)
            }
            
        except Exception as e:
            logger.error(f"Error in fetch_and_store_prices: {e}")
            return {"status": "error", "message": str(e)}


def fetch_prices_task():
    """
    Celery task to fetch prices from Deribit and store them in database.
    Runs every minute.
    """
    logger.info("Starting price fetch task...")
    
    try:
        # Получаем или создаем event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Запускаем асинхронную функцию
        result = loop.run_until_complete(fetch_and_store_prices())
        logger.info(f"Price fetch task completed: {result['status']}")
        return result
        
    except Exception as e:
        logger.error(f"Error in fetch_prices_task: {e}")
        return {"status": "error", "message": str(e)}