#!/usr/bin/env python3
"""
Simple script to run the PE Dashboard backend server
"""
import sys
import os

# Add parent directory to path so backend can be imported as a package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
