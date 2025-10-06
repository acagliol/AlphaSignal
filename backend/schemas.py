"""
Pydantic schemas for PE Dashboard API
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum

# Enums
class FlowType(str, Enum):
    CONTRIBUTION = "contribution"
    DISTRIBUTION = "distribution"
    NAV = "nav"

class DealStatus(str, Enum):
    ACTIVE = "active"
    REALIZED = "realized"
    WRITTEN_OFF = "written_off"

# Base schemas
class CompanyBase(BaseModel):
    name: str = Field(..., max_length=255)
    ticker: str = Field(..., max_length=20)
    sector: str = Field(..., max_length=100)
    currency: str = Field(default="USD", max_length=3)

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DealBase(BaseModel):
    invest_date: date
    invest_amount: float = Field(..., gt=0)
    shares: float = Field(..., gt=0)
    nav_latest: Optional[float] = None
    status: DealStatus = DealStatus.ACTIVE

class DealCreate(DealBase):
    company_id: int
    fund_id: Optional[int] = None

class Deal(DealBase):
    id: int
    company_id: int
    fund_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    company: Optional[Company] = None

    class Config:
        from_attributes = True

class CashFlowBase(BaseModel):
    date: date
    amount: float
    flow_type: FlowType
    description: Optional[str] = None

class CashFlowCreate(CashFlowBase):
    deal_id: int

class CashFlow(CashFlowBase):
    id: int
    deal_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class MarketDataBase(BaseModel):
    ticker: str = Field(..., max_length=20)
    date: date
    adj_close: float = Field(..., gt=0)
    dividend: float = Field(default=0.0, ge=0)
    volume: Optional[int] = None

class MarketDataCreate(MarketDataBase):
    pass

class MarketData(MarketDataBase):
    id: int
    last_updated: datetime
    
    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    email: str = Field(..., max_length=255)
    full_name: Optional[str] = Field(None, max_length=255)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Fund schemas
class FundBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    inception_date: Optional[date] = None
    fund_size: Optional[float] = Field(None, gt=0)
    currency: str = Field(default="USD", max_length=3)

class FundCreate(FundBase):
    pass

class FundUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    inception_date: Optional[date] = None
    fund_size: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=3)
    is_active: Optional[bool] = None

class Fund(FundBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Investment schemas (alias for Deal)
class InvestmentCreate(DealCreate):
    pass

class InvestmentUpdate(BaseModel):
    invest_date: Optional[date] = None
    invest_amount: Optional[float] = Field(None, gt=0)
    shares: Optional[float] = Field(None, gt=0)
    nav_latest: Optional[float] = None
    status: Optional[DealStatus] = None

class Investment(Deal):
    pass

# Data ingestion schemas
class CompanyIngest(BaseModel):
    name: str = Field(..., max_length=255)
    ticker: str = Field(..., max_length=20)
    sector: str = Field(..., max_length=100)
    currency: str = Field(default="USD", max_length=3)
    invest_date: date
    invest_amount: float = Field(..., gt=0)
    fund_id: Optional[int] = None  # Optional fund assignment

class IngestResult(BaseModel):
    success: bool
    message: str
    companies_processed: int
    companies_failed: int
    errors: List[str] = []

# KPI schemas
class DealKPIs(BaseModel):
    deal_id: int
    company_name: str
    ticker: str
    invest_date: date
    invest_amount: float
    current_value: float
    shares: float
    current_price: float
    irr: Optional[float] = None
    moic: Optional[float] = None
    dpi: Optional[float] = None
    tvpi: Optional[float] = None
    rvpi: Optional[float] = None
    total_distributions: float = 0.0
    unrealized_gain: float = 0.0
    realized_gain: float = 0.0
    as_of_date: date

class PortfolioKPIs(BaseModel):
    total_invested: float
    total_current_value: float
    total_distributions: float
    portfolio_irr: Optional[float] = None
    portfolio_moic: Optional[float] = None
    portfolio_dpi: Optional[float] = None
    portfolio_tvpi: Optional[float] = None
    portfolio_rvpi: Optional[float] = None
    total_unrealized_gain: float
    total_realized_gain: float
    active_deals: int
    realized_deals: int
    as_of_date: date

class SectorAnalytics(BaseModel):
    sector: str
    deal_count: int
    total_invested: float
    total_current_value: float
    avg_irr: Optional[float] = None
    avg_moic: Optional[float] = None
    total_distributions: float
    unrealized_gain: float
    realized_gain: float

class PortfolioMetrics(BaseModel):
    total_value: float
    total_invested: float
    unrealized_gain: float
    realized_gain: float
    total_distributions: float
    portfolio_irr: Optional[float] = None
    active_deals: int

class PerformanceMetrics(BaseModel):
    irr: Optional[float] = None
    moic: Optional[float] = None
    dpi: Optional[float] = None
    tvpi: Optional[float] = None
    rvpi: Optional[float] = None
    calculation_date: date

# Report schemas
class Report(BaseModel):
    id: int
    title: str
    description: str
    report_type: str
    generated_at: datetime
    file_path: Optional[str] = None
    
    class Config:
        from_attributes = True

# API Response schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: List[str] = []