"""
Private Equity Investment Dashboard Backend
FastAPI application with financial analytics and C++ integration
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import uvicorn
from typing import List, Optional
import os
from datetime import date
from dotenv import load_dotenv

from .database import get_db, engine
from .models import Base
from .schemas import (
    User, UserCreate, UserLogin, Token,
    Fund, FundCreate, FundUpdate,
    Investment, InvestmentCreate, InvestmentUpdate,
    PortfolioMetrics, PerformanceMetrics,
    CompanyIngest, IngestResult, DealKPIs, PortfolioKPIs, SectorAnalytics,
    CompanyCreate, Deal, Company, CashFlow, FlowType
)
from .auth import authenticate_user, create_access_token, get_current_user
from .services import DealService, PortfolioService, FinancialCalculator
from .crud import CompanyCRUD, DealCRUD, CashFlowCRUD, MarketDataCRUD, UserCRUD, FundCRUD
# from .alpha_service import AlphaVantageService  # Commented out - using yfinance
from .yfinance_service import YFinanceService

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="PE Investment Dashboard API",
    description="Backend API for Private Equity Investment Dashboard with C++ financial calculations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize financial calculator
calculator = FinancialCalculator()

@app.get("/")
async def root():
    return {"message": "PE Investment Dashboard API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Authentication endpoints
@app.post("/auth/register", response_model=User)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    user_crud = UserCRUD(db)
    hashed_password = "hashed_password_here"  # In production, hash the password
    return user_crud.create(user_data, hashed_password)

@app.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# Fund management endpoints
@app.get("/funds", response_model=List[Fund])
async def get_funds(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all funds for the current user"""
    fund_crud = FundCRUD(db)
    return fund_crud.get_by_user(current_user.id, skip, limit)

@app.post("/funds", response_model=Fund)
async def create_fund(
    fund_data: FundCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new fund"""
    fund_crud = FundCRUD(db)
    return fund_crud.create(fund_data, current_user.id)

@app.get("/funds/{fund_id}", response_model=Fund)
async def get_fund(
    fund_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific fund by ID"""
    fund_crud = FundCRUD(db)
    fund = fund_crud.get_by_id(fund_id, current_user.id)
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    return fund

@app.put("/funds/{fund_id}", response_model=Fund)
async def update_fund(
    fund_id: int,
    fund_data: FundUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a fund"""
    fund_crud = FundCRUD(db)
    fund = fund_crud.update(fund_id, current_user.id, fund_data.dict(exclude_unset=True))
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    return fund

# Investment management endpoints
@app.get("/investments", response_model=List[Investment])
async def get_investments(
    fund_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get investments, optionally filtered by fund"""
    deal_crud = DealCRUD(db)
    return deal_crud.get_all(skip, limit)

@app.post("/investments", response_model=Investment)
async def create_investment(
    investment_data: InvestmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new investment"""
    deal_crud = DealCRUD(db)
    return deal_crud.create(investment_data)

@app.put("/investments/{investment_id}", response_model=Investment)
async def update_investment(
    investment_id: int,
    investment_data: InvestmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an investment"""
    deal_crud = DealCRUD(db)
    investment = deal_crud.update(investment_id, investment_data.dict(exclude_unset=True))
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    return investment

# Portfolio analytics endpoints
@app.get("/portfolio/metrics", response_model=PortfolioMetrics)
async def get_portfolio_metrics(
    fund_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio-level metrics and KPIs"""
    portfolio_service = PortfolioService(db)
    kpis = await portfolio_service.get_portfolio_kpis()
    return PortfolioMetrics(
        total_value=kpis.total_current_value,
        total_invested=kpis.total_invested,
        unrealized_gain=kpis.total_unrealized_gain,
        realized_gain=kpis.total_realized_gain,
        total_distributions=kpis.total_distributions,
        portfolio_irr=kpis.portfolio_irr,
        active_deals=kpis.active_deals
    )

@app.get("/portfolio/performance", response_model=PerformanceMetrics)
async def get_performance_metrics(
    fund_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance metrics"""
    portfolio_service = PortfolioService(db)
    kpis = await portfolio_service.get_portfolio_kpis()
    return PerformanceMetrics(
        irr=kpis.portfolio_irr,
        moic=kpis.portfolio_moic,
        dpi=kpis.portfolio_dpi,
        tvpi=kpis.portfolio_tvpi,
        rvpi=kpis.portfolio_rvpi,
        calculation_date=kpis.as_of_date
    )

@app.get("/analytics/sector-analysis")
async def get_sector_analysis(
    fund_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sector-wise analysis and performance metrics"""
    portfolio_service = PortfolioService(db)
    return await portfolio_service.get_sector_analytics()

@app.get("/analytics/risk-return")
async def get_risk_return_analysis(
    fund_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get risk-return analysis"""
    portfolio_service = PortfolioService(db)
    kpis = await portfolio_service.get_portfolio_kpis()
    return {
        "portfolio_irr": kpis.portfolio_irr,
        "total_value": kpis.total_current_value,
        "total_invested": kpis.total_invested
    }

# Data Ingestion Endpoints
@app.post("/api/v1/ingest/companies", response_model=IngestResult)
async def ingest_companies(
    companies: List[CompanyIngest],
    db: Session = Depends(get_db)
):
    """Ingest companies and create deals with Alpha Vantage data"""
    company_crud = CompanyCRUD(db)
    deal_crud = DealCRUD(db)
    market_data_crud = MarketDataCRUD(db)
    deal_service = DealService(db)
    
    processed = 0
    failed = 0
    errors = []
    
    async with YFinanceService() as alpha_service:
        for company_data in companies:
            try:
                # Validate ticker with Alpha Vantage
                if not await alpha_service.validate_ticker(company_data.ticker):
                    errors.append(f"Invalid ticker: {company_data.ticker}")
                    failed += 1
                    continue
                
                # Create or get company
                existing_company = company_crud.get_by_ticker(company_data.ticker)
                if existing_company:
                    company = existing_company
                else:
                    company = company_crud.create(CompanyCreate(
                        name=company_data.name,
                        ticker=company_data.ticker,
                        sector=company_data.sector,
                        currency=company_data.currency
                    ))
                
                # Get historical price on invest_date
                historical_price = await alpha_service.get_historical_price(
                    company_data.ticker, company_data.invest_date
                )
                
                if not historical_price:
                    errors.append(f"No historical price for {company_data.ticker} on {company_data.invest_date}")
                    failed += 1
                    continue
                
                # Calculate shares
                shares = company_data.invest_amount / historical_price
                
                # Create deal (with fund_id if provided)
                deal = await deal_service.create_deal(
                    company_id=company.id,
                    invest_date=company_data.invest_date,
                    invest_amount=company_data.invest_amount,
                    shares=shares,
                    nav_latest=historical_price,
                    fund_id=company_data.fund_id  # Pass fund_id from ingestion data
                )
                
                # Get latest price and update NAV
                latest_price = await alpha_service.get_latest_price(company_data.ticker)
                if latest_price:
                    await deal_service.update_nav(deal.id, latest_price)
                
                # Get dividend history and add distributions
                dividend_history = await alpha_service.get_dividend_history(
                    company_data.ticker, company_data.invest_date
                )
                
                for dividend_data in dividend_history:
                    await deal_service.add_dividend(
                        deal.id, 
                        dividend_data['date'], 
                        dividend_data['dividend']
                    )
                
                processed += 1
                
            except Exception as e:
                errors.append(f"Error processing {company_data.ticker}: {str(e)}")
                failed += 1
                continue
    
    return IngestResult(
        success=processed > 0,
        message=f"Processed {processed} companies, {failed} failed",
        companies_processed=processed,
        companies_failed=failed,
        errors=errors
    )

# Core Data Access Endpoints

# Fund Endpoints
@app.get("/api/v1/funds", response_model=List[Fund])
async def get_all_funds(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all funds"""
    fund_crud = FundCRUD(db)
    return fund_crud.get_all(skip=skip, limit=limit)

@app.post("/api/v1/funds", response_model=Fund)
async def create_fund_v1(
    fund_data: FundCreate,
    db: Session = Depends(get_db)
):
    """Create a new fund"""
    from .models import Fund as FundModel
    fund = FundModel(**fund_data.dict())
    db.add(fund)
    db.commit()
    db.refresh(fund)
    return fund

@app.get("/api/v1/funds/{fund_id}", response_model=Fund)
async def get_fund_by_id(
    fund_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific fund by ID"""
    fund_crud = FundCRUD(db)
    fund = fund_crud.get_by_id_public(fund_id)
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    return fund

# Deal Endpoints
@app.get("/api/v1/deals", response_model=List[Deal])
async def get_deals(
    fund_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all deals, optionally filtered by fund"""
    deal_crud = DealCRUD(db)
    if fund_id:
        from .models import Deal as DealModel
        deals = db.query(DealModel).filter(DealModel.fund_id == fund_id).offset(skip).limit(limit).all()
        return deals
    return deal_crud.get_all(skip=skip, limit=limit)

@app.get("/api/v1/deals/{deal_id}/kpis", response_model=DealKPIs)
async def get_deal_kpis(
    deal_id: int,
    as_of: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get KPIs for a specific deal"""
    deal_service = DealService(db)
    
    as_of_date = None
    if as_of:
        from datetime import datetime
        as_of_date = datetime.strptime(as_of, "%Y-%m-%d").date()
    
    return await deal_service.get_deal_kpis(deal_id, as_of_date)

@app.get("/api/v1/portfolio/kpis", response_model=PortfolioKPIs)
async def get_portfolio_kpis(
    fund_id: Optional[int] = None,
    as_of: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get portfolio-level KPIs, optionally filtered by fund"""
    portfolio_service = PortfolioService(db)

    as_of_date = None
    if as_of:
        from datetime import datetime
        as_of_date = datetime.strptime(as_of, "%Y-%m-%d").date()

    return await portfolio_service.get_portfolio_kpis(fund_id=fund_id, as_of_date=as_of_date)

@app.get("/api/v1/analytics/sectors", response_model=List[SectorAnalytics])
async def get_sector_analytics(
    as_of: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get sector-wise analytics"""
    portfolio_service = PortfolioService(db)
    
    as_of_date = None
    if as_of:
        from datetime import datetime
        as_of_date = datetime.strptime(as_of, "%Y-%m-%d").date()
    
    return await portfolio_service.get_sector_analytics(as_of_date)

# Data Refresh Endpoints
@app.post("/api/v1/refresh/market-data")
async def refresh_market_data(
    tickers: List[str],
    db: Session = Depends(get_db)
):
    """Refresh market data for specified tickers"""
    market_data_crud = MarketDataCRUD(db)
    deal_service = DealService(db)
    
    updated_tickers = []
    errors = []
    
    async with YFinanceService() as alpha_service:
        for ticker in tickers:
            try:
                # Get latest price
                latest_price = await alpha_service.get_latest_price(ticker)
                if latest_price:
                    # Update market data
                    market_data_crud.update_or_create(
                        ticker=ticker,
                        date=date.today(),
                        adj_close=latest_price
                    )
                    
                    # Update all deals for this ticker
                    deals = db.query(Deal).join(Company).filter(Company.ticker == ticker).all()
                    for deal in deals:
                        await deal_service.update_nav(deal.id, latest_price)
                    
                    updated_tickers.append(ticker)
                else:
                    errors.append(f"No price data for {ticker}")
                    
            except Exception as e:
                errors.append(f"Error updating {ticker}: {str(e)}")
    
    return {
        "success": len(updated_tickers) > 0,
        "updated_tickers": updated_tickers,
        "errors": errors
    }

@app.post("/api/v1/refresh/deal/{deal_id}")
async def refresh_deal(
    deal_id: int,
    db: Session = Depends(get_db)
):
    """Refresh data for a specific deal"""
    deal_crud = DealCRUD(db)
    deal_service = DealService(db)
    
    deal = deal_crud.get_by_id(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    try:
        async with YFinanceService() as alpha_service:
            # Get latest price
            latest_price = await alpha_service.get_latest_price(deal.company.ticker)
            if latest_price:
                await deal_service.update_nav(deal_id, latest_price)
                
                # Get new dividends
                last_dividend = db.query(CashFlow).filter(
                    and_(
                        CashFlow.deal_id == deal_id,
                        CashFlow.flow_type == FlowType.DISTRIBUTION
                    )
                ).order_by(desc(CashFlow.date)).first()
                
                start_date = last_dividend.date if last_dividend else deal.invest_date
                dividend_history = await alpha_service.get_dividend_history(
                    deal.company.ticker, start_date
                )
                
                for dividend_data in dividend_history:
                    if dividend_data['date'] > start_date:
                        await deal_service.add_dividend(
                            deal_id,
                            dividend_data['date'],
                            dividend_data['dividend']
                        )
                
                return {"success": True, "message": f"Deal {deal_id} refreshed successfully"}
            else:
                return {"success": False, "message": f"No price data for {deal.company.ticker}"}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing deal: {str(e)}")

# Reports Endpoints
@app.get("/api/v1/reports/recent", response_model=List[dict])
async def get_recent_reports():
    """Get recent reports (placeholder for now)"""
    return [
        {
            "id": 1,
            "title": "Quarterly Performance Report",
            "description": "Comprehensive analysis of fund performance for Q4 2023",
            "report_type": "Performance",
            "generated_at": "2024-01-15T10:00:00Z"
        },
        {
            "id": 2,
            "title": "Portfolio Company Update",
            "description": "Detailed updates on all active portfolio companies",
            "report_type": "Portfolio",
            "generated_at": "2024-01-10T14:30:00Z"
        }
    ]

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )