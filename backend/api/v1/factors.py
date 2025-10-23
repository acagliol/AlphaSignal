"""
Factor Analysis API Routes
Fama-French 3-factor model analysis
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import logging

from database import get_db
from models import FactorExposures
from schemas import factor_schema
from services.factor_analysis.fama_french import FamaFrenchAnalysis
from services.data_ingestion.market_data import MarketDataService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/factors/{ticker}", response_model=factor_schema.FactorExposureResponse)
async def get_factor_exposure(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Get latest Fama-French factor analysis for ticker"""

    factor_data = db.query(FactorExposures)\
        .filter(FactorExposures.ticker == ticker.upper())\
        .order_by(FactorExposures.created_at.desc())\
        .first()

    if not factor_data:
        raise HTTPException(status_code=404, detail=f"No factor analysis found for {ticker}")

    return factor_data


@router.post("/factors/{ticker}/analyze")
async def analyze_factors(
    ticker: str,
    days: int = Query(default=252, ge=60, le=1260),  # 1-5 years
    db: Session = Depends(get_db)
):
    """
    Run Fama-French 3-factor analysis for ticker
    Decomposes returns into systematic risk factors
    """

    try:
        # Fetch price data
        market_service = MarketDataService()
        price_df = market_service.fetch_prices(ticker, start_date=None, end_date=None)

        if price_df.empty:
            raise HTTPException(status_code=404, detail=f"No price data found for {ticker}")

        # Take last N days
        price_df = price_df.tail(days)

        # Calculate returns
        price_df['date'] = pd.to_datetime(price_df['date'])
        returns = price_df.set_index('date')['close'].pct_change().dropna()

        if len(returns) < 30:
            raise HTTPException(status_code=400, detail="Insufficient data for factor analysis (need at least 30 days)")

        # Run FF3 analysis
        ff_analysis = FamaFrenchAnalysis()
        results = ff_analysis.run_regression(returns, return_type='daily')

        # Save to database
        factor_entry = FactorExposures(
            ticker=ticker.upper(),
            portfolio_name=ticker.upper(),
            start_date=price_df['date'].min(),
            end_date=price_df['date'].max(),
            alpha=results['alpha'],
            alpha_tstat=results['alpha_tstat'],
            alpha_pvalue=results['alpha_pvalue'],
            beta_market=results['beta_market'],
            beta_size=results['beta_size'],
            beta_value=results['beta_value'],
            r_squared=results['r_squared'],
            interpretation=results['interpretation']
        )

        db.add(factor_entry)
        db.commit()
        db.refresh(factor_entry)

        logger.info(f"Factor analysis complete for {ticker}: Alpha={results['alpha_annual_pct']:.2f}%")

        return {
            "ticker": ticker,
            "analysis_period_days": days,
            "alpha_annual_pct": round(results['alpha_annual_pct'], 2),
            "alpha_significant": results['alpha_significant'],
            "beta_market": round(results['beta_market'], 4),
            "beta_size": round(results['beta_size'], 4),
            "beta_value": round(results['beta_value'], 4),
            "r_squared": round(results['r_squared'], 4),
            "interpretation": results['interpretation']
        }

    except Exception as e:
        logger.error(f"Error analyzing factors for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/factors/{ticker}/rolling")
async def get_rolling_factors(
    ticker: str,
    window: int = Query(default=120, ge=60, le=252),
    db: Session = Depends(get_db)
):
    """
    Get rolling factor exposures over time
    Shows how factor loadings change
    """

    try:
        # Fetch price data (need extra for rolling window)
        market_service = MarketDataService()
        price_df = market_service.fetch_prices(ticker, start_date=None, end_date=None)

        if price_df.empty:
            raise HTTPException(status_code=404, detail=f"No price data found for {ticker}")

        # Calculate returns
        price_df['date'] = pd.to_datetime(price_df['date'])
        returns = price_df.set_index('date')['close'].pct_change().dropna()

        if len(returns) < window + 30:
            raise HTTPException(status_code=400, detail=f"Insufficient data for rolling analysis (need at least {window + 30} days)")

        # Calculate rolling exposures
        ff_analysis = FamaFrenchAnalysis()
        rolling_df = ff_analysis.rolling_factor_exposure(returns, window=window)

        if rolling_df.empty:
            raise HTTPException(status_code=500, detail="Failed to calculate rolling exposures")

        # Convert dates to strings for JSON serialization
        rolling_df['date'] = rolling_df['date'].astype(str)

        return {
            "ticker": ticker,
            "window_days": window,
            "n_periods": len(rolling_df),
            "data": rolling_df.to_dict('records')
        }

    except Exception as e:
        logger.error(f"Error calculating rolling factors for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
