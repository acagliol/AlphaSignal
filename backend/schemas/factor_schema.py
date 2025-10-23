"""
Factor Analysis Schemas
"""

from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class FactorExposureResponse(BaseModel):
    id: int
    ticker: str
    portfolio_name: str
    start_date: date
    end_date: date
    alpha: float
    alpha_tstat: float
    alpha_pvalue: float
    beta_market: float
    beta_size: float
    beta_value: float
    r_squared: float
    interpretation: str
    created_at: datetime

    class Config:
        from_attributes = True
