#!/bin/bash
# PE Dashboard Backend Startup Script

echo "🚀 Starting PE Dashboard Backend..."
echo "📊 API will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""

cd "$(dirname "$0")"
./venv/bin/python backend/run.py
