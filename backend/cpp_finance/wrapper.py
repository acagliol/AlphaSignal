"""
Python wrapper for C++ financial calculations
Provides fallback to pure Python if C++ module is not available
"""

from typing import List, Dict, Any, Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)

# Try to import C++ module
try:
    import finance_calc
    USE_CPP_FINANCE = True
    logger.info("✓ Using optimized C++ financial calculations (10-50x faster)")
except ImportError:
    USE_CPP_FINANCE = False
    logger.warning("⚠ C++ finance module not found, using Python fallback (slower)")
    logger.warning("  To enable C++ acceleration, run: cd backend/cpp_finance && pip install pybind11 && python setup.py install")


def calculate_xirr_cpp(cashflows: List[Dict[str, Any]], guess: float = 0.1) -> Optional[float]:
    """
    Calculate XIRR using C++ implementation

    Args:
        cashflows: List of dicts with 'date' and 'amount' keys
        guess: Initial guess for IRR

    Returns:
        IRR as decimal (e.g., 0.23 for 23%) or None if calculation fails
    """
    if len(cashflows) < 2:
        return None

    try:
        # Sort cashflows by date
        sorted_cashflows = sorted(cashflows, key=lambda x: x['date'])
        first_date = sorted_cashflows[0]['date']

        # Convert to C++ CashFlow objects
        cpp_cashflows = []
        for cf in sorted_cashflows:
            days_from_start = (cf['date'] - first_date).days
            cpp_cashflows.append(finance_calc.CashFlow(days_from_start, cf['amount']))

        # Calculate using C++ (much faster)
        irr = finance_calc.calculate_xirr(cpp_cashflows, guess)

        # Check if result is valid (not NaN)
        if irr != irr:  # NaN check
            return None

        return float(irr)

    except Exception as e:
        logger.error(f"C++ XIRR calculation failed: {e}")
        return None


def calculate_xirr_python(cashflows: List[Dict[str, Any]], guess: float = 0.1) -> Optional[float]:
    """
    Python fallback implementation for XIRR
    Uses scipy for optimization
    """
    import numpy as np
    from scipy.optimize import fsolve

    if len(cashflows) < 2:
        return None

    try:
        sorted_cashflows = sorted(cashflows, key=lambda x: x['date'])
        dates = [cf['date'] for cf in sorted_cashflows]
        amounts = [cf['amount'] for cf in sorted_cashflows]

        first_date = dates[0]
        years = [(d - first_date).days / 365.25 for d in dates]

        def npv(rate):
            return sum(amount / (1 + rate) ** year for amount, year in zip(amounts, years))

        # Use scipy's fsolve
        result = fsolve(npv, guess, full_output=True)
        if result[2] == 1:
            irr = result[0][0]
            if abs(npv(irr)) < 1e-6 and -0.99 < irr < 10:
                return float(irr)

        return None

    except Exception as e:
        logger.error(f"Python XIRR calculation failed: {e}")
        return None


def calculate_xirr(cashflows: List[Dict[str, Any]], guess: float = 0.1) -> Optional[float]:
    """
    Calculate XIRR using C++ if available, otherwise fallback to Python

    Args:
        cashflows: List of dicts with 'date' and 'amount' keys
        guess: Initial guess for IRR

    Returns:
        IRR as decimal or None
    """
    if USE_CPP_FINANCE:
        result = calculate_xirr_cpp(cashflows, guess)
        if result is not None:
            return result
        # Fallback to Python if C++ fails
        logger.warning("C++ XIRR failed, falling back to Python")

    return calculate_xirr_python(cashflows, guess)


def calculate_moic(total_distributions: float, current_value: float, total_invested: float) -> Optional[float]:
    """Calculate MOIC using C++ if available"""
    if total_invested <= 0:
        return None

    if USE_CPP_FINANCE:
        try:
            result = finance_calc.calculate_moic(total_distributions, current_value, total_invested)
            return None if result != result else float(result)  # Check for NaN
        except Exception:
            pass

    # Python fallback
    return (total_distributions + current_value) / total_invested


def calculate_dpi(total_distributions: float, total_invested: float) -> Optional[float]:
    """Calculate DPI using C++ if available"""
    if total_invested <= 0:
        return None

    if USE_CPP_FINANCE:
        try:
            result = finance_calc.calculate_dpi(total_distributions, total_invested)
            return None if result != result else float(result)
        except Exception:
            pass

    # Python fallback
    return total_distributions / total_invested


def calculate_tvpi(total_distributions: float, current_value: float, total_invested: float) -> Optional[float]:
    """Calculate TVPI using C++ if available"""
    if total_invested <= 0:
        return None

    if USE_CPP_FINANCE:
        try:
            result = finance_calc.calculate_tvpi(total_distributions, current_value, total_invested)
            return None if result != result else float(result)
        except Exception:
            pass

    # Python fallback
    return (total_distributions + current_value) / total_invested


def calculate_rvpi(current_value: float, total_invested: float) -> Optional[float]:
    """Calculate RVPI using C++ if available"""
    if total_invested <= 0:
        return None

    if USE_CPP_FINANCE:
        try:
            result = finance_calc.calculate_rvpi(current_value, total_invested)
            return None if result != result else float(result)
        except Exception:
            pass

    # Python fallback
    return current_value / total_invested


# Export indicator for debugging
def is_using_cpp() -> bool:
    """Check if C++ module is being used"""
    return USE_CPP_FINANCE


def get_performance_info() -> dict:
    """Get information about performance optimizations"""
    return {
        "cpp_enabled": USE_CPP_FINANCE,
        "expected_speedup": "10-50x" if USE_CPP_FINANCE else "1x (baseline)",
        "backend": "C++ (optimized)" if USE_CPP_FINANCE else "Python (scipy)",
    }
