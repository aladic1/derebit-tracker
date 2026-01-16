import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.price_service import PriceService
from app.schemas.price import PriceCreate


class TestPriceService:
    """Test PriceService class."""
    
    @pytest.mark.asyncio
    async def test_fetch_and_store_prices(
        self, 
        db_session: AsyncSession,
        mock_deribit_client
    ):
        """Test fetch_and_store_prices method."""
        # Mock Deribit client response
        mock_price_data = {
            "ticker": "BTC",
            "price": 45000.50,
            "timestamp": int(datetime.now().timestamp())
        }
        mock_deribit_client.get_multiple_prices.return_value = {
            "BTC": mock_price_data,
            "ETH": None  # Simulate error for ETH
        }
        
        # Create service instance
        service = PriceService(db=db_session)
        
        # Call method
        result = await service.fetch_and_store_prices(["BTC", "ETH"])
        
        # Assert results
        assert "BTC" in result
        assert result["BTC"] is not None
        assert result["BTC"]["price"] == 45000.50
        
        assert "ETH" in result
        assert result["ETH"] is None
        
        # Verify mock was called
        mock_deribit_client.get_multiple_prices.assert_called_once_with(["BTC", "ETH"])
    
    @pytest.mark.asyncio
    async def test_fetch_all_prices(
        self, 
        db_session: AsyncSession,
        mock_deribit_client
    ):
        """Test fetch_all_prices method."""
        # Mock Deribit client response
        mock_price_data = {
            "ticker": "BTC",
            "price": 45000.50,
            "timestamp": int(datetime.now().timestamp())
        }
        mock_deribit_client.get_multiple_prices.return_value = {
            "BTC": mock_price_data,
            "ETH": None
        }
        
        # Create service instance
        service = PriceService(db=db_session)
        
        # Call method
        result = await service.fetch_all_prices()
        
        # Assert results
        assert "BTC" in result
        assert "ETH" in result
        assert result["BTC"] is not None
        assert result["ETH"] is None
    
    @pytest.mark.asyncio
    async def test_fetch_prices_empty_response(
        self, 
        db_session: AsyncSession,
        mock_deribit_client
    ):
        """Test fetch_and_store_prices with empty response."""
        # Mock empty response
        mock_deribit_client.get_multiple_prices.return_value = {
            "BTC": None,
            "ETH": None
        }
        
        # Create service instance
        service = PriceService(db=db_session)
        
        # Call method
        result = await service.fetch_and_store_prices(["BTC", "ETH"])
        
        # Assert results
        assert result["BTC"] is None
        assert result["ETH"] is None