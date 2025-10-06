"""
Financial calculation services for PE Dashboard
"""

import numpy as np
from scipy.optimize import fsolve
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from .models import Company, Deal, CashFlow, MarketData, FlowType, DealStatus
from .schemas import DealKPIs, PortfolioKPIs, SectorAnalytics

logger = logging.getLogger(__name__)

class FinancialCalculator:
    """Robust financial calculations with error handling"""
    
    @staticmethod
    def calculate_xirr(cashflows: List[Dict[str, Any]], guess: float = 0.1) -> Optional[float]:
        """
        Calculate XIRR using Newton-Raphson method with fallback to scipy optimization
        """
        if len(cashflows) < 2:
            return None
        
        try:
            # Sort cashflows by date
            sorted_cashflows = sorted(cashflows, key=lambda x: x['date'])
            
            # Extract dates and amounts
            dates = [cf['date'] for cf in sorted_cashflows]
            amounts = [cf['amount'] for cf in sorted_cashflows]
            
            # Convert dates to years from first date
            first_date = dates[0]
            years = [(d - first_date).days / 365.25 for d in dates]
            
            # Define the NPV function
            def npv(rate):
                return sum(amount / (1 + rate) ** year for amount, year in zip(amounts, years))
            
            # Try Newton-Raphson first
            try:
                # Use scipy's fsolve for more robust solving
                result = fsolve(npv, guess, full_output=True)
                if result[2] == 1:  # Success
                    irr = result[0][0]
                    # Validate the result
                    if abs(npv(irr)) < 1e-6 and -0.99 < irr < 10:  # Reasonable IRR range
                        return float(irr)
            except Exception as e:
                logger.warning(f"Newton-Raphson failed: {e}")
            
            # Fallback: binary search
            low, high = -0.99, 10.0
            for _ in range(100):  # Max 100 iterations
                mid = (low + high) / 2
                npv_mid = npv(mid)
                
                if abs(npv_mid) < 1e-6:
                    return float(mid)
                elif npv_mid > 0:
                    low = mid
                else:
                    high = mid
                
                if high - low < 1e-10:
                    break
            
            return None
            
        except Exception as e:
            logger.error(f"XIRR calculation failed: {e}")
            return None
    
    @staticmethod
    def calculate_moic(total_distributions: float, current_value: float, total_invested: float) -> Optional[float]:
        """Calculate Multiple on Invested Capital (MOIC)"""
        try:
            if total_invested <= 0:
                return None
            return (total_distributions + current_value) / total_invested
        except Exception as e:
            logger.error(f"MOIC calculation failed: {e}")
            return None
    
    @staticmethod
    def calculate_dpi(total_distributions: float, total_invested: float) -> Optional[float]:
        """Calculate Distributed to Paid-In (DPI)"""
        try:
            if total_invested <= 0:
                return None
            return total_distributions / total_invested
        except Exception as e:
            logger.error(f"DPI calculation failed: {e}")
            return None
    
    @staticmethod
    def calculate_tvpi(total_distributions: float, current_value: float, total_invested: float) -> Optional[float]:
        """Calculate Total Value to Paid-In (TVPI)"""
        try:
            if total_invested <= 0:
                return None
            return (total_distributions + current_value) / total_invested
        except Exception as e:
            logger.error(f"TVPI calculation failed: {e}")
            return None
    
    @staticmethod
    def calculate_rvpi(current_value: float, total_invested: float) -> Optional[float]:
        """Calculate Residual Value to Paid-In (RVPI)"""
        try:
            if total_invested <= 0:
                return None
            return current_value / total_invested
        except Exception as e:
            logger.error(f"RVPI calculation failed: {e}")
            return None

class DealService:
    """Service for deal-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.calculator = FinancialCalculator()
    
    async def create_deal(self, company_id: int, invest_date: date, invest_amount: float,
                         shares: float, nav_latest: Optional[float] = None, fund_id: Optional[int] = None) -> Deal:
        """Create a new deal with initial cashflow"""
        try:
            # Create the deal
            deal = Deal(
                company_id=company_id,
                fund_id=fund_id,  # Add fund_id support
                invest_date=invest_date,
                invest_amount=invest_amount,
                shares=shares,
                nav_latest=nav_latest,
                status=DealStatus.ACTIVE
            )
            
            self.db.add(deal)
            self.db.flush()  # Get the deal ID
            
            # Create initial contribution cashflow
            contribution = CashFlow(
                deal_id=deal.id,
                date=invest_date,
                amount=-invest_amount,  # Negative for contribution
                flow_type=FlowType.CONTRIBUTION,
                description=f"Initial investment in {deal.company.name if deal.company else 'company'}"
            )
            
            self.db.add(contribution)
            self.db.commit()
            
            return deal
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create deal: {e}")
            raise
    
    async def update_nav(self, deal_id: int, current_price: float) -> Deal:
        """Update NAV for a deal"""
        try:
            deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                raise ValueError(f"Deal {deal_id} not found")
            
            # Update NAV
            deal.nav_latest = current_price
            deal.updated_at = datetime.utcnow()
            
            # Create NAV cashflow for IRR calculation
            nav_cashflow = CashFlow(
                deal_id=deal_id,
                date=date.today(),
                amount=deal.shares * current_price,
                flow_type=FlowType.NAV,
                description=f"NAV update at ${current_price:.2f} per share"
            )
            
            self.db.add(nav_cashflow)
            self.db.commit()
            
            return deal
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update NAV for deal {deal_id}: {e}")
            raise
    
    async def add_dividend(self, deal_id: int, dividend_date: date, dividend_per_share: float) -> CashFlow:
        """Add dividend distribution to a deal"""
        try:
            deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                raise ValueError(f"Deal {deal_id} not found")
            
            total_dividend = deal.shares * dividend_per_share
            
            dividend_cashflow = CashFlow(
                deal_id=deal_id,
                date=dividend_date,
                amount=total_dividend,
                flow_type=FlowType.DISTRIBUTION,
                description=f"Dividend distribution: ${dividend_per_share:.4f} per share"
            )
            
            self.db.add(dividend_cashflow)
            self.db.commit()
            
            return dividend_cashflow
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add dividend for deal {deal_id}: {e}")
            raise
    
    async def get_deal_kpis(self, deal_id: int, as_of_date: Optional[date] = None) -> DealKPIs:
        """Calculate KPIs for a specific deal"""
        try:
            if as_of_date is None:
                as_of_date = date.today()
            
            # Get deal with company info
            deal = self.db.query(Deal).join(Company).filter(Deal.id == deal_id).first()
            if not deal:
                raise ValueError(f"Deal {deal_id} not found")
            
            # Get all cashflows up to as_of_date
            cashflows = self.db.query(CashFlow).filter(
                and_(
                    CashFlow.deal_id == deal_id,
                    CashFlow.date <= as_of_date
                )
            ).order_by(CashFlow.date).all()
            
            # Calculate current value
            current_value = deal.shares * (deal.nav_latest or 0)
            
            # Calculate distributions
            total_distributions = sum(
                cf.amount for cf in cashflows 
                if cf.flow_type == FlowType.DISTRIBUTION
            )
            
            # Calculate unrealized and realized gains
            unrealized_gain = current_value - deal.invest_amount
            realized_gain = total_distributions
            
            # Prepare cashflows for IRR calculation
            irr_cashflows = []
            for cf in cashflows:
                if cf.flow_type == FlowType.CONTRIBUTION:
                    irr_cashflows.append({
                        'date': cf.date,
                        'amount': cf.amount  # Already negative
                    })
                elif cf.flow_type == FlowType.DISTRIBUTION:
                    irr_cashflows.append({
                        'date': cf.date,
                        'amount': cf.amount  # Positive
                    })
            
            # Add current NAV as final cashflow for IRR
            if deal.nav_latest:
                irr_cashflows.append({
                    'date': as_of_date,
                    'amount': current_value
                })
            
            # Calculate IRR
            irr = self.calculator.calculate_xirr(irr_cashflows)
            
            # Calculate other metrics
            moic = self.calculator.calculate_moic(total_distributions, current_value, deal.invest_amount)
            dpi = self.calculator.calculate_dpi(total_distributions, deal.invest_amount)
            tvpi = self.calculator.calculate_tvpi(total_distributions, current_value, deal.invest_amount)
            rvpi = self.calculator.calculate_rvpi(current_value, deal.invest_amount)
            
            return DealKPIs(
                deal_id=deal.id,
                company_name=deal.company.name,
                ticker=deal.company.ticker,
                invest_date=deal.invest_date,
                invest_amount=deal.invest_amount,
                current_value=current_value,
                shares=deal.shares,
                current_price=deal.nav_latest or 0,
                irr=irr,
                moic=moic,
                dpi=dpi,
                tvpi=tvpi,
                rvpi=rvpi,
                total_distributions=total_distributions,
                unrealized_gain=unrealized_gain,
                realized_gain=realized_gain,
                as_of_date=as_of_date
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate KPIs for deal {deal_id}: {e}")
            raise

class PortfolioService:
    """Service for portfolio-level operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.calculator = FinancialCalculator()
    
    async def get_portfolio_kpis(self, fund_id: Optional[int] = None, as_of_date: Optional[date] = None) -> PortfolioKPIs:
        """Calculate portfolio-level KPIs, optionally filtered by fund"""
        try:
            if as_of_date is None:
                as_of_date = date.today()

            # Get all active deals, optionally filtered by fund
            query = self.db.query(Deal).join(Company).filter(
                Deal.status == DealStatus.ACTIVE
            )

            if fund_id is not None:
                query = query.filter(Deal.fund_id == fund_id)

            deals = query.all()
            
            if not deals:
                return PortfolioKPIs(
                    total_invested=0,
                    total_current_value=0,
                    total_distributions=0,
                    total_unrealized_gain=0,
                    total_realized_gain=0,
                    active_deals=0,
                    realized_deals=0,
                    as_of_date=as_of_date
                )
            
            # Calculate totals
            total_invested = sum(deal.invest_amount for deal in deals)
            total_current_value = sum(deal.shares * (deal.nav_latest or 0) for deal in deals)
            
            # Get all distributions
            total_distributions = 0
            for deal in deals:
                distributions = self.db.query(CashFlow).filter(
                    and_(
                        CashFlow.deal_id == deal.id,
                        CashFlow.flow_type == FlowType.DISTRIBUTION,
                        CashFlow.date <= as_of_date
                    )
                ).all()
                total_distributions += sum(cf.amount for cf in distributions)
            
            # Calculate gains
            total_unrealized_gain = total_current_value - total_invested
            total_realized_gain = total_distributions
            
            # Count deals
            active_deals = len([d for d in deals if d.status == DealStatus.ACTIVE])
            realized_deals = len(self.db.query(Deal).filter(Deal.status == DealStatus.REALIZED).all())
            
            # Calculate portfolio IRR
            portfolio_irr = None
            if total_invested > 0:
                # Create portfolio-level cashflows
                portfolio_cashflows = []
                
                # Add all contributions
                for deal in deals:
                    contributions = self.db.query(CashFlow).filter(
                        and_(
                            CashFlow.deal_id == deal.id,
                            CashFlow.flow_type == FlowType.CONTRIBUTION,
                            CashFlow.date <= as_of_date
                        )
                    ).all()
                    portfolio_cashflows.extend([
                        {'date': cf.date, 'amount': cf.amount} for cf in contributions
                    ])
                
                # Add all distributions
                for deal in deals:
                    distributions = self.db.query(CashFlow).filter(
                        and_(
                            CashFlow.deal_id == deal.id,
                            CashFlow.flow_type == FlowType.DISTRIBUTION,
                            CashFlow.date <= as_of_date
                        )
                    ).all()
                    portfolio_cashflows.extend([
                        {'date': cf.date, 'amount': cf.amount} for cf in distributions
                    ])
                
                # Add current NAV
                portfolio_cashflows.append({
                    'date': as_of_date,
                    'amount': total_current_value
                })
                
                portfolio_irr = self.calculator.calculate_xirr(portfolio_cashflows)
            
            # Calculate other portfolio metrics
            portfolio_moic = self.calculator.calculate_moic(total_distributions, total_current_value, total_invested)
            portfolio_dpi = self.calculator.calculate_dpi(total_distributions, total_invested)
            portfolio_tvpi = self.calculator.calculate_tvpi(total_distributions, total_current_value, total_invested)
            portfolio_rvpi = self.calculator.calculate_rvpi(total_current_value, total_invested)
            
            return PortfolioKPIs(
                total_invested=total_invested,
                total_current_value=total_current_value,
                total_distributions=total_distributions,
                portfolio_irr=portfolio_irr,
                portfolio_moic=portfolio_moic,
                portfolio_dpi=portfolio_dpi,
                portfolio_tvpi=portfolio_tvpi,
                portfolio_rvpi=portfolio_rvpi,
                total_unrealized_gain=total_unrealized_gain,
                total_realized_gain=total_realized_gain,
                active_deals=active_deals,
                realized_deals=realized_deals,
                as_of_date=as_of_date
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate portfolio KPIs: {e}")
            raise
    
    async def get_sector_analytics(self, as_of_date: Optional[date] = None) -> List[SectorAnalytics]:
        """Calculate sector-wise analytics"""
        try:
            if as_of_date is None:
                as_of_date = date.today()
            
            # Get all deals with company info
            deals = self.db.query(Deal).join(Company).filter(
                Deal.status == DealStatus.ACTIVE
            ).all()
            
            # Group by sector
            sector_data = {}
            for deal in deals:
                sector = deal.company.sector
                if sector not in sector_data:
                    sector_data[sector] = {
                        'deals': [],
                        'total_invested': 0,
                        'total_current_value': 0,
                        'total_distributions': 0
                    }
                
                sector_data[sector]['deals'].append(deal)
                sector_data[sector]['total_invested'] += deal.invest_amount
                sector_data[sector]['total_current_value'] += deal.shares * (deal.nav_latest or 0)
                
                # Get distributions for this deal
                distributions = self.db.query(CashFlow).filter(
                    and_(
                        CashFlow.deal_id == deal.id,
                        CashFlow.flow_type == FlowType.DISTRIBUTION,
                        CashFlow.date <= as_of_date
                    )
                ).all()
                sector_data[sector]['total_distributions'] += sum(cf.amount for cf in distributions)
            
            # Calculate analytics for each sector
            analytics = []
            for sector, data in sector_data.items():
                deals = data['deals']
                total_invested = data['total_invested']
                total_current_value = data['total_current_value']
                total_distributions = data['total_distributions']
                
                # Calculate sector IRR
                sector_irr = None
                if total_invested > 0:
                    sector_cashflows = []
                    
                    # Add contributions
                    for deal in deals:
                        contributions = self.db.query(CashFlow).filter(
                            and_(
                                CashFlow.deal_id == deal.id,
                                CashFlow.flow_type == FlowType.CONTRIBUTION,
                                CashFlow.date <= as_of_date
                            )
                        ).all()
                        sector_cashflows.extend([
                            {'date': cf.date, 'amount': cf.amount} for cf in contributions
                        ])
                    
                    # Add distributions
                    for deal in deals:
                        distributions = self.db.query(CashFlow).filter(
                            and_(
                                CashFlow.deal_id == deal.id,
                                CashFlow.flow_type == FlowType.DISTRIBUTION,
                                CashFlow.date <= as_of_date
                            )
                        ).all()
                        sector_cashflows.extend([
                            {'date': cf.date, 'amount': cf.amount} for cf in distributions
                        ])
                    
                    # Add current NAV
                    sector_cashflows.append({
                        'date': as_of_date,
                        'amount': total_current_value
                    })
                    
                    sector_irr = self.calculator.calculate_xirr(sector_cashflows)
                
                # Calculate other metrics
                avg_irr = sector_irr
                avg_moic = self.calculator.calculate_moic(total_distributions, total_current_value, total_invested)
                unrealized_gain = total_current_value - total_invested
                realized_gain = total_distributions
                
                analytics.append(SectorAnalytics(
                    sector=sector,
                    deal_count=len(deals),
                    total_invested=total_invested,
                    total_current_value=total_current_value,
                    avg_irr=avg_irr,
                    avg_moic=avg_moic,
                    total_distributions=total_distributions,
                    unrealized_gain=unrealized_gain,
                    realized_gain=realized_gain
                ))
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to calculate sector analytics: {e}")
            raise