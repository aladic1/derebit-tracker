import pytest
from unittest.mock import patch, AsyncMock
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.price import price_crud
from app.schemas.price import PriceCreate


class TestAPIEndpoints:
    """Test API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_prices(
        self, 
        test_client, 
        db_session: AsyncSession,
        sample_price_data
    ):
        """Test GET /api/v1/prices endpoint."""
        # Create test data
        price_create = PriceCreate(**sample_price_data)
        await price_crud.create(db_session, obj_in=price_create)
        
        # Make request
        response = test_client.get("/api/v1/prices?ticker=BTC")
        
        # Assert response
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "BTC"
        assert data["count"] >= 1
        assert len(data["prices"]) >= 1
        assert data["prices"][0]["ticker"] == "BTC"
        assert data["prices"][0]["price"] == 45000.50
    
    @pytest.mark.asyncio
    async def test_get_prices_invalid_ticker(self, test_client):
        """Test GET /api/v1/prices with invalid ticker."""
        response = test_client.get("/api/v1/prices?ticker=INVALID")
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid ticker" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_get_latest_price(
        self, 
        test_client, 
        db_session: AsyncSession,
        sample_price_data
    ):
        """Test GET /api/v1/prices/latest endpoint."""
        # Create test data
        price_create = PriceCreate(**sample_price_data)
        await price_crud.create(db_session, obj_in=price_create)
        
        # Make request
        response = test_client.get("/api/v1/prices/latest?ticker=BTC")
        
        # Assert response
        assert response.status_code == 200
        data = response.json()
        assert data["ticker"] == "BTC"
        assert data["price"] == 45000.50
        assert data["timestamp"] == 1672531200
        assert "datetime" in data
    
    @pytest.mark.asyncio
    async def test_get_latest_price_not_found(self, test_client):
        """Test GET /api/v1/prices/latest when no data exists."""
        response = test_client.get("/api/v1/prices/latest?ticker=BTC")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "No price data found" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_get_price_by_date(
        self, 
        test_client, 
        db_session: AsyncSession,
        sample_price_data
    ):
        """Test GET /api/v1/prices/date endpoint."""
        # Create test data
        price_create = PriceCreate(**sample_price_data)
        await price_crud.create(db_session, obj_in=price_create)
        
        # Make request with date 2023-01-01
        response = test_client.get("/api/v1/prices/date?ticker=BTC&date=2023-01-01")
        
        # Assert response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert data[0]["ticker"] == "BTC"
            assert data[0]["price"] == 45000.50
    
    def test_get_price_by_date_missing_date(self, test_client):
        """Test GET /api/v1/prices/date without date parameter."""
        response = test_client.get("/api/v1/prices/date?ticker=BTC")
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Date parameter is required" in data["detail"]
    
    def test_get_price_by_date_future_date(self, test_client):
        """Test GET /api/v1/prices/date with future date."""
        response = test_client.get("/api/v1/prices/date?ticker=BTC&date=2100-01-01")
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Date cannot be in the future" in data["detail"]
    
    def test_root_endpoint(self, test_client):
        """Test root endpoint."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Deribit Price Tracker API"
        assert "version" in data
        assert "endpoints" in data
    
    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "deribit-tracker"