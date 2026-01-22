from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import os
from pathlib import Path
from . import crud, schemas
from .database import get_db, init_db

app = FastAPI(
    title="Deribit Ticker API",
    description="API для получения данных о ценах BTC/USD и ETH/USD с Deribit",
    version="1.0.0"
)

# Инициализируем БД при старте
@app.on_event("startup")
def startup_event():
    print("🚀 Starting Deribit Ticker API...")
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML для главной страницы
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prices</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f0f2f5;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        
        .prices-container {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .price-box {
            width: 280px;
            height: 180px;
            background: white;
            border-radius: 15px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .price-box::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            transition: background 0.3s ease;
        }
        
        .price-box.btc::before {
            background: #f7931a;
        }
        
        .price-box.eth::before {
            background: #627eea;
        }
        
        .price-box.up {
            border: 2px solid #4caf50;
        }
        
        .price-box.down {
            border: 2px solid #f44336;
        }
        
        .price-box.neutral {
            border: 2px solid #e0e0e0;
        }
        
        .ticker-name {
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .btc .ticker-name {
            color: #f7931a;
        }
        
        .eth .ticker-name {
            color: #627eea;
        }
        
        .price {
            font-size: 48px;
            font-weight: bold;
            font-family: 'Courier New', monospace;
            transition: color 0.5s ease;
            margin: 10px 0;
        }
        
        .price.up {
            color: #4caf50;
        }
        
        .price.down {
            color: #f44336;
        }
        
        .price.neutral {
            color: #333;
        }
        
        .pair {
            font-size: 16px;
            color: #666;
            margin-top: 5px;
        }
        
        .update-time {
            position: absolute;
            bottom: 10px;
            font-size: 12px;
            color: #999;
        }
        
        .history-container {
            width: 100%;
            max-width: 800px;
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        }
        
        .history-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .history-header h2 {
            margin: 0;
            color: #333;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        select, input {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        
        button {
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }
        
        button:hover {
            background: #5a67d8;
        }
        
        .history-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .history-table th {
            text-align: left;
            padding: 12px 15px;
            border-bottom: 2px solid #eee;
            color: #666;
            font-weight: normal;
        }
        
        .history-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }
        
        .history-table tr:hover {
            background: #f9f9f9;
        }
        
        .loading {
            text-align: center;
            padding: 30px;
            color: #666;
        }
        
        .error {
            text-align: center;
            padding: 15px;
            background: #fee;
            color: #c33;
            border-radius: 6px;
            margin: 10px 0;
        }
        
        @media (max-width: 650px) {
            .prices-container {
                flex-direction: column;
                gap: 20px;
            }
            
            .history-header {
                flex-direction: column;
                align-items: stretch;
            }
            
            .controls {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="prices-container">
        <!-- Bitcoin -->
        <div class="price-box btc">
            <div class="ticker-name">
                <span>₿</span>
                <span>BITCOIN</span>
            </div>
            <div id="btc-price" class="price neutral">--</div>
            <div class="pair">BTC/USD</div>
            <div id="btc-time" class="update-time"></div>
        </div>
        
        <!-- Ethereum -->
        <div class="price-box eth">
            <div class="ticker-name">
                <span>⧫</span>
                <span>ETHEREUM</span>
            </div>
            <div id="eth-price" class="price neutral">--</div>
            <div class="pair">ETH/USD</div>
            <div id="eth-time" class="update-time"></div>
        </div>
    </div>
    
    <div class="history-container">
        <div class="history-header">
            <h2>📈 Price History</h2>
            <div class="controls">
                <select id="history-ticker">
                    <option value="btc_usd">BTC/USD</option>
                    <option value="eth_usd">ETH/USD</option>
                </select>
                <input type="datetime-local" id="date-filter">
                <button onclick="loadHistory()">Load Data</button>
                <button onclick="clearFilter()">Clear Filter</button>
            </div>
        </div>
        
        <div id="history-content">
            <div class="loading">Select ticker and click "Load Data"</div>
        </div>
    </div>

    <script>
        // Храним предыдущие цены
        let previousPrices = {
            btc: null,
            eth: null
        };
        
        // Функция форматирования цены
        function formatPrice(price) {
            return '$' + price.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
        
        // Функция обновления текущей цены
        async function updatePrice(ticker, elementId) {
            try {
                const response = await fetch(`/api/ticker/latest?ticker=${ticker}`);
                
                if (!response.ok) {
                    throw new Error(`HTTP error: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.success) {
                    const priceElement = document.getElementById(`${elementId}-price`);
                    const boxElement = document.querySelector(`.${elementId}`);
                    const timeElement = document.getElementById(`${elementId}-time`);
                    
                    const currentPrice = data.price;
                    const previousPrice = previousPrices[elementId];
                    
                    // Обновляем цену
                    priceElement.textContent = formatPrice(currentPrice);
                    
                    // Определяем состояние (up/down/neutral)
                    let state = 'neutral';
                    if (previousPrice !== null) {
                        if (currentPrice > previousPrice) {
                            state = 'up';
                        } else if (currentPrice < previousPrice) {
                            state = 'down';
                        }
                    }
                    
                    // Применяем стили
                    priceElement.className = `price ${state}`;
                    boxElement.className = `price-box ${elementId} ${state}`;
                    
                    // Обновляем время
                    if (data.created_at) {
                        const updateTime = new Date(data.created_at);
                        timeElement.textContent = updateTime.toLocaleTimeString();
                    }
                    
                    // Сохраняем текущую цену как предыдущую
                    previousPrices[elementId] = currentPrice;
                    
                    return true;
                }
            } catch (error) {
                console.error(`Error updating ${ticker}:`, error);
                const priceElement = document.getElementById(`${elementId}-price`);
                priceElement.textContent = 'Error';
                priceElement.className = 'price down';
                return false;
            }
        }
        
        // Функция загрузки истории
        async function loadHistory() {
            const ticker = document.getElementById('history-ticker').value;
            const dateFilter = document.getElementById('date-filter').value;
            const container = document.getElementById('history-content');
            
            container.innerHTML = '<div class="loading">Loading data...</div>';
            
            try {
                let url = `/api/ticker/data?ticker=${ticker}&limit=50`;
                
                // Если есть фильтр по дате, используем другой эндпоинт
                if (dateFilter) {
                    const date = new Date(dateFilter);
                    const isoDate = date.toISOString();
                    url = `/api/ticker/price?ticker=${ticker}&date=${encodeURIComponent(isoDate)}`;
                    
                    const response = await fetch(url);
                    const data = await response.json();
                    
                    if (data.success) {
                        const dateObj = new Date(data.created_at);
                        container.innerHTML = `
                            <div>
                                <h3>Price at ${dateObj.toLocaleString()}:</h3>
                                <div style="font-size: 24px; font-weight: bold; margin: 20px 0;">
                                    ${formatPrice(data.price)}
                                </div>
                                <div style="color: #666;">
                                    Ticker: ${data.ticker}<br>
                                    Timestamp: ${data.timestamp}<br>
                                    Recorded: ${dateObj.toLocaleString()}
                                </div>
                            </div>
                        `;
                    } else {
                        container.innerHTML = `<div class="error">${data.detail || 'No data found for this date'}</div>`;
                    }
                } else {
                    // Загрузка всех данных
                    const response = await fetch(url);
                    const data = await response.json();
                    
                    if (data.success && data.data.length > 0) {
                        let html = `
                            <div style="margin-bottom: 15px; color: #666;">
                                Showing ${data.data.length} records
                            </div>
                            <table class="history-table">
                                <thead>
                                    <tr>
                                        <th>Time</th>
                                        <th>Price</th>
                                        <th>Timestamp</th>
                                    </tr>
                                </thead>
                                <tbody>
                        `;
                        
                        data.data.forEach(item => {
                            const date = new Date(item.created_at);
                            html += `
                                <tr>
                                    <td>${date.toLocaleString()}</td>
                                    <td style="font-family: 'Courier New', monospace; font-weight: bold;">
                                        ${formatPrice(item.price)}
                                    </td>
                                    <td style="color: #666; font-size: 0.9em;">
                                        ${item.timestamp}
                                    </td>
                                </tr>
                            `;
                        });
                        
                        html += '</tbody></table>';
                        container.innerHTML = html;
                    } else {
                        container.innerHTML = '<div class="loading">No data available yet</div>';
                    }
                }
            } catch (error) {
                console.error('Error loading history:', error);
                container.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        // Функция очистки фильтра
        function clearFilter() {
            document.getElementById('date-filter').value = '';
            loadHistory();
        }
        
        // Функция обновления всех текущих цен
        async function refreshAll() {
            await updatePrice('btc_usd', 'btc');
            await updatePrice('eth_usd', 'eth');
        }
        
        // Инициализация
        window.onload = function() {
            // Установка текущей даты в фильтр
            const now = new Date();
            now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
            document.getElementById('date-filter').value = now.toISOString().slice(0, 16);
            
            // Первоначальная загрузка
            refreshAll();
            loadHistory();
            
            // Автообновление текущих цен каждую секунду
            setInterval(refreshAll, 1000);
            
            // Автообновление истории каждые 30 секунд (только если нет фильтра по дате)
            setInterval(() => {
                if (!document.getElementById('date-filter').value) {
                    loadHistory();
                }
            }, 30000);
        };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с дашбордом"""
    return HTMLResponse(content=INDEX_HTML)


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Остальные эндпоинты API остаются без изменений
@app.get("/api/ticker/data", response_model=schemas.TickerDataResponse)
def get_all_data(
    ticker: str = Query(..., description="Тикер валюты (btc_usd или eth_usd)"),
    skip: int = Query(0, description="Количество записей для пропуска"),
    limit: int = Query(100, description="Лимит записей"),
    db: Session = Depends(get_db)
):
    """Получение всех сохраненных данных по указанной валюте"""
    if ticker not in ["btc_usd", "eth_usd"]:
        raise HTTPException(status_code=400, detail="Invalid ticker. Use 'btc_usd' or 'eth_usd'")
    
    data = crud.get_ticker_data(db, ticker=ticker, skip=skip, limit=limit)
    return {
        "success": True,
        "data": data,
        "count": len(data)
    }

@app.get("/api/ticker/latest", response_model=schemas.PriceResponse)
def get_latest_price(
    ticker: str = Query(..., description="Тикер валюты (btc_usd или eth_usd)"),
    db: Session = Depends(get_db)
):
    """Получение последней цены валюты"""
    if ticker not in ["btc_usd", "eth_usd"]:
        raise HTTPException(status_code=400, detail="Invalid ticker. Use 'btc_usd' or 'eth_usd'")
    
    data = crud.get_latest_price(db, ticker=ticker)
    if not data:
        raise HTTPException(status_code=404, detail="No data found for this ticker")
    
    return {
        "success": True,
        "ticker": data.ticker,
        "price": data.price,
        "timestamp": data.timestamp,
        "created_at": data.created_at
    }

@app.get("/api/ticker/price", response_model=schemas.PriceResponse)
def get_price_by_date(
    ticker: str = Query(..., description="Тикер валюты (btc_usd или eth_usd)"),
    date: str = Query(..., description="Дата в формате YYYY-MM-DDTHH:MM:SS"),
    db: Session = Depends(get_db)
):
    """Получение цены валюты с фильтром по дате"""
    if ticker not in ["btc_usd", "eth_usd"]:
        raise HTTPException(status_code=400, detail="Invalid ticker. Use 'btc_usd' or 'eth_usd'")
    
    try:
        target_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS")
    
    data = crud.get_price_by_date(db, ticker=ticker, date=target_date)
    if not data:
        raise HTTPException(status_code=404, detail="No data found for this date")
    
    return {
        "success": True,
        "ticker": data.ticker,
        "price": data.price,
        "timestamp": data.timestamp,
        "created_at": data.created_at
    }