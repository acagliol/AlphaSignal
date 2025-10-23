# 🚀 AlphaSignal - Alternative Data Alpha Research Platform

**Project Evolution**: PE Dashboard → AlphaSignal Quantitative Research Platform
**Target Audience**: Quant Finance, Data Science, ML Engineering Roles
**Timeline**: 6 Phases (Phases 1-3 Complete)
**Tech Stack**: Next.js 14, FastAPI, XGBoost, SQLAlchemy, C++

---

## 🎯 PROJECT VISION

**What You're Building:**
A quantitative research platform combining machine learning, factor analysis, and alternative data sources to generate alpha signals for stock trading.

**End Result:**
A portfolio project demonstrating quant finance knowledge, ML engineering, full-stack development, and data engineering — perfect for fintech/quant recruiting.

**Current Status**: ✅ 50% Complete (Backend infrastructure done, frontend needs work)

---

## 📊 CURRENT STATUS OVERVIEW

### ✅ COMPLETE: Phases 1-3 (Core Infrastructure)

**Backend (FastAPI):**
- ✅ Market data integration (Yahoo Finance via yfinance)
- ✅ Technical indicators (RSI, MACD, Bollinger Bands, Volatility)
- ✅ Database models (6 specialized tables: MarketData, TechnicalIndicators, Predictions, FactorExposures, SentimentData, SocialSignals)
- ✅ C++ technical indicators module (15-20x performance boost with Python fallback)
- ✅ Demo API endpoint (`/api/v1/demo/analyze/{ticker}`)
- ✅ Health checks, logging, CORS, error handling

**Frontend (Next.js 14):**
- ✅ Modern dark theme with gradient design
- ✅ Stock analysis page with market data display
- ✅ Technical indicators visualization
- ✅ Returns calculation (1-day, 5-day, 20-day)
- ✅ Responsive UI with Tailwind CSS + shadcn/ui

**Infrastructure:**
- ✅ SQLAlchemy ORM with proper relationships
- ✅ Pydantic schemas for validation
- ✅ FastAPI automatic OpenAPI docs
- ✅ Environment configuration
- ✅ Professional logging

---

## 🔨 IN PROGRESS: Phase 4 (ML Predictions)

**Status**: Backend 95% Complete, Frontend 0% Complete

### Backend (DONE ✅)

**Files Created:**
- `backend/services/ml_engine/feature_engineering.py` - 31 engineered features
- `backend/services/ml_engine/model_training.py` - XGBoost trainer with cross-validation
- `backend/services/ml_engine/backtester.py` - Strategy backtesting
- `backend/api/v1/predictions.py` - ML predictions API
- `backend/train_model.py` - Model training script

**API Endpoints:**
- ✅ `GET /api/v1/predictions/{ticker}` - Get historical predictions
- ✅ `POST /api/v1/predictions/{ticker}/predict` - Generate new prediction
- ✅ `GET /api/v1/predictions/{ticker}/accuracy` - Accuracy metrics

**ML Features:**
- ✅ Price-based: returns, volatility, momentum
- ✅ Technical: RSI, MACD, Bollinger Bands
- ✅ Volume: volume changes, volume trends
- ✅ Rolling statistics: mean, std, min, max
- ✅ Lagged features: previous day returns

**Model Performance (AAPL Example):**
- Accuracy: 54.21% ± 7.81%
- AUC: 0.591
- Backtest Return: +17.58%

### Frontend (TODO ❌)

**What Needs to Be Built:**
1. **Prediction Card Component**
   - Show direction forecast (UP/DOWN)
   - Display probability percentages
   - Confidence indicator (high/medium/low)
   - Visual gauge/meter for confidence

2. **Historical Predictions Chart**
   - Timeline of past predictions
   - Accuracy over time
   - Correct vs incorrect indicators

3. **Model Metrics Display**
   - Overall accuracy
   - Precision/Recall
   - Confusion matrix visualization
   - Backtest performance

4. **Prediction Controls**
   - "Generate Prediction" button
   - Model selection (if multiple models)
   - Feature importance display

**Estimated Time**: 1-2 days

---

## 🔨 IN PROGRESS: Phase 5 (Factor Analysis)

**Status**: Backend 100% Complete, Frontend 0% Complete

### Backend (DONE ✅)

**Files Created:**
- `backend/services/factor_analysis/fama_french.py` - FF3 factor model
- `backend/api/v1/factors.py` - Factor analysis API
- `backend/test_factor_analysis.py` - Validation tests

**API Endpoints:**
- ✅ `GET /api/v1/factors/{ticker}` - Get latest factor exposure
- ✅ `POST /api/v1/factors/{ticker}/analyze` - Run FF3 analysis
- ✅ `GET /api/v1/factors/{ticker}/rolling` - Rolling factor exposures

**Factor Analysis Features:**
- ✅ Fama-French 3-Factor regression
- ✅ Alpha calculation (risk-adjusted excess return)
- ✅ Beta exposures (Market, Size, Value)
- ✅ Statistical significance testing
- ✅ R-squared and interpretation
- ✅ Rolling window analysis

### Frontend (TODO ❌)

**What Needs to Be Built:**
1. **Factor Exposure Card**
   - Alpha (annualized %)
   - Beta values with visual bars
   - Statistical significance indicators
   - R-squared interpretation

2. **Alpha Breakdown**
   - Market beta contribution
   - Size factor contribution
   - Value factor contribution
   - True alpha (unexplained returns)

3. **Rolling Factor Chart**
   - Time-series of beta exposures
   - Line chart showing how factors change
   - Highlight significant periods

4. **Factor Analysis Controls**
   - "Analyze Factors" button
   - Time period selector (60/120/252 days)
   - Rolling window size selector

**Estimated Time**: 1-2 days

---

## ⏳ PLANNED: Phase 6 (Sentiment & Social Signals)

**Status**: Backend Infrastructure Ready, API Keys Required

### Backend (90% Ready, Needs API Keys)

**Files Created:**
- `backend/services/sentiment/analyzer.py` - Sentiment analysis service
- `backend/services/sentiment/reddit_scraper.py` - Reddit data scraper

**What Works:**
- ✅ News article sentiment scoring
- ✅ Reddit post aggregation
- ✅ Social signal metrics
- ✅ Database models for sentiment data

**What's Blocked:**
- ❌ Need `NEWS_API_KEY` from [newsapi.org](https://newsapi.org/)
- ❌ Need `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` from [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)

**API Endpoints (Currently Commented Out):**
```python
# TODO Phase 6 - Sentiment & Social API (requires API keys):
#   from api.v1 import sentiment
#   app.include_router(sentiment.router, prefix="/api/v1/sentiment", tags=["Sentiment"])
```

### Frontend (TODO ❌)

**What Needs to Be Built:**
1. **Sentiment Score Gauge**
   - Overall sentiment (-1 to +1)
   - Color-coded visualization
   - Source breakdown (news vs social)

2. **News Feed Card**
   - Recent news headlines
   - Sentiment scores per article
   - Click to read full article

3. **Social Signals Card**
   - Reddit mentions count
   - Trending discussions
   - Sentiment trend over time

4. **Sentiment Charts**
   - Historical sentiment trend
   - Correlation with price movements
   - Volume of mentions over time

**Estimated Time**: 2-3 days (after API keys obtained)

---

## 🎯 6-PHASE DEVELOPMENT PLAN

### ✅ Phase 1: Core Backend Infrastructure (COMPLETE)
**Goal**: Build FastAPI backend with database and basic data ingestion

**Delivered:**
- FastAPI application with OpenAPI docs
- SQLAlchemy models (6 tables)
- Pydantic schemas for validation
- Database initialization
- Health check endpoints
- Environment configuration
- CORS middleware

**Files**: `backend/alphasignal_main.py`, `backend/models/`, `backend/schemas/`, `backend/database.py`, `backend/config.py`

---

### ✅ Phase 2: Market Data & Technical Indicators (COMPLETE)
**Goal**: Integrate market data and calculate technical indicators

**Delivered:**
- Yahoo Finance integration (yfinance)
- Market data fetching and caching
- Technical indicators (RSI, MACD, BB, Volatility)
- C++ performance optimization (15-20x speedup)
- Python fallback for portability
- Demo API endpoint

**Files**: `backend/services/data_ingestion/market_data.py`, `backend/services/technical_indicators/`, `backend/cpp_indicators/`, `backend/api/v1/demo.py`

**Performance**: C++ indicators process 252 days in ~5ms vs ~100ms in Python

---

### ✅ Phase 3: Basic Frontend Dashboard (COMPLETE)
**Goal**: Create Next.js dashboard with modern UI

**Delivered:**
- Next.js 14 app with App Router
- Dark theme with gradient design
- Market data display cards
- Technical indicators visualization
- Returns calculation (1d, 5d, 20d)
- Responsive layout (Tailwind + shadcn/ui)

**Files**: `app/alphasignal/page.tsx`, `components/ui/`, `lib/`

**URLs**: Frontend on `http://localhost:3000/alphasignal`, Backend on `http://localhost:8000`

---

### 🔨 Phase 4: ML Predictions (50% COMPLETE)
**Goal**: Implement machine learning for stock direction forecasting

**Current Status**:
- ✅ Backend: Feature engineering (31 features)
- ✅ Backend: XGBoost model training
- ✅ Backend: Backtesting framework
- ✅ Backend: Prediction API endpoints
- ✅ CLI: `train_model.py` script
- ❌ Frontend: Prediction UI (NOT STARTED)

**Next Steps** (1-2 days):
1. Create prediction card component
2. Add "Generate Prediction" button
3. Display probability gauges
4. Show historical accuracy
5. Visualize model metrics

**Acceptance Criteria**:
- [ ] User can generate predictions from UI
- [ ] Confidence displayed with visual gauge
- [ ] Historical predictions shown in timeline
- [ ] Model accuracy metrics displayed
- [ ] Feature importance visualization

---

### 🔨 Phase 5: Factor Analysis (50% COMPLETE)
**Goal**: Implement Fama-French 3-factor model for risk decomposition

**Current Status**:
- ✅ Backend: FF3 regression implementation
- ✅ Backend: Alpha and beta calculations
- ✅ Backend: Statistical significance tests
- ✅ Backend: Rolling factor exposures
- ✅ Backend: Factor API endpoints
- ❌ Frontend: Factor analysis UI (NOT STARTED)

**Next Steps** (1-2 days):
1. Create factor exposure card
2. Add alpha breakdown visualization
3. Show beta bars (market, size, value)
4. Display rolling factor chart
5. Add "Analyze Factors" button

**Acceptance Criteria**:
- [ ] User can run factor analysis from UI
- [ ] Alpha displayed with significance indicator
- [ ] Beta exposures shown visually
- [ ] Rolling factors displayed as time-series
- [ ] Interpretation text generated

---

### ⏳ Phase 6: Sentiment & Social Signals (PLANNED)
**Goal**: Integrate alternative data sources for sentiment analysis

**Prerequisites**:
- [ ] Get News API key from newsapi.org
- [ ] Get Reddit API credentials
- [ ] Add API keys to `.env` file

**Tasks** (2-3 days):
1. Uncomment sentiment API routes
2. Test news scraping
3. Test Reddit data collection
4. Build sentiment UI cards
5. Create news feed component
6. Add social signals visualization
7. Implement sentiment trend charts

**Acceptance Criteria**:
- [ ] News sentiment fetched and stored
- [ ] Reddit mentions tracked
- [ ] Sentiment displayed on dashboard
- [ ] Historical sentiment trends shown
- [ ] Correlation with price analyzed

---

## 📁 PROJECT STRUCTURE

```
pe-dashboard/
├── app/                              # Next.js Frontend
│   ├── alphasignal/
│   │   └── page.tsx                  # Main dashboard (Phase 3 ✅)
│   ├── page.tsx                       # Redirect to /alphasignal
│   └── layout.tsx
│
├── backend/                           # FastAPI Backend
│   ├── alphasignal_main.py            # Main API app (Phase 1 ✅)
│   ├── config.py                      # Configuration (Phase 1 ✅)
│   ├── database.py                    # DB setup (Phase 1 ✅)
│   ├── train_model.py                 # ML training script (Phase 4 ✅)
│   │
│   ├── models/                        # SQLAlchemy Models (Phase 1 ✅)
│   │   ├── alpha_market_data.py
│   │   ├── sentiment_data.py
│   │   ├── social_signals.py
│   │   ├── predictions.py
│   │   ├── factor_exposures.py
│   │   └── technical_indicators.py
│   │
│   ├── schemas/                       # Pydantic Schemas (Phase 1 ✅)
│   │   ├── prediction_schema.py
│   │   └── factor_schema.py
│   │
│   ├── api/v1/                        # API Routes
│   │   ├── demo.py                    # Demo endpoint (Phase 2 ✅)
│   │   ├── predictions.py             # ML API (Phase 4 ✅)
│   │   └── factors.py                 # Factor API (Phase 5 ✅)
│   │
│   ├── services/
│   │   ├── data_ingestion/
│   │   │   └── market_data.py         # Market data (Phase 2 ✅)
│   │   ├── technical_indicators/
│   │   │   └── cpp_wrapper.py         # C++ indicators (Phase 2 ✅)
│   │   ├── ml_engine/
│   │   │   ├── feature_engineering.py # Features (Phase 4 ✅)
│   │   │   ├── model_training.py      # XGBoost (Phase 4 ✅)
│   │   │   └── backtester.py          # Backtesting (Phase 4 ✅)
│   │   ├── factor_analysis/
│   │   │   └── fama_french.py         # FF3 model (Phase 5 ✅)
│   │   └── sentiment/
│   │       ├── analyzer.py            # Sentiment (Phase 6 🔜)
│   │       └── reddit_scraper.py      # Reddit (Phase 6 🔜)
│   │
│   └── cpp_indicators/                # C++ Optimization (Phase 2 ✅)
│       ├── indicators.cpp
│       ├── CMakeLists.txt
│       └── setup.py
│
├── components/                        # shadcn/ui Components (Phase 3 ✅)
│   └── ui/
│
├── lib/                               # Utilities (Phase 3 ✅)
│
├── README.md                          # Documentation
├── ALPHASIGNAL_ROADMAP.md             # This file
└── package.json                       # Node dependencies
```

---

## 🎯 IMMEDIATE NEXT STEPS (Phase 4 Frontend)

### Week 1: ML Predictions UI (1-2 days)

**Day 1: Prediction Card Component**
```typescript
// app/alphasignal/components/prediction-card.tsx
- Build prediction display component
- Show UP/DOWN direction with color coding
- Display probability percentages
- Add confidence gauge (high/medium/low)
- Implement loading states
```

**Day 2: Integration & Charts**
```typescript
// Integrate with predictions API
- Add "Generate Prediction" button
- Fetch and display predictions
- Show historical predictions timeline
- Display model accuracy metrics
- Add error handling
```

**Deliverables**:
- [ ] Prediction card component complete
- [ ] Generate prediction functionality working
- [ ] Historical predictions displayed
- [ ] Model metrics shown
- [ ] UI matches dark theme

---

### Week 2: Factor Analysis UI (1-2 days)

**Day 1: Factor Exposure Components**
```typescript
// app/alphasignal/components/factor-card.tsx
- Build factor exposure display
- Show alpha with significance stars
- Display beta bars (market, size, value)
- Add interpretation text
- Implement visual indicators
```

**Day 2: Rolling Factors & Charts**
```typescript
// Add time-series visualization
- Integrate Recharts for factor trends
- Show rolling factor exposures
- Add time period controls
- Display R-squared and fit quality
```

**Deliverables**:
- [ ] Factor exposure card complete
- [ ] Alpha/beta displayed correctly
- [ ] Rolling factors chart working
- [ ] Analysis controls functional
- [ ] Statistical significance shown

---

### Week 3-4: Sentiment & Social (Phase 6) (2-3 days)

**Prerequisites**:
1. Get API keys:
   - News API: https://newsapi.org/register
   - Reddit API: https://www.reddit.com/prefs/apps

2. Add to `.env`:
   ```bash
   NEWS_API_KEY=your_key_here
   REDDIT_CLIENT_ID=your_id_here
   REDDIT_CLIENT_SECRET=your_secret_here
   REDDIT_USER_AGENT=AlphaSignal/1.0
   ```

**Implementation**:
- Uncomment sentiment API routes in `alphasignal_main.py`
- Build sentiment UI components
- Create news feed display
- Add social signals cards
- Implement sentiment trend charts

**Deliverables**:
- [ ] Sentiment API working
- [ ] News headlines displayed
- [ ] Reddit mentions tracked
- [ ] Sentiment gauge shown
- [ ] Trend charts functional

---

## 📊 SUCCESS METRICS

### Technical Performance
- [x] API response time: <100ms for demo endpoint
- [x] C++ indicators: 15-20x faster than Python
- [ ] ML prediction accuracy: >50%
- [ ] Factor model R-squared: >0.3
- [ ] Frontend load time: <1s

### Feature Completeness
- [x] Phase 1: Core Backend (100%)
- [x] Phase 2: Market Data (100%)
- [x] Phase 3: Basic Frontend (100%)
- [ ] Phase 4: ML Predictions (50% - need frontend)
- [ ] Phase 5: Factor Analysis (50% - need frontend)
- [ ] Phase 6: Sentiment (0% - need API keys)

### Code Quality
- [x] Backend organized with services pattern
- [x] Frontend using modern Next.js 14
- [x] Type safety with TypeScript + Pydantic
- [x] Error handling and logging
- [ ] Unit tests (need to add)
- [ ] Integration tests (need to add)

---

## 🎓 SKILLS DEMONSTRATED

| Skill | Demonstrated By | Status |
|-------|----------------|--------|
| **Full-Stack Development** | Next.js + FastAPI integration | ✅ |
| **Machine Learning** | XGBoost for predictions | ✅ Backend |
| **Quantitative Finance** | Factor models, technical indicators | ✅ Backend |
| **Performance Engineering** | C++ optimization (15-20x speedup) | ✅ |
| **Database Design** | 6-table schema with relationships | ✅ |
| **API Design** | RESTful FastAPI with OpenAPI docs | ✅ |
| **Data Engineering** | Market data pipeline | ✅ |
| **UI/UX Design** | Modern dark theme dashboard | ✅ |
| **Alternative Data** | Sentiment & social signals | 🔜 Phase 6 |

---

## 📝 RESUME ONE-LINER

**AlphaSignal - Alternative Data Alpha Research Platform** | Python, TypeScript, Next.js, FastAPI, XGBoost

*Built a quantitative research platform combining machine learning (XGBoost classifier, 54% accuracy), Fama-French 3-factor analysis, and technical indicators for alpha signal generation. Optimized performance with C++ integration achieving 15-20x speedup for indicator calculations. Architected full-stack application with FastAPI backend, Next.js 14 frontend, and SQLAlchemy ORM managing 6 specialized database tables. Implemented feature engineering pipeline with 31 technical features and backtesting framework for strategy validation.*

**Tech**: Python, TypeScript, FastAPI, Next.js 14, XGBoost, C++, SQLAlchemy, Tailwind CSS, Recharts

---

## 🐛 KNOWN ISSUES & TODOS

### High Priority
- [ ] Add unit tests for ML models
- [ ] Implement error boundaries in frontend
- [ ] Add rate limiting for API endpoints
- [ ] Create data validation for market data
- [ ] Add caching layer (Redis optional)

### Medium Priority
- [ ] Implement user authentication
- [ ] Add portfolio tracking (multiple stocks)
- [ ] Create strategy backtesting UI
- [ ] Add export functionality (CSV/JSON)
- [ ] Implement watchlist feature

### Low Priority
- [ ] Add more ML models (LSTM, Random Forest)
- [ ] Implement real-time data streaming
- [ ] Add notifications/alerts
- [ ] Create mobile-responsive improvements
- [ ] Add dark/light theme toggle

---

## 🚀 QUICK START

### Run Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python alphasignal_main.py
```
**Backend URL**: http://localhost:8000
**API Docs**: http://localhost:8000/docs

### Run Frontend
```bash
npm install
npm run dev
```
**Frontend URL**: http://localhost:3000/alphasignal

### Train ML Model (Optional)
```bash
cd backend
source venv/bin/activate
python train_model.py --ticker AAPL --days 365
```

### Install C++ Indicators (Optional, 15-20x speedup)
```bash
cd backend/cpp_indicators
pip install pybind11
./build.sh  # or: python setup.py build_ext --inplace
```

---

## 📚 RESOURCES

### APIs Used
- Yahoo Finance (via yfinance): Market data
- News API (Phase 6): News sentiment
- Reddit API (Phase 6): Social signals

### Libraries
- **Backend**: FastAPI, SQLAlchemy, Pandas, NumPy, SciPy, XGBoost, scikit-learn
- **Frontend**: Next.js 14, React, Tailwind CSS, shadcn/ui, Recharts
- **Performance**: C++ with pybind11

### Learning Resources
- Fama-French Model: [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
- Technical Indicators: [Investopedia](https://www.investopedia.com/terms/t/technicalindicator.asp)
- XGBoost: [Official Documentation](https://xgboost.readthedocs.io/)

---

## 🎯 PHASE 4 & 5 COMPLETION GOAL

**Target**: Complete Phase 4 & 5 frontends in 3-4 days

**Outcome**: Fully functional ML prediction and factor analysis features visible to users, demonstrating both backend quant finance knowledge and frontend engineering skills.

**Then**: Move to Phase 6 (sentiment) after obtaining API keys.

---

**Last Updated**: 2025-01-21
**Current Phase**: 4 & 5 (Backend Complete, Frontend In Progress)
**Overall Progress**: 50% Complete

**Next Action**: Build ML Predictions UI (Day 1: Prediction Card Component)
