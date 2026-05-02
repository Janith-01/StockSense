# 🚀 Quick Start Guide

## ✅ Project Files Generated

All files have been created successfully! Here's what's been built:

### Backend
- ✓ `backend/main.py` - FastAPI application with:
  - LSTM model loading (matches your training architecture)
  - 4 endpoints: health check, metrics, predict, history
  - Technical indicator calculation (15 features)
  - Error handling & CORS configuration
  
- ✓ `backend/requirements.txt` - All Python dependencies

### Frontend  
- ✓ `frontend/` - Complete Next.js TypeScript application with:
  - Dark theme dashboard (Tailwind CSS)
  - Header with model metrics display
  - Ticker input & prediction form
  - 3 stat cards (Last Close, Predicted Price, Signal)
  - 90-day historical price chart (Recharts)
  - Loading skeletons for better UX
  - Fully typed with TypeScript

- ✓ Configuration files:
  - `tsconfig.json` - TypeScript configuration
  - `tailwind.config.js` - Tailwind CSS setup
  - `next.config.js` - Next.js configuration
  - `.env.local` - Environment variables

### Documentation
- ✓ `README.md` - Comprehensive guide with:
  - Project overview
  - Model architecture explanation
  - Complete API documentation
  - Setup instructions for both backend & frontend
  - Troubleshooting guide
  - Deployment tips

---

## 🔧 Setup Instructions

### Step 1: Backend Setup (Python)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn main:app --reload --port 8000
```

✅ Backend will be available at: http://localhost:8000
- Swagger API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

### Step 2: Frontend Setup (Node.js)

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

✅ Frontend will be available at: http://localhost:3000

---

## 🧪 Testing the Application

### Test 1: Health Check
```bash
curl http://localhost:8000/
```

### Test 2: Get Metrics  
```bash
curl http://localhost:8000/metrics
```

### Test 3: Predict Apple Stock
```bash
curl http://localhost:8000/predict/AAPL
```

### Test 4: Get 60 days of history
```bash
curl "http://localhost:8000/history/AAPL?days=60"
```

### Test 5: Open Frontend
Navigate to http://localhost:3000 and try:
1. Enter "AAPL" in the ticker input
2. Click "Predict" button
3. View the 90-day chart with prediction

---

## ⚙️ Model Requirements Met

Your backend will:

✅ Load model artifacts on startup:
  - best_model.pth
  - feature_scaler.pkl
  - target_scaler.pkl
  - features.json

✅ Calculate all 15 features from raw yfinance data:
  - Close, Volume, SMA_10, SMA_20, SMA_50
  - EMA_12, EMA_26, MACD, MACD_Signal
  - RSI, BB_width, Daily_Return, Price_Range_Pct
  - Volatility_10, Volatility_20

✅ Handle all technical requirements:
  - 2-layer LSTM with hidden_size=128, dropout=0.2
  - BatchNorm1d after LSTM
  - FC head: Linear(128→64) → ReLU → Dropout(0.2) → Linear(64→1)
  - Input: (batch, 60, 15)
  - Output: single scaled price value

✅ API endpoints with proper error handling:
  - GET / - Health check
  - GET /metrics - Model metrics
  - GET /predict/{ticker} - Predictions
  - GET /history/{ticker}?days=90 - Historical data

✅ Frontend features:
  - Dark theme dashboard
  - Model metrics badge (MAPE 3.82%, R² 0.8272)
  - Trading signals (BUY/SELL/HOLD)
  - 90-day price chart with next-day prediction
  - TypeScript typing
  - Fully responsive design

---

## 📝 Important Notes

1. **First-time startup**: The backend will download 120 days of data when you first request a prediction - this may take 5-10 seconds.

2. **Model loading**: Ensure all artifact files exist in `backend/stocksenseModel/`:
   - best_model.pth
   - feature_scaler.pkl  
   - target_scaler.pkl
   - features.json

3. **Internet connection required**: The backend uses yfinance to download live market data.

4. **CORS**: Frontend and backend are configured for local development (port 3000 & 8000).

5. **Production deployment**: Update CORS origins and API URLs as needed.

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
# On Windows:
netstat -ano | findstr :8000
# On macOS/Linux:
lsof -i :8000

# Use different port if needed
uvicorn main:app --port 8001
```

### Missing dependencies
```bash
# Reinstall all requirements
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check `.env.local` has correct API_URL
- Check browser console for CORS errors

---

## 🎯 Next Steps

1. Install backend & frontend dependencies
2. Start the backend on port 8000
3. Start the frontend on port 3000
4. Open http://localhost:3000 in your browser
5. Enter a ticker and click "Predict"
6. View your first AI-powered stock prediction! 🎉

---

Good luck with StockSense! 📈
