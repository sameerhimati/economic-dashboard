import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type RefreshInterval = 1 | 5 | 10 | 30 | 0 // 0 = manual

interface SettingsState {
  // Display preferences
  showTodayFeed: boolean
  showFavorites: boolean
  showMetrics: boolean
  showBreakingNews: boolean
  showWeeklySummary: boolean

  // Auto-refresh
  refreshInterval: RefreshInterval

  // Onboarding
  hasSeenTour: boolean

  // Actions
  toggleSection: (section: keyof Omit<SettingsState, 'refreshInterval' | 'hasSeenTour' | 'toggleSection' | 'setRefreshInterval' | 'completeTour' | 'resetSettings'>) => void
  setRefreshInterval: (interval: RefreshInterval) => void
  completeTour: () => void
  resetSettings: () => void
}

const DEFAULT_SETTINGS = {
  showTodayFeed: true,
  showFavorites: true,
  showMetrics: true,
  showBreakingNews: true,
  showWeeklySummary: true,
  refreshInterval: 5 as RefreshInterval,
  hasSeenTour: false,
}

export const useSettings = create<SettingsState>()(
  persist(
    (set) => ({
      ...DEFAULT_SETTINGS,

      toggleSection: (section) =>
        set((state) => ({
          [section]: !state[section],
        })),

      setRefreshInterval: (interval) =>
        set({ refreshInterval: interval }),

      completeTour: () =>
        set({ hasSeenTour: true }),

      resetSettings: () =>
        set({ ...DEFAULT_SETTINGS }),
    }),
    {
      name: 'dashboard-settings',
    }
  )
)
