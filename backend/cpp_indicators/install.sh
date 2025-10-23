#!/bin/bash

echo "🚀 Installing C++ Technical Indicators Module"
echo "=============================================="

# Check for C++ compiler
if ! command -v g++ &> /dev/null && ! command -v clang++ &> /dev/null; then
    echo "❌ Error: No C++ compiler found"
    echo "Install with: sudo apt install build-essential (Linux)"
    echo "           or: xcode-select --install (macOS)"
    exit 1
fi

# Check for Python development headers
if ! python3 -c "import sysconfig" &> /dev/null; then
    echo "❌ Error: Python development headers not found"
    echo "Install with: sudo apt install python3-dev (Linux)"
    exit 1
fi

# Install pybind11
echo "📦 Installing pybind11..."
pip install pybind11

# Build C++ module
echo "🔨 Building C++ module..."
python setup.py build_ext --inplace

# Test import
echo "🧪 Testing module..."
python -c "import cpp_indicators; print('✅ C++ module loaded successfully!')" || {
    echo "❌ Module import failed"
    exit 1
}

# Run benchmark
echo "📊 Running performance benchmark..."
python -c "import sys; sys.path.insert(0, '../services/technical_indicators'); from cpp_wrapper import benchmark_indicators; benchmark_indicators(100)"

echo ""
echo "✅ Installation complete!"
echo "Module location: $(pwd)/cpp_indicators.so"
