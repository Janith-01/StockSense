import React, { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import { HealthData } from '@/types'

export const Header: React.FC = () => {
  const [metrics, setMetrics] = useState<Partial<HealthData> | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await apiClient.getHealth()
        setMetrics(data)
      } catch (error) {
        console.error('Failed to fetch metrics:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
  }, [])

  return (
    <header className="bg-gray-900 border-b border-gray-800 py-6 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">S</span>
            </div>
            <h1 className="text-3xl font-bold text-white">StockSense</h1>
          </div>

          <div className="flex gap-4">
            {loading ? (
              <div className="h-8 w-48 bg-gray-800 rounded animate-pulse"></div>
            ) : metrics ? (
              <div className="flex gap-6 text-sm">
                <div className="bg-gray-800 px-4 py-2 rounded-lg">
                  <span className="text-gray-400">MAPE:</span>{' '}
                  <span className="text-green-400 font-semibold">
                    {metrics.mape?.toFixed(2)}%
                  </span>
                </div>
                <div className="bg-gray-800 px-4 py-2 rounded-lg">
                  <span className="text-gray-400">R²:</span>{' '}
                  <span className="text-blue-400 font-semibold">
                    {metrics.r2?.toFixed(4)}
                  </span>
                </div>
              </div>
            ) : null}
          </div>
        </div>
        <p className="text-gray-400 text-sm">
          AI-powered stock price prediction using LSTM neural networks
        </p>
      </div>
    </header>
  )
}
