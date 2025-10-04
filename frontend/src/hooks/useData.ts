import { create } from 'zustand'
import { apiClient } from '@/services/api'
import type {
  DashboardTodayFeed,
  DashboardMetrics,
  BreakingNews,
  WeeklySummary,
} from '@/types'

interface DataState {
  todayFeed: DashboardTodayFeed | null
  metrics: DashboardMetrics | null
  breakingNews: BreakingNews | null
  weeklySummary: WeeklySummary | null
  isLoading: boolean
  error: string | null
  fetchTodayFeed: () => Promise<void>
  fetchMetrics: () => Promise<void>
  fetchBreakingNews: () => Promise<void>
  fetchWeeklySummary: () => Promise<void>
  fetchAll: () => Promise<void>
  clearError: () => void
}

export const useData = create<DataState>((set, get) => ({
  todayFeed: null,
  metrics: null,
  breakingNews: null,
  weeklySummary: null,
  isLoading: false,
  error: null,

  fetchTodayFeed: async () => {
    try {
      set({ isLoading: true, error: null })
      const response = await apiClient.get<DashboardTodayFeed>('/data/current')
      set({ todayFeed: response?.data || null, isLoading: false })
    } catch (error: any) {
      set({ error: error?.message || 'Failed to fetch data', isLoading: false })
    }
  },

  fetchMetrics: async () => {
    try {
      set({ isLoading: true, error: null })
      const response = await apiClient.get<DashboardMetrics>('/data/current')
      set({ metrics: response?.data || null, isLoading: false })
    } catch (error: any) {
      set({ error: error?.message || 'Failed to fetch metrics', isLoading: false })
    }
  },

  fetchBreakingNews: async () => {
    try {
      set({ isLoading: true, error: null })
      // Placeholder - backend doesn't have breaking news endpoint yet
      set({ breakingNews: null, isLoading: false })
    } catch (error: any) {
      set({ error: error?.message || 'Failed to fetch breaking news', isLoading: false })
    }
  },

  fetchWeeklySummary: async () => {
    try {
      set({ isLoading: true, error: null })
      // Placeholder - backend doesn't have weekly summary endpoint yet
      set({ weeklySummary: null, isLoading: false })
    } catch (error: any) {
      set({ error: error?.message || 'Failed to fetch weekly summary', isLoading: false })
    }
  },

  fetchAll: async () => {
    try {
      set({ isLoading: true, error: null })
      await Promise.all([
        get().fetchTodayFeed(),
        get().fetchMetrics(),
        get().fetchBreakingNews(),
        get().fetchWeeklySummary(),
      ])
      set({ isLoading: false })
    } catch (error: any) {
      set({ error: error?.message || 'Failed to fetch data', isLoading: false })
    }
  },

  clearError: () => set({ error: null }),
}))
