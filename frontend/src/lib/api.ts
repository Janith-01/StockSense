import axios from 'axios'
import {
  PredictionData,
  HistoryData,
  MetricsData,
  HealthData,
} from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

export const apiClient = {
  // Health check
  getHealth: async (): Promise<HealthData> => {
    const response = await api.get<HealthData>('/')
    return response.data
  },

  // Get metrics
  getMetrics: async (): Promise<MetricsData> => {
    const response = await api.get<MetricsData>('/metrics')
    return response.data
  },

  // Get prediction
  getPrediction: async (ticker: string): Promise<PredictionData> => {
    const response = await api.get<PredictionData>(`/predict/${ticker}`)
    return response.data
  },

  // Get historical data
  getHistory: async (ticker: string, days: number = 90): Promise<HistoryData> => {
    const response = await api.get<HistoryData>(`/history/${ticker}`, {
      params: { days },
    })
    return response.data
  },
}
