"""
Yahoo Finance API service using yfinance library
"""

import yfinance as yf
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)

class YFinanceService:
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def get_daily_adjusted(self, symbol: str, period: str = "max") -> Dict[str, Any]:
        """Get daily adjusted time series data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, auto_adjust=False)

            if hist.empty:
                raise ValueError(f"No data found for {symbol}")

            # Convert to dictionary format similar to Alpha Vantage
            time_series = {}
            for idx, row in hist.iterrows():
                date_str = idx.strftime("%Y-%m-%d")
                time_series[date_str] = {
                    "1. open": str(row['Open']),
                    "2. high": str(row['High']),
                    "3. low": str(row['Low']),
                    "4. close": str(row['Close']),
                    "5. adjusted close": str(row['Close']),  # yfinance Close is already adjusted
                    "6. volume": str(int(row['Volume'])),
                    "7. dividend amount": str(row.get('Dividends', 0.0))
                }

            return time_series

        except Exception as e:
            logger.error(f"Failed to get daily adjusted data for {symbol}: {e}")
            raise

    async def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """Get company overview information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or 'symbol' not in info:
                raise ValueError(f"No company data found for {symbol}")

            return {
                "Symbol": info.get('symbol', symbol),
                "Name": info.get('longName', info.get('shortName', symbol)),
                "Sector": info.get('sector', 'Unknown'),
                "Industry": info.get('industry', 'Unknown'),
                "Currency": info.get('currency', 'USD')
            }

        except Exception as e:
            logger.error(f"Failed to get company overview for {symbol}: {e}")
            raise

    async def get_dividend_data(self, symbol: str) -> Dict[str, Any]:
        """Get dividend data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            dividends = ticker.dividends

            if dividends.empty:
                logger.warning(f"No dividend data found for {symbol}")
                return {}

            # Convert to monthly format similar to Alpha Vantage
            monthly_data = {}
            for idx, div_amount in dividends.items():
                date_str = idx.strftime("%Y-%m-%d")

                # Get price data for that date
                hist = ticker.history(start=idx - timedelta(days=5), end=idx + timedelta(days=1))
                close_price = hist['Close'].iloc[-1] if not hist.empty else 0

                monthly_data[date_str] = {
                    "1. open": str(close_price),
                    "2. high": str(close_price),
                    "3. low": str(close_price),
                    "4. close": str(close_price),
                    "5. adjusted close": str(close_price),
                    "6. volume": "0",
                    "7. dividend amount": str(div_amount)
                }

            return monthly_data

        except Exception as e:
            logger.error(f"Failed to get dividend data for {symbol}: {e}")
            raise

    def parse_daily_data(self, time_series: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse daily time series data into structured format"""
        parsed_data = []

        for date_str, values in time_series.items():
            try:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()

                parsed_data.append({
                    "date": parsed_date,
                    "adj_close": float(values.get("5. adjusted close", 0)),
                    "dividend": float(values.get("7. dividend amount", 0)),
                    "volume": int(float(values.get("6. volume", 0)))
                })
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse data for date {date_str}: {e}")
                continue

        # Sort by date
        parsed_data.sort(key=lambda x: x["date"])
        return parsed_data

    def parse_monthly_data(self, time_series: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse monthly time series data for dividend information"""
        return self.parse_daily_data(time_series)  # Same format

    async def get_historical_price(self, symbol: str, target_date: date) -> Optional[float]:
        """Get historical price for a specific date, handling weekends/holidays"""
        try:
            ticker = yf.Ticker(symbol)

            # Get data around the target date (5 days before and after)
            start_date = target_date - timedelta(days=5)
            end_date = target_date + timedelta(days=5)

            hist = ticker.history(start=start_date, end=end_date, auto_adjust=False)

            if hist.empty:
                raise ValueError(f"No data available for {symbol} around {target_date}")

            # Try to find exact date
            target_str = target_date.strftime("%Y-%m-%d")
            for idx in hist.index:
                if idx.strftime("%Y-%m-%d") == target_str:
                    return float(hist.loc[idx, 'Close'])

            # Find closest date
            closest_idx = min(hist.index, key=lambda x: abs((x.date() - target_date).days))
            logger.warning(f"No exact price for {symbol} on {target_date}, using {closest_idx.date()}")
            return float(hist.loc[closest_idx, 'Close'])

        except Exception as e:
            logger.error(f"Failed to get historical price for {symbol} on {target_date}: {e}")
            return None

    async def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get the latest available price for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")

            if hist.empty:
                raise ValueError(f"No recent data for {symbol}")

            return float(hist['Close'].iloc[-1])

        except Exception as e:
            logger.error(f"Failed to get latest price for {symbol}: {e}")
            return None

    async def get_dividend_history(self, symbol: str, start_date: date) -> List[Dict[str, Any]]:
        """Get dividend history since start_date"""
        try:
            ticker = yf.Ticker(symbol)
            dividends = ticker.dividends

            if dividends.empty:
                return []

            # Filter dividends since start_date
            dividend_history = []
            for idx, div_amount in dividends.items():
                div_date = idx.date()
                if div_date >= start_date and div_amount > 0:
                    dividend_history.append({
                        "date": div_date,
                        "dividend": float(div_amount),
                        "adj_close": 0  # Not used for dividends
                    })

            return dividend_history

        except Exception as e:
            logger.error(f"Failed to get dividend history for {symbol} since {start_date}: {e}")
            return []

    async def validate_ticker(self, symbol: str) -> bool:
        """Validate if a ticker symbol exists and is valid"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return 'symbol' in info or 'regularMarketPrice' in info
        except Exception as e:
            logger.warning(f"Ticker validation failed for {symbol}: {e}")
            return False
