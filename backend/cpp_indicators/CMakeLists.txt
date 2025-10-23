cmake_minimum_required(VERSION 3.15)
project(cpp_indicators)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python and pybind11
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Create Python module
pybind11_add_module(cpp_indicators indicators.cpp)

# Optimization flags
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(cpp_indicators PRIVATE -O3 -march=native -ffast-math)
elseif(MSVC)
    target_compile_options(cpp_indicators PRIVATE /O2)
endif()

# Installation
install(TARGETS cpp_indicators LIBRARY DESTINATION .)
