"""
AlphaSignal - Alternative Data Alpha Research Platform
FastAPI Main Application
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import logging
import uvicorn

from config import settings, get_required_env_vars
from database import engine, Base, get_db
from models import (
    AlphaMarketData, SentimentData, SocialSignals,
    Predictions, FactorExposures, TechnicalIndicators
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Create database tables
    logger.info("📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully")

    # Check environment variables
    logger.info("🔑 Checking API keys and configuration...")
    env_status = get_required_env_vars()
    for key, status in env_status.items():
        logger.info(f"  {key}: {status}")

    # TODO: Load ML models
    logger.info("🤖 ML models will be loaded in Phase 4")

    # TODO: Initialize C++ indicators
    if settings.USE_CPP_INDICATORS:
        logger.info("⚡ C++ indicators will be initialized in Phase 3")

    logger.info("✅ AlphaSignal API is ready!")

    yield

    # Shutdown
    logger.info("👋 Shutting down AlphaSignal API...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Quantitative alpha research platform with alternative data, ML predictions, and factor analysis",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Health Check Endpoints =====

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connectivity"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
        raise HTTPException(status_code=503, detail="Database unavailable")

    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": db_status,
        "features": {
            "sentiment_analysis": True,
            "ml_predictions": True,  # Will be implemented in Phase 4
            "factor_analysis": True,  # Will be implemented in Phase 5
            "cpp_indicators": settings.USE_CPP_INDICATORS
        }
    }


@app.get("/api/v1/config")
async def get_config():
    """Get public configuration and feature status"""
    env_status = get_required_env_vars()

    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "features": {
            "news_api": "✓" in env_status.get("NEWS_API_KEY", "✗"),
            "reddit_api": "✓" in env_status.get("REDDIT_CLIENT_ID", "✗"),
            "market_data": True,  # Always available via yfinance
            "cpp_indicators": settings.USE_CPP_INDICATORS
        },
        "default_tickers": settings.DEFAULT_TICKERS,
        "model_version": settings.MODEL_VERSION
    }


# ===== Demo API Endpoint =====
from api.v1 import demo
app.include_router(demo.router, prefix="/api/v1/demo", tags=["Demo"])

# ===== Phase 4-6 API Endpoints =====
from api.v1 import predictions, factors

# ML Predictions API
app.include_router(predictions.router, prefix="/api/v1", tags=["ML Predictions"])

# Factor Analysis API
app.include_router(factors.router, prefix="/api/v1", tags=["Factor Analysis"])

# TODO Phase 6 - Sentiment & Social API (requires API keys):
#   from api.v1 import sentiment
#   app.include_router(sentiment.router, prefix="/api/v1/sentiment", tags=["Sentiment"])


if __name__ == "__main__":
    uvicorn.run(
        "alphasignal_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
