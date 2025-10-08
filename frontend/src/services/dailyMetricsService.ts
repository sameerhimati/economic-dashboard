import { apiClient } from './api'
import type {
  DailyMetricsResponse,
  HistoricalMetricsResponse,
  WeeklyReflectionResponse,
} from '@/types/dailyMetrics'

export const dailyMetricsService = {
  /**
   * Fetch daily metrics for a specific date
   */
  async getDailyMetrics(date: string): Promise<DailyMetricsResponse> {
    const response = await apiClient.get<DailyMetricsResponse>(
      '/api/daily-metrics/daily',
      {
        params: { date },
      }
    )
    return response.data
  },

  /**
   * Fetch historical data for a specific metric
   */
  async getHistoricalMetrics(
    code: string,
    range: '30d' | '90d' | '1y' | '5y'
  ): Promise<HistoricalMetricsResponse> {
    const response = await apiClient.get<HistoricalMetricsResponse>(
      `/api/daily-metrics/historical/${code}`,
      {
        params: { range },
      }
    )
    return response.data
  },

  /**
   * Fetch weekly reflection summary (for weekends)
   */
  async getWeeklyReflection(): Promise<WeeklyReflectionResponse> {
    const response = await apiClient.get<WeeklyReflectionResponse>(
      '/api/daily-metrics/weekly-reflection'
    )
    return response.data
  },
}
