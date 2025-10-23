from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
import sys

ext_modules = [
    Pybind11Extension(
        "cpp_indicators",
        ["indicators.cpp"],
        extra_compile_args=["-O3", "-march=native", "-ffast-math"] if sys.platform != "win32" else ["/O2"],
        language="c++"
    ),
]

setup(
    name="cpp_indicators",
    version="1.0.0",
    author="AlphaSignal",
    description="High-performance technical indicators",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.8",
)
