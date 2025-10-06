/**
 * High-performance financial calculations in C++
 * Used for IRR, NPV, and other computationally intensive metrics
 */

#include <vector>
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include <limits>

struct CashFlow {
    double days_from_start;  // Days from first cashflow
    double amount;
};

/**
 * Calculate NPV (Net Present Value) given a rate
 * Formula: NPV = Σ(CF_i / (1 + r)^t_i)
 */
double calculate_npv(const std::vector<CashFlow>& cashflows, double rate) {
    double npv = 0.0;

    for (const auto& cf : cashflows) {
        double years = cf.days_from_start / 365.25;
        npv += cf.amount / std::pow(1.0 + rate, years);
    }

    return npv;
}

/**
 * Calculate derivative of NPV with respect to rate (for Newton-Raphson)
 * Formula: dNPV/dr = Σ(-t_i * CF_i / (1 + r)^(t_i + 1))
 */
double calculate_npv_derivative(const std::vector<CashFlow>& cashflows, double rate) {
    double derivative = 0.0;

    for (const auto& cf : cashflows) {
        double years = cf.days_from_start / 365.25;
        derivative += -years * cf.amount / std::pow(1.0 + rate, years + 1.0);
    }

    return derivative;
}

/**
 * Calculate XIRR using optimized Newton-Raphson method with fallback to binary search
 * Returns IRR or NaN if calculation fails
 */
double calculate_xirr(const std::vector<CashFlow>& cashflows, double initial_guess = 0.1) {
    const int MAX_NEWTON_ITERATIONS = 50;
    const int MAX_BINARY_ITERATIONS = 100;
    const double TOLERANCE = 1e-7;
    const double MIN_RATE = -0.999;
    const double MAX_RATE = 10.0;

    if (cashflows.size() < 2) {
        return std::numeric_limits<double>::quiet_NaN();
    }

    // Try Newton-Raphson method first (faster convergence)
    double rate = initial_guess;

    for (int i = 0; i < MAX_NEWTON_ITERATIONS; ++i) {
        double npv = calculate_npv(cashflows, rate);

        // Check convergence
        if (std::abs(npv) < TOLERANCE) {
            // Validate result is in reasonable range
            if (rate > MIN_RATE && rate < MAX_RATE) {
                return rate;
            }
        }

        double derivative = calculate_npv_derivative(cashflows, rate);

        // Avoid division by zero
        if (std::abs(derivative) < 1e-10) {
            break;
        }

        // Newton-Raphson step: x_new = x_old - f(x)/f'(x)
        double new_rate = rate - npv / derivative;

        // Clamp to reasonable bounds
        new_rate = std::max(MIN_RATE, std::min(MAX_RATE, new_rate));

        // Check for convergence
        if (std::abs(new_rate - rate) < TOLERANCE) {
            rate = new_rate;
            npv = calculate_npv(cashflows, rate);
            if (std::abs(npv) < TOLERANCE) {
                return rate;
            }
            break;
        }

        rate = new_rate;
    }

    // Fallback to binary search (more robust but slower)
    double low = MIN_RATE;
    double high = MAX_RATE;

    // Check if solution exists in range
    double npv_low = calculate_npv(cashflows, low);
    double npv_high = calculate_npv(cashflows, high);

    if (npv_low * npv_high > 0) {
        // No sign change, no solution in range
        return std::numeric_limits<double>::quiet_NaN();
    }

    for (int i = 0; i < MAX_BINARY_ITERATIONS; ++i) {
        double mid = (low + high) / 2.0;
        double npv_mid = calculate_npv(cashflows, mid);

        if (std::abs(npv_mid) < TOLERANCE) {
            return mid;
        }

        if (npv_mid * npv_low < 0) {
            high = mid;
            npv_high = npv_mid;
        } else {
            low = mid;
            npv_low = npv_mid;
        }

        if (high - low < TOLERANCE) {
            return (low + high) / 2.0;
        }
    }

    return std::numeric_limits<double>::quiet_NaN();
}

/**
 * Calculate MOIC (Multiple on Invested Capital)
 * Formula: MOIC = (Total Distributions + Current Value) / Total Invested
 */
double calculate_moic(double total_distributions, double current_value, double total_invested) {
    if (total_invested <= 0) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    return (total_distributions + current_value) / total_invested;
}

/**
 * Calculate DPI (Distributed to Paid-In)
 * Formula: DPI = Total Distributions / Total Invested
 */
double calculate_dpi(double total_distributions, double total_invested) {
    if (total_invested <= 0) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    return total_distributions / total_invested;
}

/**
 * Calculate TVPI (Total Value to Paid-In)
 * Formula: TVPI = (Total Distributions + Current Value) / Total Invested
 */
double calculate_tvpi(double total_distributions, double current_value, double total_invested) {
    if (total_invested <= 0) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    return (total_distributions + current_value) / total_invested;
}

/**
 * Calculate RVPI (Residual Value to Paid-In)
 * Formula: RVPI = Current Value / Total Invested
 */
double calculate_rvpi(double current_value, double total_invested) {
    if (total_invested <= 0) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    return current_value / total_invested;
}

// Python bindings using pybind11
#ifdef USE_PYBIND11
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(finance_calc, m) {
    m.doc() = "High-performance financial calculations for PE Dashboard";

    py::class_<CashFlow>(m, "CashFlow")
        .def(py::init<double, double>())
        .def_readwrite("days_from_start", &CashFlow::days_from_start)
        .def_readwrite("amount", &CashFlow::amount);

    m.def("calculate_xirr", &calculate_xirr,
          "Calculate XIRR using optimized Newton-Raphson with binary search fallback",
          py::arg("cashflows"),
          py::arg("initial_guess") = 0.1);

    m.def("calculate_npv", &calculate_npv,
          "Calculate Net Present Value",
          py::arg("cashflows"),
          py::arg("rate"));

    m.def("calculate_moic", &calculate_moic,
          "Calculate Multiple on Invested Capital",
          py::arg("total_distributions"),
          py::arg("current_value"),
          py::arg("total_invested"));

    m.def("calculate_dpi", &calculate_dpi,
          "Calculate Distributed to Paid-In",
          py::arg("total_distributions"),
          py::arg("total_invested"));

    m.def("calculate_tvpi", &calculate_tvpi,
          "Calculate Total Value to Paid-In",
          py::arg("total_distributions"),
          py::arg("current_value"),
          py::arg("total_invested"));

    m.def("calculate_rvpi", &calculate_rvpi,
          "Calculate Residual Value to Paid-In",
          py::arg("current_value"),
          py::arg("total_invested"));
}
#endif
