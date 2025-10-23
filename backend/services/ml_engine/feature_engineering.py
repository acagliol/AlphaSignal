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

        # 4. Momentum Features
        df['rsi_slope'] = df['rsi_14'].diff()
        df['macd_cross'] = ((df['macd'] > df['macd_signal']) &
                           (df['macd'].shift(1) <= df['macd_signal'].shift(1))).astype(int)

        # 5. Volatility Regimes
        df['volatility_regime'] = pd.cut(
            df['volatility_10d'],
            bins=[0, 0.01, 0.02, 0.05, np.inf],
            labels=['low', 'medium', 'high', 'extreme']
        )
        df = pd.get_dummies(df, columns=['volatility_regime'], prefix='vol')

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

        # 8. Time Features
        logger.info("Creating time features...")
        df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
        df['month'] = pd.to_datetime(df['date']).dt.month
        df['quarter'] = pd.to_datetime(df['date']).dt.quarter

        # 9. Target Variable (next-day direction)
        df['target'] = (df['close'].shift(-1) > df['close']).astype(int)

        # 10. Drop rows with NaN
        initial_len = len(df)
        df = df.dropna()
        logger.info(f"Dropped {initial_len - len(df)} rows with NaN values")

        logger.info(f"✅ Created {len(df.columns)} features from {len(df)} samples")

        return df

    def get_feature_names(self, df: pd.DataFrame) -> List[str]:
        """Get list of feature columns (exclude target and metadata)"""
        exclude = ['date', 'ticker', 'target', 'open', 'high', 'low', 'close', 'volume']
        return [col for col in df.columns if col not in exclude]
