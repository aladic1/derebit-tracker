import aiohttp
import asyncio
from celery import Celery
from sqlalchemy.orm import Session
from typing import Dict, Any
import os
from datetime import datetime
from .database import SessionLocal
from . import crud, schemas
import time

# Настройка Celery
celery_app = Celery(
    'deribit_tasks',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

class DeribitClient:
    def __init__(self):
        self.base_url = os.getenv("DERIBIT_BASE_URL", "https://www.deribit.com/api/v2")
    
    async def get_index_price(self, currency: str) -> Dict[str, Any]:
        """Получаем индексную цену для валюты"""
        url = f"{self.base_url}/public/get_index_price"
        params = {
            "index_name": f"{currency}_usd"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("result", {})
                else:
                    raise Exception(f"Error fetching price: {response.status}")

async def fetch_prices():
    """Асинхронная функция для получения цен"""
    client = DeribitClient()
    tickers = ["btc", "eth"]
    results = []
    
    for ticker in tickers:
        try:
            data = await client.get_index_price(ticker)
            price = data.get("index_price")
            if price:
                results.append({
                    "ticker": f"{ticker}_usd",
                    "price": price,
                    "timestamp": int(time.time())
                })
        except Exception as e:
            print(f"Error fetching {ticker} price: {e}")
    
    return results

@celery_app.task
def save_prices_to_db():
    """Celery задача для сохранения цен в базу данных"""
    # Запускаем асинхронную функцию
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        prices_data = loop.run_until_complete(fetch_prices())
        
        db = SessionLocal()
        try:
            for price_data in prices_data:
                ticker_data = schemas.TickerDataCreate(**price_data)
                crud.create_ticker_data(db, ticker_data)
                print(f"Saved {price_data['ticker']}: ${price_data['price']}")
        finally:
            db.close()
    finally:
        loop.close()
    
    return {"success": True, "count": len(prices_data)}

# Периодическая задача каждую минуту
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        60.0,  # каждые 60 секунд
        save_prices_to_db.s(),
        name='fetch-and-save-prices-every-minute'
    )