"""
Fama-French 3-Factor Model Analysis
Decompose returns into systematic risk factors
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class FamaFrenchAnalysis:
    """
    Fama-French 3-Factor Model Analysis
    Decompose returns into systematic risk factors
    """

    def __init__(self):
        # Load FF factors (in practice, download from Ken French's data library)
        self.factors = self._load_factors()

    def _load_factors(self) -> pd.DataFrame:
        """
        Load Fama-French factors
        In production: Download from https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
        For now: Generate synthetic factors
        """
        # Synthetic data for demonstration
        dates = pd.date_range('2020-01-01', '2024-12-31', freq='D')

        df = pd.DataFrame({
            'date': dates,
            'mkt_rf': np.random.normal(0.0005, 0.01, len(dates)),  # Market premium
            'smb': np.random.normal(0.0002, 0.005, len(dates)),    # Size factor
            'hml': np.random.normal(0.0001, 0.005, len(dates)),    # Value factor
            'rf': np.full(len(dates), 0.0001)                      # Risk-free rate
        })

        logger.info(f"Loaded {len(df)} days of Fama-French factors (synthetic data)")

        return df

    def run_regression(
        self,
        returns: pd.Series,
        return_type: str = 'daily'  # 'daily' or 'monthly'
    ) -> Dict[str, any]:
        """
        Run FF3 regression

        Model: R_p - R_f = α + β_mkt*(R_m - R_f) + β_smb*SMB + β_hml*HML + ε

        Returns:
            alpha: Risk-adjusted excess return (annualized)
            betas: Factor loadings
            stats: T-stats, p-values, R-squared
        """

        logger.info(f"Running FF3 regression on {len(returns)} {return_type} returns")

        # Prepare data
        df = pd.DataFrame({'returns': returns})
        df = df.merge(self.factors, left_index=True, right_on='date', how='inner')

        if len(df) < 30:
            raise ValueError(f"Insufficient data for regression: {len(df)} observations (need at least 30)")

        # Excess returns
        df['excess_return'] = df['returns'] - df['rf']

        # Regression: Y = α + β_1*X_1 + β_2*X_2 + β_3*X_3
        y = df['excess_return']
        X = df[['mkt_rf', 'smb', 'hml']]
        X = sm.add_constant(X)

        # OLS regression
        model = sm.OLS(y, X).fit()

        # Annualization factor
        periods_per_year = 252 if return_type == 'daily' else 12

        # Extract results
        alpha = model.params['const']
        alpha_annual = alpha * periods_per_year

        results = {
            'alpha': alpha,
            'alpha_annual': alpha_annual,
            'alpha_annual_pct': alpha_annual * 100,
            'alpha_tstat': model.tvalues['const'],
            'alpha_pvalue': model.pvalues['const'],
            'alpha_significant': model.pvalues['const'] < 0.05,

            'beta_market': model.params['mkt_rf'],
            'beta_market_tstat': model.tvalues['mkt_rf'],
            'beta_market_significant': model.pvalues['mkt_rf'] < 0.05,

            'beta_size': model.params['smb'],
            'beta_size_tstat': model.tvalues['smb'],
            'beta_size_significant': model.pvalues['smb'] < 0.05,

            'beta_value': model.params['hml'],
            'beta_value_tstat': model.tvalues['hml'],
            'beta_value_significant': model.pvalues['hml'] < 0.05,

            'r_squared': model.rsquared,
            'adjusted_r_squared': model.rsquared_adj,
            'n_observations': len(df),

            'interpretation': self._interpret_results(model, alpha_annual)
        }

        logger.info(f"FF3 Analysis: Alpha={alpha_annual*100:.2f}% (t={model.tvalues['const']:.2f}), R²={model.rsquared:.3f}")

        return results

    def _interpret_results(self, model, alpha_annual: float) -> str:
        """Generate human-readable interpretation"""

        interpretations = []

        # Alpha interpretation
        if model.pvalues['const'] < 0.05:
            if alpha_annual > 0:
                interpretations.append(
                    f"✅ Significant POSITIVE alpha of {alpha_annual*100:.2f}% annually "
                    f"(t-stat={model.tvalues['const']:.2f}) - beating risk-adjusted benchmark"
                )
            else:
                interpretations.append(
                    f"❌ Significant NEGATIVE alpha of {alpha_annual*100:.2f}% annually "
                    f"(t-stat={model.tvalues['const']:.2f}) - underperforming after risk adjustment"
                )
        else:
            interpretations.append(
                f"⚪ Alpha of {alpha_annual*100:.2f}% is NOT statistically significant "
                f"(p={model.pvalues['const']:.4f}) - returns explained by factor exposure"
            )

        # Market beta interpretation
        beta_mkt = model.params['mkt_rf']
        if model.pvalues['mkt_rf'] < 0.05:
            if beta_mkt > 1.2:
                interpretations.append(
                    f"📈 High market beta ({beta_mkt:.2f}) - AGGRESSIVE portfolio, "
                    f"amplifies market movements by {((beta_mkt-1)*100):.0f}%"
                )
            elif beta_mkt < 0.8:
                interpretations.append(
                    f"🛡️ Low market beta ({beta_mkt:.2f}) - DEFENSIVE portfolio, "
                    f"dampens market movements by {((1-beta_mkt)*100):.0f}%"
                )
            else:
                interpretations.append(
                    f"📊 Market beta ({beta_mkt:.2f}) - moves in line with market"
                )

        # Size factor interpretation
        beta_smb = model.params['smb']
        if abs(beta_smb) > 0.3 and model.pvalues['smb'] < 0.05:
            if beta_smb > 0:
                interpretations.append(
                    f"🏢 Positive size exposure ({beta_smb:.2f}) - TILTED toward small-cap stocks"
                )
            else:
                interpretations.append(
                    f"🏛️ Negative size exposure ({beta_smb:.2f}) - TILTED toward large-cap stocks"
                )

        # Value factor interpretation
        beta_hml = model.params['hml']
        if abs(beta_hml) > 0.3 and model.pvalues['hml'] < 0.05:
            if beta_hml > 0:
                interpretations.append(
                    f"💰 Positive value exposure ({beta_hml:.2f}) - VALUE tilt (cheap stocks)"
                )
            else:
                interpretations.append(
                    f"🚀 Negative value exposure ({beta_hml:.2f}) - GROWTH tilt (expensive/momentum stocks)"
                )

        # R-squared interpretation
        r_sq = model.rsquared
        interpretations.append(
            f"📉 Factors explain {r_sq*100:.1f}% of return variance"
        )

        return " | ".join(interpretations)

    def rolling_factor_exposure(
        self,
        returns: pd.Series,
        window: int = 252  # 1 year
    ) -> pd.DataFrame:
        """Calculate rolling factor exposures over time"""

        logger.info(f"Calculating rolling factor exposures with {window}-day window")

        results = []

        for i in range(window, len(returns)):
            window_returns = returns.iloc[i-window:i]

            try:
                result = self.run_regression(window_returns, return_type='daily')
                results.append({
                    'date': returns.index[i],
                    'alpha_annual': result['alpha_annual'],
                    'beta_market': result['beta_market'],
                    'beta_size': result['beta_size'],
                    'beta_value': result['beta_value'],
                    'r_squared': result['r_squared']
                })
            except Exception as e:
                logger.warning(f"Error in rolling window {i}: {e}")
                continue

        logger.info(f"Calculated {len(results)} rolling windows")

        return pd.DataFrame(results)
