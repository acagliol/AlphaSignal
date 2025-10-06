cmake_minimum_required(VERSION 3.15)
project(finance_calc)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optimization flags
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -ffast-math")
endif()

# Find Python
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Create the extension
pybind11_add_module(finance_calc finance_calc.cpp)

# Link with OpenMP if available
find_package(OpenMP)
if(OpenMP_CXX_FOUND)
    target_link_libraries(finance_calc PRIVATE OpenMP::OpenMP_CXX)
endif()

# Install
install(TARGETS finance_calc DESTINATION .)
