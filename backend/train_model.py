#!/usr/bin/env python
"""
Train AlphaSignal ML Model
Feature engineering -> XGBoost training -> Backtesting
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
from services.ml_engine.backtester import MLBacktester

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def train_alpha_model(ticker: str = 'AAPL', days: int = 1095):
    """
    Complete ML pipeline: Data -> Features -> Training -> Backtesting
    """

    logger.info("=" * 80)
    logger.info(f"🚀 AlphaSignal ML Pipeline - Training on {ticker}")
    logger.info("=" * 80)

    # ===== 1. Fetch Market Data =====
    logger.info("\n📊 Step 1: Fetching market data...")
    market_service = MarketDataService()

    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    price_df = market_service.fetch_prices(ticker, start_date, end_date)

    if price_df.empty:
        logger.error(f"❌ No data found for {ticker}")
        return

    logger.info(f"✅ Fetched {len(price_df)} days of price data")

    # Add returns for later analysis
    price_df = market_service.calculate_returns(price_df)

    # ===== 2. Feature Engineering =====
    logger.info("\n🔧 Step 2: Creating features...")
    feature_engineer = FeatureEngineer()

    # Note: For demo, we're not using sentiment/social data
    # In production, you would merge real sentiment and social signal data here
    features_df = feature_engineer.create_features(
        price_df,
        sentiment_df=None,  # TODO: Add real sentiment data
        social_df=None      # TODO: Add real social data
    )

    logger.info(f"✅ Created feature set with shape: {features_df.shape}")

    # Get feature names
    feature_cols = feature_engineer.get_feature_names(features_df)
    logger.info(f"Features ({len(feature_cols)}): {', '.join(feature_cols[:10])}...")

    # ===== 3. Prepare Training Data =====
    logger.info("\n📋 Step 3: Preparing training data...")

    X = features_df[feature_cols]
    y = features_df['target']

    logger.info(f"X shape: {X.shape}")
    logger.info(f"y distribution: {y.value_counts().to_dict()}")
    logger.info(f"Class balance: UP={y.mean()*100:.1f}%, DOWN={(1-y.mean())*100:.1f}%")

    # ===== 4. Train XGBoost Model =====
    logger.info("\n🤖 Step 4: Training XGBoost model...")

    predictor = XGBoostPredictor(model_path='models/xgboost_model.pkl')

    cv_results = predictor.train(X, y, n_splits=5)

    logger.info("\n📊 Cross-Validation Results:")
    logger.info(f"  Accuracy: {cv_results['cv_accuracy_mean']:.4f} ± {cv_results['cv_accuracy_std']:.4f}")
    logger.info(f"  Precision: {cv_results['cv_precision_mean']:.4f}")
    logger.info(f"  Recall: {cv_results['cv_recall_mean']:.4f}")
    logger.info(f"  AUC: {cv_results['cv_auc_mean']:.4f} ± {cv_results['cv_auc_std']:.4f}")

    # ===== 5. Feature Importance =====
    logger.info("\n📈 Step 5: Analyzing feature importance...")

    importance_df = predictor.get_feature_importance()

    logger.info("Top 15 Most Important Features:")
    for idx, row in importance_df.head(15).iterrows():
        logger.info(f"  {row['feature']:30s}: {row['importance']:.4f}")

    # ===== 6. Generate Predictions for Backtesting =====
    logger.info("\n🔮 Step 6: Generating predictions for backtest...")

    predictions = []
    for i in range(len(features_df)):
        X_single = features_df[feature_cols].iloc[[i]]
        pred = predictor.predict(X_single)
        predictions.append({
            'date': features_df.iloc[i]['date'],
            'prediction': pred['prediction'],
            'confidence': pred['confidence'],
            'probability_up': pred['probability_up'],
            'probability_down': pred['probability_down']
        })

    predictions_df = pd.DataFrame(predictions)
    logger.info(f"✅ Generated {len(predictions_df)} predictions")

    # ===== 7. Backtesting =====
    logger.info("\n💰 Step 7: Running backtest...")

    backtester = MLBacktester(initial_capital=100000)

    backtest_results = backtester.run_backtest(
        predictions_df=predictions_df,
        price_df=features_df[['date', 'close']],
        position_size=0.1  # 10% position size
    )

    logger.info("\n" + "=" * 80)
    logger.info("📊 BACKTEST RESULTS")
    logger.info("=" * 80)
    logger.info(f"Initial Capital:  ${backtest_results['initial_capital']:>15,.2f}")
    logger.info(f"Final Value:      ${backtest_results['final_value']:>15,.2f}")
    logger.info(f"Total Return:     {backtest_results['total_return_pct']:>15.2f}%")
    logger.info(f"Total Trades:     {backtest_results['total_trades']:>15}")
    logger.info(f"Winning Trades:   {backtest_results['winning_trades']:>15}")
    logger.info(f"Losing Trades:    {backtest_results['losing_trades']:>15}")
    logger.info(f"Win Rate:         {backtest_results['win_rate']:>15.1f}%")
    logger.info(f"Avg Win:          ${backtest_results['avg_win']:>15.2f}")
    logger.info(f"Avg Loss:         ${backtest_results['avg_loss']:>15.2f}")
    logger.info(f"Max Win:          ${backtest_results['max_win']:>15.2f}")
    logger.info(f"Max Loss:         ${backtest_results['max_loss']:>15.2f}")
    logger.info("=" * 80)

    # ===== 8. Summary =====
    logger.info("\n✅ Training pipeline complete!")
    logger.info(f"Model saved to: models/xgboost_model.pkl")
    logger.info(f"Features used: {len(feature_cols)}")
    logger.info(f"Training samples: {len(X)}")

    return {
        'cv_results': cv_results,
        'backtest_results': backtest_results,
        'feature_importance': importance_df,
        'predictions': predictions_df
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Train AlphaSignal ML model')
    parser.add_argument('--ticker', type=str, default='AAPL', help='Stock ticker symbol')
    parser.add_argument('--days', type=int, default=1095, help='Historical days to fetch (default: 3 years)')

    args = parser.parse_args()

    results = train_alpha_model(ticker=args.ticker, days=args.days)
