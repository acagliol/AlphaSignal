"""
Technical Indicators with C++ Acceleration
Automatic fallback to Python if C++ module not available
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple
import logging
import sys
import os

# Add cpp_indicators to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../cpp_indicators'))

logger = logging.getLogger(__name__)

# Try to import C++ module
try:
    import cpp_indicators as cpp
    CPP_AVAILABLE = True
    logger.info("✅ C++ indicators module loaded (high performance)")
except ImportError:
    CPP_AVAILABLE = False
    logger.warning("⚠️  C++ indicators not available, using Python fallback")


class TechnicalIndicators:
    """
    Technical indicator calculator with C++ acceleration
    Automatic fallback to Python if C++ not available
    """

    def __init__(self, use_cpp: bool = True):
        self.use_cpp = use_cpp and CPP_AVAILABLE
        self.method = "C++" if self.use_cpp else "Python"
        logger.info(f"TechnicalIndicators using: {self.method}")

    def calculate_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators
        Input: DataFrame with 'close' column
        Output: DataFrame with all indicator columns added
        """
        df = df.copy()
        prices = df['close'].values

        if self.use_cpp:
            # C++ accelerated (10-20x faster)
            df['rsi_14'] = self._calculate_rsi_cpp(prices)
            macd_result = self._calculate_macd_cpp(prices)
            df['macd'] = macd_result.macd
            df['macd_signal'] = macd_result.signal
            df['macd_histogram'] = macd_result.histogram

            bb_result = self._calculate_bb_cpp(prices)
            df['bb_upper'] = bb_result.upper
            df['bb_middle'] = bb_result.middle
            df['bb_lower'] = bb_result.lower
        else:
            # Python fallback
            df['rsi_14'] = self._calculate_rsi_python(df['close'])
            macd = self._calculate_macd_python(df['close'])
            df['macd'] = macd['macd']
            df['macd_signal'] = macd['signal']
            df['macd_histogram'] = macd['histogram']

            bb = self._calculate_bb_python(df['close'])
            df['bb_upper'] = bb['upper']
            df['bb_middle'] = bb['middle']
            df['bb_lower'] = bb['lower']

        # Volume and volatility (always Python - simple operations)
        if 'volume' in df.columns:
            df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        df['volatility_10d'] = df['close'].pct_change().rolling(10).std()

        if 'high' in df.columns and 'low' in df.columns:
            df['high_low_ratio'] = df['high'] / df['low']

        # Returns
        df['returns_1d'] = df['close'].pct_change(1)
        df['returns_5d'] = df['close'].pct_change(5)
        df['returns_20d'] = df['close'].pct_change(20)

        return df

    # C++ methods
    def _calculate_rsi_cpp(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """RSI using C++"""
        return cpp.calculate_rsi(prices, period)

    def _calculate_macd_cpp(self, prices: np.ndarray):
        """MACD using C++"""
        return cpp.calculate_macd(prices, 12, 26, 9)

    def _calculate_bb_cpp(self, prices: np.ndarray):
        """Bollinger Bands using C++"""
        return cpp.calculate_bollinger_bands(prices, 20, 2.0)

    # Python fallback methods
    def _calculate_rsi_python(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI fallback in Python"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd_python(self, prices: pd.Series) -> Dict[str, pd.Series]:
        """MACD fallback in Python"""
        ema_fast = prices.ewm(span=12, adjust=False).mean()
        ema_slow = prices.ewm(span=26, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal

        return {
            'macd': macd,
            'signal': signal,
            'histogram': histogram
        }

    def _calculate_bb_python(self, prices: pd.Series, period: int = 20, num_std: float = 2.0) -> Dict[str, pd.Series]:
        """Bollinger Bands fallback in Python"""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)

        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }


# Performance benchmarking
def benchmark_indicators(iterations: int = 100):
    """Benchmark C++ vs Python performance"""
    import time

    # Generate sample data
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(1000) * 2)

    # Test C++
    if CPP_AVAILABLE:
        start = time.time()
        for _ in range(iterations):
            cpp.calculate_rsi(prices, 14)
        cpp_time = time.time() - start
    else:
        cpp_time = None

    # Test Python
    prices_series = pd.Series(prices)
    calc = TechnicalIndicators(use_cpp=False)
    start = time.time()
    for _ in range(iterations):
        calc._calculate_rsi_python(prices_series, 14)
    python_time = time.time() - start

    print("=" * 50)
    print(f"Benchmark Results ({iterations} iterations)")
    print("=" * 50)
    if cpp_time:
        print(f"C++ Time:     {cpp_time:.4f}s ({cpp_time/iterations*1000:.2f}ms per calc)")
        print(f"Python Time:  {python_time:.4f}s ({python_time/iterations*1000:.2f}ms per calc)")
        print(f"Speedup:      {python_time/cpp_time:.1f}x faster with C++")
    else:
        print(f"Python Time:  {python_time:.4f}s ({python_time/iterations*1000:.2f}ms per calc)")
        print("C++ module not available for comparison")
    print("=" * 50)
