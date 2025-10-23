"""
Demo API endpoint - Quick prototype to test services
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import pandas as pd
import logging

# Import our services
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from services.data_ingestion.market_data import MarketDataService
from services.technical_indicators.cpp_wrapper import TechnicalIndicators

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/analyze/{ticker}")
async def analyze_ticker(ticker: str, days: int = 90):
    """
    Quick demo endpoint - analyze a ticker with all our services
    Returns market data + technical indicators
    """
    try:
        # Fetch market data
        market_service = MarketDataService()

        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')

        logger.info(f"Fetching data for {ticker}")
        df = market_service.fetch_prices(ticker, start_date, end_date)

        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")

        # Add returns
        df = market_service.calculate_returns(df)

        # Calculate technical indicators
        tech_indicators = TechnicalIndicators(use_cpp=False)  # Use Python fallback for now
        df = tech_indicators.calculate_all(df)

        # Get latest values
        latest = df.iloc[-1]

        # Prepare response
        response = {
            "ticker": ticker.upper(),
            "as_of_date": latest['date'].strftime('%Y-%m-%d') if hasattr(latest['date'], 'strftime') else str(latest['date']),
            "market_data": {
                "close": float(latest['close']),
                "open": float(latest.get('open', 0)),
                "high": float(latest.get('high', 0)),
                "low": float(latest.get('low', 0)),
                "volume": int(latest.get('volume', 0)) if pd.notna(latest.get('volume')) else 0,
            },
            "technical_indicators": {
                "rsi_14": float(latest['rsi_14']) if pd.notna(latest['rsi_14']) else None,
                "macd": float(latest['macd']) if pd.notna(latest['macd']) else None,
                "macd_signal": float(latest['macd_signal']) if pd.notna(latest['macd_signal']) else None,
                "macd_histogram": float(latest['macd_histogram']) if pd.notna(latest['macd_histogram']) else None,
                "bb_upper": float(latest['bb_upper']) if pd.notna(latest['bb_upper']) else None,
                "bb_middle": float(latest['bb_middle']) if pd.notna(latest['bb_middle']) else None,
                "bb_lower": float(latest['bb_lower']) if pd.notna(latest['bb_lower']) else None,
                "volatility_10d": float(latest['volatility_10d']) if pd.notna(latest['volatility_10d']) else None,
            },
            "returns": {
                "returns_1d": float(latest['returns_1d']) if pd.notna(latest['returns_1d']) else None,
                "returns_5d": float(latest['returns_5d']) if pd.notna(latest['returns_5d']) else None,
                "returns_20d": float(latest['returns_20d']) if pd.notna(latest['returns_20d']) else None,
            },
            "historical_data": {
                "dates": df['date'].astype(str).tolist()[-30:],  # Last 30 days
                "close": df['close'].tolist()[-30:],
                "rsi": df['rsi_14'].fillna(0).tolist()[-30:],
                "volume": df.get('volume', pd.Series([0]*len(df))).fillna(0).tolist()[-30:],
            },
            "stats": {
                "data_points": len(df),
                "start_date": df.iloc[0]['date'].strftime('%Y-%m-%d') if hasattr(df.iloc[0]['date'], 'strftime') else str(df.iloc[0]['date']),
                "end_date": latest['date'].strftime('%Y-%m-%d') if hasattr(latest['date'], 'strftime') else str(latest['date']),
            }
        }

        return response

    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
