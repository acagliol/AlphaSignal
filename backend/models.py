"""
Database models for PE Dashboard
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date
import enum

from .database import Base

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
    __tablename__ = "market_data"
    
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