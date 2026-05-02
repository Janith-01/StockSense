export interface PredictionData {
  ticker: string
  last_close: number
  predicted_price: number
  change_pct: number
  signal: 'BUY' | 'SELL' | 'HOLD'
  timestamp: string
}

export interface HistoryData {
  ticker: string
  dates: string[]
  prices: number[]
}

export interface MetricsData {
  rmse: number
  mae: number
  mape: number
  r2: number
  features_count: number
  sequence_length: number
}

export interface HealthData {
  status: string
  model_loaded: boolean
  rmse: number
  mae: number
  mape: number
  r2: number
}
