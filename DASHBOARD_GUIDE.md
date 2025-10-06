# 🚀 PE DASHBOARD - Professional Dark Theme with Real-Time Data

## ✨ What's New

Your PE Dashboard has been **completely transformed** with:

### 🎨 Professional Dark Mode Design
- **Sleek black background** (#0a0a0a) with dark cards (#0f0f0f)
- **Neon green accents** (#00ff9d) for highlights and positive metrics
- **Glowing hover effects** with smooth transitions
- **Professional typography** with uppercase labels and proper spacing

### 📊 Real-Time Data Integration
- **Live API integration** - All data fetched from FastAPI backend
- **Real stock prices** from Alpha Vantage API
- **Calculated metrics**: IRR, MOIC, DPI, TVPI, RVPI
- **Live dividend tracking** and distribution calculations

### 📈 Professional Charts with Recharts
- **Interactive Pie Charts** for sector allocation
- **Bar Charts** for performance metrics
- **Real-time updates** when data is ingested
- **Dark-themed tooltips** with proper styling

---

## 🚀 How to Run

### Start Both Servers:

**Terminal 1 - Backend:**
```bash
./start-backend.sh
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

### Or Use VS Code:
Press `F5` → Select "Full Stack: Backend + Frontend"

---

## 📱 Access the Dashboard

- **Dashboard:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🎯 How to Use

### Step 1: Load Sample Data

1. Open http://localhost:3000
2. Click the **"🚀 LOAD PORTFOLIO DATA"** button
3. Wait 30-60 seconds for Alpha Vantage API to fetch real data
4. Dashboard will automatically refresh with real-time data

### Sample Portfolio:
- **Microsoft (MSFT)**: $1M invested on 2018-01-02
- **Johnson & Johnson (JNJ)**: $750K invested on 2019-03-01
- **JPMorgan Chase (JPM)**: $500K invested on 2020-06-15

### Step 2: Explore the Tabs

#### 📊 Portfolio Overview
- **6 Key Metrics Cards**:
  - Total Invested
  - Current Value
  - Total Return % and $
  - IRR (Internal Rate of Return)
  - MOIC (Multiple on Invested Capital)
  - Total Distributions

- **Sector Allocation Pie Chart**: Visual breakdown by sector
- **Sector Performance List**: Detailed metrics per sector with returns

#### 💼 Deal Pipeline
- **Individual Deal Cards** for each investment
- **Real-time pricing** with current stock prices
- **Performance Metrics**: IRR, MOIC, Shares, Distributions
- **Status Indicators**: Active/Realized with color coding

#### 📈 Performance
- **5 Performance Metrics**: IRR, MOIC, DPI, TVPI, RVPI
- **Bar Chart Visualization**: Compare all metrics at once
- **Large metric cards** with clear values

#### 🔍 Analytics
- **Sector-by-Sector Breakdown**
- **Investment vs Current Value** comparison
- **Average IRR per sector**
- **Deal count per sector**

#### 📄 Reports
- Placeholder for future reporting functionality

---

## 🎨 Design Features

### Color Scheme:
- **Background**: `#0a0a0a` (Deep Black)
- **Cards**: `#0f0f0f` (Dark Gray)
- **Primary/Accent**: `#00ff9d` (Neon Green)
- **Text**: `#ffffff` (White), `#888` (Gray)
- **Positive**: `#00ff9d` (Green)
- **Negative**: `#ff4444` (Red)

### Interactive Elements:
- **Hover Effects**: Cards glow with neon green border
- **Smooth Transitions**: 0.3s ease on all interactions
- **Shadow Effects**: Subtle glows on hover
- **Responsive Grid**: Auto-fit layouts for all screen sizes

---

## 💡 Real Data Flow

```
User clicks "Load Data"
    ↓
Frontend calls: POST /api/v1/ingest/companies
    ↓
Backend fetches from Alpha Vantage:
  - Historical price on investment date
  - Current price
  - Dividend history
    ↓
Backend calculates:
  - IRR using SciPy
  - MOIC, DPI, TVPI, RVPI
  - Sector aggregations
    ↓
Frontend displays real-time data in charts
```

---

## 📊 Metrics Explained

### IRR (Internal Rate of Return)
- Annualized return rate accounting for time value of money
- Calculated using cash flows (investment + dividends)
- **Formula**: Uses SciPy's IRR calculation with actual dates

### MOIC (Multiple on Invested Capital)
- Total value returned divided by amount invested
- **Formula**: (Current Value + Distributions) / Invested Amount

### DPI (Distributed to Paid-In)
- Cash returned to investors divided by invested capital
- **Formula**: Total Distributions / Invested Amount

### TVPI (Total Value to Paid-In)
- Total value (realized + unrealized) divided by invested capital
- **Formula**: (Current Value + Distributions) / Invested Amount

### RVPI (Residual Value to Paid-In)
- Remaining investment value divided by invested capital
- **Formula**: Current Value / Invested Amount

---

## 🔄 Refreshing Data

The dashboard automatically refreshes when you:
1. Ingest new data
2. Navigate between tabs (re-fetches on mount)

To manually refresh market prices:
- Use the API endpoint: `POST /api/v1/refresh/market-data`
- Or restart the backend and re-ingest

---

## 🛠️ Customization

### Adding Your Own Stocks:

Edit `app/lib/api.ts` and modify `sampleCompanies`:

```typescript
export const sampleCompanies: CompanyIngest[] = [
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

Then click "Load Portfolio Data" to ingest.

### Changing Colors:

Search and replace these hex codes:
- `#00ff9d` → Your accent color
- `#0a0a0a` → Your background color
- `#0f0f0f` → Your card color

---

## 📈 Performance Tips

1. **API Rate Limits**: Alpha Vantage free tier = 5 calls/minute
2. **Data Caching**: Backend caches market data in SQLite
3. **Loading States**: All tabs show loading spinners during fetch
4. **Error Handling**: Red error messages with clear descriptions

---

## 🎯 Next Steps

1. ✅ **Run the dashboard** and load sample data
2. ✅ **Explore all tabs** to see real calculations
3. **Add your own stocks** by modifying the sample data
4. **Customize colors** to match your brand
5. **Export reports** (coming soon)

---

## 🔑 Key Files Modified

- `app/page.tsx` - Main dashboard with dark theme
- `app/tabs/portfolio-tab.tsx` - Portfolio overview with Recharts
- `app/tabs/deals-tab.tsx` - Deal pipeline with real data
- `app/tabs/performance-tab.tsx` - Performance metrics
- `app/tabs/analytics-tab.tsx` - Sector analytics
- `app/components/data-ingestion.tsx` - Dark themed ingestion button

---

## 🎉 You're All Set!

Your professional PE Dashboard is ready to track real investments with live market data. The dark theme with neon green accents gives it a modern, high-tech feel perfect for serious investment tracking.

**Happy Investing! 📊💰**
