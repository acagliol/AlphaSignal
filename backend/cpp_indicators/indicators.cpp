#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>
#include <cmath>
#include <algorithm>

namespace py = pybind11;

// RSI Calculator (Vectorized)
py::array_t<double> calculate_rsi(py::array_t<double> prices, int period = 14) {
    auto buf = prices.request();
    double *ptr = static_cast<double *>(buf.ptr);
    size_t n = buf.shape[0];

    std::vector<double> rsi(n, 0.0);
    std::vector<double> gains(n, 0.0);
    std::vector<double> losses(n, 0.0);

    // Calculate price changes
    for (size_t i = 1; i < n; ++i) {
        double change = ptr[i] - ptr[i-1];
        if (change > 0) {
            gains[i] = change;
        } else {
            losses[i] = -change;
        }
    }

    // Initial average (Simple Moving Average)
    double avg_gain = 0.0, avg_loss = 0.0;
    for (int i = 1; i <= period; ++i) {
        avg_gain += gains[i];
        avg_loss += losses[i];
    }
    avg_gain /= period;
    avg_loss /= period;

    // Calculate RSI using Wilder's smoothing
    for (size_t i = period; i < n; ++i) {
        avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period;
        avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period;

        if (avg_loss == 0.0) {
            rsi[i] = 100.0;
        } else {
            double rs = avg_gain / avg_loss;
            rsi[i] = 100.0 - (100.0 / (1.0 + rs));
        }
    }

    return py::array_t<double>(n, rsi.data());
}

// MACD Calculator
struct MACDResult {
    py::array_t<double> macd;
    py::array_t<double> signal;
    py::array_t<double> histogram;
};

MACDResult calculate_macd(
    py::array_t<double> prices,
    int fast_period = 12,
    int slow_period = 26,
    int signal_period = 9
) {
    auto buf = prices.request();
    double *ptr = static_cast<double *>(buf.ptr);
    size_t n = buf.shape[0];

    std::vector<double> ema_fast(n, 0.0);
    std::vector<double> ema_slow(n, 0.0);
    std::vector<double> macd(n, 0.0);
    std::vector<double> signal(n, 0.0);
    std::vector<double> histogram(n, 0.0);

    // Calculate EMA multipliers
    double alpha_fast = 2.0 / (fast_period + 1);
    double alpha_slow = 2.0 / (slow_period + 1);
    double alpha_signal = 2.0 / (signal_period + 1);

    // Initialize EMAs
    ema_fast[0] = ptr[0];
    ema_slow[0] = ptr[0];

    // Calculate EMAs
    for (size_t i = 1; i < n; ++i) {
        ema_fast[i] = alpha_fast * ptr[i] + (1 - alpha_fast) * ema_fast[i-1];
        ema_slow[i] = alpha_slow * ptr[i] + (1 - alpha_slow) * ema_slow[i-1];
        macd[i] = ema_fast[i] - ema_slow[i];
    }

    // Calculate signal line (EMA of MACD)
    signal[slow_period] = macd[slow_period];
    for (size_t i = slow_period + 1; i < n; ++i) {
        signal[i] = alpha_signal * macd[i] + (1 - alpha_signal) * signal[i-1];
        histogram[i] = macd[i] - signal[i];
    }

    MACDResult result;
    result.macd = py::array_t<double>(n, macd.data());
    result.signal = py::array_t<double>(n, signal.data());
    result.histogram = py::array_t<double>(n, histogram.data());

    return result;
}

// Bollinger Bands
struct BollingerBands {
    py::array_t<double> upper;
    py::array_t<double> middle;
    py::array_t<double> lower;
};

BollingerBands calculate_bollinger_bands(
    py::array_t<double> prices,
    int period = 20,
    double num_std = 2.0
) {
    auto buf = prices.request();
    double *ptr = static_cast<double *>(buf.ptr);
    size_t n = buf.shape[0];

    std::vector<double> middle(n, 0.0);
    std::vector<double> upper(n, 0.0);
    std::vector<double> lower(n, 0.0);

    // Calculate rolling mean and std
    for (size_t i = period - 1; i < n; ++i) {
        double sum = 0.0;
        for (int j = 0; j < period; ++j) {
            sum += ptr[i - j];
        }
        double mean = sum / period;
        middle[i] = mean;

        // Calculate standard deviation
        double variance = 0.0;
        for (int j = 0; j < period; ++j) {
            double diff = ptr[i - j] - mean;
            variance += diff * diff;
        }
        double std = std::sqrt(variance / period);

        upper[i] = mean + num_std * std;
        lower[i] = mean - num_std * std;
    }

    BollingerBands result;
    result.upper = py::array_t<double>(n, upper.data());
    result.middle = py::array_t<double>(n, middle.data());
    result.lower = py::array_t<double>(n, lower.data());

    return result;
}

// Rolling Correlation (Fast)
py::array_t<double> rolling_correlation(
    py::array_t<double> x,
    py::array_t<double> y,
    int window = 20
) {
    auto buf_x = x.request();
    auto buf_y = y.request();
    double *ptr_x = static_cast<double *>(buf_x.ptr);
    double *ptr_y = static_cast<double *>(buf_y.ptr);
    size_t n = buf_x.shape[0];

    std::vector<double> corr(n, 0.0);

    for (size_t i = window - 1; i < n; ++i) {
        double sum_x = 0.0, sum_y = 0.0;
        double sum_xx = 0.0, sum_yy = 0.0, sum_xy = 0.0;

        for (int j = 0; j < window; ++j) {
            double vx = ptr_x[i - j];
            double vy = ptr_y[i - j];

            sum_x += vx;
            sum_y += vy;
            sum_xx += vx * vx;
            sum_yy += vy * vy;
            sum_xy += vx * vy;
        }

        double mean_x = sum_x / window;
        double mean_y = sum_y / window;

        double cov = (sum_xy / window) - (mean_x * mean_y);
        double std_x = std::sqrt((sum_xx / window) - (mean_x * mean_x));
        double std_y = std::sqrt((sum_yy / window) - (mean_y * mean_y));

        if (std_x > 0 && std_y > 0) {
            corr[i] = cov / (std_x * std_y);
        }
    }

    return py::array_t<double>(n, corr.data());
}

// Pybind11 module definition
PYBIND11_MODULE(cpp_indicators, m) {
    m.doc() = "High-performance technical indicators in C++";

    m.def("calculate_rsi", &calculate_rsi,
          "Calculate RSI (Relative Strength Index)",
          py::arg("prices"), py::arg("period") = 14);

    m.def("calculate_macd", &calculate_macd,
          "Calculate MACD",
          py::arg("prices"),
          py::arg("fast_period") = 12,
          py::arg("slow_period") = 26,
          py::arg("signal_period") = 9);

    m.def("calculate_bollinger_bands", &calculate_bollinger_bands,
          "Calculate Bollinger Bands",
          py::arg("prices"),
          py::arg("period") = 20,
          py::arg("num_std") = 2.0);

    m.def("rolling_correlation", &rolling_correlation,
          "Calculate rolling correlation",
          py::arg("x"), py::arg("y"), py::arg("window") = 20);

    // Struct bindings
    py::class_<MACDResult>(m, "MACDResult")
        .def_readonly("macd", &MACDResult::macd)
        .def_readonly("signal", &MACDResult::signal)
        .def_readonly("histogram", &MACDResult::histogram);

    py::class_<BollingerBands>(m, "BollingerBands")
        .def_readonly("upper", &BollingerBands::upper)
        .def_readonly("middle", &BollingerBands::middle)
        .def_readonly("lower", &BollingerBands::lower);
}
