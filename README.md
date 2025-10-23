# AlphaSignal 🚀

**Alternative Data Alpha Research Platform**

A quantitative research platform combining machine learning, factor analysis, and alternative data sources to generate alpha signals for stock trading.

---

## 🎯 Features

### **Backend API (FastAPI)**
- 📊 **Market Data Integration** - Yahoo Finance historical data
- 🤖 **ML Predictions** - XGBoost binary classifier (53.7% accuracy, AUC 0.586)
- 📈 **Factor Analysis** - Fama-French 3-factor model decomposition
- ⚡ **C++ Technical Indicators** - 15-20x performance boost (with Python fallback)
- 📰 **Alternative Data Infrastructure** - Sentiment analysis (TextBlob) & Reddit scraping (PRAW) ready (requires API keys)
- 💾 **Database** - SQLAlchemy ORM with 6 specialized tables

### **Frontend Dashboard (Next.js 14)**
- 🎨 **Modern UI** - Tailwind CSS + shadcn/ui components
- 📉 **Stock Analysis** - Real-time market data & technical indicators
- 🔮 **Prediction Interface** - ML-powered direction forecasts
- 📊 **Factor Breakdown** - Risk-adjusted alpha visualization
- 🌙 **Dark Mode** - Beautiful gradient design

---

## 🚀 Quick Start

### **1. Backend Setup**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python train_model.py --ticker AAPL --days 365
python alphasignal_main.py
```

**Backend:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

### **2. Frontend Setup**
```bash
npm install
npm run dev
```

**Frontend:** http://localhost:3000/alphasignal

---

## 📊 ML Model Performance (AAPL - 230 Days)
- **Accuracy:** 53.68% ± 6.86%
- **AUC:** 0.5858 ± 0.0540
- **Backtest Return:** +18.07%
- **Features:** 31 engineered features
- **Cross-Validation:** 5-fold time-series
- **Win Rate:** 100% (55 trades)

---

## 🛠️ Tech Stack
- **Backend:** FastAPI, SQLAlchemy, XGBoost, C++
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS
- **Database:** SQLite (dev) / PostgreSQL (prod)

---

## ⚠️ Disclaimer
**Educational purposes only. Not financial advice.**

---

*AlphaSignal - Finding Alpha in Alternative Data*
