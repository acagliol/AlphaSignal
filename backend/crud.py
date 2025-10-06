"""
CRUD operations for PE Dashboard
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from datetime import date, datetime

from .models import Company, Deal, CashFlow, MarketData, User, Fund, FlowType, DealStatus
from .schemas import CompanyCreate, DealCreate, CashFlowCreate, MarketDataCreate, UserCreate, FundCreate

class CompanyCRUD:
    """CRUD operations for Company model"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, company_data: CompanyCreate) -> Company:
        """Create a new company"""
        try:
            company = Company(**company_data.dict())
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
            return company
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_by_id(self, company_id: int) -> Optional[Company]:
        """Get company by ID"""
        return self.db.query(Company).filter(Company.id == company_id).first()
    
    def get_by_ticker(self, ticker: str) -> Optional[Company]:
        """Get company by ticker symbol"""
        return self.db.query(Company).filter(Company.ticker == ticker).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Company]:
        """Get all companies with pagination"""
        return self.db.query(Company).offset(skip).limit(limit).all()
    
    def get_by_sector(self, sector: str) -> List[Company]:
        """Get companies by sector"""
        return self.db.query(Company).filter(Company.sector == sector).all()
    
    def update(self, company_id: int, update_data: Dict[str, Any]) -> Optional[Company]:
        """Update company information"""
        try:
            company = self.db.query(Company).filter(Company.id == company_id).first()
            if not company:
                return None
            
            for key, value in update_data.items():
                if hasattr(company, key):
                    setattr(company, key, value)
            
            company.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(company)
            return company
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete(self, company_id: int) -> bool:
        """Delete a company"""
        try:
            company = self.db.query(Company).filter(Company.id == company_id).first()
            if not company:
                return False
            
            self.db.delete(company)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

class DealCRUD:
    """CRUD operations for Deal model"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, deal_data: DealCreate) -> Deal:
        """Create a new deal"""
        try:
            deal = Deal(**deal_data.dict())
            self.db.add(deal)
            self.db.commit()
            self.db.refresh(deal)
            return deal
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_by_id(self, deal_id: int) -> Optional[Deal]:
        """Get deal by ID with company info"""
        return self.db.query(Deal).join(Company).filter(Deal.id == deal_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Deal]:
        """Get all deals with company info"""
        return self.db.query(Deal).join(Company).offset(skip).limit(limit).all()
    
    def get_by_company(self, company_id: int) -> List[Deal]:
        """Get deals by company"""
        return self.db.query(Deal).filter(Deal.company_id == company_id).all()
    
    def get_by_status(self, status: DealStatus) -> List[Deal]:
        """Get deals by status"""
        return self.db.query(Deal).join(Company).filter(Deal.status == status).all()
    
    def update(self, deal_id: int, update_data: Dict[str, Any]) -> Optional[Deal]:
        """Update deal information"""
        try:
            deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                return None
            
            for key, value in update_data.items():
                if hasattr(deal, key):
                    setattr(deal, key, value)
            
            deal.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(deal)
            return deal
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete(self, deal_id: int) -> bool:
        """Delete a deal"""
        try:
            deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                return False
            
            self.db.delete(deal)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

class CashFlowCRUD:
    """CRUD operations for CashFlow model"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, cashflow_data: CashFlowCreate) -> CashFlow:
        """Create a new cashflow"""
        try:
            cashflow = CashFlow(**cashflow_data.dict())
            self.db.add(cashflow)
            self.db.commit()
            self.db.refresh(cashflow)
            return cashflow
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_by_deal(self, deal_id: int) -> List[CashFlow]:
        """Get all cashflows for a deal"""
        return self.db.query(CashFlow).filter(CashFlow.deal_id == deal_id).order_by(CashFlow.date).all()
    
    def get_by_deal_and_type(self, deal_id: int, flow_type: FlowType) -> List[CashFlow]:
        """Get cashflows by deal and type"""
        return self.db.query(CashFlow).filter(
            and_(
                CashFlow.deal_id == deal_id,
                CashFlow.flow_type == flow_type
            )
        ).order_by(CashFlow.date).all()
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[CashFlow]:
        """Get cashflows within date range"""
        return self.db.query(CashFlow).filter(
            and_(
                CashFlow.date >= start_date,
                CashFlow.date <= end_date
            )
        ).order_by(CashFlow.date).all()
    
    def get_total_by_type(self, deal_id: int, flow_type: FlowType) -> float:
        """Get total amount by flow type for a deal"""
        result = self.db.query(func.sum(CashFlow.amount)).filter(
            and_(
                CashFlow.deal_id == deal_id,
                CashFlow.flow_type == flow_type
            )
        ).scalar()
        return result or 0.0

class MarketDataCRUD:
    """CRUD operations for MarketData model"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, market_data: MarketDataCreate) -> MarketData:
        """Create new market data entry"""
        try:
            data = MarketData(**market_data.dict())
            self.db.add(data)
            self.db.commit()
            self.db.refresh(data)
            return data
        except Exception as e:
            self.db.rollback()
            raise e
    
    def create_bulk(self, market_data_list: List[MarketDataCreate]) -> List[MarketData]:
        """Create multiple market data entries"""
        try:
            data_objects = [MarketData(**data.dict()) for data in market_data_list]
            self.db.add_all(data_objects)
            self.db.commit()
            for obj in data_objects:
                self.db.refresh(obj)
            return data_objects
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_by_ticker(self, ticker: str, start_date: Optional[date] = None, 
                     end_date: Optional[date] = None) -> List[MarketData]:
        """Get market data by ticker with optional date range"""
        query = self.db.query(MarketData).filter(MarketData.ticker == ticker)
        
        if start_date:
            query = query.filter(MarketData.date >= start_date)
        if end_date:
            query = query.filter(MarketData.date <= end_date)
        
        return query.order_by(MarketData.date).all()
    
    def get_latest_price(self, ticker: str) -> Optional[MarketData]:
        """Get latest price for a ticker"""
        return self.db.query(MarketData).filter(
            MarketData.ticker == ticker
        ).order_by(desc(MarketData.date)).first()
    
    def get_price_on_date(self, ticker: str, target_date: date) -> Optional[MarketData]:
        """Get price on specific date, or closest available date"""
        # First try exact date
        exact_match = self.db.query(MarketData).filter(
            and_(
                MarketData.ticker == ticker,
                MarketData.date == target_date
            )
        ).first()
        
        if exact_match:
            return exact_match
        
        # If no exact match, find closest date within 5 days
        from datetime import timedelta
        
        for days_offset in range(6):  # 0 to 5 days
            for offset in [0, -1, 1, -2, 2, -3, 3, -4, 4, -5, 5]:
                check_date = target_date + timedelta(days=offset)
                closest = self.db.query(MarketData).filter(
                    and_(
                        MarketData.ticker == ticker,
                        MarketData.date == check_date
                    )
                ).first()
                if closest:
                    return closest
        
        return None
    
    def update_or_create(self, ticker: str, date: date, adj_close: float, 
                        dividend: float = 0.0, volume: Optional[int] = None) -> MarketData:
        """Update existing entry or create new one"""
        try:
            existing = self.db.query(MarketData).filter(
                and_(
                    MarketData.ticker == ticker,
                    MarketData.date == date
                )
            ).first()
            
            if existing:
                existing.adj_close = adj_close
                existing.dividend = dividend
                existing.volume = volume
                existing.last_updated = datetime.utcnow()
                self.db.commit()
                self.db.refresh(existing)
                return existing
            else:
                new_data = MarketData(
                    ticker=ticker,
                    date=date,
                    adj_close=adj_close,
                    dividend=dividend,
                    volume=volume
                )
                self.db.add(new_data)
                self.db.commit()
                self.db.refresh(new_data)
                return new_data
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_dividend_history(self, ticker: str, start_date: date) -> List[MarketData]:
        """Get dividend history since start_date"""
        return self.db.query(MarketData).filter(
            and_(
                MarketData.ticker == ticker,
                MarketData.date >= start_date,
                MarketData.dividend > 0
            )
        ).order_by(MarketData.date).all()

class UserCRUD:
    """CRUD operations for User model"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_data: UserCreate, hashed_password: str) -> User:
        """Create a new user"""
        try:
            user = User(
                email=user_data.email,
                full_name=user_data.full_name,
                hashed_password=hashed_password
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def update(self, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user information"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise e

class FundCRUD:
    """CRUD operations for Fund model"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, fund_data: FundCreate, user_id: int) -> Fund:
        """Create a new fund"""
        try:
            fund = Fund(
                name=fund_data.name,
                description=fund_data.description,
                user_id=user_id
            )
            self.db.add(fund)
            self.db.commit()
            self.db.refresh(fund)
            return fund
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Fund]:
        """Get all funds (public access)"""
        return self.db.query(Fund).filter(Fund.is_active == True).offset(skip).limit(limit).all()

    def get_by_id_public(self, fund_id: int) -> Optional[Fund]:
        """Get fund by ID (public access)"""
        return self.db.query(Fund).filter(Fund.id == fund_id).first()

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Fund]:
        """Get funds by user"""
        return self.db.query(Fund).filter(Fund.user_id == user_id).offset(skip).limit(limit).all()

    def get_by_id(self, fund_id: int, user_id: int) -> Optional[Fund]:
        """Get fund by ID for specific user"""
        return self.db.query(Fund).filter(
            and_(
                Fund.id == fund_id,
                Fund.user_id == user_id
            )
        ).first()
    
    def update(self, fund_id: int, user_id: int, update_data: Dict[str, Any]) -> Optional[Fund]:
        """Update fund information"""
        try:
            fund = self.db.query(Fund).filter(
                and_(
                    Fund.id == fund_id,
                    Fund.user_id == user_id
                )
            ).first()
            
            if not fund:
                return None
            
            for key, value in update_data.items():
                if hasattr(fund, key):
                    setattr(fund, key, value)
            
            fund.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(fund)
            return fund
        except Exception as e:
            self.db.rollback()
            raise e