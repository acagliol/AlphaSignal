"""
Market Data Integration Service
Fetch historical market data from Yahoo Finance
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class MarketDataService:
    """Fetch historical market data"""

    def fetch_prices(
        self,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data from Yahoo Finance
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        try:
            df = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False
            )

            if df.empty:
                logger.warning(f"No data found for {ticker}")
                return pd.DataFrame()

            # Reset index (date becomes column)
            df = df.reset_index()
            # Handle MultiIndex columns from yfinance
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df.columns = [str(col).lower() for col in df.columns]

            # Add ticker column
            df['ticker'] = ticker

            logger.info(f"Fetched {len(df)} rows for {ticker}")
            return df

        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()

    def calculate_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add return columns"""
        df = df.copy()
        df['returns_1d'] = df['close'].pct_change(1)
        df['returns_5d'] = df['close'].pct_change(5)
        df['returns_20d'] = df['close'].pct_change(20)
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        return df
