# AlphaSignal - Quantitative Alpha Research Platform

A sophisticated quantitative research platform powered by machine learning, alternative data, and advanced technical analysis. AlphaSignal delivers ML-powered stock predictions with comprehensive market analysis.

---

## 🎯 Key Features

### Machine Learning Predictions
- **54% Accuracy** on 5-day price direction predictions using XGBoost
- **2.77% Low Variance** across time-series cross-validation folds
- **Multi-Stock Training** on 8 major tech stocks (2,416+ samples)
- **70+ Engineered Features** including momentum, volatility, trend-following
- **Feature Selection** (top 40 features) with StandardScaler normalization
- **Time-Series CV** to prevent look-ahead bias

### Technical Analysis
- **C++ Accelerated Indicators** (15-20x faster than Python via pybind11)
- RSI, MACD, Bollinger Bands, Moving Averages (SMA 20/50/200)
- Trend strength analysis and momentum indicators
- Volatility regimes and pattern recognition
- 52-week high/low distance tracking

### User Interface
- **Interactive Stock Selector** with 12 popular NASDAQ stocks
- Real-time technical indicator visualization
- ML prediction confidence scores and probability distributions
- Clean, modern dark theme interface built with Next.js
- Responsive design for desktop and mobile

---

## 📊 Performance Metrics

- **Prediction Accuracy**: 54% (5-day horizon)
- **AUC Score**: 0.595
- **Backtest Results**: 19% return over 3 years (89.8% win rate)
- **Training Data**: 2,416 samples from 8 stocks
- **Features**: 70+ engineered technical indicators
- **Model**: XGBoost with feature selection and scaling

---

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **FastAPI** REST API with automatic OpenAPI documentation
- **SQLAlchemy** ORM with PostgreSQL/SQLite support
- **XGBoost** ML model with sklearn preprocessing
- **C++ Integration** via pybind11 for performance-critical indicators
- **yfinance** for real-time market data
- **Pydantic** for data validation

### Frontend (Next.js/React)
- **Next.js 14** with App Router
- **React** with TypeScript
- **Tailwind CSS** for styling
- **Radix UI** for accessible components
- **Recharts** for data visualization

---

## ⚡ Quick Start

### Prerequisites
- **Node.js** (v18+)
- **Python** (3.12+)
- **npm** or **yarn**

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/acagliol/alphasignal.git
cd alphasignal

# 2. Install frontend dependencies
npm install

# 3. Set up the backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Set up environment variables (optional for basic usage)
cp .env.example .env
# Edit .env with your API keys if you want news/social sentiment

# 5. Run the application (both frontend & backend)
npm run dev

# Or run separately:
# Backend: npm run dev:backend
# Frontend: npm run dev:frontend
```

The application will be available at:
- **Frontend**: http://localhost:3000/alphasignal
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🤖 Model Training

### Train on Single Stock
```bash
cd backend
source venv/bin/activate
python train_model.py --ticker AAPL --days 1095
```

### Train on Multiple Stocks (Recommended)
```bash
cd backend
source venv/bin/activate
python train_multi_stock.py
```

The multi-stock training provides better generalization by learning patterns from 8 different stocks (AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, AMD).

---

## 📈 Usage

1. **Select a Stock**: Choose from 12 popular NASDAQ stocks or enter a custom ticker
2. **View Analysis**: See real-time technical indicators, market data, and returns
3. **Generate Prediction**: Click "Generate Prediction" to get ML-powered 5-day direction forecast
4. **Analyze Confidence**: Review probability distributions and confidence scores
5. **Make Decisions**: Use predictions as one signal in your trading strategy

**Note**: Predictions are for informational purposes only and should be combined with other analysis methods.

---

## 🛠️ Tech Stack

**Backend**
- Python 3.12, FastAPI, SQLAlchemy
- XGBoost, scikit-learn, pandas, numpy
- C++ (pybind11), yfinance
- PostgreSQL/SQLite

**Frontend**
- Next.js 14, React, TypeScript
- Tailwind CSS, Radix UI
- Recharts for visualizations

**ML Pipeline**
- Feature Engineering: 70+ indicators
- Model: XGBoost with feature selection
- Validation: Time-series cross-validation
- Preprocessing: StandardScaler

---

## 📁 Project Structure

```
alphasignal/
├── app/                    # Next.js frontend
│   ├── alphasignal/       # Main dashboard page
│   └── layout.tsx         # Root layout
├── backend/               # Python backend
│   ├── api/v1/           # API endpoints
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   │   ├── ml_engine/   # ML training & prediction
│   │   └── technical_indicators/  # C++ indicators
│   ├── train_model.py   # Single-stock training
│   ├── train_multi_stock.py  # Multi-stock training
│   └── alphasignal_main.py   # FastAPI app
└── components/           # Reusable UI components
```

---

## 🔑 API Endpoints

- `GET /api/v1/demo/analyze/{ticker}` - Get stock analysis
- `POST /api/v1/predictions/{ticker}/predict` - Generate ML prediction
- `GET /api/v1/predictions/{ticker}` - Get historical predictions
- `GET /api/v1/predictions/{ticker}/accuracy` - Get prediction accuracy
- `GET /docs` - Interactive API documentation

---

## ⚠️ Disclaimer

This project is for educational and research purposes only. Stock market predictions are inherently uncertain. Do not use this as the sole basis for investment decisions. Always conduct thorough research and consult with financial professionals.

---

## 📝 License

MIT License

---

**AlphaSignal** - Finding Alpha in Alternative Data
