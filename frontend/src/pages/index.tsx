import React, { useState } from 'react'
import { Header } from '@/components/Header'
import { PredictionForm } from '@/components/PredictionForm'
import { StatCard } from '@/components/StatCard'
import { PriceChart } from '@/components/PriceChart'
import {
  StatCardSkeleton,
  ChartSkeleton,
} from '@/components/Skeleton'
import { apiClient } from '@/lib/api'
import { PredictionData, HistoryData } from '@/types'

export default function Home() {
  const [prediction, setPrediction] = useState<PredictionData | null>(null)
  const [history, setHistory] = useState<HistoryData | null>(null)
  const [loading, setLoading] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(false)

  const handlePredict = async (ticker: string) => {
    setLoading(true)
    setHistoryLoading(true)

    try {
      // Fetch prediction
      const predictionData = await apiClient.getPrediction(ticker)
      setPrediction(predictionData)

      // Fetch history
      const historyData = await apiClient.getHistory(ticker, 90)
      setHistory(historyData)
    } catch (error) {
      console.error('Prediction error:', error)
      setPrediction(null)
      setHistory(null)

      if (error instanceof Error) {
        throw error
      }
      throw new Error('Failed to fetch prediction')
    } finally {
      setLoading(false)
      setHistoryLoading(false)
    }
  }

  const getSignalColor = (signal: string): 'green' | 'red' | 'yellow' => {
    switch (signal) {
      case 'BUY':
        return 'green'
      case 'SELL':
        return 'red'
      case 'HOLD':
        return 'yellow'
      default:
        return 'yellow'
    }
  }

  const getChangeColor = (change: number): 'green' | 'red' => {
    return change >= 0 ? 'green' : 'red'
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Input Section */}
        <div className="mb-8">
          <PredictionForm onSubmit={handlePredict} loading={loading} />
        </div>

        {/* Prediction Stats */}
        {prediction ? (
          <div className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatCard
              label="Last Close Price"
              value={`$${prediction.last_close.toFixed(2)}`}
              subtext={prediction.ticker}
            />
            <StatCard
              label="Predicted Next Day"
              value={`$${prediction.predicted_price.toFixed(2)}`}
              color="blue"
              subtext="AI Model Prediction"
            />
            <StatCard
              label="Signal"
              value={prediction.signal}
              color={getSignalColor(prediction.signal)}
              subtext={`${prediction.change_pct > 0 ? '+' : ''}${prediction.change_pct.toFixed(2)}%`}
            />
          </div>
        ) : (
          <div className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
          </div>
        )}

        {/* Price Chart */}
        {history ? (
          <PriceChart
            dates={history.dates}
            prices={history.prices}
            predictedPrice={prediction?.predicted_price}
            loading={historyLoading}
          />
        ) : (
          <ChartSkeleton />
        )}

        {/* Info Section */}
        <div className="mt-8 bg-gray-900 rounded-lg p-6 border border-gray-800">
          <h3 className="text-lg font-semibold text-white mb-3">About</h3>
          <p className="text-gray-400 text-sm leading-relaxed">
                StockSense uses a 2-layer stacked LSTM neural network trained on 15
                technical indicators to predict stock prices. The model analyzes 60 days
                of historical data including moving averages, RSI, MACD, and volatility
                metrics. Signal interpretation: BUY (greater than 2% increase expected),
                SELL (less than -2% decrease expected), HOLD (-2% to +2%).
            </p>
        </div>
      </main>
    </div>
  )
}
