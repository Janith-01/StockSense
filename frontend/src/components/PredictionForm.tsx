import React, { useState } from 'react'

interface PredictionFormProps {
  onSubmit: (ticker: string) => Promise<void>
  loading: boolean
}

export const PredictionForm: React.FC<PredictionFormProps> = ({
  onSubmit,
  loading,
}) => {
  const [ticker, setTicker] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!ticker.trim()) {
      setError('Please enter a ticker symbol')
      return
    }

    try {
      await onSubmit(ticker.toUpperCase())
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to fetch prediction. Please try again.'
      )
    }
  }

  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
      <h2 className="text-xl font-semibold text-white mb-4">Stock Ticker</h2>
      <form onSubmit={handleSubmit} className="flex gap-3">
        <div className="flex-1">
          <input
            type="text"
            value={ticker}
            onChange={(e) => {
              setTicker(e.target.value)
              setError('')
            }}
            placeholder="Enter ticker (e.g., AAPL, GOOGL, TSLA)"
            disabled={loading}
            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 transition disabled:opacity-50"
          />
          {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
        </div>
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
        >
          {loading ? 'Loading...' : 'Predict'}
        </button>
      </form>
    </div>
  )
}
