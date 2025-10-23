#!/usr/bin/env python
"""
Train AlphaSignal ML Model on Multiple Stocks
Train on diverse stocks to learn general patterns, not just AAPL-specific
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from datetime import datetime, timedelta
import logging

from services.data_ingestion.market_data import MarketDataService
from services.ml_engine.feature_engineering import FeatureEngineer
from services.ml_engine.model_training import XGBoostPredictor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Train on diverse stocks to learn general patterns
TRAINING_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'AMD']

def train_multi_stock_model(days: int = 730):  # 2 years per stock
    """
    Train model on multiple stocks to learn general patterns
    """

    logger.info("=" * 80)
    logger.info(f"🚀 AlphaSignal Multi-Stock ML Training")
    logger.info(f"Stocks: {', '.join(TRAINING_STOCKS)}")
    logger.info("=" * 80)

    all_features = []
    market_service = MarketDataService()
    feature_engineer = FeatureEngineer()

    # Fetch and engineer features for each stock
    for ticker in TRAINING_STOCKS:
        logger.info(f"\n📊 Processing {ticker}...")

        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')

        price_df = market_service.fetch_prices(ticker, start_date, end_date)

        if price_df.empty:
            logger.warning(f"❌ No data for {ticker}, skipping")
            continue

        # Calculate returns
        price_df = market_service.calculate_returns(price_df)

        # Engineer features
        features_df = feature_engineer.create_features(
            price_df,
            sentiment_df=None,
            social_df=None
        )

        if features_df.empty:
            logger.warning(f"❌ No features created for {ticker}, skipping")
            continue

        logger.info(f"✅ {ticker}: {len(features_df)} samples")
        all_features.append(features_df)

    # Combine all stocks
    logger.info(f"\n🔄 Combining data from {len(all_features)} stocks...")
    combined_df = pd.concat(all_features, ignore_index=True)
    logger.info(f"✅ Combined dataset: {len(combined_df)} samples from {len(TRAINING_STOCKS)} stocks")

    # Get feature names
    feature_cols = feature_engineer.get_feature_names(combined_df)
    logger.info(f"Features: {len(feature_cols)}")

    # Prepare training data
    X = combined_df[feature_cols]
    y = combined_df['target']

    logger.info(f"\n📋 Training Data:")
    logger.info(f"  X shape: {X.shape}")
    logger.info(f"  y distribution: {y.value_counts().to_dict()}")
    logger.info(f"  Class balance: UP={y.mean()*100:.1f}%, DOWN={(1-y.mean())*100:.1f}%")

    # Train model
    logger.info(f"\n🤖 Training XGBoost on multi-stock data...")
    predictor = XGBoostPredictor(model_path='models/xgboost_model.pkl')

    cv_results = predictor.train(X, y, n_splits=5)

    logger.info("\n📊 Cross-Validation Results:")
    logger.info(f"  Accuracy: {cv_results['cv_accuracy_mean']:.4f} ± {cv_results['cv_accuracy_std']:.4f}")
    logger.info(f"  Precision: {cv_results['cv_precision_mean']:.4f}")
    logger.info(f"  Recall: {cv_results['cv_recall_mean']:.4f}")
    logger.info(f"  AUC: {cv_results['cv_auc_mean']:.4f} ± {cv_results['cv_auc_std']:.4f}")

    # Feature importance
    logger.info("\n📈 Top 15 Most Important Features:")
    importance_df = predictor.get_feature_importance()
    for idx, row in importance_df.head(15).iterrows():
        logger.info(f"  {row['feature']:30s}: {row['importance']:.4f}")

    logger.info("\n✅ Multi-stock training complete!")
    logger.info(f"Model saved to: models/xgboost_model.pkl")
    logger.info(f"Training samples: {len(X)}")

    return cv_results


if __name__ == "__main__":
    results = train_multi_stock_model(days=730)
