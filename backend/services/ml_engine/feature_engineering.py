"""
Feature Engineering for ML Models
Create comprehensive feature set from market data, sentiment, and social signals
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

# Import technical indicators
try:
    from services.technical_indicators.cpp_wrapper import TechnicalIndicators
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
    from services.technical_indicators.cpp_wrapper import TechnicalIndicators

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Create ML features from price data, sentiment, and social signals
    """

    def __init__(self):
        self.indicators = TechnicalIndicators(use_cpp=False)  # Use Python fallback for training

    def create_features(
        self,
        price_df: pd.DataFrame,
        sentiment_df: Optional[pd.DataFrame] = None,
        social_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Create comprehensive feature set for ML model

        Features:
        - Technical indicators (20+ features)
        - Price patterns (10+ features)
        - Sentiment features (5+ features)
        - Social signal features (5+ features)
        - Time features (5+ features)
        """

        # Start with price data
        df = price_df.copy()

        # 1. Technical Indicators (via C++)
        logger.info("Calculating technical indicators...")
        df = self.indicators.calculate_all(df)

        # 2. Price Patterns
        logger.info("Creating price pattern features...")
        df['candle_size'] = (df['high'] - df['low']) / df['close']
        df['upper_shadow'] = (df['high'] - df[['open', 'close']].max(axis=1)) / df['close']
        df['lower_shadow'] = (df[['open', 'close']].min(axis=1) - df['low']) / df['close']
        df['body_size'] = abs(df['close'] - df['open']) / df['close']

        # 3. Price Action
        df['higher_high'] = (df['high'] > df['high'].shift(1)).astype(int)
        df['lower_low'] = (df['low'] < df['low'].shift(1)).astype(int)
        df['gap_up'] = ((df['open'] - df['close'].shift(1)) / df['close'].shift(1) > 0.02).astype(int)
        df['gap_down'] = ((df['open'] - df['close'].shift(1)) / df['close'].shift(1) < -0.02).astype(int)

        # 4. Advanced Momentum Features
        df['rsi_slope'] = df['rsi_14'].diff()
        df['rsi_oversold'] = (df['rsi_14'] < 30).astype(int)
        df['rsi_overbought'] = (df['rsi_14'] > 70).astype(int)
        df['rsi_divergence'] = ((df['close'] > df['close'].shift(5)) &
                                 (df['rsi_14'] < df['rsi_14'].shift(5))).astype(int)

        df['macd_cross'] = ((df['macd'] > df['macd_signal']) &
                           (df['macd'].shift(1) <= df['macd_signal'].shift(1))).astype(int)
        df['macd_histogram_slope'] = df['macd_histogram'].diff()
        df['macd_strength'] = abs(df['macd'] - df['macd_signal']) / df['close']

        # 5. Advanced Volatility Features
        df['volatility_regime'] = pd.cut(
            df['volatility_10d'],
            bins=[0, 0.01, 0.02, 0.05, np.inf],
            labels=['low', 'medium', 'high', 'extreme']
        )
        df = pd.get_dummies(df, columns=['volatility_regime'], prefix='vol')

        # Volatility expansion/contraction
        df['volatility_trend'] = df['volatility_10d'].diff()
        df['volatility_ratio'] = df['volatility_10d'] / df['volatility_10d'].rolling(20).mean()

        # Bollinger Band squeeze
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        df['bb_squeeze'] = (df['bb_width'] < df['bb_width'].rolling(20).mean() * 0.5).astype(int)

        # 6. Merge Sentiment Data
        if sentiment_df is not None:
            logger.info("Merging sentiment features...")
            sentiment_df = sentiment_df.copy()
            sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
            df['date'] = pd.to_datetime(df['date'])

            df = df.merge(
                sentiment_df[['date', 'sentiment_score', 'article_count']],
                on='date',
                how='left'
            )

            # Sentiment features
            df['sentiment_score'] = df['sentiment_score'].fillna(0)
            df['article_count'] = df['article_count'].fillna(0)
            df['sentiment_ma_5d'] = df['sentiment_score'].rolling(5).mean()
            df['sentiment_change'] = df['sentiment_score'].diff()
            df['sentiment_positive'] = (df['sentiment_score'] > 0.1).astype(int)
            df['sentiment_negative'] = (df['sentiment_score'] < -0.1).astype(int)

        # 7. Merge Social Signals
        if social_df is not None:
            logger.info("Merging social signal features...")
            social_df = social_df.copy()
            social_df['date'] = pd.to_datetime(social_df['date'])

            df = df.merge(
                social_df[['date', 'reddit_mentions', 'reddit_sentiment', 'reddit_score']],
                on='date',
                how='left'
            )

            # Social features
            df['reddit_mentions'] = df['reddit_mentions'].fillna(0)
            df['reddit_sentiment'] = df['reddit_sentiment'].fillna(0)
            df['reddit_score'] = df['reddit_score'].fillna(0)
            df['reddit_spike'] = (
                df['reddit_mentions'] > df['reddit_mentions'].rolling(7).mean() * 2
            ).astype(int)

        # 8. Advanced Price Action Features
        logger.info("Creating advanced price action features...")

        # Moving average crossovers
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['sma_200'] = df['close'].rolling(200).mean() if len(df) >= 200 else df['close'].rolling(len(df)//2).mean()

        df['price_above_sma20'] = (df['close'] > df['sma_20']).astype(int)
        df['price_above_sma50'] = (df['close'] > df['sma_50']).astype(int)
        df['sma20_above_sma50'] = (df['sma_20'] > df['sma_50']).astype(int)

        # Momentum indicators
        df['momentum_5'] = df['close'] / df['close'].shift(5) - 1
        df['momentum_10'] = df['close'] / df['close'].shift(10) - 1
        df['momentum_20'] = df['close'] / df['close'].shift(20) - 1

        # Rate of change
        df['roc_5'] = (df['close'] - df['close'].shift(5)) / df['close'].shift(5) * 100
        df['roc_10'] = (df['close'] - df['close'].shift(10)) / df['close'].shift(10) * 100

        # Volume momentum (if volume exists)
        if 'volume_ratio' in df.columns:
            df['volume_momentum'] = df['volume_ratio'].diff()
            df['volume_trend'] = (df['volume_ratio'] > 1).astype(int)

        # 9. Trend Following Features (important for multi-day predictions)
        logger.info("Creating trend following features...")

        # Price trend over different periods
        df['trend_5d'] = (df['close'] > df['close'].shift(5)).astype(int)
        df['trend_10d'] = (df['close'] > df['close'].shift(10)).astype(int)
        df['trend_20d'] = (df['close'] > df['close'].shift(20)).astype(int)

        # Consecutive up/down days
        df['price_change'] = df['close'].diff()
        df['consecutive_up'] = (df['price_change'] > 0).astype(int).groupby((df['price_change'] <= 0).cumsum()).cumsum()
        df['consecutive_down'] = (df['price_change'] < 0).astype(int).groupby((df['price_change'] >= 0).cumsum()).cumsum()

        # Trend strength
        df['trend_strength_5d'] = df['close'].rolling(5).apply(lambda x: 1 if all(x.diff().dropna() > 0) else (-1 if all(x.diff().dropna() < 0) else 0))
        df['trend_strength_10d'] = df['close'].rolling(10).apply(lambda x: 1 if all(x.diff().dropna() > 0) else (-1 if all(x.diff().dropna() < 0) else 0))

        # Distance from highs/lows
        df['dist_from_52w_high'] = (df['close'] - df['close'].rolling(252, min_periods=50).max()) / df['close']
        df['dist_from_52w_low'] = (df['close'] - df['close'].rolling(252, min_periods=50).min()) / df['close']

        # 10. Time Features
        logger.info("Creating time features...")
        df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
        df['month'] = pd.to_datetime(df['date']).dt.month
        df['quarter'] = pd.to_datetime(df['date']).dt.quarter
        df['is_month_start'] = pd.to_datetime(df['date']).dt.is_month_start.astype(int)
        df['is_month_end'] = pd.to_datetime(df['date']).dt.is_month_end.astype(int)

        # 11. Target Variable (5-day direction for better predictability)
        # 5-day horizon is more predictable than next-day
        df['target'] = (df['close'].shift(-5) > df['close']).astype(int)

        # Also create intermediate targets for feature engineering
        df['target_1d'] = (df['close'].shift(-1) > df['close']).astype(int)
        df['target_3d'] = (df['close'].shift(-3) > df['close']).astype(int)

        # 12. Drop rows with NaN and infinite values
        initial_len = len(df)
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.dropna()
        logger.info(f"Dropped {initial_len - len(df)} rows with NaN/Inf values")

        logger.info(f"✅ Created {len(df.columns)} features from {len(df)} samples")

        return df

    def get_feature_names(self, df: pd.DataFrame) -> List[str]:
        """Get list of feature columns (exclude target and metadata)"""
        exclude = ['date', 'ticker', 'target', 'target_1d', 'target_3d', 'open', 'high', 'low', 'close', 'volume']
        return [col for col in df.columns if col not in exclude]
