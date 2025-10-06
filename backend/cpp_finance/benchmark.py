#!/usr/bin/env python3
"""
Benchmark script to compare C++ vs Python financial calculations
"""

import time
import sys
from datetime import date, timedelta
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, '..')

try:
    from cpp_finance.wrapper import (
        calculate_xirr_cpp, calculate_xirr_python,
        is_using_cpp, get_performance_info
    )
except ImportError:
    print("Error: Could not import wrapper. Make sure you're in the backend directory.")
    sys.exit(1)


def generate_test_cashflows(num_cashflows: int) -> List[Dict[str, Any]]:
    """Generate test cashflows for benchmarking"""
    cashflows = []
    start_date = date(2020, 1, 1)

    # Initial investment
    cashflows.append({
        'date': start_date,
        'amount': -1000000
    })

    # Quarterly distributions
    for i in range(1, num_cashflows - 1):
        cashflows.append({
            'date': start_date + timedelta(days=90 * i),
            'amount': 25000
        })

    # Final exit
    cashflows.append({
        'date': start_date + timedelta(days=90 * (num_cashflows - 1)),
        'amount': 1500000
    })

    return cashflows


def benchmark_xirr(num_iterations: int = 100, num_cashflows: int = 20):
    """Benchmark XIRR calculation"""
    print(f"\n{'='*60}")
    print(f"Benchmarking XIRR Calculation")
    print(f"Iterations: {num_iterations}, Cashflows per iteration: {num_cashflows}")
    print(f"{'='*60}\n")

    cashflows = generate_test_cashflows(num_cashflows)

    # Benchmark Python implementation
    print("Testing Python implementation...")
    start = time.time()
    for _ in range(num_iterations):
        result_py = calculate_xirr_python(cashflows)
    time_py = time.time() - start
    print(f"✓ Python Time: {time_py:.4f}s ({time_py/num_iterations*1000:.2f}ms per calculation)")
    print(f"  Result: {result_py*100:.2f}%" if result_py else "  Result: None")

    # Benchmark C++ implementation if available
    if is_using_cpp():
        print("\nTesting C++ implementation...")
        start = time.time()
        for _ in range(num_iterations):
            result_cpp = calculate_xirr_cpp(cashflows)
        time_cpp = time.time() - start
        print(f"✓ C++ Time: {time_cpp:.4f}s ({time_cpp/num_iterations*1000:.2f}ms per calculation)")
        print(f"  Result: {result_cpp*100:.2f}%" if result_cpp else "  Result: None")

        # Calculate speedup
        speedup = time_py / time_cpp
        print(f"\n{'='*60}")
        print(f"⚡ SPEEDUP: {speedup:.1f}x faster with C++")
        print(f"{'='*60}")

        # Verify results match
        if result_py and result_cpp:
            diff = abs(result_py - result_cpp)
            if diff < 1e-6:
                print(f"✓ Results match (difference: {diff:.10f})")
            else:
                print(f"⚠ Results differ by {diff:.10f}")
    else:
        print("\n⚠ C++ module not available. Install with: python setup.py install")


def benchmark_portfolio(num_deals: int = 100):
    """Benchmark portfolio-level calculations"""
    print(f"\n{'='*60}")
    print(f"Benchmarking Portfolio Calculation ({num_deals} deals)")
    print(f"{'='*60}\n")

    # Generate test data for multiple deals
    all_cashflows = []
    for i in range(num_deals):
        cashflows = generate_test_cashflows(8)  # 8 cashflows per deal
        all_cashflows.append(cashflows)

    # Benchmark Python
    print("Testing Python implementation...")
    start = time.time()
    results_py = []
    for cashflows in all_cashflows:
        irr = calculate_xirr_python(cashflows)
        results_py.append(irr)
    time_py = time.time() - start
    print(f"✓ Python Time: {time_py:.4f}s")

    # Benchmark C++ if available
    if is_using_cpp():
        print("\nTesting C++ implementation...")
        start = time.time()
        results_cpp = []
        for cashflows in all_cashflows:
            irr = calculate_xirr_cpp(cashflows)
            results_cpp.append(irr)
        time_cpp = time.time() - start
        print(f"✓ C++ Time: {time_cpp:.4f}s")

        speedup = time_py / time_cpp
        print(f"\n{'='*60}")
        print(f"⚡ PORTFOLIO SPEEDUP: {speedup:.1f}x faster")
        print(f"   This means refreshing {num_deals} deals takes {time_cpp:.2f}s instead of {time_py:.2f}s")
        print(f"{'='*60}")


def main():
    """Run all benchmarks"""
    print("\n" + "="*60)
    print("PE DASHBOARD - C++ FINANCE MODULE BENCHMARK")
    print("="*60)

    # Print performance info
    info = get_performance_info()
    print(f"\nCurrent Configuration:")
    print(f"  Backend: {info['backend']}")
    print(f"  Expected Speedup: {info['expected_speedup']}")

    if not is_using_cpp():
        print("\n⚠ WARNING: C++ module not loaded!")
        print("  Install with: cd backend/cpp_finance && python setup.py install")
        print("  Falling back to Python-only benchmark...\n")

    # Run benchmarks
    benchmark_xirr(num_iterations=100, num_cashflows=20)
    benchmark_portfolio(num_deals=100)

    print("\n" + "="*60)
    print("Benchmark Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
