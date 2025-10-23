"""
Pydantic schemas for AlphaSignal models
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


# ===== Market Data Schemas =====

class MarketDataBase(BaseModel):
    ticker: str
    date: date
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: float
    volume: Optional[int] = None


class MarketDataCreate(MarketDataBase):
    pass


class MarketDataResponse(MarketDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Sentiment Data Schemas =====

class SentimentDataBase(BaseModel):
    ticker: str
    date: date
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    article_count: Optional[int] = None
    positive_count: Optional[int] = None
    negative_count: Optional[int] = None
    neutral_count: Optional[int] = None
    source: Optional[str] = None


class SentimentDataCreate(SentimentDataBase):
    pass


class SentimentDataResponse(SentimentDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Social Signals Schemas =====

class SocialSignalsBase(BaseModel):
    ticker: str
    date: date
    reddit_mentions: int = 0
    reddit_sentiment: Optional[float] = None
    reddit_score: Optional[int] = None
    twitter_mentions: int = 0
    twitter_sentiment: Optional[float] = None


class SocialSignalsCreate(SocialSignalsBase):
    pass


class SocialSignalsResponse(SocialSignalsBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Predictions Schemas =====

class PredictionBase(BaseModel):
    ticker: str
    prediction_date: date
    target_date: date
    predicted_direction: Optional[str] = None
    probability_up: Optional[float] = Field(None, ge=0.0, le=1.0)
    probability_down: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    features: Optional[str] = None  # JSON string
    model_version: Optional[str] = None


class PredictionCreate(PredictionBase):
    pass


class PredictionUpdate(BaseModel):
    actual_direction: Optional[str] = None
    correct: Optional[bool] = None


class PredictionResponse(PredictionBase):
    id: int
    actual_direction: Optional[str] = None
    correct: Optional[bool] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Factor Exposures Schemas =====

class FactorExposureBase(BaseModel):
    ticker: Optional[str] = None
    portfolio_name: Optional[str] = None
    start_date: date
    end_date: date
    alpha: Optional[float] = None
    alpha_tstat: Optional[float] = None
    alpha_pvalue: Optional[float] = None
    beta_market: Optional[float] = None
    beta_size: Optional[float] = None
    beta_value: Optional[float] = None
    r_squared: Optional[float] = None
    interpretation: Optional[str] = None


class FactorExposureCreate(FactorExposureBase):
    pass


class FactorExposureResponse(FactorExposureBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Technical Indicators Schemas =====

class TechnicalIndicatorsBase(BaseModel):
    ticker: str
    date: date
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    volume_ratio: Optional[float] = None
    volatility_10d: Optional[float] = None
    returns_1d: Optional[float] = None
    returns_5d: Optional[float] = None
    returns_20d: Optional[float] = None


class TechnicalIndicatorsCreate(TechnicalIndicatorsBase):
    pass


class TechnicalIndicatorsResponse(TechnicalIndicatorsBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Analytics Response Schemas =====

class SentimentCorrelationResponse(BaseModel):
    ticker: str
    correlation: float
    p_value: float
    sample_size: int
    start_date: date
    end_date: date


class AccuracyMetrics(BaseModel):
    total_predictions: int
    correct_predictions: int
    accuracy: float
    high_confidence_accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None


class PortfolioAlphaResponse(BaseModel):
    portfolio_name: str
    alpha: float
    alpha_annualized: float
    t_statistic: float
    p_value: float
    is_significant: bool
    interpretation: str
    factor_exposures: dict
