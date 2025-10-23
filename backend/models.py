"""
Database models for PE Dashboard
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date
import enum

try:
    from .database import Base
except ImportError:
    from database import Base

class FlowType(str, enum.Enum):
    CONTRIBUTION = "contribution"
    DISTRIBUTION = "distribution"
    NAV = "nav"

class DealStatus(str, enum.Enum):
    ACTIVE = "active"
    REALIZED = "realized"
    WRITTEN_OFF = "written_off"

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    ticker = Column(String(20), nullable=False, unique=True, index=True)
    sector = Column(String(100), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    deals = relationship("Deal", back_populates="company")

class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    fund_id = Column(Integer, ForeignKey("funds.id"), nullable=True)  # Nullable for backward compatibility
    invest_date = Column(Date, nullable=False)
    invest_amount = Column(Float, nullable=False)
    shares = Column(Float, nullable=False)
    nav_latest = Column(Float, nullable=True)
    status = Column(Enum(DealStatus), nullable=False, default=DealStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="deals")
    fund = relationship("Fund", back_populates="deals")
    cashflows = relationship("CashFlow", back_populates="deal")

class CashFlow(Base):
    __tablename__ = "cashflows"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    flow_type = Column(Enum(FlowType), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    deal = relationship("Deal", back_populates="cashflows")

class MarketData(Base):
    __tablename__ = "market_data_old"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    adj_close = Column(Float, nullable=False)
    dividend = Column(Float, nullable=False, default=0.0)
    volume = Column(Integer, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())

    # Composite unique constraint
    __table_args__ = (
        {"extend_existing": True}
    )

# ===== AlphaSignal Models =====

class AlphaMarketData(Base):
    """Enhanced market data table for AlphaSignal"""
    __tablename__ = "alpha_market_data"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        {"extend_existing": True}
    )

class SentimentData(Base):
    """News and sentiment scores"""
    __tablename__ = "sentiment_data"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    sentiment_score = Column(Float, nullable=True)  # -1 to +1
    article_count = Column(Integer, nullable=True)
    positive_count = Column(Integer, nullable=True)
    negative_count = Column(Integer, nullable=True)
    neutral_count = Column(Integer, nullable=True)
    source = Column(String(50), nullable=True)  # 'news', 'reddit', 'twitter'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        {"extend_existing": True}
    )

class SocialSignals(Base):
    """Social media signals from Reddit, Twitter, etc."""
    __tablename__ = "social_signals"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    reddit_mentions = Column(Integer, default=0)
    reddit_sentiment = Column(Float, nullable=True)
    reddit_score = Column(Integer, nullable=True)  # upvotes
    twitter_mentions = Column(Integer, default=0)
    twitter_sentiment = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        {"extend_existing": True}
    )

class Predictions(Base):
    """ML predictions for price movements"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    prediction_date = Column(Date, nullable=False, index=True)
    target_date = Column(Date, nullable=False)  # Next day
    predicted_direction = Column(String(10), nullable=True)  # 'UP' or 'DOWN'
    probability_up = Column(Float, nullable=True)
    probability_down = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    features = Column(Text, nullable=True)  # JSON stored as text
    actual_direction = Column(String(10), nullable=True)  # For backtesting
    correct = Column(Boolean, nullable=True)
    model_version = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FactorExposures(Base):
    """Fama-French factor analysis results"""
    __tablename__ = "factor_exposures"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=True, index=True)
    portfolio_name = Column(String(50), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    alpha = Column(Float, nullable=True)
    alpha_tstat = Column(Float, nullable=True)
    alpha_pvalue = Column(Float, nullable=True)
    beta_market = Column(Float, nullable=True)
    beta_size = Column(Float, nullable=True)
    beta_value = Column(Float, nullable=True)
    r_squared = Column(Float, nullable=True)
    interpretation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TechnicalIndicators(Base):
    """Cached technical indicators for performance"""
    __tablename__ = "technical_indicators"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    rsi_14 = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    bb_upper = Column(Float, nullable=True)
    bb_middle = Column(Float, nullable=True)
    bb_lower = Column(Float, nullable=True)
    volume_ratio = Column(Float, nullable=True)
    volatility_10d = Column(Float, nullable=True)
    returns_1d = Column(Float, nullable=True)
    returns_5d = Column(Float, nullable=True)
    returns_20d = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        {"extend_existing": True}
    )

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Fund(Base):
    __tablename__ = "funds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    inception_date = Column(Date, nullable=True)
    fund_size = Column(Float, nullable=True)
    currency = Column(String(3), nullable=False, default="USD")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    deals = relationship("Deal", back_populates="fund")