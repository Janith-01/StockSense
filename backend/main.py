import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Try to import joblib for pickle compatibility
try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False

# ============================================================================
# LSTM Model Architecture (must match training)
# ============================================================================
class LSTMModel(nn.Module):
    def __init__(self, input_size=15, hidden_size=128, num_layers=2, dropout=0.2):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=True
        )
        self.batch_norm = nn.BatchNorm1d(hidden_size)
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_hidden = lstm_out[:, -1, :]
        batch_norm_out = self.batch_norm(last_hidden)
        output = self.fc(batch_norm_out)
        return output


# ============================================================================
# Response Models
# ============================================================================
class PredictionResponse(BaseModel):
    ticker: str
    last_close: float
    predicted_price: float
    change_pct: float
    signal: str
    timestamp: str


class HistoryResponse(BaseModel):
    ticker: str
    dates: list
    prices: list


class MetricsResponse(BaseModel):
    rmse: float
    mae: float
    mape: float
    r2: float
    features_count: int
    sequence_length: int


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    rmse: float
    mae: float
    mape: float
    r2: float


# ============================================================================
# Global Variables & Model Loading
# ============================================================================
MODEL_DIR = Path(__file__).parent / "stocksenseModel"
MODEL_PATH = MODEL_DIR / "best_model.pth"
FEATURE_SCALER_PATH = MODEL_DIR / "feature_scaler.pkl"
TARGET_SCALER_PATH = MODEL_DIR / "target_scaler.pkl"
FEATURES_PATH = MODEL_DIR / "features.json"

# Training metrics
TRAINING_METRICS = {
    "rmse": 10.30,
    "mae": 8.19,
    "mape": 3.82,
    "r2": 0.8272
}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = None
feature_scaler = None
target_scaler = None
features_list = None


def load_model_artifacts():
    """Load model, scalers, and features on startup"""
    global model, feature_scaler, target_scaler, features_list

    try:
        print("\n" + "="*70)
        print("🚀 StockSense Backend - Loading Model Artifacts")
        print("="*70)
        
        # Check file existence
        print(f"\n📂 Checking artifact files:")
        print(f"  Model:          {MODEL_PATH.exists()} → {MODEL_PATH}")
        print(f"  Feature Scaler: {FEATURE_SCALER_PATH.exists()} → {FEATURE_SCALER_PATH}")
        print(f"  Target Scaler:  {TARGET_SCALER_PATH.exists()} → {TARGET_SCALER_PATH}")
        print(f"  Features List:  {FEATURES_PATH.exists()} → {FEATURES_PATH}")
        
        # Load model
        print(f"\n🤖 Loading LSTM model...")
        model = LSTMModel(input_size=15, hidden_size=128, num_layers=2, dropout=0.2)
        
        # Load checkpoint - handle both full checkpoint and state dict
        checkpoint = torch.load(MODEL_PATH, map_location=device)
        
        # Check if it's a full checkpoint or just state dict
        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            print(f"   → Loading from full checkpoint (epoch {checkpoint.get('epoch', '?')})")
            model.load_state_dict(checkpoint["model_state_dict"])
        else:
            print(f"   → Loading from state dict")
            model.load_state_dict(checkpoint)
        
        model.to(device)
        model.eval()
        print(f"   ✓ Model loaded successfully (device: {device})")

        # Load scalers
        print(f"\n📊 Loading scalers...")
        try:
            with open(FEATURE_SCALER_PATH, "rb") as f:
                feature_scaler = pickle.load(f)
        except (pickle.UnpicklingError, ValueError) as e:
            if HAS_JOBLIB:
                print(f"   → Pickle failed, trying joblib...")
                feature_scaler = joblib.load(FEATURE_SCALER_PATH)
            else:
                raise
        print(f"   ✓ Feature scaler loaded")

        try:
            with open(TARGET_SCALER_PATH, "rb") as f:
                target_scaler = pickle.load(f)
        except (pickle.UnpicklingError, ValueError) as e:
            if HAS_JOBLIB:
                print(f"   → Pickle failed, trying joblib...")
                target_scaler = joblib.load(TARGET_SCALER_PATH)
            else:
                raise
        print(f"   ✓ Target scaler loaded")

        # Load features
        print(f"\n📋 Loading features...")
        with open(FEATURES_PATH, "r") as f:
            features_list = json.load(f)
        print(f"   ✓ Features loaded: {len(features_list)} features")
        print(f"   → {features_list}")
        
        print("\n" + "="*70)
        print("✅ Model and artifacts loaded successfully!")
        print("="*70 + "\n")
        return True
    except FileNotFoundError as e:
        print(f"\n❌ FILE NOT FOUND ERROR: {e}")
        print(f"   Make sure all artifact files exist in: {MODEL_DIR}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR loading model artifacts: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# Feature Engineering
# ============================================================================
def calculate_technical_indicators(df):
    """Calculate 15 technical indicators from OHLCV data"""
    df = df.copy()

    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # 1. Close (already in data)
    # 2. Volume
    # 3-4. Simple Moving Averages
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()

    # 5-6. Exponential Moving Averages
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()

    # 7-8. MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # 9. Relative Strength Index (RSI)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # 10. Bollinger Bands width
    sma20 = df['Close'].rolling(window=20).mean()
    std20 = df['Close'].rolling(window=20).std()
    df['BB_width'] = (sma20 + 2 * std20) - (sma20 - 2 * std20)

    # 11. Daily Return
    df['Daily_Return'] = df['Close'].pct_change()

    # 12. Price Range Percentage
    df['Price_Range_Pct'] = (df['High'] - df['Low']) / df['Close']

    # 13-14. Volatility (rolling std of returns)
    df['Volatility_10'] = df['Close'].pct_change().rolling(window=10).std()
    df['Volatility_20'] = df['Close'].pct_change().rolling(window=20).std()

    return df


def prepare_sequence(data, sequence_length=60):
    """Prepare data into sequences for LSTM"""
    sequences = []
    for i in range(len(data) - sequence_length + 1):
        sequences.append(data[i:i + sequence_length])
    return np.array(sequences)


# ============================================================================
# FastAPI Application
# ============================================================================
app = FastAPI(title="StockSense API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Load model on startup with detailed logging"""
    print("\n\n" + "🔧 "*30)
    print("STARTING STOCKSENSE BACKEND")
    print("🔧 "*30 + "\n")
    
    success = load_model_artifacts()
    
    if success:
        print("✨ Backend is ready to accept requests!")
        print(f"📡 Server running on: http://0.0.0.0:8000")
        print(f"📚 API Docs: http://localhost:8000/docs")
    else:
        print("\n⚠️  WARNING: Backend started but model is NOT loaded!")
        print("   Requests to /predict will return 503 Service Unavailable")
        print("   Please check the error messages above and fix the issues.")
    
    print("\n" + "="*70 + "\n")


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return HealthResponse(
        status="healthy",
        model_loaded=True,
        rmse=TRAINING_METRICS["rmse"],
        mae=TRAINING_METRICS["mae"],
        mape=TRAINING_METRICS["mape"],
        r2=TRAINING_METRICS["r2"]
    )


@app.get("/health/detailed")
async def health_detailed():
    """Detailed health check for debugging"""
    return {
        "status": "running",
        "model_loaded": model is not None,
        "feature_scaler_loaded": feature_scaler is not None,
        "target_scaler_loaded": target_scaler is not None,
        "features_loaded": features_list is not None,
        "device": str(device),
        "model_type": type(model).__name__ if model else None,
        "features_count": len(features_list) if features_list else 0,
        "training_metrics": TRAINING_METRICS,
        "artifact_files": {
            "model_path": str(MODEL_PATH),
            "model_exists": MODEL_PATH.exists(),
            "feature_scaler_path": str(FEATURE_SCALER_PATH),
            "feature_scaler_exists": FEATURE_SCALER_PATH.exists(),
            "target_scaler_path": str(TARGET_SCALER_PATH),
            "target_scaler_exists": TARGET_SCALER_PATH.exists(),
            "features_path": str(FEATURES_PATH),
            "features_exists": FEATURES_PATH.exists(),
        }
    }


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Return model performance metrics"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return MetricsResponse(
        rmse=TRAINING_METRICS["rmse"],
        mae=TRAINING_METRICS["mae"],
        mape=TRAINING_METRICS["mape"],
        r2=TRAINING_METRICS["r2"],
        features_count=len(features_list),
        sequence_length=60
    )


@app.get("/predict/{ticker}", response_model=PredictionResponse)
async def predict(ticker: str):
    """Predict next day's stock price"""
    if model is None or feature_scaler is None or target_scaler is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        ticker = ticker.upper()

        # Download last 300 days of data (accounts for NaN values from technical indicators)
        # SMA_50 creates ~49 NaN values, so we need extra data to have 60 usable days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=300)
        
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        except Exception as e:
            # Handle yfinance errors
            error_msg = str(e).lower()
            if "no timezone" in error_msg or "delisted" in error_msg:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Ticker {ticker} not found or delisted. Please verify the ticker symbol."
                )
            elif "failed download" in error_msg:
                raise HTTPException(
                    status_code=503,
                    detail=f"Failed to download data for {ticker}. yfinance service may be temporarily unavailable."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error downloading data: {str(e)}"
                )

        if df.empty:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found or has no data")

        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Calculate technical indicators
        df = calculate_technical_indicators(df)
        df = df.dropna()

        if len(df) < 60:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data for {ticker}. Need at least 60 days. Got {len(df)} days."
            )

        # Get last close price
        last_close = float(df['Close'].iloc[-1])

        # Prepare features
        feature_data = df[features_list].values
        feature_data_scaled = feature_scaler.transform(feature_data)

        # Prepare sequence (last 60 days)
        sequence = feature_data_scaled[-60:].reshape(1, 60, 15)
        sequence_tensor = torch.tensor(sequence, dtype=torch.float32).to(device)

        # Make prediction
        with torch.no_grad():
            prediction_scaled = model(sequence_tensor).cpu().numpy()[0][0]

        # Inverse transform prediction
        predicted_price = float(target_scaler.inverse_transform([[prediction_scaled]])[0][0])

        # Calculate change percentage
        change_pct = ((predicted_price - last_close) / last_close) * 100

        # Generate signal
        if change_pct > 2:
            signal = "BUY"
        elif change_pct < -2:
            signal = "SELL"
        else:
            signal = "HOLD"

        return PredictionResponse(
            ticker=ticker,
            last_close=round(last_close, 2),
            predicted_price=round(predicted_price, 2),
            change_pct=round(change_pct, 2),
            signal=signal,
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/history/{ticker}", response_model=HistoryResponse)
async def get_history(ticker: str, days: int = 90):
    """Get historical price data for charting"""
    if days <= 0 or days > 365:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 365")

    try:
        ticker = ticker.upper()

        # Download historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 10)
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if df.empty:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")

        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Take last 'days' entries
        df = df.tail(days)

        # Format data
        dates = [date.strftime("%Y-%m-%d") for date in df.index]
        prices = [float(price) for price in df['Close'].values]

        return HistoryResponse(
            ticker=ticker,
            dates=dates,
            prices=prices
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History retrieval error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
