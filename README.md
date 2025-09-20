# 🚀 PE Dashboard with Alpha Vantage Integration

A production-ready Private Equity Dashboard that integrates with Alpha Vantage API for real-time market data and financial analytics.

## ✨ Features

- **Real-time Market Data**: Integration with Alpha Vantage API
- **Financial Calculations**: IRR, MOIC, DPI, TVPI, RVPI calculations
- **Portfolio Analytics**: Comprehensive portfolio performance metrics
- **Sector Analysis**: Industry-wise performance breakdown
- **Deal Pipeline**: Track active investments and deal flow
- **Reports**: Generate and manage investment reports
- **Rate Limiting**: Robust API rate limiting and error handling
- **Data Caching**: Local data storage with refresh capabilities

## 🏗️ Architecture

### Backend (FastAPI)
- **Database**: SQLite with SQLAlchemy ORM
- **API**: FastAPI with automatic documentation
- **Market Data**: Alpha Vantage API integration
- **Calculations**: SciPy-based financial calculations
- **Authentication**: JWT-based authentication

### Frontend (Next.js 14)
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with custom design system
- **Components**: Radix UI with shadcn/ui
- **Charts**: Recharts for data visualization
- **API Client**: TypeScript API client with error handling

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Alpha Vantage API key (free at [alphavantage.co](https://www.alphavantage.co/support/#api-key))

### 1. Start the Backend

```bash
# Make the script executable (if not already done)
chmod +x start-backend.sh

# Start the backend server
./start-backend.sh
```

The backend will start on `http://localhost:8000`

**Important**: Update the `.env` file in the backend directory with your Alpha Vantage API key:
```env
ALPHAVANTAGE_API_KEY=your_actual_api_key_here
```

### 2. Start the Frontend

```bash
# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start on `http://localhost:3000`

### 3. Ingest Sample Data

1. Open the dashboard at `http://localhost:3000`
2. Click "Ingest Sample Data" to populate the dashboard with:
   - Microsoft Corp (MSFT) - $1M invested on 2018-01-02
   - Johnson & Johnson (JNJ) - $750K invested on 2019-03-01
   - JPMorgan Chase (JPM) - $500K invested on 2020-06-15

## 📊 API Endpoints

### Data Ingestion
- `POST /api/v1/ingest/companies` - Ingest companies and create deals

### Core Data Access
- `GET /api/v1/deals` - Get all deals
- `GET /api/v1/deals/{deal_id}/kpis` - Get deal KPIs
- `GET /api/v1/portfolio/kpis` - Get portfolio KPIs
- `GET /api/v1/analytics/sectors` - Get sector analytics
- `GET /api/v1/reports/recent` - Get recent reports

### Data Refresh
- `POST /api/v1/refresh/market-data` - Refresh market data
- `POST /api/v1/refresh/deal/{deal_id}` - Refresh specific deal

## 🔧 Configuration

### Backend Environment Variables
```env
ALPHAVANTAGE_API_KEY=your_api_key_here
API_RATE_LIMIT=5
DATABASE_URL=sqlite:///./pe_dashboard.db
SECRET_KEY=your-secret-key-here
```

### Frontend Environment Variables
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📈 Financial Metrics

The dashboard calculates comprehensive financial metrics:

- **IRR (Internal Rate of Return)**: Annualized return rate
- **MOIC (Multiple on Invested Capital)**: Total value / invested capital
- **DPI (Distributed to Paid-In)**: Distributions / invested capital
- **TVPI (Total Value to Paid-In)**: (Distributions + current value) / invested capital
- **RVPI (Residual Value to Paid-In)**: Current value / invested capital

## 🛡️ Error Handling

The system includes robust error handling for:
- Alpha Vantage API rate limits (5 calls/minute)
- Network timeouts and retries
- Invalid ticker symbols
- Missing market data
- Database transaction failures
- Financial calculation edge cases

## 📱 Dashboard Tabs

1. **Portfolio Overview**: Key metrics, portfolio value trends, sector allocation
2. **Deal Pipeline**: Active deals, pipeline metrics, deal activity
3. **Performance**: Fund performance vs benchmark, IRR trends, fund comparison
4. **Analytics**: Sector performance, risk-return analysis, investment thesis
5. **Reports**: Report generation, templates, recent reports

## 🔄 Data Flow

1. **Ingestion**: Companies are ingested with investment details
2. **Market Data**: Alpha Vantage provides historical and current prices
3. **Calculations**: Financial metrics are calculated using SciPy
4. **Storage**: Data is stored in SQLite with proper relationships
5. **Display**: Frontend consumes API and displays real-time data

## 🧪 Testing

Test the system with the provided sample data or add your own companies:

```typescript
const customCompanies = [
  {
    name: "Apple Inc",
    ticker: "AAPL",
    sector: "Technology",
    currency: "USD",
    invest_date: "2020-01-15",
    invest_amount: 2000000
  }
];
```

## 📚 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## 🚨 Important Notes

- **API Key Required**: You must have a valid Alpha Vantage API key
- **Rate Limits**: The system respects Alpha Vantage's 5 calls/minute limit
- **Data Caching**: Market data is cached locally to minimize API calls
- **Weekend Handling**: The system handles weekends/holidays by finding the nearest trading day

## 🛠️ Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload
```

### Frontend Development
```bash
npm run dev
```

### Database Management
The SQLite database is automatically created. To reset:
```bash
rm backend/pe_dashboard.db
# Restart the backend to recreate
```

## 📄 License

This project is for demonstration purposes. Please ensure you comply with Alpha Vantage's terms of service when using their API.
# Cagliolo-Ventures
A Private Equity Dashboard
