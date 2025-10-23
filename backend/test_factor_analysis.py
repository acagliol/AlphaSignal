#!/usr/bin/env python
"""
Test Fama-French Factor Analysis
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from services.data_ingestion.market_data import MarketDataService
from services.factor_analysis.fama_french import FamaFrenchAnalysis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_factor_analysis(ticker: str = 'AAPL', days: int = 365):
    """
    Test Fama-French factor analysis on a stock
    """

    logger.info("=" * 80)
    logger.info(f"🔬 Fama-French Factor Analysis - {ticker}")
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

    # Calculate returns
    price_df = market_service.calculate_returns(price_df)

    # ===== 2. Run Fama-French Regression =====
    logger.info("\n🔬 Step 2: Running Fama-French 3-Factor regression...")

    ff = FamaFrenchAnalysis()

    # Prepare returns series with date index
    returns = price_df.set_index('date')['returns_1d'].dropna()

    results = ff.run_regression(returns, return_type='daily')

    # ===== 3. Display Results =====
    logger.info("\n" + "=" * 80)
    logger.info("📊 FAMA-FRENCH 3-FACTOR ANALYSIS RESULTS")
    logger.info("=" * 80)

    logger.info(f"\n🎯 ALPHA (Risk-Adjusted Excess Return):")
    logger.info(f"  Daily Alpha:      {results['alpha']:.6f}")
    logger.info(f"  Annual Alpha:     {results['alpha_annual_pct']:.2f}%")
    logger.info(f"  T-Statistic:      {results['alpha_tstat']:.4f}")
    logger.info(f"  P-Value:          {results['alpha_pvalue']:.4f}")
    logger.info(f"  Significant:      {'✅ Yes' if results['alpha_significant'] else '❌ No'}")

    logger.info(f"\n📈 FACTOR EXPOSURES (Betas):")
    logger.info(f"  Market Beta:      {results['beta_market']:.4f} (t={results['beta_market_tstat']:.2f}) {'✅' if results['beta_market_significant'] else '❌'}")
    logger.info(f"  Size Beta (SMB):  {results['beta_size']:.4f} (t={results['beta_size_tstat']:.2f}) {'✅' if results['beta_size_significant'] else '❌'}")
    logger.info(f"  Value Beta (HML): {results['beta_value']:.4f} (t={results['beta_value_tstat']:.2f}) {'✅' if results['beta_value_significant'] else '❌'}")

    logger.info(f"\n📉 MODEL FIT:")
    logger.info(f"  R-Squared:        {results['r_squared']:.4f} ({results['r_squared']*100:.1f}%)")
    logger.info(f"  Adjusted R²:      {results['adjusted_r_squared']:.4f}")
    logger.info(f"  Observations:     {results['n_observations']}")

    logger.info(f"\n💡 INTERPRETATION:")
    logger.info(f"  {results['interpretation']}")

    logger.info("\n" + "=" * 80)

    # ===== 4. Rolling Factor Exposure Analysis =====
    logger.info("\n📊 Step 3: Calculating rolling factor exposures...")

    rolling_results = ff.rolling_factor_exposure(returns, window=120)  # 120-day window

    if len(rolling_results) > 0:
        logger.info(f"✅ Calculated {len(rolling_results)} rolling windows")

        # Display recent factor exposures
        logger.info("\n📈 Recent Rolling Factor Exposures (last 5 periods):")
        for _, row in rolling_results.tail(5).iterrows():
            logger.info(
                f"  {row['date']}: "
                f"α={row['alpha_annual']*100:>6.2f}%, "
                f"β_mkt={row['beta_market']:>5.2f}, "
                f"β_smb={row['beta_size']:>5.2f}, "
                f"β_hml={row['beta_value']:>5.2f}, "
                f"R²={row['r_squared']:.3f}"
            )

        # Summary statistics
        logger.info("\n📊 Rolling Factor Exposure Summary:")
        logger.info(f"  Alpha (mean):     {rolling_results['alpha_annual'].mean()*100:.2f}%")
        logger.info(f"  Alpha (std):      {rolling_results['alpha_annual'].std()*100:.2f}%")
        logger.info(f"  Beta Market (mean): {rolling_results['beta_market'].mean():.2f}")
        logger.info(f"  Beta Size (mean):   {rolling_results['beta_size'].mean():.2f}")
        logger.info(f"  Beta Value (mean):  {rolling_results['beta_value'].mean():.2f}")
        logger.info(f"  R² (mean):        {rolling_results['r_squared'].mean():.3f}")

    logger.info("\n✅ Factor analysis complete!")

    return results, rolling_results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Test Fama-French factor analysis')
    parser.add_argument('--ticker', type=str, default='AAPL', help='Stock ticker symbol')
    parser.add_argument('--days', type=int, default=365, help='Historical days to fetch')

    args = parser.parse_args()

    results, rolling = test_factor_analysis(ticker=args.ticker, days=args.days)
