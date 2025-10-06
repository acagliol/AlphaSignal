"""
Setup script to compile C++ extension for financial calculations
"""

from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
import sys

ext_modules = [
    Pybind11Extension(
        "finance_calc",
        ["finance_calc.cpp"],
        define_macros=[("USE_PYBIND11", "1")],
        cxx_std=17,
        extra_compile_args=[
            "-O3",  # Maximum optimization
            "-march=native",  # Optimize for current CPU
            "-ffast-math",  # Aggressive math optimizations
            "-fopenmp" if sys.platform != "darwin" else "",  # OpenMP for parallel processing
        ],
        extra_link_args=[
            "-fopenmp" if sys.platform != "darwin" else "",
        ],
    ),
]

setup(
    name="finance_calc",
    version="1.0.0",
    author="PE Dashboard",
    description="High-performance financial calculations in C++",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.8",
)
