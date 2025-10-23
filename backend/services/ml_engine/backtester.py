"""
ML Backtesting Framework
Test ML predictions on historical data with realistic trading simulation
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class MLBacktester:
    """
    Backtest ML prediction model on historical data
    """

    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.trades = []

    def run_backtest(
        self,
        predictions_df: pd.DataFrame,
        price_df: pd.DataFrame,
        position_size: float = 0.1  # 10% of capital per trade
    ) -> Dict[str, any]:
        """
        Run backtest using model predictions

        predictions_df must have: date, prediction, confidence
        price_df must have: date, close
        """

        logger.info(f"Starting backtest with ${self.initial_capital:,.0f} initial capital")

        # Merge predictions with prices
        df = predictions_df.merge(price_df[['date', 'close']], on='date', how='inner')
        df = df.sort_values('date').reset_index(drop=True)

        logger.info(f"Backtesting {len(df)} trading days")

        # Initialize
        capital = self.initial_capital
        position = 0  # Shares held
        entry_price = 0
        self.trades = []

        for i in range(len(df)):
            row = df.iloc[i]
            current_price = row['close']

            # Only trade if confidence > 60%
            if row['confidence'] < 0.6:
                continue

            # BUY signal
            if row['prediction'] == 'UP' and position == 0:
                shares_to_buy = (capital * position_size) / current_price
                position = shares_to_buy
                entry_price = current_price
                capital -= (shares_to_buy * current_price)

                self.trades.append({
                    'date': row['date'],
                    'action': 'BUY',
                    'price': current_price,
                    'shares': shares_to_buy,
                    'confidence': row['confidence']
                })

                logger.debug(f"BUY {shares_to_buy:.2f} shares @ ${current_price:.2f}")

            # SELL signal
            elif row['prediction'] == 'DOWN' and position > 0:
                sell_value = position * current_price
                capital += sell_value
                pnl = (current_price - entry_price) * position

                self.trades.append({
                    'date': row['date'],
                    'action': 'SELL',
                    'price': current_price,
                    'shares': position,
                    'pnl': pnl,
                    'return_pct': (current_price / entry_price - 1) * 100,
                    'confidence': row['confidence']
                })

                logger.debug(f"SELL {position:.2f} shares @ ${current_price:.2f}, P&L: ${pnl:.2f}")

                position = 0
                entry_price = 0

        # Close any open position
        if position > 0:
            final_price = df.iloc[-1]['close']
            capital += (position * final_price)
            pnl = (final_price - entry_price) * position

            self.trades.append({
                'date': df.iloc[-1]['date'],
                'action': 'SELL',
                'price': final_price,
                'shares': position,
                'pnl': pnl,
                'return_pct': (final_price / entry_price - 1) * 100,
                'confidence': 0
            })

            logger.info(f"Closed final position @ ${final_price:.2f}")

        # Calculate metrics
        final_value = capital
        total_return = (final_value / self.initial_capital - 1) * 100

        trades_df = pd.DataFrame(self.trades)

        if len(trades_df) == 0:
            logger.warning("No trades executed during backtest")
            return {
                'initial_capital': self.initial_capital,
                'final_value': final_value,
                'total_return_pct': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'trades': []
            }

        sell_trades = trades_df[trades_df['action'] == 'SELL']
        winning_trades = sell_trades[sell_trades['pnl'] > 0]
        losing_trades = sell_trades[sell_trades['pnl'] < 0]

        results = {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return_pct': total_return,
            'total_trades': len(trades_df[trades_df['action'] == 'BUY']),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / max(len(winning_trades) + len(losing_trades), 1) * 100,
            'avg_win': winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0,
            'avg_loss': losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0,
            'max_win': winning_trades['pnl'].max() if len(winning_trades) > 0 else 0,
            'max_loss': losing_trades['pnl'].min() if len(losing_trades) > 0 else 0,
            'trades': self.trades
        }

        logger.info(f"✅ Backtest complete:")
        logger.info(f"  Total Return: {total_return:.2f}%")
        logger.info(f"  Win Rate: {results['win_rate']:.1f}%")
        logger.info(f"  Total Trades: {results['total_trades']}")
        logger.info(f"  Avg Win: ${results['avg_win']:.2f}, Avg Loss: ${results['avg_loss']:.2f}")

        return results
