"""
Demo API endpoint - Quick prototype to test services
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
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
async def analyze_ticker(ticker: str, days: int = 180):
    """
    Full analysis endpoint - returns market data, technical indicators,
    historical OHLCV + indicators for charting, and backtest equity curve.
    """
    try:
        market_service = MarketDataService()

        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')

        logger.info(f"Fetching {days}d data for {ticker}")
        df = market_service.fetch_prices(ticker, start_date, end_date)

        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")

        # Add returns
        df = market_service.calculate_returns(df)

        # Calculate technical indicators
        tech_indicators = TechnicalIndicators(use_cpp=False)
        df = tech_indicators.calculate_all(df)

        # Get latest values
        latest = df.iloc[-1]

        # ---- Helper to safely convert values ----
        def safe_float(val):
            if val is None or (isinstance(val, float) and np.isnan(val)):
                return None
            return float(val)

        def safe_int(val):
            if val is None or (isinstance(val, float) and np.isnan(val)):
                return 0
            return int(val)

        # ---- Historical data for charts (full window) ----
        dates_list = df['date'].astype(str).tolist()
        close_list = [safe_float(v) for v in df['close'].tolist()]
        open_list = [safe_float(v) for v in df.get('open', pd.Series([None]*len(df))).tolist()]
        high_list = [safe_float(v) for v in df.get('high', pd.Series([None]*len(df))).tolist()]
        low_list = [safe_float(v) for v in df.get('low', pd.Series([None]*len(df))).tolist()]
        volume_list = [safe_int(v) for v in df.get('volume', pd.Series([0]*len(df))).fillna(0).tolist()]
        rsi_list = [safe_float(v) for v in df['rsi_14'].tolist()]
        macd_list = [safe_float(v) for v in df['macd'].tolist()]
        macd_signal_list = [safe_float(v) for v in df['macd_signal'].tolist()]
        macd_hist_list = [safe_float(v) for v in df['macd_histogram'].tolist()]
        bb_upper_list = [safe_float(v) for v in df['bb_upper'].tolist()]
        bb_middle_list = [safe_float(v) for v in df['bb_middle'].tolist()]
        bb_lower_list = [safe_float(v) for v in df['bb_lower'].tolist()]

        # ---- Equity curve simulation (buy-and-hold vs simple MA cross) ----
        # Buy-and-hold normalized to 100
        closes = df['close'].ffill().bfill()
        bh_curve = (closes / closes.iloc[0] * 100).tolist()

        # Simple 20/50 MA crossover strategy simulation
        sma20 = closes.rolling(20).mean()
        sma50 = closes.rolling(50).mean()
        position = 0
        strategy_val = 100.0
        strategy_curve = []
        for i in range(len(closes)):
            if i == 0:
                strategy_curve.append(100.0)
                continue
            # Signal: go long when 20 > 50, flat otherwise
            if not np.isnan(sma20.iloc[i]) and not np.isnan(sma50.iloc[i]):
                signal = 1 if sma20.iloc[i] > sma50.iloc[i] else 0
            else:
                signal = 0
            # Daily return
            daily_ret = (closes.iloc[i] / closes.iloc[i-1]) - 1
            strategy_val *= (1 + signal * daily_ret)
            strategy_curve.append(round(strategy_val, 4))

        # ---- Volatility regime (rolling 20d annualized vol) ----
        log_ret = np.log(closes / closes.shift(1))
        rolling_vol = log_ret.rolling(20).std() * np.sqrt(252) * 100
        vol_list = [safe_float(v) for v in rolling_vol.tolist()]

        # ---- Returns series ----
        returns_1d_series = [safe_float(v) for v in df['returns_1d'].tolist()]

        # ---- Moving averages ----
        sma20_list = [safe_float(v) for v in sma20.tolist()]
        sma50_list = [safe_float(v) for v in sma50.tolist()]
        sma200 = closes.rolling(200).mean()
        sma200_list = [safe_float(v) for v in sma200.tolist()]

        # ---- Feature importance from trained model (if available) ----
        feature_importance = []
        try:
            from services.ml_engine.model_training import XGBoostPredictor
            model = XGBoostPredictor(model_path=os.path.join(os.path.dirname(__file__), '../../models/xgboost_model.pkl'))
            model._load_model()
            imp_df = model.get_feature_importance().head(15)
            feature_importance = [
                {"feature": row['feature'], "importance": round(float(row['importance']), 4)}
                for _, row in imp_df.iterrows()
            ]
        except Exception as e:
            logger.warning(f"Could not load feature importance: {e}")

        # ---- Build response ----
        response = {
            "ticker": ticker.upper(),
            "as_of_date": latest['date'].strftime('%Y-%m-%d') if hasattr(latest['date'], 'strftime') else str(latest['date']),
            "market_data": {
                "close": safe_float(latest['close']),
                "open": safe_float(latest.get('open', 0)),
                "high": safe_float(latest.get('high', 0)),
                "low": safe_float(latest.get('low', 0)),
                "volume": safe_int(latest.get('volume', 0)),
            },
            "technical_indicators": {
                "rsi_14": safe_float(latest['rsi_14']),
                "macd": safe_float(latest['macd']),
                "macd_signal": safe_float(latest['macd_signal']),
                "macd_histogram": safe_float(latest['macd_histogram']),
                "bb_upper": safe_float(latest['bb_upper']),
                "bb_middle": safe_float(latest['bb_middle']),
                "bb_lower": safe_float(latest['bb_lower']),
                "volatility_10d": safe_float(latest['volatility_10d']),
            },
            "returns": {
                "returns_1d": safe_float(latest['returns_1d']),
                "returns_5d": safe_float(latest['returns_5d']),
                "returns_20d": safe_float(latest['returns_20d']),
            },
            "historical_data": {
                "dates": dates_list,
                "close": close_list,
                "open": open_list,
                "high": high_list,
                "low": low_list,
                "volume": volume_list,
                "rsi": rsi_list,
                "macd": macd_list,
                "macd_signal": macd_signal_list,
                "macd_histogram": macd_hist_list,
                "bb_upper": bb_upper_list,
                "bb_middle": bb_middle_list,
                "bb_lower": bb_lower_list,
                "sma20": sma20_list,
                "sma50": sma50_list,
                "sma200": sma200_list,
                "volatility": vol_list,
                "returns_1d": returns_1d_series,
                "equity_bh": bh_curve,
                "equity_strategy": strategy_curve,
            },
            "feature_importance": feature_importance,
            "stats": {
                "data_points": len(df),
                "start_date": df.iloc[0]['date'].strftime('%Y-%m-%d') if hasattr(df.iloc[0]['date'], 'strftime') else str(df.iloc[0]['date']),
                "end_date": latest['date'].strftime('%Y-%m-%d') if hasattr(latest['date'], 'strftime') else str(latest['date']),
                "annualized_vol": safe_float(rolling_vol.iloc[-1]),
                "max_drawdown": safe_float(_max_drawdown(closes)),
                "sharpe_approx": safe_float(_sharpe(closes)),
            }
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def _max_drawdown(closes: pd.Series) -> float:
    """Calculate max drawdown as a percentage."""
    roll_max = closes.cummax()
    drawdown = (closes - roll_max) / roll_max
    return float(drawdown.min() * 100)


def _sharpe(closes: pd.Series, risk_free: float = 0.05) -> float:
    """Approximate annualized Sharpe ratio."""
    rets = closes.pct_change().dropna()
    if rets.std() == 0:
        return 0.0
    excess = rets.mean() * 252 - risk_free
    vol = rets.std() * np.sqrt(252)
    return float(excess / vol)
