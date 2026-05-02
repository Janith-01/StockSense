import React from 'react'
import {
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ComposedChart,
  Legend,
} from 'recharts'

interface PriceChartProps {
  dates: string[]
  prices: number[]
  predictedPrice?: number
  loading?: boolean
}

export const PriceChart: React.FC<PriceChartProps> = ({
  dates,
  prices,
  predictedPrice,
  loading,
}) => {
  // Prepare chart data with proper typing
  const chartData: Array<{
    date: string
    price: number | null
    predicted?: number
    name: string
  }> = dates.map((date, index) => ({
    date: date,
    price: prices[index],
    name: date,
  }))

  // Add predicted price point if available
  if (predictedPrice !== undefined && chartData.length > 0) {
    const lastDate = new Date(chartData[chartData.length - 1].date)
    const nextDate = new Date(lastDate.getTime() + 24 * 60 * 60 * 1000)
    chartData.push({
      date: nextDate.toISOString().split('T')[0],
      price: null,
      predicted: predictedPrice,
      name: 'Predicted',
    })
  }

  if (loading) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
        <div className="h-80 bg-gray-800 rounded animate-pulse"></div>
      </div>
    )
  }

  if (prices.length === 0) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 border border-gray-800 flex items-center justify-center h-80">
        <p className="text-gray-400">No data available</p>
      </div>
    )
  }

  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
      <h3 className="text-lg font-semibold text-white mb-4">Price History</h3>
      <ResponsiveContainer width="100%" height={350}>
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="date"
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            interval={Math.floor(chartData.length / 6) || 0}
          />
          <YAxis
            stroke="#9ca3af"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            domain={['dataMin - 50', 'dataMax + 50']}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              padding: '10px',
            }}
            labelStyle={{ color: '#e5e7eb' }}
            cursor={{ stroke: '#60a5fa', strokeWidth: 2 }}
            formatter={(value: any) => {
              if (value !== null) {
                return [`$${value.toFixed(2)}`, '']
              }
              return value
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#3b82f6"
            dot={false}
            strokeWidth={2}
            isAnimationActive={false}
            name="Actual Price"
          />
          <Scatter
            dataKey="predicted"
            fill="#10b981"
            shape="circle"
            name="Predicted Price"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
