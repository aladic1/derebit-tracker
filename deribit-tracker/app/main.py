from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api.endpoints import router as api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Deribit Price Tracker API...")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Allowed tickers: {settings.ALLOWED_TICKERS}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Deribit Price Tracker API...")


# Create FastAPI app
app = FastAPI(
    title="Deribit Price Tracker API",
    description="API для отслеживания цен криптовалют с биржи Deribit",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Deribit Price Tracker API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else None,
        "endpoints": {
            "get_all_prices": "/api/v1/prices?ticker={ticker}",
            "get_latest_price": "/api/v1/prices/latest?ticker={ticker}",
            "get_price_by_date": "/api/v1/prices/date?ticker={ticker}&date={date}",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "deribit-tracker"}