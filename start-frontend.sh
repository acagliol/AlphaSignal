#!/bin/bash
# PE Dashboard Frontend Startup Script

echo "🌐 Starting PE Dashboard Frontend..."
echo "📱 Dashboard will be available at: http://localhost:3000"
echo ""

cd "$(dirname "$0")"
npm run dev
