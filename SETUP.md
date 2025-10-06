# PE Dashboard - Setup & Run Guide

## ✅ Setup Complete!

Your PE Dashboard is now **fully configured** and ready to run! All dependencies are installed and configured.

---

## 🚀 Quick Start

### Option 1: Using Shell Scripts (Easiest)

Open **two terminals** in the project directory:

**Terminal 1 - Backend:**
```bash
./start-backend.sh
```

**Terminal 2 - Frontend:**
```bash
./start-frontend.sh
```

### Option 2: Using VS Code (Recommended for Development)

1. Open the project in VS Code
2. Press `F5` or go to **Run and Debug** panel
3. Select **"Full Stack: Backend + Frontend"**
4. Click the green play button

This will start both backend and frontend simultaneously with debugging support!

### Option 3: Manual Commands

**Backend:**
```bash
./venv/bin/python backend/run.py
```

**Frontend:**
```bash
npm run dev
```

---

## 🌐 Access the Dashboard

Once both servers are running:

- **Frontend (Dashboard UI):** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs (Interactive Swagger UI)
- **Health Check:** http://localhost:8000/health

---

## 📋 What's Already Configured

✅ Python virtual environment created and activated
✅ All backend dependencies installed (FastAPI, Uvicorn, Pandas, NumPy, etc.)
✅ All frontend dependencies installed (Next.js, React, TailwindCSS, etc.)
✅ Alpha Vantage API key configured: `E45B7SPRJO5Z2DMV`
✅ Database configuration ready (SQLite)
✅ CORS configured for frontend-backend communication
✅ Import issues fixed (relative imports working)
✅ VS Code debug configurations created

---

## 🔧 VS Code Python Setup

To enable Python features in VS Code:

1. **Install Python Extension:**
   - Open Extensions (Ctrl+Shift+X)
   - Search for "Python" by Microsoft
   - Click Install

2. **Select Python Interpreter:**
   - Press `Ctrl+Shift+P`
   - Type "Python: Select Interpreter"
   - Choose: `./venv/bin/python`

3. **Verify Configuration:**
   - Open any Python file in `backend/`
   - You should see syntax highlighting and IntelliSense
   - The status bar should show: Python 3.12.3 64-bit ('venv')

---

## 📁 Project Structure

```
pe-dashboard/
├── backend/                 # FastAPI Backend
│   ├── main.py             # Main API application
│   ├── run.py              # Startup script
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic schemas
│   ├── services.py         # Business logic
│   ├── crud.py             # Database operations
│   ├── auth.py             # Authentication
│   ├── database.py         # Database config
│   ├── alpha_service.py    # Alpha Vantage integration
│   ├── requirements.txt    # Python dependencies
│   ├── .env                # Environment variables
│   └── venv/               # Virtual environment
├── app/                    # Next.js Frontend
│   ├── page.tsx            # Main dashboard page
│   ├── layout.tsx          # App layout
│   ├── globals.css         # Global styles
│   └── components/         # React components
├── components/             # Shared UI components
├── .vscode/                # VS Code configuration
│   ├── launch.json         # Debug configurations
│   └── settings.json       # Workspace settings
├── start-backend.sh        # Backend startup script
├── start-frontend.sh       # Frontend startup script
└── package.json            # Node dependencies
```

---

## 🧪 Testing the Setup

### 1. Test Backend Health
```bash
curl http://localhost:8000/health
```
Expected response: `{"status":"healthy","version":"1.0.0"}`

### 2. Test API Documentation
Open browser: http://localhost:8000/docs

### 3. Test Frontend
Open browser: http://localhost:3000

---

## 🔑 Environment Variables

Backend environment variables are in `backend/.env`:

```env
ALPHAVANTAGE_API_KEY=E45B7SPRJO5Z2DMV
API_RATE_LIMIT=5
DATABASE_URL=sqlite:///./pe_dashboard.db
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 📊 Using the Dashboard

1. **Ingest Sample Data:**
   - Click "Ingest Sample Data" button on the dashboard
   - This will load sample portfolio companies with real market data

2. **View Portfolio Metrics:**
   - Total portfolio value
   - IRR (Internal Rate of Return)
   - MOIC (Multiple on Invested Capital)
   - Sector allocation

3. **Track Investments:**
   - View active deals
   - Monitor performance
   - Analyze sector breakdown

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or use ./venv/bin/python directly

# Check if port 8000 is available
lsof -ti:8000 | xargs kill -9  # Kill any process on port 8000

# Reinstall dependencies if needed
./venv/bin/pip install -r backend/requirements.txt
```

### Frontend won't start
```bash
# Ensure dependencies are installed
npm install

# Check if port 3000 is available
lsof -ti:3000 | xargs kill -9  # Kill any process on port 3000

# Clear Next.js cache
rm -rf .next
npm run dev
```

### Python imports not working in VS Code
- Ensure Python extension is installed
- Select correct interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter" → Choose `./venv/bin/python`
- Reload VS Code window: `Ctrl+Shift+P` → "Developer: Reload Window"

### API Key Issues
- Verify your Alpha Vantage API key is valid
- Check rate limits (5 calls/minute for free tier)
- Test API key at: https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=YOUR_KEY

---

## 🎯 Next Steps

1. **Start both servers** using any of the methods above
2. **Open the dashboard** at http://localhost:3000
3. **Ingest sample data** to populate the dashboard
4. **Explore the API docs** at http://localhost:8000/docs
5. **Customize the dashboard** by modifying the code

---

## 📚 Additional Resources

- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Next.js Documentation:** https://nextjs.org/docs
- **Alpha Vantage API:** https://www.alphavantage.co/documentation/

---

## 💡 Development Tips

- **Hot Reload:** Both servers support hot reload - changes will reflect automatically
- **API Testing:** Use http://localhost:8000/docs for interactive API testing
- **Database:** SQLite database file is at `backend/pe_dashboard.db`
- **Logs:** Backend logs appear in the terminal running the backend server

---

**You're all set! 🎉**

If you encounter any issues, refer to the troubleshooting section above or check the logs in the terminal.
